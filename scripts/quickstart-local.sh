#!/usr/bin/env bash
# Local synthetic smoke test; does not verify any external AI agent.
set -euo pipefail
cd "$(dirname "$0")/.."
command -v cargo >/dev/null || { echo 'Rust/Cargo required' >&2; exit 2; }
output="$(mktemp)"
trap 'rm -f "$output"' EXIT
cargo run --quiet -p gauntlet-runner -- run 003 "$output"
cargo run --quiet -p gauntlet-runner -- verify-local "$output"
echo 'LOCAL SYNTHETIC SMOKE TEST COMPLETE; NO VERIFIED OR ATTESTED CLAIM'
