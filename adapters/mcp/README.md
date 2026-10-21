# GAUNTLET MCP adapter (experimental, read-only)

Optional Python 3 stdlib MCP JSON-RPC 2.0 server over newline-delimited **stdio**, outside Rust core. Start: `python3 adapters/mcp/server.py`. MCP clients can configure this command as a local stdio server. No external Python packages are needed.

Tools: `gauntlet_list_challenges`, `gauntlet_get_challenge`, `gauntlet_get_guides`, `gauntlet_get_started`, `gauntlet_get_starter`. These return only public, planned challenge manifests and documentation paths. MCP tool names use underscores; no capability to execute programs, reveal hidden variants, mint badges, grant evaluator authority or attest results.

This is an experimental subset of MCP server functionality; no remote transport, authentication or dynamic resources. Clients may vary in their supported MCP protocol versions. **Not production hardened or release-ready.** Run only on a trusted local checkout. Do not expose via HTTP. The Rust runner and verifier have no MCP dependency.

Future gated functions: read-only evidence verification only after the independent Rust verifier is implemented; local execution only after explicit command allowlisting, consent and process isolation. Never permit arbitrary shell commands through MCP.

## Architecture document import (read-only)

Set `GAUNTLET_ARCHITECTURE_ROOT=/absolute/path/to/approved-input-folder` **before starting** the MCP server. Call `gauntlet_parse_architecture` with `{ "filename": "architecture.md" }`. The MCP client may select only a single basename directly within this operator-approved directory; symlinks, `../` paths and absolute paths are rejected. No arbitrary repository or filesystem scanning is exposed. Returned sections include source SHA-256 and location, but are untrusted content, not verified architecture claims. MCP responses are limited to 100,000 extracted characters; use the ingestion CLI for larger documents. The operator is responsible for input-directory permissions and sensitive documents. No uploads, code execution, auto-implementation or external network access.
