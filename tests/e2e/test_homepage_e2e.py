import pytest
from selenium.webdriver.common.by import By

@pytest.mark.e2e
def test_homepage_renders(chrome, server_url):
    chrome.get(server_url)
    # Dash root container is present in all apps
    root = chrome.find_element(By.ID, "_dash-app-content")
    assert root.is_displayed()
