# MELD Visualizer - Comprehensive Onboarding Documentation

**Generated:** August 19, 2025  
**Claude Code Onboarding Session ID:** onboard-2025-08-19  
**Repository:** https://github.com/gregspruce/MELD_Visualizer  

## Executive Summary

MELD Visualizer is a sophisticated Python-based web application designed for visualizing and analyzing Manufacturing using Extreme Layer Deposition (MELD) process data. This is a production-quality application with enterprise-grade architecture, comprehensive testing, and advanced 3D visualization capabilities for additive manufacturing workflows.

### Key Value Proposition
- **Precision Manufacturing Visualization**: 3D toolpath analysis for MELD additive manufacturing
- **Accurate Volume Calculations**: Recently improved by 27% through corrected feedstock geometry
- **Interactive Web Interface**: Professional Dash/Plotly-based UI with 20+ theme options
- **Data Processing Excellence**: Handles CSV process data and G-code files with unit conversion

## Project Architecture Overview

### Technology Stack
```
Frontend: Dash + Plotly + Bootstrap Components
Backend: Python 3.8+ with Pandas/NumPy data processing
Testing: Pytest with Unit/Integration/E2E coverage
Packaging: Modern pyproject.toml with pip installation
Security: Input validation, file size limits, path traversal protection
```

### Application Structure
```
MELD_Visualizer/
├── src/meld_visualizer/          # Main application package
│   ├── app.py                    # Entry point and Dash app creation
│   ├── constants.py              # Manufacturing constants and thresholds
│   ├── config.py                 # Configuration and theme management
│   ├── core/                     # Core functionality
│   │   ├── layout.py            # UI components (View layer)
│   │   ├── data_processing.py   # Data operations (Model layer) 
│   │   ├── volume_calculations.py # MELD volume math
│   │   └── volume_mesh.py       # 3D mesh generation
│   ├── callbacks/               # Modular controller system
│   │   ├── data_callbacks.py    # File upload and processing
│   │   ├── graph_callbacks.py   # 3D plot interactions
│   │   ├── config_callbacks.py  # Settings management
│   │   ├── visualization_callbacks.py # Plot generation
│   │   └── filter_callbacks.py  # Data filtering
│   ├── services/                # Business logic layer
│   │   ├── cache_service.py     # Performance caching
│   │   ├── data_service.py      # Data processing services
│   │   └── file_service.py      # File handling
│   └── utils/                   # Utility modules
│       ├── hot_reload.py        # Configuration hot-reload
│       ├── logging_config.py    # Application logging
│       └── security_utils.py    # Security validation
├── tests/                       # Comprehensive test suite
├── config/                      # User configuration files
├── data/                        # Sample CSV and G-code files
├── docs/                        # Extensive documentation
└── scripts/                     # Build and utility scripts
```

## Recent Development Context

### Critical Recent Fixes (August 2025)

#### 1. Volume Calculation Accuracy Improvement (27% more accurate)
- **Issue**: Application assumed circular wire feedstock (126.7mm²)
- **Reality**: MELD uses 0.5" × 0.5" square rod feedstock (161.3mm²)
- **Impact**: Volume representations now match physical manufacturing reality
- **Files Changed**: `constants.py:25-28`, `volume_calculations.py`

#### 2. Bead Overlap Calibration
- **Problem**: Visualization showed gaps between toolpath tracks
- **Physical Reality**: Actual prints show overlapping, merged beads
- **Solution**: Implemented width multiplier (1.654) for realistic bead spreading
- **Result**: 20% bead overlap matching physical prints

#### 3. Module Import Resolution
- **Issue**: "attempted relative import with no known parent package"
- **Solution**: Added `__main__.py` for proper module execution
- **Launch Method**: `python -m meld_visualizer` (recommended)

