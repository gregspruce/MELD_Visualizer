# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Quick Start for Claude Code

### Prerequisites
- Python 3.8 or higher
- Git (for repository access)

### Installation
```bash
# Clone repository
git clone https://github.com/gregspruce/MELD_Visualizer.git
cd MELD_Visualizer

# Install in development mode (recommended)
pip install -e ".[dev,test,playwright,build]"

# Verify installation
python -c "import meld_visualizer; print('✓ Installation successful')"
```

## Commands

### Running the Application
```bash
# Using the installed command (recommended)
meld-visualizer

# Running as a Python module
python -m src.meld_visualizer.app
```
The app runs in debug mode by default with hot-reloading enabled.

### Testing
```bash
# Run all tests from project root
pytest

# Run unit tests only
pytest -m "unit"
```

### Dependencies
Dependencies are managed in `pyproject.toml`.

- **Production:** `dash`, `dash-bootstrap-components`, `plotly`, `pandas`, `numpy`, `scipy`
- **Development:** `black`, `flake8`, `mypy`, `pre-commit`
- **Testing:** `pytest`, `pytest-asyncio`, `pytest-cov`, `playwright`, `pytest-playwright`
- **Build:** `pyinstaller`


## Architecture

This is a **Dash web application** for visualizing 3D process data from MELD manufacturing. The application follows a modular MVC-like architecture:

### Core Modules
- **`src/meld_visualizer/app.py`**: Main entry point. Creates Dash app, loads layout/callbacks, starts server
- **`src/meld_visualizer/core/layout.py`**: UI components and structure (View layer)
- **`src/meld_visualizer/callbacks/`**: Modular callback system (Controller layer)
- **`src/meld_visualizer/core/data_processing.py`**: Data parsing, mesh generation, G-code processing (Model layer)
- **`src/meld_visualizer/services/`**: Business logic layer
- **`src/meld_visualizer/config.py`**: Configuration loading, theme management, constants
- **`src/meld_visualizer/utils/`**: Utility modules

### Key Features
- **CSV Data Upload**: Processes MELD manufacturing data.
- **G-code Visualization**: Parses `.nc` files to simulate toolpaths and volume meshes.
- **3D Visualizations**: Interactive scatter plots, toolpath plots, and volume meshes.
- **Theme Support**: 20+ Bootstrap themes.
- **Configurable UI**: User settings saved in `config.json`, editable via Settings tab.
- **Enhanced Desktop UI**: Optimized interface with advanced tab navigation, organized control panels, and comprehensive user feedback.

### Important Files
- **`config/config.json`**: User-configurable themes, plot options, and column mappings.
- **`data/csv/`**: Sample CSV files for testing and development.
- **`data/nc/`**: Sample G-code files for testing and development.
- **`pyproject.toml`**: Modern Python packaging with dependencies and tool configuration.
- **`README.md`**: Project overview, installation, and usage instructions.

