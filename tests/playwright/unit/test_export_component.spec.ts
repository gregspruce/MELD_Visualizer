/**
 * Comprehensive Export Functionality Component Tests for MELD Visualizer
 * Tests export buttons, formats, progress, and file validation using MCP functions
 */

import { test, expect } from '../fixtures/mcp-fixtures';
import type { TestTypes } from '../types';
import { resolve } from 'path';

test.describe('Export Functionality Component', () => {
  test.beforeEach(async ({ mcpPage, uploadPage, testFiles, performanceMonitor }) => {
    // Upload MELD data to enable export functionality
    await uploadPage.uploadFile(testFiles.validMELDData.path);
    await expect(mcpPage.locator('[data-testid="upload-success"]')).toBeVisible();

    performanceMonitor.mark('export-page-ready');

    // Navigate to visualization tab to enable various export options
    await mcpPage.locator('[data-testid="tab-visualization"]').click();
    await expect(mcpPage.locator('[data-testid="graph-container"]')).toBeVisible({ timeout: 15000 });

    // Wait for all components to be ready
    await mcpPage.waitForLoadState('networkidle');
  });

  test.describe('Export Button Functionality', () => {
    test('should display export buttons for different content types', async ({
      mcpPage,
      visualTester
    }) => {
      // Look for various export buttons
      const exportButtons = await mcpPage.evaluate(() => {
        const buttons = Array.from(document.querySelectorAll(
          '[data-testid*="export"], [data-testid*="download"], button:has-text("Export"), button:has-text("Download")'
        ));

        return buttons.map(btn => ({
          text: btn.textContent?.trim(),
          testId: btn.getAttribute('data-testid'),
          enabled: !btn.hasAttribute('disabled'),
          visible: btn.offsetWidth > 0 && btn.offsetHeight > 0
        }));
      });

      expect(exportButtons.length).toBeGreaterThan(0);

      // Should have export options for different components
      const expectedExports = ['data', 'graph', 'chart', 'table', 'visualization'];
      const hasRelevantExports = exportButtons.some(btn =>
        expectedExports.some(exp =>
          btn.text?.toLowerCase().includes(exp) ||
          btn.testId?.toLowerCase().includes(exp)
        )
      );

      expect(hasRelevantExports).toBe(true);

      await visualTester.takeScreenshot('export-buttons-available');
    });

    test('should enable export buttons only when data is available', async ({
      mcpPage,
      visualTester
    }) => {
      // Check export button states with data
      const exportButtonWithData = mcpPage.locator('[data-testid="export-data"], [data-testid="export-button"], button:has-text("Export")').first();

      if (await exportButtonWithData.count() > 0) {
        await expect(exportButtonWithData).toBeEnabled();

        // Clear data by navigating to upload and clearing
        await mcpPage.locator('[data-testid="tab-upload"]').click();

        const clearButton = mcpPage.locator('[data-testid="clear-data"], button:has-text("Clear")');
        if (await clearButton.count() > 0) {
          await clearButton.click();

          // Export button should be disabled without data
          await expect(exportButtonWithData).toBeDisabled();

          await visualTester.takeScreenshot('export-buttons-disabled-no-data');
        }
      }
    });

    test('should show export options dropdown when clicked', async ({
      mcpPage,
      visualTester
    }) => {
      const exportDropdown = mcpPage.locator('[data-testid="export-dropdown"], .export-dropdown');
      const exportButton = mcpPage.locator('[data-testid="export-button"], button:has-text("Export")').first();

      if (await exportButton.count() > 0) {
        await exportButton.click();

        // Look for dropdown menu or modal
        const exportOptions = mcpPage.locator('[data-testid="export-options"], .export-menu, .dropdown-menu');

        if (await exportOptions.count() > 0) {
          await expect(exportOptions).toBeVisible();

          // Should show different format options
          const formatOptions = await mcpPage.evaluate(() => {
            const options = Array.from(document.querySelectorAll(
              '[data-testid*="export-"], .export-option, .dropdown-item'
            ));

            return options.map(opt => opt.textContent?.trim()).filter(Boolean);
          });

          expect(formatOptions.length).toBeGreaterThan(1);

          await visualTester.takeScreenshot('export-options-dropdown');
        }
      }
    });
  });

  test.describe('Export Format Support', () => {
    test('should export data as CSV format', async ({
      mcpPage,
      visualTester,
      performanceMonitor
    }) => {
      performanceMonitor.mark('csv-export-start');

      // Look for CSV export option
      const csvExportButton = mcpPage.locator('[data-testid="export-csv"], [data-value="csv"], button:has-text("CSV")');

      if (await csvExportButton.count() > 0) {
        // Set up download handler
        const downloadPromise = mcpPage.waitForEvent('download');

        await csvExportButton.click();

        // Wait for download
        const download = await downloadPromise;

        performanceMonitor.mark('csv-export-complete');

        // Verify download properties
        expect(download.suggestedFilename()).toMatch(/\.csv$/);

        // Save and validate file content
        const downloadPath = resolve(__dirname, '../downloads', download.suggestedFilename());
        await download.saveAs(downloadPath);

        // Read and validate CSV content
        const csvContent = await require('fs').promises.readFile(downloadPath, 'utf-8');

        expect(csvContent.length).toBeGreaterThan(100);
        expect(csvContent.split('\n').length).toBeGreaterThan(5); // Should have multiple rows
        expect(csvContent).toContain('Date'); // Should have expected headers
        expect(csvContent).toContain('Time');
        expect(csvContent).toContain('XPos');

        await visualTester.takeScreenshot('csv-export-completed');

        // Check export performance
        const metrics = await performanceMonitor.getMetrics();
        expect(metrics.interactionTime).toBeLessThan(5000);

        // Cleanup
        await require('fs').promises.unlink(downloadPath).catch(() => {});
      }
    });

    test('should export data as Excel format', async ({
      mcpPage,
      performanceMonitor
    }) => {
      const excelExportButton = mcpPage.locator('[data-testid="export-excel"], [data-testid="export-xlsx"], [data-value="xlsx"], button:has-text("Excel")');

      if (await excelExportButton.count() > 0) {
        performanceMonitor.mark('excel-export-start');

        const downloadPromise = mcpPage.waitForEvent('download');
        await excelExportButton.click();

        const download = await downloadPromise;

        performanceMonitor.mark('excel-export-complete');

        // Verify Excel file properties
        expect(download.suggestedFilename()).toMatch(/\.(xlsx|xls)$/);

        const downloadPath = resolve(__dirname, '../downloads', download.suggestedFilename());
        await download.saveAs(downloadPath);

        // Verify file exists and has reasonable size
        const stats = await require('fs').promises.stat(downloadPath);
        expect(stats.size).toBeGreaterThan(1000); // Excel files should be substantial

        // Check export performance
        const metrics = await performanceMonitor.getMetrics();
        expect(metrics.interactionTime).toBeLessThan(8000); // Excel export may take longer

        // Cleanup
        await require('fs').promises.unlink(downloadPath).catch(() => {});
      }
    });

    test('should export data as JSON format', async ({
      mcpPage,
      visualTester
    }) => {
      const jsonExportButton = mcpPage.locator('[data-testid="export-json"], [data-value="json"], button:has-text("JSON")');

      if (await jsonExportButton.count() > 0) {
        const downloadPromise = mcpPage.waitForEvent('download');
        await jsonExportButton.click();

        const download = await downloadPromise;

        expect(download.suggestedFilename()).toMatch(/\.json$/);

        const downloadPath = resolve(__dirname, '../downloads', download.suggestedFilename());
        await download.saveAs(downloadPath);

        // Validate JSON content
        const jsonContent = await require('fs').promises.readFile(downloadPath, 'utf-8');
        const parsedJson = JSON.parse(jsonContent); // Should parse without error

        expect(Array.isArray(parsedJson)).toBe(true);
        expect(parsedJson.length).toBeGreaterThan(0);

        // Verify JSON structure contains expected fields
        if (parsedJson.length > 0) {
          const firstRecord = parsedJson[0];
          expect(firstRecord).toHaveProperty('Date');
          expect(firstRecord).toHaveProperty('XPos');
          expect(firstRecord).toHaveProperty('YPos');
        }

        await visualTester.takeScreenshot('json-export-completed');

        // Cleanup
        await require('fs').promises.unlink(downloadPath).catch(() => {});
      }
    });

    test('should export visualization as image formats', async ({
      mcpPage,
      visualTester
    }) => {
      // Look for image export options (usually for graphs)
      const imageFormats = ['PNG', 'SVG', 'PDF'];

      for (const format of imageFormats) {
        const imageExportButton = mcpPage.locator(`[data-testid="export-${format.toLowerCase()}"], [data-value="${format.toLowerCase()}"], button:has-text("${format}")`);

        if (await imageExportButton.count() > 0) {
          const downloadPromise = mcpPage.waitForEvent('download');
          await imageExportButton.click();

          const download = await downloadPromise;

          expect(download.suggestedFilename()).toMatch(new RegExp(`\\.${format.toLowerCase()}$`));

          const downloadPath = resolve(__dirname, '../downloads', download.suggestedFilename());
          await download.saveAs(downloadPath);

          // Verify file exists and has content
          const stats = await require('fs').promises.stat(downloadPath);
          expect(stats.size).toBeGreaterThan(500); // Image files should have reasonable size

          await visualTester.takeScreenshot(`${format.toLowerCase()}-export-completed`);

          // Cleanup
          await require('fs').promises.unlink(downloadPath).catch(() => {});
        }
      }
    });
  });

  test.describe('Export Progress and Feedback', () => {
    test('should show progress indicator during large exports', async ({
      mcpPage,
      uploadPage,
      testFiles,
      visualTester,
      performanceMonitor
    }) => {
      // Upload large dataset
      await uploadPage.uploadFile(testFiles.largeMELDData.path);
      await expect(mcpPage.locator('[data-testid="upload-success"]')).toBeVisible();

      // Navigate back to visualization
      await mcpPage.locator('[data-testid="tab-visualization"]').click();
      await expect(mcpPage.locator('[data-testid="graph-container"]')).toBeVisible({ timeout: 20000 });

      performanceMonitor.mark('large-export-start');

      const exportButton = mcpPage.locator('[data-testid="export-csv"], [data-testid="export-data"], button:has-text("Export")').first();

      if (await exportButton.count() > 0) {
        // Start export
        const downloadPromise = mcpPage.waitForEvent('download');
        await exportButton.click();

        // Look for progress indicators quickly after clicking
        const progressIndicator = mcpPage.locator('[data-testid="export-progress"], .export-loading, .progress-bar');

        if (await progressIndicator.count() > 0) {
          await expect(progressIndicator).toBeVisible({ timeout: 2000 });

          await visualTester.takeScreenshot('export-progress-indicator');

          // Progress should eventually complete
          await expect(progressIndicator).not.toBeVisible({ timeout: 30000 });
        }

        // Export should complete
        const download = await downloadPromise;
        expect(download).toBeTruthy();

        performanceMonitor.mark('large-export-complete');

        // Large export should complete within reasonable time
        const metrics = await performanceMonitor.getMetrics();
        expect(metrics.loadTime).toBeLessThan(30000); // 30 second max
      }
    });

    test('should show success confirmation after export', async ({
      mcpPage,
      visualTester
    }) => {
      const exportButton = mcpPage.locator('[data-testid="export-csv"], button:has-text("Export")').first();

      if (await exportButton.count() > 0) {
        const downloadPromise = mcpPage.waitForEvent('download');
        await exportButton.click();

        await downloadPromise; // Wait for download to complete

        // Look for success message
        const successMessage = mcpPage.locator('[data-testid="export-success"], [data-testid="download-success"], .success-message');

        if (await successMessage.count() > 0) {
          await expect(successMessage).toBeVisible();
          await expect(successMessage).toContainText(/success|complete|download/i);

          await visualTester.takeScreenshot('export-success-message');

          // Success message should eventually disappear
          await expect(successMessage).not.toBeVisible({ timeout: 10000 });
        }
      }
    });

    test('should provide export status information', async ({
      mcpPage,
      visualTester
    }) => {
      const exportButton = mcpPage.locator('[data-testid="export-button"], button:has-text("Export")').first();

      if (await exportButton.count() > 0) {
        await exportButton.click();

        // Look for status information
        const statusInfo = mcpPage.locator('[data-testid="export-status"], .export-info');

        if (await statusInfo.count() > 0) {
          const statusText = await statusInfo.textContent();

          // Should contain useful information
          expect(statusText).toMatch(/preparing|processing|rows|records|size/i);

          await visualTester.takeScreenshot('export-status-info');
        }
      }
    });
  });

  test.describe('Export Error Handling', () => {
    test('should handle export failures gracefully', async ({
      mcpPage,
      networkMocker,
      visualTester,
      consoleMonitor
    }) => {
      // Mock export API to fail
      await networkMocker.mockApiError('/export', 500);
      await networkMocker.mockApiError('/_dash-update-component', 500);

      const exportButton = mcpPage.locator('[data-testid="export-csv"], button:has-text("Export")').first();

      if (await exportButton.count() > 0) {
        await exportButton.click();

        // Should show error message
        const errorMessage = mcpPage.locator('[data-testid="export-error"], [data-testid="error-message"], .error');

        if (await errorMessage.count() > 0) {
          await expect(errorMessage).toBeVisible({ timeout: 10000 });
          await expect(errorMessage).toContainText(/error|failed|problem/i);

          await visualTester.takeScreenshot('export-error-message');

          // Should provide retry option
          const retryButton = mcpPage.locator('[data-testid="retry-export"], button:has-text("Retry")');

          if (await retryButton.count() > 0) {
            await expect(retryButton).toBeVisible();
          }
        }

        // Should handle error gracefully without breaking the app
        const errors = consoleMonitor.getErrors().filter(error =>
          !error.text.includes('500') && !error.text.includes('network')
        );
        expect(errors.length).toBeLessThan(3); // Some export errors expected
      }
    });

    test('should validate export prerequisites', async ({
      mcpPage,
      visualTester
    }) => {
      // Try to export without sufficient data
      await mcpPage.locator('[data-testid="tab-upload"]').click();

      // Clear existing data
      const clearButton = mcpPage.locator('[data-testid="clear-data"], button:has-text("Clear")');
      if (await clearButton.count() > 0) {
        await clearButton.click();
      }

      // Try to export with no data
      const exportButton = mcpPage.locator('[data-testid="export-button"], button:has-text("Export")');

      if (await exportButton.count() > 0) {
        await exportButton.click();

        // Should show validation message
        const validationMessage = mcpPage.locator('[data-testid="validation-error"], .validation-message');

        if (await validationMessage.count() > 0) {
          await expect(validationMessage).toBeVisible();
          await expect(validationMessage).toContainText(/no data|empty|select/i);

          await visualTester.takeScreenshot('export-validation-error');
        } else {
          // Export button should be disabled
          await expect(exportButton).toBeDisabled();
        }
      }
    });

    test('should handle unsupported browser features', async ({
      mcpPage,
      consoleMonitor
    }) => {
      // Disable download API to simulate unsupported browser
      await mcpPage.addInitScript(() => {
        // Override download functionality
        const originalCreateElement = document.createElement;
        document.createElement = function(tagName: string) {
          const element = originalCreateElement.call(this, tagName);
          if (tagName.toLowerCase() === 'a') {
            Object.defineProperty(element, 'download', {
              set: function() {
                throw new Error('Download not supported');
              },
              get: function() {
                return undefined;
              }
            });
          }
          return element;
        };
      });

      const exportButton = mcpPage.locator('[data-testid="export-csv"], button:has-text("Export")').first();

      if (await exportButton.count() > 0) {
        await exportButton.click();

        // Should fallback to alternative method or show appropriate message
        const fallbackMessage = mcpPage.locator('[data-testid="browser-not-supported"], .fallback-message');

        if (await fallbackMessage.count() > 0) {
          await expect(fallbackMessage).toContainText(/browser|support|alternative/i);
        }

        // Should not crash the application
        const criticalErrors = consoleMonitor.getErrors().filter(error =>
          error.text.includes('TypeError') && !error.text.includes('Download not supported')
        );
        expect(criticalErrors.length).toBe(0);
      }
    });
  });

  test.describe('Export Customization and Options', () => {
    test('should allow export range selection', async ({
      mcpPage,
      visualTester
    }) => {
      // Look for export options dialog
      const exportOptionsButton = mcpPage.locator('[data-testid="export-options"], [data-testid="advanced-export"], button:has-text("Options")');

      if (await exportOptionsButton.count() > 0) {
        await exportOptionsButton.click();

        // Look for range selection options
        const rangeOptions = mcpPage.locator('[data-testid="export-range"], .range-selection');

        if (await rangeOptions.count() > 0) {
          await expect(rangeOptions).toBeVisible();

          // Should have options like "All data", "Current page", "Selected rows"
          const rangeChoices = await mcpPage.evaluate(() => {
            const options = Array.from(document.querySelectorAll(
              'input[name*="range"], .range-option'
            ));
            return options.map(opt => opt.textContent || opt.getAttribute('value')).filter(Boolean);
          });

          expect(rangeChoices.length).toBeGreaterThan(1);

          await visualTester.takeScreenshot('export-range-options');

          // Test selecting specific range
          const currentPageOption = mcpPage.locator('input[value="current"], label:has-text("Current")').first();

          if (await currentPageOption.count() > 0) {
            await currentPageOption.click();

            // Apply and export
            const exportWithRangeButton = mcpPage.locator('[data-testid="export-with-range"], button:has-text("Export")');

            if (await exportWithRangeButton.count() > 0) {
              const downloadPromise = mcpPage.waitForEvent('download');
              await exportWithRangeButton.click();

              const download = await downloadPromise;
              expect(download).toBeTruthy();
            }
          }
        }
      }
    });

    test('should support column selection for export', async ({
      mcpPage,
      visualTester
    }) => {
      const columnSelectionButton = mcpPage.locator('[data-testid="select-columns"], [data-testid="column-options"], button:has-text("Columns")');

      if (await columnSelectionButton.count() > 0) {
        await columnSelectionButton.click();

        // Should show column checkboxes
        const columnCheckboxes = mcpPage.locator('[data-testid*="column-"], input[type="checkbox"]');
        const checkboxCount = await columnCheckboxes.count();

        if (checkboxCount > 0) {
          // Uncheck some columns
          await columnCheckboxes.first().uncheck();
          await columnCheckboxes.nth(1).uncheck();

          await visualTester.takeScreenshot('export-column-selection');

          // Export with selected columns
          const exportSelectedButton = mcpPage.locator('[data-testid="export-selected-columns"], button:has-text("Export Selected")');

          if (await exportSelectedButton.count() > 0) {
            const downloadPromise = mcpPage.waitForEvent('download');
            await exportSelectedButton.click();

            const download = await downloadPromise;

            // Validate that exported file has fewer columns
            const downloadPath = resolve(__dirname, '../downloads', download.suggestedFilename());
            await download.saveAs(downloadPath);

            if (download.suggestedFilename().endsWith('.csv')) {
              const csvContent = await require('fs').promises.readFile(downloadPath, 'utf-8');
              const headers = csvContent.split('\n')[0].split(',');

              // Should have fewer columns than total available
              expect(headers.length).toBeLessThan(checkboxCount);
            }

            // Cleanup
            await require('fs').promises.unlink(downloadPath).catch(() => {});
          }
        }
      }
    });

    test('should allow format-specific options', async ({
      mcpPage,
      visualTester
    }) => {
      // Look for format-specific options
      const csvOptionsButton = mcpPage.locator('[data-testid="csv-options"], button:has-text("CSV Options")');

      if (await csvOptionsButton.count() > 0) {
        await csvOptionsButton.click();

        // Should show CSV-specific options
        const csvOptions = await mcpPage.evaluate(() => {
          const options = Array.from(document.querySelectorAll(
            '[data-testid*="delimiter"], [data-testid*="encoding"], input, select'
          ));

          return options.map(opt => ({
            type: opt.tagName.toLowerCase(),
            name: opt.getAttribute('name'),
            value: (opt as HTMLInputElement).value || (opt as HTMLSelectElement).value
          })).filter(opt => opt.name);
        });

        expect(csvOptions.length).toBeGreaterThan(0);

        // Test delimiter option
        const delimiterSelect = mcpPage.locator('[data-testid="delimiter"], select[name*="delimiter"]');

        if (await delimiterSelect.count() > 0) {
          await delimiterSelect.selectOption('semicolon');

          await visualTester.takeScreenshot('export-csv-options');

          // Export with custom delimiter
          const exportCustomButton = mcpPage.locator('[data-testid="export-custom"], button:has-text("Export")');

          if (await exportCustomButton.count() > 0) {
            const downloadPromise = mcpPage.waitForEvent('download');
            await exportCustomButton.click();

            const download = await downloadPromise;

            // Validate delimiter in exported file
            const downloadPath = resolve(__dirname, '../downloads', download.suggestedFilename());
            await download.saveAs(downloadPath);

            const csvContent = await require('fs').promises.readFile(downloadPath, 'utf-8');
            expect(csvContent).toContain(';'); // Should use semicolon delimiter

            // Cleanup
            await require('fs').promises.unlink(downloadPath).catch(() => {});
          }
        }
      }
    });
  });

  test.describe('Export Performance and Quality', () => {
    test('should maintain export quality with large datasets', async ({
      mcpPage,
      uploadPage,
      testFiles,
      performanceMonitor
    }) => {
      // Upload large dataset
      await uploadPage.uploadFile(testFiles.largeMELDData.path);
      await expect(mcpPage.locator('[data-testid="upload-success"]')).toBeVisible();

      performanceMonitor.mark('quality-export-start');

      const exportButton = mcpPage.locator('[data-testid="export-csv"], button:has-text("Export")').first();

      if (await exportButton.count() > 0) {
        const downloadPromise = mcpPage.waitForEvent('download');
        await exportButton.click();

        const download = await downloadPromise;

        performanceMonitor.mark('quality-export-complete');

        const downloadPath = resolve(__dirname, '../downloads', download.suggestedFilename());
        await download.saveAs(downloadPath);

        // Validate export quality
        if (download.suggestedFilename().endsWith('.csv')) {
          const csvContent = await require('fs').promises.readFile(downloadPath, 'utf-8');
          const lines = csvContent.split('\n').filter(line => line.trim());

          // Should have substantial number of rows
          expect(lines.length).toBeGreaterThan(500);

          // Should have consistent structure
          const headerCount = lines[0].split(',').length;
          const sampleRow = lines[Math.floor(lines.length / 2)];
          const sampleRowCount = sampleRow.split(',').length;

          expect(sampleRowCount).toBe(headerCount);

          // Should contain proper numeric data
          const numericValues = sampleRow.split(',').slice(2, 5).map(val => parseFloat(val));
          const validNumbers = numericValues.filter(val => !isNaN(val));

          expect(validNumbers.length).toBeGreaterThan(0);
        }

        // Check performance for large export
        const metrics = await performanceMonitor.getMetrics();
        expect(metrics.loadTime).toBeLessThan(30000); // 30 second max

        // Cleanup
        await require('fs').promises.unlink(downloadPath).catch(() => {});
      }
    });

    test('should handle concurrent export requests', async ({
      mcpPage,
      consoleMonitor
    }) => {
      const exportButtons = mcpPage.locator('[data-testid*="export-"], button:has-text("Export")');
      const buttonCount = await exportButtons.count();

      if (buttonCount > 1) {
        // Start multiple exports quickly
        const downloadPromises = [];

        for (let i = 0; i < Math.min(3, buttonCount); i++) {
          const downloadPromise = mcpPage.waitForEvent('download');
          await exportButtons.nth(i).click();
          downloadPromises.push(downloadPromise);

          // Small delay to avoid simultaneous clicks
          await mcpPage.waitForTimeout(200);
        }

        // Wait for all downloads to complete or timeout
        const results = await Promise.allSettled(
          downloadPromises.map(p =>
            Promise.race([
              p,
              new Promise((_, reject) => setTimeout(() => reject(new Error('timeout')), 15000))
            ])
          )
        );

        // At least one export should succeed
        const successes = results.filter(r => r.status === 'fulfilled');
        expect(successes.length).toBeGreaterThan(0);

        // Should handle concurrent requests without errors
        const errors = consoleMonitor.getErrors().filter(error =>
          !error.text.includes('timeout') && !error.text.includes('network')
        );
        expect(errors.length).toBeLessThan(5);
      }
    });

    test('should validate exported file integrity', async ({
      mcpPage,
      visualTester
    }) => {
      const exportButton = mcpPage.locator('[data-testid="export-csv"], button:has-text("Export")').first();

      if (await exportButton.count() > 0) {
        const downloadPromise = mcpPage.waitForEvent('download');
        await exportButton.click();

        const download = await downloadPromise;
        const downloadPath = resolve(__dirname, '../downloads', download.suggestedFilename());
        await download.saveAs(downloadPath);

        // Validate file integrity
        const stats = await require('fs').promises.stat(downloadPath);
        expect(stats.size).toBeGreaterThan(0);

        if (download.suggestedFilename().endsWith('.csv')) {
          const csvContent = await require('fs').promises.readFile(downloadPath, 'utf-8');

          // Should not have truncated content
          expect(csvContent.endsWith('\n') || csvContent.split('\n').pop()?.length === 0).toBe(false);

          // Should have proper CSV structure
          const lines = csvContent.split('\n').filter(line => line.trim());
          expect(lines.length).toBeGreaterThan(1); // Header + data

          // All data rows should have same number of columns as header
          const headerCols = lines[0].split(',').length;
          const dataRows = lines.slice(1);

          const invalidRows = dataRows.filter(row => row.split(',').length !== headerCols);
          expect(invalidRows.length).toBe(0);
        }

        await visualTester.takeScreenshot('export-integrity-validated');

        // Cleanup
        await require('fs').promises.unlink(downloadPath).catch(() => {});
      }
    });
  });
});
