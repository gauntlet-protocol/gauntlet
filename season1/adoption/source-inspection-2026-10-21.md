# Source-level adoption inspection — 2026-10-21

## Locally cloned, pinned upstream
| Project | Exact inspected SHA | Python constraint | License |
|---|---|---|---|
| Inspect AI | `9868e105fa6eb371395a909b9709423c92a88512` | >=3.11 | MIT |
| AgentDojo | `357c80dea9af34323f709c3505d9e6d224654c7e` | >=3.11 | MIT |
| tau2-bench | `57e54143025bec219b5726884651c98eede202e2` | >=3.12,<3.14 | MIT |

Cloned into an isolated /tmp audit workspace on the authorized local machine, **not** into the GAUNTLET core. Verified SHA via git rev-parse HEAD. Python modules inspect_ai, agentdojo and tau2 were not installed in the active environment. The inspection did **not** run any upstream tests; a Python unittest discovery against a deliberately nonexistent pattern ran 0 tests and must not be represented as test success.

## License corrections
- ServiceNow/BrowserGym GitHub license API returned NOASSERTION, but upstream root LICENSE contains Apache License 2.0 notice.
- METR/RE-Bench GitHub license API returned NOASSERTION, but upstream root LICENSE contains MIT license; repository is archived.
- These are root code licenses only; dependency and dataset terms remain unverified.

## Decision
**Approved for method-level study only**, not for vendoring or certification. Next technical gate: isolated installation and reproducible smoke tests at pinned SHAs, with stdout, exit codes, dependency lockfiles and environment hashes. Prefer Inspect AI first; then AgentDojo; tau2-bench requires separate Python 3.12/3.13 environment. Do not claim compatibility or successful upstream test execution until actually measured.
