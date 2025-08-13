# Dash Volumetric Plotter

Welcome to the Dash Volumetric Plotter, a powerful and interactive data visualization tool designed for analyzing 3D process data. This application allows users to upload CSV data, explore it through various 3D and 2D plots, and customize the visualization to uncover insights.

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
    (If a `requirements.txt` file is not available, you can install the packages individually: `pip install pandas numpy dash dash-bootstrap-components plotly`)

2.  **Start the application:** In the same terminal, run the main `app.py` file:
    ```bash
    python app.py
    ```
3.  The application will automatically open in your default web browser.

### 2. Configuration (`config.json`)

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
/
├── CSV/
│   └── (sample data files)
├── tests/
│   ├── test_data_processing.py
│   └── test_app_e2e.py
├── app.py                  # Main entry point, runs the server
├── layout.py               # Defines the UI layout (the "view")
├── callbacks.py            # Contains all app interactivity (the "controller")
├── data_processing.py      # Data parsing and mesh generation logic
├── config.py               # Handles loading and managing configuration
├── config.json             # User-facing configuration file
├── agents.md               # Detailed instructions for AI agents/developers
└── README.md               # This file
```

-   `app.py`: The main entry point. It initializes the Dash app, brings all pieces together, and runs the server. **This is the file you execute.**
-   `layout.py`: Contains all functions that create the visual components and structure of the app (the "view").
-   `callbacks.py`: Contains all the `@callback` functions that define the app's interactivity and logic (the "controller").
-   `data_processing.py`: Contains helper functions for data manipulation, such as parsing the CSV and performing complex mesh generation calculations.
-   `config.py`: Handles loading the `config.json` file, defines theme constants, and centralizes configuration variables used by the app at runtime.
-   `config.json`: The user-facing configuration file. Stores defaults for themes and graph options.

### 5. Development Workflow

Running the app with `python app.py` starts it in **Debug Mode**. This enables **hot-reloading**, where most changes to the Python code (`layout.py`, `callbacks.py`, etc.) will automatically be reflected in the running application without requiring a manual restart.

*Note: Changes to `config.py` or `config.json` still require a manual restart to be loaded.*

### 6. Testing

The project includes a test suite using `pytest`. The tests are located in the `tests/` directory and are separated into unit tests and end-to-end (E2E) tests.

-   **Unit Tests:** `tests/test_data_processing.py` tests the data manipulation functions in isolation.
-   **E2E Tests:** `tests/test_app_e2e.py` tests the full application from a user's perspective.

To run the tests, execute `pytest` in the root directory:
```bash
pytest
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
- Settings

> **Note on styling:** The app loads a Bootstrap theme (from `config.py` if set, otherwise default) so `dash-bootstrap-components` widgets render correctly. If you see blue underlined links instead of tabs, your theme didn’t load—check network access or switch to a local CSS under `assets/`.
