/**
 * Type-Safe Playwright MCP Utilities for MELD Visualizer
 * Enhanced with comprehensive TypeScript support and error handling
 */

import { BrowserContext, Page, Request, Response, Route } from '@playwright/test';
import { writeFile, mkdir } from 'fs/promises';
import { resolve, join } from 'path';
import type {
  TestTypes,
  DashComponents,
  MELDData,
  PlotlyTypes
} from '../types';

/**
 * Type-safe MCP utilities class with comprehensive error handling
 */
export class PlaywrightMCPUtils {
  private readonly baseURL: string;
  private readonly screenshotDir: string;
  private readonly networkLogs: TestTypes.NetworkLog[] = [];
  private readonly consoleLogs: TestTypes.ConsoleLog[] = [];
  private readonly performanceMetrics: Partial<TestTypes.PerformanceMetrics> = {};

  constructor(config?: Partial<TestTypes.MELDTestConfig>) {
    this.baseURL = config?.baseURL || process.env.BASE_URL || 'http://localhost:8050';
    this.screenshotDir = config?.files?.reportDir ?
      resolve(config.files.reportDir, 'screenshots') :
      resolve(__dirname, '../../reports/screenshots');
  }

  /**
   * Create MCP-optimized browser context with type safety
   */
  async createMCPContext(
    browser: import('@playwright/test').Browser,
    options: TestTypes.MCPContextOptions = {}
  ): Promise<BrowserContext> {
    const defaultOptions: TestTypes.MCPContextOptions = {
      viewport: { width: 1920, height: 1080 },
      userAgent: 'MELD-Visualizer-Test-Agent/1.0',
      locale: 'en-US',
      timezoneId: 'America/New_York',
      permissions: ['clipboard-read', 'clipboard-write'],
      ignoreHTTPSErrors: true,
      recordVideo: {
        dir: resolve(__dirname, '../../reports/videos/'),
        size: { width: 1920, height: 1080 }
      },
      recordHar: {
        path: resolve(__dirname, '../../reports/network/har-logs.har'),
        mode: 'full'
      },
    };

    const context = await browser.newContext({
      ...defaultOptions,
      ...options,
    });

    // Set up network interception with type safety
    await this.setupNetworkInterception(context);

    // Set up console monitoring
    await this.setupConsoleMonitoring(context);

    // Set up performance monitoring
    await this.setupPerformanceMonitoring(context);

    return context;
  }

  /**
   * Type-safe network request/response interception
   */
  private async setupNetworkInterception(context: BrowserContext): Promise<void> {
    await context.route('**/*', async (route: Route, request: Request) => {
      const url = request.url();
      const method = request.method();
      const headers = request.headers();

      // Log network activity with type safety
      const logEntry: TestTypes.NetworkLog = {
        timestamp: new Date().toISOString(),
        method: method as TestTypes.HttpMethod,
        url,
        headers,
        type: 'request'
      };
      this.networkLogs.push(logEntry);

      try {
        // Handle specific API endpoints for MELD Visualizer
        if (url.includes('/_dash-update-component')) {
          await this.handleDashCallback(route, request);
        } else if (url.includes('/upload')) {
          await this.handleFileUpload(route, request);
        } else {
          // Continue with normal request
          const response = await route.fetch();

          // Log response with type safety
          const responseLog: TestTypes.NetworkLog = {
            timestamp: new Date().toISOString(),
            method: method as TestTypes.HttpMethod,
            url,
            status: response.status(),
            type: 'response',
            duration: Date.now() - new Date(logEntry.timestamp).getTime()
          };
          this.networkLogs.push(responseLog);

          await route.fulfill({ response });
        }
      } catch (error) {
        console.error(`Network interception error for ${url}:`, error);

        // Log error
        const errorLog: TestTypes.NetworkLog = {
          timestamp: new Date().toISOString(),
          method: method as TestTypes.HttpMethod,
          url,
          type: 'error',
          error: error instanceof Error ? error.message : String(error)
        };
        this.networkLogs.push(errorLog);

        // Continue with normal request on error
        await route.continue();
      }
    });
  }

