# MELD Visualizer - Comprehensive Project Context

## 1. Project Overview

### Goals and Objectives
MELD Visualizer is a **Dash web application** for visualizing 3D process data from MELD manufacturing, featuring:
- CSV data upload with automatic unit conversion (inches → mm)
- G-code visualization for `.nc` files
- Interactive 3D plots (scatter, toolpath, volume meshes)
- 20+ Bootstrap themes with matching Plotly templates
- Configurable UI with settings persistence

### Key Architectural Decisions
- **Professional Python Package Structure**: `src/meld_visualizer/` layout
- **MVC-like Architecture**: Modular separation of concerns
- **Visualization Stack**: Dash/Plotly for interactive web-based 3D visualization
- **Theme System**: Bootstrap themes with dynamically matched Plotly templates
- **Modular Callbacks**: Split into focused modules (data, filter, plot, settings, theme)

### Technology Stack
**Core Dependencies:**
- `dash >= 2.14.0` - Web framework
- `dash-bootstrap-components` - UI components and themes
- `plotly` - 3D visualization engine
- `pandas` - Data manipulation
- `numpy` - Numerical operations
- `scipy` - Scientific computing

**Development/Testing:**
- `pytest` - Testing framework
- `selenium` - E2E browser automation
- `pyinstaller` - Executable building

### Team Conventions and Patterns
- **Modular Callback System**: Organized by functionality
- **Pattern Matching IDs**: `{'type': 'component-type', 'index': 'identifier'}`
- **Error Handling**: Returns tuples `(data, error_message, conversion_flag)`
- **Plot Consistency**: All plots use `PLOTLY_TEMPLATE` from config
- **Hot-reloading**: Works for `.py` files (config.json requires restart)

## 2. Current State

### Recently Implemented Features (Latest Fixes)

#### CRITICAL FIX #1: Volume Calculation Correction
- **Issue**: Incorrect circular wire assumption (126.7mm²)
- **Solution**: Corrected to square rod geometry (161.3mm²)
- **Impact**: 27% more accurate volume representations
- **Details**: Changed from `π × (d/2)²` to `w²` calculation

#### CRITICAL FIX #2: Launch/Import Resolution
- **Issue**: "attempted relative import with no known parent package"
- **Solution**: Added `__main__.py` for proper module execution
- **Files Fixed**:
  - `src/meld_visualizer/__main__.py` (created)
  - `src/meld_visualizer/callbacks/filter_callbacks.py` (import corrected)
  - Import changed from `from security_utils` to `from ..utils.security_utils`

#### CRITICAL FIX #3: Repository URL Corrections
- **Issue**: Hallucinated GitHub URLs in documentation
- **Solution**: Corrected all references to actual repository
- **Correct URL**: https://github.com/gregspruce/MELD_Visualizer

### Work Status
- **Current Branch**: main
- **Status**: All major fixes merged and pushed
- **Application State**: Fully functional with corrected calculations

### Known Issues and Technical Debt
- Hot-reloading doesn't work for `config.json` changes
- Theme changes require full app restart
- Legacy configuration compatibility needs improvement
- Edge case error messages could be more descriptive

### Performance Baselines
- Volume mesh generation handles typical MELD datasets efficiently
- Caching system implemented for repeated operations
- Memory usage optimized for standard manufacturing data sizes

## 3. Design Decisions

### Architectural Choices
**MVC-like Pattern Implementation:**
- **View**: `layout.py` - UI components and structure
- **Controller**: `callbacks/` directory - Interactive logic
- **Model**: `data_processing.py` - Data operations
- **Configuration**: `config.py` - Settings management

### API Design Patterns
- **Dash Callbacks**: `@callback` decorator with Input/Output/State
- **Dynamic Components**: Pattern matching for flexible UI updates
- **Data Pipeline**: Upload → Parse → Validate → Visualize
- **Component Factories**: Reusable UI element generators

### Data Architecture
- **No Database**: File-based processing (CSV/G-code)
- **In-Memory Processing**: Pandas DataFrames for data manipulation
- **Caching Strategy**: Optional caching for expensive operations
- **State Management**: Dash Store components for client-side state

### Security Implementations
- **InputValidator**: Sanitizes all user inputs
- **File Validation**: Checks file types and sizes before processing
- **Error Isolation**: Security-focused error handling prevents information leakage
- **Safe Defaults**: Conservative configuration defaults

## 4. Code Patterns

### Coding Conventions
- **Package Structure**: Professional `src/` layout
- **Type Hints**: Comprehensive type annotations
- **Docstrings**: Python conventions with parameter descriptions
- **Import Organization**: Standard library → third-party → local

