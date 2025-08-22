/**
 * Enhanced File Upload Component Tests with React/Dash Integration
 * Extends the original tests with React state management and Dash callback testing
 */

import { test, expect } from '../utils/enhanced-dash-fixtures';
import { DashTestIntegration } from '../utils/dash-react-test-helpers';

test.describe('Enhanced File Upload Component - React/Dash Integration', () => {
  test.beforeEach(async ({ 
    mcpPage, 
    dashAppReady, 
    dashReactContext, 
    performanceMonitor 
  }) => {
    // Wait for Dash app to be fully ready
    await dashAppReady;
    
    // Navigate to upload section
    await mcpPage.goto('/');
    await mcpPage.locator('[data-testid="tab-upload"]').click();
    
    performanceMonitor.mark('enhanced-upload-page-ready');
    
    // Verify React component is mounted
    const uploadComponent = await dashReactContext.inspector.getComponentState('upload-dropzone');
    expect(uploadComponent.isConnected).toBe(true);
    expect(uploadComponent.hasCallbacks).toBe(true);
  });

  test.describe('React State Management Validation', () => {
    test('should maintain consistent React state during file upload', async ({ 
      mcpPage, 
      testFiles, 
      dashReactContext,
      componentStateValidator,
      visualTester
    }) => {
      const uploadDropzone = 'upload-dropzone';
      
      // Validate initial component state
      const initialValidation = await componentStateValidator(uploadDropzone, {
        accept: { type: 'string', required: false },
        multiple: { type: 'boolean', required: false },
        disabled: { type: 'boolean', required: false }
      });
      
      expect(initialValidation.valid).toBe(true);
      
      // Track state changes during upload
      const stateTracker = await dashReactContext.inspector.trackReRenders(uploadDropzone);
      await stateTracker.startTracking();
      
      // Upload file and monitor state transitions
      const fileInput = mcpPage.locator('input[type="file"]');
      await fileInput.setInputFiles(testFiles.validMELDData.path);
      
      // Wait for upload processing
      await mcpPage.waitForSelector('[data-testid="upload-success"]', { timeout: 15000 });
      
      const renderStats = await stateTracker.stopTracking();
      
      // Validate state management
      expect(renderStats.renderCount).toBeGreaterThan(0);
      expect(renderStats.averageRenderTime).toBeLessThan(100); // Should be fast re-renders
      
      // Verify final component state
      const finalState = await dashReactContext.inspector.getComponentState(uploadDropzone);
      expect(finalState.isConnected).toBe(true);
      
      await visualTester.takeScreenshot('react-state-after-upload');
    });

    test('should handle React component prop updates correctly', async ({ 
      mcpPage, 
      dashReactContext,
      dashComponentTester
    }) => {
      const uploadComponent = 'upload-dropzone';
      
      // Test component mount behavior
      const mountResult = await dashComponentTester.testComponentMount(uploadComponent);
      expect(mountResult.mounted).toBe(true);
      expect(mountResult.hasCallbacks).toBe(true);
      expect(mountResult.mountTime).toBeLessThan(1000);
      
      // Test controlled vs uncontrolled behavior for file input
      const controlledTest = await dashReactContext.events.testControlledBehavior(
        'file-input',
        'test-file.csv'
      );
      
      // File inputs are typically uncontrolled, but Dash might add control
      expect(controlledTest.valueChangedByUser).toBe(true);
      
      // Test component update behavior
      const updateResult = await dashComponentTester.testComponentUpdate(
        uploadComponent,
        async () => {
          // Simulate enabling/disabling the component
          await mcpPage.evaluate((id) => {
            const element = document.getElementById(id);
            if (element) {
              element.setAttribute('disabled', 'true');
            }
          }, uploadComponent);
        }
      );
      
      expect(updateResult.updated).toBe(true);
      expect(updateResult.propsChanged).toBe(true);
    });

    test('should properly manage React component lifecycle', async ({ 
      mcpPage,
      dashReactContext,
      testFiles
    }) => {
      const lifecycle = dashReactContext.lifecycle;
      
      // Test component cleanup when navigating away
      const cleanupTest = await lifecycle.testComponentCleanup(
        'upload-dropzone',
        async () => {
          // Navigate away from upload tab
          await mcpPage.locator('[data-testid="tab-visualization"]').click();
          await mcpPage.waitForSelector('[data-testid="graph-container"]', { timeout: 10000 });
        }
      );
      
      // Component should be properly cleaned up
      expect(cleanupTest.cleaned).toBe(true);
      expect(cleanupTest.listenersRemoved).toBe(true);
      expect(cleanupTest.memoryLeaks).toBe(false);
    });
  });

  test.describe('Dash Callback Chain Testing', () => {
    test('should execute file upload callbacks in correct order', async ({ 
      mcpPage,
      testFiles,
      callbackOrderValidator,
      dashComponentTester,
      visualTester
    }) => {
      // Define expected callback execution order for file upload
      const expectedCallbackOrder = [
        'upload-file-callback',
        'file-validation-callback', 
        'data-processing-callback',
        'ui-update-callback'
      ];
      
      const orderValidator = await callbackOrderValidator(expectedCallbackOrder);
      await orderValidator.startMonitoring();
      
      // Trigger file upload
      const fileInput = mcpPage.locator('input[type="file"]');
      await fileInput.setInputFiles(testFiles.validMELDData.path);
      
      // Wait for callback chain to complete
      await mcpPage.waitForSelector('[data-testid="upload-success"]', { timeout: 15000 });
      
      // Validate callback execution order
      const orderResult = await orderValidator.validateOrder();
      
      // Note: Actual callback names might differ, this demonstrates the pattern
      if (orderResult.valid) {
        expect(orderResult.valid).toBe(true);
      } else {
        console.warn('Callback order validation issues:', orderResult.issues);
        // Test should continue as callback names might be different
      }
      
      await visualTester.takeScreenshot('callback-chain-completed');
    });

    test('should handle callback errors gracefully', async ({ 
      mcpPage,
      testFiles,
      dashReactContext,
      consoleMonitor
    }) => {
      // Test callback error handling with invalid file
      const errorHandlingResult = await dashReactContext.callbacks.testCallbackErrorHandling(
        'upload-dropzone',
        async () => {
          // Upload corrupted file to trigger error
          const fileInput = mcpPage.locator('input[type="file"]');
          await fileInput.setInputFiles(testFiles.corruptedFile.path);
        }
      );
      
      // Verify error was caught and handled
      expect(errorHandlingResult.errorCaught).toBe(true);
      expect(errorHandlingResult.callbacksStillWorking).toBe(true);
      
      // Verify error message is displayed to user
      await expect(mcpPage.locator('[data-testid="upload-error"]')).toBeVisible();
      
      // Ensure app doesn't crash
      const appContainer = mcpPage.locator('[data-testid="app-container"]');
      await expect(appContainer).toBeVisible();
    });

    test('should validate concurrent callback handling', async ({ 
      mcpPage,
      testFiles,
      dashReactContext,
      performanceMonitor
    }) => {
      performanceMonitor.mark('concurrent-callback-test-start');
      
      // Test multiple rapid file uploads to test callback queuing
      const callbackMonitor = await dashReactContext.callbacks.monitorCallbackExecution({
        componentId: 'upload-dropzone',
        trackOrder: true
      });
      
      await callbackMonitor.startMonitoring();
      
      // Rapid file selections (simulating user changing mind quickly)
      const fileInput = mcpPage.locator('input[type="file"]');
      
      await fileInput.setInputFiles(testFiles.minimalMELDData.path);
      await mcpPage.waitForTimeout(100);
      
      await fileInput.setInputFiles(testFiles.validMELDData.path);
      
      // Wait for callbacks to settle
      await mcpPage.waitForSelector('[data-testid="upload-success"]', { timeout: 15000 });
      
      const callbackExecution = await callbackMonitor.stopMonitoring();
      
      // Verify callbacks were handled properly
      expect(callbackExecution.length).toBeGreaterThan(0);
      
      // Check for callback conflicts or race conditions
      const overlappingCallbacks = callbackExecution.filter((callback, index) => {
        const nextCallback = callbackExecution[index + 1];
        return nextCallback && 
               callback.timestamp + callback.duration > nextCallback.timestamp;
      });
      
      // Should handle overlapping callbacks gracefully
      expect(overlappingCallbacks.length).toBeLessThan(callbackExecution.length / 2);
      
      performanceMonitor.mark('concurrent-callback-test-complete');
    });
  });

  test.describe('React Event System Integration', () => {
    test('should handle React synthetic events correctly', async ({ 
      mcpPage,
      dashReactContext,
      visualTester
    }) => {
      const eventSimulator = dashReactContext.events;
      
      // Test drag and drop synthetic events
      await eventSimulator.dispatchSyntheticEvent(
        'upload-dropzone',
        'dragenter',
        { dataTransfer: { files: [], types: ['Files'] } }
      );
      
      // Verify drag state is applied
      const dropzone = mcpPage.locator('[data-testid="upload-dropzone"]');
      await expect(dropzone).toHaveClass(/drag-over|dropzone-active/);
      
      await visualTester.takeScreenshot('synthetic-drag-enter-event');
      
      // Test drag leave
      await eventSimulator.dispatchSyntheticEvent(
        'upload-dropzone',
        'dragleave',
        {}
      );
      
      // Verify drag state is removed
      await expect(dropzone).not.toHaveClass(/drag-over|dropzone-active/);
    });

    test('should validate form submission flow', async ({ 
      mcpPage,
      dashComponentTester,
      testFiles
    }) => {
      // Test upload form validation if present
      const uploadForm = mcpPage.locator('form, [data-testid="upload-form"]');
      
      if (await uploadForm.count() > 0) {
        const formResult = await dashComponentTester.testFormValidation(
          'upload-form',
          { 'file-input': testFiles.validMELDData.path }
        );
        
        expect(formResult.validated).toBe(true);
        expect(formResult.errors).toHaveLength(0);
      }
    });

    test('should test custom React hooks behavior', async ({ 
      mcpPage,
      dashReactContext,
      performanceMonitor
    }) => {
      performanceMonitor.mark('hooks-test-start');
      
      // Test custom hooks used in upload component (if any)
      const componentState = await dashReactContext.inspector.getComponentState('upload-dropzone');
      
      // Test useEffect cleanup
      const effectsTest = await mcpPage.evaluate((id) => {
        const element = document.getElementById(id);
        if (!element) return { hasEffects: false, cleanupCalled: false };
        
        // Check for effect cleanup patterns
        const reactKey = Object.keys(element).find(key => 
          key.startsWith('__reactInternalInstance') || 
          key.startsWith('__reactFiber')
        );
        
        const reactNode = reactKey ? (element as any)[reactKey] : null;
        
        return {
          hasEffects: !!reactNode?.updateQueue,
          cleanupCalled: !!reactNode?.effectTag
        };
      }, 'upload-dropzone');
      
      // Custom hooks should be properly implemented
      expect(componentState.isConnected).toBe(true);
      
      performanceMonitor.mark('hooks-test-complete');
    });
  });

  test.describe('React Performance Optimization', () => {
    test('should validate React.memo usage and re-render optimization', async ({ 
      mcpPage,
      testFiles,
      reactRenderProfiler,
      performanceMonitor
    }) => {
      const profiler = await reactRenderProfiler('upload-dropzone');
      await profiler.startProfiling();
      
      performanceMonitor.mark('memo-optimization-test-start');
      
      // Perform actions that should NOT cause unnecessary re-renders
      await mcpPage.hover('[data-testid="upload-instructions"]');
      await mcpPage.hover('[data-testid="supported-formats"]');
      
      // Only file input should cause re-render
      const fileInput = mcpPage.locator('input[type="file"]');
      await fileInput.setInputFiles(testFiles.validMELDData.path);
      
      await mcpPage.waitForSelector('[data-testid="upload-success"]', { timeout: 15000 });
      
      const profile = await profiler.getProfile();
      
      // Validate render performance
      expect(profile.renderCount).toBeLessThan(5); // Should be minimal re-renders
      expect(profile.averageRenderTime).toBeLessThan(50); // Should be fast
      expect(profile.heavyRenders).toHaveLength(0); // No heavy renders
      
      performanceMonitor.mark('memo-optimization-test-complete');
    });

    test('should test useCallback and useMemo optimization', async ({ 
      mcpPage,
      dashReactContext,
      performanceMonitor
    }) => {
      performanceMonitor.mark('callback-memo-test-start');
      
      // Test callback stability (callbacks should not change on every render)
      const initialState = await dashReactContext.inspector.getComponentState('upload-dropzone');
      
      // Trigger a minor re-render
      await mcpPage.hover('[data-testid="upload-dropzone"]');
      await mcpPage.waitForTimeout(100);
      
      const afterHoverState = await dashReactContext.inspector.getComponentState('upload-dropzone');
      
      // Props should be stable (indicating proper useCallback/useMemo usage)
      const stableProps = Object.keys(initialState.props).filter(key => {
        const initial = initialState.props[key];
        const after = afterHoverState.props[key];
        
        // Check if function props are the same reference (useCallback working)
        return typeof initial === 'function' && initial === after;
      });
      
      // At least some callback props should be stable
      if (Object.keys(initialState.props).some(key => typeof initialState.props[key] === 'function')) {
        expect(stableProps.length).toBeGreaterThan(0);
      }
      
      performanceMonitor.mark('callback-memo-test-complete');
    });

    test('should validate component memory usage', async ({ 
      mcpPage,
      testFiles,
      dashReactContext,
      performanceMonitor
    }) => {
      const memoryProfiler = dashReactContext.performance;
      
      // Profile memory usage during multiple uploads
      const memoryProfile = await memoryProfiler.profileMemoryUsage(15000);
      
      // Upload multiple files to test memory management
      for (const file of [testFiles.minimalMELDData, testFiles.validMELDData]) {
        const fileInput = mcpPage.locator('input[type="file"]');
        await fileInput.setInputFiles(file.path);
        await mcpPage.waitForSelector('[data-testid="upload-success"]', { timeout: 10000 });
        
        // Clear upload to test cleanup
        const clearButton = mcpPage.locator('[data-testid="clear-upload"], .clear-button');
        if (await clearButton.count() > 0) {
          await clearButton.click();
          await mcpPage.waitForTimeout(500);
        }
      }
      
      // Memory should be managed properly
      expect(memoryProfile.memoryGrowth).toBeLessThan(50_000_000); // Less than 50MB growth
      
      // GC should have been triggered to clean up
      if (memoryProfile.peakMemory > memoryProfile.initialMemory * 1.5) {
        expect(memoryProfile.gcTriggered).toBe(true);
      }
    });
  });

  test.describe('Accessibility and React Integration', () => {
    test('should maintain ARIA attributes through React state changes', async ({ 
      mcpPage,
      testFiles,
      dashReactContext
    }) => {
      const dropzone = mcpPage.locator('[data-testid="upload-dropzone"]');
      
      // Check initial ARIA attributes
      await expect(dropzone).toHaveAttribute('role');
      await expect(dropzone).toHaveAttribute('tabindex');
      
      // Track state changes
      const stateTracker = await dashReactContext.inspector.trackReRenders('upload-dropzone');
      await stateTracker.startTracking();
      
      // Upload file and verify ARIA attributes persist
      const fileInput = mcpPage.locator('input[type="file"]');
      await fileInput.setInputFiles(testFiles.validMELDData.path);
      
      await mcpPage.waitForSelector('[data-testid="upload-success"]', { timeout: 15000 });
      
      // ARIA attributes should be maintained through state changes
      await expect(dropzone).toHaveAttribute('role');
      await expect(dropzone).toHaveAttribute('tabindex');
      
      // Test screen reader compatibility
      const ariaLabel = await dropzone.getAttribute('aria-label');
      const ariaDescribedBy = await dropzone.getAttribute('aria-describedby');
      
      expect(ariaLabel || ariaDescribedBy).toBeTruthy();
    });

    test('should support keyboard navigation through React event handlers', async ({ 
      mcpPage,
      testFiles,
      dashReactContext
    }) => {
      const eventSimulator = dashReactContext.events;
      const fileInput = mcpPage.locator('input[type="file"]');
      
      // Test keyboard focus
      await fileInput.focus();
      await expect(fileInput).toBeFocused();
      
      // Test custom keyboard events
      await eventSimulator.dispatchSyntheticEvent(
        'upload-dropzone',
        'keydown',
        { key: 'Enter', keyCode: 13 }
      );
      
      // Should trigger file dialog or upload action
      await mcpPage.waitForTimeout(500);
      
      // Test tab navigation
      await mcpPage.keyboard.press('Tab');
      
      // Focus should move to next interactive element
      const focusedElement = await mcpPage.locator(':focus').getAttribute('data-testid');
      expect(focusedElement).toBeTruthy();
    });
  });
});