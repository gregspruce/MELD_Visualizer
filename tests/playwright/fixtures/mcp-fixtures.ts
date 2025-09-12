/**
 * Type-Safe Playwright MCP Test Fixtures for MELD Visualizer
 * Enhanced fixtures with comprehensive TypeScript support
 */

import { test as base, expect, Page, BrowserContext } from '@playwright/test';
import { PlaywrightMCPUtils } from '../config/mcp-utils';
import {
  HomePageObject,
  UploadPageObject,
  VisualizationPageObject,
  SettingsPageObject
} from '../utils/page-objects';
import { resolve, join } from 'path';
import { writeFile, mkdir, rm, readFile } from 'fs/promises';
import type {
  TestTypes,
  MELDData,
  DashComponents,
  PlotlyTypes,
  HomePage,
  UploadPage,
  VisualizationPage,
  SettingsPage
} from '../types';

/**
 * Type-safe selectors for MELD Visualizer
 */
const DEFAULT_SELECTORS: TestTypes.PageSelectors = {
  app: {
    container: '[data-testid="app-container"], .dash-app-content, #app',
    header: '[data-testid="header"], .app-header, header',
    footer: '[data-testid="footer"], .app-footer, footer',
    loading: '[data-testid="loading"], .loading, .dash-spinner',
    error: '[data-testid="error"], .error-message, .alert-danger'
  },
  upload: {
    dropzone: '[data-testid="upload-dropzone"], .upload-dropzone, #upload-area',
    fileInput: '[data-testid="file-input"], input[type="file"]',
    button: '[data-testid="upload-button"], .upload-button',
    progress: '[data-testid="upload-progress"], .progress-bar, progress',
    success: '[data-testid="upload-success"], .upload-success, .alert-success',
    error: '[data-testid="upload-error"], .upload-error, .alert-danger'
  },
  tabs: {
    container: '[data-testid="tabs"], .nav-tabs, .tabs-container',
    tab: (id: string) => `[data-testid="tab-${id}"], .nav-link[href*="${id}"], .tab[data-tab="${id}"]`,
    content: '[data-testid="tab-content"], .tab-content',
    active: '.active, [aria-selected="true"], .tab.active'
  },
  graph: {
    container: '[data-testid="graph-container"], .graph-container',
    plotly: '[data-testid="plotly-graph"], .js-plotly-plot, .plotly-graph-div',
    legend: '[data-testid="plotly-legend"], .legend, .js-legend',
    toolbar: '[data-testid="plotly-toolbar"], .modebar, .plotly-modebar',
    loading: '[data-testid="graph-loading"], .graph-loading'
  },
  controls: {
    themeToggle: '[data-testid="theme-toggle"], .theme-toggle, .dark-mode-toggle',
    exportButton: '[data-testid="export-button"], .export-button, .btn-export',
    resetButton: '[data-testid="reset-button"], .reset-button, .btn-reset',
    settingsButton: '[data-testid="settings-button"], .settings-button, .btn-settings'
  },
  table: {
    container: '[data-testid="data-table"], .data-table, .dash-table',
    header: '[data-testid="table-header"], .table-header, thead',
    row: '[data-testid="table-row"], .table-row, tbody tr',
    cell: '[data-testid="table-cell"], .table-cell, td',
    pagination: '[data-testid="table-pagination"], .table-pagination, .pagination'
  }
};

/**
 * Test data generator for MELD data
 */
class MELDTestDataGenerator {
  constructor(private config: TestTypes.TestDataGeneratorConfig) {}

