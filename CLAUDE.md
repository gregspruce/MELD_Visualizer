# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Running the Application
```bash
python app.py
```
The app runs in debug mode by default with hot-reloading enabled. Set `DEBUG="1"` environment variable for explicit debug mode.

### Testing
```bash
# Run all tests
pytest

# Run unit tests only (excludes E2E)
pytest -m "not e2e"

# Run E2E tests only  
pytest -m "e2e"

# Using the test runner script
bash run_tests.sh          # Uses test_suite.conf or defaults to unit tests
TEST_SUITE=both bash run_tests.sh    # Run both unit and E2E tests
TEST_SUITE=e2e bash run_tests.sh     # Run E2E tests only
```

### Dependencies
```bash
# Production dependencies
pip install -r requirements.txt

# Development/test dependencies
pip install -r requirements-dev.txt
```

### Building Executable
```bash
# Generate spec file
pyinstaller --name VolumetricPlotter --windowed --onefile app.py

# Build from modified spec
pyinstaller VolumetricPlotter.spec
```

## Architecture

This is a **Dash web application** for visualizing 3D process data from MELD manufacturing. The application follows a modular MVC-like architecture:

### Core Modules
- **`app.py`**: Main entry point. Creates Dash app, loads layout/callbacks, starts server
- **`layout.py`**: UI components and structure (View layer)  
- **`callbacks.py`**: Interactive logic and event handlers (Controller layer)
- **`data_processing.py`**: Data parsing, mesh generation, G-code processing (Model layer)
- **`config.py`**: Configuration loading, theme management, constants

### Key Features
- **CSV Data Upload**: Processes MELD manufacturing data with automatic unit conversion (inches→mm)
- **G-code Visualization**: Parses `.nc` files to simulate toolpaths and volume meshes
- **3D Visualizations**: Interactive scatter plots, toolpath plots, and volume meshes with Z-axis scaling
- **Theme Support**: 20+ Bootstrap themes (light/dark) with matching Plotly templates
- **Configurable UI**: User settings saved in `config.json`, editable via Settings tab

### Data Flow
1. File upload → `data_processing.py` parsing functions
2. Parsed data → `callbacks.py` for plot generation  
3. UI interactions → callbacks update plots/filters
4. Configuration changes → saved to `config.json`

### Testing Structure
- **Unit Tests**: `tests/test_*.py` - Test data processing functions in isolation
- **E2E Tests**: `tests/e2e/test_*.py` - Browser automation testing full user workflows
- Uses `pytest` with Selenium for E2E testing (requires Chrome)

### Important Files
- `config.json`: User-configurable themes, plot options, column mappings
- `CSV/`: Sample data files for testing and development
- `pytest.ini`: Test configuration with E2E markers
- `agents.md`: Detailed development instructions and testing strategy

### Development Notes
- Hot-reloading works for `.py` files but `config.json` changes require restart
- All 3D plots support Z-axis stretch factor for better layer visualization
- Theme changes require app restart to take effect
- G-code parser handles M34/M35 commands for feed rate control
- Volume mesh generation creates 3D representations from toolpath data

### Common Patterns
- Pattern matching IDs: `{'type': 'component-type', 'index': 'identifier'}`
- Dash callbacks use `@callback` decorator with Input/Output/State
- Error handling returns tuple `(data, error_message, conversion_flag)`
- All plots use `PLOTLY_TEMPLATE` from config for consistent theming