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

1.  **Install requirements:** We recommend using a virtual environment. Open a terminal or command prompt in the project directory and run:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Start the application:** In the same terminal, run the main `app.py` file:
    ```bash
    python app.py
    ```
3.  The application will automatically open in your default web browser.

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

### 3. Configuration (`config.json`)

Settings can be changed either by using the "Settings" tab within the running application or by directly editing the `config.json` file.

**IMPORTANT:** After saving any changes (either in the file or in the app), you must **close and restart the application** (`python app.py`) for your changes to take effect.

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

The application is broken into logical modules to promote maintainability and separation of concerns.

```
MELD_Visualizer/
├── app.py                  # Main application entry point
├── layout.py              # UI layout and components
├── data_processing.py     # Data parsing and transformation
├── config.py              # Configuration management
├── constants.py           # Application constants
├── security_utils.py      # Security and validation
├── logging_config.py      # Logging configuration
├── callbacks/             # Dash callback modules
│   ├── data_callbacks.py
│   ├── graph_callbacks.py
│   ├── visualization_callbacks.py
│   ├── filter_callbacks.py
│   └── config_callbacks.py
├── services/              # Service layer
│   ├── cache_service.py
│   ├── data_service.py
│   └── file_service.py
├── tests/                 # Test suites
│   ├── test_data_processing.py
│   ├── test_services.py
│   ├── test_validation.py
│   ├── test_integration.py
│   ├── test_performance.py
│   └── e2e/
│       └── test_app_e2e.py
├── docs/                  # Documentation
│   ├── api/
│   ├── architecture/
│   ├── components/
│   └── user-guide/
├── CSV/                   # Sample data files
├── requirements.txt       # Production dependencies
├── requirements-dev.txt   # Development dependencies
├── config.json           # User configuration
├── agents.md             # Detailed instructions for AI agents/developers
└── README.md             # This file
```

-   `app.py`: The main entry point. It initializes the Dash app, brings all pieces together, and runs the server. **This is the file you execute.**
-   `layout.py`: Contains all functions that create the visual components and structure of the app (the "view").
-   `callbacks.py`: Contains all the `@callback` functions that define the app's interactivity and logic (the "controller").
-   `data_processing.py`: Contains helper functions for data manipulation, such as parsing CSV files (parse_contents), parsing G-code files     (parse_gcode_file), and performing complex mesh generation calculations (generate_volume_mesh).
-   `config.py`: Handles loading the `config.json` file, defines theme constants, and centralizes configuration variables used by the app at runtime.
-   `config.json`: The user-facing configuration file. Stores defaults for themes and graph options.

### 5. Development Workflow

Running the app with `python app.py` starts it in **Debug Mode**. This enables **hot-reloading**, where most changes to the Python code (`layout.py`, `callbacks.py`, etc.) will automatically be reflected in the running application without requiring a manual restart.

*Note: Changes to `config.py` or `config.json` still require a manual restart to be loaded.*

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
# Run all tests with coverage
python run_tests_with_coverage.py

# Run specific test suites
pytest tests/test_data_processing.py -v
pytest tests/test_services.py -v
pytest tests/test_validation.py -v

# Run only unit tests (exclude E2E)
pytest -m "not e2e"

# Run E2E tests
pytest -m "e2e"

# Generate coverage report
pytest --cov=. --cov-report=html
```

For more detailed information on the testing strategy, see the `agents.md` file.

### 7. Building a Standalone Executable

You can bundle the application into a single executable file using `pyinstaller`. The following instructions are for **Windows**. The process may vary for other operating systems.

#### **Step 1: Generate a Spec File**

First, run `pyinstaller` to create a `.spec` file. This file acts as a build recipe.
```bash
pyinstaller --name VolumetricPlotter --windowed --onefile app.py
```

#### **Step 2: Edit the Spec File**

Open `VolumetricPlotter.spec` in a text editor. You need to tell PyInstaller where to find the `config.json` file and include other hidden packages that Dash uses. Modify your spec file to look like this:
```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(['app.py'],
             pathex=['C:\\path\\to\\your\\project\\volumetric_plotter_project'], # IMPORTANT: Use the absolute path to your project folder
             binaries=[],
             datas=[('config.json', '.')],  # Tells PyInstaller to include config.json
             hiddenimports=[
                'pkg_resources.py2_warn',
                'dash_bootstrap_components._components',
                'plotly.express'
             ], # Helps PyInstaller find packages Dash loads dynamically
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='VolumetricPlotter',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False, # Should be False if using --windowed
          icon=None) # You can add a path to an .ico file here
```
#### **Step 3: Build from the Spec File**

Now, run `pyinstaller` again, but this time point it to your modified `.spec` file.
```bash
pyinstaller VolumetricPlotter.spec
```
This will create a `dist` folder containing `VolumetricPlotter.exe`. This executable can be shared and run on other Windows machines without requiring a Python installation.

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
- [Development Guide](agents.md) - Detailed development instructions

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
- **Sample Files**: Available in the `CSV/` directory

---

**Made with ❤️ for the MELD manufacturing community**