  /**
   * Generate synthetic MELD data points
   */
  generateDataPoints(): MELDData.DataPoint[] {
    const points: MELDData.DataPoint[] = [];
    const { count, seed = 12345 } = this.config;

    // Simple seeded random generator for reproducible tests
    let random = this.createSeededRandom(seed);

    const baseDate = new Date('2024-01-15T10:00:00.000Z');

    for (let i = 0; i < count; i++) {
      const timestamp = new Date(baseDate.getTime() + i * 1000);

      points.push({
        Date: timestamp.toISOString().split('T')[0],
        Time: timestamp.toTimeString().split(' ')[0] + '.00',
        SpinVel: this.generateValue('SpinVel', random, 50, 150),
        SpinTrq: this.generateValue('SpinTrq', random, 2, 8),
        SpinPwr: this.generateValue('SpinPwr', random, 100, 1200),
        SpinSP: this.generateValue('SpinSP', random, 50, 150),
        FeedVel: this.generateValue('FeedVel', random, 5, 20),
        FeedPos: this.generateValue('FeedPos', random, 0, 100),
        FeedTrq: this.generateValue('FeedTrq', random, 1, 5),
        FRO: 100,
        PathVel: this.generateValue('PathVel', random, 10, 25),
        XPos: this.generateValue('XPos', random, 0, 50),
        XVel: this.generateValue('XVel', random, 0, 10),
        XTrq: this.generateValue('XTrq', random, 0, 5),
        YPos: this.generateValue('YPos', random, 0, 30),
        YVel: this.generateValue('YVel', random, 0, 10),
        YTrq: this.generateValue('YTrq', random, 0, 5),
        ZPos: this.generateValue('ZPos', random, 0, 10),
        ZVel: this.generateValue('ZVel', random, 0, 5),
        ZTrq: this.generateValue('ZTrq', random, 0, 3),
        Gcode: Math.floor(i / 10) + 10,
        Low: this.generateValue('Low', random, 20, 50),
        High: this.generateValue('High', random, 20, 50),
        Ktype1: this.generateValue('Ktype1', random, 200, 500),
        Ktype2: this.generateValue('Ktype2', random, 200, 500),
        Ktype3: this.generateValue('Ktype3', random, 200, 500),
        Ktype4: this.generateValue('Ktype4', random, 200, 500),
        O2: this.generateValue('O2', random, 0.18, 0.25),
        ToolTemp: this.generateValue('ToolTemp', random, 100, 200),
        Tool2Temp: this.generateValue('Tool2Temp', random, 50, 100)
      });
    }

    return points;
  }

  /**
   * Generate CSV content from data points
   */
  generateCSV(points: MELDData.DataPoint[]): string {
    if (points.length === 0) return '';

    const headers = Object.keys(points[0]);
    const csvLines = [
      headers.join(','),
      ...points.map(point =>
        headers.map(header => point[header as keyof MELDData.DataPoint]).join(',')
      )
    ];

    return csvLines.join('\n');
  }

  /**
   * Create seeded random number generator
   */
  private createSeededRandom(seed: number): () => number {
    return () => {
      seed = (seed * 9301 + 49297) % 233280;
      return seed / 233280;
    };
  }

  /**
   * Generate value with optional range and distribution
   */
  private generateValue(
    field: keyof MELDData.DataPoint,
    random: () => number,
    min: number,
    max: number
  ): number {
    const range = this.config.ranges?.[field];
    const actualMin = range ? range[0] : min;
    const actualMax = range ? range[1] : max;

    const distribution = this.config.distributions?.[field] || 'uniform';

    switch (distribution) {
      case 'normal':
        // Box-Muller transform for normal distribution
        const u1 = random();
        const u2 = random();
        const z0 = Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
        const mean = (actualMin + actualMax) / 2;
        const stdDev = (actualMax - actualMin) / 6; // 99.7% within range
        return Math.max(actualMin, Math.min(actualMax, mean + z0 * stdDev));

      case 'exponential':
        const lambda = 1 / ((actualMax - actualMin) / 2);
        return actualMin - Math.log(random()) / lambda;

      default: // uniform
        return actualMin + random() * (actualMax - actualMin);
    }
  }
}

/**
 * Extended test with comprehensive MCP fixtures
 */
