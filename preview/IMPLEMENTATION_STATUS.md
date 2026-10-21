# GAUNTLET v0.1 — verified implementation status

Date: 2026-10-21. Release: BLOCKED / PRIVATE.

## Implemented and locally exercised
- Rust `gauntlet-trust` key generate, proof-of-possession request and request verification.
- Ed25519 signing keys generated locally with private file mode 0600 on Unix; no private keys are uploaded by these commands.
- `cargo test --manifest-path crates/gauntlet-trust/Cargo.toml`: 2 passed, 0 failed.
- Local CLI smoke: key generate -> trust request -> trust verify-request succeeded; changing subject rejected.
- This is **enrollment request verification only**, not authority delegation or attestation.

## Unimplemented release blockers (in dependency order)
1. Rust workspace and versioned language-neutral challenge I/O; boundary regression guard (no mandatory Python, VALO or external runtime).
2. Rust runner and independent oracle with one real end-to-end challenge without Python.
3. Three executable challenges: prompt injection 003, policy bypass with explicit catalog binding, result tampering with a new unique ID; positive and adversarial controls.
4. Canonical capsule, content-addressed artifacts, replay and independent observation authenticity; tamper and missing-evidence rejection.
5. Rust verifier: signed evaluator authorization chains, scope and non-escalation, trust roots, identity/independence checks, evaluation-time validity, registry freshness, revocation and conflict-of-interest fail-closed handling.
6. Independent attestation envelope, signatures bound to exact capsule digest and a distinct trusted operator; ATTESTED vs external ACCREDITED separation.
7. V SVG badge gated on currently valid ATTESTED PASS, including expiry/revocation-safe verification URL.
8. Local negative tests for all cases in PROOF_TEST_MATRIX.md and TRUST_TEST_MATRIX.md, clean-checkout reproduction and evidence logs.
9. Security and dependency/license audit, independent second-operator reproduction and explicit launch approval.

## Non-goals for v0.1
Full 28-challenge catalog, paid certification, cloud-hosted runner, vendor adapters in core, and claiming formal accreditation without external authority.

## Release decision
No public verified badges, no authorization grants to Founding Builders and no release announcement until gates are demonstrably green.

## Update: synthetic challenge dispatch
Three Rust synthetic reference fixtures (003, 009, 029) now run locally; these are NOT completed real challenges. See `RUNNER_SCOPE.md`. Seven Rust unit tests pass locally. External SUT protocol, independent oracle and trusted evidence are still blocked.
