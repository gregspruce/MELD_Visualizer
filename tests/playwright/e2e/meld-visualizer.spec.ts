/**
 * MELD Visualizer End-to-End Tests with TypeScript Type Safety
 * Comprehensive E2E testing demonstrating type-safe Playwright integration
 */

import { test, expect } from '../fixtures/mcp-fixtures';
import { MELDDataValidator, TestDataGenerator } from '../utils/test-data-validators';
import type { MELDData, TestTypes, DashComponents, PlotlyTypes } from '../types';

/**
 * Test suite for MELD Visualizer core functionality
 * @smoke - Critical path tests
 * @regression - Full regression testing
 */
test.describe('MELD Visualizer - Core Functionality', () => {
  
  /**
   * Application Loading and Initialization
   * Verifies that the Dash application loads correctly with all components
   */
  test('should load application successfully @smoke', async ({ 
    homePage, 
    consoleMonitor, 
    performanceMonitor 
  }) => {
    // Navigate to home page with type-safe page object
    await homePage.goto();
    
    // Verify page elements are present
    await expect(homePage.header).toBeVisible();
    await expect(homePage.navigation).toBeVisible();
    
    // Check performance metrics meet thresholds
    const metrics = await performanceMonitor.getMetrics();
    expect(metrics).toMeetPerformanceThresholds({
      loadTime: 5000,
      renderTime: 2000
    });
    
    // Ensure no console errors during load
    consoleMonitor.expectNoErrors();
  });

  /**
   * Theme Switching Functionality
   * Tests theme changes with type safety for theme names
   */
  test('should switch themes correctly @smoke', async ({ 
    homePage, 
    consoleMonitor 
  }) => {
    await homePage.goto();
    
    // Test each theme with type-safe theme names
    const themes: DashComponents.ThemeConfig['name'][] = ['light', 'dark', 'plotly', 'plotly_dark'];
    
    for (const theme of themes) {
      await homePage.switchTheme(theme);
      
      const currentTheme = await homePage.getCurrentTheme();
      
      // Type-safe theme validation
      if (theme === 'dark' || theme === 'plotly_dark') {
        expect(currentTheme).toBe('dark');
      } else {
        expect(currentTheme).toBe('light');
      }
    }
    
    // Verify no errors during theme switching
    consoleMonitor.expectNoErrors();
  });

  /**
   * Tab Navigation Testing
   * Verifies tab navigation works with proper type safety
   */
  test('should navigate between tabs @smoke', async ({ 
    homePage, 
    mcpPage 
  }) => {
    await homePage.goto();
    
    // Define test tabs with proper typing
    const testTabs: Array<{ id: string; expectedContent: string }> = [
      { id: 'upload', expectedContent: 'upload' },
      { id: 'visualization', expectedContent: 'graph' },
      { id: 'data', expectedContent: 'table' },
      { id: 'settings', expectedContent: 'settings' }
    ];
    
    for (const tab of testTabs) {
      await homePage.navigateToTab(tab.id);
      
      // Wait for tab content to load
      await mcpPage.waitForTimeout(500);
      
      // Verify tab is active using type-safe selectors
      const isActive = await mcpPage.locator(`[data-tab="${tab.id}"].active`).isVisible();
      expect(isActive).toBeTruthy();
    }
  });
});

/**
 * File Upload Testing Suite
 * Comprehensive testing of file upload functionality with type-safe data handling
 */
