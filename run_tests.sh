#!/usr/bin/env bash
set -euo pipefail
# Always launch from repo root (script may be run from anywhere)
cd "$(dirname "$0")"

# Mute surprise global pytest plugins in ephemeral VMs/containers
export PYTEST_DISABLE_PLUGIN_AUTOLOAD="${PYTEST_DISABLE_PLUGIN_AUTOLOAD:-1}"
# Provide CHROME_BIN if Chrome is present (helps Selenium fixtures later)
export CHROME_BIN="${CHROME_BIN:-$(command -v google-chrome || command -v google-chrome-stable || true)}"

# Resolve suite: env var wins, else first uncommented token in config, else 'unit'
CONFIG_FILE="${TEST_SUITE_FILE:-tests/test_suite.conf}"
if [ -n "${TEST_SUITE:-}" ]; then
  SUITE="$TEST_SUITE"
elif [ -f "$CONFIG_FILE" ]; then
  SUITE="$(grep -E '^\s*[^#]+' "$CONFIG_FILE" | head -n1 | awk '{print $1}')"
  SUITE="${SUITE:-unit}"
else
  SUITE="unit"
fi

case "$SUITE" in
  unit)
    echo "Running UNIT tests only (-m 'not e2e')"
    pytest -q -m "not e2e"
    ;;
  e2e)
    echo "Running E2E tests only (-m 'e2e')"
    pytest -q -m "e2e"
    ;;
  both)
    echo "Running BOTH unit and e2e tests"
    pytest -q
    ;;
  none)
    echo "Skipping all tests (suite=none)"
    ;;
  *)
    echo "Unknown test suite '$SUITE' (expected: unit|e2e|both|none)"
    exit 2
    ;;
esac
