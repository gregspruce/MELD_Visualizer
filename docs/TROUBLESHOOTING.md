# MELD Visualizer Troubleshooting Guide

This guide helps resolve common issues encountered during development, testing, and usage of the MELD Visualizer application.

## Installation Issues

### Python Version Problems
**Problem**: Application won't install or run
```
Error: Python version 3.7 is not supported
```

**Solution**:
```bash
# Check current Python version
python --version

# Install Python 3.8+ if needed
# On Ubuntu/Debian:
sudo apt update && sudo apt install python3.8 python3.8-pip

# On macOS with Homebrew:
brew install python@3.8

# On Windows: Download from python.org
```

### Dependency Installation Failures
**Problem**: pip install fails with dependency conflicts
```
ERROR: Could not find a version that satisfies the requirement
```

**Solutions**:
```bash
# Method 1: Update pip and try again
python -m pip install -U pip
pip install -e ".[dev]"

# Method 2: Use legacy installation
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Method 3: Create fresh virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows
pip install -e ".[dev]"
```

### Import Errors
**Problem**: Cannot import meld_visualizer
```
ModuleNotFoundError: No module named 'meld_visualizer'
```

**Solutions**:
```bash
# Verify installation
pip list | grep meld

# Reinstall in development mode
pip install -e .

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Verify module location
python -c "import meld_visualizer; print(meld_visualizer.__file__)"
```

## Application Runtime Issues

### Server Won't Start
**Problem**: Application fails to start or bind to port

**Symptoms**:
- "Address already in use" error
- Application starts but browser can't connect
- ImportError during startup

**Solutions**:
```bash
# Check if port 8050 is in use
netstat -an | grep 8050  # Linux/macOS
netstat -an | findstr 8050  # Windows

# Kill existing process on port
lsof -ti:8050 | xargs kill -9  # Linux/macOS

# Start with explicit debug mode
DEBUG=1 meld-visualizer

# Try different port
PORT=8051 meld-visualizer

# Run from source for detailed error messages
python -m src.meld_visualizer.app
```

### UI Styling Issues
**Problem**: Tabs look like links, missing Bootstrap styling

**Symptoms**:
- Tabs appear as blue underlined links
- Missing button styling
- Layout appears broken

**Solutions**:
```bash
# Method 1: Check internet connection (for CDN themes)
ping cdn.jsdelivr.net

# Method 2: Use local CSS file
mkdir -p assets
# Download bootstrap.min.css to assets/ directory

# Method 3: Switch to local theme in config.json
{
    "default_theme": "bootstrap",  # Uses local assets
    "plotly_template": "plotly_white"
}
```

### Configuration Issues
**Problem**: Configuration changes not taking effect

**Solutions**:
```bash
# Restart application after config changes
# config.json changes require restart

# Verify configuration is valid JSON
python -c "import json; print(json.load(open('config/config.json')))"

# Reset to defaults
cp config/config.json config/config.json.backup
# Edit config.json to minimal settings:
{
    "default_theme": "Cerulean",
    "plotly_template": "plotly_white"
}
```

## Testing Issues

### Test Execution Problems
**Problem**: Tests hang or fail to run

**Symptoms**:
- pytest hangs without output
- "No tests ran" message
- Import errors in test files

**Solutions**:
```bash
# Disable plugin autoload
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest

# Run with verbose output to see where it hangs
pytest -v -s

# Run specific test file to isolate issues
pytest tests/unit/test_data_processing.py -v

# Check test configuration
cat tests/pytest.ini
cat tests/test_suite.conf

# Use test runner script instead
bash scripts/run_tests.sh
```

### E2E Testing Issues
**Problem**: Browser automation tests fail

**Common Errors**:
- "Chrome binary not found"
- "WebDriver session timeout"
- "Element not found"

**Solutions**:
```bash
# Install Chrome browser
# Ubuntu/Debian:
sudo apt-get update
sudo apt-get install google-chrome-stable

# macOS:
brew install --cask google-chrome

# Windows: Download from Google

# Verify Chrome installation
google-chrome --version

# Skip E2E tests if Chrome unavailable
pytest -m "not e2e"

# Increase timeout for slow systems
# Edit tests/conftest.py to increase wait times
```

### Coverage Issues
**Problem**: Coverage reports missing or incomplete

**Solutions**:
```bash
# Install coverage dependencies
pip install coverage pytest-cov

# Generate coverage report
pytest --cov=src/meld_visualizer --cov-report=html

# View coverage report
open reports/htmlcov/index.html  # macOS
start reports/htmlcov/index.html # Windows
xdg-open reports/htmlcov/index.html # Linux
```

## Data Processing Issues

### File Upload Problems
**Problem**: CSV or G-code files won't upload

