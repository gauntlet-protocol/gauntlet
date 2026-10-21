# ADR-0001 — GAUNTLET v0.1 language and runtime boundary

**Status: FROZEN**  
**Decision date:** 2026-10-21  
**Scope:** GAUNTLET v0.1 — Founding Builders Preview

## Binding decision
**Rust-first, Python-enabled, vendor-neutral, local-first.**

- Rust owns CLI, local runner/orchestration, deterministic independent verification, evidence-capsule integrity and verified SVG badge generation.
- JSON Schema and versioned process I/O define the language-neutral challenge contract.
- Python is allowed only as a separately launched, replaceable challenge or external research/benchmark adapter process. It is never a required Rust core dependency.
- No VALO Kernel, HEIMEL, Inspect AI, external agent runtime or vendor SDK may be required to compile, run or test the core.
- At least one real challenge must run end-to-end using a built-in participant **without Python**.
- The v0.1 release must support three real challenges: prompt injection, policy bypass and evaluation-result tampering, with positive controls and independent oracle checks.
- The independent verifier must distinguish participant claims from independently authenticated observations. Missing proof yields INSUFFICIENT_EVIDENCE, not PASS.
- A V-branded GAUNTLET badge must bind to independently verified challenge, contract version, system identity and evidence digest; it cannot be minted from self-attestation.
- All development and changes require an independent local test run, including architecture boundary checks, before merge. GitHub CI is supplementary.

## Architecture direction
Rust CLI -> Rust local runner -> language-neutral process protocol -> Rust independent verifier -> integrity-checked evidence capsule -> Rust SVG badge.

Python challenges and benchmark adapters remain outside the core, opt-in, process-isolated and replaceable.

## Freeze enforcement
This ADR is a normative design freeze, **not** evidence that the implementation or automated enforcement already exists. Any exception requires a separately reviewed ADR revision, explicit architectural justification and a passing local regression suite. Do not silently relax the boundaries to accelerate release. Keep repository private until the v0.1 release gates pass.
