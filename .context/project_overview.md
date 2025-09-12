# MELD Visualizer - Project Overview

## Project Goals and Objectives
MELD Visualizer is a professional Dash web application for visualizing 3D process data from MELD manufacturing. The application provides:
- CSV data upload with automatic unit conversion (inches → millimeters)
- G-code visualization for toolpath simulation
- Interactive 3D plots with Z-axis scaling
- 20+ Bootstrap themes with matching Plotly templates
- Configurable UI with hot-reload capabilities
- Real-time configuration updates without app restart

## Key Architectural Decisions
- **Package Structure**: Professional Python package layout with `src/meld_visualizer/`
- **MVC-like Architecture**: Separation of concerns with modular components
  - View: `layout.py` - UI components and structure
  - Controller: `callbacks/` directory with modular callback modules
  - Model: `data_processing.py` - Data parsing and mesh generation
- **Hot-Reload System**: Dynamic theme and configuration updates without restart
- **Bootstrap Integration**: Responsive UI with professional themes
- **Plotly Templates**: Consistent theming across all visualizations

## Technology Stack
### Core Dependencies
- **Dash** >=2.14.0 - Web framework for interactive applications
- **dash-bootstrap-components** - Bootstrap 5 integration
- **plotly** - 3D visualization library
- **pandas** - Data manipulation
- **numpy** - Numerical computations
- **scipy** - Scientific computing

### Development Dependencies
- **pytest** - Testing framework
- **selenium** - E2E browser automation
- **pyinstaller** - Executable building

## Team Conventions and Patterns
- **Modular Callback System**: Separate callback modules for different features
- **Pattern Matching IDs**: `{'type': 'component-type', 'index': 'identifier'}`
- **Error Handling**: Tuple returns `(data, error_message, conversion_flag)`
- **Configuration Management**: Centralized through `config.py`
- **Hot-Reloading**: Automatic updates for themes and configuration
- **Type Hints**: Comprehensive type annotations throughout
- **Docstrings**: Python convention documentation

## Repository Information
- **GitHub**: https://github.com/gregspruce/MELD_Visualizer
- **Main Branch**: main
- **License**: MIT
- **Python Version**: 3.8+
