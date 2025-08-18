# MELD Visualizer Development Guide (agents.md)

This document provides comprehensive instructions for AI agents (especially Claude Code) and human developers on how to understand, develop, and test the MELD_Visualizer application.

## 1. Project Overview

The MELD_Visualizer is a web application built with Python and Dash for the interactive visualization of process data from MELD manufacturing. It allows users to upload CSV data files and explore the relationships between different process parameters in 3D and 2D plots.

### Core Features:
*   **CSV Data Upload:** Parses and processes specific MELD data formats.
*   **G-code Program Upload:** Parses `.nc` files to simulate the intended toolpath and volume mesh.
*   **User-Configurable 3D Scaling:** All 3D plot tabs feature a "Z-Axis Stretch Factor" to improve visualization of layer details.
*   **Interactive 3D Scatter Plots:** Two main plots with configurable color mapping and Z-axis filtering.
*   **Customizable 3D Scatter Plot:** A tab allowing the user to select any data column for the X, Y, Z, color, and filter axes.
*   **2D Time-Series Plot:** Visualizes data parameters against time, with filtering capabilities.
*   **3D Toolpath Plot:** Renders the physical path of the machine tool during active extrusion.
*   **3D Volume Mesh Generation:** Creates a 3D mesh representing the volume of the deposited material, with color mapped to a selected data parameter.
*   **Configurable UI:** The application's theme and default plot options can be configured via a "Settings" tab and are saved in `config.json`.
*   
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

The application follows modern Python packaging standards with a clean, modular structure organized using the src-layout pattern:

### Package Structure:
*   **`src/meld_visualizer/app.py`**: Main entry point. Initializes the Dash app, loads all modules, and runs the server.
*   **`src/meld_visualizer/core/layout.py`**: UI components and structure (View layer).
*   **`src/meld_visualizer/callbacks/`**: Modular callback system (Controller layer):
    - `data_callbacks.py`: Data upload and processing callbacks
    - `graph_callbacks.py`: 3D visualization callbacks
    - `visualization_callbacks.py`: Plot generation callbacks
    - `filter_callbacks.py`: Data filtering callbacks
    - `config_callbacks.py`: Settings and configuration callbacks
*   **`src/meld_visualizer/core/data_processing.py`**: Data parsing, mesh generation, G-code processing (Model layer)
*   **`src/meld_visualizer/services/`**: Business logic layer:
    - `cache_service.py`: Caching and performance optimization
    - `data_service.py`: Data processing and transformation
    - `file_service.py`: File handling and validation
*   **`src/meld_visualizer/utils/`**: Utility modules:
    - `security_utils.py`: Security validation and sanitization
    - `logging_config.py`: Logging configuration
*   **`src/meld_visualizer/config.py`**: Configuration loading, theme management, constants
*   **`config/config.json`**: User-configurable settings (themes, plot options, column mappings)
*   **`data/csv/`**: Sample CSV files for testing and development
*   **`data/nc/`**: Sample G-code files for testing and development

### Configuration Files:
*   **`pyproject.toml`**: Modern Python packaging with dependencies, tool configuration, and metadata
*   **`tests/pytest.ini`**: Test configuration with markers (unit, integration, e2e)
*   **`tests/test_suite.conf`**: Test runner configuration

---

## 4. Development Workflow

### Development Setup (Claude Code Workflow):

#### 1. Repository Clone and Setup
```bash
# Clone the repository
git clone https://github.com/gregspruce/MELD_Visualizer.git
cd MELD_Visualizer

# Verify Python version (3.8+ required)
python --version

# Update pip to latest version
python -m pip install -U pip
```

#### 2. Installation Methods

**Method 1: Modern Development Installation (Recommended for Claude Code)**
```bash
# Install with all development dependencies
pip install -e ".[dev]"

# This installs:
# - Production dependencies
# - Development tools (black, flake8, mypy)
# - Testing frameworks (pytest, coverage)
# - Build tools (build, PyInstaller)
```

