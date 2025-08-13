# MELD_Visualizer Agent Instructions (AGENTS.MD)

This document provides instructions for AI agents (like Google's Jules) and human developers on how to understand, develop, and test the MELD_Visualizer application.

## 1. Project Overview

The MELD_Visualizer is a web application built with Python and Dash for the interactive visualization of process data from MELD manufacturing. It allows users to upload CSV data files and explore the relationships between different process parameters in 3D and 2D plots.

### Core Features:
*   **CSV Data Upload:** Parses and processes specific MELD data formats.
*   **Interactive 3D Scatter Plots:** Two main plots with configurable color mapping and Z-axis filtering.
*   **Customizable 3D Scatter Plot:** A tab allowing the user to select any data column for the X, Y, Z, color, and filter axes.
*   **2D Time-Series Plot:** Visualizes data parameters against time, with filtering capabilities.
*   **3D Toolpath Plot:** Renders the physical path of the machine tool during active extrusion.
*   **3D Volume Mesh Generation:** Creates a 3D mesh representing the volume of the deposited material, with color mapped to a selected data parameter.
*   **Configurable UI:** The application's theme and default plot options can be configured via a "Settings" tab and are saved in `config.json`.

---

## 2. Core Technologies

*   **Language:** Python 3
*   **Web Framework:** Dash
*   **UI Components:** Dash Bootstrap Components
*   **Plotting:** Plotly Express & Plotly Graph Objects
*   **Data Manipulation:** Pandas, NumPy
*   **Build Tool:** PyInstaller (for standalone executables)

---

## 3. Project Architecture

The application was refactored from a single monolithic script into a modular structure to promote separation of concerns.

*   `app.py`: **Main Entry Point.** Initializes the Dash app instance, assigns the layout, imports the callbacks to register them, and runs the web server. **This is the file to execute to start the application.**
*   `layout.py`: **The "View".** Contains all functions that create the visual components and structure of the app. It defines the entire UI layout and the IDs of each component.
*   `callbacks.py`: **The "Controller".** Contains all the `@callback` functions that define the app's interactivity and logic. It orchestrates the flow of data between the UI (layout) and the data processing backend.
*   `data_processing.py`: **The "Model"/Backend Logic.** Contains pure Python functions for data manipulation. This includes parsing CSV files (`parse_contents`) and all complex geometry calculations for the mesh plot (`generate_volume_mesh`). This module is deliberately insulated from any Dash-specific code.
*   `config.py`: **Runtime Configuration.** Handles loading the `config.json` file, defines theme constants, and centralizes configuration variables used by the app at runtime.
*   `config.json`: **User Configuration File.** Stores user-facing settings like the default theme and the list of columns to display in graph dropdowns. This file is intended to be modified by the end-user (via the Settings tab) or a developer.
*   `CSV/`: **Sample Data.** This directory contains sample input CSV files that the application is designed to ingest. These should be used for all testing.

---

## 4. Development Workflow

1.  **Setup:** Create a Python virtual environment and install all required packages from the `requirements.txt` file. This file is the single source of truth for all project dependencies.
    ```bash
    pip install -r requirements.txt
    ```
2.  **Running the App:** Execute the main entry point.
    ```bash
    python app.py
    ```
    The application runs in Debug Mode by default, which enables **hot-reloading**. Most code changes in `.py` files will automatically restart the server.
3.  **Making Changes:**
    *   To change the **UI appearance or structure**, modify functions in `layout.py`.
    *   To change the **application's behavior** (e.g., how a filter works), modify callbacks in `callbacks.py`.
    *   To change the **core data calculations** (e.g., improve mesh generation), modify functions in `data_processing.py`.

---

## 5. Testing Strategy

A multi-layered testing strategy is required to ensure stability and prevent regressions. A new `tests/` directory should be created to house all test files. The `pytest` framework is recommended.

### Layer 1: Unit & Functional Testing (Backend)

This layer tests the data processing logic in isolation, without needing to run the full web app. This is the fastest and most reliable form of testing.

**File to create:** `tests/test_data_processing.py`

**Test Cases:**
1.  **Test `parse_contents`:**
    *   Use a sample CSV file from the `CSV/` directory.
    *   Verify that the function returns a non-empty Pandas DataFrame.
    *   Check that the `TimeInSeconds` column is created and is numeric.
    *   Check that unit conversion is correctly applied (e.g., `ZPos` values are multiplied by 25.4).
    *   Test edge cases: malformed CSV, empty file content.
2.  **Test `get_cross_section_vertices`:**
    *   Provide known inputs (point, direction vector, T, L, R).
    *   Assert that the function returns a NumPy array of the correct shape (`(12, 3)` for default N).
    *   Assert that the calculated vertex positions are mathematically correct for a simple case (e.g., direction `[0, 1, 0]`).
3.  **Test `generate_volume_mesh`:**
    *   Create a small, sample DataFrame mimicking active extrusion data.
    *   Call the function and assert that it returns a dictionary containing `vertices`, `faces`, and `vertex_colors`.
    *   Assert that the output arrays are not empty and have the correct dimensions.
    *   Test that it returns `None` or handles an empty input DataFrame gracefully.

### Layer 2: End-to-End (E2E) UI Testing (Frontend)

This layer tests the running application from a user's perspective. It requires a browser automation tool. The recommended library is `dash.testing` (which builds on Selenium) as it is designed specifically for this purpose and includes powerful features like snapshot testing.

**Setup:**
*   All necessary packages, including `pytest` and `dash[testing]`, are installed via the main `requirements.txt` file. Ensure you have run `pip install -r requirements.txt` in your environment.

**File to create:** `tests/test_app_e2e.py`

**Test Cases (must be executed against a running app instance):**

1.  **Smoke Test:**
    *   The test should start the app.
    *   Verify the app loads without crashing and the page title is "Volumetric Data Plotter".
2.  **File Upload and Initial State:**
    *   Use `dash_duo.find_element` to locate the `dcc.Upload` component.
    *   Upload a sample file (e.g., `CSV/sample_data_1.csv`).
    *   Assert that the `#output-filename` div updates to contain the name of the file.
    *   Assert that the dropdowns (`#radio-buttons-1`, etc.) are populated with options.
3.  **Filtering Functionality:**
    *   After uploading a file, programmatically change the value of a `RangeSlider` (e.g., `{'type': 'range-slider', 'index': 'zpos-1'}`).
    *   **Snapshot Test:** Use `dash_duo.take_snapshot` on the corresponding graph component (`#graph-1`). The test will fail if the visual appearance of the graph changes from the last known-good version. This is excellent for catching visual regressions.
4.  **Tab Navigation:**
    *   Programmatically click on each tab in the `dbc.Tabs` component.
    *   For each tab, assert that a key, unique element of that tab's content becomes visible.
    *   Example: Click "3D Volume Mesh" tab -> Assert `#generate-mesh-plot-button` is visible and enabled.
5.  **Button-based Generation:**
    *   Navigate to the "3D Toolpath Plot" tab.
    *   Click the `#generate-line-plot-button` button.
    *   Wait for the loading spinner to disappear.
    *   Assert that the `figure` property of the `#line-plot-3d` graph is not empty.

### Regression Testing Workflow

For any new feature or bug fix, the following workflow should be followed by an agent:

1.  **Write New Tests:** Add new unit tests and/or E2E tests that specifically validate the new feature or prove the bug is fixed.
2.  **Run All Tests:** Execute the entire test suite (`pytest tests/`).
3.  **Verify No Regressions:** Ensure that all existing tests continue to pass. If an existing test fails, the new changes have caused a regression that must be fixed before the work can be considered complete.

### Environment (Jules)

1. Provision the VM and install dependencies:
   ```bash
   bash scripts/jules_setup.sh
   ```
2. Run tests with plugin autoload disabled:
```bash
bash scripts/run_tests.sh           # all tests
bash scripts/run_tests.sh -k 'not e2e'  # unit tests only
```

Notes:

Chrome is installed system-wide; Selenium 4’s Selenium Manager fetches a matching driver automatically.

If tests still hang, run:
```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest --trace-config -k test_simple -q
```
to verify no external plugins are being loaded.

---

### Agent Notes: Tabs + Theme
- Tabs are asserted in `tests/e2e/test_tabs_e2e.py`. Update labels there if UI copy changes.
- The app resolves a Bootstrap theme via `config.APP_CONFIG['theme']` / `THEMES`, falling back to `dbc.themes.BOOTSTRAP`. Agents running offline should consider a local CSS file under `assets/`.
