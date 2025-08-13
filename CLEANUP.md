# Cleanup / Deletions

Given the updated test strategy and CI, these items are **no longer needed** (or should be moved):

1) **dependencies**
   - Remove `dash[testing]` from `requirements.txt`
   - Remove `chromedriver-autoinstaller` from `requirements.txt`
   - Keep runtime-only libs in `requirements.txt`
   - Put pytest/selenium/etc. in `requirements-dev.txt` (already added)

2) **files**
   - Old placeholder E2E test: `tests/test_e2e_placeholder.py` (replaced by real E2E)
   - Any previous `scripts/jules_setup.sh` or ad-hoc setup scripts you no longer reference
   - Any top-level `conftest.py` that conflicts with `tests/conftest.py`
   - Any legacy browser driver binaries checked into the repo (not needed with Selenium Manager)

3) **docs**
   - Remove or update stale instructions referencing:
     - `chromedriver_autoinstaller.install()`
     - Running E2E without headless flags
     - Installing Chrome/driver manually for each run

4) **git hygiene**
   - Mark `run_tests.sh` as executable in git:
     ```bash
     git update-index --chmod=+x run_tests.sh
     ```
   - Ensure LF endings for shell scripts to avoid Windows issues:
     ```bash
     git config core.autocrlf input
     ```

If you want, I can perform a pass over your current repo tree and produce a targeted diff of what to delete/move based on what's actually present.