### Common Patterns and Abstractions
```python
# Data Processing Pipeline
def process_data(file):
    data = upload(file)
    parsed = parse(data)
    validated = validate(parsed)
    return visualize(validated)

# Component Pattern
def create_component(id, config):
    return dbc.Component(
        id={'type': 'component-type', 'index': id},
        **config
    )

# Error Handling Pattern
def operation():
    try:
        result = perform_operation()
        return result, None, True
    except Exception as e:
        return None, str(e), False
```

### Testing Strategies
- **Unit Tests**: `tests/test_*.py` - Isolated function testing
- **Integration Tests**: Complete workflow testing
- **E2E Tests**: `tests/e2e/test_*.py` - Browser automation
- **Test Markers**: `@pytest.mark.unit`, `@pytest.mark.e2e`

### Error Handling Approaches
- **Tuple Returns**: `(data, error_message, conversion_flag)`
- **Graceful Fallbacks**: Default values when operations fail
- **Comprehensive Logging**: Detailed error tracking
- **User-Friendly Messages**: Clear error communication

## 5. Critical Constants and Configuration

### Key Constants
```python
FEEDSTOCK_DIMENSION_INCHES = 0.5  # Square rod dimension
FEEDSTOCK_AREA_MM2 = 161.29  # Corrected square rod area (was 126.7)
INCHES_TO_MM = 25.4
DEFAULT_Z_STRETCH = 10  # Z-axis scaling factor
```

### Repository Information
- **GitHub**: https://github.com/gregspruce/MELD_Visualizer
- **Main Entry**: `src/meld_visualizer/app.py`
- **Module Entry**: `src/meld_visualizer/__main__.py`
- **Configuration**: `config.json`

## 6. CRITICAL LAUNCH INSTRUCTIONS

### CORRECT Launch Methods
```bash
# Method 1: Module execution (RECOMMENDED)
export PYTHONPATH=C:\VSCode\MELD\MELD_Visualizer\src
python -m meld_visualizer

# Method 2: After pip install -e
meld-visualizer

# Method 3: Direct app.py (ONLY from src directory)
cd C:\VSCode\MELD\MELD_Visualizer\src
python meld_visualizer/app.py
```

### INCORRECT Launch Methods (Will Fail)
```bash
# NEVER do this - causes relative import errors
python src/meld_visualizer/app.py  # From project root
```

## 7. Testing Commands

```bash
# Run all tests
pytest

# Unit tests only
pytest -m "not e2e"

# E2E tests only
pytest -m "e2e"

# Using test runner
bash run_tests.sh
TEST_SUITE=both bash run_tests.sh
```

## 8. Agent Coordination History

### Successful Agent Patterns
- **Multi-Agent Debugging**: Used specialized agents for import resolution
- **Task Tool Usage**: Effective for complex multi-step operations
- **Context Preservation**: Maintained state across agent transitions

### Critical Discoveries
1. **Volume Calculation Error**: 21.5% underestimation from wire vs rod assumption
2. **Import Context Issue**: Relative imports require proper module execution
3. **Repository URL Errors**: Systematic correction of hallucinated URLs

### Cross-Agent Dependencies
- Repository restructuring required coordination for:
  - Import path updates
  - Test modifications
  - Documentation synchronization

## 9. Future Roadmap

### Planned Features
- Enhanced G-code parsing capabilities
- Additional visualization options
- Improved theme hot-reloading
- Real-time data streaming support

### Identified Improvements
- Configuration change hot-reloading
- Enhanced caching strategies
- Memory optimization for large datasets
- Better error message specificity

### Technical Debt Items
- Legacy configuration migration
- Theme restart requirement
- Edge case handling improvements
- Performance profiling and optimization

## 10. Quick Reference

### File Structure
```
MELD_Visualizer/
├── src/
│   └── meld_visualizer/
│       ├── __init__.py
│       ├── __main__.py        # Module entry point
│       ├── app.py             # Main application
│       ├── layout.py          # UI components
│       ├── config.py          # Configuration
│       ├── data_processing.py # Data operations
│       ├── callbacks/         # Modular callbacks
│       └── utils/             # Utilities
├── tests/                     # Test suite
├── config.json               # User configuration
└── requirements.txt          # Dependencies
```

### Common Operations
```python
# Start development server
python -m meld_visualizer

# Run tests
pytest -v

# Build executable
pyinstaller VolumetricPlotter.spec

# Install development
pip install -e .
```

## Status Summary
✅ **Volume calculation corrected** (27% accuracy improvement)
✅ **Import errors resolved** (proper module structure)
✅ **Launch procedure documented** (clear instructions)
✅ **Repository URLs fixed** (correct GitHub references)
✅ **Application fully functional** (all blockers resolved)

---
*Last Updated: 2025-08-18*
*Branch: main (clean, all fixes merged)*
*Version: Post-critical-fixes release*