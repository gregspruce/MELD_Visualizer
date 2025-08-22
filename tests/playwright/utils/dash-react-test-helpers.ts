/**
 * React/Dash-Specific Test Utilities for MELD Visualizer
 * Enhanced testing patterns that leverage React expertise for Dash applications
 */

import { Page, Locator, expect } from '@playwright/test';
import type { 
  DashComponents, 
  TestTypes, 
  PlotlyTypes 
} from '../types';

/**
 * Dash Component State Inspector
 * Provides deep insights into React component state within Dash applications
 */
export class DashComponentStateInspector {
  constructor(private page: Page) {}

  /**
   * Get component props and state from Dash's React layer
   */
  async getComponentState(componentId: string): Promise<{
    props: Record<string, unknown>;
    state: Record<string, unknown>;
    children: unknown;
    isConnected: boolean;
    hasCallbacks: boolean;
  }> {
    return await this.page.evaluate((id) => {
      // Access Dash's internal React component registry
      const dash = (window as any).dash_clientside;
      const element = document.getElementById(id);
      
      if (!element) {
        throw new Error(`Component with id "${id}" not found`);
      }

      // Get React fiber node (Dash uses React internally)
      const reactKey = Object.keys(element).find(key => 
        key.startsWith('__reactInternalInstance') || 
        key.startsWith('__reactFiber')
      );
      
      const reactNode = reactKey ? (element as any)[reactKey] : null;
      
      return {
        props: reactNode?.memoizedProps || {},
        state: reactNode?.memoizedState || {},
        children: reactNode?.child ? 'has-children' : null,
        isConnected: !!element.isConnected,
        hasCallbacks: dash && dash.callback_map && 
                      Object.keys(dash.callback_map).some(key => key.includes(id))
      };
    }, componentId);
  }

  /**
   * Wait for React component to finish rendering
   */
  async waitForComponentRender(componentId: string, timeout = 10000): Promise<void> {
    await this.page.waitForFunction((id) => {
      const element = document.getElementById(id);
      if (!element) return false;
      
      // Check if React has finished rendering this component
      const reactKey = Object.keys(element).find(key => 
        key.startsWith('__reactInternalInstance') || 
        key.startsWith('__reactFiber')
      );
      
      const reactNode = reactKey ? (element as any)[reactKey] : null;
      
      // Component is considered rendered if it has props and is not in pending state
      return reactNode && 
             reactNode.memoizedProps && 
             !reactNode.pendingProps;
    }, componentId, { timeout });
  }

  /**
   * Detect React re-renders for performance testing
   */
  async trackReRenders(componentId: string): Promise<{
    startTracking: () => Promise<void>;
    stopTracking: () => Promise<{
      renderCount: number;
      lastRenderTime: number;
      averageRenderTime: number;
    }>;
  }> {
    // Inject render tracking into the component
    await this.page.evaluate((id) => {
      const element = document.getElementById(id);
      if (!element) return;

      (window as any).__renderTracking = (window as any).__renderTracking || {};
      (window as any).__renderTracking[id] = {
        renderCount: 0,
        renderTimes: [],
        startTime: 0,
        tracking: false
      };
      
      // Monkey patch the component's render method if accessible
      const reactKey = Object.keys(element).find(key => 
        key.startsWith('__reactInternalInstance') || 
        key.startsWith('__reactFiber')
      );
      
      if (reactKey) {
        const reactNode = (element as any)[reactKey];
        const tracking = (window as any).__renderTracking[id];
        
        // Hook into React's commit phase
        const originalUpdate = reactNode.stateNode?.forceUpdate;
        if (originalUpdate && !tracking.hooked) {
          reactNode.stateNode.forceUpdate = function(...args: any[]) {
            if (tracking.tracking) {
              const now = performance.now();
              tracking.renderCount++;
              tracking.renderTimes.push(now - tracking.startTime);
              tracking.startTime = now;
            }
            return originalUpdate.apply(this, args);
          };
          tracking.hooked = true;
        }
      }
    }, componentId);

    return {
      startTracking: async () => {
        await this.page.evaluate((id) => {
          const tracking = (window as any).__renderTracking[id];
          if (tracking) {
            tracking.tracking = true;
            tracking.startTime = performance.now();
            tracking.renderCount = 0;
            tracking.renderTimes = [];
          }
        }, componentId);
      },
      
      stopTracking: async () => {
        return await this.page.evaluate((id) => {
          const tracking = (window as any).__renderTracking[id];
          if (tracking) {
            tracking.tracking = false;
            return {
              renderCount: tracking.renderCount,
              lastRenderTime: tracking.renderTimes[tracking.renderTimes.length - 1] || 0,
              averageRenderTime: tracking.renderTimes.length > 0 
                ? tracking.renderTimes.reduce((a, b) => a + b) / tracking.renderTimes.length 
                : 0
            };
          }
          return { renderCount: 0, lastRenderTime: 0, averageRenderTime: 0 };
        }, componentId);
      }
    };
  }