#### 4. ✅ RESOLVED: Callback Architecture Overhaul (August 2025)
- **Problem**: 79+ console callback conflicts affecting development experience
- **Solution**: Comprehensive callback architecture improvements
  - Eliminated circular dependencies in filter callbacks
  - Unified callback registration into single flow
  - Enhanced hot-reload integration without duplicates
  - Added comprehensive error handling and logging
- **Results**: 
  - ✅ Excellent performance: 0.01s startup, <4ms responses
  - ✅ All functionality preserved (filters, themes, hot-reload)
  - ✅ Clean, maintainable callback architecture
  - 📋 79 Dash validation warnings remain (cosmetic, not functional)
- **Files Changed**: `app.py`, `callbacks/__init__.py`, `filter_callbacks.py`, `hot_reload.py`, `config_callbacks.py`

## Key Technical Constants and Configuration

### Manufacturing Constants (`constants.py`)
```python
FEEDSTOCK_DIMENSION_INCHES = 0.5      # Square rod dimension
FEEDSTOCK_AREA_MM2 = 161.29          # Corrected square geometry
INCH_TO_MM = 25.4                     # Unit conversion
BEAD_LENGTH_MM = 2.0                  # Mesh generation parameter
MAX_FILE_SIZE_MB = 10                 # Security limit
```

### Supported File Types
- **CSV Files**: Process data with position, temperature, velocity columns
- **G-code Files**: `.nc` programs for toolpath simulation
- **Unit Detection**: Automatic imperial-to-metric conversion

### Configuration System
- **File Location**: `config/config.json`
- **Hot-reload**: Themes change instantly, other config requires restart
- **Theme Options**: 20+ Bootstrap themes with matching Plotly templates
- **Security**: Whitelisted configuration keys only

## Application Features

### Core Functionality
1. **3D Visualization**: Interactive scatter plots, toolpath rendering, volume mesh generation
2. **Data Processing**: CSV parsing, G-code interpretation, unit conversion
3. **User Interface**: Professional web interface with configurable themes
4. **Volume Analysis**: Mathematically accurate MELD feedstock calculations
5. **Performance**: Multi-level caching, lazy loading, efficient data handling

### Visualization Types
- **3D Scatter Plots**: Color-coded by temperature, velocity, position
- **3D Toolpath Visualization**: Line plots showing manufacturing paths
- **3D Volume Mesh**: Realistic bead geometry with overlap modeling
- **2D Time Series**: Process monitoring over time
- **Data Tables**: Searchable, paginated data inspection

## Development Environment Setup

### Prerequisites
```bash
# Verify Python version
python --version  # Must be 3.8+

# Verify Git access
git --version
```

### Installation (Recommended Method)
```bash
# Clone repository
git clone https://github.com/gregspruce/MELD_Visualizer.git
cd MELD_Visualizer

# Install with development dependencies
pip install -e ".[dev]"

# Verify installation
python -c "import meld_visualizer; print('✓ Installation successful')"
```

### Running the Application
```bash
# Primary method (recommended)
meld-visualizer

# Alternative: module execution
python -m meld_visualizer

# Development mode with debug
DEBUG=1 meld-visualizer
```

### Application Access
- **URL**: http://127.0.0.1:8050
- **Auto-launch**: Browser opens automatically
- **Security**: Binds only to localhost (127.0.0.1)

## Testing Framework

### Test Categories
```bash
# Unit tests (fast, isolated)
pytest -m "unit" -v

# Integration tests (component interactions)
pytest -m "integration" -v  

# E2E tests (full browser automation)
pytest -m "e2e" -v

# All tests with coverage
pytest --cov=src/meld_visualizer --cov-report=html
```

### Test Structure
- **Unit Tests**: `tests/unit/` - Function-level testing
- **Integration Tests**: `tests/integration/` - Component interactions  
- **E2E Tests**: `tests/e2e/` - Selenium browser automation
- **Configuration**: `pytest.ini`, `conftest.py`

## Common Development Tasks

### Code Quality
```bash
# Format code
black src/ tests/

# Lint code  
flake8 src/ tests/

# Type checking
mypy src/
```

