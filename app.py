import os
from threading import Timer
import webbrowser
from dash import Dash, html
import dash_bootstrap_components as dbc

APP_TITLE = "Volumetric Data Plotter"

def _resolve_external_stylesheets():
    """Return Bootstrap CSS for proper dbc styling.
    Reads config.APP_CONFIG['theme'] / THEMES mapping when present,
    falls back to dbc.themes.BOOTSTRAP.
    """
    theme = dbc.themes.BOOTSTRAP
    try:
        from config import APP_CONFIG, THEMES  # optional; present in this repo
        key = None
        if isinstance(APP_CONFIG, dict):
            key = APP_CONFIG.get("theme") or APP_CONFIG.get("bootstrap_theme")
        if key and isinstance(THEMES, dict) and key in THEMES:
            val = THEMES[key]
            if isinstance(val, str) and (val.startswith("http://") or val.startswith("https://")):
                theme = val
            else:
                theme = val or theme
        elif key and hasattr(dbc.themes, key):
            theme = getattr(dbc.themes, key)
    except Exception:
        pass
    return [theme]

def _build_layout(app):
    """Prefer layout.get_layout(app), then layout.create_layout(), then layout.layout."""
    try:
        import layout as layout_mod
        if hasattr(layout_mod, "get_layout"):
            return layout_mod.get_layout(app)
        if hasattr(layout_mod, "create_layout"):
            return layout_mod.create_layout()
        if hasattr(layout_mod, "layout"):
            return layout_mod.layout
    except Exception:
        pass
    return html.Div([html.H1(APP_TITLE), html.P("Fallback layout: layout.py not found or failed to load.")])

def _register_callbacks(app):
    try:
        import callbacks as callbacks_mod
        if hasattr(callbacks_mod, "register_callbacks"):
            callbacks_mod.register_callbacks(app)
        elif hasattr(callbacks_mod, "init_callbacks"):
            callbacks_mod.init_callbacks(app)
    except Exception:
        pass

def create_app(testing: bool = False) -> Dash:
    app = Dash(
        __name__,
        external_stylesheets=_resolve_external_stylesheets(),
        suppress_callback_exceptions=True,
        title=APP_TITLE,
    )
    app.layout = _build_layout(app)
    _register_callbacks(app)
    return app

# Module-level app
app = create_app(testing=False)

def open_browser():
    """Opens the default web browser to the Dash app's URL."""
    webbrowser.open_new("http://127.0.0.1:8050")

if __name__ == "__main__":
    # Bind ONLY to local interface
    host = "127.0.0.1"
    port = 8050
    debug = os.environ.get("DEBUG", "0") in ("1", "true", "True")
        # The Timer is used to delay opening the browser, ensuring the server has started.
    # The WERKZEUG check prevents the browser from opening twice in debug mode.
    if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        Timer(1, open_browser).start()
    app.run(host=host, port=port, debug=debug)

#to run with debug
#$env:DEBUG="1"
#python app.py
