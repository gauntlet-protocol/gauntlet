# Contributing to GAUNTLET

Contributions from developers and researchers are welcome. Submit proposals against the public versioned challenge protocol, not a vendor-specific runner.

Required for each challenge contribution: threat model; legitimate and adversarial objectives; positive controls; negative controls; independent oracle; reproducible scenario seed; source/dataset licenses; evidence format; language/speech considerations where applicable; failure modes; and disclosure of conflicts.

Proposals must not modify existing challenge IDs or imply an unrun test passed. Optional external benchmark adapters live outside the kernel. Provide a local execution command and raw output for each change; a GitHub status check alone does not satisfy the acceptance gate.

Reviewers assess methodological soundness, reproducibility, oracle independence, security and fairness. Disputes and corrections must preserve previous result versions. Hidden tests are submitted privately and are never committed to public challenge artifacts.


## First contribution

1. Run `bash scripts/quickstart-local.sh` and `cargo test --workspace` locally.
2. Open an issue describing the proposed challenge, threat model, expected evidence and licensing before submitting a major new challenge.
3. Submit a pull request with focused changes, regression tests and the exact local commands/results. Do not commit keys, private datasets or hidden evaluation cases.
4. Do not claim independent verification or attestation from a local PASS. Governance charter and evaluator authorization are still proposals, not active independent authorities.

Maintainers review contributions; merging is not automatic.