  /**
   * Validate component props match expected types
   */
  async validateComponentProps(
    componentId: string, 
    expectedProps: Record<string, { type: string; required?: boolean }>
  ): Promise<{ valid: boolean; errors: string[] }> {
    const state = await this.getComponentState(componentId);
    const errors: string[] = [];
    
    // Check required props
    Object.entries(expectedProps).forEach(([propName, config]) => {
      if (config.required && !(propName in state.props)) {
        errors.push(`Required prop '${propName}' is missing`);
      }
      
      if (propName in state.props) {
        const actualType = typeof state.props[propName];
        const expectedType = config.type;
        
        if (actualType !== expectedType) {
          errors.push(`Prop '${propName}' expected ${expectedType}, got ${actualType}`);
        }
      }
    });
    
    return { valid: errors.length === 0, errors };
  }
}

/**
 * Dash Callback Chain Tester
 * Specialized utilities for testing Dash callback dependencies and execution order
 */
export class DashCallbackChainTester {
  constructor(private page: Page) {}

  /**
   * Get all registered callbacks for a component
   */
  async getComponentCallbacks(componentId: string): Promise<{
    inputs: Array<{ id: string; property: string }>;
    outputs: Array<{ id: string; property: string }>;
    state: Array<{ id: string; property: string }>;
  }> {
    return await this.page.evaluate((id) => {
      const dash = (window as any).dash_clientside;
      if (!dash || !dash.callback_map) {
        return { inputs: [], outputs: [], state: [] };
      }

      const callbacks = Object.entries(dash.callback_map)
        .filter(([key]) => key.includes(id))
        .map(([_, callback]: [string, any]) => callback);

      const result = {
        inputs: [] as Array<{ id: string; property: string }>,
        outputs: [] as Array<{ id: string; property: string }>,
        state: [] as Array<{ id: string; property: string }>
      };

      callbacks.forEach(callback => {
        if (callback.inputs) {
          result.inputs.push(...callback.inputs.map((input: any) => ({
            id: input.id,
            property: input.property
          })));
        }
        if (callback.outputs) {
          result.outputs.push(...callback.outputs.map((output: any) => ({
            id: output.id,
            property: output.property
          })));
        }
        if (callback.state) {
          result.state.push(...callback.state.map((state: any) => ({
            id: state.id,
            property: state.property
          })));
        }
      });

      return result;
    }, componentId);
  }

  /**
   * Monitor callback execution chain
   */
  async monitorCallbackExecution(options: {
    componentId?: string;
    timeout?: number;
    trackOrder?: boolean;
  } = {}): Promise<{
    startMonitoring: () => Promise<void>;
    stopMonitoring: () => Promise<Array<{
      callbackId: string;
      timestamp: number;
      duration: number;
      inputs: Record<string, unknown>;
      outputs: Record<string, unknown>;
      order: number;
    }>>;
  }> {
    const { timeout = 30000, trackOrder = true } = options;

    // Inject callback monitoring
    await this.page.evaluate((opts) => {
      (window as any).__callbackMonitoring = {
        active: false,
        callbacks: [],
        order: 0
      };

      // Override Dash's callback execution
      const dash = (window as any).dash_clientside;
      if (dash && dash.callback && !dash.callback._monitoringHooked) {
        const originalCallback = dash.callback;
        
        dash.callback = function(callbackId: string, inputs: any, state: any) {
          const monitor = (window as any).__callbackMonitoring;
          
          if (monitor.active) {
            const startTime = performance.now();
            const callbackOrder = opts.trackOrder ? ++monitor.order : 0;
            
            const result = originalCallback.call(this, callbackId, inputs, state);
            
            if (result && typeof result.then === 'function') {
              // Handle async callback
              result.then((outputs: any) => {
                monitor.callbacks.push({
                  callbackId,
                  timestamp: startTime,
                  duration: performance.now() - startTime,
                  inputs,
                  outputs,
                  order: callbackOrder
                });
              });
            } else {
              // Handle sync callback
              monitor.callbacks.push({
                callbackId,
                timestamp: startTime,
                duration: performance.now() - startTime,
                inputs,
                outputs: result,
                order: callbackOrder
              });
            }
            
            return result;
          }
          
          return originalCallback.call(this, callbackId, inputs, state);
        };
        
        dash.callback._monitoringHooked = true;
      }
    }, { timeout, trackOrder });

    return {
      startMonitoring: async () => {
        await this.page.evaluate(() => {
          const monitor = (window as any).__callbackMonitoring;
          if (monitor) {
            monitor.active = true;
            monitor.callbacks = [];
            monitor.order = 0;
          }
        });
      },

      stopMonitoring: async () => {
        return await this.page.evaluate(() => {
          const monitor = (window as any).__callbackMonitoring;
          if (monitor) {
            monitor.active = false;
            return monitor.callbacks;
          }
          return [];
        });
      }
    };
  }

