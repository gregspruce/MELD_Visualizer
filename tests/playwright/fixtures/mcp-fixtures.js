/**
 * Playwright MCP Test Fixtures for MELD Visualizer
 * Custom fixtures that integrate with Playwright MCP functions
 */

const { test as base, expect } = require('@playwright/test');
const { PlaywrightMCPUtils } = require('../config/mcp-utils');
const path = require('path');
const fs = require('fs').promises;

/**
 * Extended test with MCP-specific fixtures
 */
const test = base.extend({
  /**
   * MCP Utils fixture - provides utility functions for MCP integration
   */
  mcpUtils: async ({}, use) => {
    const utils = new PlaywrightMCPUtils();
    await use(utils);
  },

  /**
   * MCP Context fixture - creates browser context with MCP settings
   */
  mcpContext: async ({ browser, mcpUtils }, use) => {
    const context = await mcpUtils.createMCPContext(browser, {
      recordVideo: {
        dir: process.env.VIDEOS_DIR || '../reports/videos/',
        size: { 
          width: parseInt(process.env.VIDEO_SIZE_WIDTH) || 1920, 
          height: parseInt(process.env.VIDEO_SIZE_HEIGHT) || 1080 
        }
      }
    });
    
    await use(context);
    await context.close();
  },

  /**
   * MCP Page fixture - creates page with MELD Visualizer ready state
   */
  mcpPage: async ({ mcpContext, mcpUtils }, use) => {
    const page = await mcpContext.newPage();
    
    // Navigate to MELD Visualizer
    await page.goto('/');
    
    // Wait for Dash app to be ready
    if (process.env.WAIT_FOR_DASH_READY === 'true') {
      await page.waitForSelector('[data-testid="app-container"], .dash-app-content, #app', { 
        timeout: parseInt(process.env.NAVIGATION_TIMEOUT) || 30000 
      });
      
      // Wait for initial JavaScript to load
      await page.waitForFunction(() => {
        return window.dash_clientside && window.Plotly;
      }, { timeout: 15000 });
    }
    
    await use(page);
    
    // Export logs after test
    const logs = mcpUtils.exportLogs();
    if (logs.summary.consoleErrors > 0 || logs.summary.networkRequests === 0) {
      console.log('📊 Test logs:', JSON.stringify(logs.summary, null, 2));
    }
    
    await page.close();
  },

  /**
   * File upload fixture - handles test file uploads
   */
  testFiles: async ({}, use) => {
    const testDataDir = path.resolve(__dirname, process.env.TEST_DATA_DIR || 'test_data');
    
    const createTestFile = async (filename, content) => {
      const filePath = path.join(testDataDir, filename);
      await fs.mkdir(testDataDir, { recursive: true });
      await fs.writeFile(filePath, content);
      return filePath;
    };
    
    const files = {
      csv: await createTestFile('test_meld_data.csv', 
        'X,Y,Z,Temperature,Layer\n1,2,3,250,1\n4,5,6,260,1\n7,8,9,255,2'
      ),
      gcode: await createTestFile('test_toolpath.nc',
        'G21\nG90\nG1 X10 Y10 Z1 F1500\nG1 X20 Y20 Z2\nM2'
      ),
      large_csv: await createTestFile('large_test_data.csv',
        Array.from({length: 1000}, (_, i) => `${i},${i*2},${i*3},${250+i%50},${Math.floor(i/100)}`).join('\n')
      )
    };
    
    await use(files);
    
    // Cleanup test files
    try {
      await fs.rm(testDataDir, { recursive: true, force: true });
    } catch (error) {
      console.warn('Failed to cleanup test files:', error.message);
    }
  },

  /**
   * Performance monitoring fixture
   */
  performanceMonitor: async ({ mcpPage, mcpUtils }, use) => {
    const metrics = {
      start: Date.now(),
      checkpoints: [],
      mark: (name) => {
        metrics.checkpoints.push({
          name,
          timestamp: Date.now(),
          elapsed: Date.now() - metrics.start
        });
      },
      getMetrics: async () => {
        return await mcpUtils.getPerformanceMetrics(mcpPage);
      }
    };
    
    await use(metrics);
    
    // Log performance summary
    const finalMetrics = await metrics.getMetrics();
    if (finalMetrics.loadTime > parseInt(process.env.LOAD_TIME_THRESHOLD) || 5000) {
      console.warn(`⚠️  Slow load time: ${finalMetrics.loadTime}ms`);
    }
  },

  /**
   * Visual testing fixture with screenshot comparison
   */
  visualTester: async ({ mcpPage, mcpUtils }, use, testInfo) => {
    const visual = {
      takeScreenshot: async (name, options = {}) => {
        return await mcpUtils.takeScreenshot(mcpPage, `${testInfo.title}-${name}`, options);
      },
      
      compareScreenshot: async (name, options = {}) => {
        const result = await mcpUtils.compareScreenshot(mcpPage, `${testInfo.title}-${name}`, options);
        if (!result.success) {
          console.warn(`📸 Visual diff detected for ${name}:`, result.error);
        }
        return result;
      },
      
      waitForPlotlyGraph: async (selector = '.js-plotly-plot') => {
        await mcpUtils.waitForPlotlyGraph(mcpPage, selector);
      }
    };
    
    await use(visual);
  },

  /**
   * Network mocking fixture
   */
  networkMocker: async ({ mcpContext }, use) => {
    const mocker = {
      mockDashCallback: async (outputId, mockData) => {
        await mcpContext.route('**/_dash-update-component', async (route) => {
          await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
              multi: true,
              response: { [outputId]: mockData }
            })
          });
        });
      },
      
      mockFileUpload: async (response = { success: true }) => {
        await mcpContext.route('**/upload*', async (route) => {
          await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify(response)
          });
        });
      },
      
      mockApiError: async (endpoint, errorCode = 500) => {
        await mcpContext.route(`**${endpoint}**`, async (route) => {
          await route.fulfill({
            status: errorCode,
            contentType: 'application/json',
            body: JSON.stringify({ error: 'Test error condition' })
          });
        });
      }
    };
    
    await use(mocker);
  },

  /**
   * Console monitoring fixture
   */
  consoleMonitor: async ({ mcpPage, mcpUtils }, use) => {
    const monitor = {
      errors: [],
      warnings: [],
      
      getErrors: () => monitor.errors,
      getWarnings: () => monitor.warnings,
      
      expectNoErrors: () => {
        expect(monitor.errors).toHaveLength(0);
      },
      
      expectNoWarnings: () => {
        expect(monitor.warnings).toHaveLength(0);
      }
    };
    
    // Set up console monitoring
    mcpPage.on('console', (msg) => {
      if (msg.type() === 'error') {
        monitor.errors.push({
          text: msg.text(),
          timestamp: new Date().toISOString(),
          url: mcpPage.url()
        });
      } else if (msg.type() === 'warning') {
        monitor.warnings.push({
          text: msg.text(),
          timestamp: new Date().toISOString(),
          url: mcpPage.url()
        });
      }
    });
    
    await use(monitor);
  }
});

