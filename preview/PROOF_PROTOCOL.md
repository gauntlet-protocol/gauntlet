# GAUNTLET Proof Protocol v0.1 — normative design

Status: specification; NOT implemented or independently validated.

## Assurance classes
LOCAL: participant-run local execution; can be reproduced and integrity-checked but cannot be called independently attested.
VERIFIED: a verifier checks canonical evidence, challenge/runner digests, replay constraints, role separation and independently authenticated source facts; does not by itself establish external operator independence.
ATTESTED: a distinct approved evaluator independently reproduces the challenge or supplies separately trusted observation and signs an attestation bound to the exact capsule digest. This class is mandatory for a public green verified badge.

Verdicts are PASS, FAIL, INSUFFICIENT_EVIDENCE. Assurance and verdict are independent axes. A failed challenge can be ATTESTED FAIL. Missing evidence cannot be PASS. Local verification cannot silently upgrade assurance.

## Capsule content
Required: protocol_version; challenge ID and version; variant commitment; SUT build/config digest; runner build digest; oracle build digest; environment digest; scenario seed; authorization and policy snapshot digests; legitimate-task controls; adversarial outcomes; independently observed effects where relevant; evidence manifest with per-artifact sha256; canonical capsule digest; timestamp; provenance and role identities. Optional: signed external attestations stored as separate objects.

All hashes and signatures must use an unambiguous canonical byte representation. Target RFC 8785 JCS for JSON (including strict duplicate-key rejection and I-JSON constraints), or explicitly version an alternative with cross-language vectors. Never treat Python json.dumps(sort_keys=True) as automatically JCS compliant.

## Attestation envelope
version; capsule_sha256; challenge ID/version; SUT digest; evaluator identity; evaluator public-key ID; evaluator role; independent execution/observation method; verification outcome; observed control outcomes; issuance/expiry; nonce; Ed25519 signature over domain-separated canonical payload.

The evaluator key MUST be registered in a separately controlled trust registry with approval, validity period, permitted scope and revocation status. Participant-provided keys cannot establish ATTESTED. The verifier MUST reject unknown/revoked keys, incorrect signature, mismatched capsule, wrong challenge or SUT digest, expired attestations and non-independent evaluators.

## Local run and verification
1. GAUNTLET CLI runs the public challenge locally against the participant SUT and an independent local oracle, recording actual positive and negative controls.
2. Runner creates immutable content-addressed evidence capsule; verifier checks hashes and local claims, returns LOCAL assurance.
3. A separate evaluator independently re-runs or observes using a separately controlled environment and signs an attestation for the exact capsule.
4. Rust verifier validates evaluator trust, role separation, cryptographic binding, reproducibility and oracle results, returning ATTESTED PASS/FAIL/INSUFFICIENT_EVIDENCE.
5. Only ATTESTED results may yield the green V/gauntlet badge; LOCAL results are visually and semantically distinct.

## Security acceptance tests
- Mutated capsule bytes or swapped artifacts invalidate verification.
- Substituted challenge, version, SUT or runner digest fails binding.
- Forged, expired, revoked or self-issued evaluator attestations never yield ATTESTED.
- Replayed signatures against a different capsule fail.
- Deny-all SUT fails positive controls.
- Missing independent observations or incomplete effect coverage yields INSUFFICIENT_EVIDENCE for effect claims.
- Invalid local run never becomes green from GitHub CI or badge SVG.
- Revoked attestations invalidate online badge status while retaining immutable audit history.

## Badge trust
Badge is a rendering of a verified attestation lookup, not the evidence itself. Public badge issuance requires a trusted registry lookup and a consented public verification page. Static SVGs may become stale; verification links and live status must indicate revocation/expiry. Never claim an offline static SVG guarantees current status.

## Architectural boundary
Rust CLI/runner/verifier/badge core; optional Python challenge adapters via process protocol; no mandatory VALO Kernel or external agent runtime. Local E2E test evidence and clean-checkout independent reproduction required before public release.
