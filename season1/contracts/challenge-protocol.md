# Challenge protocol v0 — design contract, not implemented runtime

Inputs: challenge_id, contract_version, scenario_id, variant_visibility (public/hidden), seed, participant descriptor, permitted actions, authoritative state, positive controls, oracle specification, environment digest.

Execution: isolate participant, apply deterministic adversarial mutations, capture tool and communication traces, check both legitimate success and forbidden outcomes, collect independent state observations.

Outputs: challenge_id, variant_id, verdict (PASS/FAIL/INSUFFICIENT_EVIDENCE), assurance_level (L0–L3), oracle_id, environment digest, signed evidence references where available, failure layer, and replay inputs.

Do not embed hidden variants in public participant artifacts. Separate scenario generation from independent adjudication. Semantics: equivalence and meaning-changing minimal pairs. Speech: transcription, interpretation, authorization and effect must be scored separately. Compound scenarios are compositions of existing challenge IDs, not substitutes for per-challenge outcomes.
