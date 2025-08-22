/**
 * Visual Test Suite Configuration
 * Main configuration file that orchestrates all visual regression tests
 */

import { test, devices } from '@playwright/test';
import { VisualTestUtils } from './visual-utils';
import { 
  BROWSER_CONFIGS, 
  RESPONSIVE_VIEWPORTS, 
  THEME_CONFIGS,
  DEFAULT_VISUAL_CONFIG 
} from './visual-config';

// Test tags for selective execution
export const TEST_TAGS = {
  SMOKE: '@smoke',
  REGRESSION: '@regression',
  VISUAL: '@visual',
  CROSS_BROWSER: '@cross-browser',
  RESPONSIVE: '@responsive',
  THEME: '@theme',
  COMPONENT: '@component',
  ANIMATION: '@animation',
  ACCESSIBILITY: '@accessibility',
  CSS: '@css',
  PERFORMANCE: '@performance'
} as const;

// Test suite configuration
export const VISUAL_TEST_SUITE_CONFIG = {
  // Base URL for all tests
  baseURL: 'http://localhost:8050',
  
  // Global timeout settings
  timeout: 30000,
  actionTimeout: 10000,
  navigationTimeout: 15000,
  
  // Retry configuration
  retries: 2,
  
  // Screenshot settings
  screenshot: {
    mode: 'only-on-failure' as const,
    fullPage: true
  },
  
  // Video settings
  video: {
    mode: 'retain-on-failure' as const,
    size: { width: 1280, height: 720 }
  },
  
  // Test directory structure
  testDir: './visual',
  outputDir: './visual-results',
  
  // Browser projects for cross-browser testing
  projects: [
    {
      name: 'Visual - Chromium',
      use: { ...devices['Desktop Chrome'], ...BROWSER_CONFIGS.chromium.use },
      testMatch: /.*\.(test|spec)\.ts/
    },
    {
      name: 'Visual - Firefox',
      use: { ...devices['Desktop Firefox'], ...BROWSER_CONFIGS.firefox.use },
      testMatch: /.*\.(test|spec)\.ts/
    },
    {
      name: 'Visual - WebKit',
      use: { ...devices['Desktop Safari'], ...BROWSER_CONFIGS.webkit.use },
      testMatch: /.*\.(test|spec)\.ts/
    },
    // Mobile testing
    {
      name: 'Visual - Mobile Chrome',
      use: { ...devices['Pixel 5'] },
      testMatch: /responsive.*\.(test|spec)\.ts/
    },
    {
      name: 'Visual - Mobile Safari',
      use: { ...devices['iPhone 12'] },
      testMatch: /responsive.*\.(test|spec)\.ts/
    }
  ],
  
  // Reporter configuration
  reporter: [
    ['html', { outputFolder: 'visual-report', open: 'never' }],
    ['json', { outputFile: 'visual-results.json' }],
    ['junit', { outputFile: 'visual-junit.xml' }]
  ],
  
  // Global setup and teardown
  globalSetup: './visual-global-setup.ts',
  globalTeardown: './visual-global-teardown.ts',
  
  // Worker configuration
  workers: process.env.CI ? 2 : undefined,
  
  // Test file patterns
  testMatch: [
    '**/visual/**/*.test.ts',
    '**/visual/**/*.spec.ts'
  ],
  
  // Ignore patterns
  testIgnore: [
    '**/node_modules/**',
    '**/dist/**',
    '**/build/**'
  ]
} as const;

/**
 * Visual Test Categories
 */
