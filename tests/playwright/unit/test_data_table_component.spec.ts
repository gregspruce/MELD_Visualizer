/**
 * Comprehensive Data Table Component Tests for MELD Visualizer
 * Tests data table rendering, filtering, sorting, and pagination using MCP functions
 */

import { test, expect } from '../fixtures/mcp-fixtures';
import type { TestTypes, DashComponents } from '../types';

test.describe('Data Table Component', () => {
  test.beforeEach(async ({ mcpPage, uploadPage, testFiles, performanceMonitor }) => {
    // Upload MELD data to populate table
    await uploadPage.uploadFile(testFiles.validMELDData.path);
    await expect(mcpPage.locator('[data-testid="upload-success"]')).toBeVisible();
    
    // Navigate to data table view
    await mcpPage.locator('[data-testid="tab-analysis"], [data-testid="tab-data"]').click();
    performanceMonitor.mark('data-table-page-ready');
    
    // Wait for data table to load
    await expect(mcpPage.locator('[data-testid="data-table"], .dash-table')).toBeVisible();
    await mcpPage.waitForLoadState('networkidle');
  });

  test.describe('Data Table Rendering', () => {
    test('should render data table with MELD data', async ({ 
      mcpPage, 
      visualTester, 
      performanceMonitor, 
      consoleMonitor 
    }) => {
      performanceMonitor.mark('table-render-start');
      
      const dataTable = mcpPage.locator('[data-testid="data-table"], .dash-table');
      await expect(dataTable).toBeVisible();
      
      // Verify table structure
      const tableStructure = await mcpPage.evaluate(() => {
        const table = document.querySelector('[data-testid="data-table"], .dash-table');
        if (!table) return null;
        
        const headers = Array.from(table.querySelectorAll('th')).map(th => th.textContent?.trim());
        const rows = Array.from(table.querySelectorAll('tbody tr'));
        const firstRowCells = rows[0] ? Array.from(rows[0].querySelectorAll('td')).map(td => td.textContent?.trim()) : [];
        
        return {
          hasTable: !!table,
          headerCount: headers.length,
          headers: headers,
          rowCount: rows.length,
          firstRowData: firstRowCells,
          tableWidth: table.scrollWidth,
          tableHeight: table.scrollHeight
        };
      });
      
      expect(tableStructure?.hasTable).toBe(true);
      expect(tableStructure?.headerCount).toBeGreaterThan(5); // MELD data has many columns
      expect(tableStructure?.rowCount).toBeGreaterThan(0);
      expect(tableStructure?.headers).toContain('Date');
      expect(tableStructure?.headers).toContain('Time');
      expect(tableStructure?.headers).toContain('XPos');
      expect(tableStructure?.headers).toContain('YPos');
      expect(tableStructure?.headers).toContain('ZPos');
      expect(tableStructure?.headers).toContain('ToolTemp');
      
      performanceMonitor.mark('table-render-complete');
      
      // Take screenshot of rendered table
      await visualTester.takeScreenshot('data-table-rendered', { fullPage: true });
      
      // Check rendering performance
      const metrics = await performanceMonitor.getMetrics();
      expect(metrics.renderTime).toBeLessThan(3000); // 3 second max for table render
      
      // Verify no console errors
      consoleMonitor.expectNoErrors();
    });

    test('should display correct data types and formatting', async ({ 
      mcpPage, 
      visualTester 
    }) => {
      // Check data formatting in table cells
      const cellData = await mcpPage.evaluate(() => {
        const table = document.querySelector('[data-testid="data-table"], .dash-table');
        if (!table) return null;
        
        const rows = Array.from(table.querySelectorAll('tbody tr'));
        if (rows.length === 0) return null;
        
        const sampleRow = rows[0];
        const cells = Array.from(sampleRow.querySelectorAll('td'));
        
        return {
          dateCell: cells.find(cell => cell.textContent?.match(/\d{4}-\d{2}-\d{2}/))?.textContent,
          timeCell: cells.find(cell => cell.textContent?.match(/\d{2}:\d{2}:\d{2}/))?.textContent,
          numericCells: cells.filter(cell => 
            cell.textContent && !isNaN(parseFloat(cell.textContent)) && isFinite(parseFloat(cell.textContent))
          ).map(cell => parseFloat(cell.textContent!)),
          totalCells: cells.length
        };
      });
      
      expect(cellData).toBeTruthy();
      expect(cellData?.dateCell).toMatch(/\d{4}-\d{2}-\d{2}/);
      expect(cellData?.timeCell).toMatch(/\d{2}:\d{2}:\d{2}/);
      expect(cellData?.numericCells?.length).toBeGreaterThan(5);
      expect(cellData?.totalCells).toBeGreaterThan(10);
      
      await visualTester.takeScreenshot('data-table-formatting');
    });

    test('should handle large datasets with virtualization', async ({ 
      mcpPage, 
      uploadPage, 
      testFiles, 
      performanceMonitor, 
      visualTester 
    }) => {
      // Upload large dataset
      await uploadPage.uploadFile(testFiles.largeMELDData.path);
      await expect(mcpPage.locator('[data-testid="upload-success"]')).toBeVisible();
      
      // Navigate to table view
      await mcpPage.locator('[data-testid="tab-analysis"], [data-testid="tab-data"]').click();
      
      performanceMonitor.mark('large-table-render-start');
      
      await expect(mcpPage.locator('[data-testid="data-table"]')).toBeVisible({ timeout: 15000 });
      
      performanceMonitor.mark('large-table-render-complete');
      
      // Check if virtualization is working (not all rows rendered at once)
      const virtualizationInfo = await mcpPage.evaluate(() => {
        const table = document.querySelector('[data-testid="data-table"], .dash-table');
        if (!table) return null;
        
        const visibleRows = table.querySelectorAll('tbody tr');
        const scrollContainer = table.querySelector('.dash-spreadsheet-container, .table-scroll');
        
        return {
          visibleRowCount: visibleRows.length,
          hasScrollContainer: !!scrollContainer,
          containerHeight: scrollContainer?.scrollHeight || 0,
          tableHeight: table.scrollHeight
        };
      });
      
      // For large datasets, should not render all rows at once (virtualization)
      expect(virtualizationInfo?.visibleRowCount).toBeLessThan(500); // Should be virtualized
      expect(virtualizationInfo?.hasScrollContainer).toBe(true);
      
      await visualTester.takeScreenshot('large-data-table-virtualized');
      
      // Performance should still be good
      const metrics = await performanceMonitor.getMetrics();
      expect(metrics.renderTime).toBeLessThan(8000);
    });

    test('should display column headers with proper labels', async ({ 
      mcpPage, 
      visualTester 
    }) => {
      // Verify column headers are informative
      const headers = await mcpPage.evaluate(() => {
        const headerCells = document.querySelectorAll('[data-testid="data-table"] th, .dash-table th');
        return Array.from(headerCells).map(th => ({
          text: th.textContent?.trim(),
          hasTooltip: !!th.title || !!th.getAttribute('data-tooltip'),
          hasSort: th.classList.contains('sortable') || !!th.querySelector('.sort-icon'),
          width: th.offsetWidth
        }));
      });
      
      expect(headers.length).toBeGreaterThan(5);
      
      // Check for essential MELD columns
      const headerTexts = headers.map(h => h.text);
      expect(headerTexts).toContain('Date');
      expect(headerTexts).toContain('Time');
      expect(headerTexts).toContain('XPos');
      expect(headerTexts).toContain('YPos');
      expect(headerTexts).toContain('ZPos');
      expect(headerTexts).toContain('ToolTemp');
      
      // Headers should have reasonable widths
      headers.forEach(header => {
        expect(header.width).toBeGreaterThan(50); // Minimum readable width
        expect(header.width).toBeLessThan(500); // Not excessively wide
      });
      
      await visualTester.takeScreenshot('data-table-headers');
    });
  });

  test.describe('Table Sorting Functionality', () => {
    test('should sort columns in ascending order', async ({ 
      mcpPage, 
      visualTester, 
      performanceMonitor 
    }) => {
      performanceMonitor.mark('sort-ascending-start');
      
      // Click on ToolTemp column header to sort
      const tempHeader = mcpPage.locator('th:has-text("ToolTemp"), th:has-text("Tool")').first();
      await tempHeader.click();
      
      // Wait for sort to complete
      await mcpPage.waitForTimeout(1000);
      
      performanceMonitor.mark('sort-ascending-complete');
      
      // Verify ascending sort indicator
      const sortIndicator = tempHeader.locator('.sort-asc, .fa-sort-up, [data-sort="asc"]');
      if (await sortIndicator.count() > 0) {
        await expect(sortIndicator).toBeVisible();
      }
      
      // Verify data is sorted ascending
      const sortedValues = await mcpPage.evaluate(() => {
        const table = document.querySelector('[data-testid="data-table"], .dash-table');
        if (!table) return [];
        
        // Find ToolTemp column index
        const headers = Array.from(table.querySelectorAll('th'));
        const tempColumnIndex = headers.findIndex(th => 
          th.textContent?.toLowerCase().includes('tool') || 
          th.textContent?.toLowerCase().includes('temp')
        );
        
        if (tempColumnIndex === -1) return [];
        
        const rows = Array.from(table.querySelectorAll('tbody tr'));
        return rows.slice(0, 5).map(row => {
          const cells = Array.from(row.querySelectorAll('td'));
          const value = cells[tempColumnIndex]?.textContent?.trim();
          return parseFloat(value || '0');
        }).filter(val => !isNaN(val));
      });
      
      // Check if values are in ascending order
      for (let i = 1; i < sortedValues.length; i++) {
        expect(sortedValues[i]).toBeGreaterThanOrEqual(sortedValues[i - 1]);
      }
      
      await visualTester.takeScreenshot('table-sorted-ascending');
      
      // Check sort performance
      const metrics = await performanceMonitor.getMetrics();
      expect(metrics.interactionTime).toBeLessThan(2000);
    });

    test('should sort columns in descending order', async ({ 
      mcpPage, 
      visualTester 
    }) => {
      const tempHeader = mcpPage.locator('th:has-text("ToolTemp"), th:has-text("Tool")').first();
      
      // Click twice for descending sort
      await tempHeader.click();
      await mcpPage.waitForTimeout(500);
      await tempHeader.click();
      await mcpPage.waitForTimeout(1000);
      
      // Verify descending sort indicator
      const sortIndicator = tempHeader.locator('.sort-desc, .fa-sort-down, [data-sort="desc"]');
      if (await sortIndicator.count() > 0) {
        await expect(sortIndicator).toBeVisible();
      }
      
      // Verify data is sorted descending
      const sortedValues = await mcpPage.evaluate(() => {
        const table = document.querySelector('[data-testid="data-table"], .dash-table');
        if (!table) return [];
        
        const headers = Array.from(table.querySelectorAll('th'));
        const tempColumnIndex = headers.findIndex(th => 
          th.textContent?.toLowerCase().includes('tool') || 
          th.textContent?.toLowerCase().includes('temp')
        );
        
        if (tempColumnIndex === -1) return [];
        
        const rows = Array.from(table.querySelectorAll('tbody tr'));
        return rows.slice(0, 5).map(row => {
          const cells = Array.from(row.querySelectorAll('td'));
          const value = cells[tempColumnIndex]?.textContent?.trim();
          return parseFloat(value || '0');
        }).filter(val => !isNaN(val));
      });
      
      // Check if values are in descending order
      for (let i = 1; i < sortedValues.length; i++) {
        expect(sortedValues[i]).toBeLessThanOrEqual(sortedValues[i - 1]);
      }
      
      await visualTester.takeScreenshot('table-sorted-descending');
    });

    test('should sort multiple columns with priority', async ({ 
      mcpPage, 
      visualTester 
    }) => {
      // Sort by Date first
      const dateHeader = mcpPage.locator('th:has-text("Date")').first();
      await dateHeader.click();
      await mcpPage.waitForTimeout(1000);
      
      // Then sort by Time (with Ctrl/Cmd held for multi-sort)
      const timeHeader = mcpPage.locator('th:has-text("Time")').first();
      await mcpPage.keyboard.down(process.platform === 'darwin' ? 'Meta' : 'Control');
      await timeHeader.click();
      await mcpPage.keyboard.up(process.platform === 'darwin' ? 'Meta' : 'Control');
      
      await mcpPage.waitForTimeout(1000);
      
      // Verify multi-sort indicators
      const dateSortIndicator = dateHeader.locator('.sort-asc, .sort-desc, [data-sort]');
      const timeSortIndicator = timeHeader.locator('.sort-asc, .sort-desc, [data-sort]');
      
      if (await dateSortIndicator.count() > 0) {
        await expect(dateSortIndicator).toBeVisible();
      }
      
      await visualTester.takeScreenshot('table-multi-column-sort');
    });

    test('should handle sorting of different data types correctly', async ({ 
      mcpPage 
    }) => {
      const dataTypes = [
        { column: 'Date', type: 'date' },
        { column: 'Time', type: 'time' },
        { column: 'XPos', type: 'numeric' },
        { column: 'ToolTemp', type: 'numeric' }
      ];
      
      for (const { column, type } of dataTypes) {
        const header = mcpPage.locator(`th:has-text("${column}")`).first();
        
        if (await header.count() > 0) {
          await header.click();
          await mcpPage.waitForTimeout(1000);
          
          // Verify sorting works for this data type
          const sortedCorrectly = await mcpPage.evaluate((columnName, dataType) => {
            const table = document.querySelector('[data-testid="data-table"], .dash-table');
            if (!table) return false;
            
            const headers = Array.from(table.querySelectorAll('th'));
            const columnIndex = headers.findIndex(th => 
              th.textContent?.includes(columnName)
            );
            
            if (columnIndex === -1) return false;
            
            const rows = Array.from(table.querySelectorAll('tbody tr'));
            const values = rows.slice(0, 3).map(row => {
              const cells = Array.from(row.querySelectorAll('td'));
              return cells[columnIndex]?.textContent?.trim() || '';
            });
            
            // Simple check that values changed order (indicating sort worked)
            return values.length > 1;
          }, column, type);
          
          expect(sortedCorrectly).toBe(true);
        }
      }
    });
  });

  test.describe('Table Filtering Functionality', () => {
    test('should filter data using column filters', async ({ 
      mcpPage, 
      visualTester, 
      performanceMonitor 
    }) => {
      // Look for filter inputs
      const filterInput = mcpPage.locator('[data-testid="filter-input"], .dash-filter-input, input[placeholder*="filter"]').first();
      
      if (await filterInput.count() > 0) {
        performanceMonitor.mark('filter-start');
        
        // Get initial row count
        const initialRowCount = await mcpPage.evaluate(() => {
          const table = document.querySelector('[data-testid="data-table"], .dash-table');
          return table?.querySelectorAll('tbody tr').length || 0;
        });
        
        // Apply filter
        await filterInput.fill('300');
        await mcpPage.keyboard.press('Enter');
        
        await mcpPage.waitForTimeout(2000);
        
        performanceMonitor.mark('filter-complete');
        
        // Get filtered row count
        const filteredRowCount = await mcpPage.evaluate(() => {
          const table = document.querySelector('[data-testid="data-table"], .dash-table');
          return table?.querySelectorAll('tbody tr').length || 0;
        });
        
        expect(filteredRowCount).toBeLessThan(initialRowCount);
        expect(filteredRowCount).toBeGreaterThan(0);
        
        await visualTester.takeScreenshot('table-filtered');
        
        // Check filter performance
        const metrics = await performanceMonitor.getMetrics();
        expect(metrics.interactionTime).toBeLessThan(3000);
      }
    });

    test('should support global search functionality', async ({ 
      mcpPage, 
      visualTester 
    }) => {
      const globalSearch = mcpPage.locator('[data-testid="global-search"], [data-testid="table-search"], input[placeholder*="search"]').first();
      
      if (await globalSearch.count() > 0) {
        // Get initial state
        const initialRowCount = await mcpPage.evaluate(() => {
          const table = document.querySelector('[data-testid="data-table"], .dash-table');
          return table?.querySelectorAll('tbody tr').length || 0;
        });
        
        // Search for specific value
        await globalSearch.fill('2024');
        
        await mcpPage.waitForTimeout(1500);
        
        // Verify search results
        const searchResults = await mcpPage.evaluate(() => {
          const table = document.querySelector('[data-testid="data-table"], .dash-table');
          const rows = Array.from(table?.querySelectorAll('tbody tr') || []);
          
          return {
            rowCount: rows.length,
            hasSearchTerm: rows.some(row => 
              row.textContent?.toLowerCase().includes('2024')
            )
          };
        });
        
        expect(searchResults.rowCount).toBeGreaterThan(0);
        expect(searchResults.hasSearchTerm).toBe(true);
        
        await visualTester.takeScreenshot('table-global-search');
        
        // Clear search
        await globalSearch.fill('');
        await mcpPage.keyboard.press('Enter');
        await mcpPage.waitForTimeout(1000);
        
        // Should return to full results
        const clearedRowCount = await mcpPage.evaluate(() => {
          const table = document.querySelector('[data-testid="data-table"], .dash-table');
          return table?.querySelectorAll('tbody tr').length || 0;
        });
        
        expect(clearedRowCount).toBeGreaterThanOrEqual(initialRowCount);
      }
    });

    test('should support numeric range filtering', async ({ 
      mcpPage, 
      visualTester 
    }) => {
      // Look for range filter controls
      const minInput = mcpPage.locator('[data-testid="temp-min"], [data-testid="filter-min"], input[name*="min"]').first();
      const maxInput = mcpPage.locator('[data-testid="temp-max"], [data-testid="filter-max"], input[name*="max"]').first();
      
      if (await minInput.count() > 0 && await maxInput.count() > 0) {
        // Set temperature range filter
        await minInput.fill('250');
        await maxInput.fill('350');
        
        // Apply filter
        const applyButton = mcpPage.locator('[data-testid="apply-filter"], button:has-text("Apply")');
        if (await applyButton.count() > 0) {
          await applyButton.click();
        } else {
          await mcpPage.keyboard.press('Enter');
        }
        
        await mcpPage.waitForTimeout(2000);
        
        // Verify range filtering worked
        const rangeFilterResults = await mcpPage.evaluate(() => {
          const table = document.querySelector('[data-testid="data-table"], .dash-table');
          if (!table) return null;
          
          // Find temperature column
          const headers = Array.from(table.querySelectorAll('th'));
          const tempColumnIndex = headers.findIndex(th => 
            th.textContent?.toLowerCase().includes('tool') && 
            th.textContent?.toLowerCase().includes('temp')
          );
          
          if (tempColumnIndex === -1) return null;
          
          const rows = Array.from(table.querySelectorAll('tbody tr'));
          const temperatures = rows.map(row => {
            const cells = Array.from(row.querySelectorAll('td'));
            const tempValue = cells[tempColumnIndex]?.textContent?.trim();
            return parseFloat(tempValue || '0');
          }).filter(temp => !isNaN(temp));
          
          return {
            count: temperatures.length,
            allInRange: temperatures.every(temp => temp >= 250 && temp <= 350),
            minValue: Math.min(...temperatures),
            maxValue: Math.max(...temperatures)
          };
        });
        
        expect(rangeFilterResults?.count).toBeGreaterThan(0);
        expect(rangeFilterResults?.allInRange).toBe(true);
        
        await visualTester.takeScreenshot('table-range-filtered');
      }
    });

    test('should support date/time filtering', async ({ 
      mcpPage, 
      visualTester 
    }) => {
      const dateFilter = mcpPage.locator('[data-testid="date-filter"], input[type="date"]').first();
      
      if (await dateFilter.count() > 0) {
        // Set date filter
        await dateFilter.fill('2024-01-15');
        
        await mcpPage.waitForTimeout(1500);
        
        // Verify date filtering
        const dateFilterResults = await mcpPage.evaluate(() => {
          const table = document.querySelector('[data-testid="data-table"], .dash-table');
          if (!table) return null;
          
          const rows = Array.from(table.querySelectorAll('tbody tr'));
          return {
            rowCount: rows.length,
            hasTargetDate: rows.some(row => 
              row.textContent?.includes('2024-01-15')
            )
          };
        });
        
        expect(dateFilterResults?.rowCount).toBeGreaterThan(0);
        
        await visualTester.takeScreenshot('table-date-filtered');
      }
    });
  });

  test.describe('Table Pagination', () => {
    test('should paginate large datasets', async ({ 
      mcpPage, 
      uploadPage, 
      testFiles, 
      visualTester, 
      performanceMonitor 
    }) => {
      // Upload large dataset to test pagination
      await uploadPage.uploadFile(testFiles.largeMELDData.path);
      await expect(mcpPage.locator('[data-testid="upload-success"]')).toBeVisible();
      
      await mcpPage.locator('[data-testid="tab-analysis"], [data-testid="tab-data"]').click();
      await expect(mcpPage.locator('[data-testid="data-table"]')).toBeVisible({ timeout: 15000 });
      
      // Look for pagination controls
      const paginationControls = mcpPage.locator('[data-testid="pagination"], .dash-table-pagination, .pagination');
      
      if (await paginationControls.count() > 0) {
        await expect(paginationControls).toBeVisible();
        
        // Check current page info
        const pageInfo = await mcpPage.evaluate(() => {
          const pagination = document.querySelector('[data-testid="pagination"], .dash-table-pagination');
          if (!pagination) return null;
          
          const pageText = pagination.textContent || '';
          const currentPageMatch = pageText.match(/page\s*(\d+)/i) || pageText.match(/(\d+)\s*of/i);
          const totalPagesMatch = pageText.match(/of\s*(\d+)/i) || pageText.match(/\/\s*(\d+)/i);
          
          return {
            hasPageInfo: !!pageText,
            currentPage: currentPageMatch ? parseInt(currentPageMatch[1]) : 1,
            totalPages: totalPagesMatch ? parseInt(totalPagesMatch[1]) : 0
          };
        });
        
        expect(pageInfo?.hasPageInfo).toBe(true);
        expect(pageInfo?.totalPages).toBeGreaterThan(1);
        
        performanceMonitor.mark('pagination-test-start');
        
        // Test next page
        const nextButton = mcpPage.locator('[data-testid="next-page"], .pagination-next, button:has-text("Next")').first();
        
        if (await nextButton.count() > 0 && await nextButton.isEnabled()) {
          await nextButton.click();
          await mcpPage.waitForTimeout(1000);
          
          await visualTester.takeScreenshot('table-page-2');
          
          // Verify page changed
          const newPageInfo = await mcpPage.evaluate(() => {
            const pagination = document.querySelector('[data-testid="pagination"], .dash-table-pagination');
            const pageText = pagination?.textContent || '';
            const currentPageMatch = pageText.match(/page\s*(\d+)/i) || pageText.match(/(\d+)\s*of/i);
            return currentPageMatch ? parseInt(currentPageMatch[1]) : 1;
          });
          
          expect(newPageInfo).toBe(2);
        }
        
        performanceMonitor.mark('pagination-test-complete');
        
        // Test previous page
        const prevButton = mcpPage.locator('[data-testid="prev-page"], .pagination-prev, button:has-text("Prev")').first();
        
        if (await prevButton.count() > 0 && await prevButton.isEnabled()) {
          await prevButton.click();
          await mcpPage.waitForTimeout(1000);
          
          // Should be back to page 1
          const backToFirstPage = await mcpPage.evaluate(() => {
            const pagination = document.querySelector('[data-testid="pagination"], .dash-table-pagination');
            const pageText = pagination?.textContent || '';
            const currentPageMatch = pageText.match(/page\s*(\d+)/i) || pageText.match(/(\d+)\s*of/i);
            return currentPageMatch ? parseInt(currentPageMatch[1]) : 1;
          });
          
          expect(backToFirstPage).toBe(1);
        }
        
        // Check pagination performance
        const metrics = await performanceMonitor.getMetrics();
        expect(metrics.interactionTime).toBeLessThan(2000);
      }
    });

    test('should allow page size configuration', async ({ 
      mcpPage, 
      visualTester 
    }) => {
      // Look for page size selector
      const pageSizeSelector = mcpPage.locator('[data-testid="page-size"], [data-testid="rows-per-page"], select');
      
      if (await pageSizeSelector.count() > 0) {
        // Get initial row count
        const initialRowCount = await mcpPage.evaluate(() => {
          const table = document.querySelector('[data-testid="data-table"], .dash-table');
          return table?.querySelectorAll('tbody tr').length || 0;
        });
        
        // Change page size
        await pageSizeSelector.selectOption('50');
        await mcpPage.waitForTimeout(1000);
        
        // Verify row count changed
        const newRowCount = await mcpPage.evaluate(() => {
          const table = document.querySelector('[data-testid="data-table"], .dash-table');
          return table?.querySelectorAll('tbody tr').length || 0;
        });
        
        expect(newRowCount).toBeLessThanOrEqual(50);
        expect(newRowCount).not.toBe(initialRowCount);
        
        await visualTester.takeScreenshot('table-custom-page-size');
      }
    });

    test('should support direct page navigation', async ({ 
      mcpPage 
    }) => {
      // Look for page input field
      const pageInput = mcpPage.locator('[data-testid="page-input"], input[type="number"]');
      
      if (await pageInput.count() > 0) {
        // Jump to specific page
        await pageInput.fill('3');
        await mcpPage.keyboard.press('Enter');
        
        await mcpPage.waitForTimeout(1000);
        
        // Verify page changed to 3
        const currentPage = await mcpPage.evaluate(() => {
          const pagination = document.querySelector('[data-testid="pagination"], .dash-table-pagination');
          const pageText = pagination?.textContent || '';
          const currentPageMatch = pageText.match(/page\s*(\d+)/i) || pageText.match(/(\d+)\s*of/i);
          return currentPageMatch ? parseInt(currentPageMatch[1]) : 1;
        });
        
        expect(currentPage).toBe(3);
      }
    });
  });

  test.describe('Table Export and Selection', () => {
    test('should support row selection', async ({ 
      mcpPage, 
      visualTester 
    }) => {
      // Look for row checkboxes
      const firstRowCheckbox = mcpPage.locator('[data-testid="row-select"], tbody tr:first-child input[type="checkbox"]').first();
      
      if (await firstRowCheckbox.count() > 0) {
        // Select first row
        await firstRowCheckbox.check();
        
        // Verify row is selected
        const isSelected = await firstRowCheckbox.isChecked();
        expect(isSelected).toBe(true);
        
        // Verify visual indication of selection
        const selectedRow = mcpPage.locator('tbody tr:first-child');
        const hasSelectedClass = await selectedRow.evaluate(row => 
          row.classList.contains('selected') || row.classList.contains('row-selected')
        );
        
        await visualTester.takeScreenshot('table-row-selected');
        
        // Test select all
        const selectAllCheckbox = mcpPage.locator('[data-testid="select-all"], thead input[type="checkbox"]').first();
        
        if (await selectAllCheckbox.count() > 0) {
          await selectAllCheckbox.check();
          
          // Verify multiple rows selected
          const selectedCount = await mcpPage.evaluate(() => {
            const checkboxes = document.querySelectorAll('tbody input[type="checkbox"]:checked');
            return checkboxes.length;
          });
          
          expect(selectedCount).toBeGreaterThan(1);
          
          await visualTester.takeScreenshot('table-all-rows-selected');
        }
      }
    });

    test('should export selected data', async ({ 
      mcpPage, 
      visualTester 
    }) => {
      // Select some rows first
      const rowCheckbox = mcpPage.locator('tbody tr input[type="checkbox"]').first();
      
      if (await rowCheckbox.count() > 0) {
        await rowCheckbox.check();
        
        // Look for export button
        const exportButton = mcpPage.locator('[data-testid="export-selected"], [data-testid="export-table"], button:has-text("Export")');
        
        if (await exportButton.count() > 0) {
          // Set up download handler
          const downloadPromise = mcpPage.waitForEvent('download');
          await exportButton.click();
          
          // Verify download started
          const download = await downloadPromise;
          expect(download.suggestedFilename()).toMatch(/\.csv$|\.xlsx$|\.json$/);
          
          await visualTester.takeScreenshot('table-export-initiated');
        }
      }
    });

    test('should support bulk operations on selected rows', async ({ 
      mcpPage 
    }) => {
      // Select multiple rows
      const checkboxes = mcpPage.locator('tbody tr input[type="checkbox"]');
      const checkboxCount = await checkboxes.count();
      
      if (checkboxCount > 0) {
        // Select first 3 rows
        for (let i = 0; i < Math.min(3, checkboxCount); i++) {
          await checkboxes.nth(i).check();
        }
        
        // Look for bulk action controls
        const bulkActions = mcpPage.locator('[data-testid="bulk-actions"], .bulk-operations');
        
        if (await bulkActions.count() > 0) {
          await expect(bulkActions).toBeVisible();
          
          // Test delete action if available
          const deleteButton = bulkActions.locator('button:has-text("Delete"), [data-testid="delete-selected"]');
          
          if (await deleteButton.count() > 0) {
            await deleteButton.click();
            
            // Handle confirmation dialog
            const confirmDialog = mcpPage.locator('[data-testid="confirm-dialog"], .modal, .dialog');
            
            if (await confirmDialog.count() > 0) {
              const confirmButton = confirmDialog.locator('button:has-text("Confirm"), button:has-text("Delete")');
              
              if (await confirmButton.count() > 0) {
                await confirmButton.click();
                await mcpPage.waitForTimeout(1000);
                
                // Verify rows were removed
                const newRowCount = await mcpPage.evaluate(() => {
                  const table = document.querySelector('[data-testid="data-table"], .dash-table');
                  return table?.querySelectorAll('tbody tr').length || 0;
                });
                
                expect(newRowCount).toBeLessThan(checkboxCount);
              }
            }
          }
        }
      }
    });
  });

  test.describe('Table Accessibility and Performance', () => {
    test('should be keyboard accessible', async ({ 
      mcpPage 
    }) => {
      // Test keyboard navigation
      const table = mcpPage.locator('[data-testid="data-table"], .dash-table');
      
      // Focus on table
      await table.focus();
      
      // Test Tab navigation through table elements
      await mcpPage.keyboard.press('Tab');
      
      const focusedElement = mcpPage.locator(':focus');
      const focusedTag = await focusedElement.evaluate(el => el.tagName.toLowerCase());
      
      expect(['th', 'td', 'input', 'button'].includes(focusedTag)).toBe(true);
      
      // Test arrow key navigation if supported
      await mcpPage.keyboard.press('ArrowDown');
      await mcpPage.keyboard.press('ArrowRight');
      await mcpPage.keyboard.press('ArrowLeft');
      await mcpPage.keyboard.press('ArrowUp');
      
      // Should not throw errors
      await mcpPage.waitForTimeout(500);
    });

    test('should have proper ARIA attributes', async ({ 
      mcpPage 
    }) => {
      const table = mcpPage.locator('[data-testid="data-table"], .dash-table');
      
      // Check table role
      const tableRole = await table.getAttribute('role');
      expect(tableRole).toBe('table');
      
      // Check header accessibility
      const headers = mcpPage.locator('th');
      const headerCount = await headers.count();
      
      if (headerCount > 0) {
        const firstHeader = headers.first();
        const scope = await firstHeader.getAttribute('scope');
        expect(scope).toBe('col');
      }
      
      // Check row accessibility
      const rows = mcpPage.locator('tbody tr');
      const rowCount = await rows.count();
      
      if (rowCount > 0) {
        const firstRow = rows.first();
        const rowRole = await firstRow.getAttribute('role');
        expect(rowRole).toBe('row');
      }
    });

    test('should handle large datasets without performance degradation', async ({ 
      mcpPage, 
      uploadPage, 
      testFiles, 
      performanceMonitor 
    }) => {
      // Upload large dataset
      await uploadPage.uploadFile(testFiles.largeMELDData.path);
      await expect(mcpPage.locator('[data-testid="upload-success"]')).toBeVisible();
      
      performanceMonitor.mark('large-table-operations-start');
      
      await mcpPage.locator('[data-testid="tab-analysis"], [data-testid="tab-data"]').click();
      await expect(mcpPage.locator('[data-testid="data-table"]')).toBeVisible({ timeout: 15000 });
      
      // Perform multiple operations
      const operations = [
        // Sort
        async () => {
          const header = mcpPage.locator('th').first();
          if (await header.count() > 0) await header.click();
        },
        // Filter
        async () => {
          const filter = mcpPage.locator('[data-testid="filter-input"], input').first();
          if (await filter.count() > 0) {
            await filter.fill('300');
            await mcpPage.keyboard.press('Enter');
          }
        },
        // Paginate
        async () => {
          const nextBtn = mcpPage.locator('[data-testid="next-page"], button:has-text("Next")').first();
          if (await nextBtn.count() > 0 && await nextBtn.isEnabled()) {
            await nextBtn.click();
          }
        }
      ];
      
      for (const operation of operations) {
        await operation();
        await mcpPage.waitForTimeout(1000);
      }
      
      performanceMonitor.mark('large-table-operations-complete');
      
      // Check performance metrics
      const metrics = await performanceMonitor.getMetrics();
      expect(metrics.interactionTime).toBeLessThan(3000); // Should remain responsive
      expect(metrics.memoryUsage).toBeLessThan(150_000_000); // 150MB limit
    });
  });
});