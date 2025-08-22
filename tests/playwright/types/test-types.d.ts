/**
 * Test Configuration Type Definitions
 * Type-safe interfaces for test data, configurations, and Playwright MCP integration
 */

import type { Page, BrowserContext, TestInfo, Locator } from '@playwright/test';
import type { MELDData } from './meld-data';
import type { DashComponents } from './dash-components';
import type { PlotlyTypes } from './plotly-types';

export namespace TestTypes {
  /**
   * Test configuration for MELD Visualizer
   */
  export interface MELDTestConfig {
    readonly baseURL: string;
    readonly timeout: TestTimeouts;
    readonly viewport: ViewportSize;
    readonly screenshots: ScreenshotConfig;
    readonly performance: PerformanceThresholds;
    readonly files: TestFileConfig;
    readonly mcp: MCPConfig;
  }

  /**
   * Test timeout configuration
   */
  export interface TestTimeouts {
    readonly navigation: number;
    readonly action: number;
    readonly assertion: number;
    readonly plotlyRender: number;
    readonly fileUpload: number;
    readonly dashCallback: number;
  }

  /**
   * Viewport configuration for responsive testing
   */
  export interface ViewportSize {
    readonly width: number;
    readonly height: number;
  }

  /**
   * Screenshot configuration
   */
  export interface ScreenshotConfig {
    readonly mode: 'off' | 'only-on-failure' | 'on';
    readonly fullPage: boolean;
    readonly threshold: number;
    readonly animations: 'disabled' | 'allow';
    readonly caret: 'hide' | 'initial';
  }

  /**
   * Performance testing thresholds
   */
  export interface PerformanceThresholds {
    readonly loadTime: number;
    readonly renderTime: number;
    readonly interactionTime: number;
    readonly memoryUsage: number;
    readonly cpuUsage: number;
    readonly networkRequests: number;
  }

  /**
   * Test file configuration
   */
  export interface TestFileConfig {
    readonly testDataDir: string;
    readonly uploadDir: string;
    readonly downloadDir: string;
    readonly reportDir: string;
    readonly maxFileSize: number;
    readonly allowedExtensions: ReadonlyArray<string>;
  }

  /**
   * MCP (Model Context Protocol) configuration
   */
  export interface MCPConfig {
    readonly enabled: boolean;
    readonly serverUrl: string;
    readonly apiKey?: string;
    readonly timeout: number;
    readonly retries: number;
    readonly mockMode: boolean;
  }

  /**
   * Test data file information
   */
  export interface TestDataFile {
    readonly name: string;
    readonly path: string;
    readonly content: string | Buffer;
    readonly size: number;
    readonly type: TestFileType;
    readonly encoding: BufferEncoding;
    readonly metadata: TestFileMetadata;
  }

  /**
   * Test file types
   */
  export type TestFileType = 'csv' | 'gcode' | 'json' | 'image' | 'binary';

  /**
   * Test file metadata
   */
  export interface TestFileMetadata {
    readonly created: Date;
    readonly modified: Date;
    readonly description: string;
    readonly tags: ReadonlyArray<string>;
    readonly expectedData?: Partial<MELDData.DataPoint>;
    readonly validationRules?: TestValidationRules;
  }

  /**
   * Test validation rules
   */
  export interface TestValidationRules {
    readonly required: ReadonlyArray<string>;
    readonly numeric: ReadonlyArray<string>;
    readonly ranges: Record<string, { min: number; max: number }>;
    readonly patterns: Record<string, string>;
    readonly custom: ReadonlyArray<CustomValidationRule>;
  }

  /**
   * Custom validation rule
   */
  export interface CustomValidationRule {
    readonly field: string;
    readonly validator: (value: unknown) => boolean;
    readonly message: string;
  }

  /**
   * Test fixture data
   */
  export interface TestFixtures {
    readonly validMELDData: TestDataFile;
    readonly invalidMELDData: TestDataFile;
    readonly minimalMELDData: TestDataFile;
    readonly largeMELDData: TestDataFile;
    readonly sampleGCode: TestDataFile;
    readonly corruptedFile: TestDataFile;
    readonly emptyFile: TestDataFile;
  }

