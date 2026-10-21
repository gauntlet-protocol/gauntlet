# GAUNTLET v0.1 — Founding Builders Preview

**Status: BLOCKED / PRIVATE.** This document defines acceptance, not release approval.

## Required deliverables
1. One-command local CLI to execute a real challenge.
2. Three executable adversarial challenges: prompt injection (catalog 003), policy bypass (catalog 009 or authority-specific contract), and evaluation-result tampering (new explicit contract; do not silently reassign existing IDs).
3. Independent verifier: authenticated evidence and separation of SUT claims, runner claims and independent observations.
4. Canonical evidence capsule: hashes, provenance, version, seed, environment, oracle, verdict and reproducible replay.
5. V-branded GAUNTLET badge generated **only** from verified result bindings; never from self-report or a CI green check alone.
6. Contribution contracts for challenge authors, adapters and independent oracles.

## Mandatory quality gate
- Keep nsolland/gauntlet PRIVATE until explicit launch approval.
- Inventory and reuse existing conformance/effect_boundary.py, conformance/signed_effect.py, completion/completion.py and production_agents/conformance.py without treating attestation as proof.
- Preserve independent verifier and out-of-core optional integrations; no VALO Kernel or agentruntime hard dependency.
- Local end-to-end tests for all three challenges, including positive controls, malicious variants, corrupted capsule, replay and fail-closed behavior.
- Test on a clean checkout with documented installation steps and no private credentials.
- Verify dependency and data licenses, security and provenance; audit hidden-test handling.
- External reproduction by a second independent operator; record environment and digests.
- No Founding Builders invitations or public verified badge before all gates are green.
- GitHub CI may supplement, never replace, local test evidence.

## Definition of done
A third party can clone, install, run one command, reproduce a challenge, independently verify a capsule and understand the badge's precise scope. All three challenges must have runnable negative and positive controls. Report missing evidence as INSUFFICIENT_EVIDENCE, not PASS.

## Proof protocol prerequisite
Implement and locally verify `PROOF_PROTOCOL.md` and all cases in `PROOF_TEST_MATRIX.md`. A self-issued local result is never independently attested; green badge issuance requires independently trusted ATTESTED PASS. The trust registry and revocation checks are release blockers.

## Federated authorization requirement
Normative: `preview/ADR-0002-federated-trust.md` (relative to repository root). Founding Builder membership and evaluator certification never grant attestation authority. The Rust verifier must validate explicit scoped delegation, independent evaluator identity, full authorization chain, conflict exclusions, evaluation-time validity, current revocation/freshness and separate ATTESTED versus external ACCREDITED claims. Pass `preview/TRUST_TEST_MATRIX.md` locally before public badge issuance. This is not yet implemented.
