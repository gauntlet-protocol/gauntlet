# THE GAUNTLET — Governance policy v0.1

Status: adopted project policy; operational enforcement pending implementation and independent validation.

## Mission and openness
GAUNTLET is an open, vendor-neutral adversarial evaluation protocol. The public challenge contract, scoring rules, evidence formats, version history and reference implementation are intended to be open. Hidden adversarial variants and protected test material remain confidential to preserve evaluation integrity. Openness does not authorize publication of exploitable vulnerabilities or participants' private data.

## Constituencies
Developers and academic researchers are first-class contributors and users. Enterprise procurement and assurance adoption follows demonstrably reproducible independent results. No exclusive vendor runtime, model provider, VALO/HEIMEL integration or commercial contract may be a core requirement.

## Separation of duties
Challenge authors define a threat model and positive/negative controls. Runner operators execute in isolation. Independent oracle maintainers validate outcomes. Release reviewers inspect evidence and provenance. For any verified claim, the same actor must not unilaterally author the scenario, execute the participant, approve the oracle and publish PASS. Conflicts of interest are disclosed and reviewed.

## Result integrity
Verdicts: PASS, FAIL, INSUFFICIENT_EVIDENCE. Evidence classes L0–L3 are not a global safety score. No PASS from self-report alone, no PASS from deny-all behavior, no silent suppression of critical failures, and no external-effect PASS without authoritative independent observation. Results bind to challenge ID, contract version, variant commitment, system version, environment, oracle and evidence digest. A badge without this binding is not a verified certification.

## Challenge governance
Each proposal includes ownership, upstream attribution, threat model, source/data licenses, deterministic replay inputs, controls, independent oracle and appeal procedure. Reviewers must reject benchmark leakage, unverifiable outcomes and external adapters imported into core. Public challenges and hidden variants are versioned separately; breaking changes require a new version. Old results remain labeled with their original versions.

## Publication and appeals
Publish the evaluation methodology and challenge contract before accepting verified public results. Maintain a documented correction, dispute and revocation path with immutable revision history. Responsible disclosure and participant privacy take precedence over public release of attack payloads.

## Commercial independence
Fees, if any, may cover infrastructure, execution or audits but cannot purchase PASS, preferential scoring, secret advance access or ranking changes. Sponsors and benchmark maintainers do not override adjudication.

## Local-first quality gate
Every code iteration requires an independent **local** runner pass before approval. Tests must check architectural dependency direction, contract validation, positive controls, evidence verification, deterministic replay and failure behavior. GitHub CI is supplementary, not a substitute. No merge or green claim without recorded local execution evidence. Fail closed on missing evidence, but do not confuse that with a PASS for a deny-all participant.
