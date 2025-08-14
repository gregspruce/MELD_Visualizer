# Runbook

## Install
python -m pip install -U pip
pip install -r requirements.txt
pip install -r requirements-dev.txt

## Test suite
Edit `tests/test_suite.conf` (unit|e2e|both|none) or override:
TEST_SUITE=e2e bash run_tests.sh

## Run tests
bash run_tests.sh
# or:
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q -m "not e2e"
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q -m "e2e"

## Local app
python app.py   # binds to 127.0.0.1:8050

## CI
Workflow reads tests/test_suite.conf and runs unit/e2e jobs accordingly.

## Jules
Initial setup: see examples/JULES_initial_setup.sh (set E2E_SETUP=1 for Chrome).
Run: cd /app && bash run_tests.sh
