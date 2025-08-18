#!/usr/bin/env bash
set -euxo pipefail
cd /app
: "${E2E_SETUP:=0}"
sudo apt-get update
sudo apt-get install -y wget gnupg ca-certificates
python -m pip install -U pip
[ -f requirements.txt ] && pip install -r requirements.txt
[ -f requirements-dev.txt ] && pip install -r requirements-dev.txt || true
if [ "$E2E_SETUP" = "1" ]; then
  if [ ! -f /etc/apt/sources.list.d/google-chrome.list ]; then
    wget -qO- https://dl.google.com/linux/linux_signing_key.pub | sudo gpg --dearmor -o /usr/share/keyrings/google-chrome-keyring.gpg
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list >/dev/null
    sudo apt-get update
  fi
  sudo apt-get install -y google-chrome-stable
fi
if [ ! -f /app/run_tests.sh ] && [ -f /app/examples/run_tests.sh ]; then
  cp /app/examples/run_tests.sh /app/run_tests.sh
  chmod +x /app/run_tests.sh
fi
