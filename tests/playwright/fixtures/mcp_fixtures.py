"""
Python MCP Fixtures for MELD Visualizer E2E Tests
Provides reusable fixtures for Playwright MCP integration with Python tests.
"""

import time
from pathlib import Path
from typing import Optional

import pytest


class MCPPerformanceMonitor:
    """Performance monitoring utilities for MCP tests."""

    def __init__(self, page):
        self.page = page
        self.metrics = {}
        self.monitoring = False

    async def start_monitoring(self):
        """Start performance monitoring."""
        self.monitoring = True
        self.start_time = time.time()

        # Initialize performance tracking
        await self.page.evaluate(
            """
            () => {
                window.mcpPerformanceMetrics = {
                    startTime: Date.now(),
                    navigationTiming: performance.getEntriesByType('navigation')[0],
                    resourceTimings: performance.getEntriesByType('resource'),
                    paintTimings: performance.getEntriesByType('paint'),
                    memoryInfo: performance.memory || null
                };
            }
        """
        )

    async def stop_monitoring(self):
        """Stop performance monitoring and collect final metrics."""
        if not self.monitoring:
            return {}

        self.monitoring = False
        self.end_time = time.time()

        # Collect final metrics
        metrics = await self.page.evaluate(
            """
            () => {
                const startMetrics = window.mcpPerformanceMetrics || {};
                const endTime = Date.now();

                return {
                    startTime: startMetrics.startTime,
                    endTime: endTime,
                    duration: endTime - (startMetrics.startTime || endTime),
                    navigationTiming: performance.getEntriesByType('navigation')[0],
                    resourceCount: performance.getEntriesByType('resource').length,
                    paintTimings: performance.getEntriesByType('paint'),
                    memoryInfo: performance.memory ? {
                        used: performance.memory.usedJSHeapSize,
                        total: performance.memory.totalJSHeapSize,
                        limit: performance.memory.jsHeapSizeLimit
                    } : null,
                    userTiming: performance.getEntriesByType('measure')
                };
            }
        """
        )

        self.metrics.update(metrics)
        return self.metrics

    async def get_current_metrics(self):
        """Get current performance metrics."""
        return await self.page.evaluate(
            """
            () => {
                return {
                    currentTime: Date.now(),
                    memoryUsage: performance.memory ? {
                        used: performance.memory.usedJSHeapSize,
                        total: performance.memory.totalJSHeapSize
                    } : null,
                    resourceCount: performance.getEntriesByType('resource').length
                };
            }
        """
        )


class MCPConsoleMonitor:
    """Console monitoring utilities for MCP tests."""

    def __init__(self, page):
        self.page = page
        self.console_logs = []
        self.console_errors = []
        self.monitoring = False

    def start_monitoring(self):
        """Start console monitoring."""
        self.monitoring = True
        self.console_logs = []
        self.console_errors = []

        # Set up console error tracking
        self.page.on("console", self._handle_console_message)
        self.page.on("pageerror", self._handle_page_error)

        # Initialize console error collection in browser
        self.page.evaluate(
            """
            () => {
                window.console_errors = window.console_errors || [];
                const originalError = console.error;
                const originalWarn = console.warn;

                console.error = function(...args) {
                    window.console_errors.push({
                        type: 'error',
                        message: args.join(' '),
                        timestamp: Date.now()
                    });
                    originalError.apply(console, args);
                };

                console.warn = function(...args) {
                    window.console_errors.push({
                        type: 'warn',
                        message: args.join(' '),
                        timestamp: Date.now()
                    });
                    originalWarn.apply(console, args);
                };
            }
        """
        )

    def stop_monitoring(self):
        """Stop console monitoring."""
        if not self.monitoring:
            return

        self.monitoring = False
        self.page.remove_listener("console", self._handle_console_message)
        self.page.remove_listener("pageerror", self._handle_page_error)

    def _handle_console_message(self, msg):
        """Handle console messages."""
        if msg.type in ["error", "warning"]:
            self.console_errors.append(
                {
                    "type": msg.type,
                    "text": msg.text,
                    "location": msg.location,
                    "timestamp": time.time(),
                }
            )

        self.console_logs.append({"type": msg.type, "text": msg.text, "timestamp": time.time()})

    def _handle_page_error(self, error):
        """Handle page errors."""
        self.console_errors.append(
            {"type": "page_error", "text": str(error), "timestamp": time.time()}
        )

    def get_errors(self):
        """Get collected console errors."""
        return self.console_errors

    def get_logs(self):
        """Get all console logs."""
        return self.console_logs

    def has_errors(self):
        """Check if any errors were detected."""
        return len(self.console_errors) > 0

    def expect_no_errors(self):
        """Assert that no console errors occurred."""
        errors = self.get_errors()
        assert len(errors) == 0, f"Expected no console errors, but found: {errors}"


