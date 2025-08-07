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
    assert dash_duo.title == "Volumetric Data Plotter"
    assert dash_duo.find_element("#output-filename").text == "Please upload a CSV file to begin."

def test_file_upload_and_initial_state(dash_duo):
    """
    Tests file upload and the initial state of the UI after upload.
    """
    app = import_app("app")
    dash_duo.start_server(app)
    dash_duo.wait_for_page()

    # Get the path to the sample CSV file
    csv_path = 'CSV/20250707144618.csv'

    # Set the value of the dcc.Upload component
    dash_duo.upload_file("#upload-data", csv_path)

    # Wait for the filename to be displayed
    time.sleep(2) # Allow time for callbacks to fire

    # Assert that the filename is displayed
    assert "20250707144618.csv" in dash_duo.find_element("#output-filename").text

    # Assert that the radio buttons for graph 1 are populated
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
    time.sleep(1) # Allow time for tab content to render

    # Assert that a key element of that tab's content becomes visible
    assert dash_duo.find_element("#generate-mesh-plot-button").is_displayed()