**Method 2: Legacy Installation (Fallback)**
```bash
# Install dependencies separately
pip install -r requirements.txt         # Production dependencies
pip install -r requirements-dev.txt     # Development dependencies
```

#### 3. Verification
```bash
# Verify installation worked
python -c "import meld_visualizer; print('✓ Import successful')"

# Check available commands
meld-visualizer --help  # Should show help if command is registered
```

### Running the Application:

#### Development Modes
```bash
# Method 1: Using installed command (recommended)
meld-visualizer

# Method 2: Running as Python module
python -m meld_visualizer

# Method 3: From source (for debugging imports)
python -m src.meld_visualizer.app

# All methods bind to http://127.0.0.1:8050
```

#### Debug Configuration
```bash
# Enable explicit debug mode with environment variable
DEBUG=1 meld-visualizer

# Or set in shell session
export DEBUG=1
meld-visualizer

# Debug mode enables:
# - Hot reloading for .py files
# - Detailed error messages
# - Development server features
```

### Hot Reloading Behavior
The application runs in Debug Mode by default, enabling **hot-reloading**:
- **Automatic**: Most `.py` file changes trigger reload
- **Manual restart required**: Changes to `config/config.json` or `src/meld_visualizer/config.py`
- **Browser refresh**: UI updates appear automatically

### Making Changes:
*   **UI appearance/structure**: Modify functions in `src/meld_visualizer/core/layout.py`
*   **Application behavior**: Modify callbacks in `src/meld_visualizer/callbacks/`
*   **Data calculations**: Modify functions in `src/meld_visualizer/core/data_processing.py`
*   **Business logic**: Modify services in `src/meld_visualizer/services/`
*   **Configuration**: Edit `config/config.json` or `src/meld_visualizer/config.py`

### Code Quality:
```bash
# Format code
black src/ tests/

# Lint code  
flake8 src/ tests/

# Type checking
mypy src/

# Run pre-commit hooks
pre-commit run --all-files
```

---

## 5. Testing Strategy

A comprehensive multi-layered testing strategy ensures stability and prevents regressions. The testing structure is organized in the `tests/` directory with proper categorization.

### Testing Structure:
*   **`tests/unit/`**: Unit tests for individual functions and modules
*   **`tests/integration/`**: Integration tests for component interactions
*   **`tests/e2e/`**: End-to-end browser automation tests
*   **`tests/conftest.py`**: Shared test fixtures and configuration
*   **`tests/pytest.ini`**: Test configuration with markers
*   **`tests/test_suite.conf`**: Test runner configuration

### Running Tests (Claude Code Best Practices):

#### Quick Test Commands
```bash
# Run all tests (recommended for initial check)
pytest

# Run tests with coverage (for comprehensive analysis)
pytest --cov=src/meld_visualizer --cov-report=html

# View coverage report
open reports/htmlcov/index.html  # macOS
start reports/htmlcov/index.html # Windows
```

#### Test Categories (Use with -m flag)
```bash
# Unit tests only (fast, no browser automation)
pytest -m "unit"

# Integration tests (service interactions)
pytest -m "integration"

# End-to-end tests (requires Chrome browser)
pytest -m "e2e"

# Exclude E2E tests (for quick feedback)
pytest -m "not e2e"
```

#### Test Runner Script (Alternative)
```bash
# Configure in tests/test_suite.conf first
# Options: unit|e2e|both|none
bash scripts/run_tests.sh

# Override configuration temporarily
TEST_SUITE=unit bash scripts/run_tests.sh
TEST_SUITE=e2e bash scripts/run_tests.sh
TEST_SUITE=both bash scripts/run_tests.sh
```

#### Debugging Tests
```bash
# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_data_processing.py -v

# Run specific test function
pytest tests/unit/test_data_processing.py::test_parse_contents -v

# Stop on first failure
pytest -x

# Debug failing tests with pdb
pytest --pdb

# Disable plugin autoload (if tests hang)
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q -m "not e2e"
```

