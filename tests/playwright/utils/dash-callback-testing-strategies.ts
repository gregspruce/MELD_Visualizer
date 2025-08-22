/**
 * Advanced Dash Callback Testing Strategies
 * Comprehensive utilities for testing Dash callback dependencies, execution order, and error handling
 */

import { Page, Locator } from '@playwright/test';
import type { DashComponents } from '../types';

/**
 * Callback dependency graph analyzer
 */
export class CallbackDependencyAnalyzer {
  constructor(private page: Page) {}

  /**
   * Build a complete callback dependency graph
   */
  async buildDependencyGraph(): Promise<CallbackDependencyGraph> {
    return await this.page.evaluate(() => {
      const dash = (window as any).dash_clientside;
      if (!dash || !dash.callback_map) {
        return { nodes: [], edges: [], cycles: [] };
      }

      const nodes: CallbackNode[] = [];
      const edges: CallbackEdge[] = [];
      const componentOutputMap = new Map<string, string[]>();

      // Build nodes from callback map
      Object.entries(dash.callback_map).forEach(([callbackId, callback]: [string, any]) => {
        const node: CallbackNode = {
          id: callbackId,
          inputs: callback.inputs?.map((input: any) => `${input.id}.${input.property}`) || [],
          outputs: callback.outputs?.map((output: any) => `${output.id}.${output.property}`) || [],
          state: callback.state?.map((state: any) => `${state.id}.${state.property}`) || [],
          priority: callback.priority || 0,
          clientside: !!callback.clientside_function
        };

        nodes.push(node);

        // Track which components produce which outputs
        node.outputs.forEach(output => {
          if (!componentOutputMap.has(output)) {
            componentOutputMap.set(output, []);
          }
          componentOutputMap.get(output)!.push(callbackId);
        });
      });

      // Build edges based on input-output relationships
      nodes.forEach(node => {
        node.inputs.forEach(input => {
          const producers = componentOutputMap.get(input) || [];
          producers.forEach(producerCallbackId => {
            if (producerCallbackId !== node.id) {
              edges.push({
                from: producerCallbackId,
                to: node.id,
                dependency: input,
                type: 'input'
              });
            }
          });
        });

        // Add state dependencies
        node.state.forEach(stateInput => {
          const producers = componentOutputMap.get(stateInput) || [];
          producers.forEach(producerCallbackId => {
            if (producerCallbackId !== node.id) {
              edges.push({
                from: producerCallbackId,
                to: node.id,
                dependency: stateInput,
                type: 'state'
              });
            }
          });
        });
      });

      // Detect cycles using DFS
      const cycles = this.detectCycles(nodes, edges);

      return { nodes, edges, cycles };
    });
  }

  /**
   * Detect circular dependencies in callback graph
   */
  private async detectCycles(nodes: CallbackNode[], edges: CallbackEdge[]): Promise<string[][]> {
    const visited = new Set<string>();
    const recursionStack = new Set<string>();
    const cycles: string[][] = [];

    const dfs = (nodeId: string, path: string[]): void => {
      if (recursionStack.has(nodeId)) {
        // Found a cycle
        const cycleStart = path.indexOf(nodeId);
        if (cycleStart >= 0) {
          cycles.push(path.slice(cycleStart).concat(nodeId));
        }
        return;
      }

      if (visited.has(nodeId)) return;

      visited.add(nodeId);
      recursionStack.add(nodeId);

      const outgoingEdges = edges.filter(edge => edge.from === nodeId);
      outgoingEdges.forEach(edge => {
        dfs(edge.to, [...path, nodeId]);
      });

      recursionStack.delete(nodeId);
    };

    nodes.forEach(node => {
      if (!visited.has(node.id)) {
        dfs(node.id, []);
      }
    });

    return cycles;
  }

