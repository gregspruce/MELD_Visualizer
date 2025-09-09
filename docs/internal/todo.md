# TODO

## High Priority

- **Testing:**
    - Add per-tab panel assertions using stable IDs.
    - Add more comprehensive tests for the enhanced UI components.
    - Add snapshot testing for the 3D visualizations.
- **Offline Support:**
    - Add local assets/bootstrap.min.css for offline use.

## Medium Priority

- **Features:**
    - Persist the Z-axis stretch factor for each tab in the user session.
    - Add color-by options to the G-code mesh visualization tab (e.g., color by simulated time or segment speed).
    - Add a side-by-side comparison view for G-code simulation vs. actual CSV data.
- **Performance:**
    - Investigate using `pytest-xdist` for parallel test execution.

## Low Priority

- **Configuration:**
    - Factor the `APP_TITLE` into the configuration file.
