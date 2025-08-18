# Runbook

## Install
# Modern approach (recommended)
pip install -e ".[dev]"  # Development installation with all dependencies

# Legacy approach (still supported)
python -m pip install -U pip
pip install -r requirements.txt
pip install -r requirements-dev.txt

## Test suite
Edit `tests/test_suite.conf` (unit|e2e|both|none) or override:
TEST_SUITE=e2e bash scripts/run_tests.sh

## Run tests
bash scripts/run_tests.sh
# or directly with pytest:
pytest  # Runs all tests from pyproject.toml config
# or:
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q -m "not e2e"
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q -m "e2e"

## Local app
# Method 1: Using installed command
meld-visualizer

# Method 2: Running as module
python -m meld_visualizer

# Method 3: From source (development)
python -m src.meld_visualizer.app

# All bind to 127.0.0.1:8050

## CI
Workflow reads tests/test_suite.conf and runs unit/e2e jobs accordingly.

## Jules
Initial setup: see docs/examples/JULES_initial_setup.sh (set E2E_SETUP=1 for Chrome).
Run: cd /app && bash scripts/run_tests.sh
