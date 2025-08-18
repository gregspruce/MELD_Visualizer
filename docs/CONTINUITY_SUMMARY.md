# MELD_Visualizer — Continuity Summary
_Last updated: 2025-08-14T14:03:20Z_

## Purpose
AI-agnostic summary so any assistant/human can continue work on the MELD_Visualizer (Dash) repo.

## High-level history
- Pytest hung in testing environment → disabled global plugin autoload + fixed imports.
- Added app factory + robust layout loader; separated runtime vs test deps.
- Added Selenium 4 E2E; Chrome installed only when needed.
- Introduced test-suite switch (file/env) + `run_tests.sh`.
- Split CI jobs; used `E2E_SETUP=1` for Chrome installation when needed.
- Synced PR: title set to "Volumetric Data Plotter", use `app.run(...)`.
- Fixed tabs rendering by restoring Bootstrap CSS via `external_stylesheets`.
- Bind to 127.0.0.1:8050 by default.
- Added G-code visualization tab with a dedicated parser for NC files to simulate toolpaths and volume meshes, enabling comparison between intended program and actual CSV data.

## Intent
Reliable tests in ephemeral VMs/CI; preserve original UI; easy on/off switches.

## Contracts
- `app.py`: exports `create_app()` + `app`.
- `layout.py`: support `get_layout(app)` or `create_layout()` or `layout`.
- `callbacks.py`: optional `register_callbacks(app)` / `init_callbacks(app)`.
- `data_processing.py`: `parse_contents` for CSV, `parse_gcode_file` for NC, `generate_volume_mesh` for 3D geometry.

See RUNBOOK.md for commands.