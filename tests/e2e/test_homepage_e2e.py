import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@pytest.mark.e2e
def test_homepage_renders(chrome, server_url):
    chrome.get(server_url)
    wait = WebDriverWait(chrome, 15)
    wait.until(EC.title_contains("Volumetric Data Plotter"))
    assert "Volumetric Data Plotter" in chrome.title

    # upload element visible (header area)
    upload = wait.until(EC.presence_of_element_located((By.ID, "upload-data")))
    assert upload.is_displayed()
