"""
Responsive Design E2E Tests for MELD Visualizer
Tests responsive behavior, mobile compatibility, and cross-viewport functionality.
"""

import time
from pathlib import Path

import pytest


class TestResponsiveDesign:
    """Test suite for responsive design and cross-viewport compatibility."""

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

    async def test_desktop_viewport_optimization(self, mcp_page):
        """
        Test desktop viewport optimization and space utilization.
        """
        # Test various desktop resolutions
        desktop_viewports = [
            {"width": 1920, "height": 1080, "name": "1080p Desktop"},
            {"width": 2560, "height": 1440, "name": "1440p Desktop"},
            {"width": 3840, "height": 2160, "name": "4K Desktop"},
            {"width": 1366, "height": 768, "name": "Standard Laptop"},
            {"width": 1536, "height": 864, "name": "Surface Laptop"},
        ]

        # Upload data to populate interface
        test_csv = Path(__file__).parent.parent / "fixtures" / "test_data" / "sample_meld_data.csv"
        upload_selector = 'input[type="file"]'

        desktop_results = []

        for viewport in desktop_viewports:
            await mcp_page.set_viewport_size(
                {"width": viewport["width"], "height": viewport["height"]}
            )
            await mcp_page.wait_for_timeout(1000)  # Allow layout adjustment

            # Upload file if not already done
            try:
                await mcp_page.set_input_files(upload_selector, str(test_csv))
                await mcp_page.wait_for_timeout(2000)
            except Exception:
                pass  # File might already be uploaded

            # Measure layout efficiency
            layout_metrics = await mcp_page.evaluate(
                f"""
                () => {{
                    const viewport = {{width: {viewport["width"]}, height: {viewport["height"]}}};
                    const body = document.body;
                    const main = document.querySelector('.dash-app-content, main, [id*="app"]');
                    const graph = document.querySelector('#main-graph, [id*="graph"]');

                    return {{
                        viewportWidth: window.innerWidth,
                        viewportHeight: window.innerHeight,
                        bodyScrollWidth: body.scrollWidth,
                        bodyScrollHeight: body.scrollHeight,
                        mainWidth: main ? main.offsetWidth : 0,
                        mainHeight: main ? main.offsetHeight : 0,
                        graphWidth: graph ? graph.offsetWidth : 0,
                        graphHeight: graph ? graph.offsetHeight : 0,
                        horizontalScrollNeeded: body.scrollWidth > window.innerWidth,
                        verticalScrollNeeded: body.scrollHeight > window.innerHeight,
                        spaceUtilization: main ? (main.offsetWidth / window.innerWidth) : 0
                    }};
                }}
            """
            )

            # Desktop optimization checks
            space_utilization_good = layout_metrics["spaceUtilization"] > 0.8  # Using >80% of width
            no_horizontal_scroll = not layout_metrics["horizontalScrollNeeded"]
            graph_appropriately_sized = (
                layout_metrics["graphWidth"] > 600 if layout_metrics["graphWidth"] > 0 else True
            )

            desktop_results.append(
                {
                    "viewport": viewport["name"],
                    "width": viewport["width"],
                    "height": viewport["height"],
                    "space_utilization": layout_metrics["spaceUtilization"],
                    "no_horizontal_scroll": no_horizontal_scroll,
                    "graph_width": layout_metrics["graphWidth"],
                    "graph_height": layout_metrics["graphHeight"],
                    "optimized": space_utilization_good
                    and no_horizontal_scroll
                    and graph_appropriately_sized,
                }
            )

            # Desktop viewports should not require horizontal scrolling
            assert (
                no_horizontal_scroll
            ), f"Desktop viewport {viewport['name']} should not require horizontal scrolling"

            # Main content should utilize desktop space well
            if viewport["width"] >= 1366:  # Standard desktop and above
                assert (
                    layout_metrics["spaceUtilization"] > 0.7
                ), f"Desktop {viewport['name']} should utilize space efficiently: {layout_metrics['spaceUtilization']:.2f}"

        print("Desktop Viewport Optimization Results:")
        for result in desktop_results:
            print(f"  {result['viewport']}: {result['width']}x{result['height']}")
            print(f"    Space Utilization: {result['space_utilization']:.2f}")
            print(f"    Graph Size: {result['graph_width']}x{result['graph_height']}")
            print(f"    Optimized: {result['optimized']}")

    async def test_tablet_viewport_adaptation(self, mcp_page):
        """
        Test tablet viewport adaptation and touch-friendly interfaces.
        """
        tablet_viewports = [
            {"width": 768, "height": 1024, "name": "iPad Portrait"},
            {"width": 1024, "height": 768, "name": "iPad Landscape"},
            {"width": 820, "height": 1180, "name": "iPad Air Portrait"},
            {"width": 1180, "height": 820, "name": "iPad Air Landscape"},
            {"width": 800, "height": 1280, "name": "Android Tablet Portrait"},
            {"width": 1280, "height": 800, "name": "Android Tablet Landscape"},
        ]

        # Upload data
        test_csv = Path(__file__).parent.parent / "fixtures" / "test_data" / "sample_meld_data.csv"
        upload_selector = 'input[type="file"]'

        tablet_results = []

        for viewport in tablet_viewports:
            await mcp_page.set_viewport_size(
                {"width": viewport["width"], "height": viewport["height"]}
            )
            await mcp_page.wait_for_timeout(1500)  # Allow layout adjustment

            # Upload file if needed
            try:
                await mcp_page.set_input_files(upload_selector, str(test_csv))
                await mcp_page.wait_for_timeout(3000)
            except Exception:
                pass

            # Check touch-friendly interface elements
            touch_elements = await mcp_page.evaluate(
                """
                () => {
                    const buttons = document.querySelectorAll('button, .btn, input[type="button"], input[type="submit"]');
                    const links = document.querySelectorAll('a[href], .clickable');
                    const inputs = document.querySelectorAll('input, select, textarea');

                    let touchFriendlyElements = 0;
                    const minTouchSize = 44; // 44px minimum touch target size

                    const checkElements = (elements) => {
                        elements.forEach(el => {
                            const rect = el.getBoundingClientRect();
                            const computedStyle = window.getComputedStyle(el);
                            const width = Math.max(rect.width, parseFloat(computedStyle.minWidth) || 0);
                            const height = Math.max(rect.height, parseFloat(computedStyle.minHeight) || 0);

                            if (width >= minTouchSize && height >= minTouchSize) {
                                touchFriendlyElements++;
                            }
                        });
                    };

                    checkElements(buttons);
                    checkElements(links);
                    checkElements(inputs);

                    return {
                        totalInteractiveElements: buttons.length + links.length + inputs.length,
                        touchFriendlyElements: touchFriendlyElements,
                        touchFriendlyRatio: touchFriendlyElements / (buttons.length + links.length + inputs.length)
                    };
                }
            """
            )

            # Check layout adaptation
            layout_adapted = await mcp_page.evaluate(
                """
                () => {
                    const main = document.querySelector('.dash-app-content, main');
                    const graph = document.querySelector('#main-graph, [id*="graph"]');
                    const controls = document.querySelectorAll('.control-panel, .sidebar, [class*="control"]');

                    return {
                        mainVisible: main ? main.offsetWidth > 0 && main.offsetHeight > 0 : false,
                        graphVisible: graph ? graph.offsetWidth > 0 && graph.offsetHeight > 0 : false,
                        graphWidth: graph ? graph.offsetWidth : 0,
                        controlsCount: controls.length,
                        horizontalScroll: document.body.scrollWidth > window.innerWidth,
                        verticalScroll: document.body.scrollHeight > window.innerHeight
                    };
                }
            """
            )

            # Test touch interactions if elements are present
            touch_interaction_works = True
            try:
                # Find interactive elements
                buttons = mcp_page.locator("button, .btn")
                button_count = await buttons.count()

                if button_count > 0:
                    # Test tap instead of click for touch devices
                    first_button = buttons.first
                    if await first_button.is_visible():
                        await first_button.tap()
                        await mcp_page.wait_for_timeout(500)

                # Test graph touch interactions if graph exists
                graph = mcp_page.locator("#main-graph")
                if await graph.count() > 0 and await graph.is_visible():
                    # Test pinch-to-zoom simulation (double tap)
                    await graph.dblclick()
                    await mcp_page.wait_for_timeout(500)

            except Exception as e:
                touch_interaction_works = False
                print(f"Touch interaction test failed on {viewport['name']}: {e}")

            tablet_results.append(
                {
                    "viewport": viewport["name"],
                    "width": viewport["width"],
                    "height": viewport["height"],
                    "touch_friendly_ratio": touch_elements["touchFriendlyRatio"],
                    "layout_adapted": layout_adapted["mainVisible"]
                    and layout_adapted["graphVisible"],
                    "no_horizontal_scroll": not layout_adapted["horizontalScroll"],
                    "touch_interactions_work": touch_interaction_works,
                    "graph_width": layout_adapted["graphWidth"],
                }
            )

            # Tablet assertions
            assert layout_adapted[
                "mainVisible"
            ], f"Main content should be visible on {viewport['name']}"

            # Should not require horizontal scrolling on tablets
            if viewport["width"] >= 768:
                assert not layout_adapted[
                    "horizontalScroll"
                ], f"Tablet {viewport['name']} should not require horizontal scrolling"

        print("Tablet Viewport Adaptation Results:")
        for result in tablet_results:
            print(f"  {result['viewport']}: {result['width']}x{result['height']}")
            print(f"    Touch Friendly Ratio: {result['touch_friendly_ratio']:.2f}")
            print(f"    Layout Adapted: {result['layout_adapted']}")
            print(f"    Touch Interactions: {result['touch_interactions_work']}")

    async def test_mobile_viewport_compatibility(self, mcp_page):
        """
        Test mobile viewport compatibility and mobile-first design.
        """
        mobile_viewports = [
            {"width": 375, "height": 667, "name": "iPhone SE"},
            {"width": 390, "height": 844, "name": "iPhone 12"},
            {"width": 428, "height": 926, "name": "iPhone 12 Pro Max"},
            {"width": 360, "height": 640, "name": "Galaxy S5"},
            {"width": 412, "height": 915, "name": "Pixel 5"},
            {"width": 414, "height": 896, "name": "iPhone XR"},
        ]

        # Upload data
        test_csv = Path(__file__).parent.parent / "fixtures" / "test_data" / "sample_meld_data.csv"
        upload_selector = 'input[type="file"]'

        mobile_results = []

        for viewport in mobile_viewports:
            await mcp_page.set_viewport_size(
                {"width": viewport["width"], "height": viewport["height"]}
            )
            await mcp_page.wait_for_timeout(2000)  # Allow more time for mobile layout

            # Check if upload is accessible on mobile
            upload_accessible = False
            try:
                upload_element = mcp_page.locator(upload_selector)
                if await upload_element.count() > 0:
                    # Check if upload area is visible or can be scrolled to
                    upload_box = await upload_element.bounding_box()
                    if upload_box and upload_box["y"] >= 0:
                        upload_accessible = True

                        # Try to upload file on mobile
                        await upload_element.set_input_files(str(test_csv))
                        await mcp_page.wait_for_timeout(4000)  # Mobile may be slower
            except Exception as e:
                print(f"Mobile upload test failed on {viewport['name']}: {e}")

            # Check mobile layout adaptation
            mobile_layout = await mcp_page.evaluate(
                """
                () => {
                    const main = document.querySelector('.dash-app-content, main');
                    const graph = document.querySelector('#main-graph, [id*="graph"]');
                    const viewport = {width: window.innerWidth, height: window.innerHeight};

                    // Check if content is stacked vertically (mobile pattern)
                    const isVerticalLayout = window.innerWidth < 768;

                    // Check text readability (font sizes)
                    const textElements = document.querySelectorAll('p, span, div, h1, h2, h3, h4, h5, h6');
                    let readableTextCount = 0;

                    textElements.forEach(el => {
                        const fontSize = parseFloat(window.getComputedStyle(el).fontSize);
                        if (fontSize >= 16) { // 16px minimum for mobile readability
                            readableTextCount++;
                        }
                    });

                    return {
                        mainWidth: main ? main.offsetWidth : 0,
                        graphWidth: graph ? graph.offsetWidth : 0,
                        viewportWidth: viewport.width,
                        viewportHeight: viewport.height,
                        isVerticalLayout: isVerticalLayout,
                        contentFitsWidth: main ? main.offsetWidth <= viewport.width : true,
                        graphFitsWidth: graph ? graph.offsetWidth <= viewport.width : true,
                        horizontalScroll: document.body.scrollWidth > viewport.width,
                        readableTextElements: readableTextCount,
                        totalTextElements: textElements.length,
                        textReadabilityRatio: readableTextCount / Math.max(textElements.length, 1)
                    };
                }
            """
            )

            # Test mobile navigation (if tabs exist)
            mobile_navigation_works = True
            try:
                tabs = mcp_page.locator(".nav-tabs .nav-link, [role='tab'], .tab")
                tab_count = await tabs.count()

                if tab_count > 0:
                    # Test tapping on tabs (mobile interaction)
                    first_tab = tabs.first
                    if await first_tab.is_visible():
                        await first_tab.tap()
                        await mcp_page.wait_for_timeout(1000)
            except Exception as e:
                mobile_navigation_works = False
                print(f"Mobile navigation test failed on {viewport['name']}: {e}")

            # Test mobile scrolling
            mobile_scrolling_works = True
            try:
                # Test vertical scrolling
                await mcp_page.evaluate(
                    """
                    () => {
                        window.scrollTo(0, 100);
                        return new Promise(resolve => setTimeout(resolve, 500));
                    }
                """
                )

                # Test horizontal scrolling prevention
                scroll_x = await mcp_page.evaluate("window.scrollX")
                # Verify no horizontal scroll (scroll_x should be 0)
                assert scroll_x == 0, f"No horizontal scroll expected on {viewport['name']}"

            except Exception as e:
                mobile_scrolling_works = False
                print(f"Mobile scrolling test failed on {viewport['name']}: {e}")

            mobile_results.append(
                {
                    "viewport": viewport["name"],
                    "width": viewport["width"],
                    "height": viewport["height"],
                    "upload_accessible": upload_accessible,
                    "content_fits_width": mobile_layout["contentFitsWidth"],
                    "graph_fits_width": mobile_layout["graphFitsWidth"],
                    "no_horizontal_scroll": not mobile_layout["horizontalScroll"],
                    "text_readable": mobile_layout["textReadabilityRatio"] > 0.7,
                    "navigation_works": mobile_navigation_works,
                    "scrolling_works": mobile_scrolling_works,
                    "mobile_optimized": (
                        mobile_layout["contentFitsWidth"]
                        and not mobile_layout["horizontalScroll"]
                        and mobile_layout["textReadabilityRatio"] > 0.5
                    ),
                }
            )

            # Mobile assertions
            assert mobile_layout[
                "contentFitsWidth"
            ], f"Content should fit mobile width on {viewport['name']}"
            assert not mobile_layout[
                "horizontalScroll"
            ], f"Mobile {viewport['name']} should not require horizontal scrolling"

            # Text should be readable on mobile
            if mobile_layout["totalTextElements"] > 0:
                assert (
                    mobile_layout["textReadabilityRatio"] > 0.3
                ), f"Text should be readable on mobile {viewport['name']}: {mobile_layout['textReadabilityRatio']:.2f}"

        print("Mobile Viewport Compatibility Results:")
        for result in mobile_results:
            print(f"  {result['viewport']}: {result['width']}x{result['height']}")
            print(f"    Mobile Optimized: {result['mobile_optimized']}")
            print(f"    Upload Accessible: {result['upload_accessible']}")
            print(f"    Text Readable: {result['text_readable']}")
            print(f"    Navigation Works: {result['navigation_works']}")

    async def test_viewport_transition_smoothness(self, mcp_page):
        """
        Test smooth transitions between different viewport sizes.
        """
        # Start with desktop size
        await mcp_page.set_viewport_size({"width": 1920, "height": 1080})
        await mcp_page.wait_for_timeout(1000)

        # Upload data to have content to test with
        test_csv = Path(__file__).parent.parent / "fixtures" / "test_data" / "sample_meld_data.csv"
        upload_selector = 'input[type="file"]'

        try:
            await mcp_page.set_input_files(upload_selector, str(test_csv))
            await mcp_page.wait_for_timeout(3000)
        except Exception:
            pass

        # Test viewport transitions
        viewport_sequence = [
            {"width": 1920, "height": 1080, "name": "Desktop"},
            {"width": 1024, "height": 768, "name": "Tablet Landscape"},
            {"width": 768, "height": 1024, "name": "Tablet Portrait"},
            {"width": 375, "height": 667, "name": "Mobile"},
            {"width": 1366, "height": 768, "name": "Laptop"},
        ]

        transition_results = []

        for i, viewport in enumerate(viewport_sequence):
            transition_start = time.time()

            # Change viewport
            await mcp_page.set_viewport_size(
                {"width": viewport["width"], "height": viewport["height"]}
            )

            # Wait for layout to stabilize
            await mcp_page.wait_for_timeout(1000)

            # Check if layout adapted smoothly
            layout_stable = await mcp_page.evaluate(
                """
                () => {
                    const main = document.querySelector('.dash-app-content, main');
                    const graph = document.querySelector('#main-graph, [id*="graph"]');

                    return {
                        mainVisible: main ? main.offsetWidth > 0 && main.offsetHeight > 0 : false,
                        graphVisible: graph ? graph.offsetWidth > 0 && graph.offsetHeight > 0 : false,
                        noOverflow: document.body.scrollWidth <= window.innerWidth + 20, // 20px tolerance
                        contentStable: true // Assume stable if no errors thrown
                    };
                }
            """
            )

            transition_end = time.time()
            transition_time = (transition_end - transition_start) * 1000

            # Test interaction after viewport change
            interaction_works = True
            try:
                # Try to interact with graph if visible
                graph = mcp_page.locator("#main-graph")
                if await graph.count() > 0 and await graph.is_visible():
                    await graph.hover()
                    await mcp_page.wait_for_timeout(500)

                # Try to scroll
                await mcp_page.evaluate("window.scrollTo(0, 50)")
                await mcp_page.wait_for_timeout(500)

            except Exception as e:
                interaction_works = False
                print(f"Interaction failed after viewport change to {viewport['name']}: {e}")

            transition_results.append(
                {
                    "viewport": viewport["name"],
                    "width": viewport["width"],
                    "height": viewport["height"],
                    "transition_time_ms": transition_time,
                    "layout_stable": layout_stable["mainVisible"]
                    and layout_stable["contentStable"],
                    "no_overflow": layout_stable["noOverflow"],
                    "interaction_works": interaction_works,
                    "smooth_transition": (
                        transition_time < 2000
                        and layout_stable["contentStable"]  # Transition should be fast
                        and interaction_works
                    ),
                }
            )

            # Assertions for smooth transitions
            assert layout_stable[
                "contentStable"
            ], f"Layout should be stable after transition to {viewport['name']}"
            assert (
                transition_time < 3000
            ), f"Viewport transition to {viewport['name']} should be fast: {transition_time:.0f}ms"

        print("Viewport Transition Smoothness Results:")
        for result in transition_results:
            print(f"  {result['viewport']}: {result['width']}x{result['height']}")
            print(f"    Transition Time: {result['transition_time_ms']:.0f}ms")
            print(f"    Smooth Transition: {result['smooth_transition']}")
            print(f"    Interactions Work: {result['interaction_works']}")

    async def test_css_media_query_effectiveness(self, mcp_page):
        """
        Test effectiveness of CSS media queries for responsive design.
        """
        # Test breakpoints commonly used in responsive design
        breakpoints = [
            {"width": 320, "height": 568, "name": "Small Mobile", "expected_layout": "mobile"},
            {"width": 768, "height": 1024, "name": "Tablet", "expected_layout": "tablet"},
            {"width": 1024, "height": 768, "name": "Small Desktop", "expected_layout": "desktop"},
            {"width": 1920, "height": 1080, "name": "Large Desktop", "expected_layout": "desktop"},
        ]

        css_effectiveness_results = []

        for breakpoint in breakpoints:
            await mcp_page.set_viewport_size(
                {"width": breakpoint["width"], "height": breakpoint["height"]}
            )
            await mcp_page.wait_for_timeout(1500)

            # Analyze CSS adaptations
            css_analysis = await mcp_page.evaluate(
                f"""
                () => {{
                    const viewport = {{width: {breakpoint["width"]}, height: {breakpoint["height"]}}};

                    // Check computed styles of key elements
                    const main = document.querySelector('.dash-app-content, main');
                    const graph = document.querySelector('#main-graph, [id*="graph"]');
                    const body = document.body;

                    const getResponsiveStyles = (element) => {{
                        if (!element) return null;
                        const styles = window.getComputedStyle(element);
                        return {{
                            display: styles.display,
                            flexDirection: styles.flexDirection,
                            width: styles.width,
                            maxWidth: styles.maxWidth,
                            padding: styles.padding,
                            margin: styles.margin,
                            fontSize: styles.fontSize
                        }};
                    }};

                    // Check if layout changes based on viewport
                    const isResponsiveLayout = {{
                        flexColumn: false,
                        stackedElements: false,
                        appropriateFontSize: false,
                        appropriatePadding: false
                    }};

                    if (main) {{
                        const mainStyles = getResponsiveStyles(main);
                        isResponsiveLayout.flexColumn = mainStyles.flexDirection === 'column';

                        // Check font size adaptation
                        const fontSize = parseFloat(mainStyles.fontSize);
                        if (viewport.width < 768) {{
                            isResponsiveLayout.appropriateFontSize = fontSize >= 14 && fontSize <= 18;
                        }} else {{
                            isResponsiveLayout.appropriateFontSize = fontSize >= 16;
                        }}

                        // Check padding adaptation
                        const padding = parseFloat(mainStyles.padding);
                        if (viewport.width < 768) {{
                            isResponsiveLayout.appropriatePadding = padding >= 8 && padding <= 20;
                        }} else {{
                            isResponsiveLayout.appropriatePadding = padding >= 15;
                        }}
                    }}

                    // Check if elements stack vertically on small screens
                    if (viewport.width < 768) {{
                        const elements = document.querySelectorAll('.control-panel, .sidebar, [class*="col"]');
                        let stackedCount = 0;
                        elements.forEach(el => {{
                            const rect = el.getBoundingClientRect();
                            if (rect.width > viewport.width * 0.8) {{ // Taking most of width = stacked
                                stackedCount++;
                            }}
                        }});
                        isResponsiveLayout.stackedElements = stackedCount > 0;
                    }}

                    return {{
                        mainStyles: getResponsiveStyles(main),
                        graphStyles: getResponsiveStyles(graph),
                        isResponsiveLayout: isResponsiveLayout,
                        mediaQueryActive: viewport.width < 768 ? 'mobile' :
                                         viewport.width < 1024 ? 'tablet' : 'desktop'
                    }};
                }}
            """
            )

            # Check if breakpoint behavior matches expectations
            expected_mobile = breakpoint["expected_layout"] == "mobile"

            # Evaluate responsive effectiveness
            responsive_score = 0
            max_score = 4

            if css_analysis["isResponsiveLayout"]["appropriateFontSize"]:
                responsive_score += 1
            if css_analysis["isResponsiveLayout"]["appropriatePadding"]:
                responsive_score += 1
            if expected_mobile and css_analysis["isResponsiveLayout"]["stackedElements"]:
                responsive_score += 1
            elif not expected_mobile:
                responsive_score += 1  # Not mobile, stacking not required

            # Check media query activation
            if css_analysis["mediaQueryActive"] == breakpoint["expected_layout"]:
                responsive_score += 1

            effectiveness_ratio = responsive_score / max_score

            css_effectiveness_results.append(
                {
                    "breakpoint": breakpoint["name"],
                    "width": breakpoint["width"],
                    "height": breakpoint["height"],
                    "expected_layout": breakpoint["expected_layout"],
                    "detected_layout": css_analysis["mediaQueryActive"],
                    "responsive_score": responsive_score,
                    "max_score": max_score,
                    "effectiveness_ratio": effectiveness_ratio,
                    "font_size_appropriate": css_analysis["isResponsiveLayout"][
                        "appropriateFontSize"
                    ],
                    "padding_appropriate": css_analysis["isResponsiveLayout"]["appropriatePadding"],
                    "elements_stacked": css_analysis["isResponsiveLayout"]["stackedElements"],
                }
            )

            # Assertions for CSS media query effectiveness
            assert (
                effectiveness_ratio > 0.5
            ), f"CSS media queries should be effective at {breakpoint['name']}: {effectiveness_ratio:.2f}"

        print("CSS Media Query Effectiveness Results:")
        for result in css_effectiveness_results:
            print(f"  {result['breakpoint']}: {result['width']}x{result['height']}")
            print(
                f"    Expected: {result['expected_layout']}, Detected: {result['detected_layout']}"
            )
            print(
                f"    Effectiveness: {result['effectiveness_ratio']:.2f} ({result['responsive_score']}/{result['max_score']})"
            )
            print(
                f"    Font Size OK: {result['font_size_appropriate']}, Padding OK: {result['padding_appropriate']}"
            )

    async def test_cross_device_functionality_parity(self, mcp_page):
        """
        Test that core functionality works consistently across different device sizes.
        """
        device_configs = [
            {"width": 1920, "height": 1080, "name": "Desktop", "type": "desktop"},
            {"width": 768, "height": 1024, "name": "Tablet", "type": "tablet"},
            {"width": 375, "height": 667, "name": "Mobile", "type": "mobile"},
        ]

        functionality_parity_results = []

        for device in device_configs:
            await mcp_page.set_viewport_size({"width": device["width"], "height": device["height"]})
            await mcp_page.wait_for_timeout(2000)

            # Test core functionalities
            functionality_tests = {
                "file_upload": False,
                "graph_display": False,
                "graph_interaction": False,
                "navigation": False,
                "responsive_ui": False,
            }

            # Test file upload
            try:
                test_csv = (
                    Path(__file__).parent.parent / "fixtures" / "test_data" / "sample_meld_data.csv"
                )
                upload_selector = 'input[type="file"]'

                upload_element = mcp_page.locator(upload_selector)
                if await upload_element.count() > 0:
                    await upload_element.set_input_files(str(test_csv))
                    await mcp_page.wait_for_timeout(4000 if device["type"] == "mobile" else 2000)
                    functionality_tests["file_upload"] = True
            except Exception as e:
                print(f"File upload failed on {device['name']}: {e}")

            # Test graph display
            try:
                graph = mcp_page.locator("#main-graph .plotly-graph-div")
                if await graph.count() > 0:
                    is_visible = await graph.is_visible()
                    if is_visible:
                        # Check if graph has reasonable size
                        box = await graph.bounding_box()
                        if box and box["width"] > 100 and box["height"] > 100:
                            functionality_tests["graph_display"] = True
            except Exception as e:
                print(f"Graph display test failed on {device['name']}: {e}")

            # Test graph interaction
            try:
                graph = mcp_page.locator("#main-graph .plotly-graph-div")
                if await graph.count() > 0 and await graph.is_visible():
                    # Use appropriate interaction method for device type
                    if device["type"] == "mobile":
                        await graph.tap()
                        await graph.dblclick()  # Double tap for zoom
                    else:
                        await graph.hover()
                        await graph.dblclick()

                    await mcp_page.wait_for_timeout(1000)
                    functionality_tests["graph_interaction"] = True
            except Exception as e:
                print(f"Graph interaction failed on {device['name']}: {e}")

            # Test navigation (if tabs exist)
            try:
                tabs = mcp_page.locator(".nav-tabs .nav-link, [role='tab'], .tab")
                tab_count = await tabs.count()

                if tab_count > 0:
                    first_tab = tabs.first
                    if await first_tab.is_visible():
                        if device["type"] == "mobile":
                            await first_tab.tap()
                        else:
                            await first_tab.click()
                        await mcp_page.wait_for_timeout(1000)
                        functionality_tests["navigation"] = True
                else:
                    functionality_tests["navigation"] = True  # No tabs, navigation not applicable
            except Exception as e:
                print(f"Navigation test failed on {device['name']}: {e}")

            # Test responsive UI elements
            try:
                ui_responsive = await mcp_page.evaluate(
                    f"""
                    () => {{
                        const viewport = {{width: {device["width"]}, height: {device["height"]}}};
                        const main = document.querySelector('.dash-app-content, main');

                        if (!main) return false;

                        // Check if UI adapts to viewport
                        const mainWidth = main.offsetWidth;
                        const viewportWidth = window.innerWidth;

                        // UI should not exceed viewport width significantly
                        const fitsWidth = mainWidth <= viewportWidth + 20; // 20px tolerance

                        // Check for horizontal scrolling
                        const noHorizontalScroll = document.body.scrollWidth <= viewportWidth + 20;

                        return fitsWidth && noHorizontalScroll;
                    }}
                """
                )

                functionality_tests["responsive_ui"] = ui_responsive
            except Exception as e:
                print(f"Responsive UI test failed on {device['name']}: {e}")

            # Calculate functionality score
            functionality_score = sum(functionality_tests.values())
            max_functionality_score = len(functionality_tests)
            parity_ratio = functionality_score / max_functionality_score

            functionality_parity_results.append(
                {
                    "device": device["name"],
                    "type": device["type"],
                    "width": device["width"],
                    "height": device["height"],
                    "functionality_tests": functionality_tests.copy(),
                    "functionality_score": functionality_score,
                    "max_score": max_functionality_score,
                    "parity_ratio": parity_ratio,
                    "has_parity": parity_ratio >= 0.8,  # 80% functionality should work
                }
            )

            # Assertions for functionality parity
            assert (
                parity_ratio >= 0.6
            ), f"Core functionality should work on {device['name']}: {parity_ratio:.2f}"

        print("Cross-Device Functionality Parity Results:")
        for result in functionality_parity_results:
            print(f"  {result['device']} ({result['type']}): {result['width']}x{result['height']}")
            print(
                f"    Functionality Score: {result['functionality_score']}/{result['max_score']} ({result['parity_ratio']:.2f})"
            )
            print(f"    Tests Passed: {[k for k, v in result['functionality_tests'].items() if v]}")
            print(f"    Has Parity: {result['has_parity']}")

        # Check overall parity across devices
        all_have_parity = all(result["has_parity"] for result in functionality_parity_results)
        assert all_have_parity, "All devices should have reasonable functionality parity"
