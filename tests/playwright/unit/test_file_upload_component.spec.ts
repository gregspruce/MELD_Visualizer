/**
 * Comprehensive File Upload Component Tests for MELD Visualizer
 * Tests file upload functionality using MCP Playwright functions
 */

import { test, expect } from '../fixtures/mcp-fixtures';
import type { TestTypes, MELDData } from '../types';
import { resolve } from 'path';

test.describe('File Upload Component', () => {
  test.beforeEach(async ({ mcpPage, uploadPage, performanceMonitor }) => {
    // Navigate to upload section and start performance monitoring
    await uploadPage.navigateToUpload();
    performanceMonitor.mark('upload-page-ready');
    
    // Verify upload component is visible and interactive
    await expect(mcpPage.locator('[data-testid="upload-dropzone"]')).toBeVisible();
    await expect(mcpPage.locator('input[type="file"]')).toBeAttached();
  });

  test.describe('Valid File Upload Tests', () => {
    test('should upload valid CSV MELD data file successfully', async ({ 
      mcpPage, 
      uploadPage, 
      testFiles, 
      visualTester,
      consoleMonitor,
      performanceMonitor
    }) => {
      // Take screenshot before upload
      await visualTester.takeScreenshot('upload-before', { fullPage: true });
      
      performanceMonitor.mark('upload-start');
      
      // Upload valid MELD data file
      await uploadPage.uploadFile(testFiles.validMELDData.path);
      
      // Wait for upload processing with MCP monitoring
      await mcpPage.waitForSelector('[data-testid="upload-success"]', { timeout: 15000 });
      
      performanceMonitor.mark('upload-complete');
      
      // Verify success message appears
      const successMessage = mcpPage.locator('[data-testid="upload-success"]');
      await expect(successMessage).toBeVisible();
      await expect(successMessage).toContainText('successfully uploaded');
      
      // Verify file information is displayed
      await expect(mcpPage.locator('[data-testid="file-info"]')).toBeVisible();
      await expect(mcpPage.locator('[data-testid="file-name"]')).toContainText('valid_meld_data.csv');
      await expect(mcpPage.locator('[data-testid="file-size"]')).toBeVisible();
      
      // Verify data preview table is populated
      await expect(mcpPage.locator('[data-testid="data-preview"]')).toBeVisible();
      const previewRows = mcpPage.locator('[data-testid="data-preview"] tbody tr');
      await expect(previewRows).toHaveCount.greaterThan(0);
      
      // Take screenshot after successful upload
      await visualTester.takeScreenshot('upload-success', { fullPage: true });
      
      // Verify no console errors occurred
      consoleMonitor.expectNoErrors();
      
      // Check performance metrics
      const metrics = await performanceMonitor.getMetrics();
      expect(metrics.loadTime).toBeLessThan(5000); // 5 second threshold
    });

    test('should handle G-code file upload correctly', async ({ 
      mcpPage, 
      uploadPage, 
      testFiles, 
      visualTester 
    }) => {
      // Upload G-code file
      await uploadPage.uploadFile(testFiles.sampleGCode.path);
      
      // Wait for processing
      await mcpPage.waitForSelector('[data-testid="upload-success"]', { timeout: 10000 });
      
      // Verify G-code specific processing
      await expect(mcpPage.locator('[data-testid="gcode-info"]')).toBeVisible();
      await expect(mcpPage.locator('[data-testid="gcode-lines"]')).toBeVisible();
      
      // Take screenshot for G-code upload
      await visualTester.takeScreenshot('gcode-upload-success');
    });

    test('should show progress indicator during large file upload', async ({ 
      mcpPage, 
      uploadPage, 
      testFiles, 
      performanceMonitor 
    }) => {
      performanceMonitor.mark('large-upload-start');
      
      // Start upload of large file
      const uploadPromise = uploadPage.uploadFile(testFiles.largeMELDData.path);
      
      // Verify progress indicator appears quickly
      await expect(mcpPage.locator('[data-testid="upload-progress"]')).toBeVisible({ timeout: 2000 });
      
      // Verify progress bar shows progress
      const progressBar = mcpPage.locator('[data-testid="upload-progress"] progress, [data-testid="upload-progress"] .progress-bar');
      await expect(progressBar).toBeVisible();
      
      // Wait for upload completion
      await uploadPromise;
      await mcpPage.waitForSelector('[data-testid="upload-success"]', { timeout: 30000 });
      
      performanceMonitor.mark('large-upload-complete');
      
      // Verify progress indicator is hidden after completion
      await expect(mcpPage.locator('[data-testid="upload-progress"]')).toBeHidden();
      
      // Check that large file was processed within reasonable time
      const metrics = await performanceMonitor.getMetrics();
      expect(metrics.loadTime).toBeLessThan(15000); // 15 second threshold for large files
    });
  });

  test.describe('Drag and Drop Functionality', () => {
    test('should support drag and drop file upload', async ({ 
      mcpPage, 
      testFiles, 
      visualTester 
    }) => {
      const dropzone = mcpPage.locator('[data-testid="upload-dropzone"]');
      
      // Create file for drag and drop simulation
      const fileBuffer = Buffer.from(testFiles.validMELDData.content);
      
      // Simulate drag enter
      await dropzone.dispatchEvent('dragenter', {
        dataTransfer: {
          items: [{ kind: 'file', type: 'text/csv' }],
          files: []
        }
      });
      
      // Verify dropzone visual feedback
      await expect(dropzone).toHaveClass(/drag-over|dropzone-active/);
      await visualTester.takeScreenshot('dropzone-drag-over');
      
      // Simulate drop event
      await dropzone.setInputFiles(testFiles.validMELDData.path);
      
      // Verify upload processes automatically
      await mcpPage.waitForSelector('[data-testid="upload-success"]', { timeout: 10000 });
      await expect(mcpPage.locator('[data-testid="upload-success"]')).toBeVisible();
      
      // Take final screenshot
      await visualTester.takeScreenshot('dropzone-upload-complete');
    });

    test('should show visual feedback during drag operations', async ({ 
      mcpPage, 
      visualTester 
    }) => {
      const dropzone = mcpPage.locator('[data-testid="upload-dropzone"]');
      
      // Test drag enter visual feedback
      await dropzone.dispatchEvent('dragenter');
      await expect(dropzone).toHaveClass(/drag-over|dropzone-active/);
      await visualTester.takeScreenshot('drag-enter-feedback');
      
      // Test drag leave visual feedback
      await dropzone.dispatchEvent('dragleave');
      await expect(dropzone).not.toHaveClass(/drag-over|dropzone-active/);
      await visualTester.takeScreenshot('drag-leave-feedback');
    });
  });

  test.describe('Invalid File Upload Tests', () => {
    test('should reject files with invalid format', async ({ 
      mcpPage, 
      uploadPage, 
      testFiles, 
      visualTester 
    }) => {
      // Attempt to upload invalid file
      await uploadPage.uploadFile(testFiles.invalidMELDData.path);
      
      // Verify error message appears
      await expect(mcpPage.locator('[data-testid="upload-error"]')).toBeVisible({ timeout: 10000 });
      
      const errorMessage = mcpPage.locator('[data-testid="upload-error"]');
      await expect(errorMessage).toContainText(/invalid|format|error/i);
      
      // Verify no data preview is shown
      await expect(mcpPage.locator('[data-testid="data-preview"]')).not.toBeVisible();
      
      // Take screenshot of error state
      await visualTester.takeScreenshot('upload-invalid-format-error');
    });

    test('should handle corrupted file gracefully', async ({ 
      mcpPage, 
      uploadPage, 
      testFiles, 
      consoleMonitor 
    }) => {
      // Upload corrupted file
      await uploadPage.uploadFile(testFiles.corruptedFile.path);
      
      // Wait for error handling
      await expect(mcpPage.locator('[data-testid="upload-error"]')).toBeVisible({ timeout: 5000 });
      
      // Verify appropriate error message
      const errorMessage = mcpPage.locator('[data-testid="upload-error"]');
      await expect(errorMessage).toContainText(/corrupted|invalid|error/i);
      
      // Ensure no console errors are thrown (should be handled gracefully)
      const errors = consoleMonitor.getErrors();
      const relevantErrors = errors.filter(error => 
        !error.text.includes('network') && !error.text.includes('favicon')
      );
      expect(relevantErrors).toHaveLength(0);
    });

    test('should reject empty files', async ({ 
      mcpPage, 
      uploadPage, 
      testFiles 
    }) => {
      // Upload empty file
      await uploadPage.uploadFile(testFiles.emptyFile.path);
      
      // Verify empty file error
      await expect(mcpPage.locator('[data-testid="upload-error"]')).toBeVisible();
      await expect(mcpPage.locator('[data-testid="upload-error"]')).toContainText(/empty|no data/i);
      
      // Verify upload area returns to initial state
      await expect(mcpPage.locator('[data-testid="upload-dropzone"]')).toBeVisible();
    });

    test('should validate file size limits', async ({ 
      mcpPage, 
      uploadPage 
    }) => {
      // Create a file that exceeds size limits (mock large file)
      const mockLargeFile = resolve(__dirname, '../fixtures/test_data/mock_large_file.csv');
      
      // Create content that would exceed typical limits
      const largeContent = 'x,y,z\n' + '1,2,3\n'.repeat(100000); // ~700KB file
      await require('fs').promises.writeFile(mockLargeFile, largeContent);
      
      try {
        // Upload oversized file
        await uploadPage.uploadFile(mockLargeFile);
        
        // Check for size limit error
        await expect(mcpPage.locator('[data-testid="upload-error"]')).toBeVisible({ timeout: 5000 });
        await expect(mcpPage.locator('[data-testid="upload-error"]')).toContainText(/size|limit|large/i);
      } finally {
        // Cleanup mock file
        await require('fs').promises.unlink(mockLargeFile).catch(() => {});
      }
    });
  });

  test.describe('File Upload Error Handling', () => {
    test('should handle network errors during upload', async ({ 
      mcpPage, 
      uploadPage, 
      testFiles, 
      networkMocker 
    }) => {
      // Mock network error
      await networkMocker.mockApiError('/upload', 500);
      
      // Attempt upload
      await uploadPage.uploadFile(testFiles.validMELDData.path);
      
      // Verify error handling
      await expect(mcpPage.locator('[data-testid="upload-error"]')).toBeVisible({ timeout: 10000 });
      await expect(mcpPage.locator('[data-testid="upload-error"]')).toContainText(/network|server|error/i);
      
      // Verify retry option is available
      await expect(mcpPage.locator('[data-testid="upload-retry"]')).toBeVisible();
    });

    test('should provide clear error messages for different error types', async ({ 
      mcpPage, 
      uploadPage, 
      testFiles 
    }) => {
      // Test with file containing wrong headers
      const wrongHeadersFile = resolve(__dirname, '../fixtures/test_data/wrong_headers.csv');
      await require('fs').promises.writeFile(wrongHeadersFile, 'wrong,header,names\n1,2,3\n');
      
      try {
        await uploadPage.uploadFile(wrongHeadersFile);
        
        await expect(mcpPage.locator('[data-testid="upload-error"]')).toBeVisible();
        const errorText = await mcpPage.locator('[data-testid="upload-error"]').textContent();
        expect(errorText).toMatch(/header|column|field/i);
      } finally {
        await require('fs').promises.unlink(wrongHeadersFile).catch(() => {});
      }
    });

    test('should handle timeout scenarios', async ({ 
      mcpPage, 
      uploadPage, 
      testFiles, 
      networkMocker 
    }) => {
      // Mock slow upload response
      await networkMocker.mockFileUpload({ 
        success: false, 
        message: 'Upload timeout' 
      });
      
      // Set shorter timeout for testing
      await mcpPage.addInitScript(() => {
        window.uploadTimeout = 2000; // 2 seconds
      });
      
      await uploadPage.uploadFile(testFiles.validMELDData.path);
      
      // Verify timeout error handling
      await expect(mcpPage.locator('[data-testid="upload-error"]')).toBeVisible({ timeout: 5000 });
      await expect(mcpPage.locator('[data-testid="upload-error"]')).toContainText(/timeout|slow/i);
    });
  });

  test.describe('File Upload User Experience', () => {
    test('should provide clear upload instructions', async ({ 
      mcpPage, 
      visualTester 
    }) => {
      // Verify initial state shows instructions
      await expect(mcpPage.locator('[data-testid="upload-instructions"]')).toBeVisible();
      await expect(mcpPage.locator('[data-testid="upload-instructions"]')).toContainText(/drag.*drop|select.*file/i);
      
      // Verify supported file types are mentioned
      await expect(mcpPage.locator('[data-testid="supported-formats"]')).toContainText(/csv|gcode/i);
      
      // Take screenshot of initial state
      await visualTester.takeScreenshot('upload-initial-instructions');
    });

    test('should show file preview after successful upload', async ({ 
      mcpPage, 
      uploadPage, 
      testFiles, 
      visualTester 
    }) => {
      await uploadPage.uploadFile(testFiles.minimalMELDData.path);
      await mcpPage.waitForSelector('[data-testid="upload-success"]');
      
      // Verify preview shows correct data
      const preview = mcpPage.locator('[data-testid="data-preview"]');
      await expect(preview).toBeVisible();
      
      // Check table headers match expected MELD data columns
      const headers = preview.locator('thead th');
      await expect(headers).toContainText(['Date', 'Time', 'XPos', 'YPos', 'ZPos']);
      
      // Verify data rows are shown
      const dataRows = preview.locator('tbody tr');
      await expect(dataRows).toHaveCount(3); // minimal data has 3 rows
      
      await visualTester.takeScreenshot('upload-data-preview');
    });

    test('should allow file replacement', async ({ 
      mcpPage, 
      uploadPage, 
      testFiles 
    }) => {
      // Upload first file
      await uploadPage.uploadFile(testFiles.minimalMELDData.path);
      await mcpPage.waitForSelector('[data-testid="upload-success"]');
      
      // Verify first file info
      await expect(mcpPage.locator('[data-testid="file-name"]')).toContainText('minimal_meld_data.csv');
      
      // Upload second file (replacement)
      await uploadPage.uploadFile(testFiles.validMELDData.path);
      await mcpPage.waitForSelector('[data-testid="upload-success"]');
      
      // Verify file was replaced
      await expect(mcpPage.locator('[data-testid="file-name"]')).toContainText('valid_meld_data.csv');
      
      // Verify data preview updated
      const dataRows = mcpPage.locator('[data-testid="data-preview"] tbody tr');
      await expect(dataRows).toHaveCount.greaterThan(3); // Should have more rows now
    });

    test('should provide accessible upload controls', async ({ 
      mcpPage 
    }) => {
      // Check keyboard accessibility
      const fileInput = mcpPage.locator('input[type="file"]');
      await expect(fileInput).toHaveAttribute('aria-label');
      
      // Check focus management
      await mcpPage.keyboard.press('Tab');
      await expect(fileInput).toBeFocused();
      
      // Check ARIA attributes on dropzone
      const dropzone = mcpPage.locator('[data-testid="upload-dropzone"]');
      await expect(dropzone).toHaveAttribute('role', 'button');
      await expect(dropzone).toHaveAttribute('tabindex', '0');
    });
  });

  test.describe('Performance and Loading States', () => {
    test('should show appropriate loading states', async ({ 
      mcpPage, 
      uploadPage, 
      testFiles, 
      performanceMonitor 
    }) => {
      performanceMonitor.mark('loading-test-start');
      
      // Start file upload
      const uploadPromise = uploadPage.uploadFile(testFiles.validMELDData.path);
      
      // Verify loading indicator appears quickly
      await expect(mcpPage.locator('[data-testid="upload-loading"]')).toBeVisible({ timeout: 1000 });
      
      // Verify upload button becomes disabled during processing
      await expect(mcpPage.locator('[data-testid="upload-button"]')).toBeDisabled();
      
      // Wait for completion
      await uploadPromise;
      await mcpPage.waitForSelector('[data-testid="upload-success"]');
      
      // Verify loading state is cleared
      await expect(mcpPage.locator('[data-testid="upload-loading"]')).not.toBeVisible();
      await expect(mcpPage.locator('[data-testid="upload-button"]')).toBeEnabled();
      
      performanceMonitor.mark('loading-test-complete');
    });

    test('should handle concurrent upload attempts gracefully', async ({ 
      mcpPage, 
      uploadPage, 
      testFiles 
    }) => {
      // Start first upload
      const firstUpload = uploadPage.uploadFile(testFiles.minimalMELDData.path);
      
      // Immediately try second upload
      await uploadPage.uploadFile(testFiles.validMELDData.path);
      
      // Verify second upload is queued or first is cancelled appropriately
      await expect(mcpPage.locator('[data-testid="upload-queue"], [data-testid="upload-cancelled"]')).toBeVisible({ timeout: 5000 });
      
      // Wait for resolution
      await firstUpload;
      await mcpPage.waitForSelector('[data-testid="upload-success"]');
    });
  });
});