  /**
   * Page object selectors
   */
  export interface PageSelectors {
    readonly app: {
      readonly container: string;
      readonly header: string;
      readonly footer: string;
      readonly loading: string;
      readonly error: string;
    };
    readonly upload: {
      readonly dropzone: string;
      readonly fileInput: string;
      readonly button: string;
      readonly progress: string;
      readonly success: string;
      readonly error: string;
    };
    readonly tabs: {
      readonly container: string;
      readonly tab: (id: string) => string;
      readonly content: string;
      readonly active: string;
    };
    readonly graph: {
      readonly container: string;
      readonly plotly: string;
      readonly legend: string;
      readonly toolbar: string;
      readonly loading: string;
    };
    readonly controls: {
      readonly themeToggle: string;
      readonly exportButton: string;
      readonly resetButton: string;
      readonly settingsButton: string;
    };
    readonly table: {
      readonly container: string;
      readonly header: string;
      readonly row: string;
      readonly cell: string;
      readonly pagination: string;
    };
  }

  /**
   * Test assertion helpers
   */
  export interface TestAssertions {
    readonly page: Page;
    
    /**
     * Assert that MELD data is properly loaded
     */
    readonly assertMELDDataLoaded: (expectedCount?: number) => Promise<void>;
    
    /**
     * Assert that Plotly graph is rendered correctly
     */
    readonly assertPlotlyGraphRendered: (
      selector: string,
      expectedTraces?: number
    ) => Promise<void>;
    
    /**
     * Assert that file upload completed successfully
     */
    readonly assertFileUploadSuccess: (filename: string) => Promise<void>;
    
    /**
     * Assert that theme is applied correctly
     */
    readonly assertThemeApplied: (theme: DashComponents.ThemeConfig['name']) => Promise<void>;
    
    /**
     * Assert performance metrics meet thresholds
     */
    readonly assertPerformanceMetrics: (
      thresholds: PerformanceThresholds
    ) => Promise<TestPerformanceResult>;
    
    /**
     * Assert no console errors
     */
    readonly assertNoConsoleErrors: () => Promise<void>;
    
    /**
     * Assert network requests are successful
     */
    readonly assertNetworkHealth: () => Promise<void>;
  }

  /**
   * Performance test result
   */
  export interface TestPerformanceResult {
    readonly passed: boolean;
    readonly metrics: PerformanceMetrics;
    readonly failures: ReadonlyArray<PerformanceFailure>;
  }

  /**
   * Performance metrics
   */
  export interface PerformanceMetrics {
    readonly loadTime: number;
    readonly renderTime: number;
    readonly interactionTime: number;
    readonly memoryUsage: number;
    readonly cpuUsage: number;
    readonly networkRequests: number;
    readonly bundleSize: number;
    readonly timestamp: string;
  }

  /**
   * Performance failure details
   */
  export interface PerformanceFailure {
    readonly metric: keyof PerformanceMetrics;
    readonly actual: number;
    readonly threshold: number;
    readonly message: string;
  }

  /**
   * Test environment information
   */
  export interface TestEnvironment {
    readonly browser: string;
    readonly version: string;
    readonly platform: string;
    readonly viewport: ViewportSize;
    readonly baseURL: string;
    readonly testId: string;
    readonly timestamp: string;
  }

  /**
   * Test execution context
   */
  export interface TestExecutionContext {
    readonly testInfo: TestInfo;
    readonly page: Page;
    readonly context: BrowserContext;
    readonly environment: TestEnvironment;
    readonly fixtures: TestFixtures;
    readonly selectors: PageSelectors;
    readonly assertions: TestAssertions;
  }

  /**
   * Visual regression test configuration
   */
  export interface VisualTestConfig {
    readonly threshold: number;
    readonly animations: 'disabled' | 'allow';
    readonly caret: 'hide' | 'initial';
    readonly clip?: {
      readonly x: number;
      readonly y: number;
      readonly width: number;
      readonly height: number;
    };
    readonly fullPage: boolean;
    readonly omitBackground: boolean;
    readonly mask?: ReadonlyArray<Locator>;
  }

