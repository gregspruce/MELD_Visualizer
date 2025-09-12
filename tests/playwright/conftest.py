"""
Playwright E2E Test Configuration for MELD Visualizer
Configures pytest environment for comprehensive E2E testing with MCP integration.
"""

import asyncio
import os
import sys
from pathlib import Path

import pytest

from playwright.async_api import async_playwright

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

# Configuration
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8050")
HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"
BROWSER_TYPE = os.getenv("BROWSER", "chromium")
SLOW_MO = int(os.getenv("SLOW_MO", "0"))
VIDEO_MODE = os.getenv("VIDEO", "retain-on-failure")
SCREENSHOT_MODE = os.getenv("SCREENSHOT", "only-on-failure")


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def browser_context():
    """Create a browser context for the test session."""
    async with async_playwright() as p:
        browser_type = getattr(p, BROWSER_TYPE)

        browser = await browser_type.launch(
            headless=HEADLESS,
            slow_mo=SLOW_MO,
            args=[
                "--disable-web-security",
                "--disable-features=VizDisplayCompositor",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
            ],
        )

        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            ignore_https_errors=True,
            record_video_dir="tests/reports/videos" if VIDEO_MODE != "off" else None,
            record_video_size={"width": 1280, "height": 720},
        )

        yield context

        await context.close()
        await browser.close()


@pytest.fixture
async def page(browser_context):
    """Create a new page for each test."""
    page = await browser_context.new_page()

    # Configure page settings
    await page.set_extra_http_headers({"User-Agent": "MELD-Visualizer-E2E-Test/1.0 (Playwright)"})

    # Set up error tracking
    await page.evaluate(
        """
        () => {
            window.console_errors = [];
            const originalError = console.error;
            console.error = function(...args) {
                window.console_errors.push({
                    message: args.join(' '),
                    timestamp: Date.now(),
                    stack: new Error().stack
                });
                originalError.apply(console, args);
            };

            window.addEventListener('error', (e) => {
                window.console_errors.push({
                    message: e.message,
                    filename: e.filename,
                    lineno: e.lineno,
                    colno: e.colno,
                    timestamp: Date.now()
                });
            });

            window.addEventListener('unhandledrejection', (e) => {
                window.console_errors.push({
                    message: 'Unhandled Promise Rejection: ' + e.reason,
                    timestamp: Date.now()
                });
            });
        }
    """
    )

    yield page

    # Take screenshot on failure
    if SCREENSHOT_MODE in ["always", "only-on-failure"]:
        test_info = getattr(page, "_test_info", None)
        if test_info and hasattr(test_info, "outcome") and test_info.outcome == "failed":
            screenshot_dir = Path("tests/reports/screenshots")
            screenshot_dir.mkdir(parents=True, exist_ok=True)
            await page.screenshot(path=str(screenshot_dir / f"failure_{int(time.time())}.png"))

    await page.close()


@pytest.fixture
def base_url():
    """Base URL for the application."""
    return BASE_URL


@pytest.fixture
def test_data_dir():
    """Directory containing test data files."""
    return Path(__file__).parent / "fixtures" / "test_data"


@pytest.fixture
def sample_csv(test_data_dir):
    """Path to sample CSV test data."""
    return test_data_dir / "sample_meld_data.csv"


@pytest.fixture
def invalid_csv(test_data_dir):
    """Path to invalid CSV test data."""
    return test_data_dir / "invalid_meld_data.csv"


@pytest.fixture
def minimal_csv(test_data_dir):
    """Path to minimal CSV test data."""
    return test_data_dir / "minimal_meld_data.csv"


