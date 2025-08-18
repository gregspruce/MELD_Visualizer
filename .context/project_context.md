# MELD Visualizer - Project Context

## 1. Project Overview

### Goals and Objectives
MELD Visualizer is a **Dash web application** for visualizing 3D process data from MELD manufacturing, providing:
- CSV data upload with automatic unit conversion (inches → mm)
- G-code visualization for `.nc` files with toolpath simulation
- Interactive 3D plots (scatter, toolpath, volume meshes) with Z-axis scaling
- 20+ Bootstrap themes with matching Plotly templates
- Configurable UI with settings saved in `config.json`

### Key Architectural Decisions
- **Repository Structure**: Professional Python package layout with `src/meld_visualizer/`
- **Architecture Pattern**: MVC-like architecture with modular callbacks
- **Visualization Stack**: Dash/Plotly for interactive 3D visualizations
- **Theme System**: Bootstrap themes with automatic Plotly template matching
- **Data Processing**: In-memory pandas DataFrames with optional caching

### Technology Stack
**Core Dependencies:**
- `dash>=2.14.0` - Web framework
- `dash-bootstrap-components` - UI components and themes
- `plotly` - 3D visualization library
- `pandas` - Data processing
- `numpy` - Numerical computations
- `scipy` - Scientific computing

**Development Dependencies:**
- `pytest` - Testing framework
- `selenium` - Browser automation for E2E tests
- `pyinstaller` - Executable building

### Team Conventions
- **Callback Pattern**: Modular callback system with pattern matching IDs
- **Error Handling**: Tuple returns `(data, error_message, conversion_flag)`
- **Plot Styling**: All plots use `PLOTLY_TEMPLATE` from config
- **Development**: Hot-reloading for `.py` files (config.json requires restart)

## 2. Current State

### Recently Implemented Features
- **CRITICAL FIX**: Corrected 3D volume mesh calculation
  - Fixed: Incorrect circular wire assumption (126.7mm²)
  - Corrected: Square rod geometry (161.3mm²)
  - Impact: 27% more accurate volume representations
- **Import Error Fix**: Resolved startup blocking import issues
- **Repository URL Corrections**: Fixed all GitHub URLs from hallucinated references to actual `gregspruce/MELD_Visualizer`
- **Professional Package Structure**: Migrated from flat layout to `src/` layout

### Work Status
- **Current Branch**: main (clean, all fixes merged)
- **Application Status**: Fully functional with corrected calculations
- **Repository**: https://github.com/gregspruce/MELD_Visualizer

### Known Issues
- Hot-reloading doesn't work for `config.json` changes
- Theme changes require full app restart
- Legacy configuration compatibility needs attention

### Performance Baselines
- Volume mesh generation efficiently handles typical MELD datasets
- Caching system implemented for repeated operations
- Memory-efficient processing for large CSV files

## 3. Design Decisions

### Architectural Choices
**MVC-like Separation:**
- **View**: `layout.py` - UI components and structure
- **Controller**: `callbacks/` directory - Interactive logic and event handlers
- **Model**: `data_processing.py` - Data parsing, mesh generation, G-code processing
- **Config**: `config.py` - Configuration loading, theme management

### API Design Patterns
- **Dash Callbacks**: `@callback` decorator with Input/Output/State
- **Pattern Matching**: `{'type': 'component-type', 'index': 'identifier'}`
- **Dynamic Components**: Support for runtime UI generation

### Data Processing
- **No Database**: File-based CSV/G-code processing
- **In-Memory**: Pandas DataFrames for data manipulation
- **Caching**: Optional caching for expensive operations

### Security Implementations
- `InputValidator` for sanitizing user inputs
- File validation for uploads
- Security-focused error handling
- Safe path handling for file operations

## 4. Code Patterns

### Coding Conventions
- **Package Structure**: `src/meld_visualizer/` with proper `__init__.py` files
- **Type Hints**: Comprehensive type annotations
- **Docstrings**: Python convention docstrings for all public functions
- **Naming**: Snake_case for functions/variables, PascalCase for classes