#### E2E Testing Setup
```bash
# Ensure Chrome is available for E2E tests
# On Ubuntu/Debian:
sudo apt-get update && sudo apt-get install -y google-chrome-stable

# On macOS:
brew install --cask google-chrome

# On Windows: Download and install Chrome from Google

# Verify Chrome installation
google-chrome --version  # Linux
Chrome --version         # macOS/Windows
```

### Layer 1: Unit & Functional Testing

Tests the data processing logic in isolation, without the full web app.

**Files:** `tests/unit/test_data_processing.py`, `tests/unit/test_services.py`, etc.

**Test Cases:**
1.  **Test `parse_contents`:**
    *   Use a sample CSV file from the `CSV/` directory.
    *   Verify that the function returns a non-empty Pandas DataFrame.
    *   Check that the `TimeInSeconds` column is created and is numeric.
    *   Check that unit conversion is correctly applied (e.g., `ZPos` values are multiplied by 25.4).
    *   Test edge cases: malformed CSV, empty file content.
2.  **Test `parse_gcode_file` (G-code):**
    *   Use a sample `.nc` file.
    *   Verify the function returns a non-empty Pandas DataFrame with the correct columns (`XPos`, `YPos`, `ZPos`, `FeedVel`, `PathVel`, `TimeInSeconds`).
    *   Assert that `G0` moves result in a `FeedVel` of 0.
    *   Assert that `M34 S<value>` correctly sets `FeedVel` to `value / 10.0` on subsequent `G1` moves.
    *   Assert that `M35` sets `FeedVel` to 0 on subsequent `G1` moves.
    *   Verify that the calculated `TimeInSeconds` column is monotonically increasing.
3.  **Test `get_cross_section_vertices`:**
    *   Provide known inputs (point, direction vector, T, L, R).
    *   Assert that the function returns a NumPy array of the correct shape (`(12, 3)` for default N).
    *   Assert that the calculated vertex positions are mathematically correct for a simple case (e.g., direction `[0, 1, 0]`).
4.  **Test `generate_volume_mesh`:**
    *   Create a small, sample DataFrame mimicking active extrusion data.
    *   Call the function and assert that it returns a dictionary containing `vertices`, `faces`, and `vertex_colors`.
    *   Assert that the output arrays are not empty and have the correct dimensions.
    *   Test that it returns `None` or handles an empty input DataFrame gracefully.

### Layer 2: End-to-End (E2E) UI Testing (Frontend)

This layer tests the running application from a user's perspective. It requires a browser automation tool. The recommended library is `dash.testing` (which builds on Selenium) as it is designed specifically for this purpose and includes powerful features like snapshot testing.

**Setup:**
*   All necessary packages, including `pytest` and `dash[testing]`, are installed via the main `requirements.txt` file. Ensure you have run `pip install -r requirements.txt` in your environment.

**Files:** `tests/e2e/test_homepage_e2e.py`, `tests/e2e/test_tabs_e2e.py`, etc.

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
    *   Example: Click "G-code Visualization" tab -> Assert `#upload-gcode` is visible.
5.  **Button-based Generation:**
    *   Navigate to the "3D Toolpath Plot" tab.
    *   Click the `#generate-line-plot-button` button.
    *   Wait for the loading spinner to disappear.
    *   Assert that the `figure` property of the `#line-plot-3d` graph is not empty.
6.  **G-code Tab Workflow:**
    *   Navigate to the "G-code Visualization" tab.
    *   Upload a sample `.nc` file to the `#upload-gcode` component.
    *   Change the value in the `#gcode-z-stretch-input` to `3.0`.
    *   Click the `#generate-gcode-viz-button`.
    *   Assert that the `figure` layout's `scene.aspectratio.z` property is now `3.0`.
    *   Assert the `#gcode-filename-alert` becomes visible and shows the filename.
    *   Click the `#generate-gcode-viz-button`.
    *   Wait for the loading spinner to disappear and assert the `figure` property of `#gcode-graph` is not empty.
    *   Click the "Simulated Volume Mesh" radio button.
    *   Click the `#generate-gcode-viz-button` again.
    *   Assert the `figure` property of `#gcode-graph` is updated and contains `go.Mesh3d` data.

