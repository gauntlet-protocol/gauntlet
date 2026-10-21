# Architecture → Code: GAUNTLET builder starter

This is a minimal deterministic starter, **not** AI-generated implementation of arbitrary architecture. It helps turn a proposed interface into a runnable GAUNTLET process participant with explicit TODOs. It does not claim compliance, architecture correctness, or independent verification.

## Get started

1. Read the [process contract](../../preview/PROCESS_PROTOCOL.md).
2. Copy `participant.py` to your own repository and replace the `answer()` function with your system's actual behavior.
3. Run `cargo run -p gauntlet-runner -- run-external 003 /tmp/result.json python3 /path/to/your/participant.py` from GAUNTLET root.
4. Run `cargo run -p gauntlet-runner -- verify-local /tmp/result.json`.
5. Review the output as **LOCAL**, not independently attested. Preserve your architectural decisions and map them to tests.

## Architecture mapping worksheet

| Architecture claim | Concrete module or API | Local test | Independent oracle | Evidence |
| --- | --- | --- | --- | --- |
| Untrusted content cannot override trusted instruction | TODO | TODO | TODO | TODO |
| Authorization cannot be bypassed | TODO | TODO | TODO | TODO |
| Evaluation records cannot be silently rewritten | TODO | TODO | TODO | TODO |

Never claim a capability is implemented based only on a design document or generated stub. Add a failing test first, implement the smallest conforming behavior, then independently evaluate. Avoid importing governance engines or vendor frameworks into GAUNTLET core.
