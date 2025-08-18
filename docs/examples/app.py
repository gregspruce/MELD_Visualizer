import os
from pathlib import Path
from dash import Dash, html
import dash_bootstrap_components as dbc

APP_TITLE = "Volumetric Data Plotter"

def _has_local_bootstrap() -> bool:
    here = Path(__file__).resolve().parent.parent  # repo root assumption
    return (here / "assets" / "bootstrap.min.css").exists()

def _resolve_external_stylesheets():
    # Prefer local asset if present (offline); otherwise use dbc theme/CDN
    if _has_local_bootstrap():
        return []
    theme = dbc.themes.BOOTSTRAP
    try:
        from config import APP_CONFIG, THEMES
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
    return html.Div([html.H1(APP_TITLE), html.P("Fallback layout.")])

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
    app = Dash(__name__, external_stylesheets=_resolve_external_stylesheets(),
               suppress_callback_exceptions=True, title=APP_TITLE)
    app.layout = _build_layout(app)
    _register_callbacks(app)
    return app

app = create_app(testing=False)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8050, debug=os.environ.get("DEBUG","0") in ("1","true","True"))