**Symptoms**:
- "File too large" error
- "Invalid file format" error
- Upload hangs or fails

**Solutions**:
```bash
# Check file size (must be < 10MB)
ls -lh your_file.csv

# Verify file format
file your_file.csv
head -5 your_file.csv

# Check required columns for CSV
# Required: XPos, YPos, ZPos
# Optional: FeedVel, PathVel, ToolTemp, Time

# For G-code files
# Must have .nc extension
# Should contain G0/G1 commands
grep -E "^G[01]" your_file.nc | head -5
```

### Visualization Problems
**Problem**: Plots appear empty or incorrect

**Common Issues**:
1. **Empty G-code plot**: Ensure file contains `G1` movement commands and `M34`/`M35` extrusion codes
2. **Squashed 3D plot**: Adjust "Z-Axis Stretch Factor" (try values 2-10 for better layer visibility)
3. **Missing data points**: Check data filtering settings and range sliders
4. **Color mapping issues**: Verify selected color column contains numeric data

**Solutions**:
```bash
# Check data content
# For CSV files - verify numeric columns
python -c "
import pandas as pd
df = pd.read_csv('your_file.csv')
print(df.dtypes)
print(df.describe())
"

# For G-code files - check extrusion commands
grep -E "M3[45]" your_file.nc

# Reset all filters in UI
# Or restart application to clear cached data
```

### Unit Conversion Issues
**Problem**: Data appears in wrong units

**Symptoms**:
- Extremely large or small coordinate values
- "Units converted to mm" banner appears/doesn't appear

**Understanding**:
- Automatic conversion triggers when velocity data suggests imperial units
- Conversion multiplies position values by 25.4 (inches to mm)
- Manual override not currently available

**Solutions**:
- Ensure your data is in expected units before upload
- Check velocity columns (FeedVel, PathVel) for reasonable values
- Imperial: typically 1-100 units/min
- Metric: typically 100-5000 units/min

## Performance Issues

### Slow Application Response
**Problem**: Application becomes unresponsive with large files

**Solutions**:
```bash
# Reduce file size before upload
# Use data filtering to show subsets
# Lower mesh detail level in 3D visualizations
# Close unused browser tabs
# Restart application to clear cache

# Check system resources
top  # Linux/macOS
taskmgr  # Windows
```

### Memory Issues
**Problem**: Out of memory errors or application crashes

**Solutions**:
```bash
# Monitor memory usage
python -c "
import psutil
print(f'Available memory: {psutil.virtual_memory().available / 1024**3:.1f} GB')
"

# Reduce dataset size
# Use CSV sampling
# Apply more aggressive filtering
# Process files in smaller batches
```

## Platform-Specific Issues

### Windows Issues
**Problem**: Line ending issues (CRLF vs LF)

**Solutions**:
```bash
# Use Git Bash for commands
# Or configure Git to handle line endings
git config --global core.autocrlf true

# For files that are already checked out
git rm --cached -r .
git reset --hard
```

### macOS Issues
**Problem**: Permission issues or Xcode tools missing

**Solutions**:
```bash
# Install Xcode command line tools
xcode-select --install

# Fix Homebrew permissions
sudo chown -R $(whoami) /usr/local/share/zsh /usr/local/share/zsh/site-functions
```

### Linux Issues
**Problem**: Missing development headers

**Solutions**:
```bash
# Install build essentials
sudo apt-get install build-essential python3-dev

# For other distributions, install equivalent packages
```

## Getting Additional Help

### Debug Information to Collect
When reporting issues, include:
1. **System Information**:
   ```bash
   python --version
   pip --version
   uname -a  # Linux/macOS
   systeminfo | findstr /B /C:"OS Name" /C:"OS Version"  # Windows
   ```

2. **Python Environment**:
   ```bash
   pip list | grep -E "(meld|dash|plotly|pandas)"
   python -c "import sys; print(sys.executable)"
   ```

3. **Error Messages**: Full error text with stack trace

4. **Steps to Reproduce**: Exact sequence of actions that trigger the issue

5. **Sample Data**: If possible, provide a minimal sample file that reproduces the issue

### Log Files and Debugging
```bash
# Enable debug mode for detailed logs
DEBUG=1 meld-visualizer

# Capture output to file
meld-visualizer 2>&1 | tee application.log

# For test debugging
pytest -v -s --tb=long > test_output.log 2>&1
```

### Community Resources
- **GitHub Issues**: https://github.com/MELD-labs/meld-visualizer/issues
- **Documentation**: See `docs/` directory for comprehensive guides
- **Sample Files**: Use files in `data/csv/` and `data/nc/` for testing
- **Development Guide**: See `docs/agents.md` for detailed development instructions