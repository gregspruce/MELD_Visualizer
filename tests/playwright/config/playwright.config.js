// @ts-check
const { defineConfig, devices } = require('@playwright/test');
const path = require('path');
const dotenv = require('dotenv');

// Load environment variables
dotenv.config({ path: path.join(__dirname, 'test.env') });

/**
 * Playwright MCP Configuration for MELD Visualizer Dash Application
 * Optimized for testing with Playwright MCP functions
 * @see https://playwright.dev/docs/test-configuration
 */
module.exports = defineConfig({
  testDir: '../',
  /* Run tests in files in parallel */
  fullyParallel: true,
  /* Fail the build on CI if you accidentally left test.only in the source code. */
  forbidOnly: !!process.env.CI,
  /* Retry on CI only */
  retries: process.env.CI ? 2 : 0,
  /* Opt out of parallel tests on CI. */
  workers: process.env.CI ? 1 : undefined,
  /* Reporter to use. See https://playwright.dev/docs/test-reporters */
  reporter: [
    ['html', { outputFolder: '../reports/playwright-report' }],
    ['json', { outputFile: '../reports/test-results.json' }],
    ['junit', { outputFile: '../reports/junit-results.xml' }]
  ],
  /* Shared settings for all the projects below. See https://playwright.dev/docs/api/class-testoptions. */
  use: {
    /* Base URL to use in actions like `await page.goto('/')`. */
    baseURL: process.env.BASE_URL || 'http://localhost:8050',
    /* Collect trace when retrying the failed test. See https://playwright.dev/docs/trace-viewer */
    trace: process.env.TRACE_MODE || 'on-first-retry',
    /* Take screenshot on failure */
    screenshot: process.env.SCREENSHOT_MODE || 'only-on-failure',
    /* Record video on failure */
    video: process.env.VIDEO_MODE || 'retain-on-failure',
    /* Global timeout for each test */
    actionTimeout: parseInt(process.env.ACTION_TIMEOUT) || 10000,
    /* Global timeout for navigation */
    navigationTimeout: parseInt(process.env.NAVIGATION_TIMEOUT) || 30000,
    /* MCP-specific browser context configuration */
    viewport: { width: 1920, height: 1080 },
    /* User agent for MCP browser automation */
    userAgent: 'MELD-Visualizer-Test-Agent/1.0',
    /* Locale for consistent testing */
    locale: 'en-US',
    /* Timezone for consistent testing */
    timezoneId: 'America/New_York',
    /* Permissions for file upload testing */
    permissions: ['clipboard-read', 'clipboard-write'],
    /* Ignore HTTPS errors for local testing */
    ignoreHTTPSErrors: true,
    /* Extra HTTP headers for MCP requests */
    extraHTTPHeaders: {
      'X-Test-Framework': 'Playwright-MCP',
      'X-App-Under-Test': 'MELD-Visualizer'
    }
  },

  /* Configure projects for major browsers - MCP optimized */
  projects: [
    {
      name: 'chromium-desktop',
      use: { 
        ...devices['Desktop Chrome'],
        launchOptions: {
          args: [
            '--disable-web-security',
            '--disable-features=VizDisplayCompositor',
            '--disable-dev-shm-usage',
            '--no-sandbox'
          ]
        }
      },
    },
    {
      name: 'firefox-desktop',
      use: { 
        ...devices['Desktop Firefox'],
        launchOptions: {
          firefoxUserPrefs: {
            'media.navigator.streams.fake': true,
            'media.navigator.permission.disabled': true
          }
        }
      },
    },
    {
      name: 'webkit-desktop',
      use: { 
        ...devices['Desktop Safari'],
        launchOptions: {
          args: ['--disable-web-security']
        }
      },
    },
    /* Mobile testing for responsive design */
    {
      name: 'mobile-chrome',
      use: { 
        ...devices['Pixel 5'],
        isMobile: true,
        hasTouch: true
      },
    },
    {
      name: 'mobile-safari',
      use: { 
        ...devices['iPhone 12'],
        isMobile: true,
        hasTouch: true
      },
    },
    /* High-resolution testing for detailed visualizations */
    {
      name: 'high-dpi',
      use: {
        ...devices['Desktop Chrome'],
        viewport: { width: 2560, height: 1440 },
        deviceScaleFactor: 2,
      },
    }
  ],

  /* Global setup and teardown */
  globalSetup: require.resolve('./global-setup.js'),
  globalTeardown: require.resolve('./global-teardown.js'),

  /* Run your local dev server before starting the tests */
  webServer: {
    command: 'python -m meld_visualizer',
    url: 'http://localhost:8050',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
    env: {
      NODE_ENV: 'test',
    },
  },
  
  /* Output directories */
  outputDir: '../reports/test-results',
});