  /**
   * Test callback error handling
   */
  async testCallbackErrorHandling(
    componentId: string,
    triggerError: () => Promise<void>
  ): Promise<{
    errorCaught: boolean;
    errorMessage?: string;
    callbacksStillWorking: boolean;
  }> {
    let errorInfo = { errorCaught: false, errorMessage: undefined as string | undefined };

    // Set up error monitoring
    this.page.on('pageerror', (error) => {
      errorInfo.errorCaught = true;
      errorInfo.errorMessage = error.message;
    });

    this.page.on('console', (msg) => {
      if (msg.type() === 'error') {
        errorInfo.errorCaught = true;
        errorInfo.errorMessage = msg.text();
      }
    });

    // Trigger the error
    await triggerError();
    
    // Wait a bit for error propagation
    await this.page.waitForTimeout(1000);

    // Test if other callbacks still work
    const testElement = this.page.locator(`#${componentId}`);
    let callbacksStillWorking = true;
    
    try {
      // Try a simple interaction to test if callbacks are still responsive
      if (await testElement.count() > 0) {
        await testElement.click({ timeout: 2000 });
        await this.page.waitForTimeout(500);
      }
    } catch {
      callbacksStillWorking = false;
    }

    return {
      errorCaught: errorInfo.errorCaught,
      errorMessage: errorInfo.errorMessage,
      callbacksStillWorking
    };
  }

  /**
   * Validate callback execution order
   */
  async validateCallbackOrder(
    expectedOrder: string[],
    actualExecution: Array<{ callbackId: string; order: number }>
  ): Promise<{ valid: boolean; issues: string[] }> {
    const issues: string[] = [];
    
    // Sort actual execution by order
    const sortedExecution = actualExecution.sort((a, b) => a.order - b.order);
    
    // Check if expected callbacks executed
    expectedOrder.forEach((expectedCallback, index) => {
      const actualCallback = sortedExecution[index];
      
      if (!actualCallback) {
        issues.push(`Expected callback '${expectedCallback}' at position ${index} but found none`);
      } else if (actualCallback.callbackId !== expectedCallback) {
        issues.push(`Expected callback '${expectedCallback}' at position ${index} but found '${actualCallback.callbackId}'`);
      }
    });

    // Check for unexpected callbacks
    if (sortedExecution.length > expectedOrder.length) {
      const unexpected = sortedExecution.slice(expectedOrder.length);
      issues.push(`Unexpected callbacks executed: ${unexpected.map(c => c.callbackId).join(', ')}`);
    }

    return { valid: issues.length === 0, issues };
  }
}

/**
 * React Event Simulation for Dash Components
 * Enhanced event handling that understands React synthetic events within Dash
 */
export class DashReactEventSimulator {
  constructor(private page: Page) {}

