/**
 * Real-time Performance Monitoring for MELD Visualizer
 * Integrates Core Web Vitals and React performance tracking
 */

class PerformanceMonitor {
    constructor() {
        this.metrics = new Map();
        this.observers = new Map();
        this.thresholds = {
            renderTime: 16, // 60fps target
            memoryUsage: 150 * 1024 * 1024, // 150MB
            callbackDuration: 100, // 100ms
            lcp: 2500, // Core Web Vitals
            fid: 100,
            cls: 0.1
        };
        this.init();
    }

    init() {
        this.setupPerformanceObservers();
        this.setupReactProfiling();
        this.setupMemoryMonitoring();
        this.setupDashCallbackMonitoring();
        this.startMonitoring();
    }

    /**
     * Setup Performance Observers for Core Web Vitals
     */
    setupPerformanceObservers() {
        // Largest Contentful Paint (LCP)
        if ('PerformanceObserver' in window) {
            const lcpObserver = new PerformanceObserver((list) => {
                for (const entry of list.getEntries()) {
                    this.recordMetric('lcp', entry.startTime);
                    if (entry.startTime > this.thresholds.lcp) {
                        console.warn(`LCP threshold exceeded: ${entry.startTime}ms`);
                    }
                }
            });

            try {
                lcpObserver.observe({ type: 'largest-contentful-paint', buffered: true });
                this.observers.set('lcp', lcpObserver);
            } catch (e) {
                console.warn('LCP observer not supported');
            }

            // First Input Delay (FID)
            const fidObserver = new PerformanceObserver((list) => {
                for (const entry of list.getEntries()) {
                    this.recordMetric('fid', entry.processingStart - entry.startTime);
                }
            });

            try {
                fidObserver.observe({ type: 'first-input', buffered: true });
                this.observers.set('fid', fidObserver);
            } catch (e) {
                console.warn('FID observer not supported');
            }

            // Cumulative Layout Shift (CLS)
            let clsValue = 0;
            const clsObserver = new PerformanceObserver((list) => {
                for (const entry of list.getEntries()) {
                    if (!entry.hadRecentInput) {
                        clsValue += entry.value;
                        this.recordMetric('cls', clsValue);
                        if (clsValue > this.thresholds.cls) {
                            console.warn(`CLS threshold exceeded: ${clsValue}`);
                        }
                    }
                }
            });

            try {
                clsObserver.observe({ type: 'layout-shift', buffered: true });
                this.observers.set('cls', clsObserver);
            } catch (e) {
                console.warn('CLS observer not supported');
            }
        }
    }

    /**
     * Setup React performance profiling
     */
    setupReactProfiling() {
        // Hook into React DevTools profiler if available
        if (window.React && window.React.Profiler) {
            this.reactProfiler = {
                onRender: (id, phase, actualDuration, baseDuration, startTime, commitTime) => {
                    this.recordMetric('react_render', actualDuration);

                    if (actualDuration > this.thresholds.renderTime) {
                        console.warn(`Slow React render detected: ${id} took ${actualDuration}ms in ${phase} phase`);

                        // Record component-specific metrics
                        this.recordMetric(`react_render_${id}`, actualDuration);
                    }
                }
            };
        }

        // Track Dash re-renders
        window._dashRenderCount = 0;
        window._lastRenderDuration = 0;

        const originalRender = window.ReactDOM?.render;
        if (originalRender) {
            window.ReactDOM.render = (...args) => {
                const startTime = performance.now();
                const result = originalRender.apply(window.ReactDOM, args);
                const duration = performance.now() - startTime;

                window._dashRenderCount++;
                window._lastRenderDuration = duration;

                this.recordMetric('dash_render', duration);
                return result;
            };
        }
    }

    /**
     * Setup memory monitoring
     */
    setupMemoryMonitoring() {
        if (performance.memory) {
            setInterval(() => {
                const memInfo = {
                    used: performance.memory.usedJSHeapSize,
                    total: performance.memory.totalJSHeapSize,
                    limit: performance.memory.jsHeapSizeLimit
                };

                this.recordMetric('memory_used', memInfo.used);
                this.recordMetric('memory_total', memInfo.total);

                if (memInfo.used > this.thresholds.memoryUsage) {
                    console.warn(`High memory usage: ${(memInfo.used / 1024 / 1024).toFixed(1)}MB`);
                }

                // Track memory growth
                if (this.metrics.has('memory_baseline')) {
                    const baseline = this.metrics.get('memory_baseline');
                    const growth = memInfo.used - baseline;
                    if (growth > 50 * 1024 * 1024) { // 50MB growth warning
                        console.warn(`Memory leak potential: ${(growth / 1024 / 1024).toFixed(1)}MB growth`);
                    }
                } else {
                    this.metrics.set('memory_baseline', memInfo.used);
                }
            }, 5000); // Check every 5 seconds
        }
    }