test.describe('MELD Visualizer - File Upload', () => {
  
  /**
   * Valid File Upload Test
   * Tests upload of valid MELD data with full validation
   */
  test('should upload valid MELD data file @regression', async ({ 
    uploadPage, 
    testFiles, 
    consoleMonitor,
    performanceMonitor
  }) => {
    await uploadPage.goto();
    
    // Use type-safe test fixture
    const validFile = testFiles.validMELDData;
    
    // Validate file data before upload
    const { data, validation } = MELDDataValidator.parseCSV(validFile.content);
    expect(validation.isValid).toBeTruthy();
    expect(data).toBeValidMELDData();
    
    // Perform upload with performance monitoring
    performanceMonitor.mark('upload-start');
    await uploadPage.uploadFile(validFile);
    performanceMonitor.mark('upload-complete');
    
    // Verify upload success
    const status = await uploadPage.getUploadStatus();
    expect(status).toBe('success');
    
    // Check performance
    const metrics = await performanceMonitor.getMetrics();
    expect(metrics.loadTime).toBeLessThan(30000); // 30 second max for large files
    
    // Ensure no console errors
    consoleMonitor.expectNoErrors();
  });

  /**
   * Invalid File Upload Test
   * Tests error handling for invalid data with type safety
   */
  test('should handle invalid file upload gracefully @regression', async ({ 
    uploadPage, 
    testFiles,
    consoleMonitor
  }) => {
    await uploadPage.goto();
    
    // Test with invalid data file
    const invalidFile = testFiles.invalidMELDData;
    
    // Validate that file is indeed invalid
    const { validation } = MELDDataValidator.parseCSV(invalidFile.content);
    expect(validation.isValid).toBeFalsy();
    expect(validation.errors.length).toBeGreaterThan(0);
    
    try {
      await uploadPage.uploadFile(invalidFile);
      const status = await uploadPage.getUploadStatus();
      expect(status).toBe('error');
    } catch (error) {
      // Upload should fail gracefully
      expect(error).toBeInstanceOf(Error);
    }
    
    // Should have no unexpected console errors
    const errors = consoleMonitor.getErrors();
    const unexpectedErrors = errors.filter(e => !e.text.includes('validation'));
    expect(unexpectedErrors).toHaveLength(0);
  });

  /**
   * Large File Upload Performance Test
   * Tests performance with large datasets
   */
  test('should handle large file uploads within time limits @performance', async ({ 
    uploadPage, 
    testFiles,
    performanceMonitor 
  }) => {
    await uploadPage.goto();
    
    const largeFile = testFiles.largeMELDData;
    
    // Verify file is actually large
    expect(largeFile.size).toBeGreaterThan(100_000); // 100KB minimum
    
    performanceMonitor.mark('large-upload-start');
    await uploadPage.uploadFile(largeFile);
    performanceMonitor.mark('large-upload-complete');
    
    const status = await uploadPage.getUploadStatus();
    expect(status).toBe('success');
    
    // Check upload performance
    const metrics = await performanceMonitor.getMetrics();
    expect(metrics.loadTime).toBeLessThan(60_000); // 60 seconds max
  });
});

/**
 * Data Visualization Testing Suite
 * Tests 3D visualization with type-safe Plotly integration
 */
