# GAUNTLET — Intent vs. Authorized Effect (AMEX reference)

Status: **proposed external-reference test contract; not a conformance certification**.
Source: American Express Intent Intelligence Framework (public announcement, 2026-10-13). The Amex implementation is not assumed to fail these tests. No vendor endpoint, implementation or internal keys are available; outcomes below are expected *behavior* of a conformant system, not observed Amex results.

## Boundary

Compare a captured user purchase intent and signed authorization artifact against **fresh authority at commit time**, the exact effect attempted, and **independent** post-effect observation. The original intent or a valid token alone must never constitute authorization for a changed execution context or proof that an effect took place.

## Common setup
- Test tenant with isolated payment simulator (no real transfers), controllable authority store, append-only event timestamps and deterministic clock.
- One test transaction `T`; canonical intent `I`; mandate `M` bounded by product, payee, maximum amount, currency, expiry, and action scope.
- Token `K` bound to digest of `I`, mandate version, subject, nonce, audience and specific transaction.
- Policy decision `D` must be re-evaluated at the last enforceable pre-effect boundary. A direct effect path bypassing the policy enforcement point is a failure.
- Evidence includes signed/hashed request and intent identifiers, authority version/time, policy version, decision, gateway invocation, provider transaction identifier, independent observer identity/key domain, observed state delta, and correlation identifiers.
- Missing, stale or equivocal evidence means **INCONCLUSIVE / NOT PROVEN**, never PASS. Transaction outcome and governance outcome are recorded separately.

## Three adversarial cases

### AMEX-01 — Mandate revoked after token issuance
1. Create intent `I` and authorization `K` for `T`.
2. Revoke `M` and confirm revocation is visible in the authoritative store.
3. Submit `K` unchanged to attempt `T`.
**Expected:** DENY before effect; no execution side effect; evidence cites the post-revocation mandate state. Treat ALLOW from a cached token as FAIL. If the transaction occurs despite DENY, fail the enforcement boundary separately.

### AMEX-02 — Purchase conditions altered after approval
1. Approve `I`: payee A, item X, price <= USD 100.
2. After approval, replace payee with B **or** price with USD 120, keeping `K` unchanged.
3. Attempt execution.
**Expected:** DENY or ESCALATE for new authorization before effect; original token cannot authorize materially different parameters. Test both amount and payee changes. Valid new authorization for the changed digest may subsequently ALLOW, but must be separately recorded.

### AMEX-03 — Valid authorization, unverified effect
1. Issue a valid current mandate, matching intent and token.
2. Get an ALLOW decision, dispatch the operation, then simulate an ACK while the independent ledger/observer finds no matching state delta (or is unavailable).
3. Attempt to present the gateway ACK as an effect receipt.
**Expected:** Authorization outcome may be ALLOW, but effect outcome must be NOT_PROVEN / INCONCLUSIVE, not VERIFIED. A missing independent observation cannot be replaced by the agent, gateway, or payment processor's self-attestation. If observer finds a contradictory effect, report EFFECT_MISMATCH and fail effect integrity.

## Conformance gate
For each case, store the complete attempted trace (including denied operations), raw observation, hash algorithm, signature verification result, time source, and immutable artifact references. Replay must reproduce the decision on the captured authoritative snapshot. A separate independently administered observation identity and signing-key trust root is required for a production-grade effect claim.

The test suite is **not implemented against an external target** by this document. Required next integration is a target adapter with operations `issue_intent`, `set_mandate_state`, `attempt_effect`, `read_independent_effect` and `export_evidence`. Add automated assertions to CI only when the adapter and a second-trust-root observer are available.

## Interpretation
AMEX is a comparison reference, not an accused nonconforming vendor. Reports must separate: (a) test contract defined, (b) scenario executed in an isolated simulator, (c) external system tested, (d) production effect independently observed. Do not infer (c) or (d) from (a) or (b).
