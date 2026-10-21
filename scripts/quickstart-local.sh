#!/usr/bin/env bash
# Ten local synthetic smoke tests; does not verify any external AI agent.
set -euo pipefail
cd "$(dirname "$0")/.."
command -v cargo >/dev/null || { echo 'Rust/Cargo required' >&2; exit 2; }
output="$(mktemp)"
trap 'rm -f "$output"' EXIT
for id in 001 002 003 004 005 006 007 008 009 010; do
  cargo run --quiet -p gauntlet-runner -- run "$id" "$output"
  cargo run --quiet -p gauntlet-runner -- verify-local "$output"
done
echo 'LOCAL SYNTHETIC SMOKE TEST COMPLETE; NO VERIFIED OR ATTESTED CLAIM'