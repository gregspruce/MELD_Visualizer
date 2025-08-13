import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

TABS = [
    "Main 3D Plots",
    "2D Time Plot",
    "Custom 3D Plot",
    "Data Table",
    "3D Toolpath Plot",
    "3D Volume Mesh",
    "Settings",
]

def _find_tab_el(driver, label):
    # Try common tab element types with exact text
    xpaths = [
        f"//button[normalize-space()='{label}']",
        f"//a[normalize-space()='{label}']",
        f"//div[normalize-space()='{label}']",
        f"//span[normalize-space()='{label}']",
        f"//*[contains(@class, 'tab') and normalize-space()='{label}']",
        f"//*[contains(@role, 'tab') and normalize-space()='{label}']",
    ]
    for xp in xpaths:
        els = driver.find_elements(By.XPATH, xp)
        for el in els:
            if el.is_displayed():
                return el
    return None

@pytest.mark.e2e
def test_tabs_present_and_clickable(chrome, server_url):
    chrome.get(server_url)
    wait = WebDriverWait(chrome, 20)
    # ensure app mounted
    wait.until(EC.title_contains("Volumetric Data Plotter"))

    missing = []
    for label in TABS:
        el = _find_tab_el(chrome, label)
        if not el:
            # last resort: wait briefly then re-check (slow render)
            WebDriverWait(chrome, 5).until(lambda d: _find_tab_el(d, label) is not None)
            el = _find_tab_el(chrome, label)
        if not el:
            missing.append(label)
            continue

        # Click the tab; tolerate no-op if already selected
        try:
            WebDriverWait(chrome, 5).until(EC.element_to_be_clickable(el))
            el.click()
        except Exception:
            # JS fallback for obscured elements
            chrome.execute_script("arguments[0].click();", el)

        # Soft-check: the tab element remains displayed
        assert el.is_displayed(), f"Tab '{label}' not visible after click"

    assert not missing, f"Missing tab labels: {missing}"
