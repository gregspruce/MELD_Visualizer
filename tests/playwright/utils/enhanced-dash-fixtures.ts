/**
 * Enhanced Playwright Fixtures with React/Dash Integration
 * Extends the existing MCP fixtures with Dash/React-specific testing capabilities
 */

import { test as base } from '@playwright/test';
import { DashTestIntegration } from './dash-react-test-helpers';
import type { Page } from '@playwright/test';

/**
 * Enhanced fixtures that extend the existing mcp-fixtures
 */
export const enhancedTest = base.extend<{
  dashReactContext: {
    inspector: import('./dash-react-test-helpers').DashComponentStateInspector;
    callbacks: import('./dash-react-test-helpers').DashCallbackChainTester;
    events: import('./dash-react-test-helpers').DashReactEventSimulator;
    lifecycle: import('./dash-react-test-helpers').DashComponentLifecycleTester;
    performance: import('./dash-react-test-helpers').DashPerformanceProfiler;
  };

  dashAppReady: void;

  componentStateValidator: (componentId: string, expectedProps: Record<string, any>) => Promise<{
    valid: boolean;
    errors: string[];
  }>;

  callbackOrderValidator: (expectedOrder: string[]) => Promise<{
    startMonitoring: () => Promise<void>;
    validateOrder: () => Promise<{ valid: boolean; issues: string[] }>;
  }>;

  reactRenderProfiler: (componentId: string) => Promise<{
    startProfiling: () => Promise<void>;
    getProfile: () => Promise<{
      renderCount: number;
      averageRenderTime: number;
      heavyRenders: Array<{ timestamp: number; duration: number }>;
    }>;
  }>;

  dashComponentTester: {
    testComponentMount: (componentId: string) => Promise<{
      mounted: boolean;
      mountTime: number;
      hasCallbacks: boolean;
    }>;

    testComponentUpdate: (componentId: string, triggerUpdate: () => Promise<void>) => Promise<{
      updated: boolean;
      renderTime: number;
      propsChanged: boolean;
    }>;

    testCallbackChain: (triggerElement: string, expectedCallbacks: string[]) => Promise<{
      executed: boolean;
      order: Array<{ callbackId: string; timestamp: number; duration: number }>;
      errors: string[];
    }>;

    testFormValidation: (formId: string, testData: Record<string, string>) => Promise<{
      validated: boolean;
      errors: Array<{ field: string; message: string }>;
      submitted: boolean;
    }>;
  };
}>({
  /**
   * Enhanced Dash/React test context
   */
  dashReactContext: async ({ page }, use) => {
    const context = DashTestIntegration.createTestContext(page);
    await use(context);
  },

  /**
   * Wait for Dash app to be fully ready with React integration
   */
  dashAppReady: async ({ page }, use) => {
    await DashTestIntegration.waitForDashAppReady(page);

    // Additional readiness checks for MELD Visualizer
    await page.waitForSelector('[data-testid="app-container"], .dash-app-content, #app', {
      timeout: 30000
    });

    // Wait for initial theme application
    await page.waitForFunction(() => {
      const body = document.body;
      return body.classList.length > 0 || body.style.length > 0;
    }, { timeout: 10000 });

    await use();
  },

  /**
   * Component state validation fixture
   */
  componentStateValidator: async ({ dashReactContext }, use) => {
    const validator = async (componentId: string, expectedProps: Record<string, any>) => {
      return await dashReactContext.inspector.validateComponentProps(componentId, expectedProps);
    };

    await use(validator);
  },

  /**
   * Callback order validation fixture
   */
  callbackOrderValidator: async ({ dashReactContext }, use) => {
    const createValidator = async (expectedOrder: string[]) => {
      const monitor = await dashReactContext.callbacks.monitorCallbackExecution({
        trackOrder: true
      });

      return {
        startMonitoring: monitor.startMonitoring,
        validateOrder: async () => {
          const execution = await monitor.stopMonitoring();
          return await dashReactContext.callbacks.validateCallbackOrder(expectedOrder, execution);
        }
      };
    };

    await use(createValidator);
  },

  /**
   * React render profiling fixture
   */
  reactRenderProfiler: async ({ dashReactContext }, use) => {
    const createProfiler = async (componentId: string) => {
      const tracker = await dashReactContext.inspector.trackReRenders(componentId);

      return {
        startProfiling: tracker.startTracking,
        getProfile: async () => {
          const stats = await tracker.stopTracking();
          const performance = await dashReactContext.performance.profileComponentRender(componentId);

          return {
            renderCount: stats.renderCount,
            averageRenderTime: stats.averageRenderTime,
            heavyRenders: performance.heavyRenders
          };
        }
      };
    };

    await use(createProfiler);
  },

  /**
   * Comprehensive Dash component testing fixture
   */
  dashComponentTester: async ({ dashReactContext, page }, use) => {
    const tester = {
      testComponentMount: async (componentId: string) => {
        const result = await dashReactContext.lifecycle.testComponentMount(componentId);
        const callbacks = await dashReactContext.callbacks.getComponentCallbacks(componentId);

        return {
          mounted: result.mounted,
          mountTime: result.mountTime,
          hasCallbacks: callbacks.inputs.length > 0 || callbacks.outputs.length > 0
        };
      },

      testComponentUpdate: async (componentId: string, triggerUpdate: () => Promise<void>) => {
        const tracker = await dashReactContext.inspector.trackReRenders(componentId);
        await tracker.startTracking();

        const startTime = performance.now();
        const initialState = await dashReactContext.inspector.getComponentState(componentId);

        await triggerUpdate();

        // Wait for update to propagate
        await page.waitForTimeout(500);

        const finalState = await dashReactContext.inspector.getComponentState(componentId);
        const renderStats = await tracker.stopTracking();
        const updateTime = performance.now() - startTime;

        return {
          updated: true,
          renderTime: updateTime,
          propsChanged: JSON.stringify(initialState.props) !== JSON.stringify(finalState.props)
        };
      },

      testCallbackChain: async (triggerElement: string, expectedCallbacks: string[]) => {
        const monitor = await dashReactContext.callbacks.monitorCallbackExecution({
          trackOrder: true
        });

        await monitor.startMonitoring();

        // Trigger the callback chain
        const element = page.locator(`#${triggerElement}`);
        await element.click();

        // Wait for callbacks to complete
        await page.waitForTimeout(2000);

        const execution = await monitor.stopMonitoring();
        const validation = await dashReactContext.callbacks.validateCallbackOrder(
          expectedCallbacks,
          execution
        );

        return {
          executed: execution.length > 0,
          order: execution,
          errors: validation.issues
        };
      },

      testFormValidation: async (formId: string, testData: Record<string, string>) => {
        const result = await dashReactContext.events.testFormFlow(formId, testData);

        return {
          validated: result.validationErrors.length === 0,
          errors: result.validationErrors.map(error => {
            const [field, message] = error.split(': ');
            return { field, message };
          }),
          submitted: result.submitted
        };
      }
    };

    await use(tester);
  }
});