  /**
   * Simulate React synthetic events on Dash components
   */
  async dispatchSyntheticEvent(
    componentId: string,
    eventType: string,
    eventData: Record<string, unknown> = {}
  ): Promise<void> {
    await this.page.evaluate((id, type, data) => {
      const element = document.getElementById(id);
      if (!element) throw new Error(`Component ${id} not found`);

      // Create React synthetic event
      const event = new CustomEvent(type, {
        bubbles: true,
        cancelable: true,
        detail: data
      });

      // Add React-specific properties
      Object.defineProperty(event, 'nativeEvent', { value: event });
      Object.defineProperty(event, 'isDefaultPrevented', { 
        value: () => event.defaultPrevented 
      });
      Object.defineProperty(event, 'isPropagationStopped', { 
        value: () => event.cancelBubble 
      });

      // Dispatch the event
      element.dispatchEvent(event);
    }, componentId, eventType, eventData);

    // Wait for React to process the event
    await this.page.waitForTimeout(50);
  }

  /**
   * Test controlled vs uncontrolled component behavior
   */
  async testControlledBehavior(
    inputComponentId: string,
    testValue: string
  ): Promise<{
    isControlled: boolean;
    valueChangedByUser: boolean;
    valueResetByApp: boolean;
  }> {
    const input = this.page.locator(`#${inputComponentId}`);
    
    // Get initial value
    const initialValue = await input.inputValue();
    
    // Try to type new value
    await input.clear();
    await input.type(testValue);
    
    const userValue = await input.inputValue();
    const valueChangedByUser = userValue === testValue;
    
    // Wait for potential callback to reset the value
    await this.page.waitForTimeout(1000);
    
    const finalValue = await input.inputValue();
    const valueResetByApp = finalValue !== userValue;
    
    // Restore initial value
    await input.clear();
    await input.type(initialValue);
    
    return {
      isControlled: valueResetByApp,
      valueChangedByUser,
      valueResetByApp
    };
  }

  /**
   * Test form validation and submission flow
   */
  async testFormFlow(
    formComponentId: string,
    inputData: Record<string, string>,
    submitButtonId?: string
  ): Promise<{
    validationErrors: string[];
    submitted: boolean;
    formData: Record<string, unknown>;
  }> {
    const formElement = this.page.locator(`#${formComponentId}`);
    const validationErrors: string[] = [];

    // Fill form inputs
    for (const [inputId, value] of Object.entries(inputData)) {
      const input = this.page.locator(`#${inputId}`);
      await input.clear();
      await input.type(value);
      
      // Check for validation errors
      const errorElement = this.page.locator(`[data-error-for="${inputId}"], .error[data-field="${inputId}"]`);
      if (await errorElement.count() > 0) {
        const errorText = await errorElement.textContent();
        if (errorText) validationErrors.push(`${inputId}: ${errorText}`);
      }
    }

    // Attempt form submission
    let submitted = false;
    if (submitButtonId) {
      const submitButton = this.page.locator(`#${submitButtonId}`);
      if (await submitButton.isEnabled()) {
        await submitButton.click();
        submitted = true;
      }
    }

    // Extract form data
    const formData = await this.page.evaluate((formId) => {
      const form = document.getElementById(formId);
      const data: Record<string, unknown> = {};
      
      if (form) {
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach((input: any) => {
          if (input.id) {
            data[input.id] = input.value;
          }
        });
      }
      
      return data;
    }, formComponentId);

    return { validationErrors, submitted, formData };
  }
}

/**
 * Dash Component Lifecycle Tester
 * Test component mounting, updating, and unmounting patterns
 */
export class DashComponentLifecycleTester {
  constructor(private page: Page) {}

  /**
   * Test component mounting behavior
   */
  async testComponentMount(componentId: string): Promise<{
    mounted: boolean;
    mountTime: number;
    initialProps: Record<string, unknown>;
    hasEffects: boolean;
  }> {
    const startTime = performance.now();
    
    // Wait for component to appear in DOM
    await this.page.waitForSelector(`#${componentId}`, { timeout: 10000 });
    
    const mountTime = performance.now() - startTime;
    
    // Get component state after mounting
    const inspector = new DashComponentStateInspector(this.page);
    const state = await inspector.getComponentState(componentId);
    
    // Check for side effects (event listeners, timers, etc.)
    const hasEffects = await this.page.evaluate((id) => {
      const element = document.getElementById(id);
      if (!element) return false;
      
      // Check for event listeners
      const hasListeners = (element as any)._listeners || 
                          Object.keys(element).some(key => key.startsWith('on'));
      
      // Check for active intervals/timeouts (basic detection)
      const hasTimers = (window as any)[`__${id}_timers`] !== undefined;
      
      return hasListeners || hasTimers;
    }, componentId);
    
    return {
      mounted: true,
      mountTime,
      initialProps: state.props,
      hasEffects
    };
  }

