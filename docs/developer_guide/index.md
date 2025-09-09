# MELD Visualizer Developer Guide

This guide provides comprehensive information for developers contributing to the MELD Visualizer project.

## 1. Getting Started

### Prerequisites

*   Python 3.8+
*   Git

### Installation for Development

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

### Running the Application in Development Mode

Once installed, you can run the application using the following command:

```bash
meld-visualizer
```

The application will be available at `http://127.0.0.1:8050`.

To run in debug mode for development, use:
```bash
DEBUG=1 meld-visualizer
```

You can also run it as a Python module:
```bash
python -m src.meld_visualizer.app
```

## 2. Project Architecture

The MELD Visualizer is built on a modular, MVC-like architecture using Python, Dash, and Plotly.

### Core Modules

*   **`src/meld_visualizer/app.py`**: Main entry point. Creates Dash app, loads layout/callbacks, starts server.
*   **`src/meld_visualizer/core/layout.py`**: UI components and structure (View layer).
*   **`src/meld_visualizer/callbacks/`**: Modular callback system (Controller layer).
*   **`src/meld_visualizer/core/data_processing.py`**: Data parsing, mesh generation, G-code processing (Model layer).
*   **`src/meld_visualizer/services/`**: Business logic layer.
*   **`src/meld_visualizer/config.py`**: Configuration loading, theme management, constants.
*   **`src/meld_visualizer/utils/`**: Utility modules.

For a more detailed explanation and diagrams, please see the [Architecture Documentation](architecture/architecture.md).

## 3. Development Workflow

### Running Tests

The project uses `pytest` for testing. To run the full test suite:

```bash
pytest
```

You can also run specific types of tests using markers (e.g., `pytest -m unit`).

*   **Run all tests:**
    ```bash
    pytest
    ```
*   **Run with coverage reporting:**
    ```bash
    pytest --cov=src/meld_visualizer --cov-report=html
    ```
*   **Run specific test categories:**
    ```bash
    pytest -m "unit"
    pytest -m "not e2e"
    ```

### Code Quality

This project uses `black` for code formatting, `ruff` for linting, and `mypy` for type checking.

*   **Format code:**
    ```bash
    black src/ tests/
    ```
*   **Lint code:**
    ```bash
    ruff check src/ tests/
    ```
*   **Type check:**
    ```bash
    mypy src/
    ```

### Building and Packaging

*   **Python Package Build:**
    ```bash
    # Build wheel and source distribution
    python -m build
    ```
*   **Executable Build:**
    ```bash
    # Build the executable using PyInstaller
    pyinstaller MELD-Visualizer.spec
    ```

## 4. Technical Decisions

This section logs key technical decisions made throughout the MELD Visualizer project.

### UI/UX and Frontend

*   **Enhanced Desktop UI**: Implemented a desktop-first responsive design strategy targeting resolutions from 1024x768 to 2560x1440+.
*   **Client-Side Management**: Created a JavaScript `EnhancedUIManager` class to manage complex UI interactions, such as toast notifications and tab scrolling, on the client side.
*   **Theming**: Adopted CSS custom properties (variables) for theming to ensure consistency with the Bootstrap theme and allow for dynamic theme switching.
*   **Accessibility**: Committed to WCAG 2.1 compliance, implementing features like focus management, ARIA labels, and keyboard navigation.
*   **Z-Axis Scaling**: The 3D plot Z-axis scaling is a direct, user-configurable "stretch factor" (e.g., 2 = 2x taller Z-axis) for intuitive control.

### Backend and Architecture

*   **MVC-like Architecture**: Organized the application into a Model-View-Controller-like structure to separate concerns:
    *   **View**: `layout.py`
    *   **Controller**: `callbacks/` modules
    *   **Model**: `data_processing.py` and `services/` modules
*   **G-Code Parser**: Implemented a G-code parser to produce a DataFrame compatible with existing mesh/toolpath generation logic, maximizing code reuse.
*   **Default G-Code Coloring**: G-code mesh is colored by Z-position as a sensible default, since process data is unavailable in the source file.
*   **Layout Flexibility**: The application supports both `get_layout(app)` and `create_layout()` functions in the layout module for flexibility.
*   **Local Server**: The application binds to `127.0.0.1` by default for security.

### Testing and Dependencies

*   **Dependency Management**: Split dependencies into production and test environments, managed via `pyproject.toml`.
*   **Test Configuration**: A repository-controlled test switch with an environment variable override is used for test execution.
*   **Idempotent Setup**: The setup process is idempotent, and Chrome is optional (only required for E2E tests).
*   **E2E Assertions**: End-to-end tests assert the application title, the presence of the upload control, and the labels of all tabs.

