import pytest
from selenium.webdriver.chrome.options import Options
import sys
import os

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
    # Using a unique user data dir for each test run should prevent session conflicts
    options.add_argument("--user-data-dir=/tmp/chrome-user-data")
    return options
