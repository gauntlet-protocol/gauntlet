# THE GAUNTLET — Season 1

Vendor-neutral adversarial challenge registry. This is a **skeleton**, not 28 implemented challenges.

Each challenge is independent, with a stable identifier and one machine-readable manifest. `planned` means no runnable evaluator or verified result exists. The original GAUNTLET conformance, capture, completion and production-agent packages remain unchanged.

## Disciplines
Authority, Semantics, Effects, Tools, Communication, Memory/Knowledge. Cross-cutting concerns include provenance, evidence integrity, reference validity, and cache freshness.

## Verdicts
`PASS`, `FAIL`, `INSUFFICIENT_EVIDENCE` are reserved for evaluated submissions. `planned` is a catalog lifecycle state, **not a verdict**. No aggregate safety certification. Positive controls prevent deny-all from passing. Independent effect observation is required for claims about real effects.

## Structure
- `catalog.json`: stable registry of 28 proposed challenges.
- `contracts/challenge.schema.json`: manifest validation schema.
- `challenges/NNN/manifest.json`: one declaration per challenge, initially planned.
- `tests/test_catalog.py`: structural invariants only, not challenge coverage.

## Next
Implement one challenge at a time with a threat model, public/hidden variants, independent oracle, positive controls, evidence requirements and reproducible runner. Keep VALO/HEIMEL outside the core as optional systems under test.

Run: `python -m unittest discover -s season1/tests -v`
