import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


@pytest.mark.e2e
def test_homepage_renders(chrome, server_url):
    """
    A full E2E test for the home page.
    It verifies that the page title is correct and that the main layout
    (including the file upload component) is rendered.
    """
    chrome.get(server_url)
    wait = WebDriverWait(chrome, 10)

    # 1. Verify the page title is set correctly by the full app
    wait.until(EC.title_contains("Volumetric Data Plotter"))
    assert "Volumetric Data Plotter" in chrome.title, "Page title is incorrect."

    # 2. Verify a key component from layout.py is present
    upload_element = wait.until(EC.presence_of_element_located((By.ID, "upload-data")))
    assert upload_element.is_displayed(), "The file upload component should be visible."
