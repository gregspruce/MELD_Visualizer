#!/usr/bin/env bash
# === Jules Initial Setup Script (v5) ===
set -euxo pipefail

echo "--> Installing prerequisites..."
sudo apt-get update
sudo apt-get install -y wget gnupg ca-certificates

echo "--> Adding Google Chrome repo..."
wget -qO- https://dl.google.com/linux/linux_signing_key.pub | sudo gpg --dearmor -o /usr/share/keyrings/google-chrome-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" | \
  sudo tee /etc/apt/sources.list.d/google-chrome.list

echo "--> Installing Google Chrome..."
sudo apt-get update
sudo apt-get install -y google-chrome-stable

echo "--> Upgrading pip/setuptools/wheel..."
python3 -m pip install -U pip setuptools wheel

echo "--> Installing app dependencies..."
# Don't fail CI if requirements.txt is missing; remove '|| true' if you want hard failure
python3 -m pip install -r requirements.txt || true

echo "--> Installing pinned test dependencies..."
python3 -m pip install "pytest==8.3.*" "selenium==4.23.*" "pytest-timeout==2.3.*"

echo "--> Smoke check"
google-chrome --version || true
python3 - <<'PY'
import pytest, selenium
print("pytest", pytest.__version__, "| selenium", selenium.__version__)
PY

echo "--> Setup complete."
