// global-setup.js - Playwright MCP Global Setup for MELD Visualizer
const { chromium } = require('@playwright/test');
const { PlaywrightMCPUtils } = require('./mcp-utils');
const fs = require('fs').promises;
const path = require('path');

async function globalSetup(config) {
  console.log('🚀 Starting Playwright MCP global setup for MELD Visualizer tests...');

  // Initialize MCP utilities
  const mcpUtils = new PlaywrightMCPUtils();

  // Ensure report directories exist
  await ensureDirectories();

  // Launch browser with MCP configuration
  const browser = await chromium.launch({
    headless: process.env.HEADLESS === 'true',
    args: [
      '--disable-web-security',
      '--disable-features=VizDisplayCompositor',
      '--disable-dev-shm-usage',
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-background-timer-throttling',
      '--disable-backgrounding-occluded-windows',
      '--disable-renderer-backgrounding'
    ]
  });

  // Create MCP context for setup verification
  const context = await mcpUtils.createMCPContext(browser, {
    recordVideo: {
      dir: process.env.VIDEOS_DIR || '../reports/videos/',
      size: { width: 1920, height: 1080 }
    }
  });

  const page = await context.newPage();

  try {
    console.log('⏳ Waiting for MELD Visualizer to be available...');

    // Navigate with MCP settings
    await page.goto(process.env.BASE_URL || 'http://localhost:8050', {
      waitUntil: 'networkidle',
      timeout: parseInt(process.env.NAVIGATION_TIMEOUT) || 30000
    });

    // Verify the Dash app loaded correctly
    console.log('🔍 Verifying Dash application structure...');
    await page.waitForSelector([
      '[data-testid="app-container"]',
      '.dash-app-content',
      '#app',
      '.container-fluid'
    ].join(', '), { timeout: 30000 });

    // Wait for critical JavaScript libraries
    console.log('📚 Waiting for JavaScript libraries to load...');
    await page.waitForFunction(() => {
      return window.dash_clientside &&
             window.Plotly &&
             window.dash_clientside.callback_context !== undefined;
    }, { timeout: 15000 });

    // Verify Plotly is properly initialized
    const plotlyReady = await page.evaluate(() => {
      return typeof window.Plotly === 'object' &&
             typeof window.Plotly.newPlot === 'function' &&
             typeof window.Plotly.react === 'function';
    });

    if (!plotlyReady) {
      throw new Error('Plotly library not properly initialized');
    }

    console.log('✅ MELD Visualizer is ready for MCP testing');

    // Take comprehensive setup screenshots
    await page.screenshot({
      path: path.resolve('../reports/mcp-global-setup-full.png'),
      fullPage: true
    });

    await page.screenshot({
      path: path.resolve('../reports/mcp-global-setup-viewport.png'),
      fullPage: false
    });

    // Capture initial performance metrics
    const initialMetrics = await mcpUtils.getPerformanceMetrics(page);
    console.log('📊 Initial performance metrics:', {
      loadTime: `${initialMetrics.loadTime}ms`,
      firstPaint: `${initialMetrics.firstPaint}ms`,
      firstContentfulPaint: `${initialMetrics.firstContentfulPaint}ms`
    });

    // Test file upload capability
    console.log('📁 Testing file upload capability...');
    const fileInputs = await page.locator('input[type="file"]').count();
    if (fileInputs > 0) {
      console.log(`✅ Found ${fileInputs} file input(s) for upload testing`);
    }

    // Test navigation elements
    console.log('🧭 Verifying navigation elements...');
    const tabCount = await page.locator('.nav-tabs .nav-link, dcc-tabs .tab').count();
    if (tabCount > 0) {
      console.log(`✅ Found ${tabCount} navigation tab(s)`);
    }

    // Export setup logs
    const setupLogs = mcpUtils.exportLogs();
    await fs.writeFile(
      path.resolve('../reports/mcp-global-setup-logs.json'),
      JSON.stringify(setupLogs, null, 2)
    );

    // Store global test state
    const globalState = {
      timestamp: new Date().toISOString(),
      baseURL: process.env.BASE_URL || 'http://localhost:8050',
      performanceMetrics: initialMetrics,
      setupSuccess: true,
      librariesLoaded: {
        dash: !!await page.evaluate(() => window.dash_clientside),
        plotly: plotlyReady,
        jquery: !!await page.evaluate(() => window.jQuery || window.$)
      }
    };

    await fs.writeFile(
      path.resolve('../reports/mcp-global-state.json'),
      JSON.stringify(globalState, null, 2)
    );

    console.log('💾 Global state and logs saved to reports directory');

  } catch (error) {
    console.error('❌ Failed to verify MELD Visualizer is running:', error.message);

    // Capture error state
    try {
      await page.screenshot({
        path: path.resolve('../reports/mcp-global-setup-error.png'),
        fullPage: true
      });

      const errorLogs = mcpUtils.exportLogs();
      await fs.writeFile(
        path.resolve('../reports/mcp-global-setup-error-logs.json'),
        JSON.stringify({ error: error.message, logs: errorLogs }, null, 2)
      );
    } catch (screenshotError) {
      console.error('Failed to capture error state:', screenshotError.message);
    }

    throw error;
  } finally {
    await context.close();
    await browser.close();
  }

  console.log('🎯 Playwright MCP global setup complete');
}

/**
 * Ensure all required directories exist
 */
async function ensureDirectories() {
  const directories = [
    '../reports',
    '../reports/screenshots',
    '../reports/videos',
    '../reports/network',
    '../visual/expected',
    '../visual/diffs',
    '../fixtures/test_data'
  ];

  for (const dir of directories) {
    try {
      await fs.mkdir(path.resolve(__dirname, dir), { recursive: true });
    } catch (error) {
      if (error.code !== 'EEXIST') {
        console.warn(`Warning: Could not create directory ${dir}:`, error.message);
      }
    }
  }

  console.log('📁 Directory structure verified');
}

module.exports = globalSetup;