  /**
   * Get callback execution order recommendation
   */
  async getRecommendedExecutionOrder(): Promise<{
    order: string[];
    parallelizable: string[][];
    bottlenecks: string[];
  }> {
    const graph = await this.buildDependencyGraph();
    
    return await this.page.evaluate((graphData) => {
      const { nodes, edges } = graphData;
      
      // Topological sort for execution order
      const inDegree = new Map<string, number>();
      const adjList = new Map<string, string[]>();
      
      // Initialize
      nodes.forEach(node => {
        inDegree.set(node.id, 0);
        adjList.set(node.id, []);
      });
      
      // Build adjacency list and calculate in-degrees
      edges.forEach(edge => {
        adjList.get(edge.from)!.push(edge.to);
        inDegree.set(edge.to, (inDegree.get(edge.to) || 0) + 1);
      });
      
      // Kahn's algorithm for topological sorting
      const queue: string[] = [];
      const result: string[] = [];
      const parallelizable: string[][] = [];
      
      // Start with nodes that have no dependencies
      nodes.forEach(node => {
        if (inDegree.get(node.id) === 0) {
          queue.push(node.id);
        }
      });
      
      while (queue.length > 0) {
        const currentLevel = [...queue];
        if (currentLevel.length > 1) {
          parallelizable.push(currentLevel);
        }
        
        queue.length = 0;
        
        currentLevel.forEach(nodeId => {
          result.push(nodeId);
          
          const neighbors = adjList.get(nodeId) || [];
          neighbors.forEach(neighbor => {
            inDegree.set(neighbor, inDegree.get(neighbor)! - 1);
            if (inDegree.get(neighbor) === 0) {
              queue.push(neighbor);
            }
          });
        });
      }
      
      // Identify bottlenecks (nodes with high fan-in/fan-out)
      const bottlenecks = nodes
        .filter(node => {
          const fanIn = edges.filter(edge => edge.to === node.id).length;
          const fanOut = edges.filter(edge => edge.from === node.id).length;
          return fanIn > 3 || fanOut > 3;
        })
        .map(node => node.id);
      
      return {
        order: result,
        parallelizable,
        bottlenecks
      };
    }, graph);
  }
}

/**
 * Callback execution flow tester
 */
export class CallbackFlowTester {
  constructor(private page: Page) {}

