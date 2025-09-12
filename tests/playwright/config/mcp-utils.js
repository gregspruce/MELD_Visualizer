/**
 * Playwright MCP Utilities for MELD Visualizer
 * This module provides wrapper functions and utilities for Playwright MCP integration
 */

class PlaywrightMCPUtils {
  constructor() {
    this.baseURL = process.env.BASE_URL || 'http://localhost:8050';
    this.screenshotDir = '../reports/screenshots';
    this.networkLogs = [];
    this.consoleLogs = [];
  }

  /**
   * Initialize browser context with MCP-specific settings
   * @param {Object} browser - Playwright browser instance
   * @param {Object} options - Additional context options
   */
  async createMCPContext(browser, options = {}) {
    const context = await browser.newContext({
      viewport: { width: 1920, height: 1080 },
      userAgent: 'MELD-Visualizer-Test-Agent/1.0',
      locale: 'en-US',
      timezoneId: 'America/New_York',
      permissions: ['clipboard-read', 'clipboard-write'],
      ignoreHTTPSErrors: true,
      recordVideo: {
        dir: '../reports/videos/',
        size: { width: 1920, height: 1080 }
      },
      recordHar: {
        path: '../reports/network/har-logs.har',
        mode: 'full'
      },
      ...options
    });

    // Set up network interception
    await this.setupNetworkInterception(context);

    // Set up console monitoring
    await this.setupConsoleMonitoring(context);

    return context;
  }

  /**
   * Set up network request/response interception for API mocking
   * @param {Object} context - Browser context
   */
  async setupNetworkInterception(context) {
    // Intercept all network requests
    await context.route('**/*', async (route, request) => {
      const url = request.url();
      const method = request.method();
      const headers = request.headers();

      // Log network activity
      this.networkLogs.push({
        timestamp: new Date().toISOString(),
        method,
        url,
        headers,
        type: 'request'
      });

      // Handle specific API endpoints for MELD Visualizer
      if (url.includes('/_dash-update-component')) {
        // Mock Dash callback responses for testing
        await this.handleDashCallback(route, request);
      } else if (url.includes('/upload')) {
        // Handle file upload requests
        await this.handleFileUpload(route, request);
      } else {
        // Continue with normal request
        const response = await route.fetch();

        // Log response
        this.networkLogs.push({
          timestamp: new Date().toISOString(),
          method,
          url,
          status: response.status(),
          type: 'response'
        });

        await route.fulfill({ response });
      }
    });
  }

  /**
   * Set up console log monitoring for error detection
   * @param {Object} context - Browser context
   */
  async setupConsoleMonitoring(context) {
    context.on('page', (page) => {
      // Monitor console messages
      page.on('console', (msg) => {
        const logEntry = {
          timestamp: new Date().toISOString(),
          type: msg.type(),
          text: msg.text(),
          url: page.url()
        };

        this.consoleLogs.push(logEntry);

        // Flag errors and warnings
        if (msg.type() === 'error' || msg.type() === 'warning') {
          console.log(`🚨 ${msg.type().toUpperCase()}: ${msg.text()}`);
        }
      });

      // Monitor uncaught exceptions
      page.on('pageerror', (error) => {
        this.consoleLogs.push({
          timestamp: new Date().toISOString(),
          type: 'pageerror',
          text: error.message,
          stack: error.stack,
          url: page.url()
        });
        console.error('🔥 Page Error:', error.message);
      });

      // Monitor request failures
      page.on('requestfailed', (request) => {
        const failure = {
          timestamp: new Date().toISOString(),
          type: 'requestfailed',
          url: request.url(),
          failure: request.failure()?.errorText,
          method: request.method()
        };

        this.networkLogs.push(failure);
        console.error('🌐 Request Failed:', request.url(), request.failure()?.errorText);
      });
    });
  }

