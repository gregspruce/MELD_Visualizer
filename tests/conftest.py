import pytest
from selenium.webdriver.chrome.options import Options
import sys
import os
import uuid  # <-- Import the uuid library

# Add the project root to the path to allow imports from the 'app' module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# Set an environment variable to indicate that we are running via pytest
os.environ['RUNNING_VIA_PYTEST'] = 'true'

@pytest.hookimpl(tryfirst=True)
def pytest_setup_options():
    """
    Adds Chrome options for running in a headless/CI environment.
    """
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # --- THIS IS THE FIX ---
    # Create a UNIQUE user data directory for each test run to prevent session conflicts.
    # A static path causes "directory is already in use" errors in test runners.
    options.add_argument(f"--user-data-dir=/tmp/chrome-user-data-{uuid.uuid4()}")
    
    # Explicitly tell Selenium where to find the chromium binary.
    options.binary_location = "/usr/bin/chromium-browser"
    
    return options