  /**
   * Test callback execution with detailed flow analysis
   */
  async testCallbackFlow(options: {
    triggerAction: () => Promise<void>;
    expectedFlow: CallbackFlowExpectation[];
    timeout?: number;
    validateTiming?: boolean;
  }): Promise<CallbackFlowResult> {
    const { triggerAction, expectedFlow, timeout = 30000, validateTiming = true } = options;
    
    // Set up comprehensive callback monitoring
    await this.page.evaluate(() => {
      (window as any).__callbackFlowMonitoring = {
        active: false,
        flows: [],
        startTime: 0,
        componentStates: new Map(),
        networkRequests: []
      };
      
      const dash = (window as any).dash_clientside;
      const monitoring = (window as any).__callbackFlowMonitoring;
      
      if (dash && !dash.__flowMonitoringHooked) {
        // Hook into callback execution
        const originalCallback = dash.callback;
        dash.callback = function(callbackId: string, inputs: any, state: any) {
          if (monitoring.active) {
            const startTime = performance.now();
            
            // Record component states before callback
            const preStates = new Map();
            Object.keys(inputs).forEach(key => {
              const [componentId] = key.split('.');
              const element = document.getElementById(componentId);
              if (element) {
                preStates.set(componentId, {
                  props: (element as any).__reactInternalInstance$memoizedProps || {},
                  visible: element.offsetParent !== null,
                  value: (element as any).value
                });
              }
            });
            
            const result = originalCallback.call(this, callbackId, inputs, state);
            
            const handleResult = (outputs: any) => {
              const endTime = performance.now();
              
              // Record component states after callback
              const postStates = new Map();
              Object.keys(outputs || {}).forEach(key => {
                const [componentId] = key.split('.');
                const element = document.getElementById(componentId);
                if (element) {
                  postStates.set(componentId, {
                    props: (element as any).__reactInternalInstance$memoizedProps || {},
                    visible: element.offsetParent !== null,
                    value: (element as any).value
                  });
                }
              });
              
              monitoring.flows.push({
                callbackId,
                startTime: startTime - monitoring.startTime,
                duration: endTime - startTime,
                inputs,
                outputs: outputs || result,
                state,
                preStates: Object.fromEntries(preStates),
                postStates: Object.fromEntries(postStates),
                order: monitoring.flows.length
              });
            };
            
            if (result && typeof result.then === 'function') {
              result.then(handleResult);
            } else {
              handleResult(result);
            }
            
            return result;
          }
          
          return originalCallback.call(this, callbackId, inputs, state);
        };
        
        dash.__flowMonitoringHooked = true;
        
        // Hook into network requests
        const originalFetch = window.fetch;
        window.fetch = function(...args) {
          if (monitoring.active) {
            const startTime = performance.now();
            monitoring.networkRequests.push({
              url: args[0],
              startTime: startTime - monitoring.startTime,
              method: args[1]?.method || 'GET'
            });
          }
          return originalFetch.apply(this, args);
        };
      }
    });

    // Start monitoring
    await this.page.evaluate(() => {
      const monitoring = (window as any).__callbackFlowMonitoring;
      monitoring.active = true;
      monitoring.flows = [];
      monitoring.startTime = performance.now();
      monitoring.componentStates.clear();
      monitoring.networkRequests = [];
    });

    // Trigger the action
    const actionStartTime = Date.now();
    await triggerAction();

    // Wait for callbacks to complete
    await this.page.waitForTimeout(2000);

    // Stop monitoring and collect results
    const flowData = await this.page.evaluate(() => {
      const monitoring = (window as any).__callbackFlowMonitoring;
      monitoring.active = false;
      return {
        flows: monitoring.flows,
        networkRequests: monitoring.networkRequests,
        totalTime: performance.now() - monitoring.startTime
      };
    });

    // Analyze the flow
    return this.analyzeCallbackFlow(flowData, expectedFlow, validateTiming);
  }

  /**
   * Analyze callback flow results against expectations
   */
  private analyzeCallbackFlow(
    flowData: any, 
    expectedFlow: CallbackFlowExpectation[], 
    validateTiming: boolean
  ): CallbackFlowResult {
    const { flows, networkRequests, totalTime } = flowData;
    const issues: string[] = [];
    const timingIssues: string[] = [];
    
    // Validate execution order
    expectedFlow.forEach((expectation, index) => {
      const actualFlow = flows.find((f: any) => f.callbackId.includes(expectation.callbackPattern));
      
      if (!actualFlow) {
        issues.push(`Expected callback matching '${expectation.callbackPattern}' was not found`);
        return;
      }
      
      // Validate timing constraints
      if (validateTiming && expectation.maxDuration) {
        if (actualFlow.duration > expectation.maxDuration) {
          timingIssues.push(`Callback '${actualFlow.callbackId}' took ${actualFlow.duration}ms (max: ${expectation.maxDuration}ms)`);
        }
      }
      
      // Validate dependencies
      if (expectation.dependencies) {
        expectation.dependencies.forEach(dep => {
          const depFlow = flows.find((f: any) => f.callbackId.includes(dep));
          if (depFlow && depFlow.order >= actualFlow.order) {
            issues.push(`Dependency '${dep}' should execute before '${actualFlow.callbackId}'`);
          }
        });
      }
      
      // Validate component state changes
      if (expectation.expectedStateChanges) {
        expectation.expectedStateChanges.forEach(change => {
          const componentState = actualFlow.postStates[change.componentId];
          if (!componentState) {
            issues.push(`Component '${change.componentId}' state not recorded`);
            return;
          }
          
          if (change.property === 'visible' && componentState.visible !== change.expectedValue) {
            issues.push(`Component '${change.componentId}' visibility should be ${change.expectedValue}`);
          }
          
          if (change.property === 'value' && componentState.value !== change.expectedValue) {
            issues.push(`Component '${change.componentId}' value should be '${change.expectedValue}', got '${componentState.value}'`);
          }
        });
      }
    });
    
    // Analyze performance
    const performanceMetrics = {
      totalExecutionTime: totalTime,
      callbackCount: flows.length,
      averageCallbackTime: flows.length > 0 ? flows.reduce((sum: number, f: any) => sum + f.duration, 0) / flows.length : 0,
      networkRequestCount: networkRequests.length,
      slowestCallback: flows.reduce((slowest: any, current: any) => 
        current.duration > (slowest?.duration || 0) ? current : slowest, null
      )
    };
    
    return {
      success: issues.length === 0,
      executionOrder: flows.map((f: any) => ({ id: f.callbackId, order: f.order, duration: f.duration })),
      issues,
      timingIssues,
      performanceMetrics,
      componentStateChanges: flows.map((f: any) => ({
        callbackId: f.callbackId,
        changes: Object.keys(f.postStates).map(componentId => ({
          componentId,
          before: f.preStates[componentId],
          after: f.postStates[componentId]
        }))
      })),
      networkActivity: networkRequests
    };
  }
}