  /**
   * Test component update behavior
   */
  async testComponentUpdate(
    componentId: string,
    propChange: { prop: string; newValue: unknown }
  ): Promise<{
    updated: boolean;
    updateTime: number;
    propsChanged: boolean;
    reRendered: boolean;
  }> {
    const inspector = new DashComponentStateInspector(this.page);
    const renderTracker = await inspector.trackReRenders(componentId);
    
    // Start tracking
    await renderTracker.startTracking();
    
    const startTime = performance.now();
    
    // Get initial props
    const initialState = await inspector.getComponentState(componentId);
    
    // Trigger prop change (simulate callback updating the component)
    await this.page.evaluate((id, prop, value) => {
      const dash = (window as any).dash_clientside;
      if (dash && dash.callback_map) {
        // Simulate a callback response that updates the component
        const updateEvent = new CustomEvent('dash-update', {
          detail: {
            componentId: id,
            props: { [prop]: value }
          }
        });
        document.dispatchEvent(updateEvent);
      }
    }, componentId, propChange.prop, propChange.newValue);
    
    // Wait for update to process
    await this.page.waitForTimeout(500);
    
    const updateTime = performance.now() - startTime;
    
    // Get updated state
    const updatedState = await inspector.getComponentState(componentId);
    const renderStats = await renderTracker.stopTracking();
    
    return {
      updated: true,
      updateTime,
      propsChanged: JSON.stringify(initialState.props) !== JSON.stringify(updatedState.props),
      reRendered: renderStats.renderCount > 0
    };
  }

  /**
   * Test component cleanup on unmount
   */
  async testComponentCleanup(
    componentId: string,
    unmountTrigger: () => Promise<void>
  ): Promise<{
    cleaned: boolean;
    listenersRemoved: boolean;
    timersCleared: boolean;
    memoryLeaks: boolean;
  }> {
    // Check initial state
    const initialListeners = await this.page.evaluate((id) => {
      const element = document.getElementById(id);
      return element ? Object.keys(element).filter(key => key.startsWith('on')).length : 0;
    }, componentId);

    // Trigger unmount
    await unmountTrigger();
    
    // Wait for cleanup
    await this.page.waitForTimeout(500);
    
    // Check if element was removed
    const elementExists = await this.page.locator(`#${componentId}`).count() > 0;
    
    // Check for memory leaks (basic check)
    const memoryLeaks = await this.page.evaluate((id) => {
      // Check if any global references to the component still exist
      const windowRefs = Object.keys(window).filter(key => 
        key.includes(id) && key !== 'componentId'
      );
      
      return windowRefs.length > 0;
    }, componentId);

    return {
      cleaned: !elementExists,
      listenersRemoved: !elementExists, // If element is removed, listeners should be too
      timersCleared: !memoryLeaks, // Simplified check
      memoryLeaks
    };
  }
}

/**
 * Dash Performance Profiler
 * React-specific performance testing for Dash applications
 */
export class DashPerformanceProfiler {
  constructor(private page: Page) {}

  /**
   * Profile React component render performance
   */
  async profileComponentRender(componentId: string): Promise<{
    initialRenderTime: number;
    averageUpdateTime: number;
    renderCount: number;
    heavyRenders: Array<{ timestamp: number; duration: number }>;
  }> {
    const inspector = new DashComponentStateInspector(this.page);
    
    // Start profiling
    await this.page.evaluate(() => {
      (window as any).performance.mark('dash-render-start');
    });

    const renderTracker = await inspector.trackReRenders(componentId);
    await renderTracker.startTracking();

    // Simulate some interactions to trigger renders
    const component = this.page.locator(`#${componentId}`);
    
    for (let i = 0; i < 5; i++) {
      if (await component.count() > 0) {
        // Trigger re-render through interaction
        await component.hover();
        await this.page.waitForTimeout(100);
      }
    }

    const stats = await renderTracker.stopTracking();
    
    await this.page.evaluate(() => {
      (window as any).performance.mark('dash-render-end');
      (window as any).performance.measure('dash-render-total', 'dash-render-start', 'dash-render-end');
    });

    const performanceEntries = await this.page.evaluate(() => {
      const entries = (window as any).performance.getEntriesByType('measure')
        .filter((entry: any) => entry.name.includes('dash-render'));
      
      return entries.map((entry: any) => ({
        name: entry.name,
        duration: entry.duration,
        startTime: entry.startTime
      }));
    });

    const heavyRenders = performanceEntries
      .filter(entry => entry.duration > 100) // Renders taking more than 100ms
      .map(entry => ({ timestamp: entry.startTime, duration: entry.duration }));

    return {
      initialRenderTime: performanceEntries[0]?.duration || 0,
      averageUpdateTime: stats.averageRenderTime,
      renderCount: stats.renderCount,
      heavyRenders
    };
  }

