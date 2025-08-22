/**
 * MELD Visualizer Test Suite Type Definitions
 * Comprehensive TypeScript support for test automation
 */

// Core data types
export * from './meld-data';
export * from './dash-components';
export * from './plotly-types';
export * from './test-types';

// Re-export commonly used types for convenience
export type {
  // MELD Data
  MELDData.DataPoint,
  MELDData.Dataset,
  MELDData.MELDPoint3D,
  MELDData.ValidationResult,
  
  // Dash Components
  DashComponents.CallbackContext,
  DashComponents.UploadedFile,
  DashComponents.ThemeConfig,
  DashComponents.DataTableProps,
  
  // Plotly
  PlotlyTypes.Scatter3DTrace,
  PlotlyTypes.PlotlyLayout,
  PlotlyTypes.PlotlyConfig,
  PlotlyTypes.MELDPlotConfig,
  
  // Testing
  TestTypes.MELDTestConfig,
  TestTypes.TestDataFile,
  TestTypes.PageSelectors,
  TestTypes.TestAssertions,
  TestTypes.PerformanceMetrics,
  TestTypes.VisualTestConfig
} from './meld-data';

// Global type augmentations for testing environment
declare global {
  namespace NodeJS {
    interface ProcessEnv {
      readonly BASE_URL?: string;
      readonly TRACE_MODE?: string;
      readonly SCREENSHOT_MODE?: string;
      readonly VIDEO_MODE?: string;
      readonly ACTION_TIMEOUT?: string;
      readonly NAVIGATION_TIMEOUT?: string;
      readonly WAIT_FOR_DASH_READY?: string;
      readonly TEST_DATA_DIR?: string;
      readonly LOAD_TIME_THRESHOLD?: string;
      readonly RENDER_TIME_THRESHOLD?: string;
      readonly VIDEO_SIZE_WIDTH?: string;
      readonly VIDEO_SIZE_HEIGHT?: string;
      readonly VIDEOS_DIR?: string;
      readonly CI?: string;
    }
  }

  namespace Playwright {
    interface Matchers<R> {
      /**
       * Custom matcher for Plotly graph validation
       */
      toHavePlotlyData(expectedStructure?: object): R;
      
      /**
       * Custom matcher for viewport validation
       */
      toBeInViewport(): R;
      
      /**
       * Custom matcher for performance validation
       */
      toMeetPerformanceThresholds(thresholds?: object): R;
      
      /**
       * Custom matcher for MELD data validation
       */
      toBeValidMELDData(): R;
      
      /**
       * Custom matcher for accessibility compliance
       */
      toBeAccessible(options?: object): R;
      
      /**
       * Custom matcher for visual regression
       */
      toMatchVisualSnapshot(name: string, options?: object): R;
    }
  }
}

// Module augmentations for Playwright fixtures
declare module '@playwright/test' {
  interface Fixtures {
    // MCP-specific fixtures
    mcpUtils: import('./test-types').TestTypes.TestExecutionContext['fixtures'];
    mcpContext: BrowserContext;
    mcpPage: Page;
    
    // MELD-specific fixtures
    testFiles: import('./test-types').TestTypes.TestFixtures;
    performanceMonitor: import('./test-types').TestTypes.PerformanceMetrics;
    visualTester: import('./test-types').TestTypes.VisualTestConfig;
    networkMocker: import('./test-types').TestTypes.NetworkMockConfig;
    consoleMonitor: import('./test-types').TestTypes.TestAssertions;
    
    // Page objects
    homePage: HomePage;
    uploadPage: UploadPage;
    visualizationPage: VisualizationPage;
    settingsPage: SettingsPage;
  }
}

// Page object type definitions
export interface HomePage extends import('./test-types').BasePage {
  readonly header: Locator;
  readonly navigation: Locator;
  readonly themeToggle: Locator;
  
  goto(): Promise<void>;
  switchTheme(theme: import('./dash-components').DashComponents.ThemeConfig['name']): Promise<void>;
  navigateToTab(tabId: string): Promise<void>;
}

export interface UploadPage extends import('./test-types').BasePage {
  readonly dropzone: Locator;
  readonly fileInput: Locator;
  readonly uploadButton: Locator;
  readonly progressBar: Locator;
  readonly statusMessage: Locator;
  
  uploadFile(file: import('./test-types').TestTypes.TestDataFile): Promise<void>;
  waitForUploadComplete(): Promise<void>;
  getUploadStatus(): Promise<'success' | 'error' | 'pending'>;
}

export interface VisualizationPage extends import('./test-types').BasePage {
  readonly plotlyGraph: Locator;
  readonly dataTable: Locator;
  readonly exportButton: Locator;
  readonly resetButton: Locator;
  readonly legend: Locator;
  
  waitForGraphRender(): Promise<void>;
  getTraceCount(): Promise<number>;
  getDataPoints(): Promise<ReadonlyArray<import('./meld-data').MELDData.MELDPoint3D>>;
  exportData(format: 'csv' | 'json'): Promise<string>;
  resetView(): Promise<void>;
  toggleTrace(traceName: string): Promise<void>;
}

export interface SettingsPage extends import('./test-types').BasePage {
  readonly themeSelector: Locator;
  readonly performanceOptions: Locator;
  readonly exportSettings: Locator;
  readonly resetSettings: Locator;
  