## 5. Volume Calculation System

The MELD Visualizer volume calculation system provides accurate 3D visualization of extruded material volume based on process parameters. This section explains the physics, implementation, and calibration of the volume calculation system.

### Overview

Successfully refactored the MELD Visualizer volume calculation system to be more modular, maintainable, and easier to tune for matching physical print results.

### Physical Principles

The fundamental principle is the conservation of mass:

`Volume_in = Volume_out`

`Feed_velocity × Feedstock_area = Path_velocity × Bead_area`

Therefore, the bead area can be calculated as:

`Bead_area = (Feed_velocity × Feedstock_area) / Path_velocity`

### Module Structure

The volume calculation system is organized into the following modules:

*   **`src/meld_visualizer/core/volume_calculations.py`:** Handles the core physics calculations, including bead area and thickness.
*   **`src/meld_visualizer/core/volume_mesh.py`:** Generates the 3D mesh for visualization based on the calculated volumes.
*   **`src/meld_visualizer/services/data_service.py`:** Integrates the volume calculation components with the main application, providing caching and data management.

### Calibration

The system can be calibrated to match the physical output of the MELD machine. The calibration process involves:

1.  **Printing a test part:** A test part with known parameters is printed.
2.  **Measuring the actual volume:** The actual volume of the printed part is measured.
3.  **Calculating the theoretical volume:** The theoretical volume is calculated based on the process parameters.
4.  **Determining the correction factor:** The correction factor is calculated by dividing the actual volume by the theoretical volume.
5.  **Applying the correction factor:** The correction factor is applied to all subsequent volume calculations.

### Configuration

The volume calculation system is configured through the `config/volume_calibration.json` file. This file allows you to specify the feedstock parameters, bead geometry, and calibration settings.

### Benefits of the New Architecture

*   **Separation of Concerns**: Physics, mesh generation, and visualization are now separate.
*   **Easier Testing**: Each component can be tested independently.
*   **Better Documentation**: Clear interfaces and comprehensive docs.
*   **Type Hints**: Added throughout for better IDE support.
*   **Calibration Factors**: Easy adjustment via `correction_factor` and `area_offset`.
*   **Configuration File**: Parameters persist between sessions.
*   **Validation Workflow**: Clear process for comparing with physical prints.
*   **Statistics**: Built-in analysis of volume distribution.

### Key Improvements

1.  **Correct Feedstock Area**: Fixed calculation to use actual square rod area (161.3 mm²).
2.  **Modular Design**: Each component has a single responsibility.
3.  **Calibration Support**: Built-in from the ground up.
4.  **Documentation**: Comprehensive docs for users and developers.
5.  **Backward Compatibility**: Existing code continues to work.

## 6. Contribution Guidelines

Contributions are welcome! Please refer to the `PR_TEMPLATE.md` for guidelines on creating pull requests.

### Core Features and Enhancements (Roadmap)

*   **Data Pipeline and Caching:** The application uses a data pipeline that caches CSV data to Parquet for faster loading times.
*   **Configuration and Column Mapping:** The application supports configuration validation and allows users to map CSV columns to the application's data model.
*   **Performance and Level of Detail (LOD):** The application includes performance optimizations such as data decimation and a payload cap to ensure smooth interaction with large datasets.
*   **Voxelization and Isosurface Mode:** The application can visualize large datasets as voxelized volumes and isosurfaces.
*   **Region of Interest (ROI) Selection and Cross-filtering:** Users can select a region of interest in the 3D view and filter the data in other plots accordingly.
*   **Error Handling and User Feedback:** The application includes an error panel and provides users with feedback during long-running operations.
*   **Session Management and Export:** Users can save and load their sessions and export visualizations to images.
*   **Enhanced Desktop UI:** The application features an enhanced desktop UI with improved navigation, control panel organization, and user feedback.

### Development Roadmap

1.  **Infrastructure and CI/CD:** Set up the project structure, dependencies, and CI/CD pipeline.
2.  **Data Pipeline:** Implement the data pipeline with CSV to Parquet caching.
3.  **Configuration and UI:** Develop the configuration validation and column mapping UI.
4.  **Performance Optimizations:** Implement performance optimizations suchs as LOD and data decimation.
5.  **Advanced Visualization:** Add support for voxelization and isosurface rendering.
6.  **Interactivity:** Implement ROI selection and cross-filtering.
7.  **UX and Error Handling:** Improve the user experience with better error handling and feedback.
8.  **Session Management:** Add support for saving and loading sessions.
9.  **Testing:** Enhance the test suite with snapshot and property-based testing.
10. **Packaging and Release:** Package the application for Windows and set up a release pipeline.
