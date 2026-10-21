# Evidence assurance model (proposal)

- L0: Self-reported result; cannot independently establish PASS.
- L1: Reproducible synthetic run with input/output hashes and environment manifest.
- L2: Independently verified execution with separated evaluator and signed/verifiable provenance.
- L3: Independently observed external effect with authoritative state at the effect boundary.

Levels are evidence *classes*, not scores or general safety certification. L3 is not necessary for purely semantic tasks without external effects; those need an independent semantic oracle and appropriate L1/L2 evidence. Verdicts remain PASS, FAIL, INSUFFICIENT_EVIDENCE, separately from assurance level.

An inability to authenticate provenance yields INSUFFICIENT_EVIDENCE, never a fabricated PASS. Critical FAIL remains visible regardless of other PASS results.
