# MELD Visualizer Runbook

This runbook provides quick reference commands for development, testing, and deployment.

## Installation

### Development Setup
```bash
# Clone repository
git clone https://github.com/gregspruce/MELD_Visualizer.git
cd MELD_Visualizer

# Install with all development dependencies
pip install -e ".[dev,test,playwright,build]"
```

### Production Installation
```bash
pip install meld-visualizer
```

## Running the Application

### Development Mode
```bash
# Using the installed command (recommended)
meld-visualizer

# Running as a Python module
python -m src.meld_visualizer.app
```

### Debug Mode
```bash
# Enable explicit debug mode
DEBUG=1 meld-visualizer
```

## Testing

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage reporting
pytest --cov=src/meld_visualizer --cov-report=html

# Run specific test categories
pytest -m "unit"
pytest -m "not e2e"
```

## Code Quality

### Formatting and Linting
```bash
# Format code with black
black src/ tests/

# Lint with ruff
ruff check src/ tests/

# Type checking with mypy
mypy src/
```

## Building and Packaging

### Python Package Build
```bash
# Build wheel and source distribution
python -m build
```

### Executable Build
```bash
# Build the executable using PyInstaller
pyinstaller MELD-Visualizer.spec
```

## Quick Reference

### Essential Commands
```bash
# Setup
pip install -e ".[dev,test,playwright,build]"

# Run app
meld-visualizer

# Test
pytest

# Quality
black src/ tests/ && ruff check src/ tests/ && mypy src/

# Build
python -m build
```