export const VISUAL_TEST_CATEGORIES = {
  // Core visual regression tests
  CORE: {
    description: 'Core visual regression tests for critical UI components',
    files: [
      'component-tests.ts',
      'theme-tests.ts'
    ],
    tags: [TEST_TAGS.VISUAL, TEST_TAGS.REGRESSION],
    priority: 'high'
  },
  
  // Cross-browser compatibility
  CROSS_BROWSER: {
    description: 'Cross-browser visual consistency validation',
    files: [
      'cross-browser-tests.ts'
    ],
    tags: [TEST_TAGS.VISUAL, TEST_TAGS.CROSS_BROWSER],
    priority: 'high'
  },
  
  // Responsive design validation
  RESPONSIVE: {
    description: 'Responsive design and viewport testing',
    files: [
      'responsive-tests.ts'
    ],
    tags: [TEST_TAGS.VISUAL, TEST_TAGS.RESPONSIVE],
    priority: 'medium'
  },
  
  // Animation and interaction testing
  ANIMATION: {
    description: 'Animation, transitions, and interactive feedback',
    files: [
      'animation-tests.ts'
    ],
    tags: [TEST_TAGS.VISUAL, TEST_TAGS.ANIMATION],
    priority: 'medium'
  },
  
  // Accessibility visual validation
  ACCESSIBILITY: {
    description: 'Accessibility features and WCAG compliance',
    files: [
      'accessibility-tests.ts'
    ],
    tags: [TEST_TAGS.VISUAL, TEST_TAGS.ACCESSIBILITY],
    priority: 'high'
  },
  
  // CSS and layout validation
  CSS: {
    description: 'CSS properties, layouts, and performance validation',
    files: [
      'css-validation-tests.ts'
    ],
    tags: [TEST_TAGS.VISUAL, TEST_TAGS.CSS],
    priority: 'medium'
  }
} as const;

/**
 * Test execution helpers
 */
export class VisualTestRunner {
  /**
   * Run smoke tests (critical visual components only)
   */
  static async runSmokeTests(): Promise<void> {
    console.log('🔍 Running visual smoke tests...');
    // Implementation would run tests tagged with @smoke
  }

  /**
   * Run full visual regression suite
   */
  static async runFullSuite(): Promise<void> {
    console.log('🎯 Running full visual regression suite...');
    // Implementation would run all visual tests
  }

  /**
   * Run cross-browser tests only
   */
  static async runCrossBrowserTests(): Promise<void> {
    console.log('🌐 Running cross-browser visual tests...');
    // Implementation would run cross-browser specific tests
  }

  /**
   * Update visual baselines
   */
  static async updateBaselines(): Promise<void> {
    console.log('📸 Updating visual baselines...');
    // Implementation would update screenshot baselines
  }

  /**
   * Generate visual test report
   */
  static async generateReport(): Promise<void> {
    console.log('📊 Generating visual test report...');
    // Implementation would generate comprehensive test report
  }
}

/**
 * Environment-specific configurations
 */
export const ENVIRONMENT_CONFIGS = {
  development: {
    ...DEFAULT_VISUAL_CONFIG,
    threshold: 0.2, // More lenient for development
    timeout: 60000
  },
  
  staging: {
    ...DEFAULT_VISUAL_CONFIG,
    threshold: 0.1, // Stricter for staging
    timeout: 45000
  },
  
  production: {
    ...DEFAULT_VISUAL_CONFIG,
    threshold: 0.05, // Very strict for production
    timeout: 30000
  }
} as const;

/**
 * Get configuration for current environment
 */
export function getEnvironmentConfig() {
  const env = process.env.NODE_ENV || 'development';
  return ENVIRONMENT_CONFIGS[env as keyof typeof ENVIRONMENT_CONFIGS] || ENVIRONMENT_CONFIGS.development;
}

/**
 * Visual test utilities for common operations
 */
export const VisualTestHelpers = {
  /**
   * Setup test environment
   */
  async setupTestEnvironment(page: any): Promise<VisualTestUtils> {
    const visualUtils = new VisualTestUtils(page);
    
    // Wait for application to be ready
    await page.waitForLoadState('networkidle');
    
    // Disable animations by default
    await visualUtils.disableAnimations();
    
    return visualUtils;
  },

  /**
   * Cleanup after tests
   */
  async cleanupTestEnvironment(page: any): Promise<void> {
    // Clear any test data or state
    await page.evaluate(() => {
      // Remove any test elements
      const testElements = document.querySelectorAll('[data-testid]');
      testElements.forEach(el => el.remove());
      
      // Reset any modified styles
      const modifiedStyles = document.querySelectorAll('style[data-test]');
      modifiedStyles.forEach(style => style.remove());
    });
  },

  /**
   * Wait for application stability
   */
  async waitForStability(page: any): Promise<void> {
    // Wait for network requests to complete
    await page.waitForLoadState('networkidle');
    
    // Wait for any pending animations
    await page.waitForTimeout(500);
    
    // Wait for fonts to load
    await page.evaluate(() => {
      return document.fonts.ready;
    });
  }
};

export default VISUAL_TEST_SUITE_CONFIG;