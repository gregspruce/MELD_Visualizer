#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
cd .

export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
export CHROME_BIN="${CHROME_BIN:-$(command -v google-chrome || command -v google-chrome-stable || true)}"

TEST_SUITE="${TEST_SUITE:-unit}"  # unit | e2e | both | none
case "$TEST_SUITE" in
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
    echo "Skipping all tests (TEST_SUITE=none)"
    ;;
  *)
    echo "Unknown TEST_SUITE='$TEST_SUITE' (expected: unit|e2e|both|none)"
    exit 2
    ;;
esac
