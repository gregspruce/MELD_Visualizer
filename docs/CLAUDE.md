# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Quick Start for Claude Code

### Prerequisites
- Python 3.8 or higher
- Git (for repository access)
- Chrome browser (for E2E testing)

### Installation
```bash
# Clone repository
git clone https://github.com/gregspruce/MELD_Visualizer.git
cd MELD_Visualizer

# Install in development mode (recommended)
pip install -e ".[dev]"

# Verify installation
python -c "import meld_visualizer; print('✓ Installation successful')"
```

## Commands

### Running the Application
```bash
# Method 1: Using the installed command (recommended)
meld-visualizer

# Method 2: Running as a Python module
python -m meld_visualizer

# Method 3: From source (development debugging)
python -m src.meld_visualizer.app

# Method 4: With explicit debug mode
DEBUG=1 meld-visualizer

# All methods bind to http://127.0.0.1:8050
```
The app runs in debug mode by default with hot-reloading enabled. `.py` file changes automatically refresh, themes apply instantly, and configuration changes update immediately without restart.

### Testing
```bash
# Run all tests from project root
pytest

# Run unit tests only (excludes E2E)
pytest -m "unit"
pytest -m "not e2e"  # Alternative syntax

# Run specific test categories
pytest -m "integration"  # Integration tests
pytest -m "e2e"         # E2E tests only

# Run with coverage
pytest --cov=src/meld_visualizer --cov-report=html

# Using the test runner script
bash scripts/run_tests.sh          # Uses tests/test_suite.conf or defaults to unit tests
TEST_SUITE=both bash scripts/run_tests.sh    # Run both unit and E2E tests
TEST_SUITE=e2e bash scripts/run_tests.sh     # Run E2E tests only
```

### Dependencies
```bash
# Production dependencies (modern approach)
pip install -e .

# With optional dependencies
pip install -e ".[dev]"      # Development tools
pip install -e ".[test]"     # Test dependencies
pip install -e ".[build]"    # Build tools

# Legacy approach (still supported)
pip install -r requirements.txt         # Production dependencies
pip install -r requirements-dev.txt     # Development/test dependencies
```

### Building Executable
```bash
# Modern Python packaging
python -m build

# PyInstaller executable
pyinstaller --name MELD-Visualizer --windowed --onefile \
    --add-data "config:config" \
    --add-data "data:data" \
    --hidden-import="dash_bootstrap_components._components" \
    src/meld_visualizer/app.py

# Build from modified spec
pyinstaller MELD-Visualizer.spec
```

## Architecture

This is a **Dash web application** for visualizing 3D process data from MELD manufacturing. The application follows a modular MVC-like architecture:

### Core Modules
- **`src/meld_visualizer/app.py`**: Main entry point. Creates Dash app, loads layout/callbacks, starts server
- **`src/meld_visualizer/core/layout.py`**: UI components and structure (View layer)  
- **`src/meld_visualizer/callbacks/`**: Modular callback system (Controller layer)
  - `data_callbacks.py`: Data upload and processing callbacks
  - `graph_callbacks.py`: 3D visualization callbacks  
  - `visualization_callbacks.py`: Plot generation callbacks
  - `filter_callbacks.py`: Data filtering callbacks
  - `config_callbacks.py`: Settings and configuration callbacks
- **`src/meld_visualizer/core/data_processing.py`**: Data parsing, mesh generation, G-code processing (Model layer)
- **`src/meld_visualizer/services/`**: Business logic layer
  - `cache_service.py`: Caching and performance optimization
  - `data_service.py`: Data processing and transformation
  - `file_service.py`: File handling and validation
- **`src/meld_visualizer/config.py`**: Configuration loading, theme management, constants
- **`src/meld_visualizer/utils/`**: Utility modules
  - `security_utils.py`: Security validation and sanitization
  - `logging_config.py`: Logging configuration

### Key Features
- **CSV Data Upload**: Processes MELD manufacturing data with automatic unit conversion (inches→mm)
- **G-code Visualization**: Parses `.nc` files to simulate toolpaths and volume meshes
- **3D Visualizations**: Interactive scatter plots, toolpath plots, and volume meshes with Z-axis scaling
- **Accurate Volume Calculations**: Corrected feedstock geometry using 0.5" × 0.5" square rod (161.3mm²)
- **Feedstock Configuration**: Supports both square rod and circular wire feedstock types
- **Theme Support**: 20+ Bootstrap themes (light/dark) with matching Plotly templates
- **Configurable UI**: User settings saved in `config.json`, editable via Settings tab

### Data Flow
1. File upload → `src/meld_visualizer/core/data_processing.py` parsing functions
2. Parsed data → `src/meld_visualizer/services/data_service.py` for processing
3. Processed data → `src/meld_visualizer/callbacks/` modules for plot generation  
4. UI interactions → callbacks update plots/filters via `src/meld_visualizer/services/`
5. Configuration changes → saved to `config/config.json`

