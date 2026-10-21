# Bring Your Own Governance (BYOG) — interoperability contract v0.1

Status: design specification; no adapter or benchmark result is implemented.

## Participants
- System under test (SUT): agent/runtime plus optional governance control.
- Governance provider: policy, identity, guardrail, monitoring or other independent component.
- GAUNTLET runner: isolated test coordinator.
- Oracle: independent authoritative evaluation of legitimate success and forbidden effects.

## Comparison design
Run a baseline configuration and a governance-enabled configuration under equivalent task, authorized state, adversarial variant, seed, tool capability and environment. Record any unavoidable differences. Pair runs by scenario and seed; do not compare unlike configurations or infer causal impact without controlled conditions.

## Required inputs
Challenge ID and version; system build digest; governance component identity/version/config digest; adapter version; policy snapshot; authorization state; scenario seed; expected permitted outcomes; forbidden effects; oracle specification; environment and dependency digests; consent and data-handling constraints.

## Required outputs
Per-run PASS / FAIL / INSUFFICIENT_EVIDENCE; positive-control success; negative-control results; independent effect observations where relevant; false-block rate; prohibited-effect rate; failure stage; raw replay references; evidence assurance class; comparison uncertainty.

## Safety and fairness
Deny-all cannot pass. A governance control that prevents all legitimate work fails positive controls. Report both safety and utility; no single headline improvement obscures regressions. Self-reported prevention does not prove absence of effect. Never run dangerous effects on live production systems; use authorized sandbox fixtures and explicit consent for external effect observation.

## Architecture
SUT/governance -> optional external adapter -> public GAUNTLET protocol -> isolated runner -> independent oracle -> evidence verifier. No reverse dependency from core into an external vendor SDK. Adapter must be removable without changing challenge definitions.

## Publication
Publish only consented, independently verified comparisons. Preserve raw baseline and protected results with versioned provenance. Public badges bind to actual challenge IDs, versions, system digests and verification levels, and expire or are revoked when material evidence is invalidated.
