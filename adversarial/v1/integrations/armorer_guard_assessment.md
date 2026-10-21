# Armorer Guard – integration assessment (2026-10-21)

Source: https://github.com/ArmorerLabs/Armorer-Guard (public MIT-licensed SDK and contracts).

## Boundary
The public repository exposes Python/Node clients, schema, adapters and tests. It does **not** ship the Guard runtime, ML models, proprietary policies, or reviewer. SDK unit tests do not demonstrate protection efficacy. No Guard authorization or independent attestation is claimed.

## GAUNTLET evaluation protocol
1. Pin a commit and validate the public schema and client error handling offline.
2. Exercise negative controls: missing/invalid authorization, replayed one-use token, mismatched effect/resource, absent execution receipt, compromised agent direct credential attempt.
3. If a separately provisioned runtime is supplied, evaluate denial and false-positive rates against frozen challenge corpus, with baseline and latency/cost metrics.
4. Keep agent-neutral adapters outside the GAUNTLET authority core. External guard decisions are observations, never GAUNTLET VERIFIED verdicts.

## HEIMEL/VALO relevance
Credential-owning effect gateway and execution receipt are suitable design references; do not import a proprietary runtime as a governance authority.

## Status
SDK-only evaluation; runtime unavailable, efficacy INCONCLUSIVE. No automatic adoption.