# Proof and attestation acceptance matrix

This is a required test plan, not a test execution report.

| Case | Expected |
|---|---|
| valid local run + intact capsule | LOCAL verdict only |
| participant self-signs attestation | never ATTESTED |
| independent trusted evaluator signs bound capsule after reproduction | ATTESTED with underlying verdict |
| tamper one byte of artifact | INSUFFICIENT_EVIDENCE |
| swap SUT/challenge/runner digest | INSUFFICIENT_EVIDENCE |
| unknown evaluator key | INSUFFICIENT_EVIDENCE |
| revoked evaluator key | INSUFFICIENT_EVIDENCE |
| expired attestation | INSUFFICIENT_EVIDENCE |
| replay signed envelope on other capsule | INSUFFICIENT_EVIDENCE |
| deny-all governance | FAIL positive control |
| incomplete observer coverage | INSUFFICIENT_EVIDENCE for external-effect claim |
| failed challenge with valid attestation | ATTESTED FAIL, never PASS |
| invalid signature + static green badge | no trusted green status |

Local acceptance requires executable automated tests for each row, reproducible commands, recorded toolchain versions, and raw test output. All release gates remain BLOCKED until evidence is available.