  /**
   * Enhanced console monitoring with type safety
   */
  private async setupConsoleMonitoring(context: BrowserContext): Promise<void> {
    context.on('page', (page: Page) => {
      // Monitor console messages
      page.on('console', (msg) => {
        const logEntry: TestTypes.ConsoleLog = {
          timestamp: new Date().toISOString(),
          type: msg.type() as TestTypes.ConsoleLogType,
          text: msg.text(),
          url: page.url(),
          location: msg.location()
        };

        this.consoleLogs.push(logEntry);

        // Flag errors and warnings with enhanced formatting
        if (msg.type() === 'error' || msg.type() === 'warning') {
          const prefix = msg.type() === 'error' ? '🚨 ERROR' : '⚠️  WARNING';
          console.log(`${prefix}: ${msg.text()}`);
          if (msg.location()) {
            console.log(`  at ${msg.location().url}:${msg.location().lineNumber}:${msg.location().columnNumber}`);
          }
        }
      });

      // Monitor uncaught exceptions with stack traces
      page.on('pageerror', (error: Error) => {
        const logEntry: TestTypes.ConsoleLog = {
          timestamp: new Date().toISOString(),
          type: 'pageerror',
          text: error.message,
          stack: error.stack,
          url: page.url()
        };

        this.consoleLogs.push(logEntry);
        console.error('🔥 Page Error:', error.message);
        if (error.stack) {
          console.error('Stack trace:', error.stack);
        }
      });

      // Monitor request failures with detailed information
      page.on('requestfailed', (request) => {
        const failure: TestTypes.NetworkLog = {
          timestamp: new Date().toISOString(),
          type: 'requestfailed',
          url: request.url(),
          method: request.method() as TestTypes.HttpMethod,
          failure: request.failure()?.errorText,
          headers: request.headers()
        };

        this.networkLogs.push(failure);
        console.error(`🌐 Request Failed: ${request.method()} ${request.url()}`);
        console.error(`  Error: ${request.failure()?.errorText}`);
      });

      // Monitor response errors
      page.on('response', (response: Response) => {
        if (response.status() >= 400) {
          const errorLog: TestTypes.NetworkLog = {
            timestamp: new Date().toISOString(),
            type: 'response',
            url: response.url(),
            method: response.request().method() as TestTypes.HttpMethod,
            status: response.status(),
            statusText: response.statusText()
          };

          this.networkLogs.push(errorLog);
          console.warn(`📡 HTTP ${response.status()}: ${response.request().method()} ${response.url()}`);
        }
      });
    });
  }

  /**
   * Performance monitoring setup
   */
  private async setupPerformanceMonitoring(context: BrowserContext): Promise<void> {
    context.on('page', (page: Page) => {
      // Track page load performance
      page.on('load', async () => {
        try {
          const metrics = await this.getPerformanceMetrics(page);
          Object.assign(this.performanceMetrics, metrics);
        } catch (error) {
          console.warn('Failed to collect performance metrics:', error);
        }
      });
    });
  }