  /**
   * Visual test result
   */
  export interface VisualTestResult {
    readonly passed: boolean;
    readonly diff?: Buffer;
    readonly diffPixels: number;
    readonly totalPixels: number;
    readonly diffRatio: number;
    readonly threshold: number;
  }

  /**
   * Network interception configuration
   */
  export interface NetworkMockConfig {
    readonly enabled: boolean;
    readonly mocks: ReadonlyArray<NetworkMock>;
    readonly recordUnmatched: boolean;
    readonly failOnUnmatched: boolean;
  }

  /**
   * Network mock definition
   */
  export interface NetworkMock {
    readonly url: string | RegExp;
    readonly method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
    readonly response: NetworkMockResponse;
    readonly delay?: number;
    readonly status?: number;
    readonly headers?: Record<string, string>;
    readonly times?: number;
  }

  /**
   * Network mock response
   */
  export interface NetworkMockResponse {
    readonly body?: string | object | Buffer;
    readonly json?: object;
    readonly file?: string;
    readonly contentType?: string;
  }

  /**
   * Test data generator configuration
   */
  export interface TestDataGeneratorConfig {
    readonly seed?: number;
    readonly count: number;
    readonly template: Partial<MELDData.DataPoint>;
    readonly ranges: Partial<Record<keyof MELDData.DataPoint, [number, number]>>;
    readonly patterns: Partial<Record<keyof MELDData.DataPoint, string>>;
    readonly distributions: Partial<Record<keyof MELDData.DataPoint, 'normal' | 'uniform' | 'exponential'>>;
  }

  /**
   * Test report configuration
   */
  export interface TestReportConfig {
    readonly format: 'html' | 'json' | 'junit' | 'allure';
    readonly outputDir: string;
    readonly includeScreenshots: boolean;
    readonly includeVideos: boolean;
    readonly includeTraces: boolean;
    readonly includeNetworkLogs: boolean;
    readonly includeConsoleLog: boolean;
  }

  /**
   * Test execution result
   */
  export interface TestResult {
    readonly testId: string;
    readonly name: string;
    readonly status: 'passed' | 'failed' | 'skipped' | 'timedout';
    readonly duration: number;
    readonly error?: string;
    readonly steps: ReadonlyArray<TestStep>;
    readonly screenshots: ReadonlyArray<string>;
    readonly videos: ReadonlyArray<string>;
    readonly traces: ReadonlyArray<string>;
    readonly performance?: PerformanceMetrics;
    readonly coverage?: TestCoverageReport;
  }

  /**
   * Test step information
   */
  export interface TestStep {
    readonly name: string;
    readonly category: 'action' | 'assertion' | 'setup' | 'teardown';
    readonly duration: number;
    readonly status: 'passed' | 'failed';
    readonly error?: string;
    readonly screenshot?: string;
  }

  /**
   * Test coverage report
   */
  export interface TestCoverageReport {
    readonly lines: CoverageMetric;
    readonly functions: CoverageMetric;
    readonly branches: CoverageMetric;
    readonly statements: CoverageMetric;
  }

  /**
   * Coverage metric
   */
  export interface CoverageMetric {
    readonly total: number;
    readonly covered: number;
    readonly percentage: number;
  }

  /**
   * Test suite configuration
   */
  export interface TestSuiteConfig {
    readonly name: string;
    readonly description: string;
    readonly parallel: boolean;
    readonly retries: number;
    readonly timeout: number;
    readonly setup?: string;
    readonly teardown?: string;
    readonly tags: ReadonlyArray<string>;
    readonly dependencies: ReadonlyArray<string>;
  }

  /**
   * Test execution plan
   */
  export interface TestExecutionPlan {
    readonly suites: ReadonlyArray<TestSuiteConfig>;
    readonly environment: TestEnvironment;
    readonly config: MELDTestConfig;
    readonly estimatedDuration: number;
    readonly resourceRequirements: TestResourceRequirements;
  }

  /**
   * Test resource requirements
   */
  export interface TestResourceRequirements {
    readonly memory: number; // MB
    readonly storage: number; // MB
    readonly network: boolean;
    readonly browsers: ReadonlyArray<string>;
    readonly parallel: number;
  }

