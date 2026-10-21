# Evaluators, verifiers and authorized attestors

**Status: invitation and authorization workflow not yet operational.** Do not interpret this page as an application portal, approved evaluator registry, or authorization grant.

## Roles

- **Founding Builder:** contributes challenges, code and local test runs. Membership does not grant verification or signing privileges.
- **Certified Evaluator:** competence has been assessed for named domains. Competence alone is not authorization.
- **Authorized Attestor:** may sign attestations only with a current, independently delegated authorization for named challenge IDs and versions, domains, subjects and validity periods.
- **Trust Authority:** may delegate and revoke rights only within its own authority.
- **Governance Council:** governs admission rules and independent oversight.

## Intended pathway

1. Read [Founding Builders](../season1/ecosystem/FOUNDING_BUILDERS.md), [contributor requirements](../season1/governance/CONTRIBUTING.md) and [federated trust ADR](ADR-0002-federated-trust.md).
2. Contribute or independently reproduce a public challenge, with positive controls and raw local evidence.
3. Demonstrate relevant technical competence, legal/organizational identity and disclosed affiliations or conflicts.
4. Generate your Ed25519 signing key **locally** and submit only the public key and a signed proof-of-possession request. Never send the private key.
5. A separately authorized Trust Authority reviews competence, independence, requested scope and eligibility. No automatic approval.
6. Only after explicit signed, time-limited, revocable delegation may an Authorized Attestor issue recognized attestations. Every verification checks the full trust chain and current revocation state.

## Verification versus attestation

A local verifier may validate a result's format and internal consistency, but it cannot establish independence merely by verifying a self-issued signature. Independent attestation requires a distinct trusted operator and authenticated observations or reproduction. [Proof protocol](PROOF_PROTOCOL.md) and [proof test matrix](PROOF_TEST_MATRIX.md) define acceptance.

An **ATTESTED** result is not automatically **ACCREDITED**. No public verified badge may be issued before the release gates pass.

## Security and impartiality

An evaluator must not attest its own system, own run, or a controlled affiliate's result. Two different keys do not establish organizational independence. Conflict data, challenge scope, delegation validity, expiry, revocation and registry freshness must be checked by the Rust verifier. See [trust test matrix](TRUST_TEST_MATRIX.md).

There is currently **no application endpoint, public trust registry or authorized attestor enrollment service**. These will be published only after implementation and independent testing.
