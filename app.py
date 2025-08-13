import os
from dash import Dash, html

def _build_layout(app):
    try:
        import layout as layout_mod
        if hasattr(layout_mod, "get_layout"):
            return layout_mod.get_layout(app)
        if hasattr(layout_mod, "layout"):
            return layout_mod.layout
    except Exception:
        pass
    return html.Div([html.H1("MELD Visualizer"), html.P("App layout placeholder")])

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
    app = Dash(__name__, suppress_callback_exceptions=True)
    app.layout = _build_layout(app)
    _register_callbacks(app)
    return app

app = create_app(testing=False)

if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8050"))
    debug = os.environ.get("DEBUG", "0") in ("1", "true", "True")
    app.run_server(host=host, port=port, debug=debug)