### Regression Testing Workflow

For any new feature or bug fix, the following workflow should be followed by an agent:

1.  **Write New Tests:** Add new unit tests and/or E2E tests that specifically validate the new feature or prove the bug is fixed.
2.  **Run All Tests:** Execute the entire test suite from the project root:
    ```bash
    pytest  # Runs all tests with configuration from pyproject.toml
    ```
3.  **Verify No Regressions:** Ensure that all existing tests continue to pass. If an existing test fails, the new changes have caused a regression that must be fixed before the work can be considered complete.


---

---

## Claude Code Specific Workflow

### For Claude Code Agents

#### 1. Project Analysis
When working on this project, Claude Code should:
1. **Read key files first**: Start with `docs/CLAUDE.md`, this file (`agents.md`), and `README.md`
2. **Understand architecture**: Review `src/meld_visualizer/` structure using modular callback system
3. **Check configuration**: Examine `config/config.json` and `pyproject.toml` for dependencies
4. **Identify test strategy**: Review `tests/` directory structure and `pytest.ini` markers

#### 2. Development Best Practices
```bash
# Always start with a fresh environment check
python --version && pip --version

# Install in development mode for immediate feedback
pip install -e ".[dev]"

# Run application to verify setup
meld-visualizer

# Run tests to ensure baseline functionality
pytest -m "not e2e"  # Skip E2E initially for speed
```

#### 3. Code Modification Workflow
1. **Before making changes**: Run `pytest -m "unit"` to establish baseline
2. **Make incremental changes**: Modify one module at a time
3. **Test frequently**: Use hot-reloading to see changes immediately
4. **Run specific tests**: Test only the modules you've modified
5. **Full test suite**: Run complete tests before committing

#### 4. Common Debugging Steps
```bash
# If app won't start
DEBUG=1 python -m meld_visualizer

# If tests fail unexpectedly
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -v

# If imports are broken
python -c "import sys; print('\n'.join(sys.path))"
python -c "import meld_visualizer; print(meld_visualizer.__file__)"

# If configuration issues
python -c "from meld_visualizer.config import load_config; print(load_config())"
```

#### 5. File Change Patterns
- **UI changes**: Modify `src/meld_visualizer/core/layout.py` → automatic reload
- **Logic changes**: Modify files in `src/meld_visualizer/callbacks/` → automatic reload  
- **Data processing**: Modify `src/meld_visualizer/core/data_processing.py` → automatic reload
- **Configuration**: Modify `config/config.json` → **requires restart**
- **Dependencies**: Modify `pyproject.toml` → **requires reinstall**

#### 6. Quality Assurance
```bash
# Before committing, run quality checks
black src/ tests/           # Format code
flake8 src/ tests/          # Check style
mypy src/                   # Type checking
pytest --cov=src/meld_visualizer  # Test with coverage
```

### Agent Notes: UI Components
- **Tabs**: Asserted in `tests/e2e/test_tabs_e2e.py`. Update labels there if UI copy changes
- **Themes**: App resolves Bootstrap theme via `config.APP_CONFIG['theme']`, falls back to `dbc.themes.BOOTSTRAP`
- **Offline development**: Consider local CSS file under `assets/` if external CDN access is limited
- **Component IDs**: Use pattern matching IDs like `{'type': 'component-type', 'index': 'identifier'}`
- **Callbacks**: All use `@callback` decorator with Input/Output/State patterns

### Testing Strategy for Agents
1. **Unit tests first**: Fast feedback on data processing functions
2. **Integration tests**: Verify service interactions work correctly  
3. **E2E tests last**: Comprehensive but slow browser automation
4. **Coverage reports**: Use to identify untested code paths
5. **Performance tests**: Monitor for regressions in large file handling
