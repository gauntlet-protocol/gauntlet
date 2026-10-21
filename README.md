# GAUNTLET

Vendor-neutral adversarial challenges for AI agents, with reproducible local runs and independently verifiable evidence.

> **v0.1 status: PRIVATE / NOT RELEASED.** The Rust runner and trust enrollment are early implementations. A local PASS is **not** an independently attested result. No public verified badges, evaluator accreditation or GAUNTLET certification are currently issued.

## Start here

| You want to… | Read |
| --- | --- |
| **Contribute** challenges, oracles or code | [Contributor guide](season1/governance/CONTRIBUTING.md) |
| **Join as a Founding Builder** | [Founding Builders program](season1/ecosystem/FOUNDING_BUILDERS.md) |
| **Evaluate or independently verify** a run | [Proof protocol](preview/PROOF_PROTOCOL.md) and [trust architecture](preview/ADR-0002-federated-trust.md) |
| **Become an Authorized Attestor** | [Evaluator and attestor pathway](preview/EVALUATORS.md) |
| **Review governance** and conflicts | [Governance rules](season1/governance/GOVERNANCE.md) |
| **Implement a challenge** | [Challenge protocol](season1/contracts/challenge-protocol.md) and [catalog](season1/README.md) |
| **Integrate governance controls** | [BYOG contract](season1/ecosystem/BYOG_CONTRACT.md) |
| **See release readiness** | [Implementation status](preview/IMPLEMENTATION_STATUS.md) and [release gate](preview/RELEASE_GATE.md) |

## Local development (Rust)

```bash
cargo test --workspace
cargo run -p gauntlet-runner -- run 003 /tmp/gauntlet-capsule.json
cargo run -p gauntlet-runner -- verify-local /tmp/gauntlet-capsule.json
```

The built-in participant for challenge 003 is synthetic. Its result is LOCAL, not an independent verification of a third-party AI system.

External process adapter (trusted local executable only):

```bash
cargo run -p gauntlet-runner -- run-external 003 /tmp/gauntlet-external.json python3 preview/examples/participant.py
```

See [process protocol and limitations](preview/PROCESS_PROTOCOL.md). This example is optional; Rust core does not require Python.

Evaluator key enrollment prototype:

```bash
cargo run -p gauntlet-trust -- key generate /tmp/evaluator.key
cargo run -p gauntlet-trust -- trust request /tmp/evaluator.key evaluator-demo 003 /tmp/evaluator-request.json
cargo run -p gauntlet-trust -- trust verify-request /tmp/evaluator-request.json
```

**Never commit a private key.** A signed enrollment request proves possession of a key; it does not confer authorization to attest.

## Legacy prototypes

The historical CAP-03 detector remains in `capture/cap03/`; see [legacy README](README.txt). Its self-reported inputs are not independent proof.

## Principles

Local-first; Rust core; optional out-of-core adapters; challenge and oracle independence; positive controls; no pay-to-pass; no silent assurance upgrades; no formal ACCREDITED claim without external accreditation.
