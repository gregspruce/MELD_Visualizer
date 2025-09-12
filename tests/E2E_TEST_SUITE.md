# MELD Visualizer E2E Test Suite

Comprehensive end-to-end testing suite for the MELD Visualizer Dash application using Playwright with MCP (Model Context Protocol) integration.

## Overview

This E2E test suite provides comprehensive validation of the MELD Visualizer application across multiple browsers, devices, and scenarios. It includes performance benchmarking, error scenario testing, responsive design validation, and Enhanced UI functionality verification.

## Test Suite Components

### 1. Critical User Journeys (`test_critical_user_journeys.py`)
Tests the essential workflows that users depend on:
- **Complete CSV upload to visualization workflow** - End-to-end data processing pipeline
- **Graph interaction and filtering** - Zoom, pan, hover, and filter operations
- **Theme switching functionality** - UI theme consistency across changes
- **Tab navigation workflow** - Navigation between application sections
- **Data export workflow** - Export functionality validation
- **Responsive design behavior** - Cross-viewport functionality
- **Error recovery scenarios** - Recovery from invalid data uploads
- **Performance benchmarks** - Load time and processing speed validation

### 2. Enhanced UI Functionality (`test_enhanced_ui_functionality.py`)
Validates the Enhanced UI components and desktop-optimized features:
- **Loading overlay behavior** - Loading states during data processing
- **Toast notification system** - User feedback and notification display
- **Progress indicator functionality** - Progress bars and indicators
- **Enhanced upload area styling** - Improved file upload UX
- **Responsive control panels** - Control panel adaptation across viewports
- **Enhanced tab navigation** - Desktop-optimized tab scrolling
- **Desktop-optimized layout** - Space utilization and layout efficiency
- **User feedback consistency** - Consistent feedback patterns
- **Keyboard accessibility** - Enhanced UI keyboard navigation

### 3. Performance Benchmarks (`test_performance_benchmarks.py`)
Comprehensive performance testing and optimization validation:
- **Initial page load performance** - Core Web Vitals and load times
- **CSV upload processing performance** - File processing speed by size
- **Graph rendering performance** - Plotly graph render times and interactions
- **Memory usage benchmarks** - Memory consumption and leak detection
- **Concurrent operations performance** - Stress testing under load
- **Network request optimization** - Request efficiency and optimization
- **Browser resource efficiency** - Resource cleanup and management

### 4. Error Scenarios (`test_error_scenarios.py`)
Robust error handling and recovery validation:
- **Invalid CSV upload handling** - Error messages and graceful degradation
- **Recovery from invalid to valid uploads** - Application recovery processes
- **Network interruption simulation** - Resilience during connectivity issues
- **Memory pressure scenarios** - Behavior under memory constraints
- **Rapid user input handling** - Race condition and input validation
- **Browser compatibility errors** - Cross-browser error handling
- **Graceful degradation** - Feature availability with browser limitations
- **Data validation error boundaries** - Handling of malformed data
- **Concurrent error scenarios** - Multiple simultaneous error conditions

### 5. Responsive Design (`test_responsive_design.py`)
Cross-device and viewport compatibility validation:
- **Desktop viewport optimization** - Space utilization across desktop sizes
- **Tablet viewport adaptation** - Touch-friendly interface adaptation
- **Mobile viewport compatibility** - Mobile-first design validation
- **Viewport transition smoothness** - Smooth responsive transitions
- **CSS media query effectiveness** - Responsive breakpoint validation
- **Cross-device functionality parity** - Consistent functionality across devices

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- MELD Visualizer application running at `http://127.0.0.1:8050`
- Node.js (for Playwright browser installation)

### Install Dependencies
```bash
# Install E2E testing dependencies
pip install -r tests/requirements-e2e.txt

# Install Playwright browsers
python -m playwright install
```

### Verify Setup
```bash
# Check if server is running
curl http://127.0.0.1:8050

# Run prerequisites check
python tests/run_e2e_tests.py --suite smoke
```

## Running Tests

### Quick Start
```bash
# Run smoke tests (fastest validation)
python tests/run_e2e_tests.py --suite smoke

# Run all critical user journeys
python tests/run_e2e_tests.py --suite critical

# Run specific test suite
python tests/run_e2e_tests.py --suite enhanced_ui
```

### Advanced Usage

#### Test Suite Options
```bash
# All test suites
--suite all              # Run all E2E tests
--suite smoke            # Quick validation tests
--suite critical         # Critical user journey tests
--suite enhanced_ui      # Enhanced UI functionality tests
--suite performance      # Performance benchmark tests
--suite error_handling   # Error scenario tests
--suite responsive       # Responsive design tests
```