    /**
     * Setup Dash callback monitoring
     */
    setupDashCallbackMonitoring() {
        // Monitor client-side callback performance
        const originalDashClientside = window.dash_clientside;
        if (originalDashClientside) {
            const monitorCallback = (namespace, functionName, originalFn) => {
                return function(...args) {
                    const startTime = performance.now();
                    const result = originalFn.apply(this, args);
                    const duration = performance.now() - startTime;

                    window.performanceMonitor.recordMetric('dash_callback', duration);

                    if (duration > window.performanceMonitor.thresholds.callbackDuration) {
                        console.warn(`Slow Dash callback: ${namespace}.${functionName} took ${duration.toFixed(2)}ms`);
                    }

                    return result;
                };
            };

            // Wrap existing callbacks
            Object.keys(originalDashClientside).forEach(namespace => {
                if (typeof originalDashClientside[namespace] === 'object') {
                    Object.keys(originalDashClientside[namespace]).forEach(functionName => {
                        const originalFn = originalDashClientside[namespace][functionName];
                        if (typeof originalFn === 'function') {
                            originalDashClientside[namespace][functionName] =
                                monitorCallback(namespace, functionName, originalFn);
                        }
                    });
                }
            });
        }
    }

    /**
     * Record a performance metric
     */
    recordMetric(name, value, timestamp = performance.now()) {
        if (!this.metrics.has(name)) {
            this.metrics.set(name, []);
        }

        const metrics = this.metrics.get(name);
        metrics.push({ value, timestamp });

        // Keep only last 100 measurements to prevent memory bloat
        if (metrics.length > 100) {
            metrics.shift();
        }

        // Emit custom event for dashboard updates
        window.dispatchEvent(new CustomEvent('performance-metric', {
            detail: { name, value, timestamp }
        }));
    }

    /**
     * Get performance summary
     */
    getPerformanceSummary() {
        const summary = {
            timestamp: performance.now(),
            metrics: {},
            scores: {},
            warnings: []
        };

        // Calculate averages and scores for each metric
        this.metrics.forEach((measurements, name) => {
            if (measurements.length === 0) return;

            const recent = measurements.slice(-10); // Last 10 measurements
            const avg = recent.reduce((sum, m) => sum + m.value, 0) / recent.length;
            const max = Math.max(...recent.map(m => m.value));
            const min = Math.min(...recent.map(m => m.value));

            summary.metrics[name] = { avg, max, min, count: measurements.length };

            // Calculate scores (0-100)
            let score = 100;
            switch (name) {
                case 'lcp':
                    score = Math.max(0, 100 - (avg - 1000) / 20); // Good < 2.5s
                    break;
                case 'fid':
                    score = Math.max(0, 100 - avg); // Good < 100ms
                    break;
                case 'cls':
                    score = Math.max(0, 100 - avg * 1000); // Good < 0.1
                    break;
                case 'react_render':
                case 'dash_render':
                    score = Math.max(0, 100 - (avg - this.thresholds.renderTime) * 2);
                    break;
                case 'dash_callback':
                    score = Math.max(0, 100 - (avg - 10) / 2); // Good < 50ms
                    break;
                case 'memory_used':
                    const memMB = avg / 1024 / 1024;
                    score = Math.max(0, 100 - (memMB - 50) / 2); // Good < 100MB
                    break;
            }

            summary.scores[name] = Math.round(score);

            // Generate warnings
            if (score < 70) {
                summary.warnings.push(`${name}: Performance below threshold (Score: ${Math.round(score)})`);
            }
        });

        // Overall performance score
        const scoreValues = Object.values(summary.scores);
        summary.overall_score = scoreValues.length > 0
            ? Math.round(scoreValues.reduce((sum, score) => sum + score, 0) / scoreValues.length)
            : 100;

        return summary;
    }

    /**
     * Start continuous monitoring
     */
    startMonitoring() {
        // Performance summary every 30 seconds
        setInterval(() => {
            const summary = this.getPerformanceSummary();
            console.log('Performance Summary:', summary);

            // Store in sessionStorage for debugging
            try {
                sessionStorage.setItem('meld_performance_summary', JSON.stringify(summary));
            } catch (e) {
                // Ignore storage errors
            }

            // Send to analytics if available
            if (window.gtag) {
                window.gtag('event', 'performance_summary', {
                    overall_score: summary.overall_score,
                    warning_count: summary.warnings.length
                });
            }
        }, 30000);

        console.log('Performance monitoring started');
    }

    /**
     * Cleanup observers
     */
    cleanup() {
        this.observers.forEach(observer => observer.disconnect());
        this.observers.clear();
        this.metrics.clear();
    }
}

// Initialize performance monitoring
window.addEventListener('DOMContentLoaded', () => {
    window.performanceMonitor = new PerformanceMonitor();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (window.performanceMonitor) {
        window.performanceMonitor.cleanup();
    }
});

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PerformanceMonitor;
}
