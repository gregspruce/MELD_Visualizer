# MELD Visualizer Test Suite

A comprehensive testing infrastructure for the MELD Visualizer Dash application, supporting unit tests, integration tests, end-to-end tests, performance testing, and visual regression testing.

## 📁 Directory Structure

```
tests/
├── playwright/              # Browser-based tests using Playwright
│   ├── config/              # Test configuration files
│   │   ├── playwright.config.js      # Main Playwright configuration
│   │   ├── global-setup.js           # Global test setup
│   │   ├── global-teardown.js        # Global test cleanup
│   │   ├── test.env                  # Test environment variables
│   │   └── ci.env                    # CI environment variables
│   ├── fixtures/            # Test data and utilities
│   │   ├── test_data/       # Sample CSV, NC files
│   │   │   ├── sample_meld_data.csv  # Standard test dataset
│   │   │   ├── minimal_meld_data.csv # Minimal test dataset
│   │   │   ├── invalid_meld_data.csv # Invalid data for error testing
│   │   │   └── sample_toolpath.nc    # Sample G-code file
│   │   └── page_objects.py  # Page Object Model classes
│   ├── unit/                # Component-level browser tests
│   ├── integration/         # Multi-component interactions
│   ├── e2e/                 # Complete user workflows
│   ├── performance/         # Performance benchmarks
│   ├── visual/              # Screenshot comparisons
│   └── package.json         # Node.js dependencies
├── python/                  # Pure Python unit tests (no browser)
│   ├── unit/                # Unit tests for Python modules
│   │   ├── test_data_processing.py   # Data processing tests
│   │   ├── test_config.py            # Configuration tests
│   │   └── test_services.py          # Service layer tests
│   ├── conftest.py          # PyTest fixtures and configuration
│   └── pytest.ini           # PyTest configuration
├── recordings/              # Playwright codegen recordings
├── reports/                 # Test execution reports and artifacts
│   ├── coverage_html/       # HTML coverage reports
│   ├── junit.xml           # JUnit test results
│   ├── coverage.xml        # Coverage XML for CI
│   └── *.json              # Various JSON reports
├── run_tests.py            # Main test runner script
├── run_playwright_tests.py # Playwright MCP test runner
└── README.md               # This file
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+ with pip
- Node.js 18+ with npm
- Git

### Installation

1. **Install Python dependencies:**
   ```bash
   # Install test dependencies
   pip install -e ".[test,playwright]"

   # Or install from requirements
   pip install -r requirements-dev.txt
   ```

2. **Install Playwright and browsers:**
   ```bash
   cd tests/playwright
   npm install
   npx playwright install --with-deps
   ```

3. **Verify installation:**
   ```bash
   # Test Python setup
   python -m pytest tests/python/unit/ --collect-only

   # Test Playwright setup
   npx playwright test --list
   ```

## 🧪 Running Tests

### Quick Start

```bash
# Run all tests
python tests/run_tests.py --all

# Run specific test types
python tests/run_tests.py --unit           # Python unit tests only
python tests/run_tests.py --e2e            # E2E tests only
python tests/run_tests.py --performance    # Performance tests only

# Run with application auto-start
python tests/run_tests.py --all --start-app
```

### Python Unit Tests

```bash
# Run all Python unit tests
python -m pytest tests/python/unit/

# Run with coverage
python -m pytest tests/python/unit/ --cov=src/meld_visualizer

# Run specific test file
python -m pytest tests/python/unit/test_data_processing.py

# Run with markers
python -m pytest -m "not slow"           # Skip slow tests
python -m pytest -m "performance"        # Run performance tests only
```

### Playwright Tests

```bash
# Navigate to Playwright directory
cd tests/playwright

# Run all Playwright tests
npx playwright test

# Run specific test suites
npx playwright test e2e/                  # E2E tests
npx playwright test integration/          # Integration tests
npx playwright test performance/          # Performance tests

# Run in headed mode (visible browser)
npx playwright test --headed

# Debug mode
npx playwright test --debug

