# MELD_Visualizer

A Dash-based visualizer with a **Jules-proof** test setup and CI. This repo is designed to run clean in short‑lived VMs (Jules, GitHub Actions) without flaky global pytest plugins or brittle browser dependencies.

## TL;DR

- Runtime deps are in `requirements.txt` (no test tools here).
- Test-only deps are in `requirements-dev.txt`.
- Tests are split:
  - **Unit/HTTP**: fast, no browser.
  - **E2E**: headless Chrome via Selenium 4 (Selenium Manager auto-downloads the driver).
- Choose what to run by editing **`tests/test_suite.conf`** (or override with `TEST_SUITE` env).

## Quickstart (local)

```bash
python -m pip install -U pip
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Unit only
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q -m "not e2e"

# E2E only (requires Chrome installed locally)
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q -m "e2e"

# Or use the switch file / script:
#   Edit tests/test_suite.conf (unit|e2e|both|none), then:
bash run_tests.sh
```

### Why `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`?
Shared VMs and developer machines often have random pytest plugins installed. This env var **prevents pytest from auto-loading** those plugins at startup, eliminating mysterious hangs.

## Test Suite Switch

Pick **one** mode in `tests/test_suite.conf` by leaving it uncommented:

```
unit
# e2e
# both
# none
```

- You can override ad‑hoc without editing the file:
  ```bash
  TEST_SUITE=e2e bash run_tests.sh
  ```

## Project Layout (relevant files)

```
.
├─ app.py                       # Dash app; exposes create_app()
├─ requirements.txt             # runtime deps only
├─ requirements-dev.txt         # test-only deps (pytest, selenium, etc.)
├─ run_tests.sh                 # reads TEST_SUITE or tests/test_suite.conf
├─ pytest.ini                   # pytest defaults + 'e2e' marker
├─ tests/
│  ├─ test_suite.conf           # <- toggle unit/e2e/both/none
│  ├─ conftest.py               # stable app import; fallback app
│  ├─ test_imports.py           # module import checks
│  ├─ test_config_schema.py     # config.json parses (if present)
│  ├─ test_app_smoke.py         # HTTP smoke (no browser)
│  └─ e2e/
│     ├─ conftest.py            # starts Dash server + headless Chrome
│     └─ test_homepage_e2e.py   # basic page renders
└─ .github/workflows/ci.yml     # split unit/e2e jobs; driven by test_suite.conf
```

## Jules

This repo is tuned for Jules’ VM model.

### Initial Setup (snapshot)
Paste the script from `JULES_initial_setup_v3.sh` into Jules’ **Initial setup** box. It:
- Installs Python deps,
- Optionally installs Chrome if you set `E2E_SETUP=1`,
- Writes `/app/run_tests.sh` that respects the test suite switch.

If you want to run E2E in Jules, set at the **top** of the script:
```bash
E2E_SETUP=1
```

### Run
Use the script; it handles environment flags and suite selection:

```bash
cd /app
# Edit tests/test_suite.conf, then:
bash run_tests.sh
# or override temporarily:
TEST_SUITE=both bash run_tests.sh
```

## GitHub Actions

Workflow lives at `.github/workflows/ci.yml` and mirrors the Jules environment:

- **resolve-suite** job reads `tests/test_suite.conf` and outputs which jobs to run.
- **unit-tests** job installs deps and runs `-m "not e2e"`.
- **e2e-tests** job installs **Google Chrome** and runs `-m "e2e"`.

No YAML edits needed to toggle suites—change the file, commit, push.

## Troubleshooting

- **E2E skips**: The e2e suite self-skips if Chrome is missing. In Jules, ensure your Initial setup included `E2E_SETUP=1` before snapshot; in CI, Chrome is installed by the e2e job.
- **Pytest hangs at collection**: confirm `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` is set (run via `run_tests.sh` to be safe).
- **Windows line endings**: ensure `run_tests.sh` is LF (`dos2unix run_tests.sh` if needed).

## Contributing / Dev Tips

- Keep test tools **out** of `requirements.txt`. Use `requirements-dev.txt` instead.
- Prefer IDs or stable selectors in E2E tests; avoid brittle XPath.
- Keep CI fast: small unit tests, minimal waits in E2E, and use headless Chrome flags:
  `--headless=new --no-sandbox --disable-dev-shm-usage --window-size=1280,800`.

---

Happy testing. If something’s flaky, it’s probably a plugin—muzzle it with the env var and carry on.
