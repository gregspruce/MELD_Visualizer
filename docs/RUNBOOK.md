# MELD Visualizer Runbook

This runbook provides quick reference commands for development, testing, and deployment.

## Prerequisites

### System Requirements
- Python 3.8 or higher
- Git (for cloning repository)
- Chrome browser (for E2E testing)

### Environment Setup
```bash
# Check Python version
python --version  # Should be 3.8+

# Update pip to latest
python -m pip install -U pip
```

## Installation

### Method 1: Modern Development Setup (Recommended)
```bash
# Clone repository
git clone https://github.com/gregspruce/MELD_Visualizer.git
cd MELD_Visualizer

# Install with all development dependencies
pip install -e ".[dev]"
```

### Method 2: Legacy Installation (Still Supported)
```bash
# Update pip and install dependencies separately
python -m pip install -U pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Method 3: Production Installation
```bash
# Install from PyPI (when available)
pip install meld-visualizer
```

## Running the Application

### Development Mode
```bash
# Method 1: Using installed command (recommended)
meld-visualizer

# Method 2: Running as Python module
python -m meld_visualizer

# Method 3: From source (for development)
python -m src.meld_visualizer.app

# All methods bind to 127.0.0.1:8050
```

### Debug Mode
```bash
# Enable explicit debug mode
DEBUG=1 meld-visualizer

# Or set as environment variable
export DEBUG=1
meld-visualizer
```

## Testing

### Test Configuration
Configure test suite in `tests/test_suite.conf`:
- `unit` - Run unit tests only
- `e2e` - Run end-to-end tests only  
- `both` - Run all tests
- `none` - Skip tests

### Running Tests

#### Using Test Runner Script
```bash
# Run tests according to test_suite.conf
bash scripts/run_tests.sh

# Override test suite temporarily
TEST_SUITE=unit bash scripts/run_tests.sh
TEST_SUITE=e2e bash scripts/run_tests.sh
TEST_SUITE=both bash scripts/run_tests.sh
```

#### Using pytest Directly
```bash
# Run all tests with configuration from pyproject.toml
pytest

# Run with coverage reporting
pytest --cov=src/meld_visualizer --cov-report=html

# Run specific test categories
pytest -m "unit"        # Unit tests only
pytest -m "integration" # Integration tests only
pytest -m "e2e"         # End-to-end tests only
pytest -m "not e2e"     # Exclude E2E tests

# Run specific test files
pytest tests/unit/test_data_processing.py -v
pytest tests/e2e/test_homepage_e2e.py -v

# Disable plugin autoload (if experiencing issues)
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q -m "not e2e"
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q -m "e2e"
```

### E2E Testing Requirements
```bash
# Ensure Chrome is installed (automatic in CI)
# E2E tests use Selenium WebDriver with Chrome

# Check if Chrome is available
google-chrome --version  # Linux
Chrome --version         # macOS
```

## Code Quality

### Formatting and Linting
```bash
# Format code with black
black src/ tests/

# Lint with flake8
flake8 src/ tests/

# Type checking with mypy
mypy src/

# Run all pre-commit hooks
pre-commit run --all-files
```

### Pre-commit Setup
```bash
# Install pre-commit hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

## Building and Packaging

### Python Package Build
```bash
# Build wheel and source distribution
python -m build

# Install built package
pip install dist/meld_visualizer-*.whl
```

### Executable Build
```bash
# Generate PyInstaller spec file
pyinstaller --name MELD-Visualizer --windowed --onefile \
    --add-data "config:config" \
    --add-data "data:data" \
    --hidden-import="dash_bootstrap_components._components" \
    src/meld_visualizer/app.py

# Build from spec file
pyinstaller MELD-Visualizer.spec
```

## Configuration

### Theme Configuration
Edit `config/config.json`:
```json
{
    "default_theme": "Cerulean",
    "plotly_template": "plotly_white"
}
```

### Environment Variables
- `DEBUG=1` - Enable debug mode
- `HOST=127.0.0.1` - Bind host (default)
- `PORT=8050` - Bind port (default)

## Troubleshooting

### Common Issues
```bash
# Application won't start
DEBUG=1 python -m meld_visualizer  # Check debug output

# Tests hanging
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest

# Chrome not found for E2E tests
sudo apt-get install google-chrome-stable  # Linux
brew install --cask google-chrome          # macOS
```

### Log Files
- Application logs: Console output in debug mode
- Test logs: `reports/` directory (when generated)
- Coverage reports: `reports/htmlcov/` directory

## CI/CD Integration

### GitHub Actions
The CI workflow:
1. Reads `tests/test_suite.conf` 
2. Runs appropriate test jobs (unit/e2e/both)
3. Generates coverage reports
4. Builds packages on successful tests

### Local CI Simulation
```bash
# Simulate CI environment
pip install -e ".[dev]"
bash scripts/run_tests.sh
python -m build
```

## Quick Reference

### Essential Commands
```bash
# Setup
pip install -e ".[dev]"

# Run app
meld-visualizer

# Test
bash scripts/run_tests.sh

# Quality
black src/ tests/ && flake8 src/ tests/ && mypy src/

# Build
python -m build
```

### Directory Structure
- `src/meld_visualizer/` - Main application code
- `tests/` - Test suite  
- `config/` - Configuration files
- `data/` - Sample data files
- `docs/` - Documentation
- `scripts/` - Utility scripts