/**
 * Custom test matchers for Dash/React components
 */
export const dashExpect = {
  /**
   * Validate that a Dash component has proper React state
   */
  async toHaveValidReactState(
    componentId: string,
    expectedState: Record<string, any>,
    dashContext: any
  ) {
    const state = await dashContext.inspector.getComponentState(componentId);

    const missingProps = Object.keys(expectedState).filter(key =>
      !(key in state.props) && expectedState[key].required !== false
    );

    const invalidTypes = Object.keys(expectedState).filter(key => {
      if (key in state.props && expectedState[key].type) {
        return typeof state.props[key] !== expectedState[key].type;
      }
      return false;
    });

    const valid = missingProps.length === 0 && invalidTypes.length === 0;

    return {
      pass: valid,
      message: () => valid
        ? `Expected component ${componentId} not to have valid React state`
        : `Component ${componentId} has invalid React state. Missing: [${missingProps.join(', ')}], Wrong types: [${invalidTypes.join(', ')}]`
    };
  },

  /**
   * Validate that callbacks execute in the correct order
   */
  async toHaveCorrectCallbackOrder(
    actualExecution: Array<{ callbackId: string; order: number }>,
    expectedOrder: string[],
    callbackTester: any
  ) {
    const validation = await callbackTester.validateCallbackOrder(expectedOrder, actualExecution);

    return {
      pass: validation.valid,
      message: () => validation.valid
        ? `Expected callback order to be incorrect`
        : `Callback execution order issues: ${validation.issues.join(', ')}`
    };
  },

  /**
   * Validate component performance meets thresholds
   */
  async toMeetRenderPerformance(
    profileData: { renderCount: number; averageRenderTime: number; heavyRenders: any[] },
    thresholds: { maxRenderTime?: number; maxHeavyRenders?: number }
  ) {
    const { maxRenderTime = 50, maxHeavyRenders = 2 } = thresholds;

    const performant =
      profileData.averageRenderTime <= maxRenderTime &&
      profileData.heavyRenders.length <= maxHeavyRenders;

    return {
      pass: performant,
      message: () => performant
        ? `Expected component not to meet performance thresholds`
        : `Component performance issues: Average render time ${profileData.averageRenderTime}ms (max ${maxRenderTime}ms), Heavy renders ${profileData.heavyRenders.length} (max ${maxHeavyRenders})`
    };
  },

  /**
   * Validate that a component properly handles controlled/uncontrolled behavior
   */
  async toBeProperlyControlled(
    componentId: string,
    testValue: string,
    eventSimulator: any
  ) {
    const result = await eventSimulator.testControlledBehavior(componentId, testValue);

    return {
      pass: result.isControlled,
      message: () => result.isControlled
        ? `Expected component ${componentId} not to be properly controlled`
        : `Component ${componentId} is not properly controlled. User value changed: ${result.valueChangedByUser}, App reset: ${result.valueResetByApp}`
    };
  }
};

export { enhancedTest as test };