#### Browser Options
```bash
# Single browser
--browser chromium       # Google Chrome/Chromium
--browser firefox        # Mozilla Firefox
--browser webkit         # Safari WebKit

# Cross-browser testing
--cross-browser          # Test across all browsers
```

#### Execution Modes
```bash
# Visual debugging
--headed                 # Run with visible browser windows
--verbose                # Detailed test output

# Performance optimization
--no-parallel            # Disable parallel execution
--max-failures 5         # Stop after 5 failures
```

#### Special Test Modes
```bash
# Performance testing
--performance-only       # Run only performance benchmarks

# Browser compatibility
--cross-browser          # Test across all supported browsers

# Specific test filtering
--markers "smoke and not slow"  # Run only fast smoke tests
```

### Example Commands

```bash
# Development workflow - quick validation
python tests/run_e2e_tests.py --suite smoke --headed --verbose

# CI/CD pipeline - comprehensive testing
python tests/run_e2e_tests.py --suite all --browser chromium

# Performance analysis
python tests/run_e2e_tests.py --performance-only --verbose

# Cross-browser validation
python tests/run_e2e_tests.py --cross-browser --suite critical

# Error handling validation
python tests/run_e2e_tests.py --suite error_handling --max-failures 3
```

## Test Reports

### Generated Reports
- **HTML Report**: Interactive test results with screenshots and videos
- **JSON Report**: Machine-readable test results and metrics
- **Performance Metrics**: Detailed performance benchmarks
- **Screenshots**: Failure screenshots and visual regression baselines
- **Videos**: Test execution recordings for debugging

### Report Locations
```
tests/reports/
├── e2e/                    # E2E test reports
│   ├── e2e_report_*.html   # HTML test reports
│   ├── e2e_report_*.json   # JSON test results
│   └── e2e_summary_*.json  # Test execution summaries
├── screenshots/            # Test screenshots
├── videos/                 # Test execution videos
└── visual_regression/      # Visual comparison baselines
```

## Configuration

### Environment Variables
```bash
# Application settings
BASE_URL=http://127.0.0.1:8050    # Application URL
BROWSER=chromium                   # Default browser

# Execution settings
HEADLESS=true                      # Headless mode
SLOW_MO=0                         # Slow motion delay (ms)
PARALLEL=true                      # Parallel execution

# Debugging settings
SCREENSHOT=only-on-failure         # Screenshot mode
VIDEO=retain-on-failure           # Video recording mode
```

### Test Data
Test data files are located in `tests/playwright/fixtures/test_data/`:
- `sample_meld_data.csv` - Valid MELD data for testing
- `minimal_meld_data.csv` - Minimal dataset for quick tests
- `invalid_meld_data.csv` - Invalid data for error testing

## Architecture

### Test Structure
```
tests/
├── playwright/
│   ├── e2e/                       # E2E test files
│   │   ├── test_critical_user_journeys.py
│   │   ├── test_enhanced_ui_functionality.py
│   │   ├── test_performance_benchmarks.py
│   │   ├── test_error_scenarios.py
│   │   └── test_responsive_design.py
│   ├── fixtures/                  # Test fixtures and utilities
│   │   ├── mcp_fixtures.py       # Python MCP fixtures
│   │   └── test_data/            # Test data files
│   └── conftest.py               # Pytest configuration
├── run_e2e_tests.py              # Main test runner
├── requirements-e2e.txt          # E2E dependencies
└── reports/                      # Generated reports
```

### Key Components

#### MCP Fixtures (`mcp_fixtures.py`)
- **MCPPerformanceMonitor**: Performance metrics collection
- **MCPConsoleMonitor**: Console error monitoring
- **MCPNetworkMonitor**: Network request tracking
- **MCPPageUtils**: Common page interaction utilities
- **MCPVisualRegression**: Visual regression testing support

#### Test Configuration (`conftest.py`)
- Browser context management
- Test environment setup
- Error tracking configuration
- Report generation hooks
- Fixture dependency management

#### Test Runner (`run_e2e_tests.py`)
- Test suite orchestration
- Browser compatibility testing
- Performance test execution
- Report generation and summary
- Cleanup and maintenance utilities

## Best Practices

### Writing E2E Tests
1. **Use Page Object Pattern**: Encapsulate page interactions in reusable methods
2. **Wait for Elements**: Always wait for elements to be ready before interaction
3. **Handle Async Operations**: Use proper async/await patterns
4. **Test Real User Scenarios**: Focus on actual user workflows
5. **Validate Both Success and Failure**: Test error conditions as well as happy paths

