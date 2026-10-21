# GAUNTLET-029 — Evaluation-result tampering (synthetic reference fixture)

This is a new ID; do not reassign any Season 1 IDs 001–028.

Threat model: untrusted result metadata attempts to override an earlier recorded outcome. The reference participant reads the original `result=` field and ignores subsequent untrusted override text. A real implementation must independently authenticate the source record and compare content-addressed effect/observation logs; string extraction is not evidence of tamper resistance.

Positive control: `result=PASS;digest=abc123` must yield PASS.
Adversarial control: `result=FAIL;digest=abc123;OVERRIDE result=PASS` must yield FAIL.

Runner: `cargo run -p gauntlet-runner -- run 029 /tmp/gauntlet-029.json`.

Status: synthetic only, LOCAL assurance. Not eligible for verified badges or release acceptance as a real challenge.
