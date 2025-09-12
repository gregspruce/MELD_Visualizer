# Comprehensive Dash/React Testing Guide for MELD Visualizer

## Table of Contents
1. [Overview](#overview)
2. [Architecture Understanding](#architecture-understanding)
3. [Testing Strategies](#testing-strategies)
4. [Component Testing](#component-testing)
5. [Callback Testing](#callback-testing)
6. [Performance Testing](#performance-testing)
7. [Best Practices](#best-practices)
8. [Common Patterns](#common-patterns)
9. [Troubleshooting](#troubleshooting)
10. [Examples](#examples)

## Overview

This guide provides comprehensive testing strategies for Dash applications, leveraging React expertise to create robust and efficient tests. Dash applications are built on React, and understanding this underlying architecture enables more effective testing approaches.

### Key Concepts
- **Dash Components**: React components wrapped for Python use
- **Callbacks**: Server-side functions triggered by client interactions
- **Component State**: React state management within Dash
- **Lifecycle**: React component mounting, updating, and unmounting
- **Performance**: React render optimization and memory management

## Architecture Understanding

### Dash + React Integration

```typescript
// Dash applications use React under the hood
window.dash_clientside  // Dash's client-side runtime
window.React           // React library
window.Plotly         // Plotly.js for visualizations
```

### Component Hierarchy
```
Dash App Container
├── React Components (wrapped as Dash components)
│   ├── State Management (React hooks/state)
│   ├── Event Handlers (React events → Dash callbacks)
│   └── Lifecycle Methods (React lifecycle)
└── Callback System (Server-side Python functions)
```

## Testing Strategies

### 1. Component State Testing

Test React component state management within Dash applications:

```typescript
import { DashComponentStateInspector } from '../utils/dash-react-test-helpers';

test('should validate component state transitions', async ({ mcpPage, dashReactContext }) => {
  const inspector = dashReactContext.inspector;

  // Get component state
  const initialState = await inspector.getComponentState('upload-dropzone');
  expect(initialState.isConnected).toBe(true);
  expect(initialState.hasCallbacks).toBe(true);

  // Validate props
  const validation = await inspector.validateComponentProps('upload-dropzone', {
    accept: { type: 'string', required: false },
    disabled: { type: 'boolean', required: false }
  });

  expect(validation.valid).toBe(true);
});
```

### 2. Callback Chain Testing

Test Dash callback execution and dependencies:

```typescript
import { CallbackFlowTester } from '../utils/dash-callback-testing-strategies';

test('should execute callbacks in correct order', async ({ mcpPage }) => {
  const flowTester = new CallbackFlowTester(mcpPage);

  const flowResult = await flowTester.testCallbackFlow({
    triggerAction: async () => {
      await mcpPage.locator('input[type="file"]').setInputFiles('test.csv');
    },
    expectedFlow: [
      {
        callbackPattern: 'upload-file-callback',
        maxDuration: 5000,
        dependencies: [],
        expectedStateChanges: [
          {
            componentId: 'upload-status',
            property: 'visible',
            expectedValue: true
          }
        ]
      }
    ]
  });

  expect(flowResult.success).toBe(true);
  expect(flowResult.issues).toHaveLength(0);
});
```

### 3. Performance Testing

Test React rendering and memory performance:

```typescript
import { DashPerformanceBenchmarker } from '../utils/dash-lifecycle-performance-testing';

test('should meet performance benchmarks', async ({ mcpPage }) => {
  const benchmarker = new DashPerformanceBenchmarker(mcpPage);

  const results = await benchmarker.benchmarkApplication([
    {
      name: 'Component Render Performance',
      actions: [
        { type: 'navigate', target: '/' },
        { type: 'click', target: '[data-testid="tab-visualization"]' },
        { type: 'wait', duration: 3000 }
      ]
    }
  ]);

  expect(results.overall.averageLoadTime).toBeLessThan(5000);
  expect(results.overall.renderPerformance).toBeGreaterThan(80);
});
```

## Component Testing

### React Component Lifecycle

```typescript
test('should handle component lifecycle correctly', async ({
  mcpPage,
  dashReactContext
}) => {
  const lifecycle = dashReactContext.lifecycle;

  // Test mounting
  const mountResult = await lifecycle.testComponentMount('my-component');
  expect(mountResult.mounted).toBe(true);
  expect(mountResult.hasCallbacks).toBe(true);

  // Test updates
  const updateResult = await lifecycle.testComponentUpdate(
    'my-component',
    { newProp: 'updated-value' }
  );
  expect(updateResult.updated).toBe(true);
  expect(updateResult.reRendered).toBe(true);

  // Test cleanup
  const cleanupResult = await lifecycle.testComponentCleanup(
    'my-component',
    async () => {
      // Navigate away or unmount component
      await mcpPage.locator('[data-testid="other-tab"]').click();
    }
  );
  expect(cleanupResult.cleaned).toBe(true);
  expect(cleanupResult.memoryLeaks).toBe(false);
});
```

### React Event Handling

```typescript
test('should handle React synthetic events', async ({
  mcpPage,
  dashReactContext
}) => {
  const events = dashReactContext.events;

  // Test controlled component behavior
  const controlledTest = await events.testControlledBehavior(
    'input-component',
    'test-value'
  );

  expect(controlledTest.isControlled).toBe(true);
  expect(controlledTest.valueChangedByUser).toBe(true);

  // Test synthetic events
  await events.dispatchSyntheticEvent(
    'upload-dropzone',
    'dragenter',
    { dataTransfer: { files: [] } }
  );

  // Verify event handling
  const dropzone = mcpPage.locator('[data-testid="upload-dropzone"]');
  await expect(dropzone).toHaveClass(/drag-over/);
});
```

## Callback Testing

### Dependency Analysis

```typescript
test('should analyze callback dependencies', async ({ mcpPage }) => {
  const analyzer = new CallbackDependencyAnalyzer(mcpPage);

  const graph = await analyzer.buildDependencyGraph();

  // Validate graph structure
  expect(graph.nodes.length).toBeGreaterThan(0);
  expect(graph.cycles).toHaveLength(0); // No circular dependencies

  // Get execution order
  const order = await analyzer.getRecommendedExecutionOrder();
  expect(order.order.length).toBe(graph.nodes.length);
});
```

### Error Resilience

```typescript
test('should handle callback errors gracefully', async ({
  mcpPage,
  testFiles
}) => {
  const errorTester = new CallbackErrorResilienceTester(mcpPage);

  const resilience = await errorTester.testErrorResilience({
    errorTrigger: async () => {
      // Upload corrupted file to trigger error
      await mcpPage.locator('input[type="file"]').setInputFiles(testFiles.corruptedFile.path);
    },
    expectedErrorHandling: {
      shouldCatchErrors: true,
      shouldStayResponsive: true,
      shouldDisplayErrorToUser: true,
      maxErrorRecoveryTime: 5000
    },
    recoveryActions: [
      async () => {
        // Clear the error and try valid file
        await mcpPage.locator('[data-testid="clear-error"]').click();
        await mcpPage.locator('input[type="file"]').setInputFiles(testFiles.validMELDData.path);
      }
    ]
  });

  expect(resilience.errorTriggered).toBe(true);
  expect(resilience.appStillResponsive).toBe(true);
  expect(resilience.recoveryResults[0].successful).toBe(true);
});
```

## Performance Testing

### Memory Management

```typescript
test('should manage memory efficiently', async ({
  mcpPage,
  dashReactContext
}) => {
  const profiler = dashReactContext.performance;

  const memoryProfile = await profiler.profileMemoryUsage(30000);

  // Perform memory-intensive operations
  for (let i = 0; i < 10; i++) {
    await mcpPage.locator('[data-testid="generate-large-graph"]').click();
    await mcpPage.waitForTimeout(1000);
    await mcpPage.locator('[data-testid="clear-graph"]').click();
    await mcpPage.waitForTimeout(500);
  }

  expect(memoryProfile.memoryGrowth).toBeLessThan(50_000_000); // <50MB growth
  expect(memoryProfile.gcTriggered).toBe(true); // GC should run
});
```

### Render Performance

```typescript
test('should optimize render performance', async ({
  mcpPage,
  dashReactContext
}) => {
  const inspector = dashReactContext.inspector;
  const renderTracker = await inspector.trackReRenders('component-id');

  await renderTracker.startTracking();

  // Perform actions that should NOT cause re-renders
  await mcpPage.hover('[data-testid="static-element"]');
  await mcpPage.mouse.move(100, 100);

  // Perform actions that SHOULD cause re-renders
  await mcpPage.locator('[data-testid="update-button"]').click();

  const stats = await renderTracker.stopTracking();

  expect(stats.renderCount).toBeLessThan(3); // Minimal re-renders
  expect(stats.averageRenderTime).toBeLessThan(50); // Fast renders
});
```

## Best Practices

### 1. Test Structure

```typescript
// Use enhanced fixtures for Dash/React testing
import { test, expect } from '../utils/enhanced-dash-fixtures';

test.describe('Component Name - React/Dash Integration', () => {
  test.beforeEach(async ({ dashAppReady, performanceMonitor }) => {
    await dashAppReady; // Wait for Dash app to be ready
    performanceMonitor.mark('test-start');
  });

  test.describe('React State Management', () => {
    // State-specific tests
  });

  test.describe('Dash Callback Integration', () => {
    // Callback-specific tests
  });

  test.describe('Performance Validation', () => {
    // Performance tests
  });
});
```

### 2. Component State Validation

```typescript
// Always validate component state consistency
test('should maintain consistent state', async ({
  componentStateValidator
}) => {
  const validation = await componentStateValidator('component-id', {
    requiredProp: { type: 'string', required: true },
    optionalProp: { type: 'boolean', required: false }
  });

  expect(validation.valid).toBe(true);
  expect(validation.errors).toHaveLength(0);
});
```

### 3. Callback Order Testing

```typescript
// Test callback execution order
test('should execute callbacks in correct order', async ({
  callbackOrderValidator
}) => {
  const validator = await callbackOrderValidator([
    'input-validation-callback',
    'data-processing-callback',
    'ui-update-callback'
  ]);

  await validator.startMonitoring();

  // Trigger action
  await mcpPage.locator('[data-testid="submit"]').click();

  const result = await validator.validateOrder();
  expect(result.valid).toBe(true);
});
```

### 4. Performance Monitoring

```typescript
// Always include performance assertions
test('should meet performance requirements', async ({
  reactRenderProfiler,
  performanceMonitor
}) => {
  const profiler = await reactRenderProfiler('component-id');
  await profiler.startProfiling();

  // Perform test actions

  const profile = await profiler.getProfile();
  const metrics = await performanceMonitor.getMetrics();

  expect(profile.averageRenderTime).toBeLessThan(100);
  expect(metrics.memoryUsage).toBeLessThan(100_000_000);
});
```

## Common Patterns

### 1. File Upload Testing

```typescript
test('should handle file upload with React state', async ({
  mcpPage,
  testFiles,
  dashReactContext
}) => {
  // Track component state during upload
  const stateTracker = await dashReactContext.inspector.trackReRenders('upload-component');
  await stateTracker.startTracking();

  // Upload file
  await mcpPage.setInputFiles('input[type="file"]', testFiles.validMELDData.path);

  // Wait for processing
  await mcpPage.waitForSelector('[data-testid="upload-success"]');

  const renderStats = await stateTracker.stopTracking();

  // Validate state management
  expect(renderStats.renderCount).toBeGreaterThan(0);
  expect(renderStats.averageRenderTime).toBeLessThan(200);
});
```

### 2. Theme Testing

```typescript
test('should handle theme changes efficiently', async ({
  mcpPage,
  dashReactContext
}) => {
  const renderTracker = await dashReactContext.inspector.trackReRenders('app-container');
  await renderTracker.startTracking();

  // Change theme
  await mcpPage.locator('[data-testid="theme-toggle"]').click();
  await mcpPage.waitForTimeout(1000);

  const stats = await renderTracker.stopTracking();

  // Theme change should be efficient
  expect(stats.renderCount).toBeLessThan(10);
  expect(stats.averageRenderTime).toBeLessThan(100);

  // Verify theme applied
  const theme = await mcpPage.evaluate(() =>
    document.body.getAttribute('data-theme')
  );
  expect(theme).toBeTruthy();
});
```

### 3. Data Visualization Testing

```typescript
test('should render Plotly graphs with React optimization', async ({
  mcpPage,
  dashReactContext
}) => {
  // Wait for Plotly to render
  await mcpPage.waitForFunction(() => {
    const plot = document.querySelector('.js-plotly-plot') as any;
    return plot && plot._fullData && plot._fullData.length > 0;
  });

  // Test interaction performance
  const renderTracker = await dashReactContext.inspector.trackReRenders('graph-container');
  await renderTracker.startTracking();

  // Plotly interactions shouldn't trigger React re-renders
  await mcpPage.locator('.js-plotly-plot').hover();
  await mcpPage.mouse.wheel(0, -100);

  const stats = await renderTracker.stopTracking();

  // Minimal React involvement in Plotly interactions
  expect(stats.renderCount).toBeLessThan(2);
});
```

## Troubleshooting

### Common Issues

1. **Component Not Found**
   ```typescript
   // Wait for React component to mount
   await dashReactContext.inspector.waitForComponentRender('component-id');
   ```

2. **Callback Not Executing**
   ```typescript
   // Check callback registration
   const callbacks = await dashReactContext.callbacks.getComponentCallbacks('component-id');
   expect(callbacks.inputs.length).toBeGreaterThan(0);
   ```

3. **Performance Issues**
   ```typescript
   // Profile memory usage
   const memoryProfile = await dashReactContext.performance.profileMemoryUsage(10000);
   console.log('Memory growth:', memoryProfile.memoryGrowth);
   ```

4. **State Synchronization**
   ```typescript
   // Validate state consistency
   const state = await dashReactContext.inspector.getComponentState('component-id');
   expect(state.isConnected).toBe(true);
   ```

### Debugging Tips

1. **Enable Detailed Logging**
   ```typescript
   // Log callback execution
   const monitor = await dashReactContext.callbacks.monitorCallbackExecution();
   await monitor.startMonitoring();
   // ... perform actions ...
   const execution = await monitor.stopMonitoring();
   console.log('Callback execution:', execution);
   ```

2. **Memory Leak Detection**
   ```typescript
   // Check for memory leaks
   const memoryBefore = await mcpPage.evaluate(() =>
     (performance as any).memory?.usedJSHeapSize || 0
   );

   // ... perform test actions ...

   const memoryAfter = await mcpPage.evaluate(() =>
     (performance as any).memory?.usedJSHeapSize || 0
   );

   const memoryGrowth = memoryAfter - memoryBefore;
   expect(memoryGrowth).toBeLessThan(10_000_000); // 10MB threshold
   ```

3. **React DevTools Integration**
   ```typescript
   // Access React fiber for debugging
   const reactInfo = await mcpPage.evaluate((id) => {
     const element = document.getElementById(id);
     const reactKey = Object.keys(element).find(key =>
       key.startsWith('__reactFiber')
     );
     return reactKey ? (element as any)[reactKey] : null;
   }, 'component-id');
   ```

## Examples

### Complete Test Example

```typescript
import { test, expect } from '../utils/enhanced-dash-fixtures';
import { CallbackFlowTester } from '../utils/dash-callback-testing-strategies';

test.describe('MELD Data Upload - Complete Integration Test', () => {
  test('should handle complete upload workflow', async ({
    mcpPage,
    testFiles,
    dashReactContext,
    componentStateValidator,
    callbackOrderValidator,
    reactRenderProfiler,
    performanceMonitor
  }) => {
    // Setup performance monitoring
    const profiler = await reactRenderProfiler('upload-dropzone');
    await profiler.startProfiling();

    // Validate initial component state
    const initialValidation = await componentStateValidator('upload-dropzone', {
      accept: { type: 'string', required: false },
      disabled: { type: 'boolean', required: false }
    });
    expect(initialValidation.valid).toBe(true);

    // Setup callback monitoring
    const callbackValidator = await callbackOrderValidator([
      'upload-file-callback',
      'data-validation-callback',
      'ui-update-callback'
    ]);
    await callbackValidator.startMonitoring();

    performanceMonitor.mark('upload-test-start');

    // Perform file upload
    await mcpPage.setInputFiles('input[type="file"]', testFiles.validMELDData.path);

    // Wait for completion
    await mcpPage.waitForSelector('[data-testid="upload-success"]', { timeout: 15000 });

    performanceMonitor.mark('upload-test-complete');

    // Validate callback execution
    const callbackResult = await callbackValidator.validateOrder();
    expect(callbackResult.valid).toBe(true);
    expect(callbackResult.issues).toHaveLength(0);

    // Validate render performance
    const renderProfile = await profiler.getProfile();
    expect(renderProfile.renderCount).toBeGreaterThan(0);
    expect(renderProfile.averageRenderTime).toBeLessThan(150);
    expect(renderProfile.heavyRenders.length).toBeLessThan(2);

    // Validate overall performance
    const metrics = await performanceMonitor.getMetrics();
    expect(metrics.loadTime).toBeLessThan(10000);
    expect(metrics.memoryUsage).toBeLessThan(50_000_000);

    // Validate final component state
    const finalState = await dashReactContext.inspector.getComponentState('upload-dropzone');
    expect(finalState.isConnected).toBe(true);

    // Test error recovery
    const errorTester = new CallbackFlowTester(mcpPage);
    const errorResult = await errorTester.testCallbackFlow({
      triggerAction: async () => {
        await mcpPage.setInputFiles('input[type="file"]', testFiles.corruptedFile.path);
      },
      expectedFlow: [
        {
          callbackPattern: 'error-handling-callback',
          maxDuration: 2000,
          expectedStateChanges: [
            {
              componentId: 'upload-error',
              property: 'visible',
              expectedValue: true
            }
          ]
        }
      ]
    });

    expect(errorResult.success).toBe(true);
  });
});
```

This comprehensive guide provides the foundation for robust Dash/React testing in the MELD Visualizer application, leveraging React expertise to create more effective and efficient tests.
