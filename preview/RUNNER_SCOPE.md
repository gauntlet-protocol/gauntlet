# Runner status and remaining challenge work

The current Rust CLI executes deterministic built-in synthetic reference fixtures for challenge IDs 003 (prompt injection), 009 (policy bypass), and 029 (result tampering). These are smoke tests of local dispatch, simple controls and verdict logic, **not real adversarial AI-agent evaluations**. The reference participant is embedded in the runner, so independence and external SUT execution are absent.

The `verify-local` command re-evaluates verdict against participant-controlled observations. It detects an inconsistent verdict but **cannot detect a forged, internally consistent capsule**. `runner_digest` hashes source bytes, not a trusted build provenance statement; `cases_sha256` is not an authenticated oracle commitment. No capsule signature, attestation or independent effect proof is provided.

Before release, replace these fixtures with a versioned process protocol that launches external systems under test, records independent oracle observations, proves artifact integrity and applies full attestor authorization and revocation validation. Preserve positive controls and add executable tampering and replay negatives. The release gate remains BLOCKED.
