# --- app.py ---

import os
from threading import Timer
import webbrowser
from dash import Dash

# Import app configuration and layout creation function
from config import APP_CONFIG, THEMES
from layout import create_layout

# --- App Initialization ---
# This is the central Dash app instance. It's imported by callbacks.py.
app = Dash(
    __name__,
    external_stylesheets=[THEMES.get(APP_CONFIG['default_theme'])],
    suppress_callback_exceptions=True,
    prevent_initial_callbacks=True
)
# Set the app title
app.title = "Volumetric Data Plotter"

# Assign the layout to the app
# The function create_layout() is called from layout.py
app.layout = create_layout()

# This import is what registers the callbacks.
# It must be done AFTER the app is initialized and the layout is set.
import callbacks

# --- Main Execution ---
def open_browser():
    """Opens the default web browser to the Dash app's URL."""
    webbrowser.open_new("http://127.0.0.1:8050")

if __name__ == '__main__':
    # The Timer is used to delay opening the browser, ensuring the server has started.
    # The WERKZEUG check prevents the browser from opening twice in debug mode.
    if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        Timer(1, open_browser).start()

    # Run the Dash app server
    app.run(debug=True, port=8050)