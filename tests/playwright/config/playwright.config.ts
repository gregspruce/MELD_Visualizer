/**
 * TypeScript Playwright Configuration for MELD Visualizer
 * Type-safe configuration with MCP integration
 */

import { defineConfig, devices, PlaywrightTestConfig } from '@playwright/test';
import { config } from 'dotenv';
import { resolve } from 'path';
import type { TestTypes } from '../types';

// Load environment variables
config({ path: resolve(__dirname, 'test.env') });

/**
 * Type-safe environment variable parsing
 */
const getEnvNumber = (key: string, defaultValue: number): number => {
  const value = process.env[key];
  return value ? parseInt(value, 10) : defaultValue;
};

const getEnvBoolean = (key: string, defaultValue: boolean): boolean => {
  const value = process.env[key];
  return value ? value.toLowerCase() === 'true' : defaultValue;
};

const getEnvString = <T extends string>(
  key: string, 
  defaultValue: T, 
  allowedValues?: ReadonlyArray<T>
): T => {
  const value = process.env[key] as T;
  if (!value) return defaultValue;
  if (allowedValues && !allowedValues.includes(value)) {
    console.warn(`Invalid value for ${key}: ${value}. Using default: ${defaultValue}`);
    return defaultValue;
  }
  return value;
};

/**
 * Base test configuration
 */
const baseTestConfig: TestTypes.MELDTestConfig = {
  baseURL: getEnvString('BASE_URL', 'http://localhost:8050'),
  timeout: {
    navigation: getEnvNumber('NAVIGATION_TIMEOUT', 30_000),
    action: getEnvNumber('ACTION_TIMEOUT', 10_000),
    assertion: 5_000,
    plotlyRender: 15_000,
    fileUpload: 30_000,
    dashCallback: 10_000,
  },
  viewport: {
    width: 1920,
    height: 1080,
  },
  screenshots: {
    mode: getEnvString('SCREENSHOT_MODE', 'only-on-failure', ['off', 'only-on-failure', 'on']),
    fullPage: true,
    threshold: 0.2,
    animations: 'disabled',
    caret: 'hide',
  },
  performance: {
    loadTime: getEnvNumber('LOAD_TIME_THRESHOLD', 5_000),
    renderTime: getEnvNumber('RENDER_TIME_THRESHOLD', 2_000),
    interactionTime: 100,
    memoryUsage: 100_000_000,
    cpuUsage: 80,
    networkRequests: 50,
  },
  files: {
    testDataDir: resolve(__dirname, '../fixtures/test_data'),
    uploadDir: resolve(__dirname, '../uploads'),
    downloadDir: resolve(__dirname, '../downloads'),
    reportDir: resolve(__dirname, '../../reports'),
    maxFileSize: 10_000_000,
    allowedExtensions: ['.csv', '.tsv', '.nc', '.gcode'],
  },
  mcp: {
    enabled: true,
    serverUrl: 'http://localhost:3000',
    timeout: 10_000,
    retries: 2,
    mockMode: getEnvBoolean('MCP_MOCK_MODE', false),
  },
};

/**
 * Playwright configuration with full type safety
 */
