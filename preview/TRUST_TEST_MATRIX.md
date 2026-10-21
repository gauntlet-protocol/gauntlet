# Federated trust negative-test matrix

Specification only; no tests claimed executed.

| Scenario | Required result |
|---|---|
| Founding Builder membership alone | no attestation authority |
| Certified Evaluator without delegation | no attestation authority |
| Authorized Attestor with scoped valid chain | eligible for ATTESTED only if independent proof also passes |
| Self-signed root not configured by verifier | reject |
| Trust Authority delegates outside parent challenge/version scope | reject |
| Delegation exceeds parent expiry or maximum depth | reject |
| Unauthorized DELEGATE permission | reject |
| Attestor owns SUT or controlled affiliate | reject |
| Attestor operated the evaluated run | reject |
| Two keys controlled by same organization used to fake independence | reject |
| Attestation valid at evaluation but currently revoked retroactively | reject current badge |
| Expired key at evaluation time | reject |
| Expired attestation at verification time | reject current badge |
| Old signed revocation snapshot replayed | reject current status or INSUFFICIENT_EVIDENCE |
| No current registry access and stale snapshot | historical proof only, no current green badge |
| Unknown or unverifiable conflict-of-interest data | INSUFFICIENT_EVIDENCE |
| Valid ATTESTED FAIL | no PASS badge |
| ATTESTED PASS with no external accreditation | display ATTESTED, never ACCREDITED |
| Forged accreditation metadata | reject ACCREDITED label |

Tests must run locally on a clean checkout, include positive controls and capture toolchain, input vectors, output and digests before release.