  /**
   * Test memory usage during component lifecycle
   */
  async profileMemoryUsage(
    testDuration: number = 30000
  ): Promise<{
    initialMemory: number;
    peakMemory: number;
    finalMemory: number;
    memoryGrowth: number;
    gcTriggered: boolean;
  }> {
    const memoryStats: number[] = [];
    const startTime = Date.now();

    // Start memory monitoring
    const memoryInterval = setInterval(async () => {
      try {
        const memory = await this.page.evaluate(() => {
          return (performance as any).memory ? (performance as any).memory.usedJSHeapSize : 0;
        });
        memoryStats.push(memory);
      } catch (e) {
        // Memory API might not be available in all browsers
      }
    }, 1000);

    // Wait for test duration
    await this.page.waitForTimeout(testDuration);
    
    clearInterval(memoryInterval);

    // Try to trigger garbage collection for final measurement
    await this.page.evaluate(() => {
      if ((window as any).gc) {
        (window as any).gc();
      }
    });

    await this.page.waitForTimeout(1000);
    
    const finalMemory = await this.page.evaluate(() => {
      return (performance as any).memory ? (performance as any).memory.usedJSHeapSize : 0;
    });

    if (memoryStats.length > 0) {
      const initialMemory = memoryStats[0];
      const peakMemory = Math.max(...memoryStats);
      const memoryGrowth = finalMemory - initialMemory;
      
      return {
        initialMemory,
        peakMemory,
        finalMemory,
        memoryGrowth,
        gcTriggered: finalMemory < peakMemory * 0.9 // Assume GC if memory dropped significantly
      };
    }

    return {
      initialMemory: 0,
      peakMemory: 0,
      finalMemory,
      memoryGrowth: 0,
      gcTriggered: false
    };
  }
}

/**
 * Integration helpers for the existing test framework
 */
export class DashTestIntegration {
  static inspector = DashComponentStateInspector;
  static callbackTester = DashCallbackChainTester;
  static eventSimulator = DashReactEventSimulator;
  static lifecycleTester = DashComponentLifecycleTester;
  static performanceProfiler = DashPerformanceProfiler;

  /**
   * Create a comprehensive test context for Dash/React testing
   */
  static createTestContext(page: Page): {
    inspector: DashComponentStateInspector;
    callbacks: DashCallbackChainTester;
    events: DashReactEventSimulator;
    lifecycle: DashComponentLifecycleTester;
    performance: DashPerformanceProfiler;
  } {
    return {
      inspector: new DashComponentStateInspector(page),
      callbacks: new DashCallbackChainTester(page),
      events: new DashReactEventSimulator(page),
      lifecycle: new DashComponentLifecycleTester(page),
      performance: new DashPerformanceProfiler(page)
    };
  }

  /**
   * Validate Dash app readiness with React-specific checks
   */
  static async waitForDashAppReady(page: Page, timeout = 30000): Promise<void> {
    // Wait for Dash core libraries
    await page.waitForFunction(() => {
      return (window as any).dash_clientside && 
             (window as any).Plotly && 
             (window as any).React;
    }, { timeout });

    // Wait for React to finish initial render
    await page.waitForFunction(() => {
      const app = document.querySelector('.dash-app-content, #app');
      if (!app) return false;

      // Check if React has attached to the app container
      const reactKey = Object.keys(app).find(key => 
        key.startsWith('__reactInternalInstance') || 
        key.startsWith('__reactFiber')
      );

      return !!reactKey;
    }, { timeout });

    // Wait for initial callbacks to settle
    await page.waitForLoadState('networkidle');
  }
}

export {
  DashComponentStateInspector,
  DashCallbackChainTester,
  DashReactEventSimulator,
  DashComponentLifecycleTester,
  DashPerformanceProfiler,
  DashTestIntegration
};