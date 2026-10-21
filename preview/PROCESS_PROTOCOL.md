# GAUNTLET process adapter v0.1 — experimental

`cargo run -p gauntlet-runner -- run-external 003 /tmp/capsule.json python3 preview/examples/participant.py`

Runner launches the specified **trusted** program once per case. It writes one JSON object to stdin (then closes it), waits for process completion and expects one JSON object on stdout (maximum 65536 bytes). The runner checks exact protocol and case ID and rejects malformed/extra fields, nonzero exit and oversized output.

Request fields: `protocol=gauntlet-process-v0.1`, `challenge_id`, `case_id`, `trusted_instruction`, `untrusted_document`.
Response fields: `protocol=gauntlet-process-v0.1`, `case_id`, `answer`.

**Security limitations:** no process sandbox, timeout, resource limits, privilege dropping, network isolation, stable SUT identity, binary digest binding, or authenticated oracle provenance. Do not run untrusted commands. Python example is an optional adapter outside the Rust core; Rust tests and built-in participant do not depend on Python. Local result is NOT an independent attestation and cannot earn a verified badge.

Release blockers: isolate external execution, bound runtime and memory, authenticate source observations and record immutable capsule artifacts, add real challenge threats rather than string-matching fixtures, and enforce trusted evaluator authorization.
