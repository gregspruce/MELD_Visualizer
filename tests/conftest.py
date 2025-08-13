import os
import pytest

# Only set this here as a safety net; scripts/run_tests.sh already exports it.
os.environ.setdefault("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")

# Optional: only import selenium if E2E tests actually need it
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    _HAVE_SELENIUM = True
except Exception:
    _HAVE_SELENIUM = False


@pytest.fixture(scope="session")
def browser():
    """
    Headless Chrome fixture using Selenium 4's Selenium Manager (auto driver).
    Skips gracefully if selenium isn't installed.
    """
    if not _HAVE_SELENIUM:
        pytest.skip("Selenium not installed; skipping browser-based tests.")

    opts = Options()
    # Use the modern headless mode for stability
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1280,800")

    # If a custom chrome path is set, honor it
    chrome_bin = os.environ.get("CHROME_BIN")
    if chrome_bin:
        opts.binary_location = chrome_bin

    driver = webdriver.Chrome(options=opts)
    yield driver
    driver.quit()
