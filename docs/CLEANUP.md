# Cleanup checklist (tailored to current repo behavior)

Based on recent installs and test runs, adjust the repo as follows:

## Dependencies
- **Move test tools out of `requirements.txt`:**
  - Remove: `pytest`, `dash[testing]`, `chromedriver-autoinstaller`
  - Keep: `pandas`, `numpy`, `dash`, `dash-bootstrap-components`, `plotly`
- **Ensure `requirements-dev.txt` exists** with:
  - `pytest==8.3.5`
  - `pytest-timeout==2.3.1`
  - `pytest-xdist==3.6.*`
  - `selenium==4.23.*`
  - `requests>=2.31`

## Files likely safe to delete or replace
- `tests/test_e2e_placeholder.py` (replaced by `tests/e2e/test_homepage_e2e.py`)
- Any old setup scripts you no longer invoke
- Any checked-in browser driver binaries (Selenium Manager handles drivers)
- Any conflicting top-level `conftest.py` outside `tests/`

## Keep / Add
- `tests/test_suite.conf` (toggle)
- `run_tests.sh` (sets env + reads toggle)
- `.github/workflows/ci.yml` (split jobs; reads toggle)
- Modern setup scripts for initial environment configuration

## Windows notes
- Ensure LF endings for `run_tests.sh` (use `dos2unix` or `git config core.autocrlf input`)
- Mark executable:
  ```bash
  git update-index --chmod=+x run_tests.sh
  ```
