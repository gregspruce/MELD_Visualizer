#!/usr/bin/env bash
# Always run pytest with plugin autoload disabled to avoid VM global plugin hangs.
set -euo pipefail
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
# Respect any args you pass through, e.g. -k 'not e2e'
pytest -q "$@"