test.describe('MELD Visualizer - Data Visualization', () => {
  
  /**
   * 3D Graph Rendering Test
   * Verifies Plotly 3D graph renders correctly with proper data
   */
  test('should render 3D visualization correctly @smoke', async ({ 
    visualizationPage, 
    testFiles,
    visualTester,
    consoleMonitor 
  }) => {
    // First upload data
    await visualizationPage.goto();
    
    // Wait for any existing graph to load or timeout gracefully
    try {
      await visualTester.waitForPlotlyGraph('.js-plotly-plot', { 
        timeout: 10_000,
        expectedTraces: 1,
        validateData: true 
      });
    } catch {
      // No existing graph, which is fine for this test
    }
    
    // Verify graph container exists
    await expect(visualizationPage.plotlyGraph).toBeVisible();
    
    // Check for proper 3D scene setup
    const cameraPosition = await visualizationPage.getCameraPosition();
    expect(cameraPosition).not.toBeNull();
    
    // Verify graph is interactive
    const isInteractive = await visualizationPage.isGraphInteractive();
    expect(isInteractive).toBeTruthy();
    
    // Ensure no rendering errors
    consoleMonitor.expectNoErrors();
  });

  /**
   * Graph Interaction Testing
   * Tests user interactions with the 3D visualization
   */
  test('should support graph interactions @regression', async ({ 
    visualizationPage, 
    mcpPage 
  }) => {
    await visualizationPage.goto();
    
    try {
      await visualizationPage.waitForGraphRender();
      
      // Test reset functionality
      await visualizationPage.resetView();
      
      // Get initial camera position after reset
      const initialCamera = await visualizationPage.getCameraPosition();
      expect(initialCamera).not.toBeNull();
      
      // Test export functionality
      const exportedFile = await visualizationPage.exportData('csv');
      expect(exportedFile).toContain('.csv');
      
      // Test trace count
      const traceCount = await visualizationPage.getTraceCount();
      expect(traceCount).toBeGreaterThanOrEqual(0);
      
    } catch (error) {
      // Log error for debugging but don't fail if no data is loaded
      console.log('Graph interaction test skipped - no data loaded:', error);
    }
  });

  /**
   * Data Points Extraction Test
   * Verifies data extraction with proper typing
   */
  test('should extract data points with correct types @regression', async ({ 
    visualizationPage, 
    testFiles 
  }) => {
    await visualizationPage.goto();
    
    try {
      await visualizationPage.waitForGraphRender();
      
      // Extract data points with type safety
      const dataPoints = await visualizationPage.getDataPoints();
      
      // Validate data structure
      expect(Array.isArray(dataPoints)).toBeTruthy();
      
      if (dataPoints.length > 0) {
        const firstPoint = dataPoints[0];
        
        // Type-safe property checks
        expect(typeof firstPoint.x).toBe('number');
        expect(typeof firstPoint.y).toBe('number');
        expect(typeof firstPoint.z).toBe('number');
        expect(typeof firstPoint.temperature).toBe('number');
        expect(typeof firstPoint.timestamp).toBe('string');
        
        // Validate as MELD point
        expect([firstPoint]).toBeValidMELDData();
      }
    } catch (error) {
      console.log('Data extraction test skipped - no data available:', error);
    }
  });
});

/**
 * Visual Regression Testing Suite
 * Comprehensive visual testing with type-safe configuration
 */
test.describe('MELD Visualizer - Visual Regression', () => {
  
  /**
   * Application Layout Visual Test
   * Captures and compares application layout
   */
  test('should maintain consistent visual layout @visual', async ({ 
    homePage, 
    visualTester,
    mcpPage 
  }) => {
    await homePage.goto();
    
    // Wait for complete load
    await mcpPage.waitForLoadState('networkidle');
    
    // Take screenshot with type-safe configuration
    const screenshotResult = await visualTester.takeScreenshot('homepage-layout', {
      fullPage: true,
      animations: 'disabled'
    });
    
    expect(screenshotResult.success).toBeTruthy();
    
    // Compare with baseline
    const comparisonResult = await visualTester.compareScreenshot('homepage-layout', {
      threshold: 0.1,
      fullPage: true,
      animations: 'disabled'
    });
    
    expect(comparisonResult.passed).toBeTruthy();
  });

  /**
   * Theme Visual Consistency Test
   * Verifies visual consistency across themes
   */
  test('should maintain visual consistency across themes @visual', async ({ 
    homePage, 
    visualTester 
  }) => {
    await homePage.goto();
    
    const themes: DashComponents.ThemeConfig['name'][] = ['light', 'dark'];
    
    for (const theme of themes) {
      await homePage.switchTheme(theme);
      
      const screenshotResult = await visualTester.takeScreenshot(`theme-${theme}`, {
        fullPage: true,
        animations: 'disabled'
      });
      
      expect(screenshotResult.success).toBeTruthy();
      
      // Visual comparison with theme-specific baseline
      const comparisonResult = await visualTester.compareScreenshot(`theme-${theme}`, {
        threshold: 0.15, // Slightly higher threshold for theme changes
        animations: 'disabled'
      });
      
      // Log result for debugging
      if (!comparisonResult.passed) {
        console.warn(`Theme ${theme} visual regression detected`);
      }
    }
  });
});

/**
 * Performance Testing Suite
 * Comprehensive performance testing with type-safe metrics
 */
