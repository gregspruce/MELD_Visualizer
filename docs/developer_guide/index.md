# MELD Visualizer Developer Guide

## Introduction

This guide provides a comprehensive overview of the MELD Visualizer application for developers. It covers the project's architecture, components, development workflow, and more.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/gregspruce/MELD_Visualizer.git
cd MELD_Visualizer

# Install in development mode with all dependencies
pip install -e ".[dev,test,playwright,build]"
```

## Architecture

The MELD Visualizer is a Dash web application with a modular, MVC-like architecture.

-   **Frontend (View):** The frontend is built with Dash and Dash Bootstrap Components. The UI is defined in the `src/meld_visualizer/core/layout.py` module.
-   **Backend (Controller):** The backend is built with Python and Flask. The application's logic is handled by callbacks in the `src/meld_visualizer/callbacks/` directory.
-   **Data Processing (Model):** The data processing layer is responsible for parsing and processing data from CSV and G-code files. The core logic is in `src/meld_visualizer/core/data_processing.py`.

For more details and diagrams, see the main [Architecture Document](../architecture/architecture.md).

## Components

-   **Main Application (`app.py`):** The entry point of the application.
-   **Layout (`layout.py`):** Defines the structure of the user interface.
-   **Callbacks (`callbacks/`):** Contains the application's controller logic.
-   **Data Processing (`data_processing.py`):** Handles the parsing and processing of data.
-   **Services (`services/`):** Provides services for caching, data management, and file handling.
-   **Configuration (`config.py`):** Manages the application's configuration.

## Development Workflow

### Running the Application

```bash
# Run the application in development mode
meld-visualizer

# Run with debug mode enabled
DEBUG=1 meld-visualizer
```

### Testing

```bash
# Run all tests
pytest

# Run unit tests only
pytest -m "unit"
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type check code
mypy src/
```

## Enhanced UI

The MELD Visualizer features an enhanced desktop UI with improved navigation, control panel organization, and user feedback.

### Enhanced UI Architecture

The Enhanced UI System is a layer on top of the existing Dash framework that provides a desktop-optimized user experience. It introduces a more organized and maintainable approach to UI development.

The architecture is composed of three main layers:

1.  **Python Layer (Server-Side):** This layer is responsible for creating the UI components and handling the application’s logic. It uses a factory pattern to create consistent UI elements.
    -   **`EnhancedUIComponents` Factory:** A central factory in `src/meld_visualizer/core/enhanced_ui.py` for creating enhanced UI components like tabs, control panels, and toast notifications.
    -   **Modular Callbacks:** Callbacks are organized into modules based on their functionality in `src/meld_visualizer/callbacks/`.

2.  **JavaScript Layer (Client-Side):** This layer manages the UI’s client-side interactions, such as animations, event handling, and communication with the Dash server.
    -   **`EnhancedUIManager` Class:** A client-side class in `src/meld_visualizer/static/js/enhanced-ui.js` that manages all enhanced UI functionality.

3.  **CSS Layer (Styling):** This layer provides the styling for the enhanced UI components, with a responsive design that adapts to different desktop screen sizes.
    -   **Responsive Design:** The CSS in `src/meld_visualizer/static/css/enhanced-desktop-ui.css` is designed with a desktop-first approach.
    -   **CSS Custom Properties:** The styling leverages CSS custom properties to ensure consistency with the selected Bootstrap theme.

### Working with the Enhanced UI

-   **Use the Factory:** When creating enhanced UI components, always use the `EnhancedUIComponents` factory to ensure consistency.
-   **Separate Concerns:** Keep the UI layout, component creation, and callback logic in their respective modules.
-   **Explore the Code:** The best way to understand the enhanced UI is to explore the code in the following locations:
    -   `src/meld_visualizer/core/layout.py`: See how the enhanced UI components are used to build the application's layout.
    -   `src/meld_visualizer/callbacks/`: Review the callbacks to understand how the enhanced UI components are controlled.
    -   `src/meld_visualizer/static/css/enhanced-desktop-ui.css`: Examine the CSS to understand how the enhanced UI is styled.
    -   `src/meld_visualizer/static/js/enhanced-ui.js`: Read the JavaScript to understand the client-side interactions.

## Project Management

-   **Roadmap:** The project's development roadmap is outlined in the `docs/PR.md` file.
-   **Decisions:** Key technical decisions are logged in the `docs/DECISIONS.md` file.
-   **TODO:** The project's TODO list is in the `docs/TODO.md` file.