# AI Agent Guidelines for MELD Visualizer

This document provides specific guidance for AI agents (like Claude Code) when working with the MELD Visualizer repository.

## 1. Quick Start for AI Agents

### Prerequisites
*   Python 3.8 or higher
*   Git (for repository access)

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

## 2. Commands

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

## 3. Dependencies

Dependencies are managed in `pyproject.toml`.

*   **Production:** `dash`, `dash-bootstrap-components`, `plotly`, `pandas`, `numpy`, `scipy`
*   **Development:** `black`, `flake8`, `mypy`, `pre-commit`
*   **Testing:** `pytest`, `pytest-asyncio`, `pytest-cov`, `playwright`, `pytest-playwright`
*   **Build:** `pyinstaller`

## 4. Architecture Overview

The MELD Visualizer is a **Dash web application** for visualizing 3D process data from MELD manufacturing. The application follows a modular MVC-like architecture:

### Core Modules
*   **`src/meld_visualizer/app.py`**: Main entry point. Creates Dash app, loads layout/callbacks, starts server
*   **`src/meld_visualizer/core/layout.py`**: UI components and structure (View layer)
*   **`src/meld_visualizer/callbacks/`**: Modular callback system (Controller layer)
*   **`src/meld_visualizer/core/data_processing.py`**: Data parsing, mesh generation, G-code processing (Model layer)
*   **`src/meld_visualizer/services/`**: Business logic layer
*   **`src/meld_visualizer/config.py`**: Configuration loading, theme management, constants
*   **`src/meld_visualizer/utils/`**: Utility modules

## 5. Key Features

*   **CSV Data Upload**: Processes MELD manufacturing data.
*   **G-code Visualization**: Parses `.nc` files to simulate toolpaths and volume meshes.
*   **3D Visualizations**: Interactive scatter plots, toolpath plots, and volume meshes.
*   **Theme Support**: 20+ Bootstrap themes.
*   **Configurable UI**: User settings saved in `config.json`, editable via Settings tab.
*   **Enhanced Desktop UI**: Optimized interface with advanced tab navigation, organized control panels, and comprehensive user feedback.

## 6. Important Files for AI Agents

*   **`config/config.json`**: User-configurable themes, plot options, and column mappings.
*   **`data/csv/`**: Sample CSV files for testing and development.
*   **`data/nc/`**: Sample G-code files for testing and development.
*   **`pyproject.toml`**: Modern Python packaging with dependencies and tool configuration.
*   **`README.md`**: Project overview, installation, and usage instructions.

## 7. General Guidance for AI Agents

*   **Adhere to existing conventions:** Always analyze surrounding code, tests, and configuration first.
*   **Verify library usage:** Never assume a library is available. Check imports and configuration files.
*   **Mimic style and structure:** Follow existing formatting, naming, framework choices, typing, and architectural patterns.
*   **Idiomatic changes:** Understand local context to ensure changes integrate naturally.
*   **Comments:** Add comments sparingly, focusing on *why* something is done.
*   **Proactiveness:** Fulfill requests thoroughly, including implied follow-up actions.
*   **Confirm ambiguity:** Do not take significant actions beyond clear scope without confirmation.
*   **Explain changes:** Do not provide summaries unless asked.
*   **Path construction:** Always use full absolute paths for file system tools.
*   **Do not revert changes:** Unless asked or due to error.
*   **Security:** Never introduce code that exposes sensitive information.
*   **Explain critical commands:** Before executing commands that modify the file system or system state.
*   **Respect user confirmations:** Do not re-request cancelled tool calls unless explicitly asked.
