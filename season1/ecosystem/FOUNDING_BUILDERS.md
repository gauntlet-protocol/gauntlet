# GAUNTLET Founding Builders Program — proposal v0.1

## Purpose
Recruit independent governance, identity, policy, security, observability and agent-framework builders as contributors and early interoperable participants. Their users should be able to evaluate governance controls independently through GAUNTLET. No partnership or endorsement is implied by listing a candidate.

## Open participation
The challenge protocol, integration specification, public cases, scoring rules and evidence schemas are open. Hidden variants and participant secrets are protected. Participation is free to propose and does not require purchasing services, transferring IP, adopting a particular runtime, or using a proprietary cloud.

## Contribution tracks
- Challenge author: contribute attack cases, positive controls, threat models and reproducibility evidence.
- Integration maintainer: provide an optional out-of-core adapter for a governance system.
- Independent evaluator: reproduce results, review oracles and adjudicate disputes.
- Design partner: run the same public challenge against baseline and governance-enabled configurations with explicit consent.

## Governance and conflicts
Partners may contribute scenarios but may not unilaterally adjudicate their own results. Disclose financial and technical conflicts. Never give founding members advance access to hidden variants, privileged scoring, guaranteed PASS, preferential rankings or exemptions. No endorsement or certification until independent verification.

## Entry gates
1. Identify real maintainer and repository/product; obtain consent before naming as partner.
2. Document integration surface, licensing, security and privacy constraints.
3. Run locally using neutral GAUNTLET contract and optional adapter, without kernel dependencies.
4. Demonstrate legitimate-task positive controls and at least one adversarial negative control.
5. Independently verify and reproduce results before publishing a badge.

## Outreach stages
candidate -> contacted -> interested -> technical evaluation -> independently verified participant -> public reference (only with consent). A candidate is never presented as a confirmed partner.

## Initial candidate categories (uncontacted)
Policy: Open Policy Agent, Cedar. Security: NVIDIA NeMo Guardrails, Lakera Guard. Observability: Langfuse, Arize Phoenix. Agent frameworks: LangGraph, CrewAI. Standards/research: OWASP, Cloud Security Alliance. These are ecosystem research targets, not partners or endorsements.

## Growth measurement
Track qualified candidates, confirmed technical integrations, independent reproductions, repeat evaluation by distinct organizations, and procurement usage. Do not count GitHub stars or badges alone as verified adoption.

## Federated authorization requirement
Normative: `preview/ADR-0002-federated-trust.md` (relative to repository root). Founding Builder membership and evaluator certification never grant attestation authority. The Rust verifier must validate explicit scoped delegation, independent evaluator identity, full authorization chain, conflict exclusions, evaluation-time validity, current revocation/freshness and separate ATTESTED versus external ACCREDITED claims. Pass `preview/TRUST_TEST_MATRIX.md` locally before public badge issuance. This is not yet implemented.
