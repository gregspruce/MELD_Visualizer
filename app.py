import os
from dash import Dash, html

APP_TITLE = "Volumetric Data Plotter"

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
    return html.Div([html.H1(APP_TITLE), html.P("Fallback layout (layout.py failed to load).")])

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
    app = Dash(__name__, suppress_callback_exceptions=True, title=APP_TITLE)
    app.layout = _build_layout(app)
    _register_callbacks(app)
    return app

# Module-level app
app = create_app(testing=False)

if __name__ == "__main__":
    # Bind ONLY to local interface, per request
    host = "127.0.0.1"
    port = 8050
    debug = os.environ.get("DEBUG", "0") in ("1", "true", "True")
    app.run(host=host, port=port, debug=debug)