export const test = base.extend<{
  // Core MCP fixtures
  mcpUtils: PlaywrightMCPUtils;
  mcpContext: BrowserContext;
  mcpPage: Page;

  // MELD-specific fixtures
  testFiles: TestTypes.TestFixtures;
  performanceMonitor: TestTypes.PerformanceMetrics;
  visualTester: {
    takeScreenshot: (name: string, options?: TestTypes.ScreenshotOptions) => Promise<TestTypes.ScreenshotResult>;
    compareScreenshot: (name: string, options?: TestTypes.VisualTestConfig) => Promise<TestTypes.VisualTestResult>;
    waitForPlotlyGraph: (selector?: string, options?: TestTypes.PlotlyWaitOptions) => Promise<void>;
  };
  networkMocker: {
    mockDashCallback: (outputId: string, mockData: unknown) => Promise<void>;
    mockFileUpload: (response?: Partial<TestTypes.FileUploadResponse>) => Promise<void>;
    mockApiError: (endpoint: string, errorCode?: number) => Promise<void>;
  };
  consoleMonitor: {
    errors: TestTypes.ConsoleLog[];
    warnings: TestTypes.ConsoleLog[];
    getErrors: () => TestTypes.ConsoleLog[];
    getWarnings: () => TestTypes.ConsoleLog[];
    expectNoErrors: () => void;
    expectNoWarnings: () => void;
  };

  // Page objects
  homePage: HomePage;
  uploadPage: UploadPage;
  visualizationPage: VisualizationPage;
  settingsPage: SettingsPage;
}>({
  /**
   * MCP Utils fixture with enhanced configuration
   */
  mcpUtils: async ({}, use, testInfo) => {
    const config: Partial<TestTypes.MELDTestConfig> = {
      baseURL: process.env.BASE_URL || 'http://localhost:8050',
      files: {
        testDataDir: resolve(__dirname, 'test_data'),
        uploadDir: resolve(__dirname, '../uploads'),
        downloadDir: resolve(__dirname, '../downloads'),
        reportDir: resolve(__dirname, '../../reports'),
        maxFileSize: 10_000_000,
        allowedExtensions: ['.csv', '.tsv', '.nc', '.gcode']
      }
    };

    const utils = new PlaywrightMCPUtils(config);
    await use(utils);
  },

  /**
   * MCP Context fixture with type-safe configuration
   */
  mcpContext: async ({ browser, mcpUtils }, use) => {
    const context = await mcpUtils.createMCPContext(browser, {
      recordVideo: {
        dir: process.env.VIDEOS_DIR || resolve(__dirname, '../../reports/videos/'),
        size: {
          width: parseInt(process.env.VIDEO_SIZE_WIDTH || '1920'),
          height: parseInt(process.env.VIDEO_SIZE_HEIGHT || '1080')
        }
      }
    });

    await use(context);
    await context.close();
  },

  /**
   * MCP Page fixture with MELD Visualizer initialization
   */
  mcpPage: async ({ mcpContext, mcpUtils }, use, testInfo) => {
    const page = await mcpContext.newPage();

    // Navigate to MELD Visualizer
    await page.goto('/');

    // Wait for Dash app to be ready
    if (process.env.WAIT_FOR_DASH_READY !== 'false') {
      await page.waitForSelector(DEFAULT_SELECTORS.app.container, {
        timeout: parseInt(process.env.NAVIGATION_TIMEOUT || '30000')
      });

      // Wait for initial JavaScript to load
      await page.waitForFunction(() => {
        return (window as any).dash_clientside && (window as any).Plotly;
      }, { timeout: 15000 });
    }

    await use(page);

    // Export logs after test with enhanced metadata
    const logs = mcpUtils.exportLogs();
    if (logs.summary.consoleErrors > 0 || logs.summary.networkErrors > 0) {
      console.log(`📊 Test "${testInfo.title}" logs:`, JSON.stringify(logs.summary, null, 2));

      // Save detailed logs for failed tests
      if (testInfo.status === 'failed') {
        const logFile = await mcpUtils.saveLogsToFile(`${testInfo.title}-${Date.now()}.json`);
        console.log(`💾 Detailed logs saved to: ${logFile}`);
      }
    }

    await page.close();
  },

  /**
   * Test files fixture with comprehensive data generation
   */
  testFiles: async ({}, use, testInfo) => {
    const testDataDir = resolve(__dirname, 'test_data');
    await mkdir(testDataDir, { recursive: true });

    const generator = new MELDTestDataGenerator({
      seed: 12345,
      count: 100,
      template: {},
      ranges: {
        ToolTemp: [200, 400],
        XPos: [0, 50],
        YPos: [0, 30],
        ZPos: [0, 10]
      },
      distributions: {
        ToolTemp: 'normal',
        SpinVel: 'normal'
      }
    });

    // Generate test data
    const validData = generator.generateDataPoints();
    const validCSV = generator.generateCSV(validData);

    // Create minimal data (3 points)
    const minimalData = validData.slice(0, 3);
    const minimalCSV = generator.generateCSV(minimalData);

    // Create large dataset (1000 points)
    const largeGenerator = new MELDTestDataGenerator({
      seed: 54321,
      count: 1000,
      template: {},
      ranges: {},
      distributions: {}
    });
    const largeData = largeGenerator.generateDataPoints();
    const largeCSV = generator.generateCSV(largeData);

    // Create test files with proper metadata
    const createTestFile = async (
      filename: string,
      content: string,
      type: TestTypes.TestFileType,
      description: string
    ): Promise<TestTypes.TestDataFile> => {
      const filePath = join(testDataDir, filename);
      await writeFile(filePath, content, 'utf-8');

      return {
        name: filename,
        path: filePath,
        content,
        size: Buffer.byteLength(content, 'utf-8'),
        type,
        encoding: 'utf-8',
        metadata: {
          created: new Date(),
          modified: new Date(),
          description,
          tags: ['test', 'meld', type],
          validationRules: {
            required: ['Date', 'Time', 'XPos', 'YPos', 'ZPos', 'ToolTemp'],
            numeric: ['XPos', 'YPos', 'ZPos', 'ToolTemp', 'SpinVel'],
            ranges: {
              ToolTemp: { min: 0, max: 1000 },
              XPos: { min: -100, max: 100 },
              YPos: { min: -100, max: 100 },
              ZPos: { min: -50, max: 50 }
            },
            patterns: {},
            custom: []
          }
        }
      };
    };

    const files: TestTypes.TestFixtures = {
      validMELDData: await createTestFile(
        'valid_meld_data.csv',
        validCSV,
        'csv',
        'Valid MELD manufacturing data with 100 points'
      ),

      invalidMELDData: await createTestFile(
        'invalid_meld_data.csv',
        'Invalid,Header,Structure\n1,2,3\nfoo,bar,baz',
        'csv',
        'Invalid MELD data with wrong headers and non-numeric values'
      ),

      minimalMELDData: await createTestFile(
        'minimal_meld_data.csv',
        minimalCSV,
        'csv',
        'Minimal MELD data with only 3 data points'
      ),

      largeMELDData: await createTestFile(
        'large_meld_data.csv',
        largeCSV,
        'csv',
        'Large MELD dataset with 1000 data points for performance testing'
      ),

      sampleGCode: await createTestFile(
        'sample_toolpath.nc',
        await readFile(resolve(__dirname, 'test_data/sample_toolpath.nc'), 'utf-8'),
        'gcode',
        'Sample G-code toolpath for MELD manufacturing'
      ),

      corruptedFile: await createTestFile(
        'corrupted_file.csv',
        'Date,Time,XPos\n\x00\x01\x02corrupted\x03\x04',
        'csv',
        'Corrupted file with binary characters'
      ),

      emptyFile: await createTestFile(
        'empty_file.csv',
        '',
        'csv',
        'Empty file for testing error handling'
      )
    };

    await use(files);

    // Cleanup test files
    try {
      await rm(testDataDir, { recursive: true, force: true });
    } catch (error) {
      console.warn('Failed to cleanup test files:', error);
    }
  },

  /**
   * Performance monitoring fixture with enhanced metrics
   */
  performanceMonitor: async ({ mcpPage, mcpUtils }, use) => {
    let startTime = Date.now();
    const checkpoints: Array<{ name: string; timestamp: number; elapsed: number }> = [];

    const monitor = {
      loadTime: 0,
      renderTime: 0,
      interactionTime: 0,
      memoryUsage: 0,
      cpuUsage: 0,
      networkRequests: 0,
      bundleSize: 0,
      timestamp: new Date().toISOString(),

      // Helper methods
      mark: (name: string) => {
        checkpoints.push({
          name,
          timestamp: Date.now(),
          elapsed: Date.now() - startTime
        });
      },

      getMetrics: async () => {
        const metrics = await mcpUtils.getPerformanceMetrics(mcpPage);
        Object.assign(monitor, metrics);
        return metrics;
      },

      reset: () => {
        startTime = Date.now();
        checkpoints.length = 0;
      }
    };

    // Initial metrics collection
    try {
      await monitor.getMetrics();
    } catch (error) {
      console.warn('Failed to collect initial performance metrics:', error);
    }

    await use(monitor);

    // Log performance summary
    const finalMetrics = await monitor.getMetrics();
    const loadThreshold = parseInt(process.env.LOAD_TIME_THRESHOLD || '5000');

    if (finalMetrics.loadTime > loadThreshold) {
      console.warn(`⚠️  Slow load time: ${finalMetrics.loadTime}ms (threshold: ${loadThreshold}ms)`);
    }

    if (checkpoints.length > 0) {
      console.log('📊 Performance checkpoints:', checkpoints);
    }
  },

  /**
   * Visual testing fixture with enhanced comparison
   */
  visualTester: async ({ mcpPage, mcpUtils }, use, testInfo) => {
    const visual = {
      takeScreenshot: async (name: string, options: TestTypes.ScreenshotOptions = {}) => {
        return await mcpUtils.takeScreenshot(mcpPage, `${testInfo.title}-${name}`, options);
      },

      compareScreenshot: async (name: string, options: TestTypes.VisualTestConfig = {}) => {
        const screenshotName = `${testInfo.title}-${name}`;
        const threshold = options.threshold || 0.2;

        try {
          await expect(mcpPage).toHaveScreenshot(`${screenshotName}.png`, {
            threshold,
            animations: options.animations || 'disabled',
            clip: options.clip,
            fullPage: options.fullPage !== false,
            mask: options.mask
          });

          return { passed: true, name: screenshotName, diffPixels: 0, totalPixels: 0, diffRatio: 0, threshold };
        } catch (error) {
          console.warn(`📸 Visual diff detected for ${screenshotName}:`, error);
          return {
            passed: false,
            name: screenshotName,
            diffPixels: 0,
            totalPixels: 0,
            diffRatio: 1,
            threshold
          };
        }
      },

      waitForPlotlyGraph: async (selector = '.js-plotly-plot', options: TestTypes.PlotlyWaitOptions = {}) => {
        await mcpUtils.waitForPlotlyGraph(mcpPage, selector, options);
      }
    };

    await use(visual);
  },

  /**
   * Network mocking fixture with comprehensive request handling
   */
  networkMocker: async ({ mcpContext }, use) => {
    const mocker = {
      mockDashCallback: async (outputId: string, mockData: unknown) => {
        await mcpContext.route('**/_dash-update-component', async (route) => {
          const response: DashComponents.CallbackResponse = {
            multi: true,
            response: { [outputId]: mockData }
          };

          await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify(response)
          });
        });
      },

      mockFileUpload: async (response: Partial<TestTypes.FileUploadResponse> = {}) => {
        const defaultResponse: TestTypes.FileUploadResponse = {
          success: true,
          filename: 'mock_upload.csv',
          size: 1024,
          message: 'Mock upload successful',
          data: {
            rows: 100,
            columns: ['X', 'Y', 'Z', 'Temperature'],
            preview: [{ X: 1, Y: 2, Z: 3, Temperature: 250 }]
          },
          ...response
        };

        await mcpContext.route('**/upload*', async (route) => {
          await route.fulfill({
            status: defaultResponse.success ? 200 : 400,
            contentType: 'application/json',
            body: JSON.stringify(defaultResponse)
          });
        });
      },

      mockApiError: async (endpoint: string, errorCode = 500) => {
        await mcpContext.route(`**${endpoint}**`, async (route) => {
          await route.fulfill({
            status: errorCode,
            contentType: 'application/json',
            body: JSON.stringify({
              error: 'Mock API error for testing',
              code: errorCode,
              timestamp: new Date().toISOString()
            })
          });
        });
      }
    };

    await use(mocker);
  },

  /**
   * Console monitoring fixture with categorized logging
   */
  consoleMonitor: async ({ mcpPage }, use) => {
    const errors: TestTypes.ConsoleLog[] = [];
    const warnings: TestTypes.ConsoleLog[] = [];
    const allLogs: TestTypes.ConsoleLog[] = [];

    const monitor = {
      errors,
      warnings,

      getErrors: () => errors.slice(),
      getWarnings: () => warnings.slice(),

      expectNoErrors: () => {
        if (errors.length > 0) {
          const errorMessages = errors.map(e => `${e.type}: ${e.text}`).join('\n');
          throw new Error(`Expected no console errors, but found ${errors.length}:\n${errorMessages}`);
        }
      },

      expectNoWarnings: () => {
        if (warnings.length > 0) {
          const warningMessages = warnings.map(w => `${w.type}: ${w.text}`).join('\n');
          throw new Error(`Expected no console warnings, but found ${warnings.length}:\n${warningMessages}`);
        }
      }
    };

    // Set up console monitoring
    mcpPage.on('console', (msg) => {
      const logEntry: TestTypes.ConsoleLog = {
        timestamp: new Date().toISOString(),
        type: msg.type() as TestTypes.ConsoleLogType,
        text: msg.text(),
        url: mcpPage.url(),
        location: msg.location()
      };

      allLogs.push(logEntry);

      if (msg.type() === 'error') {
        errors.push(logEntry);
      } else if (msg.type() === 'warn') {
        warnings.push(logEntry);
      }
    });

    // Monitor page errors
    mcpPage.on('pageerror', (error) => {
      const errorLog: TestTypes.ConsoleLog = {
        timestamp: new Date().toISOString(),
        type: 'pageerror',
        text: error.message,
        url: mcpPage.url(),
        stack: error.stack
      };

      allLogs.push(errorLog);
      errors.push(errorLog);
    });

    await use(monitor);
  },

  /**
   * Home page object fixture
   */
  homePage: async ({ mcpPage }, use) => {
    const homePage = new HomePageObject(mcpPage, DEFAULT_SELECTORS);
    await use(homePage);
  },

  /**
   * Upload page object fixture
   */
  uploadPage: async ({ mcpPage }, use) => {
    const uploadPage = new UploadPageObject(mcpPage, DEFAULT_SELECTORS);
    await use(uploadPage);
  },

  /**
   * Visualization page object fixture
   */
  visualizationPage: async ({ mcpPage }, use) => {
    const visualizationPage = new VisualizationPageObject(mcpPage, DEFAULT_SELECTORS);
    await use(visualizationPage);
  },

  /**
   * Settings page object fixture
   */
  settingsPage: async ({ mcpPage }, use) => {
    const settingsPage = new SettingsPageObject(mcpPage, DEFAULT_SELECTORS);
    await use(settingsPage);
  }
});

