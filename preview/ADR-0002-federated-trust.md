# ADR-0002 — Federated GAUNTLET trust architecture

Status: FROZEN DESIGN (implementation and validation pending)
Date: 2026-10-21
Scope: GAUNTLET v0.1

## Roles and powers
- Founding Builder: may contribute challenges, code and local test results. No attestation authority.
- Certified Evaluator: assessed competence in named challenge domains. No signing authority solely from certification.
- Authorized Attestor: has a separately delegated, scope-limited, time-bound, revocable signing capability.
- Trust Authority: can approve, delegate and revoke authorized attestors only within its own delegated authority.
- Governance Council: owns public protocol and oversight rules, not automatic adjudication of a participant's own result.

## Federation and explicit roots
A verifier accepts only configured trust roots and validated chains. Federation does not mean accepting arbitrary self-declared trust authorities. Roots and delegated authorities must be independently governed, auditable and replaceable. A Trust Authority cannot enlarge its delegated scope or grant beyond its expiry. Delegation must be explicit; no ambient authority from membership or job title.

## Authorization envelope
Every delegation binds: delegation ID; issuer and subject public-key IDs; permitted actions (EVALUATE, ATTEST, DELEGATE, REVOKE); challenge IDs and version ranges; domain and protocol versions; permitted system/organization scope; excluded affiliated systems and organizations; not-before and expiry; maximum delegation depth; parent delegation digest; policy version; conflict disclosures; signature over domain-separated canonical bytes.

Verifier must check every link from configured trust root, issuer authority and scope subset, cryptographic signatures, delegation depth, non-escalation, evaluation-time validity and current revocation state. Missing data fails closed.

## Independence and conflicts
The SUT operator, build owner, run operator, evaluator, attestor and relevant controlling organizations must be identified by stable, verifiable identities. Evaluators cannot independently attest their own SUT, own run, employer/controlled affiliate, or challenge result where their role creates a material conflict. Challenge authorship alone does not automatically prohibit evaluating unrelated systems, but material conflicts must be adjudicated. Merely different key IDs are not evidence of organizational independence.

## Attestation
An attestation binds to exact evidence capsule digest, SUT digest, challenge/version, evaluation timestamp, evaluator identity, authorization-chain digest, independent method, outcome, positive controls, oracle observations and domain-separated Ed25519 signature. Distinguish signing time from evaluation time and enforce both applicable validity windows.

## Revocation and freshness
Maintain append-only signed revocation events for keys, delegations and attestations. Verify historical authority at evaluation time AND current trust/revocation state at verification time. Revocation policies must distinguish prospective suspension and retroactive invalidation, record effective timestamps and reasons, and prevent rollback via monotonic registry checkpoint/version and freshness bound. Offline checks may report a historical proof but cannot claim current unrevoked status without sufficiently fresh authenticated registry data.

## Assurance and accreditation
LOCAL, VERIFIED and ATTESTED are technical evidence assurance levels. ACCREDITED is not a GAUNTLET assurance level and must only be displayed when externally established and independently documented. An ATTESTED PASS does not imply ACCREDITED.

## Architecture and release
Rust verifier enforces chain, scope, conflict, signature and revocation checks. Python adapters are optional. No VALO Kernel or external agentruntime core dependency. No green public badge without valid ATTESTED PASS and current trust state. Keep repository private until independent local tests and release gates pass.

Any change to this ADR requires a new reviewed ADR and local regression evidence.
