# Troubleshooting
- Tabs look like links → Bootstrap CSS missing → ensure external_stylesheets or assets/bootstrap.min.css.
- Pytest hang → set PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 (run via run_tests.sh).
- Chrome missing → install (Jules E2E_SETUP=1; CI installs).
- Server not ready → increase wait or inspect logs; fixture binds to free port.
- G-code plot is empty → Ensure the uploaded G-code file contains `G1` movement commands and the `M34`/`M35` codes for extrusion. The parser only visualizes active extrusion paths.
- Windows CRLF → use LF or run from Git Bash.