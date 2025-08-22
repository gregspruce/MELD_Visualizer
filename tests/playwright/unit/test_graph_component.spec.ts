/**
 * Comprehensive Plotly Graph Component Tests for MELD Visualizer
 * Tests 3D graph rendering, interactions, and performance using MCP functions
 */

import { test, expect } from '../fixtures/mcp-fixtures';
import type { TestTypes, PlotlyTypes } from '../types';

test.describe('Plotly Graph Component', () => {
  test.beforeEach(async ({ mcpPage, uploadPage, testFiles, performanceMonitor }) => {
    // Upload MELD data to enable graph functionality
    await uploadPage.uploadFile(testFiles.validMELDData.path);
    await expect(mcpPage.locator('[data-testid="upload-success"]')).toBeVisible();
    
    // Navigate to visualization tab
    await mcpPage.locator('[data-testid="tab-visualization"]').click();
    performanceMonitor.mark('graph-page-ready');
    
    // Wait for graph to initialize
    await expect(mcpPage.locator('[data-testid="graph-container"]')).toBeVisible();
    await mcpPage.waitForLoadState('networkidle');
  });

  test.describe('3D Graph Rendering', () => {
    test('should render 3D MELD visualization successfully', async ({ 
      mcpPage, 
      visualTester, 
      performanceMonitor, 
      consoleMonitor 
    }) => {
      performanceMonitor.mark('3d-render-start');
      
      // Wait for Plotly graph to fully render
      await visualTester.waitForPlotlyGraph('.js-plotly-plot', { 
        timeout: 15000,
        waitForData: true 
      });
      
      performanceMonitor.mark('3d-render-complete');
      
      // Verify Plotly graph is present and has 3D data
      const plotlyElement = mcpPage.locator('.js-plotly-plot');
      await expect(plotlyElement).toBeVisible();
      
      // Check 3D graph properties
      const graph3DInfo = await mcpPage.evaluate(() => {
        const plotElement = document.querySelector('.js-plotly-plot') as any;
        if (!plotElement?._fullData || !plotElement._fullLayout) {
          return { hasData: false, is3D: false, traceCount: 0 };
        }
        
        const traces = plotElement._fullData;
        const layout = plotElement._fullLayout;
        
        return {
          hasData: traces.length > 0,
          is3D: traces.some((trace: any) => trace.type === 'scatter3d' || trace.type === 'surface' || trace.type === 'mesh3d'),
          traceCount: traces.length,
          hasXYZAxes: !!(layout.scene?.xaxis && layout.scene?.yaxis && layout.scene?.zaxis),
          dimensions: traces[0] ? {
            x: Array.isArray(traces[0].x) ? traces[0].x.length : 0,
            y: Array.isArray(traces[0].y) ? traces[0].y.length : 0,
            z: Array.isArray(traces[0].z) ? traces[0].z.length : 0
          } : null
        };
      });
      
      expect(graph3DInfo.hasData).toBe(true);
      expect(graph3DInfo.is3D).toBe(true);
      expect(graph3DInfo.traceCount).toBeGreaterThan(0);
      expect(graph3DInfo.hasXYZAxes).toBe(true);
      expect(graph3DInfo.dimensions?.x).toBeGreaterThan(0);
      
      // Take screenshot of rendered 3D graph
      await visualTester.takeScreenshot('3d-graph-rendered', { fullPage: true });
      
      // Check rendering performance
      const metrics = await performanceMonitor.getMetrics();
      expect(metrics.renderTime).toBeLessThan(10000); // 10 second max for initial render
      
      // Verify no console errors during rendering
      consoleMonitor.expectNoErrors();
    });

    test('should display proper axis labels and titles', async ({ 
      mcpPage, 
      visualTester 
    }) => {
      await visualTester.waitForPlotlyGraph();
      
      // Check axis labels and graph title
      const graphLabels = await mcpPage.evaluate(() => {
        const plotElement = document.querySelector('.js-plotly-plot') as any;
        if (!plotElement?._fullLayout?.scene) return null;
        
        const scene = plotElement._fullLayout.scene;
        
        return {
          title: plotElement._fullLayout.title?.text || '',
          xAxisTitle: scene.xaxis?.title?.text || '',
          yAxisTitle: scene.yaxis?.title?.text || '',
          zAxisTitle: scene.zaxis?.title?.text || '',
          hasColorbar: !!plotElement._fullLayout.coloraxis || 
                      plotElement._fullData.some((trace: any) => trace.colorbar)
        };
      });
      
      expect(graphLabels).toBeTruthy();
      expect(graphLabels?.title).toBeTruthy();
      expect(graphLabels?.xAxisTitle).toMatch(/position|x|coordinate/i);
      expect(graphLabels?.yAxisTitle).toMatch(/position|y|coordinate/i);
      expect(graphLabels?.zAxisTitle).toMatch(/position|z|coordinate|height/i);
      
      await visualTester.takeScreenshot('graph-labels-and-titles');
    });

    test('should render different visualization modes', async ({ 
      mcpPage, 
      visualTester, 
      performanceMonitor 
    }) => {
      const visualizationModes = ['scatter', 'surface', 'heatmap'];
      
      for (const mode of visualizationModes) {
        const modeSelector = mcpPage.locator(`[data-testid="viz-mode-${mode}"], [data-value="${mode}"]`);
        
        if (await modeSelector.count() > 0) {
          performanceMonitor.mark(`${mode}-render-start`);
          
          // Switch visualization mode
          await modeSelector.click();
          
          // Wait for re-render
          await mcpPage.waitForTimeout(1000);
          await visualTester.waitForPlotlyGraph();
          
          performanceMonitor.mark(`${mode}-render-complete`);
          
          // Verify mode changed
          const currentMode = await mcpPage.evaluate((expectedMode) => {
            const plotElement = document.querySelector('.js-plotly-plot') as any;
            if (!plotElement?._fullData) return null;
            
            const traces = plotElement._fullData;
            return {
              mode: expectedMode,
              traceTypes: traces.map((trace: any) => trace.type),
              traceCount: traces.length
            };
          }, mode);
          
          expect(currentMode).toBeTruthy();
          expect(currentMode?.traceCount).toBeGreaterThan(0);
          
          await visualTester.takeScreenshot(`graph-${mode}-mode`);
          
          // Check render performance for each mode
          const metrics = await performanceMonitor.getMetrics();
          expect(metrics.renderTime).toBeLessThan(5000);
        }
      }
    });

    test('should handle large datasets efficiently', async ({ 
      mcpPage, 
      uploadPage, 
      testFiles, 
      performanceMonitor, 
      visualTester 
    }) => {
      // Upload large dataset
      await uploadPage.uploadFile(testFiles.largeMELDData.path);
      await expect(mcpPage.locator('[data-testid="upload-success"]')).toBeVisible();
      
      performanceMonitor.mark('large-dataset-render-start');
      
      // Navigate to visualization
      await mcpPage.locator('[data-testid="tab-visualization"]').click();
      await visualTester.waitForPlotlyGraph('.js-plotly-plot', { 
        timeout: 30000,
        waitForData: true 
      });
      
      performanceMonitor.mark('large-dataset-render-complete');
      
      // Verify large dataset handling
      const dataInfo = await mcpPage.evaluate(() => {
        const plotElement = document.querySelector('.js-plotly-plot') as any;
        if (!plotElement?._fullData) return null;
        
        const trace = plotElement._fullData[0];
        return {
          pointCount: trace?.x?.length || 0,
          hasDownsampling: trace?.marker?.size !== undefined,
          renderMode: trace?.mode || trace?.type
        };
      });
      
      expect(dataInfo?.pointCount).toBeGreaterThan(500); // Large dataset
      
      // Performance should still be reasonable
      const metrics = await performanceMonitor.getMetrics();
      expect(metrics.renderTime).toBeLessThan(15000); // 15 second max for large dataset
      
      await visualTester.takeScreenshot('graph-large-dataset');
    });
  });

  test.describe('Graph Interactions', () => {
    test('should support zoom interactions', async ({ 
      mcpPage, 
      visualTester, 
      performanceMonitor 
    }) => {
      await visualTester.waitForPlotlyGraph();
      
      const plotlyGraph = mcpPage.locator('.js-plotly-plot');
      
      // Get initial camera position
      const initialCamera = await mcpPage.evaluate(() => {
        const plotElement = document.querySelector('.js-plotly-plot') as any;
        return plotElement?._fullLayout?.scene?.camera;
      });
      
      performanceMonitor.mark('zoom-interaction-start');
      
      // Perform zoom by scrolling
      await plotlyGraph.hover();
      await mcpPage.mouse.wheel(0, -200); // Zoom in
      
      await mcpPage.waitForTimeout(500);
      
      // Verify zoom changed
      const zoomedCamera = await mcpPage.evaluate(() => {
        const plotElement = document.querySelector('.js-plotly-plot') as any;
        return plotElement?._fullLayout?.scene?.camera;
      });
      
      expect(zoomedCamera).not.toEqual(initialCamera);
      
      performanceMonitor.mark('zoom-interaction-complete');
      
      await visualTester.takeScreenshot('graph-zoomed-in');
      
      // Test zoom out
      await mcpPage.mouse.wheel(0, 200);
      await mcpPage.waitForTimeout(500);
      
      await visualTester.takeScreenshot('graph-zoomed-out');
      
      // Check interaction responsiveness
      const metrics = await performanceMonitor.getMetrics();
      expect(metrics.interactionTime).toBeLessThan(500);
    });

    test('should support pan interactions', async ({ 
      mcpPage, 
      visualTester 
    }) => {
      await visualTester.waitForPlotlyGraph();
      
      const plotlyGraph = mcpPage.locator('.js-plotly-plot');
      
      // Get graph bounds
      const graphBounds = await plotlyGraph.boundingBox();
      expect(graphBounds).toBeTruthy();
      
      const centerX = graphBounds!.x + graphBounds!.width / 2;
      const centerY = graphBounds!.y + graphBounds!.height / 2;
      
      // Get initial camera position
      const initialCamera = await mcpPage.evaluate(() => {
        const plotElement = document.querySelector('.js-plotly-plot') as any;
        return plotElement?._fullLayout?.scene?.camera;
      });
      
      // Perform pan by dragging
      await mcpPage.mouse.move(centerX, centerY);
      await mcpPage.mouse.down();
      await mcpPage.mouse.move(centerX + 50, centerY + 50);
      await mcpPage.mouse.up();
      
      await mcpPage.waitForTimeout(500);
      
      // Verify pan changed view
      const pannedCamera = await mcpPage.evaluate(() => {
        const plotElement = document.querySelector('.js-plotly-plot') as any;
        return plotElement?._fullLayout?.scene?.camera;
      });
      
      expect(pannedCamera).not.toEqual(initialCamera);
      
      await visualTester.takeScreenshot('graph-panned');
    });

    test('should support rotation interactions', async ({ 
      mcpPage, 
      visualTester, 
      performanceMonitor 
    }) => {
      await visualTester.waitForPlotlyGraph();
      
      const plotlyGraph = mcpPage.locator('.js-plotly-plot');
      const graphBounds = await plotlyGraph.boundingBox();
      
      const centerX = graphBounds!.x + graphBounds!.width / 2;
      const centerY = graphBounds!.y + graphBounds!.height / 2;
      
      performanceMonitor.mark('rotation-start');
      
      // Get initial camera angles
      const initialCamera = await mcpPage.evaluate(() => {
        const plotElement = document.querySelector('.js-plotly-plot') as any;
        return plotElement?._fullLayout?.scene?.camera;
      });
      
      // Perform rotation by dragging in circular motion
      await mcpPage.mouse.move(centerX, centerY);
      await mcpPage.mouse.down({ button: 'left' });
      
      // Circular motion for rotation
      const radius = 30;
      const steps = 8;
      for (let i = 0; i < steps; i++) {
        const angle = (i / steps) * Math.PI * 2;
        const x = centerX + Math.cos(angle) * radius;
        const y = centerY + Math.sin(angle) * radius;
        await mcpPage.mouse.move(x, y);
        await mcpPage.waitForTimeout(50);
      }
      
      await mcpPage.mouse.up();
      await mcpPage.waitForTimeout(500);
      
      performanceMonitor.mark('rotation-complete');
      
      // Verify rotation changed view
      const rotatedCamera = await mcpPage.evaluate(() => {
        const plotElement = document.querySelector('.js-plotly-plot') as any;
        return plotElement?._fullLayout?.scene?.camera;
      });
      
      expect(rotatedCamera.eye).not.toEqual(initialCamera.eye);
      
      await visualTester.takeScreenshot('graph-rotated');
      
      // Check rotation performance
      const metrics = await performanceMonitor.getMetrics();
      expect(metrics.interactionTime).toBeLessThan(1000);
    });

    test('should support toolbar interactions', async ({ 
      mcpPage, 
      visualTester 
    }) => {
      await visualTester.waitForPlotlyGraph();
      
      // Verify toolbar is visible
      const toolbar = mcpPage.locator('.modebar, [data-testid="plotly-toolbar"]');
      await expect(toolbar).toBeVisible();
      
      // Test zoom reset button
      const resetZoomBtn = mcpPage.locator('.modebar-btn[data-title*="Reset"], .modebar-btn[data-title*="Autoscale"]');
      if (await resetZoomBtn.count() > 0) {
        await resetZoomBtn.click();
        await mcpPage.waitForTimeout(500);
        await visualTester.takeScreenshot('graph-zoom-reset');
      }
      
      // Test pan tool
      const panBtn = mcpPage.locator('.modebar-btn[data-title*="Pan"]');
      if (await panBtn.count() > 0) {
        await panBtn.click();
        await visualTester.takeScreenshot('graph-pan-mode');
        
        // Verify pan mode is active
        const isPanActive = await panBtn.evaluate((btn) => {
          return btn.classList.contains('active') || btn.getAttribute('data-pressed') === 'true';
        });
        expect(isPanActive).toBe(true);
      }
      
      // Test download button
      const downloadBtn = mcpPage.locator('.modebar-btn[data-title*="Download"], .modebar-btn[data-title*="download"]');
      if (await downloadBtn.count() > 0) {
        // Set up download handler
        const downloadPromise = mcpPage.waitForEvent('download');
        await downloadBtn.click();
        
        // Verify download initiated
        const download = await downloadPromise;
        expect(download.suggestedFilename()).toMatch(/\.png$|\.svg$|\.pdf$/);
      }
    });

    test('should display tooltips on data points', async ({ 
      mcpPage, 
      visualTester 
    }) => {
      await visualTester.waitForPlotlyGraph();
      
      const plotlyGraph = mcpPage.locator('.js-plotly-plot');
      
      // Find data points to hover over
      const dataPoints = await mcpPage.evaluate(() => {
        const plotElement = document.querySelector('.js-plotly-plot') as any;
        if (!plotElement?._fullData) return [];
        
        // Get some sample points from the first trace
        const trace = plotElement._fullData[0];
        if (!trace.x || !trace.y) return [];
        
        return [
          { x: trace.x[0], y: trace.y[0], z: trace.z?.[0] },
          { x: trace.x[Math.floor(trace.x.length / 2)], y: trace.y[Math.floor(trace.y.length / 2)], z: trace.z?.[Math.floor((trace.z?.length || 0) / 2)] }
        ].filter(point => point.x !== undefined && point.y !== undefined);
      });
      
      expect(dataPoints.length).toBeGreaterThan(0);
      
      // Hover over a data point
      const graphBounds = await plotlyGraph.boundingBox();
      const centerX = graphBounds!.x + graphBounds!.width / 2;
      const centerY = graphBounds!.y + graphBounds!.height / 2;
      
      await mcpPage.mouse.move(centerX, centerY);
      await mcpPage.waitForTimeout(500);
      
      // Look for tooltip/hover info
      const tooltip = mcpPage.locator('.hovertext, .plotly-tooltip, [data-testid="tooltip"]');
      
      // May not always be visible, but if it is, it should contain data
      if (await tooltip.count() > 0) {
        await expect(tooltip).toBeVisible();
        const tooltipText = await tooltip.textContent();
        expect(tooltipText).toBeTruthy();
        
        await visualTester.takeScreenshot('graph-tooltip-visible');
      }
    });
  });

  test.describe('Graph Controls and Configuration', () => {
    test('should allow axis range configuration', async ({ 
      mcpPage, 
      visualTester 
    }) => {
      await visualTester.waitForPlotlyGraph();
      
      // Look for axis controls
      const axisControls = mcpPage.locator('[data-testid="axis-controls"], [data-testid="range-controls"]');
      
      if (await axisControls.count() > 0) {
        // Test X-axis range
        const xMinInput = mcpPage.locator('[data-testid="x-min"], input[name*="x"][name*="min"]');
        const xMaxInput = mcpPage.locator('[data-testid="x-max"], input[name*="x"][name*="max"]');
        
        if (await xMinInput.count() > 0 && await xMaxInput.count() > 0) {
          await xMinInput.fill('-10');
          await xMaxInput.fill('10');
          
          // Apply changes
          const applyBtn = mcpPage.locator('[data-testid="apply-range"], button:has-text("Apply")');
          if (await applyBtn.count() > 0) {
            await applyBtn.click();
          } else {
            await mcpPage.keyboard.press('Enter');
          }
          
          await mcpPage.waitForTimeout(1000);
          
          // Verify axis range changed
          const axisRange = await mcpPage.evaluate(() => {
            const plotElement = document.querySelector('.js-plotly-plot') as any;
            return plotElement?._fullLayout?.scene?.xaxis?.range;
          });
          
          if (axisRange) {
            expect(axisRange[0]).toBeCloseTo(-10, 1);
            expect(axisRange[1]).toBeCloseTo(10, 1);
          }
          
          await visualTester.takeScreenshot('graph-custom-axis-range');
        }
      }
    });

    test('should support colormap/colorscale changes', async ({ 
      mcpPage, 
      visualTester 
    }) => {
      await visualTester.waitForPlotlyGraph();
      
      // Look for colormap selector
      const colormapSelector = mcpPage.locator('[data-testid="colormap-selector"], [data-testid="colorscale-selector"]');
      
      if (await colormapSelector.count() > 0) {
        // Get available colormap options
        await colormapSelector.click();
        
        const colormapOptions = mcpPage.locator('[data-testid^="colormap-"], option');
        const optionCount = await colormapOptions.count();
        
        if (optionCount > 1) {
          // Select a different colormap
          await colormapOptions.nth(1).click();
          
          await mcpPage.waitForTimeout(1000);
          
          // Verify colorscale changed
          const colorscale = await mcpPage.evaluate(() => {
            const plotElement = document.querySelector('.js-plotly-plot') as any;
            if (!plotElement?._fullData) return null;
            
            const trace = plotElement._fullData[0];
            return trace.colorscale || trace.colorbar?.colorscale;
          });
          
          expect(colorscale).toBeTruthy();
          
          await visualTester.takeScreenshot('graph-custom-colormap');
        }
      }
    });

    test('should allow data filtering/selection', async ({ 
      mcpPage, 
      visualTester 
    }) => {
      await visualTester.waitForPlotlyGraph();
      
      // Look for data filter controls
      const filterControls = mcpPage.locator('[data-testid="data-filters"], [data-testid="selection-controls"]');
      
      if (await filterControls.count() > 0) {
        // Test temperature range filter
        const tempMinSlider = mcpPage.locator('[data-testid="temp-min"], input[type="range"][name*="temp"]');
        const tempMaxSlider = mcpPage.locator('[data-testid="temp-max"], input[type="range"][name*="temp"]');
        
        if (await tempMinSlider.count() > 0) {
          // Get initial point count
          const initialPointCount = await mcpPage.evaluate(() => {
            const plotElement = document.querySelector('.js-plotly-plot') as any;
            return plotElement?._fullData?.[0]?.x?.length || 0;
          });
          
          // Adjust filter
          await tempMinSlider.fill('300');
          
          if (await tempMaxSlider.count() > 0) {
            await tempMaxSlider.fill('400');
          }
          
          // Wait for filter to apply
          await mcpPage.waitForTimeout(1000);
          
          // Verify point count changed
          const filteredPointCount = await mcpPage.evaluate(() => {
            const plotElement = document.querySelector('.js-plotly-plot') as any;
            return plotElement?._fullData?.[0]?.x?.length || 0;
          });
          
          expect(filteredPointCount).not.toBe(initialPointCount);
          expect(filteredPointCount).toBeGreaterThan(0);
          
          await visualTester.takeScreenshot('graph-data-filtered');
        }
      }
    });

    test('should handle legend interactions', async ({ 
      mcpPage, 
      visualTester 
    }) => {
      await visualTester.waitForPlotlyGraph();
      
      // Look for legend
      const legend = mcpPage.locator('.legend, [data-testid="plotly-legend"]');
      
      if (await legend.count() > 0) {
        await expect(legend).toBeVisible();
        
        // Find legend items
        const legendItems = mcpPage.locator('.legendtext, .legend-item');
        const itemCount = await legendItems.count();
        
        if (itemCount > 0) {
          // Click on first legend item to toggle visibility
          await legendItems.first().click();
          await mcpPage.waitForTimeout(500);
          
          await visualTester.takeScreenshot('graph-legend-toggled');
          
          // Double-click to isolate trace
          await legendItems.first().dblclick();
          await mcpPage.waitForTimeout(500);
          
          await visualTester.takeScreenshot('graph-trace-isolated');
        }
      }
    });
  });

  test.describe('Graph Performance and Optimization', () => {
    test('should maintain smooth performance during interactions', async ({ 
      mcpPage, 
      performanceMonitor, 
      visualTester 
    }) => {
      await visualTester.waitForPlotlyGraph();
      
      const plotlyGraph = mcpPage.locator('.js-plotly-plot');
      const graphBounds = await plotlyGraph.boundingBox();
      
      performanceMonitor.mark('performance-test-start');
      
      // Perform multiple rapid interactions
      const centerX = graphBounds!.x + graphBounds!.width / 2;
      const centerY = graphBounds!.y + graphBounds!.height / 2;
      
      // Zoom operations
      for (let i = 0; i < 5; i++) {
        await mcpPage.mouse.move(centerX, centerY);
        await mcpPage.mouse.wheel(0, -100);
        await mcpPage.waitForTimeout(100);
      }
      
      // Pan operations
      await mcpPage.mouse.move(centerX, centerY);
      await mcpPage.mouse.down();
      for (let i = 0; i < 10; i++) {
        await mcpPage.mouse.move(centerX + i * 5, centerY + i * 3);
        await mcpPage.waitForTimeout(50);
      }
      await mcpPage.mouse.up();
      
      performanceMonitor.mark('performance-test-complete');
      
      // Check performance metrics
      const metrics = await performanceMonitor.getMetrics();
      expect(metrics.interactionTime).toBeLessThan(100); // Should remain responsive
      expect(metrics.cpuUsage).toBeLessThan(90); // Should not max out CPU
      
      await visualTester.takeScreenshot('graph-after-intensive-interactions');
    });

    test('should handle memory efficiently with large datasets', async ({ 
      mcpPage, 
      uploadPage, 
      testFiles, 
      performanceMonitor 
    }) => {
      // Upload large dataset
      await uploadPage.uploadFile(testFiles.largeMELDData.path);
      await expect(mcpPage.locator('[data-testid="upload-success"]')).toBeVisible();
      
      performanceMonitor.mark('large-memory-test-start');
      
      // Navigate to visualization
      await mcpPage.locator('[data-testid="tab-visualization"]').click();
      await visualTester.waitForPlotlyGraph('.js-plotly-plot', { timeout: 30000 });
      
      // Perform memory-intensive operations
      for (let i = 0; i < 3; i++) {
        // Switch visualization modes
        const modeSelector = mcpPage.locator('[data-testid="viz-mode-surface"], [data-value="surface"]');
        if (await modeSelector.count() > 0) {
          await modeSelector.click();
          await mcpPage.waitForTimeout(2000);
        }
        
        const scatterMode = mcpPage.locator('[data-testid="viz-mode-scatter"], [data-value="scatter"]');
        if (await scatterMode.count() > 0) {
          await scatterMode.click();
          await mcpPage.waitForTimeout(2000);
        }
      }
      
      performanceMonitor.mark('large-memory-test-complete');
      
      // Check memory usage
      const metrics = await performanceMonitor.getMetrics();
      expect(metrics.memoryUsage).toBeLessThan(200_000_000); // 200MB limit
    });

    test('should render progressively for very large datasets', async ({ 
      mcpPage, 
      performanceMonitor, 
      visualTester 
    }) => {
      // Look for progressive loading indicators
      const loadingIndicator = mcpPage.locator('[data-testid="graph-loading"], .graph-loading');
      
      performanceMonitor.mark('progressive-render-test-start');
      
      // If there's a way to trigger progressive loading, test it
      const progressiveToggle = mcpPage.locator('[data-testid="progressive-loading"], [data-testid="enable-sampling"]');
      
      if (await progressiveToggle.count() > 0) {
        await progressiveToggle.click();
        
        // Should show loading states
        if (await loadingIndicator.count() > 0) {
          await expect(loadingIndicator).toBeVisible();
          await visualTester.takeScreenshot('graph-progressive-loading');
        }
        
        // Wait for completion
        await visualTester.waitForPlotlyGraph();
      }
      
      performanceMonitor.mark('progressive-render-test-complete');
      
      // Progressive loading should be faster than full render
      const metrics = await performanceMonitor.getMetrics();
      expect(metrics.renderTime).toBeLessThan(8000);
    });

    test('should handle WebGL fallback gracefully', async ({ 
      mcpPage, 
      consoleMonitor, 
      visualTester 
    }) => {
      // Disable WebGL to test fallback
      await mcpPage.addInitScript(() => {
        const canvas = HTMLCanvasElement.prototype.getContext;
        HTMLCanvasElement.prototype.getContext = function(type, ...args) {
          if (type === 'webgl' || type === 'webgl2') {
            return null; // Force WebGL failure
          }
          return canvas.call(this, type, ...args);
        };
      });
      
      // Reload to apply WebGL disable
      await mcpPage.reload();
      await mcpPage.locator('[data-testid="tab-visualization"]').click();
      
      // Graph should still render (possibly with Canvas fallback)
      await expect(mcpPage.locator('[data-testid="graph-container"]')).toBeVisible();
      
      // Wait longer for Canvas rendering
      await mcpPage.waitForTimeout(5000);
      
      const graphExists = await mcpPage.locator('.js-plotly-plot').count();
      expect(graphExists).toBeGreaterThan(0);
      
      await visualTester.takeScreenshot('graph-webgl-fallback');
      
      // Should handle gracefully without errors
      const errors = consoleMonitor.getErrors().filter(error => 
        !error.text.includes('WebGL') && !error.text.includes('canvas')
      );
      expect(errors.length).toBeLessThan(3); // Some WebGL errors expected, but app should continue
    });
  });

  test.describe('Graph Accessibility and Responsiveness', () => {
    test('should be responsive to window resize', async ({ 
      mcpPage, 
      visualTester 
    }) => {
      await visualTester.waitForPlotlyGraph();
      
      // Get initial graph size
      const initialSize = await mcpPage.locator('.js-plotly-plot').boundingBox();
      
      // Resize window
      await mcpPage.setViewportSize({ width: 1200, height: 800 });
      await mcpPage.waitForTimeout(1000);
      
      const mediumSize = await mcpPage.locator('.js-plotly-plot').boundingBox();
      
      // Resize to mobile
      await mcpPage.setViewportSize({ width: 375, height: 667 });
      await mcpPage.waitForTimeout(1000);
      
      const mobileSize = await mcpPage.locator('.js-plotly-plot').boundingBox();
      
      // Sizes should be different and responsive
      expect(mediumSize?.width).not.toBe(initialSize?.width);
      expect(mobileSize?.width).toBeLessThan(mediumSize?.width || 0);
      
      await visualTester.takeScreenshot('graph-mobile-responsive');
      
      // Restore original size
      await mcpPage.setViewportSize({ width: 1920, height: 1080 });
    });

    test('should support keyboard navigation', async ({ 
      mcpPage 
    }) => {
      await visualTester.waitForPlotlyGraph();
      
      const plotlyGraph = mcpPage.locator('.js-plotly-plot');
      
      // Focus on graph
      await plotlyGraph.focus();
      
      // Test keyboard controls if available
      await mcpPage.keyboard.press('Tab');
      
      // Some Plotly graphs support keyboard navigation
      const focusedElement = await mcpPage.locator(':focus').count();
      expect(focusedElement).toBeGreaterThanOrEqual(1);
      
      // Try arrow keys for navigation
      await mcpPage.keyboard.press('ArrowUp');
      await mcpPage.keyboard.press('ArrowDown');
      await mcpPage.keyboard.press('ArrowLeft');
      await mcpPage.keyboard.press('ArrowRight');
      
      // Should not throw errors
      await mcpPage.waitForTimeout(500);
    });

    test('should provide alternative text representation', async ({ 
      mcpPage 
    }) => {
      await visualTester.waitForPlotlyGraph();
      
      // Check for accessibility features
      const graphContainer = mcpPage.locator('[data-testid="graph-container"]');
      
      // Should have proper ARIA labels
      const ariaLabel = await graphContainer.getAttribute('aria-label');
      const ariaDescription = await graphContainer.getAttribute('aria-describedby');
      const role = await graphContainer.getAttribute('role');
      
      expect(ariaLabel || ariaDescription || role).toBeTruthy();
      
      // Check for data table alternative
      const dataTable = mcpPage.locator('[data-testid="data-table"], [data-testid="graph-data-table"]');
      
      if (await dataTable.count() > 0) {
        await expect(dataTable).toBeAttached(); // Should exist as alternative
      }
      
      // Check for text summary
      const graphSummary = mcpPage.locator('[data-testid="graph-summary"], [data-testid="visualization-summary"]');
      
      if (await graphSummary.count() > 0) {
        const summaryText = await graphSummary.textContent();
        expect(summaryText?.length).toBeGreaterThan(10);
      }
    });
  });
});