  /**
   * Handle Dash callback mocking for testing
   * @param {Object} route - Playwright route
   * @param {Object} request - Request object
   */
  async handleDashCallback(route, request) {
    const url = request.url();
    const postData = request.postData();

    // Parse the callback request
    let mockResponse = { multi: true, response: {} };

    try {
      if (postData) {
        const data = JSON.parse(postData);

        // Mock responses for common MELD Visualizer callbacks
        if (data.output && data.output.includes('graph-3d')) {
          // Mock 3D graph update
          mockResponse.response = {
            'graph-3d': {
              data: [{ type: 'scatter3d', x: [1, 2, 3], y: [1, 2, 3], z: [1, 2, 3] }],
              layout: { title: 'Test 3D Graph' }
            }
          };
        } else if (data.output && data.output.includes('data-table')) {
          // Mock data table update
          mockResponse.response = {
            'data-table': {
              data: [{ column1: 'test', column2: 'data' }],
              columns: [{ name: 'Column 1', id: 'column1' }]
            }
          };
        }
      }
    } catch (error) {
      console.warn('Failed to parse callback data:', error.message);
    }

    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(mockResponse)
    });
  }

  /**
   * Handle file upload mocking
   * @param {Object} route - Playwright route
   * @param {Object} request - Request object
   */
  async handleFileUpload(route, request) {
    // Mock successful file upload
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        success: true,
        filename: 'test_file.csv',
        size: 1024,
        message: 'File uploaded successfully'
      })
    });
  }

  /**
   * Take screenshot with comparison utilities
   * @param {Object} page - Playwright page
   * @param {string} name - Screenshot name
   * @param {Object} options - Screenshot options
   */
  async takeScreenshot(page, name, options = {}) {
    const screenshotPath = `${this.screenshotDir}/${name}-${Date.now()}.png`;

    const defaultOptions = {
      path: screenshotPath,
      fullPage: true,
      clip: null,
      ...options
    };

    await page.screenshot(defaultOptions);

    return {
      path: screenshotPath,
      name,
      timestamp: new Date().toISOString()
    };
  }

  /**
   * Visual comparison with threshold
   * @param {Object} page - Playwright page
   * @param {string} name - Screenshot name for comparison
   * @param {Object} options - Comparison options
   */
  async compareScreenshot(page, name, options = {}) {
    const { threshold = 0.2, clip = null } = options;

    try {
      await page.screenshot({
        path: `../visual/expected/${name}.png`,
        fullPage: true,
        clip,
        threshold
      });

      return { success: true, name };
    } catch (error) {
      return {
        success: false,
        name,
        error: error.message,
        diff: error.diff || null
      };
    }
  }

  /**
   * Wait for Plotly graph to be rendered
   * @param {Object} page - Playwright page
   * @param {string} selector - Graph container selector
   */
  async waitForPlotlyGraph(page, selector = '.js-plotly-plot') {
    await page.waitForSelector(selector, { timeout: 30000 });

    // Wait for Plotly to finish rendering
    await page.waitForFunction((sel) => {
      const element = document.querySelector(sel);
      return element && element._fullLayout && element._fullData;
    }, selector, { timeout: 30000 });

    // Additional wait for animations to complete
    await page.waitForTimeout(1000);
  }

  /**
   * Monitor performance metrics
   * @param {Object} page - Playwright page
   */
  async getPerformanceMetrics(page) {
    const metrics = await page.evaluate(() => {
      const navigation = performance.getEntriesByType('navigation')[0];
      const paint = performance.getEntriesByType('paint');

      return {
        loadTime: navigation ? navigation.loadEventEnd - navigation.fetchStart : 0,
        domContentLoaded: navigation ? navigation.domContentLoadedEventEnd - navigation.fetchStart : 0,
        firstPaint: paint.find(p => p.name === 'first-paint')?.startTime || 0,
        firstContentfulPaint: paint.find(p => p.name === 'first-contentful-paint')?.startTime || 0,
        timestamp: Date.now()
      };
    });

    return metrics;
  }

  /**
   * Export logs for debugging
   */
  exportLogs() {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const logData = {
      timestamp,
      network: this.networkLogs,
      console: this.consoleLogs,
      summary: {
        networkRequests: this.networkLogs.filter(l => l.type === 'request').length,
        networkResponses: this.networkLogs.filter(l => l.type === 'response').length,
        consoleErrors: this.consoleLogs.filter(l => l.type === 'error').length,
        consoleWarnings: this.consoleLogs.filter(l => l.type === 'warning').length
      }
    };

    return logData;
  }

  /**
   * Clear accumulated logs
   */
  clearLogs() {
    this.networkLogs = [];
    this.consoleLogs = [];
  }
}

module.exports = { PlaywrightMCPUtils };
