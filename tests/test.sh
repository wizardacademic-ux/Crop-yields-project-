#!/usr/bin/env bash
# Entry point for the verifier. Runs the pytest suite against the attempt's
# output files, then combines per-test pass/fail with signed weights from
# test_weights.json to produce /logs/verifier/reward.json and
# /logs/verifier/ctrf.json.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p /logs/verifier

python3 "$HERE/run_verifier.py"
