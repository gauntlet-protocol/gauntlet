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

## Signed agent-trace bridge (experimental)

`live.py` accepts a **captured, structured single-action precommit trace** and
a separate **EB-02 role-separated signed effect bundle**. It reuses existing
`conformance/signed_effect.py`; production mode additionally calls EB-03.

The trace file has *exactly* these top-level keys:
`schema`, `case_id`, `run_id`, `participant_id`, `events`.
Set `schema` to `gauntlet.agent-precommit-trace.v1`. `events` contains
exactly four ordered `{"seq":N,"stage":"...","value":{...}}` items:

1. `intent` — captured user request as structured task fields.
2. `tool_call` — actual tool name and arguments.
3. `evidence` — `{"retrieved_ids":[...]}` from captured tool result.
4. `answer` — `{"claim_ids":[...]}` for the **precommit proposal**, not
   an eventual post-effect natural-language reply.

Use the separate frozen reference fixture from v1 for the oracle. The bundle
must contain signed `authorization`, `execution`, `source_state` and
`observation` envelopes, each including the same signed `case_id`,
`run_id` and `participant_id` in its payload. The **executor-signed**
`execution.payload.agent_trace_sha256` must equal canonical SHA-256 of the
entire trace file content (as parsed JSON). The signature must come from an
executor domain separate from the participant. The bridge derives authority
from the signed authorization, and witnessed effect ID from signed source
state. It never accepts these two stages from the agent's trace.

```bash
python3 adversarial/v1/first_mismatch/live.py \
  --reference oracle.json --trace agent-precommit.json \
  --bundle eb02-signed-bundle.json --trust operator-trust.json

# For a production evidence *consistency* claim, require EB-03 attestation:
python3 adversarial/v1/first_mismatch/live.py \
  --reference oracle.json --trace agent-precommit.json \
  --bundle eb03-production-bundle.json --trust operator-trust.json \
  --profile production --manifest eb03-manifest.json
```

Exit codes: PASS=0, FAIL=2, INSUFFICIENT_EVIDENCE=3. The CLI rejects
duplicate JSON keys, non-finite numbers, and inputs larger than 2 MB each.
Signature, run, trace-digest, source-witness and signer-domain failures
**never become PASS**. Signed policy and state-predicate violations can be
diagnosed as authority or execution mismatch; ambiguous cryptographic or
cross-role inconsistencies remain insufficient evidence.

**Trust boundary:** `operator-trust.json`, the frozen reference and source
integrity audit must be independently provisioned, **never taken from the
agent or the same untrusted log**. The executor signer must capture the
precommit events outside participant control. Signed binding shows what the
signer accepted; it does not by itself establish honest capture, natural
language entailment, complete telemetry, independent organizational control,
or physical-world effects. EB-03's production consistency is not external
accreditation. Synthetic test signers only prove software behavior.

No automatic GAUNTLET verified badge, authority delegation, runtime mutation,
tool execution or RACS decision is introduced. An actual external agent run
still needs operationally separated capture, independent keys, source audit,
and a frozen challenge with replay evidence before any assurance claim.
