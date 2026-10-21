#!/usr/bin/env python3
"""Offline evidence bundle verifier; does not confer independent attestation.
Signer and verifier must be operationally separated for independent assurance.
"""
import argparse,base64,hashlib,json,pathlib,sys
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey,Ed25519PublicKey

def canonical(data):return json.dumps(data,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
def digest(data):return hashlib.sha256(data).hexdigest()
def create_bundle(evidence:bytes,private_key:Ed25519PrivateKey):
 public=private_key.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)
 payload={'schema':'gauntlet.evidence-bundle.v1','assurance':'LOCAL_EXECUTED','evidence_sha256':digest(evidence),'evidence_base64':base64.b64encode(evidence).decode(),'signer_public_key':base64.b64encode(public).decode()}
 return {'payload':payload,'signature':base64.b64encode(private_key.sign(canonical(payload))).decode()}
def verify(bundle, trusted_public_key:bytes):
 if not isinstance(bundle,dict) or set(bundle)!={'payload','signature'}:raise ValueError('invalid_bundle')
 p=bundle['payload']
 if not isinstance(p,dict) or set(p)!={'schema','assurance','evidence_sha256','evidence_base64','signer_public_key'}:raise ValueError('invalid_payload')
 if p['schema']!='gauntlet.evidence-bundle.v1' or p['assurance']!='LOCAL_EXECUTED':raise ValueError('unsupported_assurance')
 key=base64.b64decode(p['signer_public_key'],validate=True)
 if key!=trusted_public_key:raise ValueError('untrusted_signer')
 evidence=base64.b64decode(p['evidence_base64'],validate=True)
 if digest(evidence)!=p['evidence_sha256']:raise ValueError('evidence_digest_mismatch')
 try:Ed25519PublicKey.from_public_bytes(key).verify(base64.b64decode(bundle['signature'],validate=True),canonical(p))
 except InvalidSignature as exc:raise ValueError('invalid_signature') from exc
 return {'signature_valid':True,'digest_valid':True,'evidence_sha256':p['evidence_sha256'],'assurance':'LOCAL_EXECUTED','independent_attestation':False}
def main():
 parser=argparse.ArgumentParser();parser.add_argument('bundle',type=pathlib.Path);parser.add_argument('--trusted-public-key',required=True,type=pathlib.Path);args=parser.parse_args()
 key=bytes.fromhex(args.trusted_public_key.read_text().strip())
 try:print(json.dumps(verify(json.loads(args.bundle.read_text()),key),indent=2));return 0
 except (ValueError,KeyError,TypeError) as exc:print('REJECTED',str(exc),file=sys.stderr);return 1
if __name__=='__main__':sys.exit(main())