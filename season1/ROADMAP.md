# THE GAUNTLET — Adoption and verification roadmap

Decision: openness=open; audiences=developers + researchers first, enterprise thereafter; launch=quality. This is a plan, not a claim of completed delivery. Dates are relative to execution kickoff.

## Gate 0 — audit before additional engines (P0)
Inventory existing GAUNTLET code, all 28 challenge manifests and original legacy GAUNTLET-001 protocol. Verify upstream licenses, exact revisions, data restrictions, maintenance and independent-oracle methods. Map rather than duplicate. Publish adoption decision log. **Exit:** reviewed dependency graph, upstream evidence and identified gaps.

## Gate 1 — protocol and local runner (P0)
Freeze versioned challenge/evidence contract and stable IDs. Implement smallest vendor-neutral local runner and contract tests. Rust for security-critical deterministic verification where justified; Python benchmark tools remain optional external integrations. Require positive controls, independent oracle and reproducible evidence. **Exit:** local test artifacts with commands, exit codes, seeds, environment and digests; no unverified PASS.

## Gate 2 — two-system interoperability (P0)
Use one optional Inspect AI adapter outside core; validate the same neutral contract against two independent systems under test. Run negative and positive controls. **Exit:** reproducible independent local executions and documented failure cases.

## Gate 3 — one verified public challenge (P0 launch gate)
Implement exactly one fully evaluated challenge, reconcile legacy GAUNTLET-001 numbering, test adversarial variants and oracle independence, publish an appeal process. **Exit:** third-party reproduction of a verified result and badge that binds to challenge/version/evidence. No mass badge launch before this gate.

## Gate 4 — researcher/developer adoption (P1)
Open contribution guidelines, reference CLI, documentation, challenge submissions, multilingual/speech profiles, optional benchmark adapters, and community review. Publish per-challenge leaderboard without hiding critical failures. **Exit:** external contributors and independently reproduced submissions.

## Gate 5 — enterprise adoption (P1)
Add procurement-friendly evidence bundles, controlled/private evaluation, versioned assurance reporting and independent auditing without preferential scoring. **Exit:** actual procurement or vendor-assurance use, not vanity metrics.

## Metrics (proposed 12-month ambitions, not forecasts)
- 100+ independently participating agent projects with valid reproducible runs
- 25+ external contributors with accepted evaluation contributions
- 10+ optional integrations, zero external agent SDKs in core
- 5+ organizations requesting GAUNTLET evidence in real procurement/evaluation

North-star: **Verified Adoption** = distinct external projects that repeat a valid GAUNTLET run and demonstrably use its outcome in a technical decision. Track reproducibility rate, appeal/correction rate, time-to-first-local-run, oracle disagreement and critical failure visibility.

## Non-negotiable release gates
No draft-as-done; no skipped-test-as-green; no synthetic evidence presented as external effect; no integration dependency in core; no leaderboard claim without versioned reproducible evidence. Every iteration must pass a separate local run and architecture boundary checks before merge.
