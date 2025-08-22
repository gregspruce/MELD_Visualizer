# Playwright MCP Configuration for MELD Visualizer

This document describes the comprehensive Playwright MCP (Model Context Protocol) configuration for testing the MELD Visualizer Dash application.

## Overview

The Playwright MCP configuration provides advanced browser automation capabilities specifically tailored for testing modern Dash applications with complex 3D visualizations, real-time updates, and file upload functionality.

## Architecture

```
tests/playwright/
├── config/
│   ├── playwright.config.js       # Main MCP configuration
│   ├── mcp-utils.js               # MCP utility functions
│   ├── global-setup.js            # MCP global setup
│   ├── global-teardown.js         # Global cleanup
│   └── test.env                   # Environment variables
├── fixtures/
│   ├── mcp-fixtures.js            # Custom MCP test fixtures
│   └── test_data/                 # Test data files
├── e2e/                           # End-to-end tests
├── integration/                   # Integration tests
├── visual/                        # Visual regression tests
├── performance/                   # Performance tests
└── reports/                       # Test reports and artifacts
```

## Key Features

### 1. Browser Context Configuration
- **Multi-browser support**: Chrome, Firefox, Safari (WebKit)
- **Mobile testing**: Responsive design validation
- **High-DPI testing**: 4K/Retina display support
- **Custom user agents**: Test-specific identification
- **Permission handling**: File upload, clipboard access

### 2. Network Interception
- **API mocking**: Dash callback response simulation
- **Request monitoring**: Complete network traffic logging
- **File upload handling**: Multipart form data processing
- **Error injection**: Network failure simulation
- **HAR recording**: Complete network session capture

### 3. Console Monitoring
- **Error detection**: Real-time console error capture
- **Performance tracking**: Runtime performance metrics
- **Debug logging**: Comprehensive application state logging
- **Exception handling**: Uncaught error monitoring

### 4. Visual Testing
- **Screenshot comparison**: Pixel-perfect visual regression
- **Plotly graph validation**: 3D visualization verification
- **Responsive testing**: Multi-viewport validation
- **Animation handling**: Dynamic content stabilization

### 5. Performance Monitoring
- **Load time tracking**: Page initialization metrics
- **Render performance**: Plotly graph rendering speed
- **Memory usage**: Application resource consumption
- **Network optimization**: Request/response optimization

## Configuration Files

### playwright.config.js
Main configuration file with MCP-optimized settings:
- Browser launch options with security disabled for testing
- Custom viewport sizes for visualization testing
- Environment-based configuration loading
- Comprehensive reporting setup

### mcp-utils.js
Utility class providing:
- Browser context creation with MCP settings
- Network interception setup
- Console monitoring configuration
- Performance metrics collection
- Screenshot utilities with comparison

### test.env
Environment variables for:
- Application URLs and timeouts
- Browser configuration
- Performance thresholds
- File paths and directories
- Feature flags

## Usage

### Installation
```bash
# Install Node.js dependencies and browsers
npm run install:mcp

# Or manually:
cd tests/playwright
npm install
npx playwright install
```

### Running Tests
```bash
# Run all tests with MCP configuration
npm run test:mcp

# Run specific test types
npm run test:mcp:e2e
npm run test:mcp:visual
npm run test:mcp:performance

# Run with browser visible (headed mode)
npm run test:mcp:headed

# Debug mode
npm run test:mcp:debug
```

### Python Integration
```bash
# Using the Python runner
python tests/run_playwright_mcp_tests.py

# With options
python tests/run_playwright_mcp_tests.py --type e2e --headed
python tests/run_playwright_mcp_tests.py --type visual --project chromium-desktop
```

## Test Fixtures

### mcpUtils
Provides utility functions for MCP integration:
```javascript
const { test, expect } = require('./fixtures/mcp-fixtures');

test('example test', async ({ mcpUtils, mcpPage }) => {
  await mcpUtils.waitForPlotlyGraph(mcpPage);
  const screenshot = await mcpUtils.takeScreenshot(mcpPage, 'test-state');
});
```

### mcpContext
Browser context with MCP settings:
```javascript
test('context test', async ({ mcpContext }) => {
  const page = await mcpContext.newPage();
  // Context has network interception, console monitoring enabled
});
```