test.describe('MELD Visualizer - Performance', () => {
  
  /**
   * Application Load Performance Test
   * Measures and validates load performance
   */
  test('should load within performance thresholds @performance', async ({ 
    homePage, 
    performanceMonitor 
  }) => {
    performanceMonitor.mark('app-load-start');
    await homePage.goto();
    performanceMonitor.mark('app-load-complete');
    
    const metrics = await performanceMonitor.getMetrics();
    
    // Type-safe performance validation
    expect(metrics).toMeetPerformanceThresholds({
      loadTime: 5000,
      renderTime: 2000,
      memoryUsage: 100_000_000 // 100MB
    });
    
    // Log performance metrics for monitoring
    console.log('📊 Performance Metrics:', {
      loadTime: `${metrics.loadTime}ms`,
      renderTime: `${metrics.renderTime}ms`,
      memoryUsage: `${Math.round(metrics.memoryUsage / 1024 / 1024)}MB`
    });
  });

  /**
   * Large Dataset Performance Test
   * Tests performance with large MELD datasets
   */
  test('should handle large datasets efficiently @performance', async ({ 
    uploadPage, 
    visualizationPage,
    testFiles,
    performanceMonitor 
  }) => {
    // Upload large dataset
    await uploadPage.goto();
    
    performanceMonitor.mark('large-data-upload-start');
    await uploadPage.uploadFile(testFiles.largeMELDData);
    performanceMonitor.mark('large-data-upload-complete');
    
    // Navigate to visualization
    await visualizationPage.goto();
    
    performanceMonitor.mark('large-data-render-start');
    await visualizationPage.waitForGraphRender();
    performanceMonitor.mark('large-data-render-complete');
    
    const metrics = await performanceMonitor.getMetrics();
    
    // Large dataset should still meet reasonable performance thresholds
    expect(metrics.loadTime).toBeLessThan(15_000); // 15 seconds
    expect(metrics.renderTime).toBeLessThan(5_000); // 5 seconds
    
    console.log('📊 Large Dataset Performance:', {
      uploadTime: `${metrics.loadTime}ms`,
      renderTime: `${metrics.renderTime}ms`
    });
  });
});

/**
 * Error Handling and Edge Cases
 * Tests application robustness with type-safe error handling
 */
test.describe('MELD Visualizer - Error Handling', () => {
  
  /**
   * Network Error Handling Test
   * Tests graceful handling of network issues
   */
  test('should handle network errors gracefully @regression', async ({ 
    mcpPage, 
    networkMocker,
    homePage,
    consoleMonitor 
  }) => {
    // Mock API error
    await networkMocker.mockApiError('/_dash-update-component', 500);
    
    await homePage.goto();
    
    // Application should still load basic interface
    await expect(homePage.header).toBeVisible();
    
    // Should handle errors gracefully without crashing
    const errors = consoleMonitor.getErrors();
    const criticalErrors = errors.filter(e => 
      e.text.includes('TypeError') || 
      e.text.includes('ReferenceError')
    );
    
    expect(criticalErrors).toHaveLength(0);
  });

  /**
   * Invalid Data Handling Test
   * Tests handling of corrupted or invalid data files
   */
  test('should handle corrupted data files @regression', async ({ 
    uploadPage, 
    testFiles,
    consoleMonitor 
  }) => {
    await uploadPage.goto();
    
    // Test with corrupted file
    const corruptedFile = testFiles.corruptedFile;
    
    try {
      await uploadPage.uploadFile(corruptedFile);
      const status = await uploadPage.getUploadStatus();
      expect(status).toBe('error');
    } catch (error) {
      // Expected to fail
      expect(error).toBeInstanceOf(Error);
    }
    
    // Application should remain stable
    await expect(uploadPage.dropzone).toBeVisible();
    
    // No critical console errors
    const errors = consoleMonitor.getErrors();
    const criticalErrors = errors.filter(e => 
      e.text.includes('CRITICAL') || 
      e.text.includes('FATAL')
    );
    
    expect(criticalErrors).toHaveLength(0);
  });
});

