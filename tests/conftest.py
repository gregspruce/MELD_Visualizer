import pytest
from selenium.webdriver.chrome.options import Options
import sys
import os
import uuid
import chromedriver_autoinstaller

# Add the project root to the path to allow imports from the 'app' module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# Set an environment variable to indicate that we are running via pytest
os.environ['RUNNING_VIA_PYTEST'] = 'true'

# Automatically find the installed Chrome and download the correct chromedriver
chromedriver_autoinstaller.install()

@pytest.hookimpl(tryfirst=True)
def pytest_setup_options():
    """
    Adds Chrome options for running in a headless/CI environment.
    """
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # Explicitly point to the Google Chrome binary (NOT chromium)
    options.binary_location = "/usr/bin/google-chrome"
    
    # Keep the unique user data directory to prevent test conflicts
    options.add_argument(f"--user-data-dir=/tmp/chrome-user-data-{uuid.uuid4()}")
    
    return options