### Common Patterns
**Data Processing Pipeline:**
1. Upload → Validate file type/size
2. Parse → Extract data with error handling
3. Process → Apply transformations and calculations
4. Visualize → Generate interactive plots

**Component Pattern:**
- Reusable UI components in `layout.py`
- Callback registration in modular files
- State management through Dash stores

### Testing Strategies
- **Unit Tests**: `tests/test_*.py` - Isolated function testing
- **Integration Tests**: Complete workflow testing
- **E2E Tests**: `tests/e2e/test_*.py` - Browser automation with Selenium
- **Test Markers**: `pytest -m "unit"`, `pytest -m "e2e"`

### Error Handling
- Graceful fallbacks for missing data
- Comprehensive logging for debugging
- User-friendly error messages
- Validation at multiple levels

## 5. Agent Coordination History

### Agent Utilization
- **Repository Restructuring**: Multiple subagents for package migration
- **Error Detective**: Identified and fixed import issues
- **Code Reviewer**: Quality checks and best practices
- **Database Optimizer**: Performance improvements for data processing

### Successful Combinations
- Task tool with specialized agents for complex operations
- Parallel agent execution for independent tasks
- Sequential coordination for dependent operations

### Critical Discoveries
- **Volume Calculation Error**: 21.5% underestimation from wire diameter assumption
- **Import Path Issues**: Incorrect relative imports blocking startup
- **GitHub URL Errors**: Systematic correction of hallucinated repository references

### Cross-Agent Dependencies
- Repository restructuring required coordinated updates to:
  - Import statements across all modules
  - Test configurations
  - Documentation references
  - Build specifications

## 6. Future Roadmap

### Planned Features
- Enhanced G-code parsing for additional commands
- Real-time data streaming support
- Additional 3D visualization options
- Improved theme management system
- Export functionality for plots and data

### Identified Improvements
- Better hot-reloading for all configuration changes
- Enhanced caching strategies with TTL
- Memory optimization for very large datasets
- Progressive loading for better UX
- WebSocket support for live updates

### Technical Debt
- Legacy configuration migration path
- Improved error messages for edge cases
- Comprehensive API documentation
- Performance profiling and optimization
- Test coverage expansion

### Performance Opportunities
- Volume mesh generation optimization using NumPy vectorization
- Lazy loading for large G-code files
- Plot decimation for dense datasets
- Worker threads for CPU-intensive operations
- Client-side caching for static assets

## Key Constants and Configuration

### Feedstock Geometry (CRITICAL)
```python
# Square rod dimensions (NOT circular wire)
FEEDSTOCK_DIMENSION_INCHES = 0.5  # Square rod side length
FEEDSTOCK_DIMENSION_MM = 12.7     # Square rod side in mm
FEEDSTOCK_AREA_MM2 = 161.29       # Square cross-sectional area
```

### File Paths
- **Main Entry**: `src/meld_visualizer/app.py`
- **Configuration**: `config.json`
- **Sample Data**: `CSV/` directory
- **Tests**: `tests/` with unit and e2e subdirectories

### Commands
```bash
# Run application
python app.py

# Testing
pytest -m "not e2e"  # Unit tests only
pytest -m "e2e"      # E2E tests only
pytest               # All tests

# Build executable
pyinstaller VolumetricPlotter.spec
```

### Environment Variables
- `DEBUG="1"` - Enable debug mode
- `TEST_SUITE` - Control test execution scope

## Recent Critical Fixes Summary

1. **Volume Calculation** (2025-08-18)
   - Problem: Used circular wire formula π × (d/2)²
   - Solution: Corrected to square rod formula w²
   - Impact: 27% accuracy improvement

2. **Import Errors** (2025-08-18)
   - Problem: Incorrect relative imports after restructuring
   - Solution: Fixed all import paths to use proper package structure
   - Files affected: Multiple callback modules

3. **Repository References** (2025-08-18)
   - Problem: Hallucinated GitHub URLs
   - Solution: Corrected all references to `gregspruce/MELD_Visualizer`
   - Files updated: Documentation and configuration

## Context Metadata
- **Last Updated**: 2025-08-18
- **Context Version**: 1.0
- **Project Phase**: Production-ready with recent critical fixes
- **Next Review**: After next major feature implementation