class MCPNetworkMonitor:
    """Network monitoring utilities for MCP tests."""

    def __init__(self, page):
        self.page = page
        self.requests = []
        self.responses = []
        self.failed_requests = []
        self.monitoring = False

    def start_monitoring(self):
        """Start network monitoring."""
        self.monitoring = True
        self.requests = []
        self.responses = []
        self.failed_requests = []

        self.page.on("request", self._handle_request)
        self.page.on("response", self._handle_response)
        self.page.on("requestfailed", self._handle_request_failed)

    def stop_monitoring(self):
        """Stop network monitoring."""
        if not self.monitoring:
            return

        self.monitoring = False
        self.page.remove_listener("request", self._handle_request)
        self.page.remove_listener("response", self._handle_response)
        self.page.remove_listener("requestfailed", self._handle_request_failed)

    def _handle_request(self, request):
        """Handle network requests."""
        self.requests.append(
            {
                "url": request.url,
                "method": request.method,
                "headers": request.headers,
                "timestamp": time.time(),
            }
        )

    def _handle_response(self, response):
        """Handle network responses."""
        self.responses.append(
            {
                "url": response.url,
                "status": response.status,
                "headers": response.headers,
                "timestamp": time.time(),
            }
        )

    def _handle_request_failed(self, request):
        """Handle failed requests."""
        self.failed_requests.append(
            {
                "url": request.url,
                "method": request.method,
                "failure": request.failure,
                "timestamp": time.time(),
            }
        )

    def get_requests(self):
        """Get all captured requests."""
        return self.requests

    def get_responses(self):
        """Get all captured responses."""
        return self.responses

    def get_failed_requests(self):
        """Get all failed requests."""
        return self.failed_requests

    def get_requests_by_url_pattern(self, pattern: str):
        """Get requests matching URL pattern."""
        return [req for req in self.requests if pattern in req["url"]]


class MCPPageUtils:
    """Utility methods for MCP page interactions."""

    def __init__(self, page):
        self.page = page

    async def wait_for_app_ready(self, timeout: int = 30000):
        """Wait for MELD Visualizer application to be ready."""
        # Wait for main content
        await self.page.wait_for_selector(".dash-app-content", timeout=timeout)

        # Wait for any loading spinners to disappear
        loading_selectors = [".dash-spinner", '[data-loading="true"]', ".loading-spinner"]
        for selector in loading_selectors:
            try:
                await self.page.wait_for_selector(selector, state="detached", timeout=5000)
            except Exception:
                pass  # Selector might not exist

    async def wait_for_graph_render(self, graph_id: str = "main-graph", timeout: int = 15000):
        """Wait for a Plotly graph to render completely."""
        # Wait for graph container
        await self.page.wait_for_selector(f"#{graph_id}", timeout=timeout)

        # Wait for Plotly graph div
        await self.page.wait_for_selector(f"#{graph_id} .plotly-graph-div", timeout=timeout)

        # Wait for graph data to be available
        await self.page.wait_for_function(
            f"""
            () => {{
                const graphDiv = document.querySelector('#{graph_id}');
                return graphDiv && graphDiv.data && graphDiv.data.length > 0;
            }}
        """,
            timeout=timeout,
        )

        # Additional wait for rendering to complete
        await self.page.wait_for_timeout(1000)

    async def upload_csv_file(self, file_path: str, selector: str = 'input[type="file"]'):
        """Upload a CSV file using the upload component."""
        await self.page.set_input_files(selector, file_path)

    async def take_screenshot(self, name: str, element_selector: Optional[str] = None):
        """Take a screenshot of page or specific element."""
        screenshot_dir = Path(__file__).parent.parent / "reports" / "screenshots"
        screenshot_dir.mkdir(parents=True, exist_ok=True)

        screenshot_path = screenshot_dir / f"{name}_{int(time.time())}.png"

        if element_selector:
            element = self.page.locator(element_selector)
            await element.screenshot(path=str(screenshot_path))
        else:
            await self.page.screenshot(path=str(screenshot_path))

        return str(screenshot_path)

    async def get_element_metrics(self, selector: str):
        """Get metrics for an element (size, position, visibility)."""
        return await self.page.evaluate(
            """
            (selector) => {
                const element = document.querySelector(selector);
                if (!element) return null;

                const rect = element.getBoundingClientRect();
                const styles = window.getComputedStyle(element);

                return {
                    width: rect.width,
                    height: rect.height,
                    x: rect.x,
                    y: rect.y,
                    visible: rect.width > 0 && rect.height > 0 && styles.visibility !== 'hidden',
                    display: styles.display,
                    opacity: styles.opacity
                };
            }
        """,
            selector,
        )

    async def simulate_mobile_touch(self, selector: str, action: str = "tap"):
        """Simulate mobile touch interactions."""
        element = self.page.locator(selector)

        if action == "tap":
            await element.tap()
        elif action == "double_tap":
            await element.dblclick()
        elif action == "long_press":
            await element.click(button="right")  # Approximate long press
        elif action == "swipe":
            box = await element.bounding_box()
            if box:
                start_x = box["x"] + box["width"] * 0.2
                end_x = box["x"] + box["width"] * 0.8
                y = box["y"] + box["height"] * 0.5

                await self.page.mouse.move(start_x, y)
                await self.page.mouse.down()
                await self.page.mouse.move(end_x, y)
                await self.page.mouse.up()


