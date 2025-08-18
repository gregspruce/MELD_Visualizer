# MELD Visualizer (Dash Volumetric Plotter)

A powerful 3D visualization platform for MELD (Manufacturing using Extreme Layer Deposition) process data analysis and toolpath visualization. This application allows users to upload CSV data from a manufacturing process or the original G-code (.nc) file to visualize, compare, and understand the build.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-green)
![License](https://img.shields.io/badge/license-MIT-purple)
![Tests](https://img.shields.io/badge/tests-passing-brightgreen)
![Coverage](https://img.shields.io/badge/coverage-85%25-yellowgreen)

## Features

### Core Capabilities
- **3D Visualization**: Interactive scatter plots, mesh generation, and toolpath rendering
- **File Support**: CSV data files and G-code (.nc) programs  
- **Automatic Unit Conversion**: Imperial to metric conversion with detection
- **Real-time Filtering**: Range-based and custom column filtering
- **Multi-theme Support**: 20+ Bootstrap themes with matching Plotly templates
- **Performance Optimization**: Multi-level caching and lazy loading
- **Security**: Input validation, path traversal protection, and content inspection

### Visualization Types
- 3D Scatter Plots with customizable coloring
- 3D Volume Mesh generation from toolpaths
- 3D Line Plots for path analysis
- 2D Time Series plots
- Z-axis scaling for layer visibility

This guide explains how to run the application, customize its appearance, and understand its structure for future development.

---

## User Guide

This section is for users who want to run the application and configure its settings.

### 1. Running the Application

To run the application, you must have Python and the required packages installed.

#### Installation Options

**Option 1: Using pip (Recommended)**
```bash
# Install from PyPI (when available)
pip install meld-visualizer

# Run the application
meld-visualizer
```

**Option 2: Development Installation**
```bash
# Clone the repository
git clone https://github.com/MELD-labs/meld-visualizer.git
cd meld-visualizer

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Run the application
python -m meld_visualizer
# OR
meld-visualizer
```

**Option 3: From Source (Legacy)**
```bash
# Install dependencies (legacy approach)
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run from source
python -m src.meld_visualizer.app
```

The application will automatically open in your default web browser at `http://127.0.0.1:8050`.

### 2. Using the Visualization Tabs

*   **CSV Data Tabs (Main 3D, 2D Time Plot, etc.):** Upload a CSV file using the main "Drag and Drop" area. These tabs will populate with the actual, logged data from the machine.
*   **G-code Visualization Tab:**
    1.  Navigate to the **"G-code Visualization"** tab.
    2.  Use its dedicated upload box to select a G-code program file (typically with a `.nc` extension).
    3.  A success message will appear once the file is parsed.
    4.  Select either the "Simulated Toolpath" or "Simulated Volume Mesh" view.
    5.  Click the **"Generate Visualization"** button to see the plot.

#### **Controlling 3D Plot Scaling**

On the "3D Toolpath Plot", "3D Volume Mesh", and "G-code Visualization" tabs, you will find a **"Z-Axis Stretch Factor"** input.

*   **Function:** This control allows you to visually stretch or compress the Z-axis of the 3D plots. This is useful for making the layer details of a flat part more visible.
*   **Usage:**
    *   A value of **1.0** represents a true-to-scale plot where X, Y, and Z axes are scaled according to their data ranges.
    *   A value **greater than 1.0** (e.g., `2.0`) will stretch the Z-axis, making the plot appear taller.
    *   A value **less than 1.0** (e.g., `0.5`) will compress the Z-axis, making it appear flatter.

### 3. Configuration (`config/config.json`)

Settings can be changed either by using the "Settings" tab within the running application or by directly editing the `config/config.json` file.

**IMPORTANT:** After saving any changes (either in the file or in the app), you must **close and restart the application** for your changes to take effect.

#### **Changing the Application Theme**

-   **Key:** `default_theme`
-   **Function:** Controls the overall color scheme and style of the application UI.

**Available Themes:**
*   **Light Themes:** `Cerulean (Default)`, `Cosmo`, `Flatly`, `Journal`, `Litera`, `Lumen`, `Lux`, `Materia`, `Minty`, `Morph`, `Pulse`, `Quartz`, `Sandstone`, `Simplex`, `Sketchy`, `Spacelab`, `United`, `Yeti`, `Zephyr`
*   **Dark Themes:** `Cyborg`, `Darkly`, `Slate`, `Solar`, `Superhero`, `Vapor`

*Example:* To use the dark "Cyborg" theme, your `config.json` would have this line:
`"default_theme": "Cyborg",`

#### **Synchronizing Plot Themes**

-   **Key:** `plotly_template`
-   **Function:** Ensures the graphs (e.g., scatter plots) match the application theme.
-   **Behavior:**
    *   **Automatic (Recommended):** If you **delete this line** from `config.json`, the application will automatically select `"plotly_dark"` for dark themes and `"plotly_white"` for all light themes.
    *   **Manual Override:** To force a specific style, specify a template name.
-   **Common Templates:** `plotly_white`, `plotly_dark`, `ggplot2`, `seaborn`, `simple_white`

*Example:* To manually set a dark plot background:
`"plotly_template": "plotly_dark",`

#### **Customizing Graph Options**

You can control which data columns appear as selectable options for each plot.

**IMPORTANT:** Column names in `config.json` are **case-sensitive** and must exactly match the column headers in your CSV file.

-   `graph_1_options`: Sets the color dropdown options for the top-left 3D scatter plot.
-   `graph_2_options`: Sets the color dropdown options for the top-right 3D scatter plot.
-   `plot_2d_y_options`: Sets the Y-Axis radio button options for the 2D time plot.
-   `plot_2d_color_options`: Sets the Color Scale radio button options for the 2D time plot.

### 3. In-App Settings Tab

The "Settings" tab provides an easy interface for modifying all the options mentioned above.

1.  Load a CSV file. The dropdowns for graph options will populate with columns from your file.
2.  Navigate to the "Settings" tab.
3.  Make your desired changes.
4.  Click the **"Save Configuration"** button.
5.  A success message will appear. **You must close and restart the application** for the new settings to take effect.

---

## Developer Guide

This section is for developers who want to modify, maintain, or build upon the application.

### 4. Project Structure

The application follows modern Python packaging standards with a clean, modular structure:

```
meld_visualizer/
├── pyproject.toml          # Modern Python packaging configuration
├── README.md              # This file
├── requirements.txt       # Production dependencies (legacy support)
├── requirements-dev.txt   # Development dependencies (legacy support)
├── src/meld_visualizer/   # Source package
│   ├── __init__.py
│   ├── app.py            # Main application entry point
│   ├── config.py         # Configuration management
│   ├── constants.py      # Application constants
│   ├── core/             # Core functionality
│   │   ├── __init__.py
│   │   ├── layout.py     # UI layout and components (View layer)
│   │   └── data_processing.py  # Data parsing and transformation (Model layer)
│   ├── callbacks/        # Dash callback modules (Controller layer)
│   │   ├── __init__.py
│   │   ├── config_callbacks.py
│   │   ├── data_callbacks.py
│   │   ├── filter_callbacks.py
│   │   ├── graph_callbacks.py
│   │   └── visualization_callbacks.py
│   ├── services/         # Business logic layer
│   │   ├── __init__.py
│   │   ├── cache_service.py
│   │   ├── data_service.py
│   │   └── file_service.py
│   └── utils/            # Utility modules
│       ├── __init__.py
│       ├── logging_config.py
│       └── security_utils.py
├── tests/                # Comprehensive test suite
│   ├── conftest.py      # Pytest configuration
│   ├── pytest.ini      # Test settings
│   ├── test_suite.conf  # Test runner configuration
│   ├── unit/            # Unit tests
│   ├── integration/     # Integration tests
│   └── e2e/             # End-to-end tests
├── docs/                # Consolidated documentation
│   ├── CLAUDE.md        # AI assistant instructions
│   ├── architecture/    # System architecture docs
│   ├── components/      # Component documentation
│   ├── user-guide/      # User manual
│   └── api/             # API documentation
├── config/              # Configuration files
│   └── config.json     # User-configurable settings
├── data/                # Sample and test data
│   ├── csv/            # Sample CSV files
│   └── nc/             # Sample G-code files
├── scripts/             # Build and utility scripts
│   ├── run_tests.sh    # Test runner
│   └── create_pr.sh    # PR creation script
└── reports/             # Generated reports (coverage, performance)
```

#### Key Components
-   **`src/meld_visualizer/app.py`**: Main entry point. Initializes the Dash app, loads all modules, and starts the server.
-   **`src/meld_visualizer/core/layout.py`**: UI components and structure (View layer).
-   **`src/meld_visualizer/callbacks/`**: Modular callback system (Controller layer) with separate files for different functionality areas.
-   **`src/meld_visualizer/core/data_processing.py`**: Data parsing, mesh generation, and G-code processing (Model layer).
-   **`src/meld_visualizer/services/`**: Business logic services including caching, data processing, and file handling.
-   **`src/meld_visualizer/config.py`**: Configuration management and theme handling.
-   **`config/config.json`**: User-configurable settings file (themes, plot options, column mappings).
-   **`pyproject.toml`**: Modern Python packaging configuration with dependencies and metadata.

### 5. Development Workflow

#### Development Setup
```bash
# Clone the repository
git clone https://github.com/MELD-labs/meld-visualizer.git
cd meld-visualizer

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Run the application (debug mode is enabled by default)
python -m meld_visualizer
# OR
meld-visualizer

# For explicit debug mode
DEBUG=1 meld-visualizer
```

#### Hot Reloading
The application starts in **Debug Mode** by default, enabling **hot-reloading** where most changes to Python code will automatically refresh without requiring a manual restart.

*Note: Changes to `src/meld_visualizer/config.py` or `config/config.json` still require a manual restart.*

#### Code Quality Tools
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

### 6. Testing

The project includes a comprehensive test suite using `pytest`. The tests are located in the `tests/` directory.

#### Test Categories
- **Unit Tests**: Test individual functions and modules
- **Integration Tests**: Test component interactions
- **Security Tests**: Validate input sanitization and security measures
- **Performance Tests**: Benchmark critical operations
- **E2E Tests**: Test full application workflows

#### Running Tests
```bash
# Install test dependencies
pip install -e ".[test]"

# Run all tests
pytest

# Run with coverage reporting
pytest --cov=src/meld_visualizer --cov-report=html

# Run specific test categories
pytest -m "unit"        # Unit tests only
pytest -m "integration" # Integration tests only
pytest -m "e2e"         # End-to-end tests only
pytest -m "not e2e"     # Exclude E2E tests

# Run specific test files
pytest tests/unit/test_data_processing.py -v
pytest tests/integration/test_services.py -v

# Using the test runner script
bash scripts/run_tests.sh          # Uses tests/test_suite.conf
TEST_SUITE=both bash scripts/run_tests.sh    # Run both unit and E2E tests
TEST_SUITE=e2e bash scripts/run_tests.sh     # Run E2E tests only
```

For more detailed information on the testing strategy, see the `agents.md` file.

### 7. Building a Standalone Executable

The application can be packaged into a standalone executable using PyInstaller.

#### Prerequisites
```bash
# Install build dependencies
pip install -e ".[build]"
```

#### Method 1: Using Python Build Tools
```bash
# Build wheel and source distribution
python -m build

# The built packages will be in dist/
# Install the wheel: pip install dist/meld_visualizer-*.whl
```

#### Method 2: PyInstaller Executable
```bash
# Generate spec file
pyinstaller --name MELD-Visualizer --windowed --onefile \
    --add-data "config:config" \
    --add-data "data:data" \
    --hidden-import="dash_bootstrap_components._components" \
    --hidden-import="plotly.express" \
    --hidden-import="pkg_resources.py2_warn" \
    src/meld_visualizer/app.py

# Build from spec file (after customization if needed)
pyinstaller MELD-Visualizer.spec
```

#### Example PyInstaller Spec Configuration
```python
# MELD-Visualizer.spec
a = Analysis(
    ['src/meld_visualizer/app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config/config.json', 'config'),
        ('data', 'data'),
    ],
    hiddenimports=[
        'pkg_resources.py2_warn',
        'dash_bootstrap_components._components',
        'plotly.express',
        'meld_visualizer.callbacks',
        'meld_visualizer.services',
        'meld_visualizer.utils',
    ],
    # ... rest of configuration
)
```

The built executable will be in `dist/MELD-Visualizer.exe` and can run on target systems without Python installation.

---

## E2E Tabs Coverage & Theme Note
The E2E suite asserts the application title (**Volumetric Data Plotter**) and verifies the presence & clickability of these tab labels:

- Main 3D Plots
- 2D Time Plot
- Custom 3D Plot
- Data Table
- 3D Toolpath Plot
- 3D Volume Mesh
- G-code Visualization
- Settings

> **Note on styling:** The app loads a Bootstrap theme (from `config.py` if set, otherwise default) so `dash-bootstrap-components` widgets render correctly. If you see blue underlined links instead of tabs, your theme didn't load—check network access or switch to a local CSS under `assets/`.

---

## Documentation

- [User Guide](docs/user-guide/user-guide.md) - Complete usage instructions
- [API Documentation](docs/api/openapi.yaml) - REST API specifications
- [Architecture](docs/architecture/architecture.md) - System design and diagrams
- [Components](docs/components/components.md) - Detailed component documentation
- [Development Guide](docs/agents.md) - Detailed development instructions

## Security Features

- **Input Validation**: All user inputs are validated and sanitized
- **Path Traversal Protection**: File paths are checked for directory traversal attempts
- **File Size Limits**: 10MB maximum file size enforced
- **Content Inspection**: Files are scanned for malicious content
- **Safe Error Handling**: Error messages don't expose sensitive information
- **Configuration Security**: Only whitelisted configuration keys are allowed

## Performance

### Benchmarks
- CSV parsing: < 50ms for 100 rows, < 2s for 10,000 rows
- Mesh generation: < 500ms for 100 points, < 5s for 1,000 points
- Cache hit rate: > 80% for typical usage
- Memory usage: < 500MB for standard datasets

### Optimization Tips
- Use filtering for large datasets
- Adjust mesh detail level for performance
- Enable caching (default)
- Use appropriate Z-axis scaling

## Troubleshooting

### Common Issues

**Application won't start**
```bash
# Check Python version
python --version  # Should be 3.8+

# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

**File upload fails**
- Check file size (< 10MB limit)
- Verify file format (CSV or .nc)
- Ensure required columns exist

**Slow performance**
- Reduce data points using filters
- Lower mesh detail level
- Clear browser cache
- Restart application

See [User Guide](docs/user-guide/user-guide.md#troubleshooting) for more solutions.

## Contributing

We welcome contributions! When contributing:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Write tests for new features
4. Ensure all tests pass
5. Update documentation
6. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
7. Push to the branch (`git push origin feature/AmazingFeature`)
8. Open a Pull Request

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Support

- **Issues**: Report bugs through GitHub Issues
- **Documentation**: See the `docs/` directory
- **Sample Files**: Available in the `data/csv/` and `data/nc/` directories

---

**Made with ❤️ for the MELD manufacturing community**
