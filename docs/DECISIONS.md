# Technical Decisions

This document logs key technical decisions made throughout the MELD Visualizer project.

## UI/UX and Frontend

- **Enhanced Desktop UI**: Implemented a desktop-first responsive design strategy targeting resolutions from 1024x768 to 2560x1440+.
- **Client-Side Management**: Created a JavaScript `EnhancedUIManager` class to manage complex UI interactions, such as toast notifications and tab scrolling, on the client side.
- **Theming**: Adopted CSS custom properties (variables) for theming to ensure consistency with the Bootstrap theme and allow for dynamic theme switching.
- **Accessibility**: Committed to WCAG 2.1 compliance, implementing features like focus management, ARIA labels, and keyboard navigation.
- **Z-Axis Scaling**: The 3D plot Z-axis scaling is a direct, user-configurable "stretch factor" (e.g., 2 = 2x taller Z-axis) for intuitive control.

## Backend and Architecture

- **MVC-like Architecture**: Organized the application into a Model-View-Controller-like structure to separate concerns:
    - **View**: `layout.py`
    - **Controller**: `callbacks/` modules
    - **Model**: `data_processing.py` and `services/` modules
- **G-Code Parser**: Implemented a G-code parser to produce a DataFrame compatible with existing mesh/toolpath generation logic, maximizing code reuse.
- **Default G-Code Coloring**: G-code mesh is colored by Z-position as a sensible default, since process data is unavailable in the source file.
- **Layout Flexibility**: The application supports both `get_layout(app)` and `create_layout()` functions in the layout module for flexibility.
- **Local Server**: The application binds to `127.0.0.1` by default for security.

## Testing and Dependencies

- **Dependency Management**: Split dependencies into production and test environments, managed via `pyproject.toml`.
- **Test Configuration**: A repository-controlled test switch with an environment variable override is used for test execution.
- **Idempotent Setup**: The setup process is idempotent, and Chrome is optional (only required for E2E tests).
- **E2E Assertions**: End-to-end tests assert the application title, the presence of the upload control, and the labels of all tabs.