  /**
   * Type-safe Dash callback mocking
   */
  private async handleDashCallback(route: Route, request: Request): Promise<void> {
    const url = request.url();
    const postData = request.postData();

    // Parse the callback request with type safety
    let mockResponse: DashComponents.CallbackResponse = {
      multi: true,
      response: {}
    };

    try {
      if (postData) {
        const data = JSON.parse(postData) as DashComponents.CallbackContext;

        // Mock responses for common MELD Visualizer callbacks
        if (data.outputs && JSON.stringify(data.outputs).includes('graph-3d')) {
          // Mock 3D graph update with proper Plotly data structure
          const mockTrace: PlotlyTypes.Scatter3DTrace = {
            type: 'scatter3d',
            mode: 'markers',
            x: [1, 2, 3, 4, 5],
            y: [1, 4, 2, 8, 5],
            z: [1, 2, 3, 2, 4],
            marker: {
              size: 5,
              color: [10, 20, 30, 40, 50],
              colorscale: 'Viridis',
              showscale: true
            },
            name: 'Mock MELD Data'
          };

          const mockLayout: Partial<PlotlyTypes.PlotlyLayout> = {
            title: 'Mock 3D MELD Visualization',
            scene: {
              xaxis: { title: { text: 'X Position (mm)' } },
              yaxis: { title: { text: 'Y Position (mm)' } },
              zaxis: { title: { text: 'Z Position (mm)' } }
            }
          };

          mockResponse.response['graph-3d'] = {
            figure: {
              data: [mockTrace],
              layout: mockLayout
            }
          };
        } else if (data.outputs && JSON.stringify(data.outputs).includes('data-table')) {
          // Mock data table update
          mockResponse.response['data-table'] = {
            data: [
              { X: 1.0, Y: 2.0, Z: 3.0, Temperature: 250.5, Velocity: 15.2 },
              { X: 2.0, Y: 3.0, Z: 4.0, Temperature: 255.8, Velocity: 16.1 }
            ],
            columns: [
              { name: 'X Position', id: 'X', type: 'numeric', format: { specifier: '.2f' } },
              { name: 'Y Position', id: 'Y', type: 'numeric', format: { specifier: '.2f' } },
              { name: 'Z Position', id: 'Z', type: 'numeric', format: { specifier: '.2f' } },
              { name: 'Temperature (°C)', id: 'Temperature', type: 'numeric', format: { specifier: '.1f' } },
              { name: 'Velocity (mm/min)', id: 'Velocity', type: 'numeric', format: { specifier: '.1f' } }
            ]
          };
        }
      }
    } catch (error) {
      console.warn('Failed to parse callback data:', error);
      // Use default mock response
    }

    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(mockResponse)
    });
  }

  /**
   * Type-safe file upload mocking
   */
  private async handleFileUpload(route: Route, request: Request): Promise<void> {
    const uploadResponse: TestTypes.FileUploadResponse = {
      success: true,
      filename: 'mock_test_file.csv',
      size: 2048,
      message: 'File uploaded successfully',
      data: {
        rows: 100,
        columns: ['X', 'Y', 'Z', 'Temperature', 'Velocity'],
        preview: [
          { X: 1.0, Y: 2.0, Z: 3.0, Temperature: 250.5, Velocity: 15.2 }
        ]
      }
    };

    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(uploadResponse)
    });
  }

  /**
   * Enhanced screenshot functionality with type safety
   */
  async takeScreenshot(
    page: Page,
    name: string,
    options: TestTypes.ScreenshotOptions = {}
  ): Promise<TestTypes.ScreenshotResult> {
    // Ensure screenshot directory exists
    await mkdir(this.screenshotDir, { recursive: true });

    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `${name}-${timestamp}.png`;
    const screenshotPath = resolve(this.screenshotDir, filename);

    const defaultOptions: TestTypes.ScreenshotOptions = {
      path: screenshotPath,
      fullPage: true,
      animations: 'disabled',
      caret: 'hide',
      ...options
    };

    try {
      await page.screenshot(defaultOptions);

      return {
        success: true,
        path: screenshotPath,
        name: filename,
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      console.error(`Screenshot failed for ${name}:`, error);
      return {
        success: false,
        name: filename,
        timestamp: new Date().toISOString(),
        error: error instanceof Error ? error.message : String(error)
      };
    }
  }

  /**
   * Type-safe Plotly graph waiting with enhanced validation
   */
  async waitForPlotlyGraph(
    page: Page,
    selector = '.js-plotly-plot',
    options: TestTypes.PlotlyWaitOptions = {}
  ): Promise<void> {
    const { timeout = 30_000, expectedTraces, validateData = true } = options;

    // Wait for the graph container to be present
    await page.waitForSelector(selector, { timeout });

    // Wait for Plotly to finish rendering with enhanced validation
    await page.waitForFunction((sel: string) => {
      const element = document.querySelector(sel) as any;
      if (!element) return false;

      // Check if Plotly has initialized
      if (!element._fullLayout || !element._fullData) return false;

      // Check if data exists
      if (!Array.isArray(element._fullData) || element._fullData.length === 0) return false;

      // Ensure the plot is not in a loading state
      const plotDiv = element;
      return !plotDiv.style.pointerEvents || plotDiv.style.pointerEvents !== 'none';
    }, selector, { timeout });

    // Additional validation if requested
    if (validateData || expectedTraces !== undefined) {
      const plotData = await page.evaluate((sel: string) => {
        const element = document.querySelector(sel) as any;
        return {
          traceCount: element._fullData ? element._fullData.length : 0,
          hasLayout: !!element._fullLayout,
          isRendered: element._fullLayout && element._fullData
        };
      }, selector);

      if (!plotData.isRendered) {
        throw new Error('Plotly graph failed to render properly');
      }

      if (expectedTraces !== undefined && plotData.traceCount !== expectedTraces) {
        throw new Error(`Expected ${expectedTraces} traces, but found ${plotData.traceCount}`);
      }
    }

    // Additional wait for animations to complete
    await page.waitForTimeout(1000);
  }

  /**
   * Enhanced performance metrics collection
   */
  async getPerformanceMetrics(page: Page): Promise<TestTypes.PerformanceMetrics> {
    const metrics = await page.evaluate(() => {
      const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      const paint = performance.getEntriesByType('paint');
      const resources = performance.getEntriesByType('resource');

      return {
        loadTime: navigation ? navigation.loadEventEnd - navigation.fetchStart : 0,
        domContentLoaded: navigation ? navigation.domContentLoadedEventEnd - navigation.fetchStart : 0,
        renderTime: paint.find(p => p.name === 'first-contentful-paint')?.startTime || 0,
        interactionTime: 0, // Will be measured separately
        firstPaint: paint.find(p => p.name === 'first-paint')?.startTime || 0,
        firstContentfulPaint: paint.find(p => p.name === 'first-contentful-paint')?.startTime || 0,
        resourceCount: resources.length,
        timestamp: new Date().toISOString()
      } as TestTypes.PerformanceMetrics;
    });

    // Get memory usage if available
    try {
      const memoryInfo = await page.evaluate(() => {
        return (performance as any).memory ? {
          memoryUsage: (performance as any).memory.usedJSHeapSize,
          totalMemory: (performance as any).memory.totalJSHeapSize
        } : { memoryUsage: 0, totalMemory: 0 };
      });

      Object.assign(metrics, memoryInfo);
    } catch {
      // Memory API not available
      metrics.memoryUsage = 0;
    }

    return metrics;
  }

  /**
   * Type-safe log export functionality
   */
  exportLogs(): TestTypes.TestLogExport {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');

    return {
      timestamp,
      network: this.networkLogs,
      console: this.consoleLogs,
      performance: this.performanceMetrics,
      summary: {
        networkRequests: this.networkLogs.filter(l => l.type === 'request').length,
        networkResponses: this.networkLogs.filter(l => l.type === 'response').length,
        networkErrors: this.networkLogs.filter(l => l.type === 'error' || l.type === 'requestfailed').length,
        consoleErrors: this.consoleLogs.filter(l => l.type === 'error').length,
        consoleWarnings: this.consoleLogs.filter(l => l.type === 'warning').length,
        totalLogs: this.networkLogs.length + this.consoleLogs.length
      }
    };
  }

  /**
   * Save logs to file with type safety
   */
  async saveLogsToFile(filename?: string): Promise<string> {
    const logs = this.exportLogs();
    const logFilename = filename || `test-logs-${logs.timestamp}.json`;
    const logPath = resolve(this.screenshotDir, '..', 'logs', logFilename);

    await mkdir(resolve(logPath, '..'), { recursive: true });
    await writeFile(logPath, JSON.stringify(logs, null, 2));

    return logPath;
  }

  /**
   * Clear accumulated logs
   */
  clearLogs(): void {
    this.networkLogs.length = 0;
    this.consoleLogs.length = 0;
    Object.keys(this.performanceMetrics).forEach(key => {
      delete this.performanceMetrics[key as keyof TestTypes.PerformanceMetrics];
    });
  }

  /**
   * Get current log summary
   */
  getLogSummary(): TestTypes.TestLogSummary {
    return {
      networkRequests: this.networkLogs.filter(l => l.type === 'request').length,
      networkResponses: this.networkLogs.filter(l => l.type === 'response').length,
      networkErrors: this.networkLogs.filter(l => l.type === 'error' || l.type === 'requestfailed').length,
      consoleErrors: this.consoleLogs.filter(l => l.type === 'error').length,
      consoleWarnings: this.consoleLogs.filter(l => l.type === 'warning').length,
      totalLogs: this.networkLogs.length + this.consoleLogs.length
    };
  }
}