/**
 * Callback error resilience tester
 */
export class CallbackErrorResilienceTester {
  constructor(private page: Page) {}

  /**
   * Test callback error propagation and recovery
   */
  async testErrorResilience(options: {
    errorTrigger: () => Promise<void>;
    expectedErrorHandling: ErrorHandlingExpectation;
    recoveryActions?: Array<() => Promise<void>>;
  }): Promise<ErrorResilienceResult> {
    const { errorTrigger, expectedErrorHandling, recoveryActions = [] } = options;
    
    // Set up error monitoring
    const errorMonitoring = await this.setupErrorMonitoring();
    
    await errorMonitoring.start();
    
    // Trigger error
    let errorTriggered = false;
    try {
      await errorTrigger();
      await this.page.waitForTimeout(1000);
    } catch (error) {
      errorTriggered = true;
    }
    
    // Check initial error handling
    const initialResults = await errorMonitoring.getResults();
    
    // Test recovery
    const recoveryResults: RecoveryTestResult[] = [];
    
    for (const [index, recoveryAction] of recoveryActions.entries()) {
      try {
        await recoveryAction();
        await this.page.waitForTimeout(1000);
        
        const afterRecovery = await errorMonitoring.getResults();
        
        recoveryResults.push({
          actionIndex: index,
          successful: afterRecovery.callbacksWorking && !afterRecovery.hasActiveErrors,
          timeToRecover: afterRecovery.lastErrorTime ? Date.now() - afterRecovery.lastErrorTime : 0,
          errorsCleared: afterRecovery.errorCount < initialResults.errorCount
        });
      } catch (recoveryError) {
        recoveryResults.push({
          actionIndex: index,
          successful: false,
          timeToRecover: -1,
          errorsCleared: false,
          error: (recoveryError as Error).message
        });
      }
    }
    
    await errorMonitoring.stop();
    
    const finalResults = await errorMonitoring.getResults();
    
    return {
      errorTriggered,
      errorsCaught: finalResults.errorCount > 0,
      errorTypes: finalResults.errorTypes,
      appStillResponsive: finalResults.callbacksWorking,
      errorDisplayedToUser: await this.checkErrorDisplayed(),
      recoveryResults,
      meetsExpectations: this.validateErrorHandling(finalResults, expectedErrorHandling)
    };
  }

