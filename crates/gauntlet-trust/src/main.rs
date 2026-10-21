//! Local key ownership and bounded authorization request validation.
//! No issuer signing or independent attestation is implied.
use ed25519_dalek::{Signature, Signer, SigningKey, Verifier, VerifyingKey};
use rand::rngs::OsRng;
use serde::{Deserialize, Serialize};
use std::{env, fs, path::Path};

#[derive(Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
struct Request {
    protocol: String,
    subject: String,
    public_key_hex: String,
    challenges: Vec<String>,
    nonce: String,
    proof_of_possession_hex: String,
}
fn bytes(subject: &str, key: &str, challenges: &[String], nonce: &str) -> Vec<u8> {
    format!(
        "GAUNTLET-KEY-REQUEST-v0.1\n{}\n{}\n{}\n{}",
        subject,
        key,
        challenges.join(","),
        nonce
    )
    .into_bytes()
}
fn verify_request(r: &Request) -> Result<(), String> {
    if r.protocol != "gauntlet-key-request-v0.1"
        || r.subject.trim().is_empty()
        || r.nonce.len() < 16
        || r.challenges.is_empty()
        || r.challenges
            .iter()
            .any(|c| c.trim().is_empty() || c.contains(','))
    {
        return Err("invalid request fields".into());
    }
    let pk: [u8; 32] = hex::decode(&r.public_key_hex)
        .map_err(|_| "invalid public key")?
        .try_into()
        .map_err(|_| "invalid public key length")?;
    let sig: [u8; 64] = hex::decode(&r.proof_of_possession_hex)
        .map_err(|_| "invalid signature")?
        .try_into()
        .map_err(|_| "invalid signature length")?;
    VerifyingKey::from_bytes(&pk)
        .map_err(|_| "invalid public key")?
        .verify(
            &bytes(&r.subject, &r.public_key_hex, &r.challenges, &r.nonce),
            &Signature::from_bytes(&sig),
        )
        .map_err(|_| "proof of possession failed".into())
}
fn run(args: Vec<String>) -> Result<(), String> {
    match args.iter().map(String::as_str).collect::<Vec<_>>().as_slice() {
        ["key", "generate", path] => {
            let path = Path::new(path);
            if path.exists() { return Err("refusing to overwrite private key".into()); }
            let key = SigningKey::generate(&mut OsRng);
            #[cfg(unix)] {
                use std::os::unix::fs::OpenOptionsExt;
                use std::io::Write;
                let mut f = fs::OpenOptions::new().write(true).create_new(true).mode(0o600).open(path).map_err(|e| e.to_string())?;
                f.write_all(hex::encode(key.to_bytes()).as_bytes()).map_err(|e| e.to_string())?;
            }
            #[cfg(not(unix))] { return Err("secure key creation currently supported only on Unix".into()); }
            println!("public_key_hex={}", hex::encode(key.verifying_key().to_bytes()));
            Ok(())
        }
        ["trust", "request", keyfile, subject, challenge, outfile] => {
            let secret = fs::read_to_string(keyfile).map_err(|e| e.to_string())?;
            let secret: [u8; 32] = hex::decode(secret.trim()).map_err(|_| "invalid secret")?.try_into().map_err(|_| "invalid secret length")?;
            let key = SigningKey::from_bytes(&secret);
            let pk = hex::encode(key.verifying_key().to_bytes());
            let nonce = hex::encode(SigningKey::generate(&mut OsRng).verifying_key().to_bytes());
            let challenges = vec![challenge.to_string()];
            let sig = hex::encode(key.sign(&bytes(subject, &pk, &challenges, &nonce)).to_bytes());
            let request = Request { protocol: "gauntlet-key-request-v0.1".into(), subject: subject.to_string(), public_key_hex: pk, challenges, nonce, proof_of_possession_hex: sig };
            verify_request(&request)?;
            fs::write(outfile, serde_json::to_vec_pretty(&request).map_err(|e| e.to_string())?).map_err(|e| e.to_string())?;
            println!("request_created=UNAUTHORIZED; awaiting independent authority review");
            Ok(())
        }
        ["trust", "verify-request", path] => {
            let r: Request = serde_json::from_slice(&fs::read(path).map_err(|e| e.to_string())?).map_err(|e| e.to_string())?;
            verify_request(&r)?;
            println!("proof_of_possession=VALID; authorization=NOT_GRANTED");
            Ok(())
        }
        _ => Err("usage: gauntlet-trust key generate <private-key-path> | trust request <private-key-path> <subject> <challenge-id> <output.json> | trust verify-request <request.json>".into()),
    }
}
fn main() {
    if let Err(e) = run(env::args().skip(1).collect()) {
        eprintln!("{e}");
        std::process::exit(1);
    }
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn valid_and_tampered_request() {
        let key = SigningKey::generate(&mut OsRng);
        let pk = hex::encode(key.verifying_key().to_bytes());
        let cs = vec!["GAUNTLET-003".to_string()];
        let nonce = "0123456789abcdef".to_string();
        let sig = hex::encode(key.sign(&bytes("evaluator", &pk, &cs, &nonce)).to_bytes());
        let mut r = Request {
            protocol: "gauntlet-key-request-v0.1".into(),
            subject: "evaluator".into(),
            public_key_hex: pk,
            challenges: cs,
            nonce,
            proof_of_possession_hex: sig,
        };
        assert!(verify_request(&r).is_ok());
        r.subject = "another-evaluator".into();
        assert!(verify_request(&r).is_err());
    }
    #[test]
    fn empty_scope_rejected() {
        let r = Request {
            protocol: "gauntlet-key-request-v0.1".into(),
            subject: "x".into(),
            public_key_hex: "00".repeat(32),
            challenges: vec![],
            nonce: "0123456789abcdef".into(),
            proof_of_possession_hex: "00".repeat(64),
        };
        assert!(verify_request(&r).is_err());
    }
}
