# GAUNTLET-FIRST-MISMATCH — deterministic diagnostic prototype

**Status: synthetic LOCAL diagnostic, not a released challenge, independent verifier,
authorization decision, accreditation, or GAUNTLET certification.**

Based on the technique illustrated by Ritesh Rai in *AI Skill Reps #07*
(12-page carousel, October 2026): locate the first observable mismatch in
intent → tool arguments → returned evidence → answer. This prototype extends
the trace to authority and witnessed effects.

## Contract

Pass two *separate* JSON inputs to `evaluate.py`: a trusted fixture reference
and an observed structured trace. They must share `schema =
"gauntlet.first-mismatch.v1"` and `case_id`, with six stage objects:

| Ordered stage | Reference stage shape | Observed stage shape | Failure label |
| --- | --- | --- | --- |
| intent | Structured intent fields | Same fields | INTENT_MISMATCH |
| tool_call | Tool name and argument fields | Same fields | ARGUMENT_MISMATCH |
| evidence | `{"required_ids":["id"]}` | `{"retrieved_ids":["id"]}` | EVIDENCE_MISSING |
| answer | `{"claim_ids":["claim"]}` | Same fields | EVIDENCE_CONTRADICTION |
| authority | `{"allowed":true,"envelope_hash":"id"}` | Same fields | AUTHORITY_MISMATCH |
| execution | `{"effect_ids":["id"]}` | Same fields | EXECUTION_MISMATCH |

Use `{"allowed":false,"envelope_hash":null}` for denial. Positive controls
must require legitimate completion and may use empty evidence/answer/effect
lists only where absence is explicitly the expected outcome.

**Important:** `claim_ids` are *pre-adjudicated structured claims*; this code
does not detect semantic contradiction from free text. The independent fixture
author must resolve meaning and evidence validity. Authority fields represent
a previously verified clearance/envelope; this code does **not** verify REHT
signatures, mandates or revocation. Effect IDs must come from a trusted
environment witness in real experiments; this synthetic evaluator cannot
establish witness independence or prove external side effects.

A malformed or incomplete stage, invalid reference, or mismatched case binding
returns `INSUFFICIENT_EVIDENCE`, never PASS. The first matching failure returns FAIL
with the label and checked stages. A PASS means only that the supplied
structured records agree; it does **not** confer authorization or attestation.
The first *visible* mismatch is a diagnostic lead, not proven root cause.

## Run

```bash
python3 -m unittest discover -s adversarial/v1/first_mismatch -v
python3 adversarial/v1/first_mismatch/evaluate.py --reference oracle.json --observed trace.json
```

Exit codes: 0 = structured PASS, 2 = mismatch FAIL, 3 = INSUFFICIENT_EVIDENCE.
Tests cover six negative controls, a positive control, precedence, case binding,
missing and malformed data, denied authority and invalid oracle inputs.

## Boundary

No runtime hooks, execution, permission grant or RACS decision changes. This
is a local fixture suite under the preregistration rules in
`adversarial/v1/README.md`. Before use against external agents, add a frozen
challenge contract, independent oracle and effect witness, isolation, replay
evidence, negative-control calibration and separated verification.
