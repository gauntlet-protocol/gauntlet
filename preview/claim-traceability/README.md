# Claim-to-attestation traceability contract v0.1

**Status: proposed schema and local validation, NOT an implemented GAUNTLET verifier or attestation authority.** Inspired by the distinction between product-scoped documentation and tested behavior; no Breeple integration or dependency.

The chain is CLAIM → CONTRACT → EXECUTION → EVIDENCE → VERIFICATION → ATTESTATION. Each record has an explicit object type, identifier, subject binding, version/scope and upstream reference. The existence of an object does not imply the next stage. In particular, document signatures only support integrity/provenance; a verification statement must record the verification method, and an attestation needs an independently authorized evaluator per `preview/ADR-0002-federated-trust.md`.

`claim-chain.schema.json` defines an exchange envelope, not a trust decision. `validate.py` checks schema-like structure and exact referential binding using only Python standard library; it does not validate signatures, canonical evidence digests, independent evaluation or test outcomes. Its successful exit means `STRUCTURALLY_VALID_UNVERIFIED` only.

## Boundaries
- Product identity, product version, environment and validity scope are explicit. No cross-product, cross-version or cross-environment inheritance.
- Each contract names a challenge ID and contract version; execution names its contract and actual run; evidence names the exact execution and artifact digest; verification names the evidence; attestation names the verification and independent evaluator.
- `LOCAL`, `VERIFIED`, `ATTESTED` are assurance classes, not inferred from chain completeness. No badge or PASS from this envelope.
- Source documents and vendor imports belong in optional adapters; no mandatory external runtime or proprietary service in core.
- Source links and claims are untrusted inputs, not proof. Never execute a source document.
