# GAUNTLET

Vendor-neutral adversarial challenges for AI agents, with reproducible local runs and independently verifiable evidence.

> **v0.1 status: PUBLIC PREVIEW / NOT RELEASED.** The Rust runner and trust enrollment are early implementations. A local PASS is **not** an independently attested result. No public verified badges, evaluator accreditation or GAUNTLET certification are currently issued.

## Start here

| You want to… | Read |
| --- | --- |
| **Contribute** challenges, oracles or code | [Contributor guide](season1/governance/CONTRIBUTING.md) |
| **Join as a Founding Builder** | [Founding Builders program](season1/ecosystem/FOUNDING_BUILDERS.md) |
| **Evaluate or independently verify** a run | [Proof protocol](preview/PROOF_PROTOCOL.md) and [trust architecture](preview/ADR-0002-federated-trust.md) |
| **Become an Authorized Attestor** | [Evaluator and attestor pathway](preview/EVALUATORS.md) |
| **Review proposed community charter** | [Charter v0.1](governance/CHARTER-v0.1.md), [GIP process](governance/GIP-PROCESS.md) and [control inventory](governance/CONTROL_INVENTORY.md) |
| **Review governance** and conflicts | [Governance rules](season1/governance/GOVERNANCE.md) |
| **Implement a challenge** | [Challenge protocol](season1/contracts/challenge-protocol.md) and [catalog](season1/README.md) |
| **Integrate governance controls** | [BYOG contract](season1/ecosystem/BYOG_CONTRACT.md) |
| **Go from architecture to code** | [Builder starter](starter/architecture-to-code/README.md) |
| **Connect via MCP** | [Experimental read-only MCP adapter](adapters/mcp/README.md) |
| **See release readiness** | [Implementation status](preview/IMPLEMENTATION_STATUS.md) and [release gate](preview/RELEASE_GATE.md) |

## Ten executable challenge fixtures

The runner currently accepts IDs **001–010** (plus experimental 029). Each has a positive control and an adversarial input. These are public, deterministic **synthetic fixtures**, not hidden benchmarks or independent assurance. `run-external` can exercise a trusted participant process, but its result remains LOCAL and the process is not sandboxed. Season 1 manifests are still proposals and are not represented as certified challenges.

## First local smoke test

Requires Rust/Cargo. From the repository root:

```bash
bash scripts/quickstart-local.sh
```

This runs a **synthetic reference participant** against challenge 003 and checks a LOCAL capsule. It does **not** test a third-party agent, validate independent evidence, or issue a VERIFIED/ATTESTED badge. The Season 1 manifest remains `planned`; the executable harness is an early smoke-test implementation, not a released challenge.

To evaluate your own trusted local process, see `run-external` below; it executes your command without sandboxing.

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