import pytest
from dash.testing.application_runners import import_app
import time

# --- E2E Test Cases ---

def test_app_smoke_test(dash_duo):
    """
    Smoke test to ensure the app loads without crashing.
    """
    app = import_app("app")
    dash_duo.start_server(app)
    dash_duo.wait_for_page()
    assert dash_duo.find_element("#output-filename").text == "Please upload a CSV file to begin."

import base64

def test_file_upload_and_initial_state(dash_duo):
    """
    Tests file upload and the initial state of the UI after upload.
    """
    app = import_app("app")
    dash_duo.start_server(app)
    dash_duo.wait_for_page()

    # Read the sample CSV file and encode it in base64
    with open('CSV/20250707144618.csv', 'rb') as f:
        content_bytes = f.read()
    encoded = base64.b64encode(content_bytes).decode('utf-8')

    # Trigger the upload callback with the file content
    time.sleep(10)
    dash_duo.driver.execute_script(
        "window.dash_clientside.setProps("
        "    'upload-data',"
        "    {"
        "        'contents': 'data:text/csv;base64," + encoded + "',"
        "        'filename': '20250707144618.csv'"
        "    }"
        ")"
    )

    # Wait for the filename to be displayed
    dash_duo.wait_for_text_to_equal("#output-filename", "Current file: 20250707144618.csv (Imperial units detected and converted to mm)", timeout=15)

    # Assert that the radio buttons for graph 1 are populated
    dash_duo.wait_for_element("#radio-buttons-1 .form-check-input")
    radio_buttons_1 = dash_duo.find_elements("#radio-buttons-1 .form-check-input")
    assert len(radio_buttons_1) > 0

def test_tab_navigation(dash_duo):
    """
    Tests navigation between tabs.
    """
    app = import_app("app")
    dash_duo.start_server(app)
    dash_duo.wait_for_page()

    # Navigate to the '3D Volume Mesh' tab
    dash_duo.find_elements(".nav-tabs .nav-link")[6].click()
    time.sleep(10)

    # Assert that a key element of that tab's content becomes visible
    assert dash_duo.find_element("#generate-mesh-plot-button").is_displayed()