### Running Tests During Development
```bash
# Quick unit tests (development cycle)
pytest tests/unit/ -v

# Full test suite (before commits)
bash scripts/run_tests.sh

# E2E tests (integration verification)
TEST_SUITE=e2e bash scripts/run_tests.sh
```

### Configuration Changes
```bash
# Theme changes (instant via UI)
# 1. Navigate to Settings tab
# 2. Select new theme
# 3. Changes apply immediately

# Other configuration (requires restart)
# 1. Edit config/config.json
# 2. Restart application
```

## File Processing Workflow

### CSV File Processing
1. **Upload**: Drag-and-drop or file selection
2. **Validation**: Security checks, size limits, format verification
3. **Parsing**: Pandas-based CSV parsing with error handling
4. **Unit Detection**: Automatic imperial-to-metric conversion
5. **Processing**: Data cleanup, column mapping, time handling
6. **Visualization**: Interactive 3D plots with customizable parameters

### G-code Processing  
1. **Upload**: Dedicated G-code upload area
2. **Parsing**: G-code command interpretation (G0, G1, M34, M35)
3. **Simulation**: Toolpath generation with feedstock extrusion
4. **Volume Calculation**: Accurate bead geometry with width multipliers
5. **Visualization**: 3D toolpath and volume mesh rendering

## Security Features

### Input Validation
- **File Size**: 10MB maximum upload limit
- **File Types**: Whitelist of allowed extensions (.csv, .nc, .gcode, .txt)
- **Content Inspection**: File content validation before processing
- **Path Traversal**: Protection against directory traversal attacks

### Configuration Security
- **Whitelisted Keys**: Only approved configuration parameters accepted
- **Safe Defaults**: Conservative default values for all settings
- **Error Isolation**: Security-focused error messages prevent information leakage

## Performance Characteristics

### Benchmarks (Typical Usage)
- **CSV Parsing**: <50ms for 100 rows, <2s for 10,000 rows
- **Mesh Generation**: <500ms for 100 points, <5s for 1,000 points  
- **Cache Hit Rate**: >80% for standard workflows
- **Memory Usage**: <500MB for typical manufacturing datasets

### Optimization Features
- **Multi-level Caching**: File content, processed data, rendered plots
- **Lazy Loading**: Data loaded on-demand for large datasets
- **Chunk Processing**: Large datasets processed in 10,000 row chunks
- **Mesh Level-of-Detail**: Configurable quality vs performance

## Known Issues and Technical Debt

### ✅ RESOLVED: High Priority Issues (August 2025)
1. **✅ Console Callback Architecture**: Resolved circular dependencies and registration conflicts
   - Eliminated functional callback conflicts through architectural improvements
   - Achieved excellent performance (0.01s startup, <4ms responses)
   - Remaining 79 console warnings are Dash validation warnings (cosmetic, not functional)
2. **✅ Hot-reload Functionality**: Enhanced configuration and theme hot-reload system
   - Theme switching works instantly without restart
   - Configuration updates apply dynamically through trigger mechanism
3. **📋 UI Layout Optimization**: Identified in UI/UX Analysis (pending future improvements)

### Current Medium Priority Technical Debt
1. **Dash Validation Warnings**: 79 cosmetic console warnings (optional optimization)
2. **Legacy Configuration**: Backward compatibility code could be streamlined
3. **Error Message Specificity**: Some edge cases need more descriptive error messages
4. **Memory Optimization**: Large dataset handling could be further optimized

## Integration Points and APIs

### External Dependencies
- **Core**: `dash>=2.14.0`, `plotly>=5.15.0`, `pandas>=2.0.0`
- **UI**: `dash-bootstrap-components>=1.4.0` for theming
- **Scientific**: `numpy>=1.24.0`, `scipy>=1.10.0` for calculations
- **Testing**: `pytest`, `selenium`, `webdriver-manager`

