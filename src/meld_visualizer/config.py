# --- config.py ---

import json
import dash_bootstrap_components as dbc

# --- Theme Configuration ---
THEMES = {
    "Cerulean (Default)": dbc.themes.CERULEAN, "Cosmo": dbc.themes.COSMO,
    "Cyborg": dbc.themes.CYBORG, "Darkly": dbc.themes.DARKLY,
    "Flatly": dbc.themes.FLATLY, "Journal": dbc.themes.JOURNAL,
    "Litera": dbc.themes.LITERA, "Lumen": dbc.themes.LUMEN,
    "Lux": dbc.themes.LUX, "Materia": dbc.themes.MATERIA,
    "Minty": dbc.themes.MINTY, "Morph": dbc.themes.MORPH,
    "Pulse": dbc.themes.PULSE, "Quartz": dbc.themes.QUARTZ,
    "Sandstone": dbc.themes.SANDSTONE, "Simplex": dbc.themes.SIMPLEX,
    "Sketchy": dbc.themes.SKETCHY, "Slate": dbc.themes.SLATE,
    "Solar": dbc.themes.SOLAR, "Spacelab": dbc.themes.SPACELAB,
    "Superhero": dbc.themes.SUPERHERO, "United": dbc.themes.UNITED,
    "Vapor": dbc.themes.VAPOR, "Yeti": dbc.themes.YETI, "Zephyr": dbc.themes.ZEPHYR,
}

# Define styles for the DataTable based on theme
TABLE_STYLE_LIGHT = {
    'style_header': {'backgroundColor': 'white', 'fontWeight': 'bold'},
    'style_cell': {'textAlign': 'left'},
    'style_data': {'backgroundColor': 'white', 'color': 'black'},
}
TABLE_STYLE_DARK = {
    'style_header': {'backgroundColor': 'rgb(50, 50, 50)', 'fontWeight': 'bold', 'color': 'white'},
    'style_cell': {'textAlign': 'left', 'backgroundColor': 'rgb(70, 70, 70)', 'color': 'white', 'border': '1px solid grey'},
    'style_data': {'backgroundColor': 'rgb(70, 70, 70)', 'color': 'white'},
}

# --- Configuration Loading ---
def load_config():
    """
    Loads user configuration from config.json, merging it with defaults.
    Ensures that critical keys exist and assigns a dark/light plot template if not specified.
    """
    default_config = {
        "default_theme": "Cerulean (Default)", "plotly_template": "plotly_white",
        "graph_1_options": ["YPos", "ZPos", "SpinVel"], "graph_2_options": ["XPos", "ZPos", "SpinVel"],
        "plot_2d_y_options": ["XPos", "YPos", "ZPos"], "plot_2d_color_options": ["FRO", "ToolTemp"]
    }
    try:
        import os
        # Path from src/meld_visualizer/config.py to config/config.json
        # Go up 3 levels: config.py -> meld_visualizer -> src -> root, then down to config/
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', 'config.json')
        with open(config_path, 'r') as f:
            user_config = json.load(f)
        # Merge user config with defaults, user_config takes precedence
        final_config = {**default_config, **user_config}

        # Validate theme selection, fallback to default if invalid
        if final_config.get("default_theme") not in THEMES:
            final_config["default_theme"] = default_config["default_theme"]

        # Auto-select plotly template if not specified by user
        if "plotly_template" not in user_config:
            DARK_THEMES = ["Cyborg", "Darkly", "Slate", "Solar", "Superhero", "Vapor"]
            final_config['plotly_template'] = 'plotly_dark' if final_config['default_theme'] in DARK_THEMES else 'plotly_white'
        return final_config
    except (FileNotFoundError, json.JSONDecodeError):
        return default_config

# --- Global Constants ---
APP_CONFIG = load_config()
PLOTLY_TEMPLATE = APP_CONFIG.get("plotly_template", "plotly_white")
SCATTER_3D_HEIGHT = '80vh'