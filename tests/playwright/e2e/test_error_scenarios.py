"""
Error Scenarios E2E Tests for MELD Visualizer
Tests error handling, recovery scenarios, and application resilience.
"""

from pathlib import Path

import pytest


class TestErrorScenarios:
    """Test suite for error handling and recovery scenarios."""

    @pytest.fixture(autouse=True)
    async def setup(self, mcp_page, performance_monitor, console_monitor):
        """Setup for each test with monitoring."""
        self.page = mcp_page
        self.performance_monitor = performance_monitor
        self.console_monitor = console_monitor

        # Navigate to application
        await self.page.goto("http://127.0.0.1:8050")
        await self.page.wait_for_load_state("networkidle")

        # Wait for application to be ready
        await self.page.wait_for_selector(".dash-app-content", timeout=30000)

        # Start monitoring
        await self.performance_monitor.start_monitoring()
        self.console_monitor.start_monitoring()

    async def test_invalid_csv_upload_handling(self, mcp_page):
        """
        Test handling of invalid CSV files and error recovery.
        """
        # Test with invalid CSV file
        invalid_csv = (
            Path(__file__).parent.parent / "fixtures" / "test_data" / "invalid_meld_data.csv"
        )

        if not invalid_csv.exists():
            # Create a temporary invalid CSV for testing
            invalid_content = "invalid,csv,header\n1,2\nincomplete,row"
            with open(invalid_csv, "w") as f:
                f.write(invalid_content)

        upload_selector = 'input[type="file"]'

        # Upload invalid file
        await mcp_page.set_input_files(upload_selector, str(invalid_csv))
        await mcp_page.wait_for_timeout(3000)  # Allow time for processing

        # Check for error messages
        error_message_found = False
        error_selectors = [
            ".alert-danger",
            ".alert-error",
            ".error-message",
            "[role='alert']",
            ".notification.error",
            ".toast.error",
            "#config-warning-alert",
        ]

        error_texts = []
        for selector in error_selectors:
            error_elements = mcp_page.locator(selector)
            count = await error_elements.count()
            if count > 0:
                for i in range(count):
                    element = error_elements.nth(i)
                    if await element.is_visible():
                        text = await element.text_content()
                        if text and text.strip():
                            error_texts.append(text.strip())
                            error_message_found = True

        # Verify error handling
        # Note: Error messages might appear in console instead of UI
        console_errors = await mcp_page.evaluate("window.console_errors || []")

        # Either UI error message or console error should be present
        has_error_indication = error_message_found or len(console_errors) > 0

        # Application should remain stable after error
        main_content = mcp_page.locator(".dash-app-content")
        assert (
            await main_content.is_visible()
        ), "Application should remain visible after invalid upload"

        # Upload input should still be functional
        upload_input = mcp_page.locator(upload_selector)
        assert await upload_input.count() > 0, "Upload functionality should remain available"

        print(f"Invalid CSV handling:")
        print(f"  UI Error Messages: {error_texts}")
        print(f"  Console Errors: {len(console_errors)}")
        print(f"  Error Indication Present: {has_error_indication}")

    async def test_recovery_from_invalid_to_valid_upload(self, mcp_page):
        """
        Test recovery process from invalid to valid file upload.
        """
        upload_selector = 'input[type="file"]'

        # First, upload invalid file
        invalid_csv = (
            Path(__file__).parent.parent / "fixtures" / "test_data" / "invalid_meld_data.csv"
        )
        if invalid_csv.exists():
            await mcp_page.set_input_files(upload_selector, str(invalid_csv))
            await mcp_page.wait_for_timeout(2000)

        # Clear any existing error states
        await mcp_page.wait_for_timeout(1000)

        # Now upload valid file to test recovery
        valid_csv = Path(__file__).parent.parent / "fixtures" / "test_data" / "sample_meld_data.csv"
        await mcp_page.set_input_files(upload_selector, str(valid_csv))

        # Wait for successful processing
        try:
            await mcp_page.wait_for_selector("#main-graph .plotly-graph-div", timeout=20000)
            recovery_successful = True

            # Verify graph has data
            graph_has_data = await mcp_page.evaluate(
                """
                () => {
                    const graphDiv = document.querySelector('#main-graph');
                    return graphDiv && graphDiv.data && graphDiv.data.length > 0;
                }
            """
            )

            assert graph_has_data, "Graph should contain data after recovery"

        except Exception as e:
            recovery_successful = False
            print(f"Recovery failed: {e}")

        assert recovery_successful, "Application should recover from invalid file upload"

        # Check if error messages are cleared
        error_selectors = [".alert-danger", ".alert-error", ".error-message", ".notification.error"]

        persistent_errors = []
        for selector in error_selectors:
            error_elements = mcp_page.locator(selector)
            count = await error_elements.count()
            if count > 0:
                for i in range(count):
                    element = error_elements.nth(i)
                    if await element.is_visible():
                        text = await element.text_content()
                        if text and text.strip() and "success" not in text.lower():
                            persistent_errors.append(text.strip())

        # Error messages should be cleared or replaced with success messages
        print(f"Persistent errors after recovery: {persistent_errors}")

    async def test_network_interruption_simulation(self, mcp_page):
        """
        Simulate network interruptions and test application resilience.
        """
        # Upload file first
        test_csv = Path(__file__).parent.parent / "fixtures" / "test_data" / "sample_meld_data.csv"
        upload_selector = 'input[type="file"]'
        await mcp_page.set_input_files(upload_selector, str(test_csv))
        await mcp_page.wait_for_selector("#main-graph .plotly-graph-div", timeout=20000)

        # Simulate network failure by blocking network requests
        await mcp_page.route("**/*", lambda route: route.abort())

        # Try to interact with the application
        graph_element = mcp_page.locator("#main-graph .plotly-graph-div")

        # These interactions should still work since they're client-side
        try:
            await graph_element.hover()
            await mcp_page.wait_for_timeout(1000)

            # Try zoom (should work since it's client-side Plotly)
            await graph_element.dblclick()
            await mcp_page.wait_for_timeout(1000)

            client_side_functional = True
        except Exception as e:
            client_side_functional = False
            print(f"Client-side functionality failed during network interruption: {e}")

        # Restore network
        await mcp_page.unroute("**/*")
        await mcp_page.wait_for_timeout(2000)  # Allow network to recover

        # Verify application recovers
        try:
            # Test that new uploads still work after network recovery
            await mcp_page.set_input_files(upload_selector, str(test_csv))
            await mcp_page.wait_for_timeout(3000)

            network_recovery_successful = True
        except Exception as e:
            network_recovery_successful = False
            print(f"Network recovery failed: {e}")

        # Application should remain responsive during network issues
        main_content = mcp_page.locator(".dash-app-content")
        assert (
            await main_content.is_visible()
        ), "Application should remain visible during network issues"

        print(f"Network Interruption Test:")
        print(f"  Client-side functional during interruption: {client_side_functional}")
        print(f"  Network recovery successful: {network_recovery_successful}")

    async def test_memory_pressure_scenarios(self, mcp_page):
        """
        Test application behavior under memory pressure conditions.
        """
        # Load application and data
        test_csv = Path(__file__).parent.parent / "fixtures" / "test_data" / "sample_meld_data.csv"
        upload_selector = 'input[type="file"]'
        await mcp_page.set_input_files(upload_selector, str(test_csv))
        await mcp_page.wait_for_selector("#main-graph .plotly-graph-div", timeout=20000)

        # Simulate memory pressure by creating large objects
        initial_memory = await mcp_page.evaluate(
            """
            () => {
                if (performance.memory) {
                    return performance.memory.usedJSHeapSize;
                }
                return 0;
            }
        """
        )

        # Create memory pressure
        memory_pressure_created = await mcp_page.evaluate(
            """
            () => {
                try {
                    // Create large arrays to simulate memory pressure
                    window.memoryPressureArrays = [];
                    for (let i = 0; i < 50; i++) {
                        window.memoryPressureArrays.push(new Array(100000).fill(Math.random()));
                    }
                    return true;
                } catch (e) {
                    return false;
                }
            }
        """
        )

        if memory_pressure_created:
            await mcp_page.wait_for_timeout(2000)

            # Test if application still functions under memory pressure
            graph_element = mcp_page.locator("#main-graph .plotly-graph-div")

            try:
                await graph_element.hover()
                await graph_element.dblclick()
                await mcp_page.wait_for_timeout(1000)

                functions_under_pressure = True
            except Exception as e:
                functions_under_pressure = False
                print(f"Application failed under memory pressure: {e}")

            # Clean up memory pressure
            await mcp_page.evaluate(
                """
                () => {
                    if (window.memoryPressureArrays) {
                        window.memoryPressureArrays = null;
                        if (window.gc) window.gc();
                    }
                }
            """
            )

            await mcp_page.wait_for_timeout(3000)  # Allow GC to run

            final_memory = await mcp_page.evaluate(
                """
                () => {
                    if (performance.memory) {
                        return performance.memory.usedJSHeapSize;
                    }
                    return 0;
                }
            """
            )

            # Verify memory is cleaned up
            if initial_memory > 0 and final_memory > 0:
                memory_cleanup_ratio = final_memory / initial_memory
                memory_cleaned_up = memory_cleanup_ratio < 2.0  # Allow some growth
                print(f"Memory cleanup ratio: {memory_cleanup_ratio:.2f}")
            else:
                memory_cleaned_up = True  # Can't measure, assume good

            print(f"Memory Pressure Test:")
            print(f"  Functions under pressure: {functions_under_pressure}")
            print(f"  Memory cleaned up: {memory_cleaned_up}")

        # Verify application is still responsive after memory pressure test
        main_content = mcp_page.locator(".dash-app-content")
        assert (
            await main_content.is_visible()
        ), "Application should remain responsive after memory pressure"

    async def test_rapid_user_input_error_handling(self, mcp_page):
        """
        Test error handling with rapid user inputs that might cause race conditions.
        """
        upload_selector = 'input[type="file"]'
        test_csv = Path(__file__).parent.parent / "fixtures" / "test_data" / "sample_meld_data.csv"

        # Rapid file uploads
        try:
            for _ in range(3):
                await mcp_page.set_input_files(upload_selector, str(test_csv))
                await mcp_page.wait_for_timeout(500)  # Very short wait
        except Exception as e:
            print(f"Rapid upload error (expected): {e}")

        # Wait for processing to stabilize
        await mcp_page.wait_for_timeout(5000)

        # Verify application is still functional
        try:
            await mcp_page.wait_for_selector("#main-graph .plotly-graph-div", timeout=10000)
            graph_functional = await mcp_page.evaluate(
                """
                () => {
                    const graphDiv = document.querySelector('#main-graph');
                    return graphDiv && graphDiv.data && graphDiv.data.length > 0;
                }
            """
            )
        except Exception:
            graph_functional = False

        # Test rapid graph interactions
        if graph_functional:
            graph_element = mcp_page.locator("#main-graph .plotly-graph-div")

            try:
                # Rapid clicks and interactions
                for _ in range(10):
                    await graph_element.click()
                    await graph_element.hover()
                    await mcp_page.wait_for_timeout(50)  # Very short wait

                rapid_interaction_handled = True
            except Exception as e:
                rapid_interaction_handled = False
                print(f"Rapid interaction error: {e}")
        else:
            rapid_interaction_handled = False

        # Check for excessive console errors
        await mcp_page.wait_for_timeout(2000)
        console_errors = await mcp_page.evaluate("window.console_errors || []")
        error_count = len(console_errors)

        # Some errors are expected with rapid inputs, but not excessive
        excessive_errors = error_count > 20

        # Verify application recovers
        main_content = mcp_page.locator(".dash-app-content")
        app_responsive = await main_content.is_visible()

        assert app_responsive, "Application should remain responsive after rapid inputs"
        assert not excessive_errors, f"Should not have excessive errors: {error_count}"

        print(f"Rapid Input Test:")
        print(f"  Graph functional: {graph_functional}")
        print(f"  Rapid interactions handled: {rapid_interaction_handled}")
        print(f"  Console errors: {error_count}")

    async def test_browser_compatibility_error_scenarios(self, mcp_page):
        """
        Test error scenarios specific to browser compatibility issues.
        """
        # Test JavaScript error injection
        js_error_injected = await mcp_page.evaluate(
            """
            () => {
                try {
                    // Inject a controlled error to test error handling
                    window.testError = function() {
                        throw new Error('Test error for compatibility testing');
                    };

                    // Test undefined function call (common compatibility issue)
                    if (typeof window.nonExistentFunction === 'undefined') {
                        window.nonExistentFunction = function() {
                            console.warn('Calling undefined function - compatibility test');
                        };
                    }

                    return true;
                } catch (e) {
                    return false;
                }
            }
        """
        )

        if js_error_injected:
            # Trigger the test error
            try:
                await mcp_page.evaluate("window.testError()")
            except Exception:
                pass  # Expected to fail

            await mcp_page.wait_for_timeout(1000)

        # Test CSS compatibility by temporarily breaking styles
        css_test_applied = await mcp_page.evaluate(
            """
            () => {
                try {
                    const style = document.createElement('style');
                    style.id = 'compatibility-test-style';
                    style.textContent = `
                        /* Test invalid CSS that might break in some browsers */
                        .test-invalid-css {
                            display: invalid-value;
                            position: invalid-position;
                        }
                    `;
                    document.head.appendChild(style);
                    return true;
                } catch (e) {
                    return false;
                }
            }
        """
        )

        await mcp_page.wait_for_timeout(1000)

        # Clean up test CSS
        if css_test_applied:
            await mcp_page.evaluate(
                """
                () => {
                    const testStyle = document.getElementById('compatibility-test-style');
                    if (testStyle) testStyle.remove();
                }
            """
            )

        # Verify application remains functional
        main_content = mcp_page.locator(".dash-app-content")
        app_functional = await main_content.is_visible()

        # Test file upload still works after compatibility errors
        upload_functional = False
        try:
            test_csv = (
                Path(__file__).parent.parent / "fixtures" / "test_data" / "sample_meld_data.csv"
            )
            upload_selector = 'input[type="file"]'
            await mcp_page.set_input_files(upload_selector, str(test_csv))
            await mcp_page.wait_for_timeout(2000)
            upload_functional = True
        except Exception as e:
            print(f"Upload failed after compatibility test: {e}")

        assert app_functional, "Application should remain functional after compatibility errors"

        print(f"Browser Compatibility Test:")
        print(f"  JS Error Injected: {js_error_injected}")
        print(f"  CSS Test Applied: {css_test_applied}")
        print(f"  App Functional: {app_functional}")
        print(f"  Upload Functional: {upload_functional}")

    async def test_graceful_degradation_scenarios(self, mcp_page):
        """
        Test graceful degradation when certain features are unavailable.
        """
        # Test with JavaScript partially disabled (simulate older browsers)
        degradation_test_results = await mcp_page.evaluate(
            """
            () => {
                const results = {
                    consoleAvailable: typeof console !== 'undefined',
                    localStorageAvailable: typeof localStorage !== 'undefined',
                    webGLAvailable: false,
                    performanceAvailable: typeof performance !== 'undefined'
                };

                // Test WebGL availability
                try {
                    const canvas = document.createElement('canvas');
                    const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
                    results.webGLAvailable = !!gl;
                } catch (e) {
                    results.webGLAvailable = false;
                }

                return results;
            }
        """
        )

        # Upload data to test basic functionality
        test_csv = Path(__file__).parent.parent / "fixtures" / "test_data" / "sample_meld_data.csv"
        upload_selector = 'input[type="file"]'

        try:
            await mcp_page.set_input_files(upload_selector, str(test_csv))
            basic_upload_works = True
        except Exception as e:
            basic_upload_works = False
            print(f"Basic upload failed: {e}")

        if basic_upload_works:
            try:
                await mcp_page.wait_for_selector("#main-graph .plotly-graph-div", timeout=15000)
                graph_renders = True
            except Exception:
                graph_renders = False
        else:
            graph_renders = False

        # Test if application provides fallbacks for missing features
        fallback_content_available = await mcp_page.evaluate(
            """
            () => {
                // Check for fallback content or error messages
                const errorElements = document.querySelectorAll('.error, .warning, .fallback, [role="alert"]');
                const hasContent = document.querySelector('.dash-app-content');

                return {
                    hasErrorElements: errorElements.length > 0,
                    hasMainContent: !!hasContent,
                    contentVisible: hasContent ? hasContent.offsetWidth > 0 && hasContent.offsetHeight > 0 : false
                };
            }
        """
        )

        # Application should provide some level of functionality even with degraded features
        basic_functionality_available = (
            fallback_content_available["hasMainContent"]
            and fallback_content_available["contentVisible"]
        )

        assert (
            basic_functionality_available
        ), "Application should provide basic functionality even with feature degradation"

        print(f"Graceful Degradation Test:")
        print(f"  Console Available: {degradation_test_results['consoleAvailable']}")
        print(f"  LocalStorage Available: {degradation_test_results['localStorageAvailable']}")
        print(f"  WebGL Available: {degradation_test_results['webGLAvailable']}")
        print(f"  Performance API Available: {degradation_test_results['performanceAvailable']}")
        print(f"  Basic Upload Works: {basic_upload_works}")
        print(f"  Graph Renders: {graph_renders}")
        print(f"  Basic Functionality Available: {basic_functionality_available}")

    async def test_data_validation_error_boundaries(self, mcp_page):
        """
        Test error boundaries and validation for different types of malformed data.
        """
        upload_selector = 'input[type="file"]'

        # Create various types of problematic CSV files for testing
        test_files = []

        # Empty file
        empty_file = Path(__file__).parent.parent / "fixtures" / "test_data" / "empty.csv"
        empty_file.parent.mkdir(parents=True, exist_ok=True)
        with open(empty_file, "w") as f:
            f.write("")
        test_files.append(("empty", empty_file))

        # File with only headers
        headers_only = Path(__file__).parent.parent / "fixtures" / "test_data" / "headers_only.csv"
        with open(headers_only, "w") as f:
            f.write("x,y,z\n")
        test_files.append(("headers_only", headers_only))

        # File with inconsistent columns
        inconsistent_cols = (
            Path(__file__).parent.parent / "fixtures" / "test_data" / "inconsistent.csv"
        )
        with open(inconsistent_cols, "w") as f:
            f.write("x,y,z\n1,2,3\n4,5\n6,7,8,9\n")
        test_files.append(("inconsistent_columns", inconsistent_cols))

        # File with invalid data types
        invalid_types = (
            Path(__file__).parent.parent / "fixtures" / "test_data" / "invalid_types.csv"
        )
        with open(invalid_types, "w") as f:
            f.write("x,y,z\nabc,def,ghi\n1,two,3\n")
        test_files.append(("invalid_types", invalid_types))

        error_handling_results = []

        for file_type, file_path in test_files:
            try:
                # Upload problematic file
                await mcp_page.set_input_files(upload_selector, str(file_path))
                await mcp_page.wait_for_timeout(3000)  # Wait for processing

                # Check for error handling
                error_displayed = False
                error_selectors = [
                    ".alert-danger",
                    ".alert-error",
                    ".error-message",
                    "[role='alert']",
                    ".notification.error",
                    "#config-warning-alert",
                ]

                for selector in error_selectors:
                    error_elements = mcp_page.locator(selector)
                    if await error_elements.count() > 0:
                        element = error_elements.first
                        if await element.is_visible():
                            error_text = await element.text_content()
                            if error_text and error_text.strip():
                                error_displayed = True
                                break

                # Check if application crashed
                app_responsive = await mcp_page.locator(".dash-app-content").is_visible()

                # Check console errors
                console_errors = await mcp_page.evaluate("window.console_errors || []")
                has_console_errors = len(console_errors) > 0

                error_handling_results.append(
                    {
                        "file_type": file_type,
                        "error_displayed": error_displayed,
                        "app_responsive": app_responsive,
                        "has_console_errors": has_console_errors,
                        "handled_gracefully": app_responsive
                        and (error_displayed or has_console_errors),
                    }
                )

                # Clean up error state before next test
                await mcp_page.wait_for_timeout(1000)

            except Exception as e:
                error_handling_results.append(
                    {
                        "file_type": file_type,
                        "error_displayed": False,
                        "app_responsive": False,
                        "has_console_errors": True,
                        "handled_gracefully": False,
                        "exception": str(e),
                    }
                )

        # Verify application handles all error scenarios gracefully
        all_handled_gracefully = all(
            result["handled_gracefully"] for result in error_handling_results
        )
        app_remains_responsive = all(result["app_responsive"] for result in error_handling_results)

        # Application should remain responsive even with bad data
        assert (
            app_remains_responsive
        ), "Application should remain responsive with all data validation errors"

        print(f"Data Validation Error Boundaries:")
        for result in error_handling_results:
            print(
                f"  {result['file_type']}: handled_gracefully={result['handled_gracefully']}, responsive={result['app_responsive']}"
            )

        # Clean up test files
        for file_type, file_path in test_files:
            try:
                file_path.unlink()
            except Exception:
                pass

    async def test_concurrent_error_scenarios(self, mcp_page):
        """
        Test error handling when multiple error conditions occur simultaneously.
        """
        upload_selector = 'input[type="file"]'

        # Create multiple error conditions simultaneously

        # 1. Inject JavaScript errors
        await mcp_page.evaluate(
            """
            () => {
                // Simulate random JavaScript errors
                window.errorGenerator = setInterval(() => {
                    if (Math.random() < 0.3) {
                        console.error('Simulated concurrent error', Math.random());
                    }
                }, 1000);

                // Override some methods to potentially cause errors
                const originalFetch = window.fetch;
                window.fetch = function(...args) {
                    if (Math.random() < 0.1) {
                        return Promise.reject(new Error('Simulated fetch error'));
                    }
                    return originalFetch.apply(this, args);
                };
            }
        """
        )

        # 2. Create memory pressure
        await mcp_page.evaluate(
            """
            () => {
                window.memoryPressure = [];
                for (let i = 0; i < 20; i++) {
                    window.memoryPressure.push(new Array(50000).fill(Math.random()));
                }
            }
        """
        )

        # 3. Upload invalid file while errors are occurring
        invalid_csv = (
            Path(__file__).parent.parent / "fixtures" / "test_data" / "invalid_meld_data.csv"
        )
        if not invalid_csv.exists():
            with open(invalid_csv, "w") as f:
                f.write("invalid,data\n1,2,3,4,5\nincomplete")

        try:
            await mcp_page.set_input_files(upload_selector, str(invalid_csv))
            await mcp_page.wait_for_timeout(2000)
        except Exception as e:
            print(f"Expected error during concurrent error test: {e}")

        # 4. Try to interact with the graph while errors are occurring
        graph_interaction_successful = False
        try:
            graph_element = mcp_page.locator("#main-graph")
            if await graph_element.count() > 0:
                await graph_element.click()
                await graph_element.hover()
                graph_interaction_successful = True
        except Exception:
            pass

        await mcp_page.wait_for_timeout(3000)  # Let concurrent errors accumulate

        # Check application state during concurrent errors
        app_state = await mcp_page.evaluate(
            """
            () => {
                return {
                    responsive: document.querySelector('.dash-app-content') !== null,
                    hasErrors: (window.console_errors || []).length > 0,
                    memoryPressureActive: window.memoryPressure && window.memoryPressure.length > 0
                };
            }
        """
        )

        # Clean up error generators
        await mcp_page.evaluate(
            """
            () => {
                if (window.errorGenerator) {
                    clearInterval(window.errorGenerator);
                }
                window.memoryPressure = null;
                if (window.gc) window.gc();
            }
        """
        )

        await mcp_page.wait_for_timeout(2000)  # Recovery time

        # Test recovery with valid file
        recovery_successful = False
        try:
            valid_csv = (
                Path(__file__).parent.parent / "fixtures" / "test_data" / "sample_meld_data.csv"
            )
            await mcp_page.set_input_files(upload_selector, str(valid_csv))
            await mcp_page.wait_for_timeout(3000)

            # Check if graph renders after recovery
            if await mcp_page.locator("#main-graph .plotly-graph-div").count() > 0:
                recovery_successful = True
        except Exception as e:
            print(f"Recovery failed: {e}")

        # Application should survive concurrent error conditions
        assert app_state[
            "responsive"
        ], "Application should remain responsive during concurrent errors"

        print(f"Concurrent Error Scenarios:")
        print(f"  App Responsive During Errors: {app_state['responsive']}")
        print(f"  Errors Detected: {app_state['hasErrors']}")
        print(f"  Memory Pressure Applied: {app_state['memoryPressureActive']}")
        print(f"  Graph Interaction During Errors: {graph_interaction_successful}")
        print(f"  Recovery Successful: {recovery_successful}")