### testFiles
Provides test data files:
```javascript
test('file upload', async ({ mcpPage, testFiles }) => {
  await mcpPage.setInputFiles('input[type="file"]', testFiles.csv);
});
```

### visualTester
Visual regression testing:
```javascript
test('visual test', async ({ visualTester }) => {
  await visualTester.waitForPlotlyGraph();
  const result = await visualTester.compareScreenshot('dashboard');
  expect(result.success).toBe(true);
});
```

## Environment Variables

### Core Settings
- `BASE_URL`: Application URL (default: http://localhost:8050)
- `NAVIGATION_TIMEOUT`: Page load timeout (default: 30000ms)
- `ACTION_TIMEOUT`: Element interaction timeout (default: 10000ms)

### MCP-Specific
- `MCP_USER_AGENT`: Custom user agent for test identification
- `MCP_ENABLE_HAR_RECORDING`: Enable network session recording
- `MCP_ENABLE_VIDEO_RECORDING`: Enable test video capture

### Performance Thresholds
- `LOAD_TIME_THRESHOLD`: Maximum acceptable load time (default: 5000ms)
- `RENDER_TIME_THRESHOLD`: Maximum render time (default: 2000ms)
- `PLOTLY_LOAD_THRESHOLD`: Plotly-specific load threshold (default: 3000ms)

## Custom Matchers

### toHavePlotlyData
Validates Plotly graph data structure:
```javascript
expect(plotlyElement).toHavePlotlyData();
```

### toBeInViewport
Checks element visibility:
```javascript
expect(element).toBeInViewport();
```

### toMeetPerformanceThresholds
Performance validation:
```javascript
expect(metrics).toMeetPerformanceThresholds({
  loadTime: 3000,
  renderTime: 1500
});
```

## Reporting

### Generated Reports
- **HTML Report**: Interactive test results with screenshots/videos
- **JSON Report**: Machine-readable test results
- **JUnit Report**: CI/CD integration format
- **HAR Files**: Complete network session logs
- **Performance Metrics**: Load and render time statistics

### Report Locations
- `tests/reports/playwright-report/`: HTML reports
- `tests/reports/screenshots/`: Test screenshots
- `tests/reports/videos/`: Test execution videos
- `tests/reports/network/`: Network logs and HAR files

## Integration with MELD Visualizer

### Dash-Specific Features
- **Callback mocking**: Simulates Dash server responses
- **Component state tracking**: Monitors Dash component updates
- **Upload handling**: Processes CSV and G-code file uploads
- **Tab navigation**: Tests multi-tab interface behavior

### Plotly Integration
- **3D graph validation**: Ensures proper 3D visualization rendering
- **Interaction testing**: Zoom, pan, rotate functionality
- **Data binding verification**: Confirms data-to-visualization mapping
- **Animation handling**: Manages dynamic graph updates

## Best Practices

### Test Structure
1. Use fixtures for consistent setup
2. Implement page object patterns for reusability
3. Separate test data from test logic
4. Use meaningful test descriptions

### Performance
1. Run tests in parallel where possible
2. Use browser contexts efficiently
3. Clean up resources after tests
4. Monitor test execution times

### Reliability
1. Wait for elements properly
2. Handle dynamic content with appropriate waits
3. Use stable selectors
4. Implement retry logic for flaky tests

### Maintenance
1. Keep screenshots and baselines updated
2. Review and update thresholds regularly
3. Monitor test execution metrics
4. Update dependencies consistently

## Troubleshooting

### Common Issues
1. **Timeouts**: Increase timeout values in test.env
2. **Visual differences**: Update snapshots with --update-snapshots
3. **Network issues**: Check HAR files in reports/network/
4. **Performance failures**: Review metrics in test reports

### Debug Mode
Run tests with debug flag to:
- Step through test execution
- Inspect page state
- Modify selectors interactively
- Analyze network requests

### Logging
Enable detailed logging by setting:
```bash
ENABLE_DEBUG_LOGS=true
ENABLE_NETWORK_LOGGING=true
ENABLE_CONSOLE_LOGGING=true
```

This configuration provides a robust foundation for comprehensive testing of the MELD Visualizer application using Playwright MCP functions.