/**
 * Enhanced expect matchers for MELD Visualizer testing
 */
expect.extend({
  /**
   * Validate Plotly graph data structure
   */
  async toHavePlotlyData(received: unknown, expectedStructure?: object) {
    const plotElement = received as any;
    const pass = plotElement &&
                  plotElement._fullData &&
                  Array.isArray(plotElement._fullData) &&
                  plotElement._fullData.length > 0 &&
                  plotElement._fullLayout;

    if (expectedStructure && pass) {
      // Additional structure validation could be added here
    }

    return {
      message: () => pass
        ? `Expected element not to have valid Plotly data structure`
        : `Expected element to have valid Plotly data structure`,
      pass
    };
  },

  /**
   * Check if element is within viewport
   */
  async toBeInViewport(elementHandle: any) {
    const isInViewport = await elementHandle.evaluate((element: Element) => {
      const rect = element.getBoundingClientRect();
      return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= window.innerHeight &&
        rect.right <= window.innerWidth &&
        rect.width > 0 &&
        rect.height > 0
      );
    });

    return {
      message: () => isInViewport
        ? `Expected element not to be in viewport`
        : `Expected element to be in viewport`,
      pass: isInViewport
    };
  },

  /**
   * Validate performance metrics against thresholds
   */
  async toMeetPerformanceThresholds(metrics: TestTypes.PerformanceMetrics, thresholds: Partial<TestTypes.PerformanceThresholds> = {}) {
    const defaultThresholds: TestTypes.PerformanceThresholds = {
      loadTime: parseInt(process.env.LOAD_TIME_THRESHOLD || '5000'),
      renderTime: parseInt(process.env.RENDER_TIME_THRESHOLD || '2000'),
      interactionTime: 100,
      memoryUsage: 100_000_000,
      cpuUsage: 80,
      networkRequests: 50
    };

    const finalThresholds = { ...defaultThresholds, ...thresholds };
    const failures: string[] = [];

    if (metrics.loadTime > finalThresholds.loadTime) {
      failures.push(`Load time ${metrics.loadTime}ms exceeds threshold ${finalThresholds.loadTime}ms`);
    }

    if (metrics.renderTime > finalThresholds.renderTime) {
      failures.push(`Render time ${metrics.renderTime}ms exceeds threshold ${finalThresholds.renderTime}ms`);
    }

    if (metrics.memoryUsage > finalThresholds.memoryUsage) {
      failures.push(`Memory usage ${metrics.memoryUsage} bytes exceeds threshold ${finalThresholds.memoryUsage} bytes`);
    }

    return {
      message: () => failures.length === 0
        ? `Expected performance metrics not to meet thresholds`
        : `Performance issues: ${failures.join(', ')}`,
      pass: failures.length === 0
    };
  },

  /**
   * Validate MELD data structure
   */
  async toBeValidMELDData(received: unknown) {
    const data = received as MELDData.DataPoint[];

    if (!Array.isArray(data) || data.length === 0) {
      return {
        message: () => `Expected valid MELD data array, received ${typeof received}`,
        pass: false
      };
    }

    const requiredFields: Array<keyof MELDData.DataPoint> = [
      'Date', 'Time', 'XPos', 'YPos', 'ZPos', 'ToolTemp'
    ];

    const missingFields = requiredFields.filter(field =>
      data.some(point => point[field] === undefined || point[field] === null)
    );

    const hasInvalidNumbers = data.some(point =>
      ['XPos', 'YPos', 'ZPos', 'ToolTemp'].some(field =>
        isNaN(Number(point[field as keyof MELDData.DataPoint]))
      )
    );

    const pass = missingFields.length === 0 && !hasInvalidNumbers;

    return {
      message: () => pass
        ? `Expected invalid MELD data`
        : `Invalid MELD data: missing fields [${missingFields.join(', ')}], has invalid numbers: ${hasInvalidNumbers}`,
      pass
    };
  }
});

// Export the enhanced test and expect
export { expect };
