/**
 * Enhanced Plotly Graph Component Performance Tests
 * React/Dash-specific performance testing with advanced monitoring
 */

import { test, expect } from '../utils/enhanced-dash-fixtures';
import {
  DashComponentLifecycleTester,
  DashPerformanceBenchmarker
} from '../utils/dash-lifecycle-performance-testing';

test.describe('Enhanced Plotly Graph Performance - React/Dash Integration', () => {
  test.beforeEach(async ({
    mcpPage,
    dashAppReady,
    uploadPage,
    testFiles,
    performanceMonitor
  }) => {
    await dashAppReady;

    // Upload data for visualization
    await uploadPage.uploadFile(testFiles.validMELDData);
    await expect(mcpPage.locator('[data-testid="upload-success"]')).toBeVisible();

    // Navigate to visualization
    await mcpPage.locator('[data-testid="tab-visualization"]').click();

    performanceMonitor.mark('plotly-performance-test-ready');
  });

  test.describe('React Rendering Performance', () => {
    test('should maintain optimal render performance with large datasets', async ({
      mcpPage,
      testFiles,
      uploadPage,
      dashReactContext,
      reactRenderProfiler,
      performanceMonitor
    }) => {
      // Upload large dataset for stress testing
      await uploadPage.uploadFile(testFiles.largeMELDData);
      await expect(mcpPage.locator('[data-testid="upload-success"]')).toBeVisible();

      const profiler = await reactRenderProfiler('plotly-graph');
      await profiler.startProfiling();

      performanceMonitor.mark('large-dataset-render-start');

      // Navigate to visualization with large dataset
      await mcpPage.locator('[data-testid="tab-visualization"]').click();
      await mcpPage.waitForSelector('.js-plotly-plot', { timeout: 30000 });

      // Wait for complete render
      await mcpPage.waitForFunction(() => {
        const plotElement = document.querySelector('.js-plotly-plot') as any;
        return plotElement && plotElement._fullData && plotElement._fullData.length > 0;
      }, { timeout: 30000 });

      performanceMonitor.mark('large-dataset-render-complete');

      // Get render profile
      const profile = await profiler.getProfile();

      // Performance assertions for large datasets
      expect(profile.renderCount).toBeLessThan(5); // Should minimize re-renders
      expect(profile.averageRenderTime).toBeLessThan(200); // Should render within 200ms
      expect(profile.heavyRenders.length).toBeLessThan(2); // Maximum 1 heavy render for initial load

      // Check overall performance metrics
      const metrics = await performanceMonitor.getMetrics();
      expect(metrics.renderTime).toBeLessThan(15000); // 15 second max for large dataset
      expect(metrics.memoryUsage).toBeLessThan(200_000_000); // 200MB memory limit

      // Test interaction responsiveness after render
      const plotlyGraph = mcpPage.locator('.js-plotly-plot');
      const interactionStart = performance.now();

      await plotlyGraph.hover();
      await mcpPage.mouse.wheel(0, -100); // Zoom

      const interactionTime = performance.now() - interactionStart;
      expect(interactionTime).toBeLessThan(500); // Should remain responsive
    });

    test('should optimize React component updates during Plotly interactions', async ({
      mcpPage,
      dashReactContext,
      performanceMonitor
    }) => {
      const lifecycleTester = new DashComponentLifecycleTester(mcpPage);

      // Test component lifecycle during various Plotly interactions
      const lifecycleResult = await lifecycleTester.testCompleteLifecycle('plotly-graph', {
        stressTest: true,
        memoryProfiling: true,
        renderOptimization: true
      });

      // Validate lifecycle performance
      expect(lifecycleResult.mount.success).toBe(true);
      expect(lifecycleResult.mount.time).toBeLessThan(5000);
      expect(lifecycleResult.mount.hasCallbacks).toBe(true);

      // Check render optimization
      expect(lifecycleResult.rerenders.efficiency).toBeGreaterThan(0.8); // 80% efficiency
      expect(lifecycleResult.rerenders.unnecessary).toBeLessThan(3);

      // Memory management
      expect(lifecycleResult.performance.memoryPeakUsage).toBeLessThan(150_000_000); // 150MB peak
      expect(lifecycleResult.performance.gcTriggers).toBeGreaterThan(0); // GC should run

      // Test specific Plotly interactions
      const plotlyGraph = mcpPage.locator('.js-plotly-plot');

      // Track renders during interactions
      const interactionProfiler = await dashReactContext.inspector.trackReRenders('plotly-graph');
      await interactionProfiler.startTracking();

      // Perform Plotly interactions that should NOT trigger React re-renders
      await plotlyGraph.hover();
      await mcpPage.mouse.wheel(0, -200); // Zoom in
      await mcpPage.mouse.move(200, 200); // Pan

      const renderStats = await interactionProfiler.stopTracking();

      // These interactions should be handled by Plotly, not React
      expect(renderStats.renderCount).toBeLessThan(2); // Minimal React re-renders
    });

    test('should handle Plotly graph updates without unnecessary React renders', async ({
      mcpPage,
      dashReactContext,
      dashComponentTester
    }) => {
      const plotlyContainer = 'graph-container';

      // Test component update behavior when Plotly data changes
      const updateResult = await dashComponentTester.testComponentUpdate(
        plotlyContainer,
        async () => {
          // Simulate changing visualization mode (should trigger data update)
          const modeSelector = mcpPage.locator('[data-testid="viz-mode-surface"]');
          if (await modeSelector.count() > 0) {
            await modeSelector.click();
            await mcpPage.waitForTimeout(2000);
          }
        }
      );

      expect(updateResult.updated).toBe(true);
      expect(updateResult.renderTime).toBeLessThan(3000); // Should update quickly
      expect(updateResult.propsChanged).toBe(true); // Props should change for mode switch

      // Test that irrelevant updates don't affect Plotly
      const irrelevantUpdateResult = await dashComponentTester.testComponentUpdate(
        plotlyContainer,
        async () => {
          // Change theme (should not affect Plotly data)
          const themeToggle = mcpPage.locator('[data-testid="theme-toggle"]');
          if (await themeToggle.count() > 0) {
            await themeToggle.click();
            await mcpPage.waitForTimeout(1000);
          }
        }
      );

      // Theme changes should be handled efficiently
      expect(irrelevantUpdateResult.renderTime).toBeLessThan(1000);
    });
  });

  test.describe('Plotly-React Integration Performance', () => {
    test('should efficiently handle Plotly callbacks within Dash', async ({
      mcpPage,
      dashReactContext,
      performanceMonitor
    }) => {
      // Monitor callback execution for Plotly events
      const callbackMonitor = await dashReactContext.callbacks.monitorCallbackExecution({
        componentId: 'plotly-graph',
        trackOrder: true
      });

      await callbackMonitor.startMonitoring();

      performanceMonitor.mark('plotly-callback-test-start');

      // Trigger Plotly-specific events that might have Dash callbacks
      const plotlyGraph = mcpPage.locator('.js-plotly-plot');

      // Hover to trigger potential hover callbacks
      await plotlyGraph.hover();
      await mcpPage.waitForTimeout(500);

      // Click to trigger potential selection callbacks
      await plotlyGraph.click({ position: { x: 200, y: 200 } });
      await mcpPage.waitForTimeout(500);

      // Zoom to trigger potential relayout callbacks
      await mcpPage.mouse.wheel(0, -300);
      await mcpPage.waitForTimeout(1000);

      const callbackExecution = await callbackMonitor.stopMonitoring();

      performanceMonitor.mark('plotly-callback-test-complete');

      // Analyze callback performance
      const metrics = await performanceMonitor.getMetrics();

      if (callbackExecution.length > 0) {
        // If callbacks were triggered, they should be fast
        const averageCallbackTime = callbackExecution.reduce((sum, cb) => sum + cb.duration, 0) / callbackExecution.length;
        expect(averageCallbackTime).toBeLessThan(100); // 100ms average

        // No callback should take too long
        callbackExecution.forEach(callback => {
          expect(callback.duration).toBeLessThan(500); // 500ms max per callback
        });
      }

      expect(metrics.interactionTime).toBeLessThan(2000); // Total interaction time
    });

    test('should maintain memory efficiency during extended Plotly usage', async ({
      mcpPage,
      dashReactContext,
      performanceMonitor
    }) => {
      const memoryProfiler = dashReactContext.performance;

      // Profile memory usage during extended Plotly operations
      const memoryProfile = await memoryProfiler.profileMemoryUsage(30000); // 30 seconds

      const plotlyGraph = mcpPage.locator('.js-plotly-plot');

      performanceMonitor.mark('extended-usage-start');

      // Simulate extended usage patterns
      for (let i = 0; i < 10; i++) {
        // Zoom in and out
        await mcpPage.mouse.wheel(0, -200);
        await mcpPage.waitForTimeout(200);
        await mcpPage.mouse.wheel(0, 200);
        await mcpPage.waitForTimeout(200);

        // Pan around
        await plotlyGraph.dragTo(plotlyGraph, {
          sourcePosition: { x: 100, y: 100 },
          targetPosition: { x: 200, y: 150 }
        });
        await mcpPage.waitForTimeout(300);

        // Reset view
        const resetButton = mcpPage.locator('[data-testid="reset-button"], .modebar-btn[data-title*="Autoscale"]');
        if (await resetButton.count() > 0) {
          await resetButton.click();
          await mcpPage.waitForTimeout(300);
        }
      }

      performanceMonitor.mark('extended-usage-complete');

      // Memory should be managed efficiently
      expect(memoryProfile.memoryGrowth).toBeLessThan(100_000_000); // Less than 100MB growth

      // Garbage collection should have occurred
      if (memoryProfile.peakMemory > memoryProfile.initialMemory * 2) {
        expect(memoryProfile.gcTriggered).toBe(true);
      }

      const metrics = await performanceMonitor.getMetrics();
      expect(metrics.memoryUsage).toBeLessThan(300_000_000); // 300MB total limit
    });

    test('should handle React context updates efficiently with Plotly', async ({
      mcpPage,
      dashReactContext
    }) => {
      // Test React context changes (like theme) don't interfere with Plotly performance
      const stateInspector = dashReactContext.inspector;

      // Get initial Plotly state
      const initialPlotlyState = await mcpPage.evaluate(() => {
        const plotElement = document.querySelector('.js-plotly-plot') as any;
        return plotElement ? {
          hasData: plotElement._fullData?.length || 0,
          layoutTheme: plotElement._fullLayout?.template || 'none'
        } : null;
      });

      expect(initialPlotlyState?.hasData).toBeGreaterThan(0);

      // Change theme context
      const themeToggle = mcpPage.locator('[data-testid="theme-toggle"]');
      if (await themeToggle.count() > 0) {
        // Track renders during theme change
        const renderTracker = await stateInspector.trackReRenders('plotly-graph');
        await renderTracker.startTracking();

        await themeToggle.click();
        await mcpPage.waitForTimeout(2000); // Wait for theme application

        const renderStats = await renderTracker.stopTracking();

        // Verify Plotly adapted to theme
        const newPlotlyState = await mcpPage.evaluate(() => {
          const plotElement = document.querySelector('.js-plotly-plot') as any;
          return plotElement ? {
            hasData: plotElement._fullData?.length || 0,
            layoutTheme: plotElement._fullLayout?.template || 'none',
            paperBgColor: plotElement._fullLayout?.paper_bgcolor,
            plotBgColor: plotElement._fullLayout?.plot_bgcolor
          } : null;
        });

        // Data should be preserved
        expect(newPlotlyState?.hasData).toBe(initialPlotlyState?.hasData);

        // Theme should have changed
        expect(newPlotlyState?.layoutTheme).not.toBe(initialPlotlyState?.layoutTheme);

        // Theme change should be efficient
        expect(renderStats.renderCount).toBeLessThan(5); // Minimal re-renders
        expect(renderStats.averageRenderTime).toBeLessThan(100); // Fast re-renders
      }
    });
  });

  test.describe('Performance Benchmarking', () => {
    test('should meet performance benchmarks for Plotly operations', async ({
      mcpPage,
      testFiles,
      uploadPage
    }) => {
      const benchmarker = new DashPerformanceBenchmarker(mcpPage);

      // Define benchmark scenarios for Plotly operations
      const scenarios = [
        {
          name: 'Initial Graph Render',
          actions: [
            { type: 'navigate' as const, target: '/', waitAfter: 1000 },
            { type: 'click' as const, target: '[data-testid="tab-visualization"]', waitAfter: 2000 },
            { type: 'wait' as const, duration: 3000 }
          ]
        },
        {
          name: 'Graph Interaction Performance',
          actions: [
            { type: 'click' as const, target: '.js-plotly-plot', waitAfter: 200 },
            { type: 'scroll' as const, target: '.js-plotly-plot', value: -200, waitAfter: 300 },
            { type: 'scroll' as const, target: '.js-plotly-plot', value: 200, waitAfter: 300 },
            { type: 'click' as const, target: '[data-testid="reset-button"]', waitAfter: 500 }
          ]
        },
        {
          name: 'Mode Switching Performance',
          actions: [
            { type: 'click' as const, target: '[data-testid="viz-mode-surface"]', waitAfter: 3000 },
            { type: 'click' as const, target: '[data-testid="viz-mode-scatter"]', waitAfter: 3000 }
          ]
        }
      ];

      const benchmarkResults = await benchmarker.benchmarkApplication(scenarios);

      // Validate benchmark results
      expect(benchmarkResults.overall.averageLoadTime).toBeLessThan(10000); // 10s load time
      expect(benchmarkResults.overall.averageInteractionTime).toBeLessThan(500); // 500ms interaction
      expect(benchmarkResults.overall.renderPerformance).toBeGreaterThan(70); // 70+ render score
      expect(benchmarkResults.overall.memoryEfficiency).toBeGreaterThan(60); // 60+ memory score

      // Check individual scenarios
      const successfulScenarios = benchmarkResults.scenarios.filter(s => s.success);
      expect(successfulScenarios.length).toBe(scenarios.length); // All scenarios should succeed

      // Specific scenario requirements
      const initialRenderScenario = benchmarkResults.scenarios.find(s => s.name === 'Initial Graph Render');
      if (initialRenderScenario) {
        expect(initialRenderScenario.loadTime).toBeLessThan(15000); // 15s for initial render
      }

      const interactionScenario = benchmarkResults.scenarios.find(s => s.name === 'Graph Interaction Performance');
      if (interactionScenario) {
        expect(interactionScenario.interactionTime).toBeLessThan(300); // 300ms for interactions
      }
    });

    test('should handle concurrent users simulation efficiently', async ({
      mcpPage,
      dashReactContext,
      performanceMonitor
    }) => {
      performanceMonitor.mark('concurrent-simulation-start');

      // Simulate concurrent user interactions
      const concurrentTasks = [];

      for (let i = 0; i < 5; i++) {
        concurrentTasks.push(
          (async () => {
            const plotlyGraph = mcpPage.locator('.js-plotly-plot');

            // Simulate user interaction pattern
            await plotlyGraph.hover();
            await mcpPage.mouse.wheel(0, -50); // Small zoom
            await mcpPage.waitForTimeout(100);

            await plotlyGraph.click({ position: { x: 100 + i * 50, y: 100 + i * 30 } });
            await mcpPage.waitForTimeout(200);

            return performance.now();
          })()
        );
      }

      const completionTimes = await Promise.all(concurrentTasks);

      performanceMonitor.mark('concurrent-simulation-complete');

      // All tasks should complete without significant delays
      const maxTime = Math.max(...completionTimes);
      const minTime = Math.min(...completionTimes);
      const timeSpread = maxTime - minTime;

      expect(timeSpread).toBeLessThan(1000); // Tasks should complete within 1s of each other

      // App should remain responsive
      const appContainer = mcpPage.locator('[data-testid="app-container"]');
      await expect(appContainer).toBeVisible();

      const finalMetrics = await performanceMonitor.getMetrics();
      expect(finalMetrics.cpuUsage).toBeLessThan(90); // CPU shouldn't max out
    });

    test('should maintain performance across different viewport sizes', async ({
      mcpPage,
      dashReactContext
    }) => {
      const viewports = [
        { width: 1920, height: 1080, name: 'Desktop' },
        { width: 1366, height: 768, name: 'Laptop' },
        { width: 768, height: 1024, name: 'Tablet' },
        { width: 375, height: 667, name: 'Mobile' }
      ];

      const performanceResults = [];

      for (const viewport of viewports) {
        await mcpPage.setViewportSize(viewport);
        await mcpPage.waitForTimeout(1000);

        // Test render performance at this viewport
        const renderTracker = await dashReactContext.inspector.trackReRenders('plotly-graph');
        await renderTracker.startTracking();

        // Trigger re-render
        const themeToggle = mcpPage.locator('[data-testid="theme-toggle"]');
        if (await themeToggle.count() > 0) {
          await themeToggle.click();
          await mcpPage.waitForTimeout(2000);
          await themeToggle.click(); // Toggle back
          await mcpPage.waitForTimeout(2000);
        }

        const renderStats = await renderTracker.stopTracking();

        performanceResults.push({
          viewport: viewport.name,
          renderCount: renderStats.renderCount,
          averageRenderTime: renderStats.averageRenderTime
        });
      }

      // Performance should be consistent across viewports
      const renderTimes = performanceResults.map(r => r.averageRenderTime);
      const maxRenderTime = Math.max(...renderTimes);
      const minRenderTime = Math.min(...renderTimes);

      // Render time variance should be reasonable
      expect(maxRenderTime / minRenderTime).toBeLessThan(3); // Max 3x difference

      // All viewport render times should be acceptable
      renderTimes.forEach(time => {
        expect(time).toBeLessThan(200); // 200ms max per viewport
      });
    });
  });
});