### Data Interfaces
- **Input**: CSV files (manufacturing data), G-code files (.nc programs)
- **Output**: Interactive HTML plots, data tables, configuration JSON
- **State Management**: Dash Store components for client-side data persistence

## Deployment and Distribution

### Development Deployment
```bash
# Local development server
meld-visualizer  # Runs on http://127.0.0.1:8050
```

### Production Build Options
```bash
# Python wheel distribution
python -m build

# Standalone executable
pyinstaller --name MELD-Visualizer --windowed --onefile src/meld_visualizer/app.py
```

## Future Roadmap and Extension Points

### Planned Features
- Enhanced G-code parsing capabilities for additional manufacturing commands
- Real-time data streaming support for live manufacturing monitoring
- Additional visualization options (cross-sections, layer analysis)
- Improved theme hot-reloading for seamless configuration updates

### Extension Points
- **Callback System**: Modular architecture supports additional callback modules
- **Visualization**: Plotly-based system can be extended with new plot types
- **Data Processing**: Pipeline architecture supports additional file formats
- **Theme System**: Bootstrap-based theming supports custom themes

## Troubleshooting Guide

### Common Issues

#### Application Won't Start
```bash
# Check Python version
python --version  # Must be 3.8+

# Reinstall dependencies
pip install -e ".[dev]" --force-reinstall
```

#### Import Errors
```bash
# Correct launch method
python -m meld_visualizer

# Avoid this (causes import errors)
python src/meld_visualizer/app.py
```

#### File Upload Failures
- **Check file size**: Must be <10MB
- **Verify file format**: CSV or .nc files only
- **Column requirements**: Position columns (XPos, YPos, ZPos) required

#### Performance Issues
- **Clear browser cache**: May help with loading issues
- **Reduce dataset size**: Use data filtering for large files
- **Check console**: Look for callback error patterns
- **Restart application**: Clears memory caches

### Debug Mode
```bash
# Enable debug mode for detailed error messages
DEBUG=1 meld-visualizer
```

## Contact and Support Resources

### Documentation Locations
- **Main README**: `README.md` - Complete user and developer guide
- **User Guide**: `docs/user-guide/user-guide.md` - End-user instructions
- **Architecture**: `docs/architecture/architecture.md` - System design
- **Components**: `docs/components/components.md` - Technical components
- **API Docs**: `docs/api/openapi.yaml` - API specifications

### Development Resources  
- **Development Guide**: `docs/agents.md` - Detailed development instructions
- **Claude Instructions**: `docs/CLAUDE.md` - AI assistant guidance
- **Security Audit**: `docs/SECURITY_AUDIT.md` - Security analysis
- **Performance Report**: `docs/PERFORMANCE_REPORT.md` - Performance benchmarks

## Onboarding Completion Checklist

### Technical Understanding ✅
- [x] Application purpose and value proposition understood
- [x] Architecture and component relationships mapped
- [x] Technology stack and dependencies identified
- [x] Recent development context and critical fixes reviewed

### Development Environment ✅
- [x] Project structure explored and documented
- [x] Installation methods and requirements understood  
- [x] Testing framework and categories identified
- [x] Common development workflows documented

### Domain Knowledge ✅
- [x] MELD manufacturing process context understood
- [x] Volume calculation accuracy improvements comprehended
- [x] Feedstock geometry constants and their importance grasped
- [x] Data processing pipeline from upload to visualization mapped

### Current State Assessment ✅
- [x] Recent commits and their impacts analyzed
- [x] Known issues and technical debt cataloged
- [x] Performance characteristics and optimization features understood
- [x] Security features and validation mechanisms identified

---

**Onboarding Status**: ✅ COMPLETE  
**Documentation**: Comprehensive and ready for development work  
**Next Steps**: Ready to begin feature development, bug fixes, or enhancement tasks

*This onboarding documentation serves as the complete reference for any future Claude Code sessions working with the MELD Visualizer codebase.*