# External research adoption register

Adoption means **explicitly choosing methods, contracts and interoperability targets**, not vendoring third-party code. No framework is a GAUNTLET core dependency. All integrations are optional, out-of-process adapters.

## Priority register
| Project | Intended adoption | Challenge mapping | Gate |
|---|---|---|---|
| Inspect AI | Task/scorer interface, traces, external agent bridge | all | license, version pin, two-system interoperability |
| AgentDojo | Legitimate user objective vs attacker objective vs outcome | 003,009,015 | license, attack taxonomy, reproducibility |
| AgentLAB | Long-horizon adaptive adversary | 009,011,013,015 | paper/code verification, reproducibility |
| tau2-bench | Stateful user/policy/tool simulation | 001,008,019,021 | license, state oracle |
| OSWorld / BrowserGym | Isolated computer/browser environments | 005,010,021 | sandbox and effect observation |
| ProEvolve / SchemaDrift-120 | Consistent tool/schema mutations | 021,022,026 | source verification, deterministic mutation |
| AgentWorld | Causal collaboration measurement | 012,013,023,024 | method reproduction |
| LongMINT | Contradictory/updated long-term memory | 011,027,028 | data license and ground truth |
| Terminal-Bench / Harbor | Operational robustness interoperability | optional | external adapter |
| METR RE-Bench | Long-horizon task format | optional | external adapter |
| OWASP Agentic Top 10 | Threat coverage taxonomy | all | versioned mapping |

## Research verification
Each project is **candidate**, not adopted source code. Record verified repository/paper URL, license SPDX and compatibility, revision, dataset terms, maintenance, dependency risks, reproduction evidence and decision before importing or running. Never claim a published benchmark's results are GAUNTLET verified.

## Integration rule
External framework -> optional adapter -> GAUNTLET public challenge protocol. The kernel cannot import Inspect, AgentDojo, VALO, HEIMEL or any third-party agent SDK. No copied code until provenance and license checks are completed.