const playwrightConfig: PlaywrightTestConfig = defineConfig({
  testDir: '../',
  
  // Execution settings
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  
  // Reporting configuration
  reporter: [
    ['html', { 
      outputFolder: resolve(baseTestConfig.files.reportDir, 'playwright-report'),
      open: 'never'
    }],
    ['json', { 
      outputFile: resolve(baseTestConfig.files.reportDir, 'test-results.json')
    }],
    ['junit', { 
      outputFile: resolve(baseTestConfig.files.reportDir, 'junit-results.xml')
    }],
    ['line'],
  ],
  
  // Global test configuration
  use: {
    // Base URL
    baseURL: baseTestConfig.baseURL,
    
    // Tracing and debugging
    trace: getEnvString('TRACE_MODE', 'on-first-retry', [
      'on-first-retry', 'on-all-retries', 'off', 'on', 'retain-on-failure'
    ]),
    screenshot: baseTestConfig.screenshots.mode,
    video: getEnvString('VIDEO_MODE', 'retain-on-failure', [
      'off', 'on', 'retain-on-failure', 'on-first-retry'
    ]),
    
    // Timeouts
    actionTimeout: baseTestConfig.timeout.action,
    navigationTimeout: baseTestConfig.timeout.navigation,
    
    // Browser context settings
    viewport: baseTestConfig.viewport,
    userAgent: 'MELD-Visualizer-Test-Agent/1.0',
    locale: 'en-US',
    timezoneId: 'America/New_York',
    
    // Permissions and security
    permissions: ['clipboard-read', 'clipboard-write'],
    ignoreHTTPSErrors: true,
    
    // HTTP headers for identification
    extraHTTPHeaders: {
      'X-Test-Framework': 'Playwright-MCP-TypeScript',
      'X-App-Under-Test': 'MELD-Visualizer',
      'X-Test-Session': `test-${Date.now()}`,
    },
  },

  // Browser projects with type safety
  projects: [
    // Desktop browsers
    {
      name: 'chromium-desktop',
      use: { 
        ...devices['Desktop Chrome'],
        launchOptions: {
          args: [
            '--disable-web-security',
            '--disable-features=VizDisplayCompositor',
            '--disable-dev-shm-usage',
            '--no-sandbox',
            '--disable-background-timer-throttling',
            '--disable-backgrounding-occluded-windows',
            '--disable-renderer-backgrounding',
          ],
        },
      },
    },
    {
      name: 'firefox-desktop',
      use: { 
        ...devices['Desktop Firefox'],
        launchOptions: {
          firefoxUserPrefs: {
            'media.navigator.streams.fake': true,
            'media.navigator.permission.disabled': true,
            'dom.webnotifications.enabled': false,
            'dom.push.enabled': false,
          },
        },
      },
    },
    {
      name: 'webkit-desktop',
      use: { 
        ...devices['Desktop Safari'],
        launchOptions: {
          args: [
            '--disable-web-security',
            '--allow-running-insecure-content',
          ],
        },
      },
    },

    // Mobile testing for responsive design
    {
      name: 'mobile-chrome',
      use: { 
        ...devices['Pixel 5'],
        isMobile: true,
        hasTouch: true,
      },
    },
    {
      name: 'mobile-safari',
      use: { 
        ...devices['iPhone 12'],
        isMobile: true,
        hasTouch: true,
      },
    },

    // High-resolution testing for detailed visualizations
    {
      name: 'high-dpi',
      use: {
        ...devices['Desktop Chrome'],
        viewport: { width: 2560, height: 1440 },
        deviceScaleFactor: 2,
      },
    },

    // Accessibility testing
    {
      name: 'accessibility',
      use: {
        ...devices['Desktop Chrome'],
        // Force reduced motion for accessibility testing
        reducedMotion: 'reduce',
      },
    },
  ],

  // Global setup and teardown
  globalSetup: require.resolve('./global-setup.ts'),
  globalTeardown: require.resolve('./global-teardown.ts'),

  // Development server configuration
  webServer: {
    command: 'python -m meld_visualizer',
    url: baseTestConfig.baseURL,
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
    env: {
      NODE_ENV: 'test',
      DASH_ENV: 'test',
      PYTHONPATH: process.env.PYTHONPATH || '',
    },
    ignoreHTTPSErrors: true,
  },
  
  // Output configuration
  outputDir: resolve(baseTestConfig.files.reportDir, 'test-results'),
  
  // Expect configuration
  expect: {
    // Visual comparisons
    threshold: baseTestConfig.screenshots.threshold,
    
    // Animation handling
    toHaveScreenshot: {
      threshold: baseTestConfig.screenshots.threshold,
      animations: baseTestConfig.screenshots.animations,
      caret: baseTestConfig.screenshots.caret,
    },
    
    toMatchSnapshot: {
      threshold: baseTestConfig.screenshots.threshold,
      animations: baseTestConfig.screenshots.animations,
    },
  },

  // Test metadata
  metadata: {
    testFramework: 'Playwright with TypeScript',
    application: 'MELD Visualizer',
    version: '1.0.0',
    environment: process.env.NODE_ENV || 'test',
    mcp: baseTestConfig.mcp.enabled,
  },
});

// Export both the Playwright config and base test config for use in tests
export default playwrightConfig;
export { baseTestConfig };

// Type-safe configuration validation
export function validateConfig(config: TestTypes.MELDTestConfig): boolean {
  try {
    // Validate URLs
    new URL(config.baseURL);
    
    // Validate timeouts are positive
    Object.values(config.timeout).forEach(timeout => {
      if (timeout <= 0) throw new Error(`Invalid timeout: ${timeout}`);
    });
    
    // Validate viewport dimensions
    if (config.viewport.width <= 0 || config.viewport.height <= 0) {
      throw new Error('Invalid viewport dimensions');
    }
    
    // Validate thresholds
    Object.values(config.performance).forEach(threshold => {
      if (threshold <= 0) throw new Error(`Invalid performance threshold: ${threshold}`);
    });
    
    return true;
  } catch (error) {
    console.error('Configuration validation failed:', error);
    return false;
  }
}

// Validate configuration on import
if (!validateConfig(baseTestConfig)) {
  throw new Error('Invalid test configuration');
}