# Generate code from interactions
npx playwright codegen http://localhost:8050
```

### Playwright MCP Tests

```bash
# Run using MCP functions (requires MCP setup)
python tests/run_playwright_tests.py
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the tests directory:

```bash
# Application settings
BASE_URL=http://localhost:8050
HEADLESS=false

# Test timeouts (milliseconds)
DEFAULT_TIMEOUT=30000
NAVIGATION_TIMEOUT=30000

# Performance thresholds
LOAD_TIME_THRESHOLD=5000
RENDER_TIME_THRESHOLD=2000

# Visual regression
VISUAL_THRESHOLD=0.2
UPDATE_SNAPSHOTS=false
```

### Test Markers

Use pytest markers to categorize and run specific test types:

```python
@pytest.mark.unit
def test_data_loading():
    """Unit test for data loading functionality"""
    pass

@pytest.mark.performance
def test_large_dataset_processing():
    """Performance test for large datasets"""
    pass

@pytest.mark.skip_ci
def test_local_only_feature():
    """Test that only runs locally"""
    pass
```

## 📊 Test Types

### 1. Python Unit Tests (`tests/python/unit/`)

**Purpose:** Test individual Python functions and classes in isolation.

**Examples:**
- Data processing logic
- Configuration management
- Service layer functionality
- Utility functions

**Key Features:**
- Fast execution (< 1 second per test)
- Mocked external dependencies
- High code coverage
- Property-based testing with Hypothesis

### 2. Playwright Component Tests (`tests/playwright/unit/`)

**Purpose:** Test individual UI components in the browser.

**Examples:**
- File upload component
- Graph rendering
- Filter controls
- Theme switching

### 3. Integration Tests (`tests/playwright/integration/`)

**Purpose:** Test interactions between multiple components.

**Examples:**
- File upload → data processing → graph rendering
- Filter controls → graph updates
- Tab navigation → content switching
- Export functionality

### 4. End-to-End Tests (`tests/playwright/e2e/`)

**Purpose:** Test complete user workflows from start to finish.

**Examples:**
- Complete data analysis workflow
- Error handling and recovery
- Cross-browser compatibility
- Accessibility compliance

### 5. Performance Tests (`tests/playwright/performance/`)

**Purpose:** Measure and validate application performance.

**Examples:**
- Page load time
- Large file upload performance
- Graph rendering speed
- Memory usage monitoring

### 6. Visual Regression Tests (`tests/playwright/visual/`)

**Purpose:** Detect unintended visual changes in the UI.

**Examples:**
- Screenshot comparisons
- Cross-browser visual consistency
- Theme visual validation
- Responsive design testing

## 🛠 Development Workflow

### Adding New Tests

1. **Python Unit Tests:**
   ```python
   # tests/python/unit/test_new_feature.py
   import pytest
   from meld_visualizer.new_feature import NewFeature

   class TestNewFeature:
       def test_basic_functionality(self):
           feature = NewFeature()
           result = feature.process()
           assert result is not None
   ```

2. **Playwright Tests:**
   ```javascript
   // tests/playwright/e2e/test_new_workflow.spec.js
   import { test, expect } from '@playwright/test';

   test('new workflow test', async ({ page }) => {
     await page.goto('http://localhost:8050');
     // Add test steps
   });
   ```

3. **Using Page Objects:**
   ```python
   # tests/playwright/e2e/test_with_page_objects.py
   from fixtures.page_objects import MeldVisualizerPage

   async def test_file_upload(page):
       meld_page = MeldVisualizerPage(page)
       await meld_page.navigate()
       await meld_page.upload_csv_file("test_data.csv")
       await meld_page.wait_for_graph_render()
   ```

### Test Data Management

1. **Static Test Data:**
   - Located in `tests/playwright/fixtures/test_data/`
   - Version controlled
   - Represents typical use cases

2. **Generated Test Data:**
   ```python
   # Use Faker for dynamic test data
   from faker import Faker
   fake = Faker()

   test_data = {
       'date': fake.date(),
       'temperature': fake.pyfloat(min_value=100, max_value=200),
       'position': fake.pyfloat(min_value=0, max_value=10)
   }
   ```

