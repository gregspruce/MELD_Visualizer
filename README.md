# MELD Visualizer

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/pypi/pyversions/meld-visualizer.svg)](https://pypi.org/project/meld-visualizer/)
[![PyPI version](https://badge.fury.io/py/meld-visualizer.svg)](https://badge.fury.io/py/meld-visualizer)

A Dash web application for visualizing 3D process data from MELD manufacturing.

The MELD Visualizer is a powerful tool for engineers, technicians, and researchers to analyze and understand the data generated during the MELD manufacturing process. It provides interactive 3D visualizations of toolpaths, material deposition, and process parameters, enabling users to gain insights into the quality and characteristics of the manufactured part.

## Key Features

-   **Interactive 3D Visualization:** Explore toolpaths and volumetric data in a fully interactive 3D environment.
-   **G-Code and CSV Support:** Load and visualize data from standard G-code files or detailed CSV process logs.
-   **Volumetric Mesh Generation:** Accurately visualizes the volume of deposited material based on process parameters.
-   **Data Filtering and Analysis:** Filter data by time, layer, and other parameters to isolate and inspect specific regions of the part.
-   **Enhanced Desktop UI:** A modern, responsive user interface optimized for desktop use, featuring tabbed navigation, organized control panels, and real-time user feedback.
-   **Customizable Plots:** Adjust plot settings, such as Z-axis scaling, to enhance visualization and analysis.
-   **Enterprise-Grade Code Quality:** Full type safety, comprehensive error handling, and automated quality assurance with pre-commit hooks.
-   **Professional Development Standards:** 100% mypy compliance, consistent formatting, and structured testing framework.

## Screenshots

Here are some screenshots of the MELD Visualizer in action:

| Main Interface                                                                                    | 3D Toolpath Tab                                                                                         | 3D Volume Mesh Tab                                                                                        |
| ------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| !<Main Interface>(.playwright-mcp/meld-visualizer-main-interface.png) | !<3D Toolpath Tab>(.playwright-mcp/meld-visualizer-3d-toolpath-tab.png) | !<3D Volume Mesh Tab>(.playwright-mcp/meld-visualizer-3d-volume-mesh-tab.png) |

## Getting Started

### Prerequisites

-   Python 3.8+
-   Git

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/gregspruce/MELD_Visualizer.git
    cd MELD_Visualizer
    ```

2.  **Install dependencies:**
    Install the project in editable mode with all development, testing, and build dependencies.
    ```bash
    pip install -e ".[dev,test,playwright,build]"
    ```

### Running the Application

Once installed, you can run the application using the following command:

```bash
meld-visualizer
```

The application will be available at `http://127.0.0.1:8050`.

To run in debug mode for development, use:
```bash
DEBUG=1 meld-visualizer
```

## Architecture

The MELD Visualizer is built on a modular, MVC-like architecture using Python, Dash, and Plotly.

-   **Frontend (View):** The UI is defined using Dash and Dash Bootstrap Components in `src/meld_visualizer/core/layout.py`.
-   **Backend (Controller):** Application logic is handled by callbacks located in the `src/meld_visualizer/callbacks/` directory.
-   **Data Processing (Model):** The core data processing logic for parsing files, calculating volumes, and generating meshes resides in `src/meld_visualizer/core/`.
-   **Services:** Shared services for caching, data management, and file handling are located in `src/meld_visualizer/services/`.

For a more detailed explanation and diagrams, please see the [Architecture Documentation](docs/architecture/architecture.md).

## Development

### Running Tests

The project uses `pytest` for testing. To run the full test suite:

```bash
pytest
```

You can also run specific types of tests using markers (e.g., `pytest -m unit`).

### Code Quality

This project maintains enterprise-grade code quality with comprehensive tooling and automated validation:

**Development Tools (Phase 1 Complete):**
-   **Type Safety:** `mypy` - 100% compliance on core modules
-   **Code Formatting:** `black` - Consistent 100-character line formatting
-   **Import Organization:** `isort` - PEP8 compliant import ordering
-   **Linting:** `flake8` - Style and complexity validation
-   **Pre-commit Hooks:** Automated quality assurance on git commits

**Quality Commands:**
```bash
# Format code (applied automatically via pre-commit)
black src/ tests/

# Organize imports (applied automatically via pre-commit)
isort src/ tests/

# Check linting
flake8 src/ tests/

# Type checking
mypy src/

# Run all pre-commit hooks manually
pre-commit run --all-files
```

**Quality Metrics:**
- Core modules: 100% type annotated and mypy compliant
- Security tests: 98.8% coverage (47/47 tests passing)
- Volume mesh: 94.47% coverage (47 tests)
- Error handling: 95%+ coverage (35 tests)

## Documentation

Comprehensive project documentation is now organized into the following sections:

-   **[User Guide](docs/user_guide/index.md):** A comprehensive guide for end-users, covering features, installation, running, UI usage, and interactive tools.
-   **[Developer Guide](docs/developer_guide/index.md):** A comprehensive guide for contributors, covering architecture, development setup, testing, code quality, building, and detailed technical explanations.
-   **[API Reference](docs/api_reference/index.md):** Documentation for the application's API.
-   **[Internal Documentation](docs/internal/):** Specific guidance for AI agents, quick project context, and project TODOs.

## Contributing

Contributions are welcome! Please refer to the `PR_TEMPLATE.md` for guidelines on creating pull requests.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
