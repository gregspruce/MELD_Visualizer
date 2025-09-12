# MELD Visualizer Testing - Quick Start Guide

Get up and running with the MELD Visualizer test suite in minutes.

## ⚡ TL;DR - Run Tests Now

```bash
# 1. Install dependencies
pip install -e ".[test,playwright]"

# 2. Install browsers (one-time setup)
cd tests/playwright && npm install && npx playwright install

# 3. Run all tests
python tests/run_tests.py --all --start-app
```

## 🏃‍♂️ 5-Minute Setup

### Step 1: Dependencies
```bash
# From project root
pip install -r requirements-dev.txt
```

### Step 2: Playwright Setup
```bash
cd tests/playwright
npm install
npx playwright install chromium firefox webkit
```

### Step 3: Verify Setup
```bash
# Test Python environment
python -c "import pytest; print('✅ Python tests ready')"

# Test Playwright
npx playwright test --list | head -5
```

### Step 4: Run Your First Tests
```bash
# Python unit tests (fast)
pytest tests/python/unit/ -v

# Playwright tests (requires running app)
python -m meld_visualizer &  # Start app in background
sleep 10                     # Wait for startup
cd tests/playwright && npx playwright test e2e/
```

## 🎯 Common Test Commands

### Python Tests
```bash
# All unit tests
pytest tests/python/unit/

# With coverage
pytest tests/python/unit/ --cov=src/meld_visualizer

# Specific test file
pytest tests/python/unit/test_data_processing.py

# Specific test function
pytest tests/python/unit/test_data_processing.py::test_load_csv_data

# Performance tests only
pytest -m performance

# Skip slow tests
pytest -m "not slow"
```

### Playwright Tests
```bash
cd tests/playwright

# All tests
npx playwright test

# Specific suite
npx playwright test e2e/
npx playwright test integration/
npx playwright test performance/

# Debug mode (opens browser)
npx playwright test --debug

# Headed mode (visible browser)
npx playwright test --headed

# Generate test code
npx playwright codegen http://localhost:8050
```

### Combined Test Runner
```bash
# All tests with app management
python tests/run_tests.py --all --start-app

# Specific test types
python tests/run_tests.py --unit
python tests/run_tests.py --e2e
python tests/run_tests.py --performance

# With verbose output
python tests/run_tests.py --all --verbose
```

## 🔧 Development Workflow

### Adding a New Feature
1. **Write unit tests first:**
   ```python
   # tests/python/unit/test_my_feature.py
   def test_my_new_feature():
       # Test the expected behavior
       assert my_feature() == expected_result
   ```

2. **Implement the feature:**
   ```python
   # src/meld_visualizer/my_feature.py
   def my_feature():
       return expected_result
   ```

3. **Add integration tests if needed:**
   ```javascript
   // tests/playwright/integration/test_my_feature.spec.js
   test('my feature integration', async ({ page }) => {
     // Test feature in browser context
   });
   ```

4. **Run tests:**
   ```bash
   pytest tests/python/unit/test_my_feature.py -v
   ```

### Before Committing
```bash
# Run the full test suite
python tests/run_tests.py --all --start-app

# Or just the essentials
pytest tests/python/unit/ --cov=src/meld_visualizer --cov-fail-under=75
```

## 🐛 Debugging Tests

### Python Test Debugging
```bash
# Drop into debugger on failure
pytest tests/python/unit/test_file.py --pdb

# Show local variables on failure
pytest tests/python/unit/test_file.py -l

# Verbose output with print statements
pytest tests/python/unit/test_file.py -v -s
```

### Playwright Test Debugging
```bash
cd tests/playwright

# Interactive debugging
npx playwright test --debug

# Visual debugging (see the browser)
npx playwright test --headed --slowMo=1000

# Trace recording (for later analysis)
npx playwright test --trace on
npx playwright show-trace trace.zip
```

### Common Issues

**"Application not responding":**
```bash
# Check if app is running
curl http://localhost:8050

# Start app manually
python -m meld_visualizer
```

**"ModuleNotFoundError":**
```bash
# Install in development mode
pip install -e .

# Verify Python path
python -c "import sys; print('\\n'.join(sys.path))"
```

**"Playwright browser not found":**
```bash
# Reinstall browsers
npx playwright install --force
```

## 📊 Test Reports

### Coverage Reports
```bash
# Generate HTML coverage report
pytest tests/python/unit/ --cov=src/meld_visualizer --cov-report=html

# Open report
open tests/reports/coverage_html/index.html  # macOS
xdg-open tests/reports/coverage_html/index.html  # Linux
```

### Playwright Reports
```bash
cd tests/playwright

# Generate and view HTML report
npx playwright test
npx playwright show-report
```

## 🎨 Page Objects (Playwright)

Use page objects for maintainable browser tests:

```python
from tests.playwright.fixtures.page_objects import MeldVisualizerPage

async def test_file_upload(page):
    meld_page = MeldVisualizerPage(page)

    # Navigate and wait for app to load
    await meld_page.navigate()
    await meld_page.wait_for_app_ready()

    # Upload test file
    test_file = "tests/playwright/fixtures/test_data/sample_meld_data.csv"
    await meld_page.upload_csv_file(test_file)

    # Verify results
    await meld_page.wait_for_graph_render()
    assert "data loaded" in await meld_page.get_output_filename()
```

## 🔍 Test Data

### Using Existing Test Data
```python
# Pytest fixtures provide test data paths
def test_with_sample_data(sample_meld_csv_path):
    df = load_csv_data(sample_meld_csv_path)
    assert len(df) > 0

def test_with_sample_dataframe(sample_meld_dataframe):
    assert 'XPos' in sample_meld_dataframe.columns
```

### Generating Test Data
```python
# Use factories for dynamic test data
def test_with_generated_data(large_dataframe):
    stats = calculate_statistics(large_dataframe)
    assert stats['count'] == len(large_dataframe)
```

## ⚙️ Configuration

### Environment Variables
Create `tests/.env`:
```bash
BASE_URL=http://localhost:8050
HEADLESS=false
DEFAULT_TIMEOUT=30000
SCREENSHOT_MODE=only-on-failure
```

### Pytest Markers
```python
# Mark slow tests
@pytest.mark.slow
def test_large_dataset_processing():
    pass

# Mark performance tests
@pytest.mark.performance
def test_processing_speed():
    pass

# Run only fast tests
pytest -m "not slow"
```

## 🚀 CI/CD Integration

### GitHub Actions
Tests run automatically on:
- Pull requests
- Pushes to main/develop
- Nightly (extended tests)

### Local CI Simulation
```bash
# Run tests as they would in CI
export CI=true
python tests/run_tests.py --all --start-app --verbose
```

## 📚 Further Reading

- **[Testing Strategy](TESTING_STRATEGY.md)** - Comprehensive testing approach
- **[Main README](README.md)** - Detailed documentation
- **[Playwright Docs](https://playwright.dev/)** - Playwright testing framework
- **[PyTest Docs](https://docs.pytest.org/)** - Python testing framework

## 🆘 Getting Help

1. **Check the logs:**
   ```bash
   ls tests/reports/  # Test execution logs
   ```

2. **Run with verbose output:**
   ```bash
   pytest -v -s
   npx playwright test --reporter=line
   ```

3. **Common test patterns:**
   Look at existing tests in `tests/python/unit/` and `tests/playwright/` for examples

4. **Debug interactively:**
   ```bash
   pytest --pdb  # Drop into Python debugger
   npx playwright test --debug  # Interactive browser debugging
   ```

---

**Happy Testing! 🧪✨**

Remember: Good tests make refactoring fearless and deployments confident.