# Test configuration markers
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line("markers", "smoke: mark test as smoke test")
    config.addinivalue_line("markers", "regression: mark test as regression test")
    config.addinivalue_line("markers", "performance: mark test as performance test")
    config.addinivalue_line("markers", "visual: mark test as visual regression test")
    config.addinivalue_line("markers", "mobile: mark test as mobile-specific test")
    config.addinivalue_line("markers", "desktop: mark test as desktop-specific test")
    config.addinivalue_line("markers", "slow: mark test as slow-running")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names."""
    for item in items:
        # Add smoke marker for critical tests
        if "critical" in item.name or "smoke" in item.name:
            item.add_marker(pytest.mark.smoke)

        # Add performance marker for performance tests
        if "performance" in item.name or "benchmark" in item.name:
            item.add_marker(pytest.mark.performance)

        # Add visual marker for visual tests
        if "visual" in item.name or "screenshot" in item.name:
            item.add_marker(pytest.mark.visual)

        # Add mobile marker for responsive/mobile tests
        if "mobile" in item.name or "responsive" in item.name:
            item.add_marker(pytest.mark.mobile)

        # Add slow marker for tests that might take longer
        if any(slow_test in item.name for slow_test in ["error_scenarios", "concurrent", "stress"]):
            item.add_marker(pytest.mark.slow)


@pytest.fixture(autouse=True)
async def check_server_running(page):
    """Ensure MELD Visualizer server is running before tests."""
    try:
        await page.goto(BASE_URL, wait_until="domcontentloaded", timeout=10000)
    except Exception as e:
        pytest.fail(
            f"MELD Visualizer server is not running at {BASE_URL}. "
            f"Please start the server with: python -m meld_visualizer\n"
            f"Error: {e}"
        )


@pytest.fixture
async def app_ready(page):
    """Fixture that ensures the application is ready for testing."""
    await page.goto(BASE_URL)
    await page.wait_for_load_state("networkidle")
    await page.wait_for_selector(".dash-app-content", timeout=30000)

    # Wait for any initial loading to complete
    try:
        await page.wait_for_selector(".dash-spinner", state="detached", timeout=5000)
    except Exception:
        pass  # No spinner found, which is fine

    return page


# Utility functions for test helpers
class E2ETestHelpers:
    """Helper utilities for E2E tests."""

    @staticmethod
    async def wait_for_graph_ready(page, graph_id="main-graph", timeout=15000):
        """Wait for a Plotly graph to be ready."""
        await page.wait_for_selector(f"#{graph_id} .plotly-graph-div", timeout=timeout)

        # Wait for graph data
        await page.wait_for_function(
            f"""
            () => {{
                const graph = document.querySelector('#{graph_id}');
                return graph && graph.data && graph.data.length > 0;
            }}
        """,
            timeout=timeout,
        )

    @staticmethod
    async def upload_test_file(page, file_path, selector='input[type="file"]'):
        """Upload a test file."""
        await page.set_input_files(selector, str(file_path))

    @staticmethod
    async def get_console_errors(page):
        """Get console errors from the page."""
        return await page.evaluate("window.console_errors || []")

    @staticmethod
    async def clear_console_errors(page):
        """Clear console errors."""
        await page.evaluate("window.console_errors = []")

    @staticmethod
    async def wait_for_no_loading(page, timeout=10000):
        """Wait for all loading indicators to disappear."""
        loading_selectors = [
            ".dash-spinner",
            ".loading-overlay",
            '[data-loading="true"]',
            ".loading-spinner",
        ]

        for selector in loading_selectors:
            try:
                await page.wait_for_selector(
                    selector, state="detached", timeout=timeout // len(loading_selectors)
                )
            except Exception:
                pass  # Selector might not exist


@pytest.fixture
def e2e_helpers():
    """Fixture providing E2E test helper utilities."""
    return E2ETestHelpers


# Async test timeout configuration
@pytest.fixture(autouse=True)
def configure_async_timeout():
    """Configure default timeout for async tests."""
    # This can be overridden per test if needed
    return 60  # 60 seconds default timeout


# Performance test configuration
@pytest.fixture
def performance_config():
    """Configuration for performance tests."""
    return {
        "page_load_timeout": 5000,  # 5 seconds
        "csv_processing_timeout": 10000,  # 10 seconds
        "graph_render_timeout": 3000,  # 3 seconds
        "interaction_timeout": 1000,  # 1 second
        "memory_threshold_mb": 150,  # 150 MB
    }


# Visual regression test configuration
@pytest.fixture
def visual_config():
    """Configuration for visual regression tests."""
    return {
        "screenshot_dir": Path("tests/reports/visual_regression"),
        "threshold": 0.1,  # 10% difference threshold
        "pixel_threshold": 100,  # 100 pixel difference threshold
    }


# Mobile test configuration
@pytest.fixture
def mobile_config():
    """Configuration for mobile tests."""
    return {
        "viewports": [
            {"width": 375, "height": 667, "name": "iPhone SE"},
            {"width": 390, "height": 844, "name": "iPhone 12"},
            {"width": 768, "height": 1024, "name": "iPad"},
        ],
        "touch_timeout": 2000,
        "min_touch_target_size": 44,  # pixels
    }


# Error handling configuration
@pytest.fixture
def error_config():
    """Configuration for error handling tests."""
    return {
        "max_console_errors": 10,
        "error_recovery_timeout": 5000,
        "memory_leak_threshold": 200,  # MB
        "concurrent_error_count": 20,
    }


def pytest_runtest_makereport(item, call):
    """Generate test reports with additional information."""
    if call.when == "call":
        # Add test timing information
        if hasattr(item, "start_time"):
            duration = call.stop - call.start
            item.duration = duration

        # Add test outcome to page object for screenshot handling
        if hasattr(item, "funcargs") and "page" in item.funcargs:
            page = item.funcargs["page"]
            page._test_info = type(
                "TestInfo", (), {"outcome": "passed" if call.excinfo is None else "failed"}
            )()


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment and create necessary directories."""
    # Create report directories
    report_dirs = [
        "tests/reports",
        "tests/reports/screenshots",
        "tests/reports/videos",
        "tests/reports/visual_regression/baselines",
        "tests/reports/visual_regression/current",
        "tests/reports/performance",
    ]

    for report_dir in report_dirs:
        Path(report_dir).mkdir(parents=True, exist_ok=True)

    yield

    # Cleanup after all tests
    print("\nE2E Test Suite completed. Reports available in tests/reports/")
