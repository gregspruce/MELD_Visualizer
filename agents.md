# Agents / Jules Instructions

This repo is configured to be friendly to ephemeral VMs like **Google Jules**. Keep setup idempotent and testing selectable.

## Initial Setup (Snapshot)

Paste the following script (see `JULES_initial_setup_v3.sh` in the repo for a copy):

- Installs Python runtime and dev deps
- Optionally installs **Google Chrome** if `E2E_SETUP=1`
- Creates `/app/run_tests.sh` (test runner with stable env)

### Switch for Chrome (E2E)
Set this near the top **before** Run & snapshot:

```bash
E2E_SETUP=1   # install Chrome and cache it in the snapshot (optional)
```

If omitted, setup remains unit/HTTP‑only (faster snapshot).

## Run Step

Use the helper runner which respects either:
- The repo toggle `tests/test_suite.conf`, or
- The env override `TEST_SUITE` (unit|e2e|both|none)

```bash
cd /app
bash run_tests.sh
# or override temporarily
TEST_SUITE=e2e bash run_tests.sh
```

The runner exports:
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` → avoids surprise pytest plugins
- Detects `CHROME_BIN` automatically

## Recommended Task Templates

- **Unit only**:
  - Initial setup: omit `E2E_SETUP`
  - Run: `TEST_SUITE=unit bash /app/run_tests.sh`

- **E2E only**:
  - Initial setup: include `E2E_SETUP=1`
  - Run: `TEST_SUITE=e2e bash /app/run_tests.sh`

- **Both**:
  - Initial setup: include `E2E_SETUP=1`
  - Run: `TEST_SUITE=both bash /app/run_tests.sh`

## Diagnostics

If something fails:
- Print versions (already in setup script)
- Check Chrome availability:
  ```bash
  google-chrome --version || google-chrome-stable --version || true
  ```
- Run pytest verbosely:
  ```bash
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -vv -s --maxfail=1 --durations=10
  ```

## Notes

- Do not clone in setup; Jules clones to `/app`.
- Keep setup non-interactive and idempotent.
- Leave running tests for the **Run** step—setup is for dependencies only.