  changeTheme(theme: import('./dash-components').DashComponents.ThemeConfig['name']): Promise<void>;
  updatePerformanceSettings(settings: object): Promise<void>;
  resetToDefaults(): Promise<void>;
  exportConfiguration(): Promise<string>;
}

// Utility type helpers for test development
export namespace TypeHelpers {
  /**
   * Create a type-safe test data builder
   */
  export interface TestDataBuilder<T> {
    with<K extends keyof T>(key: K, value: T[K]): TestDataBuilder<T>;
    build(): T;
  }
  
  /**
   * Create a mock response builder
   */
  export interface MockBuilder {
    forUrl(url: string | RegExp): MockBuilder;
    withMethod(method: string): MockBuilder;
    withResponse(response: object): MockBuilder;
    withDelay(ms: number): MockBuilder;
    withStatus(code: number): MockBuilder;
    build(): import('./test-types').TestTypes.NetworkMock;
  }
  
  /**
   * Create a performance assertion builder
   */
  export interface PerformanceAssertionBuilder {
    loadTime(threshold: number): PerformanceAssertionBuilder;
    renderTime(threshold: number): PerformanceAssertionBuilder;
    memoryUsage(threshold: number): PerformanceAssertionBuilder;
    build(): import('./test-types').TestTypes.PerformanceThresholds;
  }
  
  /**
   * Create a visual test configuration builder
   */
  export interface VisualTestBuilder {
    threshold(value: number): VisualTestBuilder;
    fullPage(enabled: boolean): VisualTestBuilder;
    animations(mode: 'disabled' | 'allow'): VisualTestBuilder;
    clip(x: number, y: number, width: number, height: number): VisualTestBuilder;
    build(): import('./test-types').TestTypes.VisualTestConfig;
  }
}

// Constants for commonly used values
export const TEST_CONSTANTS = {
  // Default timeouts (milliseconds)
  TIMEOUTS: {
    NAVIGATION: 30_000,
    ACTION: 10_000,
    ASSERTION: 5_000,
    PLOTLY_RENDER: 15_000,
    FILE_UPLOAD: 30_000,
    DASH_CALLBACK: 10_000,
  },
  
  // Viewport sizes
  VIEWPORTS: {
    DESKTOP: { width: 1920, height: 1080 },
    LAPTOP: { width: 1366, height: 768 },
    TABLET: { width: 768, height: 1024 },
    MOBILE: { width: 375, height: 667 },
    HIGH_DPI: { width: 2560, height: 1440 },
  },
  
  // Performance thresholds
  PERFORMANCE: {
    LOAD_TIME: 5_000,
    RENDER_TIME: 2_000,
    INTERACTION_TIME: 100,
    MEMORY_USAGE: 100_000_000, // 100MB
    CPU_USAGE: 80, // 80%
  },
  
  // File size limits
  FILE_SIZES: {
    MIN: 1024, // 1KB
    MAX: 10_000_000, // 10MB
    LARGE: 1_000_000, // 1MB
  },
  
  // Visual regression thresholds
  VISUAL: {
    THRESHOLD: 0.2,
    PIXEL_DIFF: 100,
    RATIO_DIFF: 0.01,
  },
  
  // Test data generation
  DATA_GENERATION: {
    DEFAULT_COUNT: 1000,
    MIN_TEMPERATURE: 200,
    MAX_TEMPERATURE: 500,
    MIN_VELOCITY: 0,
    MAX_VELOCITY: 100,
  },
  
  // Common selectors
  SELECTORS: {
    APP_CONTAINER: '[data-testid="app-container"], .dash-app-content, #app',
    PLOTLY_GRAPH: '.js-plotly-plot',
    LOADING_INDICATOR: '[data-testid="loading"], .loading',
    ERROR_MESSAGE: '[data-testid="error"], .error',
    SUCCESS_MESSAGE: '[data-testid="success"], .success',
  },
  
  // Network patterns
  NETWORK: {
    DASH_CALLBACK: '**/_dash-update-component',
    FILE_UPLOAD: '**/upload*',
    STATIC_ASSETS: '**/*.{css,js,png,jpg,svg,woff,woff2}',
  },
  
  // Theme names
  THEMES: ['light', 'dark', 'plotly', 'plotly_dark'] as const,
  
  // File extensions
  EXTENSIONS: {
    MELD_DATA: ['.csv', '.tsv'],
    GCODE: ['.nc', '.gcode', '.tap'],
    IMAGES: ['.png', '.jpg', '.jpeg', '.gif', '.svg'],
    EXPORTS: ['.csv', '.json', '.xlsx', '.pdf'],
  },
} as const;

// Type-safe configuration validation
export interface ConfigValidator {
  validateTestConfig(config: import('./test-types').TestTypes.MELDTestConfig): {
    valid: boolean;
    errors: ReadonlyArray<string>;
  };
  
  validateMELDData(data: unknown): data is import('./meld-data').MELDData.DataPoint;
  
  validatePlotlyConfig(config: unknown): config is import('./plotly-types').PlotlyTypes.PlotlyConfig;
  
  validatePageSelectors(selectors: unknown): selectors is import('./test-types').TestTypes.PageSelectors;
}