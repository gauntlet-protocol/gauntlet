# GAUNTLET Governance Charter v0.1 — proposed founding transition

**Status: PROPOSAL / NOT RATIFIED.** This is a public-review candidate for the future Founding Builders community, not evidence that a TSC, Trust Council, Security Team, elections, protected branches or independent key custody already exist. GAUNTLET remains private pending release gates.

## Constitutional purpose
GAUNTLET was initiated by its founder, but it will be governed by its contributors. No individual, company, or vendor shall have permanent unilateral authority over the standard, its evaluation rules, or its trust infrastructure.

GAUNTLET shall be vendor-neutral, locally reproducible and open to challenge authors, maintainers, independent evaluators and builders. Open governance does not expose protected test variants, private participant data or embargoed security findings.

## Authority and boundaries
- **Founding Builders:** propose GIPs, contribute, review and elect community representatives once voter eligibility is ratified. Membership alone does not confer attestation authority.
- **Technical Steering Committee (TSC):** technical roadmap, protocol revisions and release approval, subject to security and trust constraints. Proposed size: five voting members, at least three independent of the founder and VALO. Consensus first; recorded majority vote when consensus fails; conflicted members recuse. Quorum and election mechanics must be ratified before first election.
- **Component Maintainers:** scoped review, local-test evidence and integration; no unilateral override of protected requirements. Ownership is recorded in CODEOWNERS after actual maintainers accept roles.
- **Trust Council:** scoped evaluator/attestor authorization, expiry, revocation and appeals according to the federated trust protocol. Cannot redefine scoring or technical standards by itself. No automatic elevation from TSC membership.
- **Security Team:** documented ability to block releases/merges for a concrete security violation, with confidential disclosure and time-bounded review/appeal; no general roadmap veto.
- **Founder:** one ordinary vote when eligible, with no permanent veto, special certification power or permanent unilateral standard authority. During the unratified bootstrapping period, existing repository administrator powers are a practical concentration of control, not delegated legitimacy.

## Non-bypassable protocol invariants
1. LOCAL never becomes ATTESTED without independently authorized evidence and evaluation.
2. Nobody independently attests their own run, controlled system or affiliate.
3. Evidence integrity, source binding, provenance and current trust status are mandatory.
4. Attestation authority is explicit, scoped, expiring and revocable.
5. No mandatory proprietary service, external agent runtime or vendor dependency in core.
6. Every code change requires locally recorded tests and architecture checks; CI alone is insufficient.

A GIP may propose revising these invariants only as an explicit, versioned protocol change with threat model, independent security review, compatibility/migration analysis and, when guarantees weaken, a new major version. No ordinary vote, merge or exception may silently bypass them.

## GAUNTLET Improvement Proposals (GIPs)
Any contributor may submit a GIP with motivation, precise normative change, alternatives, impact, security analysis, local test plan and migration strategy. Discuss openly except security-sensitive details. TSC decisions and recusals must be recorded in a permanent decision log. Security objections are reasoned, appealable and cannot be silently overridden. Changes to evaluator authority additionally require the Trust Council's scoped procedure. No self-approval for critical governance, trust or security changes.

## Transition milestones — proposed, not accomplished
- **Phase 1, founding:** publish this charter as a proposal alongside a public release when release gates permit; maintain a visible governance ledger and invite GIPs. Record current control concentration rather than claiming independence.
- **Phase 2, formation:** when at least five active, independent maintainers have demonstrated sustained contribution, establish an elected five-seat TSC, at least three independent of founder/VALO; ratify eligibility, election, recall and conflict rules first. Set a published target date within 90 days of the public Founding Builders kickoff to review readiness; if thresholds are unmet, publish reasons and a revised deadline, not a fictional election.
- **Phase 3, community control:** time-limited elected mandates, documented recall, independent Trust Council procedures and distributed administrative custody. Founder may stand for election but receives no reserved seat.

## Control-plane transition and transparency
Before claiming community governance, publish an inventory of actual control over repository ownership, branch protections, domains, release signing keys, evaluator registry, authority roots and legal/trademark assets. Migrate to organization-owned infrastructure with multiple independent administrators, enforce protected branches and independent review, separate signing authorities and create an auditable decision archive. Establish a legal stewardship plan without claiming foundation affiliation.

## Ratification and amendments
This proposal does not grant powers to nonexistent bodies. Ratification requires an openly documented community process after eligibility and independence criteria are agreed. Until then, explicitly label governance as provisional and keep trust/attestation issuance disabled. Future amendments follow GIPs, with elevated scrutiny for constitutional and trust provisions.