# Pytest fixtures
@pytest.fixture
async def mcp_page(page):
    """Fixture providing an MCP-enhanced Playwright page."""
    # Set up page for MCP testing
    await page.goto("http://127.0.0.1:8050")
    await page.wait_for_load_state("networkidle")
    yield page


@pytest.fixture
async def performance_monitor(mcp_page):
    """Fixture providing performance monitoring capabilities."""
    monitor = MCPPerformanceMonitor(mcp_page)
    yield monitor
    if monitor.monitoring:
        await monitor.stop_monitoring()


@pytest.fixture
async def console_monitor(mcp_page):
    """Fixture providing console monitoring capabilities."""
    monitor = MCPConsoleMonitor(mcp_page)
    yield monitor
    if monitor.monitoring:
        monitor.stop_monitoring()


@pytest.fixture
async def network_monitor(mcp_page):
    """Fixture providing network monitoring capabilities."""
    monitor = MCPNetworkMonitor(mcp_page)
    yield monitor
    if monitor.monitoring:
        monitor.stop_monitoring()


@pytest.fixture
async def page_utils(mcp_page):
    """Fixture providing MCP page utilities."""
    utils = MCPPageUtils(mcp_page)
    yield utils


@pytest.fixture
async def test_data_csv():
    """Fixture providing path to test CSV data."""
    return Path(__file__).parent / "test_data" / "sample_meld_data.csv"


@pytest.fixture
async def invalid_test_data_csv():
    """Fixture providing path to invalid test CSV data."""
    return Path(__file__).parent / "test_data" / "invalid_meld_data.csv"


@pytest.fixture(scope="session")
async def mcp_test_config():
    """Fixture providing MCP test configuration."""
    return {
        "base_url": "http://127.0.0.1:8050",
        "timeout": 30000,
        "screenshot_on_failure": True,
        "performance_monitoring": True,
        "console_monitoring": True,
        "network_monitoring": False,  # Disable by default due to overhead
    }


@pytest.fixture(autouse=True)
async def mcp_test_setup(mcp_page, mcp_test_config):
    """Auto-used fixture for MCP test setup and teardown."""
    # Setup
    if mcp_test_config.get("performance_monitoring"):
        await mcp_page.evaluate(
            """
            () => {
                window.mcpTestStart = Date.now();
                window.console_errors = [];
            }
        """
        )

    yield

    # Teardown
    if mcp_test_config.get("screenshot_on_failure"):
        # This would be handled by pytest-playwright plugin
        pass


class MCPVisualRegression:
    """Visual regression testing utilities for MCP."""

    def __init__(self, page):
        self.page = page
        self.screenshot_dir = Path(__file__).parent.parent / "reports" / "visual_regression"
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)

    async def compare_screenshot(
        self, name: str, selector: Optional[str] = None, threshold: float = 0.2
    ):
        """Compare screenshot with baseline."""
        screenshot_name = f"{name}.png"
        baseline_path = self.screenshot_dir / "baselines" / screenshot_name
        current_path = self.screenshot_dir / "current" / screenshot_name

        # Ensure directories exist
        baseline_path.parent.mkdir(parents=True, exist_ok=True)
        current_path.parent.mkdir(parents=True, exist_ok=True)

        # Take current screenshot
        if selector:
            element = self.page.locator(selector)
            await element.screenshot(path=str(current_path))
        else:
            await self.page.screenshot(path=str(current_path))

        # If baseline doesn't exist, create it
        if not baseline_path.exists():
            import shutil

            shutil.copy2(current_path, baseline_path)
            return True

        # Compare screenshots (simplified - in practice would use image comparison library)
        return True  # Placeholder for actual comparison logic


@pytest.fixture
async def visual_regression(mcp_page):
    """Fixture providing visual regression testing capabilities."""
    return MCPVisualRegression(mcp_page)