  /**
   * A11y (Accessibility) test configuration
   */
  export interface AccessibilityTestConfig {
    readonly enabled: boolean;
    readonly standards: ReadonlyArray<'wcag2a' | 'wcag2aa' | 'wcag2aaa' | 'section508'>;
    readonly tags: ReadonlyArray<string>;
    readonly include: ReadonlyArray<string>;
    readonly exclude: ReadonlyArray<string>;
    readonly disableRules: ReadonlyArray<string>;
  }

  /**
   * A11y test result
   */
  export interface AccessibilityTestResult {
    readonly violations: ReadonlyArray<AccessibilityViolation>;
    readonly passes: ReadonlyArray<AccessibilityRule>;
    readonly incomplete: ReadonlyArray<AccessibilityRule>;
    readonly inapplicable: ReadonlyArray<AccessibilityRule>;
  }

  /**
   * A11y violation details
   */
  export interface AccessibilityViolation {
    readonly id: string;
    readonly impact: 'minor' | 'moderate' | 'serious' | 'critical';
    readonly description: string;
    readonly help: string;
    readonly helpUrl: string;
    readonly nodes: ReadonlyArray<AccessibilityNode>;
  }

  /**
   * A11y rule information
   */
  export interface AccessibilityRule {
    readonly id: string;
    readonly description: string;
    readonly help: string;
  }

  /**
   * A11y node information
   */
  export interface AccessibilityNode {
    readonly html: string;
    readonly target: ReadonlyArray<string>;
    readonly failureSummary: string;
  }
}

/**
 * Type-safe page object base class
 */
export abstract class BasePage {
  constructor(
    protected readonly page: Page,
    protected readonly selectors: TestTypes.PageSelectors
  ) {}

  /**
   * Navigate to page
   */
  abstract goto(url?: string): Promise<void>;

  /**
   * Wait for page to be loaded
   */
  abstract waitForLoad(): Promise<void>;

  /**
   * Take screenshot of current state
   */
  async screenshot(name: string): Promise<Buffer> {
    return await this.page.screenshot({ 
      fullPage: true,
      path: `screenshots/${name}.png`
    });
  }

  /**
   * Get element by test ID
   */
  getByTestId(testId: string): Locator {
    return this.page.getByTestId(testId);
  }

  /**
   * Wait for element to be visible
   */
  async waitForElement(selector: string): Promise<Locator> {
    const element = this.page.locator(selector);
    await element.waitFor({ state: 'visible' });
    return element;
  }
}

/**
 * Utility types for test development
 */
export namespace TestUtilityTypes {
  /**
   * Extract test configuration keys
   */
  export type ConfigKeys = keyof TestTypes.MELDTestConfig;

  /**
   * Test function signature
   */
  export type TestFunction<T = void> = (context: TestTypes.TestExecutionContext) => Promise<T>;

  /**
   * Test data validator function
   */
  export type DataValidator<T> = (data: T) => TestTypes.TestValidationRules;

  /**
   * Performance metric extractor
   */
  export type MetricExtractor = (page: Page) => Promise<Partial<TestTypes.PerformanceMetrics>>;

  /**
   * Test fixture generator
   */
  export type FixtureGenerator<T> = (config: TestTypes.TestDataGeneratorConfig) => T;

  /**
   * Mock response generator
   */
  export type MockResponseGenerator = (request: {
    url: string;
    method: string;
    headers: Record<string, string>;
    body?: string;
  }) => TestTypes.NetworkMockResponse;

  /**
   * Visual test comparator
   */
  export type VisualComparator = (
    actual: Buffer,
    expected: Buffer,
    config: TestTypes.VisualTestConfig
  ) => TestTypes.VisualTestResult;

  /**
   * Test result formatter
   */
  export type ResultFormatter<T> = (results: ReadonlyArray<TestTypes.TestResult>) => T;

  /**
   * Test environment detector
   */
  export type EnvironmentDetector = () => TestTypes.TestEnvironment;

  /**
   * Custom assertion function
   */
  export type CustomAssertion<T> = (actual: T, expected: T, message?: string) => Promise<void>;
}