3. **Large Dataset Generation:**
   ```python
   # For performance testing
   def generate_large_dataset(rows=10000):
       # Generate performance test data
       pass
   ```

### Debugging Tests

1. **Python Tests:**
   ```bash
   # Run with debugger
   python -m pytest tests/python/unit/test_file.py::test_function --pdb

   # Verbose output
   python -m pytest tests/python/unit/ -v -s

   # Show local variables on failure
   python -m pytest tests/python/unit/ -l
   ```

2. **Playwright Tests:**
   ```bash
   # Debug mode (opens browser debugger)
   npx playwright test --debug

   # Headed mode (visible browser)
   npx playwright test --headed

   # Trace viewer
   npx playwright test --trace on
   ```

### Performance Monitoring

1. **Python Performance:**
   ```python
   @pytest.mark.performance
   def test_performance():
       import time
       start = time.time()
       # Test code
       duration = time.time() - start
       assert duration < 2.0  # Should complete in under 2 seconds
   ```

2. **Browser Performance:**
   ```javascript
   test('page performance', async ({ page }) => {
     const start = Date.now();
     await page.goto('http://localhost:8050');
     const loadTime = Date.now() - start;
     expect(loadTime).toBeLessThan(5000);
   });
   ```

## 🔍 CI/CD Integration

### GitHub Actions

The test suite integrates with GitHub Actions for continuous testing:

- **PR Tests:** Run on pull requests (`test-suite.yml`)
- **Nightly Tests:** Extended testing (`nightly-tests.yml`)
- **Security Scans:** Dependency and code security analysis
- **Cross-Platform:** Testing on multiple OS and Python versions

### Local CI Simulation

```bash
# Run tests as they would run in CI
python tests/run_tests.py --all --start-app --verbose

# Security scanning
bandit -r src/
safety check
```

## 📈 Reporting and Metrics

### Coverage Reports

- **HTML Report:** `tests/reports/coverage_html/index.html`
- **XML Report:** `tests/reports/coverage.xml` (for CI)
- **JSON Report:** `tests/reports/coverage.json` (for analysis)

### Test Results

- **JUnit XML:** `tests/reports/junit.xml`
- **Playwright HTML:** `tests/reports/playwright-report/`
- **Custom JSON:** Various detailed reports

### Performance Metrics

- **Load Times:** Tracked per test run
- **Memory Usage:** Monitored during performance tests
- **Render Times:** Graph and component rendering speeds

## 🚨 Troubleshooting

### Common Issues

1. **Application not starting:**
   ```bash
   # Check if port 8050 is available
   netstat -an | grep 8050

   # Start application manually
   python -m meld_visualizer
   ```

2. **Playwright browser issues:**
   ```bash
   # Reinstall browsers
   npx playwright install --force

   # Install system dependencies
   npx playwright install-deps
   ```

3. **Python import errors:**
   ```bash
   # Install in development mode
   pip install -e .

   # Check Python path
   python -c "import sys; print(sys.path)"
   ```

4. **Test data not found:**
   ```bash
   # Verify test data exists
   ls tests/playwright/fixtures/test_data/

   # Regenerate if needed
   python tests/generate_test_data.py
   ```

### Getting Help

1. Check the logs in `tests/reports/`
2. Run tests with verbose output (`-v` or `--verbose`)
3. Use debug mode for step-by-step execution
4. Review GitHub Actions logs for CI failures
5. Check the main project documentation

## 🔄 Maintenance

### Regular Tasks

1. **Update dependencies:** Keep test dependencies current
2. **Review test data:** Ensure test data reflects current usage
3. **Monitor performance:** Watch for performance regressions
4. **Update snapshots:** Refresh visual regression baselines when UI changes
5. **Clean reports:** Archive or remove old test reports

### Best Practices

1. **Test Naming:** Use descriptive, behavior-focused names
2. **Test Independence:** Each test should be able to run in isolation
3. **Data Management:** Use fixtures and factories for test data
4. **Performance:** Keep unit tests fast, mark slow tests appropriately
5. **Documentation:** Update test documentation with code changes

---

For more information, see the main project documentation and individual test file docstrings.