  /**
   * Set up comprehensive error monitoring
   */
  private async setupErrorMonitoring() {
    await this.page.evaluate(() => {
      (window as any).__errorMonitoring = {
        active: false,
        errors: [],
        callbackErrors: [],
        networkErrors: [],
        consoleErrors: [],
        lastErrorTime: 0,
        callbacksWorking: true
      };
      
      const monitoring = (window as any).__errorMonitoring;
      
      // Monitor console errors
      const originalConsoleError = console.error;
      console.error = function(...args) {
        if (monitoring.active) {
          monitoring.consoleErrors.push({
            timestamp: Date.now(),
            message: args.join(' '),
            stack: new Error().stack
          });
          monitoring.lastErrorTime = Date.now();
        }
        originalConsoleError.apply(console, args);
      };
      
      // Monitor callback errors
      const dash = (window as any).dash_clientside;
      if (dash && !dash.__errorMonitoringHooked) {
        const originalCallback = dash.callback;
        dash.callback = function(callbackId: string, inputs: any, state: any) {
          try {
            const result = originalCallback.call(this, callbackId, inputs, state);
            
            if (result && typeof result.then === 'function') {
              return result.catch((error: any) => {
                if (monitoring.active) {
                  monitoring.callbackErrors.push({
                    callbackId,
                    timestamp: Date.now(),
                    error: error.message || error.toString(),
                    inputs,
                    state
                  });
                  monitoring.lastErrorTime = Date.now();
                }
                throw error;
              });
            }
            
            return result;
          } catch (error: any) {
            if (monitoring.active) {
              monitoring.callbackErrors.push({
                callbackId,
                timestamp: Date.now(),
                error: error.message || error.toString(),
                inputs,
                state
              });
              monitoring.lastErrorTime = Date.now();
            }
            throw error;
          }
        };
        
        dash.__errorMonitoringHooked = true;
      }
      
      // Monitor network errors
      const originalFetch = window.fetch;
      window.fetch = function(...args) {
        const promise = originalFetch.apply(this, args);
        
        if (monitoring.active) {
          promise.catch(error => {
            monitoring.networkErrors.push({
              url: args[0],
              timestamp: Date.now(),
              error: error.message || error.toString()
            });
            monitoring.lastErrorTime = Date.now();
          });
        }
        
        return promise;
      };
      
      // Monitor unhandled promise rejections
      window.addEventListener('unhandledrejection', event => {
        if (monitoring.active) {
          monitoring.errors.push({
            type: 'unhandled_promise_rejection',
            timestamp: Date.now(),
            error: event.reason?.message || event.reason?.toString() || 'Unknown promise rejection'
          });
          monitoring.lastErrorTime = Date.now();
        }
      });
      
      // Monitor JavaScript errors
      window.addEventListener('error', event => {
        if (monitoring.active) {
          monitoring.errors.push({
            type: 'javascript_error',
            timestamp: Date.now(),
            error: event.error?.message || event.message,
            filename: event.filename,
            lineno: event.lineno,
            colno: event.colno
          });
          monitoring.lastErrorTime = Date.now();
        }
      });
    });

    return {
      start: async () => {
        await this.page.evaluate(() => {
          const monitoring = (window as any).__errorMonitoring;
          monitoring.active = true;
          monitoring.errors = [];
          monitoring.callbackErrors = [];
          monitoring.networkErrors = [];
          monitoring.consoleErrors = [];
          monitoring.lastErrorTime = 0;
          monitoring.callbacksWorking = true;
        });
      },
      
      stop: async () => {
        await this.page.evaluate(() => {
          (window as any).__errorMonitoring.active = false;
        });
      },
      
      getResults: async () => {
        return await this.page.evaluate(() => {
          const monitoring = (window as any).__errorMonitoring;
          
          // Test if callbacks are still working by checking if Dash is responsive
          try {
            const dash = (window as any).dash_clientside;
            monitoring.callbacksWorking = !!dash && typeof dash.callback === 'function';
          } catch {
            monitoring.callbacksWorking = false;
          }
          
          const allErrors = [
            ...monitoring.errors,
            ...monitoring.callbackErrors.map((e: any) => ({ type: 'callback_error', ...e })),
            ...monitoring.networkErrors.map((e: any) => ({ type: 'network_error', ...e })),
            ...monitoring.consoleErrors.map((e: any) => ({ type: 'console_error', ...e }))
          ];
          
          return {
            errorCount: allErrors.length,
            errorTypes: [...new Set(allErrors.map(e => e.type))],
            errors: allErrors,
            callbacksWorking: monitoring.callbacksWorking,
            hasActiveErrors: allErrors.some(e => Date.now() - e.timestamp < 5000),
            lastErrorTime: monitoring.lastErrorTime
          };
        });
      }
    };
  }

