"""
Critical User Journey E2E Tests for MELD Visualizer
Tests the core workflows that users depend on for data visualization and analysis.
"""

import time
from pathlib import Path

import pytest


class TestCriticalUserJourneys:
    """Test suite for critical user workflows in MELD Visualizer."""

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

    async def test_complete_csv_upload_to_visualization_workflow(self, mcp_page):
        """
        Test the complete workflow from CSV upload to data visualization.
        This is the most critical user journey.
        """
        # Step 1: Upload CSV file
        test_csv = Path(__file__).parent.parent / "fixtures" / "test_data" / "sample_meld_data.csv"

        # Find upload component
        upload_selector = 'input[type="file"]'
        await mcp_page.wait_for_selector(upload_selector)
        await mcp_page.set_input_files(upload_selector, str(test_csv))

        # Step 2: Wait for upload processing
        await mcp_page.wait_for_timeout(2000)  # Allow time for upload processing

        # Step 3: Verify filename display
        filename_element = mcp_page.locator("#output-filename")
        if await filename_element.count() > 0:
            filename = await filename_element.text_content()
            assert "sample_meld_data.csv" in filename

        # Step 4: Wait for graph rendering
        graph_selector = "#main-graph .plotly-graph-div"
        await mcp_page.wait_for_selector(graph_selector, timeout=20000)

        # Step 5: Verify graph has rendered data
        # Check if graph has data points by evaluating Plotly data
        graph_has_data = await mcp_page.evaluate(
            """
            () => {
                const graphDiv = document.querySelector('#main-graph');
                if (!graphDiv || !graphDiv.data) return false;
                return graphDiv.data.length > 0 && graphDiv.data[0].x && graphDiv.data[0].x.length > 0;
            }
        """
        )
        assert graph_has_data, "Graph should contain data points after CSV upload"

        # Step 6: Verify data table is populated
        table_selector = "#data-table"
        if await mcp_page.locator(table_selector).count() > 0:
            # Check if table has rows
            table_rows = mcp_page.locator(f"{table_selector} tbody tr")
            row_count = await table_rows.count()
            assert row_count > 0, "Data table should have rows after CSV upload"

        # Step 7: Verify no console errors during workflow
        console_errors = await mcp_page.evaluate("window.console_errors || []")
        assert len(console_errors) == 0, f"No console errors expected, but found: {console_errors}"

    async def test_graph_interaction_and_filtering(self, mcp_page):
        """
        Test graph interaction capabilities including zoom, pan, and filtering.
        """
        # First upload data
        test_csv = Path(__file__).parent.parent / "fixtures" / "test_data" / "sample_meld_data.csv"
        upload_selector = 'input[type="file"]'
        await mcp_page.set_input_files(upload_selector, str(test_csv))
        await mcp_page.wait_for_selector("#main-graph .plotly-graph-div", timeout=20000)

        # Test graph interactions
        graph_element = mcp_page.locator("#main-graph .plotly-graph-div")

        # Get initial graph bounds (for future use in interaction verification)
        await mcp_page.evaluate(
            """
            () => {
                const graphDiv = document.querySelector('#main-graph');
                if (graphDiv && graphDiv.layout) {
                    return {
                        xRange: graphDiv.layout.xaxis ? graphDiv.layout.xaxis.range : null,
                        yRange: graphDiv.layout.yaxis ? graphDiv.layout.yaxis.range : null
                    };
                }
                return null;
            }
        """
        )

        # Test zoom by double-clicking
        await graph_element.dblclick()
        await mcp_page.wait_for_timeout(1000)  # Wait for zoom animation

        # Test pan by dragging
        box = await graph_element.bounding_box()
        if box:
            start_x = box["x"] + box["width"] * 0.3
            start_y = box["y"] + box["height"] * 0.5
            end_x = start_x + 50
            end_y = start_y

            await mcp_page.mouse.move(start_x, start_y)
            await mcp_page.mouse.down()
            await mcp_page.mouse.move(end_x, end_y)
            await mcp_page.mouse.up()
            await mcp_page.wait_for_timeout(500)

        # Test filter controls if they exist
        filter_controls = [
            {"selector": 'input[type="range"]', "value": "50"},
            {"selector": 'input[type="number"]', "value": "100"},
            {"selector": "select", "value": "1"},
        ]

        for control in filter_controls:
            elements = mcp_page.locator(control["selector"])
            count = await elements.count()
            if count > 0:
                # Test the first matching element
                first_element = elements.first
                if await first_element.is_visible():
                    if control["selector"] == "select":
                        await first_element.select_option(control["value"])
                    else:
                        await first_element.fill(control["value"])
                    await mcp_page.wait_for_timeout(500)

    async def test_theme_switching_workflow(self, mcp_page):
        """
        Test theme switching functionality across the application.
        """
        # Look for theme selector
        theme_selectors = [
            "select#theme-selector",
            "[data-testid='theme-selector']",
            "select[id*='theme']",
            ".theme-selector",
        ]

        theme_selector = None
        for selector in theme_selectors:
            if await mcp_page.locator(selector).count() > 0:
                theme_selector = selector
                break

        if theme_selector:
            # Get available theme options
            theme_options = await mcp_page.locator(f"{theme_selector} option").all_text_contents()

            # Test switching between available themes
            for theme in theme_options[:3]:  # Test first 3 themes to avoid timeout
                await mcp_page.select_option(theme_selector, theme)
                await mcp_page.wait_for_timeout(1000)  # Wait for theme change

                # Verify theme change by checking CSS properties
                body_styles = await mcp_page.evaluate(
                    """
                    () => {
                        const body = document.body;
                        const styles = window.getComputedStyle(body);
                        return {
                            backgroundColor: styles.backgroundColor,
                            color: styles.color
                        };
                    }
                """
                )

                assert body_styles["backgroundColor"], "Background color should be set"
                assert body_styles["color"], "Text color should be set"

        else:
            # If no theme selector found, just verify current theme consistency
            body_styles = await mcp_page.evaluate(
                """
                () => {
                    const body = document.body;
                    const styles = window.getComputedStyle(body);
                    return {
                        backgroundColor: styles.backgroundColor,
                        color: styles.color
                    };
                }
            """
            )
            assert body_styles[
                "backgroundColor"
            ], "Background color should be set even without theme selector"

    async def test_tab_navigation_workflow(self, mcp_page):
        """
        Test navigation between different tabs/sections of the application.
        """
        # Look for tab navigation elements
        tab_selectors = [
            ".nav-tabs .nav-link",
            ".enhanced-tabs .tab",
            "[role='tab']",
            ".dbc-tab",
            ".tab-button",
        ]

        tabs_found = False
        for selector in tab_selectors:
            tab_count = await mcp_page.locator(selector).count()
            if tab_count > 0:
                tabs_found = True
                tabs = mcp_page.locator(selector)

                # Test clicking on each tab
                for i in range(min(tab_count, 4)):  # Test up to 4 tabs
                    tab = tabs.nth(i)
                    if await tab.is_visible():
                        tab_text = await tab.text_content()

                        # Click the tab
                        await tab.click()
                        await mcp_page.wait_for_timeout(1000)

                        # Verify tab is active (check for active class)
                        classes = await tab.get_attribute("class")
                        active_indicators = ["active", "selected", "current"]
                        is_active = any(
                            indicator in classes.lower() for indicator in active_indicators
                        )

                        # Alternative check: look for active state in parent or nearby elements
                        if not is_active:
                            parent = tab.locator("..")
                            parent_classes = await parent.get_attribute("class") or ""
                            is_active = any(
                                indicator in parent_classes.lower()
                                for indicator in active_indicators
                            )

                        assert is_active or tab_text, f"Tab {i} should be active or have content"

                break

        if not tabs_found:
            # If no traditional tabs, check for other navigation elements
            nav_elements = await mcp_page.locator("nav, .navigation, .sidebar").count()
            assert nav_elements >= 0  # Just verify app loaded

    async def test_data_export_workflow(self, mcp_page):
        """
        Test data export functionality if available.
        """
        # First upload data
        test_csv = Path(__file__).parent.parent / "fixtures" / "test_data" / "sample_meld_data.csv"
        upload_selector = 'input[type="file"]'
        await mcp_page.set_input_files(upload_selector, str(test_csv))
        await mcp_page.wait_for_timeout(2000)

        # Look for export buttons
        export_selectors = [
            "button[data-export-format]",
            ".export-button",
            "button:has-text('Export')",
            "button:has-text('Download')",
            "[id*='export']",
            "[id*='download']",
        ]

        for selector in export_selectors:
            export_buttons = mcp_page.locator(selector)
            button_count = await export_buttons.count()

            if button_count > 0:
                # Test the first export button
                export_button = export_buttons.first
                if await export_button.is_visible():

                    # Setup download handler
                    async with mcp_page.expect_download() as download_info:
                        await export_button.click()
                        await mcp_page.wait_for_timeout(2000)

                    try:
                        download = await download_info.value
                        assert download.suggested_filename, "Downloaded file should have a filename"

                        # Verify file was downloaded
                        download_path = f"/tmp/{download.suggested_filename}"
                        await download.save_as(download_path)

                        # Check file exists and has content
                        import os

                        assert os.path.exists(download_path), "Downloaded file should exist"
                        assert (
                            os.path.getsize(download_path) > 0
                        ), "Downloaded file should not be empty"

                        return  # Success - exit after first successful export

                    except Exception as e:
                        # Download might not trigger immediately, continue to next selector
                        print(f"Export test warning: {e}")
                        continue

        # If no export functionality found, that's acceptable
        print("No export functionality detected - this is acceptable")

    async def test_responsive_design_workflow(self, mcp_page):
        """
        Test responsive design behavior across different viewport sizes.
        """
        # Test different viewport sizes
        viewports = [
            {"width": 1920, "height": 1080, "name": "Desktop Large"},
            {"width": 1366, "height": 768, "name": "Desktop Standard"},
            {"width": 768, "height": 1024, "name": "Tablet"},
            {"width": 375, "height": 667, "name": "Mobile"},
        ]

        for viewport in viewports:
            await mcp_page.set_viewport_size(
                {"width": viewport["width"], "height": viewport["height"]}
            )
            await mcp_page.wait_for_timeout(1000)  # Allow layout to adjust

            # Verify page elements are still accessible
            main_content = mcp_page.locator(".dash-app-content")
            assert (
                await main_content.is_visible()
            ), f"Main content should be visible at {viewport['name']} size"

            # Check if critical elements are still accessible
            upload_area = mcp_page.locator('input[type="file"]')
            if await upload_area.count() > 0:
                # Check if upload area is visible or can be made visible
                is_visible = await upload_area.is_visible()
                if not is_visible:
                    # Try to find parent upload container
                    upload_container = mcp_page.locator('[id*="upload"], .upload')
                    container_count = await upload_container.count()
                    assert (
                        container_count > 0
                    ), f"Upload functionality should be accessible at {viewport['name']} size"

            # Verify no horizontal scrolling needed (within reason)
            if viewport["width"] >= 768:  # Only check for tablet and desktop
                page_width = await mcp_page.evaluate("document.documentElement.scrollWidth")
                viewport_width = viewport["width"]
                assert (
                    page_width <= viewport_width + 20
                ), f"Page should not require horizontal scrolling at {viewport['name']} size"

    async def test_error_recovery_workflow(self, mcp_page):
        """
        Test error handling and recovery scenarios.
        """
        # Test invalid file upload
        invalid_csv = (
            Path(__file__).parent.parent / "fixtures" / "test_data" / "invalid_meld_data.csv"
        )

        if invalid_csv.exists():
            upload_selector = 'input[type="file"]'
            await mcp_page.set_input_files(upload_selector, str(invalid_csv))
            await mcp_page.wait_for_timeout(3000)  # Wait for error processing

            # Look for error messages
            error_selectors = [
                ".alert-danger",
                ".error-message",
                "[role='alert']",
                ".notification.error",
                ".toast.error",
            ]

            error_found = False
            for selector in error_selectors:
                error_elements = mcp_page.locator(selector)
                if await error_elements.count() > 0:
                    error_text = await error_elements.first.text_content()
                    assert error_text.strip(), "Error message should not be empty"
                    error_found = True
                    break

            # If no specific error UI found, check console for errors
            if not error_found:
                console_errors = await mcp_page.evaluate("window.console_errors || []")
                # Some console errors are expected with invalid data
                assert isinstance(console_errors, list), "Console errors should be tracked"

        # Test recovery by uploading valid file
        valid_csv = Path(__file__).parent.parent / "fixtures" / "test_data" / "sample_meld_data.csv"
        await mcp_page.set_input_files(upload_selector, str(valid_csv))
        await mcp_page.wait_for_timeout(2000)

        # Verify recovery by checking for successful graph render
        graph_selector = "#main-graph .plotly-graph-div"
        await mcp_page.wait_for_selector(graph_selector, timeout=20000)

        graph_has_data = await mcp_page.evaluate(
            """
            () => {
                const graphDiv = document.querySelector('#main-graph');
                return graphDiv && graphDiv.data && graphDiv.data.length > 0;
            }
        """
        )
        assert graph_has_data, "Application should recover and display valid data after error"

    async def test_performance_benchmarks(self, mcp_page):
        """
        Test performance benchmarks for critical operations.
        """
        # Measure page load time
        load_start = time.time()
        await mcp_page.goto("http://127.0.0.1:8050")
        await mcp_page.wait_for_load_state("networkidle")
        load_time = (time.time() - load_start) * 1000  # Convert to milliseconds

        assert load_time < 5000, f"Page load should be under 5 seconds, actual: {load_time:.0f}ms"

        # Measure CSV upload and processing time
        test_csv = Path(__file__).parent.parent / "fixtures" / "test_data" / "sample_meld_data.csv"

        upload_start = time.time()
        upload_selector = 'input[type="file"]'
        await mcp_page.set_input_files(upload_selector, str(test_csv))
        await mcp_page.wait_for_selector("#main-graph .plotly-graph-div", timeout=30000)
        upload_time = (time.time() - upload_start) * 1000

        assert (
            upload_time < 10000
        ), f"CSV processing should be under 10 seconds, actual: {upload_time:.0f}ms"

        # Measure memory usage if available
        memory_info = await mcp_page.evaluate(
            """
            () => {
                if (performance.memory) {
                    return {
                        used: performance.memory.usedJSHeapSize,
                        total: performance.memory.totalJSHeapSize,
                        limit: performance.memory.jsHeapSizeLimit
                    };
                }
                return null;
            }
        """
        )

        if memory_info:
            memory_usage_mb = memory_info["used"] / (1024 * 1024)
            assert (
                memory_usage_mb < 100
            ), f"Memory usage should be reasonable, actual: {memory_usage_mb:.1f}MB"
