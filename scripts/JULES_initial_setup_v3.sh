# === MELD_Visualizer — Jules Initial Setup (E2E-ready) v3 ===
# Paste into Jules "Initial setup". It does NOT run tests.
set -euxo pipefail
cd /app

E2E_SETUP=1

# ----- privilege helper (root/non-root) -----
if [ "$(id -u)" -ne 0 ]; then SUDO="sudo"; else SUDO=""; fi

# ----- Python deps first (fast snapshot when no E2E) -----
python -m pip install -U pip
if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
if [ -f requirements-dev.txt ]; then pip install -r requirements-dev.txt; fi

# ----- Optional Chrome install (controlled by E2E_SETUP=1) -----
E2E_SETUP="${E2E_SETUP:-0}"
if [ "$E2E_SETUP" = "1" ]; then
  $SUDO apt-get update
  $SUDO apt-get install -y wget gnupg ca-certificates
  if [ ! -f /etc/apt/sources.list.d/google-chrome.list ]; then
    wget -qO- https://dl.google.com/linux/linux_signing_key.pub | $SUDO gpg --dearmor -o /usr/share/keyrings/google-chrome-keyring.gpg
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" |       $SUDO tee /etc/apt/sources.list.d/google-chrome.list >/dev/null
    $SUDO apt-get update
  fi
  if ! command -v google-chrome >/dev/null 2>&1 && ! command -v google-chrome-stable >/dev/null 2>&1; then
    $SUDO apt-get install -y google-chrome-stable
  fi
  (google-chrome --version || google-chrome-stable --version) || true
else
  echo "E2E_SETUP is not 1; skipping Chrome install (OK for unit/http tests)"
fi

# ----- helper test runner -----
cat > /app/run_tests.sh <<'SH'
#!/usr/bin/env bash
set -euo pipefail
cd /app
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
export CHROME_BIN="$(command -v google-chrome || command -v google-chrome-stable || true)"
TEST_SUITE="${TEST_SUITE:-unit}"  # unit|e2e|both|none
case "$TEST_SUITE" in
  unit)  pytest -q -m "not e2e" ;;
  e2e)   pytest -q -m "e2e" ;;
  both)  pytest -q ;;
  none)  echo "Skipping tests (TEST_SUITE=none)";;
  *) echo "Unknown TEST_SUITE='$TEST_SUITE'"; exit 2;;
esac
SH
chmod +x /app/run_tests.sh

echo "Setup complete. Use TEST_SUITE={unit|e2e|both|none} to control runs."