  /**
   * Check if error is displayed to user
   */
  private async checkErrorDisplayed(): Promise<boolean> {
    const errorSelectors = [
      '[data-testid="error"]',
      '.error-message',
      '.alert-danger',
      '[role="alert"]',
      '.notification.error',
      '.toast.error'
    ];
    
    for (const selector of errorSelectors) {
      if (await this.page.locator(selector).count() > 0) {
        const isVisible = await this.page.locator(selector).isVisible();
        if (isVisible) return true;
      }
    }
    
    return false;
  }

  /**
   * Validate error handling against expectations
   */
  private validateErrorHandling(
    results: any, 
    expectations: ErrorHandlingExpectation
  ): { valid: boolean; issues: string[] } {
    const issues: string[] = [];
    
    if (expectations.shouldCatchErrors && results.errorCount === 0) {
      issues.push('Expected errors to be caught, but none were detected');
    }
    
    if (expectations.shouldStayResponsive && !results.callbacksWorking) {
      issues.push('App became unresponsive after error');
    }
    
    if (expectations.shouldDisplayErrorToUser && !await this.checkErrorDisplayed()) {
      issues.push('Error should be displayed to user but was not found');
    }
    
    if (expectations.maxErrorRecoveryTime && results.lastErrorTime) {
      const recoveryTime = Date.now() - results.lastErrorTime;
      if (recoveryTime > expectations.maxErrorRecoveryTime) {
        issues.push(`Error recovery took ${recoveryTime}ms (max: ${expectations.maxErrorRecoveryTime}ms)`);
      }
    }
    
    return {
      valid: issues.length === 0,
      issues
    };
  }
}

// Type definitions
export interface CallbackDependencyGraph {
  nodes: CallbackNode[];
  edges: CallbackEdge[];
  cycles: string[][];
}

export interface CallbackNode {
  id: string;
  inputs: string[];
  outputs: string[];
  state: string[];
  priority: number;
  clientside: boolean;
}

export interface CallbackEdge {
  from: string;
  to: string;
  dependency: string;
  type: 'input' | 'state';
}

export interface CallbackFlowExpectation {
  callbackPattern: string;
  dependencies?: string[];
  maxDuration?: number;
  expectedStateChanges?: Array<{
    componentId: string;
    property: 'visible' | 'value' | 'props';
    expectedValue: any;
  }>;
}

export interface CallbackFlowResult {
  success: boolean;
  executionOrder: Array<{ id: string; order: number; duration: number }>;
  issues: string[];
  timingIssues: string[];
  performanceMetrics: {
    totalExecutionTime: number;
    callbackCount: number;
    averageCallbackTime: number;
    networkRequestCount: number;
    slowestCallback: any;
  };
  componentStateChanges: any[];
  networkActivity: any[];
}

export interface ErrorHandlingExpectation {
  shouldCatchErrors: boolean;
  shouldStayResponsive: boolean;
  shouldDisplayErrorToUser: boolean;
  maxErrorRecoveryTime?: number;
}

export interface ErrorResilienceResult {
  errorTriggered: boolean;
  errorsCaught: boolean;
  errorTypes: string[];
  appStillResponsive: boolean;
  errorDisplayedToUser: boolean;
  recoveryResults: RecoveryTestResult[];
  meetsExpectations: { valid: boolean; issues: string[] };
}

export interface RecoveryTestResult {
  actionIndex: number;
  successful: boolean;
  timeToRecover: number;
  errorsCleared: boolean;
  error?: string;
}

export {
  CallbackDependencyAnalyzer,
  CallbackFlowTester,
  CallbackErrorResilienceTester
};