/**
 * Custom expect matchers for MELD Visualizer testing
 */
expect.extend({
  /**
   * Check if Plotly graph has expected data structure
   */
  toHavePlotlyData(received, expectedStructure) {
    const pass = received && 
                  received._fullData && 
                  Array.isArray(received._fullData) &&
                  received._fullData.length > 0;
    
    return {
      message: () => `expected ${received} to have valid Plotly data structure`,
      pass
    };
  },

  /**
   * Check if element is within viewport
   */
  async toBeInViewport(elementHandle) {
    const isInViewport = await elementHandle.evaluate((element) => {
      const rect = element.getBoundingClientRect();
      return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= window.innerHeight &&
        rect.right <= window.innerWidth
      );
    });

    return {
      message: () => `expected element to be in viewport`,
      pass: isInViewport
    };
  },

  /**
   * Check performance metrics against thresholds
   */
  toMeetPerformanceThresholds(metrics, thresholds = {}) {
    const defaultThresholds = {
      loadTime: parseInt(process.env.LOAD_TIME_THRESHOLD) || 5000,
      renderTime: parseInt(process.env.RENDER_TIME_THRESHOLD) || 2000
    };
    
    const finalThresholds = { ...defaultThresholds, ...thresholds };
    const failures = [];
    
    if (metrics.loadTime > finalThresholds.loadTime) {
      failures.push(`Load time ${metrics.loadTime}ms exceeds threshold ${finalThresholds.loadTime}ms`);
    }
    
    if (metrics.firstContentfulPaint > finalThresholds.renderTime) {
      failures.push(`Render time ${metrics.firstContentfulPaint}ms exceeds threshold ${finalThresholds.renderTime}ms`);
    }
    
    return {
      message: () => `Performance issues: ${failures.join(', ')}`,
      pass: failures.length === 0
    };
  }
});

module.exports = { test, expect };