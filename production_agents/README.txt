GAUNTLET-PROD-001: Production Agent Systems conformance matrix
Source: PracticAI, "Production Agent Systems", 44-page PDF, Q01-Q18.

All 18 topics have explicit machine-readable evidence gates.
A case requires:
  question: "Q01" .. "Q18"
  material_effect: true/false
  evidence: {signal_name: true/false/null}

All required signals must be explicitly true for PASS. False -> FAIL,
unknown, absent, or non-boolean -> INSUFFICIENT_EVIDENCE.
Material effects additionally require all EFFECT_GATES in conformance.py.
The suite-level status is the most conservative of its case verdicts.
Examples: python -m unittest discover -s production_agents/tests -v
          python -m production_agents.conformance production_agents/example.json

IMPORTANT: The evaluator consumes DECLARED signals only. A PASS is not a
production certification; connect independent capture, signatures, witnesses,
gateway runtime and effect-state probes before making verification claims.
These checks never issue a permit and cannot authorize tool execution.