### Performance Testing
1. **Establish Baselines**: Set realistic performance thresholds
2. **Test Different Data Sizes**: Validate performance across file sizes
3. **Monitor Memory Usage**: Watch for memory leaks and excessive consumption
4. **Test Under Load**: Simulate concurrent operations and stress conditions

### Error Testing
1. **Test Recovery**: Ensure application can recover from errors
2. **Validate Error Messages**: Check that users receive helpful feedback
3. **Test Edge Cases**: Include boundary conditions and invalid inputs
4. **Simulate Real Failures**: Test network interruptions and resource constraints

## Troubleshooting

### Common Issues

#### Server Not Running
```bash
Error: MELD Visualizer server is not running at http://127.0.0.1:8050
Solution: Start server with: python -m meld_visualizer
```

#### Browser Installation Issues
```bash
Error: Playwright browsers not installed
Solution: python -m playwright install
```

#### Permission Errors on Screenshots/Videos
```bash
Error: Permission denied writing to tests/reports/
Solution: Ensure write permissions on reports directory
```

#### Memory Issues During Testing
```bash
Error: Out of memory during test execution
Solution: Run tests with --no-parallel or increase system memory
```

### Debugging Tests

#### Visual Debugging
```bash
# Run with visible browser and verbose output
python tests/run_e2e_tests.py --suite critical --headed --verbose
```

#### Performance Debugging
```bash
# Run performance tests with detailed metrics
python tests/run_e2e_tests.py --performance-only --verbose
```

#### Error Investigation
```bash
# Run specific failing test with maximum detail
python tests/run_e2e_tests.py --suite "test_name" --headed --verbose --max-failures 1
```

## Continuous Integration

### GitHub Actions Integration
```yaml
name: E2E Tests
on: [push, pull_request]

jobs:
  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r tests/requirements-e2e.txt
          python -m playwright install --with-deps

      - name: Start MELD Visualizer
        run: python -m meld_visualizer &

      - name: Run E2E tests
        run: python tests/run_e2e_tests.py --suite all --browser chromium

      - name: Upload test reports
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: e2e-reports
          path: tests/reports/
```

### Jenkins Integration
```groovy
pipeline {
    agent any
    stages {
        stage('E2E Tests') {
            steps {
                sh 'pip install -r tests/requirements-e2e.txt'
                sh 'python -m playwright install'
                sh 'python -m meld_visualizer &'
                sh 'python tests/run_e2e_tests.py --suite all'
            }
            post {
                always {
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'tests/reports/e2e',
                        reportFiles: '*.html',
                        reportName: 'E2E Test Report'
                    ])
                }
            }
        }
    }
}
```

## Maintenance

### Regular Tasks
```bash
# Clean up old reports (older than 7 days)
python tests/run_e2e_tests.py --cleanup 7

# Update browser installations
python -m playwright install

# Validate test environment
python tests/run_e2e_tests.py --suite smoke
```

### Test Suite Updates
1. **Add New Test Cases**: Follow existing patterns in test files
2. **Update Baselines**: Refresh visual regression baselines when UI changes
3. **Performance Thresholds**: Adjust performance expectations as application evolves
4. **Browser Support**: Update browser matrix as support requirements change

## Contributing

### Adding New Tests
1. Choose appropriate test file based on test category
2. Follow existing test patterns and naming conventions
3. Use MCP fixtures for common operations
4. Include both positive and negative test cases
5. Add appropriate test markers for filtering

### Test Categories
- `@pytest.mark.smoke` - Critical functionality tests
- `@pytest.mark.performance` - Performance validation tests
- `@pytest.mark.visual` - Visual regression tests
- `@pytest.mark.mobile` - Mobile-specific tests
- `@pytest.mark.slow` - Long-running tests

## Support

For questions or issues with the E2E test suite:
1. Check the troubleshooting section above
2. Review test logs in `tests/reports/`
3. Run tests with `--verbose` flag for detailed output
4. Check application logs for server-side issues

## Performance Benchmarks

### Baseline Expectations
- **Page Load**: < 5 seconds
- **CSV Upload Processing**: < 10 seconds (typical files)
- **Graph Rendering**: < 3 seconds
- **User Interactions**: < 1 second response time
- **Memory Usage**: < 150 MB total application memory

### Performance Test Coverage
- Initial page load with Core Web Vitals
- File upload and processing across different file sizes
- Graph rendering and interaction responsiveness
- Memory usage patterns and leak detection
- Network request optimization and caching
- Concurrent operation handling

These benchmarks are validated in the performance test suite and adjusted based on application evolution and performance improvements.
