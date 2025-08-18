Files likely safe to remove now (if present):

1) `tests/test_e2e_placeholder.py` — replaced by real E2E under `tests/e2e/`.
2) Any legacy setup scripts from earlier iterations — superseded by current setup process and top-level `run_tests.sh`.
3) `chromedriver_autoinstaller` usage — Selenium 4+ manages drivers itself. Remove from code and `requirements.txt`.
4) `dash[testing]` in `requirements.txt` — move test tooling to `requirements-dev.txt`.
5) Any checked-in WebDriver binaries — not needed with Selenium Manager.
6) A `conftest.py` at repo root — keep `tests/conftest.py` only to avoid accidental imports.

If you want me to scan a fresh tree and produce an exact diff, push your latest and I can generate a targeted list next.
