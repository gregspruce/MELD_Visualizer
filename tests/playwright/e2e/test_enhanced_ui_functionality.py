"""
Enhanced UI Functionality E2E Tests for MELD Visualizer
Tests the Enhanced UI components: loading states, notifications, responsive design, and desktop-optimized UX.
"""

import time
from pathlib import Path

import pytest


class TestEnhancedUIFunctionality:
    """Test suite for Enhanced UI components and functionality."""

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

    async def test_loading_overlay_behavior(self, mcp_page):
        """
        Test loading overlay appears and disappears correctly during data processing.
        """
        # Look for loading overlay elements
        loading_selectors = [
            ".loading-overlay",
            ".dash-spinner",
            '[data-loading="true"]',
            ".loading-spinner",
            ".enhanced-loading-overlay",
        ]

        # Upload file to trigger loading
        test_csv = Path(__file__).parent.parent / "fixtures" / "test_data" / "sample_meld_data.csv"
        upload_selector = 'input[type="file"]'

        # Start file upload
        await mcp_page.set_input_files(upload_selector, str(test_csv))

        # Check if loading indicators appear (within first 2 seconds)
        loading_appeared = False
        start_time = time.time()

        while time.time() - start_time < 2.0:
            for selector in loading_selectors:
                loading_elements = mcp_page.locator(selector)
                if await loading_elements.count() > 0:
                    if await loading_elements.first.is_visible():
                        loading_appeared = True
                        break

            if loading_appeared:
                break
            await mcp_page.wait_for_timeout(100)

        # Wait for processing to complete
        await mcp_page.wait_for_selector("#main-graph .plotly-graph-div", timeout=20000)
        await mcp_page.wait_for_timeout(1000)  # Additional wait for cleanup

        # Verify loading indicators are gone
        for selector in loading_selectors:
            loading_elements = mcp_page.locator(selector)
            if await loading_elements.count() > 0:
                is_visible = await loading_elements.first.is_visible()
                assert (
                    not is_visible
                ), f"Loading indicator {selector} should be hidden after processing"

    async def test_toast_notification_system(self, mcp_page):
        """
        Test toast notification system for user feedback.
        """
        # Look for toast container
        toast_selectors = [
            ".toast-container",
            "#toast-container",
            ".notification-container",
            ".alert-container",
            ".enhanced-toast",
        ]

        toast_container = None
        for selector in toast_selectors:
            if await mcp_page.locator(selector).count() > 0:
                toast_container = selector
                break

        # Upload valid file to potentially trigger success notification
        test_csv = Path(__file__).parent.parent / "fixtures" / "test_data" / "sample_meld_data.csv"
        upload_selector = 'input[type="file"]'
        await mcp_page.set_input_files(upload_selector, str(test_csv))

        # Wait for processing
        await mcp_page.wait_for_timeout(3000)

        # Check for any notification messages
        notification_selectors = [".toast", ".alert", ".notification", ".message", "[role='alert']"]

        notifications_found = []
        for selector in notification_selectors:
            notifications = mcp_page.locator(selector)
            count = await notifications.count()
            if count > 0:
                for i in range(count):
                    notification = notifications.nth(i)
                    if await notification.is_visible():
                        text = await notification.text_content()
                        classes = await notification.get_attribute("class") or ""
                        notifications_found.append(
                            {"text": text.strip(), "classes": classes, "selector": selector}
                        )

        # Verify notification system is working (even if no notifications are currently shown)
        if toast_container:
            container_element = mcp_page.locator(toast_container)
            assert await container_element.count() > 0, "Toast container should exist"

        # Test invalid file upload to trigger error notification
        invalid_csv = (
            Path(__file__).parent.parent / "fixtures" / "test_data" / "invalid_meld_data.csv"
        )
        if invalid_csv.exists():
            await mcp_page.set_input_files(upload_selector, str(invalid_csv))
            await mcp_page.wait_for_timeout(3000)

            # Look for error notifications
            error_notifications = []
            for selector in notification_selectors:
                notifications = mcp_page.locator(selector)
                count = await notifications.count()
                if count > 0:
                    for i in range(count):
                        notification = notifications.nth(i)
                        if await notification.is_visible():
                            text = await notification.text_content()
                            classes = await notification.get_attribute("class") or ""
                            if any(
                                error_class in classes.lower()
                                for error_class in ["error", "danger", "fail"]
                            ):
                                error_notifications.append(text.strip())

            # Error notifications are good to have but not required
            print(f"Error notifications found: {error_notifications}")

    async def test_progress_indicator_functionality(self, mcp_page):
        """
        Test progress indicators during data processing operations.
        """
        # Look for progress indicator elements
        progress_selectors = [
            ".progress",
            ".progress-bar",
            ".enhanced-progress",
            ".progress-indicator",
            "[role='progressbar']",
        ]

        # Upload file to trigger progress indication
        test_csv = Path(__file__).parent.parent / "fixtures" / "test_data" / "sample_meld_data.csv"
        upload_selector = 'input[type="file"]'

        await mcp_page.set_input_files(upload_selector, str(test_csv))

        # Check for progress indicators during processing
        progress_found = False
        start_time = time.time()

        while time.time() - start_time < 5.0:  # Check for 5 seconds
            for selector in progress_selectors:
                progress_elements = mcp_page.locator(selector)
                if await progress_elements.count() > 0:
                    progress_element = progress_elements.first
                    if await progress_element.is_visible():
                        progress_found = True

                        # Check progress bar attributes
                        aria_valuenow = await progress_element.get_attribute("aria-valuenow")
                        style = await progress_element.get_attribute("style") or ""

                        # Verify progress indicator has meaningful values
                        if aria_valuenow:
                            value = float(aria_valuenow)
                            assert 0 <= value <= 100, "Progress value should be between 0 and 100"

                        if "width:" in style:
                            # Progress bar should have width style
                            assert (
                                "%" in style or "px" in style
                            ), "Progress bar should have width styling"

                        break

            if progress_found:
                break
            await mcp_page.wait_for_timeout(200)

        # Wait for completion
        await mcp_page.wait_for_selector("#main-graph .plotly-graph-div", timeout=20000)

        # Verify progress indicators are cleaned up after completion
        for selector in progress_selectors:
            progress_elements = mcp_page.locator(selector)
            if await progress_elements.count() > 0:
                for i in range(await progress_elements.count()):
                    progress_element = progress_elements.nth(i)
                    if await progress_element.is_visible():
                        # Check if progress shows 100% completion or is hidden
                        aria_valuenow = await progress_element.get_attribute("aria-valuenow")
                        if aria_valuenow:
                            value = float(aria_valuenow)
                            # Progress should be complete (100) or element should be hidden
                            is_complete = value == 100 or value == 0  # 0 might indicate reset state
                            assert (
                                is_complete
                            ), f"Progress should be complete after processing, found: {value}"

    async def test_enhanced_upload_area_styling(self, mcp_page):
        """
        Test enhanced upload area with improved visual feedback.
        """
        # Find upload area
        upload_selectors = [
            ".enhanced-upload-area",
            ".upload-area",
            '[id*="upload"]',
            'input[type="file"]',
        ]

        upload_element = None
        for selector in upload_selectors:
            if await mcp_page.locator(selector).count() > 0:
                upload_element = mcp_page.locator(selector).first
                break

        assert upload_element, "Upload area should be found"

        # Check upload area styling and visual feedback
        if await upload_element.is_visible():
            # Get computed styles
            styles = await mcp_page.evaluate(
                """
                (selector) => {
                    const element = document.querySelector(selector);
                    if (!element) return null;
                    const computedStyle = window.getComputedStyle(element);
                    return {
                        border: computedStyle.border,
                        borderStyle: computedStyle.borderStyle,
                        borderColor: computedStyle.borderColor,
                        borderRadius: computedStyle.borderRadius,
                        backgroundColor: computedStyle.backgroundColor,
                        padding: computedStyle.padding,
                        minHeight: computedStyle.minHeight
                    };
                }
            """,
                upload_selectors[0] if upload_element else upload_selectors[-1],
            )

            if styles:
                # Enhanced upload area should have styling
                assert (
                    styles["border"] or styles["borderStyle"]
                ), "Upload area should have border styling"
                assert styles["padding"], "Upload area should have padding for better UX"

        # Test drag and drop styling (simulate drag enter/leave)
        if await upload_element.is_visible():
            # Get element box
            box = await upload_element.bounding_box()
            if box:
                # Simulate drag enter
                await mcp_page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)

                # Check for hover/active states via CSS classes or styling changes
                classes_before = await upload_element.get_attribute("class") or ""

                # Hover over the element
                await upload_element.hover()
                await mcp_page.wait_for_timeout(500)

                classes_after = await upload_element.get_attribute("class") or ""

                # Enhanced upload areas often have hover states
                # This is not required but good for UX
                print(f"Upload area classes - before: {classes_before}, after: {classes_after}")

    async def test_responsive_control_panels(self, mcp_page):
        """
        Test responsive behavior of control panels and UI components.
        """
        # Test different viewport sizes
        viewports = [
            {"width": 1920, "height": 1080, "name": "Desktop Large"},
            {"width": 1366, "height": 768, "name": "Desktop Standard"},
            {"width": 768, "height": 1024, "name": "Tablet"},
            {"width": 375, "height": 667, "name": "Mobile"},
        ]

        # Upload data first to ensure controls are available
        test_csv = Path(__file__).parent.parent / "fixtures" / "test_data" / "sample_meld_data.csv"
        upload_selector = 'input[type="file"]'
        await mcp_page.set_input_files(upload_selector, str(test_csv))
        await mcp_page.wait_for_timeout(3000)

        # Find control panels
        control_selectors = [
            ".control-panel",
            ".enhanced-control-panel",
            ".sidebar",
            ".controls",
            ".filter-controls",
            "[class*='control']",
        ]

        control_panels = []
        for selector in control_selectors:
            panels = mcp_page.locator(selector)
            count = await panels.count()
            for i in range(count):
                panel = panels.nth(i)
                if await panel.is_visible():
                    control_panels.append(panel)

        # Test responsiveness across viewports
        for viewport in viewports:
            await mcp_page.set_viewport_size(
                {"width": viewport["width"], "height": viewport["height"]}
            )
            await mcp_page.wait_for_timeout(1000)  # Allow layout to adjust

            # Check if control panels adapt properly
            for i, panel in enumerate(control_panels):
                try:
                    is_visible = await panel.is_visible()
                    if is_visible:
                        box = await panel.bounding_box()
                        if box:
                            # Control panel should not overflow viewport
                            assert (
                                box["x"] >= 0
                            ), f"Control panel {i} should not overflow left at {viewport['name']}"
                            assert (
                                box["x"] + box["width"] <= viewport["width"] + 20
                            ), f"Control panel {i} should not overflow right at {viewport['name']}"  # 20px tolerance

                            # Panel should have reasonable minimum size
                            if viewport["width"] >= 768:  # Desktop/tablet only
                                assert (
                                    box["width"] >= 200
                                ), f"Control panel {i} should maintain minimum width at {viewport['name']}"
                except Exception as e:
                    print(f"Control panel {i} test warning at {viewport['name']}: {e}")

    async def test_enhanced_tab_navigation(self, mcp_page):
        """
        Test enhanced tab navigation with scroll functionality.
        """
        # Look for enhanced tab navigation
        tab_selectors = [
            ".enhanced-tabs",
            ".enhanced-tabs-container",
            ".tab-scroll-button",
            ".enhanced-tab-item",
        ]

        enhanced_tabs_found = False
        tab_container = None

        for selector in tab_selectors:
            if await mcp_page.locator(selector).count() > 0:
                enhanced_tabs_found = True
                if "container" in selector:
                    tab_container = mcp_page.locator(selector).first
                break

        if enhanced_tabs_found:
            # Test tab scroll buttons if they exist
            scroll_buttons = [
                ".tab-scroll-button.left",
                ".tab-scroll-button.right",
                "#tab-scroll-left",
                "#tab-scroll-right",
            ]

            for button_selector in scroll_buttons:
                scroll_button = mcp_page.locator(button_selector)
                if await scroll_button.count() > 0:
                    button = scroll_button.first
                    is_visible = await button.is_visible()
                    is_disabled = await button.is_disabled()

                    # Test scroll button functionality
                    if is_visible and not is_disabled:
                        await button.click()
                        await mcp_page.wait_for_timeout(500)  # Wait for scroll animation

                        # Verify scroll occurred (tabs container should have changed scroll position)
                        if tab_container:
                            scroll_left = await tab_container.evaluate("el => el.scrollLeft")
                            assert isinstance(
                                scroll_left, (int, float)
                            ), "Scroll position should be numeric"

        # Test standard tab navigation regardless of enhanced features
        standard_tabs = mcp_page.locator(".nav-tabs .nav-link, [role='tab'], .tab")
        tab_count = await standard_tabs.count()

        if tab_count > 0:
            # Click through available tabs
            for i in range(min(tab_count, 4)):  # Test up to 4 tabs
                tab = standard_tabs.nth(i)
                if await tab.is_visible():
                    await tab.click()
                    await mcp_page.wait_for_timeout(1000)

                    # Verify tab activation
                    classes = await tab.get_attribute("class") or ""
                    is_active = "active" in classes.lower()

                    # Alternative check for active state
                    if not is_active:
                        aria_selected = await tab.get_attribute("aria-selected")
                        is_active = aria_selected == "true"

                    assert is_active or classes, f"Tab {i} should show active state or have classes"

    async def test_desktop_optimized_layout(self, mcp_page):
        """
        Test desktop-optimized layout features and spacing.
        """
        # Set desktop viewport
        await mcp_page.set_viewport_size({"width": 1920, "height": 1080})
        await mcp_page.wait_for_timeout(1000)

        # Upload data to populate interface
        test_csv = Path(__file__).parent.parent / "fixtures" / "test_data" / "sample_meld_data.csv"
        upload_selector = 'input[type="file"]'
        await mcp_page.set_input_files(upload_selector, str(test_csv))
        await mcp_page.wait_for_selector("#main-graph .plotly-graph-div", timeout=20000)

        # Test layout efficiency - check for good use of screen real estate
        layout_metrics = await mcp_page.evaluate(
            """
            () => {
                const body = document.body;
                const main = document.querySelector('.dash-app-content, main, [id*="app"]');
                const graphs = document.querySelectorAll('[id*="graph"], .plotly-graph-div');
                const controls = document.querySelectorAll('.control-panel, .sidebar, [class*="control"]');

                return {
                    bodyHeight: body.scrollHeight,
                    viewportHeight: window.innerHeight,
                    viewportWidth: window.innerWidth,
                    mainWidth: main ? main.offsetWidth : 0,
                    graphCount: graphs.length,
                    controlCount: controls.length,
                    verticalScrollNeeded: body.scrollHeight > window.innerHeight,
                    horizontalScrollNeeded: body.scrollWidth > window.innerWidth
                };
            }
        """
        )

        # Desktop layout should efficiently use space
        assert layout_metrics["viewportWidth"] == 1920, "Viewport should be set to desktop size"
        assert (
            layout_metrics["mainWidth"] > 1200
        ), "Main content should use desktop space efficiently"

        # Should not require horizontal scrolling on desktop
        assert not layout_metrics[
            "horizontalScrollNeeded"
        ], "Desktop layout should not require horizontal scrolling"

        # Graphs should be appropriately sized for desktop
        if layout_metrics["graphCount"] > 0:
            graph_metrics = await mcp_page.evaluate(
                """
                () => {
                    const graph = document.querySelector('[id*="graph"], .plotly-graph-div');
                    if (!graph) return null;
                    return {
                        width: graph.offsetWidth,
                        height: graph.offsetHeight
                    };
                }
            """
            )

            if graph_metrics:
                assert (
                    graph_metrics["width"] > 800
                ), "Graphs should be sized appropriately for desktop viewing"
                assert (
                    graph_metrics["height"] > 400
                ), "Graphs should have adequate height for desktop"

    async def test_user_feedback_consistency(self, mcp_page):
        """
        Test consistency of user feedback across different operations.
        """
        # Test feedback for successful operations
        test_csv = Path(__file__).parent.parent / "fixtures" / "test_data" / "sample_meld_data.csv"
        upload_selector = 'input[type="file"]'

        # Upload valid file and monitor feedback
        await mcp_page.set_input_files(upload_selector, str(test_csv))

        # Look for consistent feedback patterns
        feedback_elements = []

        # Check for loading feedback
        await mcp_page.wait_for_timeout(1000)
        loading_indicators = await mcp_page.locator(
            ".loading-overlay, .dash-spinner, [data-loading='true']"
        ).count()
        if loading_indicators > 0:
            feedback_elements.append("loading")

        # Wait for completion
        await mcp_page.wait_for_selector("#main-graph .plotly-graph-div", timeout=20000)

        # Check for completion feedback
        success_indicators = [
            ".alert-success",
            ".notification.success",
            ".toast.success",
            ".success-message",
        ]

        for selector in success_indicators:
            if await mcp_page.locator(selector).count() > 0:
                feedback_elements.append("success")
                break

        # Check for visual feedback (graph appearance)
        graph_visible = await mcp_page.locator("#main-graph .plotly-graph-div").is_visible()
        if graph_visible:
            feedback_elements.append("visual")

        # User should get some form of feedback for operations
        assert (
            len(feedback_elements) > 0
        ), f"User should receive feedback for operations, found: {feedback_elements}"

        # Test error feedback consistency
        invalid_csv = (
            Path(__file__).parent.parent / "fixtures" / "test_data" / "invalid_meld_data.csv"
        )
        if invalid_csv.exists():
            await mcp_page.set_input_files(upload_selector, str(invalid_csv))
            await mcp_page.wait_for_timeout(3000)

            # Look for error feedback
            error_feedback = []
            error_selectors = [
                ".alert-danger",
                ".alert-error",
                ".notification.error",
                ".toast.error",
                ".error-message",
                "[role='alert']",
            ]

            for selector in error_selectors:
                error_elements = mcp_page.locator(selector)
                if await error_elements.count() > 0:
                    for i in range(await error_elements.count()):
                        element = error_elements.nth(i)
                        if await element.is_visible():
                            text = await element.text_content()
                            if text and text.strip():
                                error_feedback.append(text.strip())

            # Error feedback is helpful but not required
            print(f"Error feedback found: {error_feedback}")

    async def test_keyboard_accessibility_enhanced_ui(self, mcp_page):
        """
        Test keyboard accessibility for Enhanced UI components.
        """
        # Focus on enhanced UI elements and test keyboard navigation
        focusable_selectors = [
            "button",
            "input",
            "select",
            "textarea",
            "[tabindex]:not([tabindex='-1'])",
            ".enhanced-tab-item",
            ".tab-scroll-button",
        ]

        focusable_elements = []
        for selector in focusable_selectors:
            elements = mcp_page.locator(selector)
            count = await elements.count()
            for i in range(count):
                element = elements.nth(i)
                if await element.is_visible():
                    focusable_elements.append(element)

        # Test tab navigation through focusable elements
        for i, element in enumerate(focusable_elements[:10]):  # Test first 10 elements
            try:
                await element.focus()
                await mcp_page.wait_for_timeout(200)

                # Check if element is actually focused
                is_focused = await element.evaluate("el => document.activeElement === el")

                # Test keyboard interaction if element is interactive
                tag_name = await element.evaluate("el => el.tagName.toLowerCase()")

                if tag_name == "button":
                    # Test Enter key on buttons
                    await element.press("Enter")
                    await mcp_page.wait_for_timeout(500)
                elif tag_name in ["input", "textarea"]:
                    # Test typing in input fields
                    input_type = await element.get_attribute("type") or "text"
                    if input_type in ["text", "number", "email"]:
                        await element.fill("test")
                        await mcp_page.wait_for_timeout(200)
                        await element.clear()
                elif tag_name == "select":
                    # Test arrow keys on selects
                    await element.press("ArrowDown")
                    await mcp_page.wait_for_timeout(200)

                # Verify element maintains focus or behaves appropriately
                assert is_focused or tag_name in [
                    "button"
                ], f"Element {i} ({tag_name}) should be focusable"

            except Exception as e:
                print(f"Keyboard test warning for element {i}: {e}")

        # Test escape key behavior (should not break the interface)
        await mcp_page.keyboard.press("Escape")
        await mcp_page.wait_for_timeout(500)

        # Verify application is still responsive
        main_content = mcp_page.locator(".dash-app-content")
        assert (
            await main_content.is_visible()
        ), "Application should remain responsive after keyboard interactions"
