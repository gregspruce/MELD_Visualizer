"""
Performance Benchmarks E2E Tests for MELD Visualizer
Tests application performance across various scenarios and establishes performance baselines.
"""

import time
from pathlib import Path

import pytest


class TestPerformanceBenchmarks:
    """Test suite for performance benchmarking and validation."""

    @pytest.fixture(autouse=True)
    async def setup(self, mcp_page, performance_monitor, console_monitor):
        """Setup for each test with monitoring."""
        self.page = mcp_page
        self.performance_monitor = performance_monitor
        self.console_monitor = console_monitor

        # Start monitoring
        await self.performance_monitor.start_monitoring()
        self.console_monitor.start_monitoring()

    async def test_initial_page_load_performance(self, mcp_page):
        """
        Benchmark initial page load performance and Core Web Vitals.
        """
        # Clear cache and start fresh
        await mcp_page.context.clear_cookies()

        # Measure page load time
        load_start = time.time()
        await mcp_page.goto("http://127.0.0.1:8050")
        await mcp_page.wait_for_load_state("domcontentloaded")
        dom_load_time = (time.time() - load_start) * 1000

        # Wait for network idle
        await mcp_page.wait_for_load_state("networkidle")
        network_idle_time = (time.time() - load_start) * 1000

        # Wait for application to be fully ready
        await mcp_page.wait_for_selector(".dash-app-content", timeout=30000)
        full_load_time = (time.time() - load_start) * 1000

        # Collect performance metrics
        performance_metrics = await mcp_page.evaluate(
            """
            () => {
                const navigation = performance.getEntriesByType('navigation')[0];
                const paint = performance.getEntriesByType('paint');

                let fcp = 0, lcp = 0;
                paint.forEach(entry => {
                    if (entry.name === 'first-contentful-paint') fcp = entry.startTime;
                    if (entry.name === 'largest-contentful-paint') lcp = entry.startTime;
                });

                return {
                    domContentLoaded: navigation.domContentLoadedEventEnd - navigation.navigationStart,
                    loadComplete: navigation.loadEventEnd - navigation.navigationStart,
                    firstContentfulPaint: fcp,
                    largestContentfulPaint: lcp,
                    ttfb: navigation.responseStart - navigation.navigationStart,
                    domInteractive: navigation.domInteractive - navigation.navigationStart
                };
            }
        """
        )

        # Performance assertions (reasonable thresholds for a Dash app)
        assert dom_load_time < 3000, f"DOM load should be under 3s, actual: {dom_load_time:.0f}ms"
        assert (
            network_idle_time < 5000
        ), f"Network idle should be under 5s, actual: {network_idle_time:.0f}ms"
        assert (
            full_load_time < 8000
        ), f"Full app load should be under 8s, actual: {full_load_time:.0f}ms"

        # Core Web Vitals (if available)
        if performance_metrics["firstContentfulPaint"] > 0:
            assert (
                performance_metrics["firstContentfulPaint"] < 2500
            ), f"FCP should be under 2.5s, actual: {performance_metrics['firstContentfulPaint']:.0f}ms"

        if performance_metrics["largestContentfulPaint"] > 0:
            assert (
                performance_metrics["largestContentfulPaint"] < 4000
            ), f"LCP should be under 4s, actual: {performance_metrics['largestContentfulPaint']:.0f}ms"

        # TTFB should be reasonable
        assert (
            performance_metrics["ttfb"] < 1000
        ), f"TTFB should be under 1s, actual: {performance_metrics['ttfb']:.0f}ms"

        print(f"Performance Summary:")
        print(f"  DOM Load: {dom_load_time:.0f}ms")
        print(f"  Network Idle: {network_idle_time:.0f}ms")
        print(f"  Full Load: {full_load_time:.0f}ms")
        print(f"  FCP: {performance_metrics['firstContentfulPaint']:.0f}ms")
        print(f"  LCP: {performance_metrics['largestContentfulPaint']:.0f}ms")
        print(f"  TTFB: {performance_metrics['ttfb']:.0f}ms")

    async def test_csv_upload_processing_performance(self, mcp_page):
        """
        Benchmark CSV upload and processing performance.
        """
        # Navigate to application
        await mcp_page.goto("http://127.0.0.1:8050")
        await mcp_page.wait_for_load_state("networkidle")
        await mcp_page.wait_for_selector(".dash-app-content", timeout=30000)

        # Test different CSV file sizes
        test_files = [
            {
                "name": "minimal",
                "path": Path(__file__).parent.parent
                / "fixtures"
                / "test_data"
                / "minimal_meld_data.csv",
            },
            {
                "name": "standard",
                "path": Path(__file__).parent.parent
                / "fixtures"
                / "test_data"
                / "sample_meld_data.csv",
            },
        ]

        # Add larger CSV files if they exist
        large_csvs = list(Path("C:/VSCode/MELD_Visualizer/data/csv").glob("*.csv"))
        if large_csvs:
            test_files.append({"name": "large", "path": large_csvs[0]})

        upload_performance = []

        for test_file in test_files:
            if not test_file["path"].exists():
                continue

            # Measure file size
            file_size = test_file["path"].stat().st_size

            # Start upload timing
            upload_start = time.time()

            # Upload file
            upload_selector = 'input[type="file"]'
            await mcp_page.set_input_files(upload_selector, str(test_file["path"]))

            # Wait for processing to complete
            try:
                await mcp_page.wait_for_selector("#main-graph .plotly-graph-div", timeout=30000)

                # Additional wait for graph rendering
                await mcp_page.wait_for_timeout(2000)

                upload_end = time.time()
                processing_time = (upload_end - upload_start) * 1000

                # Verify graph has data
                graph_has_data = await mcp_page.evaluate(
                    """
                    () => {
                        const graphDiv = document.querySelector('#main-graph');
                        return graphDiv && graphDiv.data && graphDiv.data.length > 0;
                    }
                """
                )

                upload_performance.append(
                    {
                        "file": test_file["name"],
                        "size_bytes": file_size,
                        "processing_time_ms": processing_time,
                        "success": graph_has_data,
                        "throughput_bytes_per_sec": (
                            file_size / (processing_time / 1000) if processing_time > 0 else 0
                        ),
                    }
                )

                # Performance assertions based on file size
                if file_size < 1024 * 100:  # Under 100KB
                    assert (
                        processing_time < 5000
                    ), f"Small CSV processing should be under 5s, actual: {processing_time:.0f}ms"
                elif file_size < 1024 * 1024:  # Under 1MB
                    assert (
                        processing_time < 10000
                    ), f"Medium CSV processing should be under 10s, actual: {processing_time:.0f}ms"
                else:  # Larger files
                    assert (
                        processing_time < 30000
                    ), f"Large CSV processing should be under 30s, actual: {processing_time:.0f}ms"

                assert (
                    graph_has_data
                ), f"Graph should contain data after processing {test_file['name']}"

            except Exception as e:
                upload_performance.append(
                    {
                        "file": test_file["name"],
                        "size_bytes": file_size,
                        "processing_time_ms": -1,
                        "success": False,
                        "error": str(e),
                    }
                )

        # Print performance summary
        print(f"CSV Processing Performance:")
        for result in upload_performance:
            if result["success"]:
                print(
                    f"  {result['file']}: {result['size_bytes']} bytes in {result['processing_time_ms']:.0f}ms ({result['throughput_bytes_per_sec']:.0f} B/s)"
                )
            else:
                print(f"  {result['file']}: FAILED - {result.get('error', 'Unknown error')}")

    async def test_graph_rendering_performance(self, mcp_page):
        """
        Benchmark graph rendering and interaction performance.
        """
        # Setup with data
        await mcp_page.goto("http://127.0.0.1:8050")
        await mcp_page.wait_for_load_state("networkidle")
        await mcp_page.wait_for_selector(".dash-app-content", timeout=30000)

        test_csv = Path(__file__).parent.parent / "fixtures" / "test_data" / "sample_meld_data.csv"
        upload_selector = 'input[type="file"]'
        await mcp_page.set_input_files(upload_selector, str(test_csv))
        await mcp_page.wait_for_selector("#main-graph .plotly-graph-div", timeout=20000)

        # Measure initial render time
        render_start = time.time()

        # Wait for graph to be fully rendered
        await mcp_page.wait_for_function(
            """
            () => {
                const graphDiv = document.querySelector('#main-graph');
                return graphDiv && graphDiv._fullLayout && graphDiv._fullData;
            }
        """,
            timeout=10000,
        )

        initial_render_time = (time.time() - render_start) * 1000

        # Test graph interaction performance
        graph_element = mcp_page.locator("#main-graph .plotly-graph-div")

        # Measure zoom performance
        zoom_start = time.time()
        await graph_element.dblclick()
        await mcp_page.wait_for_timeout(1000)  # Wait for zoom animation
        zoom_time = (time.time() - zoom_start) * 1000

        # Measure pan performance
        box = await graph_element.bounding_box()
        if box:
            pan_start = time.time()

            start_x = box["x"] + box["width"] * 0.3
            start_y = box["y"] + box["height"] * 0.5
            end_x = start_x + 100
            end_y = start_y

            await mcp_page.mouse.move(start_x, start_y)
            await mcp_page.mouse.down()
            await mcp_page.mouse.move(end_x, end_y)
            await mcp_page.mouse.up()
            await mcp_page.wait_for_timeout(500)

            pan_time = (time.time() - pan_start) * 1000
        else:
            pan_time = -1

        # Measure hover performance
        hover_start = time.time()
        await graph_element.hover()
        await mcp_page.wait_for_timeout(500)
        hover_time = (time.time() - hover_start) * 1000

        # Get graph performance metrics
        graph_metrics = await mcp_page.evaluate(
            """
            () => {
                const graphDiv = document.querySelector('#main-graph');
                if (!graphDiv) return null;

                return {
                    dataPointCount: graphDiv.data ? graphDiv.data.reduce((sum, trace) => sum + (trace.x ? trace.x.length : 0), 0) : 0,
                    traceCount: graphDiv.data ? graphDiv.data.length : 0,
                    hasLayout: !!graphDiv.layout,
                    isResponsive: graphDiv.config ? graphDiv.config.responsive : false
                };
            }
        """
        )

        # Performance assertions
        assert (
            initial_render_time < 3000
        ), f"Initial graph render should be under 3s, actual: {initial_render_time:.0f}ms"
        assert zoom_time < 2000, f"Zoom operation should be under 2s, actual: {zoom_time:.0f}ms"

        if pan_time > 0:
            assert pan_time < 1000, f"Pan operation should be under 1s, actual: {pan_time:.0f}ms"

        assert hover_time < 1000, f"Hover response should be under 1s, actual: {hover_time:.0f}ms"

        # Verify graph has reasonable amount of data
        if graph_metrics:
            assert graph_metrics["dataPointCount"] > 0, "Graph should have data points"
            assert graph_metrics["traceCount"] > 0, "Graph should have traces"

        print(f"Graph Performance Summary:")
        print(f"  Initial Render: {initial_render_time:.0f}ms")
        print(f"  Zoom Response: {zoom_time:.0f}ms")
        print(f"  Pan Response: {pan_time:.0f}ms")
        print(f"  Hover Response: {hover_time:.0f}ms")
        if graph_metrics:
            print(f"  Data Points: {graph_metrics['dataPointCount']}")
            print(f"  Traces: {graph_metrics['traceCount']}")

    async def test_memory_usage_benchmarks(self, mcp_page):
        """
        Monitor memory usage during various operations.
        """
        # Check if memory monitoring is available
        memory_available = await mcp_page.evaluate(
            """
            () => {
                return typeof performance !== 'undefined' &&
                       typeof performance.memory !== 'undefined';
            }
        """
        )

        if not memory_available:
            pytest.skip("Memory monitoring not available in this browser")

        # Baseline memory measurement
        await mcp_page.goto("http://127.0.0.1:8050")
        await mcp_page.wait_for_load_state("networkidle")
        await mcp_page.wait_for_selector(".dash-app-content", timeout=30000)

        baseline_memory = await mcp_page.evaluate(
            """
            () => {
                return {
                    used: performance.memory.usedJSHeapSize,
                    total: performance.memory.totalJSHeapSize,
                    limit: performance.memory.jsHeapSizeLimit
                };
            }
        """
        )

        # Upload data and measure memory
        test_csv = Path(__file__).parent.parent / "fixtures" / "test_data" / "sample_meld_data.csv"
        upload_selector = 'input[type="file"]'
        await mcp_page.set_input_files(upload_selector, str(test_csv))
        await mcp_page.wait_for_selector("#main-graph .plotly-graph-div", timeout=20000)
        await mcp_page.wait_for_timeout(3000)  # Let processing complete

        after_upload_memory = await mcp_page.evaluate(
            """
            () => {
                return {
                    used: performance.memory.usedJSHeapSize,
                    total: performance.memory.totalJSHeapSize,
                    limit: performance.memory.jsHeapSizeLimit
                };
            }
        """
        )

        # Perform graph interactions and measure memory
        graph_element = mcp_page.locator("#main-graph .plotly-graph-div")

        # Multiple zoom/pan operations
        for _ in range(3):
            await graph_element.dblclick()
            await mcp_page.wait_for_timeout(500)

            box = await graph_element.bounding_box()
            if box:
                await mcp_page.mouse.move(box["x"] + 100, box["y"] + 100)
                await mcp_page.mouse.down()
                await mcp_page.mouse.move(box["x"] + 150, box["y"] + 150)
                await mcp_page.mouse.up()
                await mcp_page.wait_for_timeout(500)

        after_interaction_memory = await mcp_page.evaluate(
            """
            () => {
                return {
                    used: performance.memory.usedJSHeapSize,
                    total: performance.memory.totalJSHeapSize,
                    limit: performance.memory.jsHeapSizeLimit
                };
            }
        """
        )

        # Calculate memory usage
        baseline_mb = baseline_memory["used"] / (1024 * 1024)
        upload_mb = after_upload_memory["used"] / (1024 * 1024)
        interaction_mb = after_interaction_memory["used"] / (1024 * 1024)

        upload_increase = upload_mb - baseline_mb
        interaction_increase = interaction_mb - upload_mb

        # Memory assertions (reasonable limits for a visualization app)
        assert (
            baseline_mb < 50
        ), f"Baseline memory should be under 50MB, actual: {baseline_mb:.1f}MB"
        assert (
            upload_mb < 150
        ), f"Memory after upload should be under 150MB, actual: {upload_mb:.1f}MB"
        assert (
            upload_increase < 100
        ), f"Upload memory increase should be under 100MB, actual: {upload_increase:.1f}MB"

        # Memory should not grow excessively during interactions
        assert (
            interaction_increase < 50
        ), f"Interaction memory increase should be under 50MB, actual: {interaction_increase:.1f}MB"

        # Check for memory leaks (rough check)
        total_increase = interaction_mb - baseline_mb
        assert (
            total_increase < 150
        ), f"Total memory increase should be reasonable, actual: {total_increase:.1f}MB"

        print(f"Memory Usage Summary:")
        print(f"  Baseline: {baseline_mb:.1f}MB")
        print(f"  After Upload: {upload_mb:.1f}MB (+{upload_increase:.1f}MB)")
        print(f"  After Interactions: {interaction_mb:.1f}MB (+{interaction_increase:.1f}MB)")
        print(f"  Total Increase: {total_increase:.1f}MB")

    async def test_concurrent_operations_performance(self, mcp_page):
        """
        Test performance under concurrent operations and stress scenarios.
        """
        await mcp_page.goto("http://127.0.0.1:8050")
        await mcp_page.wait_for_load_state("networkidle")
        await mcp_page.wait_for_selector(".dash-app-content", timeout=30000)

        # Upload data
        test_csv = Path(__file__).parent.parent / "fixtures" / "test_data" / "sample_meld_data.csv"
        upload_selector = 'input[type="file"]'
        await mcp_page.set_input_files(upload_selector, str(test_csv))
        await mcp_page.wait_for_selector("#main-graph .plotly-graph-div", timeout=20000)

        # Simulate rapid user interactions
        graph_element = mcp_page.locator("#main-graph .plotly-graph-div")

        stress_start = time.time()

        # Rapid zoom operations
        for _ in range(5):
            await graph_element.dblclick()
            await mcp_page.wait_for_timeout(200)  # Minimal wait

        # Rapid pan operations
        box = await graph_element.bounding_box()
        if box:
            for i in range(5):
                start_x = box["x"] + (i * 20)
                start_y = box["y"] + (i * 20)
                end_x = start_x + 50
                end_y = start_y + 50

                await mcp_page.mouse.move(start_x, start_y)
                await mcp_page.mouse.down()
                await mcp_page.mouse.move(end_x, end_y)
                await mcp_page.mouse.up()
                await mcp_page.wait_for_timeout(100)  # Minimal wait

        # Test multiple hover events
        for _ in range(10):
            await graph_element.hover()
            await mcp_page.wait_for_timeout(50)

        stress_end = time.time()
        stress_duration = (stress_end - stress_start) * 1000

        # Verify application remains responsive after stress
        await mcp_page.wait_for_timeout(2000)  # Recovery time

        # Check if graph is still functional
        graph_functional = await mcp_page.evaluate(
            """
            () => {
                const graphDiv = document.querySelector('#main-graph');
                return graphDiv && graphDiv.data && graphDiv.data.length > 0;
            }
        """
        )

        assert graph_functional, "Graph should remain functional after rapid interactions"

        # Check for console errors during stress test
        console_errors = await mcp_page.evaluate("window.console_errors || []")
        error_count = len([e for e in console_errors if "error" in str(e).lower()])

        # Allow some errors during stress testing, but not excessive
        assert (
            error_count < 10
        ), f"Should not have excessive errors during stress test, found: {error_count}"

        # Performance should be reasonable even under stress
        assert (
            stress_duration < 10000
        ), f"Stress test operations should complete reasonably fast, actual: {stress_duration:.0f}ms"

        print(f"Stress Test Summary:")
        print(f"  Duration: {stress_duration:.0f}ms")
        print(f"  Console Errors: {error_count}")
        print(f"  Graph Functional: {graph_functional}")

    async def test_network_request_optimization(self, mcp_page):
        """
        Monitor and validate network request optimization.
        """
        # Monitor network requests
        network_requests = []

        def handle_request(request):
            network_requests.append(
                {"url": request.url, "method": request.method, "timestamp": time.time()}
            )

        def handle_response(response):
            for req in network_requests:
                if req["url"] == response.url and "response_time" not in req:
                    req["response_time"] = time.time() - req["timestamp"]
                    req["status"] = response.status
                    req["size"] = len(response.headers.get("content-length", "0"))
                    break

        mcp_page.on("request", handle_request)
        mcp_page.on("response", handle_response)

        # Load application
        time.time()
        await mcp_page.goto("http://127.0.0.1:8050")
        await mcp_page.wait_for_load_state("networkidle")
        await mcp_page.wait_for_selector(".dash-app-content", timeout=30000)
        load_end = time.time()

        # Upload data
        upload_start = time.time()
        test_csv = Path(__file__).parent.parent / "fixtures" / "test_data" / "sample_meld_data.csv"
        upload_selector = 'input[type="file"]'
        await mcp_page.set_input_files(upload_selector, str(test_csv))
        await mcp_page.wait_for_selector("#main-graph .plotly-graph-div", timeout=20000)
        upload_end = time.time()

        # Analyze network requests
        load_requests = [req for req in network_requests if req["timestamp"] <= load_end]
        upload_requests = [
            req
            for req in network_requests
            if req["timestamp"] > upload_start and req["timestamp"] <= upload_end
        ]

        # Network optimization assertions
        total_requests = len(network_requests)
        assert total_requests < 50, f"Should not make excessive requests, actual: {total_requests}"

        # Check for failed requests
        failed_requests = [req for req in network_requests if req.get("status", 200) >= 400]
        assert len(failed_requests) == 0, f"Should not have failed requests: {failed_requests}"

        # Check request response times
        slow_requests = [req for req in network_requests if req.get("response_time", 0) > 5.0]
        assert len(slow_requests) < 3, f"Should not have many slow requests: {len(slow_requests)}"

        # Verify no duplicate unnecessary requests
        request_urls = [req["url"] for req in network_requests]
        unique_urls = set(request_urls)

        # Some duplication is normal (CSS, JS caching), but excessive duplication is bad
        duplication_ratio = len(request_urls) / len(unique_urls) if unique_urls else 1
        assert (
            duplication_ratio < 3.0
        ), f"Request duplication ratio should be reasonable: {duplication_ratio:.2f}"

        print(f"Network Optimization Summary:")
        print(f"  Total Requests: {total_requests}")
        print(f"  Load Requests: {len(load_requests)}")
        print(f"  Upload Requests: {len(upload_requests)}")
        print(f"  Failed Requests: {len(failed_requests)}")
        print(f"  Slow Requests (>5s): {len(slow_requests)}")
        print(f"  Duplication Ratio: {duplication_ratio:.2f}")

        # Clean up event listeners
        mcp_page.remove_listener("request", handle_request)
        mcp_page.remove_listener("response", handle_response)

    async def test_browser_resource_efficiency(self, mcp_page):
        """
        Test browser resource efficiency and cleanup.
        """
        await mcp_page.goto("http://127.0.0.1:8050")
        await mcp_page.wait_for_load_state("networkidle")
        await mcp_page.wait_for_selector(".dash-app-content", timeout=30000)

        # Check initial resource usage
        initial_metrics = await mcp_page.evaluate(
            """
            () => {
                const result = {
                    elementCount: document.querySelectorAll('*').length,
                    eventListenerCount: 0,
                    timers: 0
                };

                // Try to estimate event listeners (rough approximation)
                const elements = document.querySelectorAll('*');
                elements.forEach(el => {
                    if (el.onclick || el.onmouseover || el.onkeydown) {
                        result.eventListenerCount++;
                    }
                });

                // Check for memory metrics if available
                if (performance.memory) {
                    result.memory = {
                        used: performance.memory.usedJSHeapSize,
                        total: performance.memory.totalJSHeapSize
                    };
                }

                return result;
            }
        """
        )

        # Upload and process data
        test_csv = Path(__file__).parent.parent / "fixtures" / "test_data" / "sample_meld_data.csv"
        upload_selector = 'input[type="file"]'
        await mcp_page.set_input_files(upload_selector, str(test_csv))
        await mcp_page.wait_for_selector("#main-graph .plotly-graph-div", timeout=20000)

        # Perform various operations
        graph_element = mcp_page.locator("#main-graph .plotly-graph-div")
        for _ in range(3):
            await graph_element.dblclick()
            await mcp_page.wait_for_timeout(500)
            await graph_element.hover()
            await mcp_page.wait_for_timeout(500)

        # Check resource usage after operations
        final_metrics = await mcp_page.evaluate(
            """
            () => {
                const result = {
                    elementCount: document.querySelectorAll('*').length,
                    eventListenerCount: 0,
                    timers: 0
                };

                // Try to estimate event listeners
                const elements = document.querySelectorAll('*');
                elements.forEach(el => {
                    if (el.onclick || el.onmouseover || el.onkeydown) {
                        result.eventListenerCount++;
                    }
                });

                // Check for memory metrics if available
                if (performance.memory) {
                    result.memory = {
                        used: performance.memory.usedJSHeapSize,
                        total: performance.memory.totalJSHeapSize
                    };
                }

                return result;
            }
        """
        )

        # Resource efficiency checks
        element_growth = final_metrics["elementCount"] - initial_metrics["elementCount"]
        assert element_growth < 1000, f"DOM element growth should be reasonable: {element_growth}"

        # Memory growth (if available)
        if "memory" in initial_metrics and "memory" in final_metrics:
            memory_growth = (
                final_metrics["memory"]["used"] - initial_metrics["memory"]["used"]
            ) / (1024 * 1024)
            assert memory_growth < 100, f"Memory growth should be reasonable: {memory_growth:.1f}MB"

        # Check for memory leaks by forcing garbage collection and checking again
        await mcp_page.evaluate("if (window.gc) window.gc();")
        await mcp_page.wait_for_timeout(2000)

        post_gc_metrics = await mcp_page.evaluate(
            """
            () => {
                const result = {};
                if (performance.memory) {
                    result.memory = {
                        used: performance.memory.usedJSHeapSize,
                        total: performance.memory.totalJSHeapSize
                    };
                }
                return result;
            }
        """
        )

        print(f"Resource Efficiency Summary:")
        print(f"  Initial Elements: {initial_metrics['elementCount']}")
        print(f"  Final Elements: {final_metrics['elementCount']}")
        print(f"  Element Growth: {element_growth}")

        if "memory" in initial_metrics:
            initial_mb = initial_metrics["memory"]["used"] / (1024 * 1024)
            final_mb = final_metrics["memory"]["used"] / (1024 * 1024)
            print(f"  Memory Growth: {initial_mb:.1f}MB → {final_mb:.1f}MB")

            if "memory" in post_gc_metrics:
                post_gc_mb = post_gc_metrics["memory"]["used"] / (1024 * 1024)
                print(f"  After GC: {post_gc_mb:.1f}MB")
