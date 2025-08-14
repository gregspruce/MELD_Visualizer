#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTEST_DISABLE_PLUGIN_AUTOLOAD="${PYTEST_DISABLE_PLUGIN_AUTOLOAD:-1}"
export CHROME_BIN="${CHROME_BIN:-$(command -v google-chrome || command -v google-chrome-stable || true)}"
CFG="${TEST_SUITE_FILE:-tests/test_suite.conf}"
if [ -n "${TEST_SUITE:-}" ]; then SUITE="$TEST_SUITE";
elif [ -f "$CFG" ]; then SUITE="$(grep -E '^[[:space:]]*[^#]+' "$CFG" | head -n1 | awk '{print $1}')"; SUITE="${SUITE:-unit}";
else SUITE="unit"; fi
case "$SUITE" in
  unit)  pytest -q -m "not e2e" ;;
  e2e)   pytest -q -m "e2e" ;;
  both)  pytest -q ;;
  none)  echo "Skipping tests." ;;
  *)     echo "Unknown suite '$SUITE'"; exit 2 ;;
esac