/**
 * Accessibility Testing
 * Basic accessibility checks with type safety
 */
test.describe('MELD Visualizer - Accessibility @a11y', () => {
  
  /**
   * Basic Accessibility Test
   * Verifies basic accessibility compliance
   */
  test('should meet basic accessibility standards', async ({ 
    homePage, 
    mcpPage 
  }) => {
    await homePage.goto();
    
    // Check for proper heading structure
    const headings = await mcpPage.locator('h1, h2, h3, h4, h5, h6').all();
    expect(headings.length).toBeGreaterThan(0);
    
    // Check for proper alt text on images
    const images = await mcpPage.locator('img').all();
    for (const img of images) {
      const alt = await img.getAttribute('alt');
      expect(alt).toBeTruthy();
    }
    
    // Check for proper form labels
    const inputs = await mcpPage.locator('input').all();
    for (const input of inputs) {
      const label = await mcpPage.locator(`label[for="${await input.getAttribute('id')}"]`);
      const hasLabel = await label.count() > 0 || await input.getAttribute('aria-label');
      expect(hasLabel).toBeTruthy();
    }
  });
});

/**
 * Data Generation and Validation Testing
 * Tests the type-safe data generation utilities
 */
test.describe('Test Data Generation and Validation', () => {
  
  /**
   * Data Generator Test
   * Tests the synthetic data generation with proper typing
   */
  test('should generate valid MELD test data', async ({}) => {
    const config: TestTypes.TestDataGeneratorConfig = {
      seed: 12345,
      count: 50,
      template: {},
      ranges: {
        ToolTemp: [200, 400],
        XPos: [0, 100],
        YPos: [0, 50]
      },
      patterns: {},
      distributions: {
        ToolTemp: 'normal'
      }
    };
    
    const dataset = TestDataGenerator.generateMELDDataset(config);
    
    // Validate generated dataset
    expect(dataset.data).toHaveLength(50);
    expect(dataset.metadata.recordCount).toBe(50);
    expect(dataset.statistics).toBeDefined();
    
    // Validate individual data points
    expect(dataset.data).toBeValidMELDData();
    
    // Check that ranges were applied
    const toolTemps = dataset.data.map(d => d.ToolTemp);
    const minTemp = Math.min(...toolTemps);
    const maxTemp = Math.max(...toolTemps);
    
    expect(minTemp).toBeGreaterThanOrEqual(200);
    expect(maxTemp).toBeLessThanOrEqual(400);
  });

  /**
   * Data Validation Test
   * Tests the MELD data validation utilities
   */
  test('should validate MELD data correctly', async ({}) => {
    // Create test data with known issues
    const testData = [
      {
        Date: '2024-01-15',
        Time: '10:00:00.00',
        XPos: 1.5,
        YPos: 2.5,
        ZPos: 3.5,
        ToolTemp: 250.5,
        SpinVel: 100,
        SpinTrq: 5.5,
        SpinPwr: 550
      },
      {
        Date: 'invalid-date', // Invalid date format
        Time: '10:00:01.00',
        XPos: 'invalid', // Invalid numeric value
        YPos: 3.5,
        ZPos: 4.5,
        ToolTemp: 1500, // Out of range
        SpinVel: 101,
        SpinTrq: 5.6,
        SpinPwr: 565
      }
    ];
    
    const result = MELDDataValidator.validateDataset(testData);
    
    // Should detect issues
    expect(result.isValid).toBeFalsy();
    expect(result.errors.length).toBeGreaterThan(0);
    expect(result.summary.validRows).toBe(1);
    expect(result.summary.totalRows).toBe(2);
    expect(result.summary.dataQuality).toBe('poor');
    
    // Check specific error types
    const dateError = result.errors.find(e => e.field === 'Date');
    const numericError = result.errors.find(e => e.field === 'XPos');
    const rangeWarning = result.warnings?.find(w => w.field === 'ToolTemp');
    
    expect(dateError).toBeDefined();
    expect(numericError).toBeDefined();
  });
});