### Testing Structure
- **Unit Tests**: `tests/unit/test_*.py` - Test individual functions and modules in isolation
- **Integration Tests**: `tests/integration/test_*.py` - Test component interactions and service integrations
- **E2E Tests**: `tests/e2e/test_*.py` - Browser automation testing full user workflows
- **Configuration**: `tests/pytest.ini` and `tests/test_suite.conf`
- Uses `pytest` with Selenium for E2E testing (requires Chrome)
- Test coverage configured in `pyproject.toml`

### Important Files
- **`config/config.json`**: User-configurable themes, plot options, column mappings, and feedstock geometry
- **`data/csv/`**: Sample CSV files for testing and development
- **`data/nc/`**: Sample G-code files for testing and development
- **`src/meld_visualizer/constants.py`**: Feedstock geometry constants and configuration types
- **`tests/pytest.ini`**: Test configuration with markers (unit, integration, e2e)
- **`tests/test_suite.conf`**: Test runner configuration
- **`pyproject.toml`**: Modern Python packaging with dependencies and tool configuration
- **`docs/agents.md`**: Detailed development instructions and testing strategy

### Development Notes
- **Enhanced Hot-Reload**: 
  - ✅ `.py` files hot-reload automatically in debug mode
  - ✅ **Themes**: Apply instantly via Settings tab (no restart needed)
  - ✅ **Graph Options**: Update immediately after saving in Settings tab
  - ⚠️ Manual `config/config.json` edits still require restart
- All 3D plots support Z-axis stretch factor for better layer visualization
- G-code parser handles M34/M35 commands for feed rate control
- **Volume mesh generation**: Creates 3D representations with mathematically correct feedstock geometry
  - **Feedstock geometry**: 0.5" × 0.5" square rod (12.7mm × 12.7mm, 161.3mm²)
  - **Volume accuracy**: 27% more accurate than previous circular wire assumption
  - **Configuration**: Supports both square and circular feedstock types via `config.json`
- **Feedstock Configuration Options**:
  - `feedstock_type`: "square" (default) or "circular"
  - `feedstock_dimension_inches`: 0.5 (default, configurable)
  - Automatic area calculations based on geometry type
- Package follows src-layout with proper `__init__.py` files for imports
- Entry points defined in `pyproject.toml` for `meld-visualizer` command
- Code quality enforced with black, flake8, mypy, and pre-commit hooks
- Modern packaging allows `pip install -e .` for development installation

### Common Patterns
- **Pattern matching IDs**: `{'type': 'component-type', 'index': 'identifier'}`
- **Dash callbacks**: Use `@callback` decorator with Input/Output/State
- **Error handling**: Returns tuple `(data, error_message, conversion_flag)`
- **Theming**: All plots use `PLOTLY_TEMPLATE` from config for consistent theming
- **Import paths**: Use `from meld_visualizer.core import data_processing`
- **Service layer**: Business logic in `services/` modules for separation of concerns
- **Configuration**: Centralized in `config.py` with `config/config.json` file
- **Testing**: Modular test structure with fixtures in `tests/conftest.py`

## Troubleshooting for Claude Code

### Common Issues and Quick Fixes
```bash
# Application won't start
DEBUG=1 meld-visualizer

# Tests hanging
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest

# Import errors
pip install -e ".[dev]"
python -c "import meld_visualizer; print(meld_visualizer.__file__)"

# Configuration issues
python -c "from meld_visualizer.config import load_config; print(load_config())"

# E2E tests failing (missing Chrome)
pytest -m "not e2e"  # Skip E2E tests
```

### Development Workflow for Claude Code
1. **Setup**: `pip install -e ".[dev]"` and verify with `meld-visualizer`
2. **Quick test**: `pytest -m "not e2e"` for fast validation
3. **Development**: Modify files with hot-reloading active
4. **Full validation**: `pytest` for complete test suite
5. **Quality check**: `black src/ tests/ && flake8 src/ tests/`

### Key File Locations
- **Main app**: `src/meld_visualizer/app.py`
- **UI layout**: `src/meld_visualizer/core/layout.py`
- **Data processing**: `src/meld_visualizer/core/data_processing.py`
- **Callbacks**: `src/meld_visualizer/callbacks/`
- **Services**: `src/meld_visualizer/services/`
- **Configuration**: `config/config.json`
- **Tests**: `tests/` with markers in `pytest.ini`

### Testing Strategy for Claude Code
1. **Unit tests first**: Fast feedback on data processing functions
2. **Integration tests**: Verify service interactions work correctly  
3. **E2E tests last**: Comprehensive but slow browser automation
4. **Coverage reports**: Use to identify untested code paths
5. **Performance tests**: Monitor for regressions in large file handling

For comprehensive troubleshooting, see `docs/TROUBLESHOOTING.md`.