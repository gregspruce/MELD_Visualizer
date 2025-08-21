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
        "plot_2d_y_options": ["XPos", "YPos", "ZPos"], "plot_2d_color_options": ["FRO", "ToolTemp"],
        "feedstock_type": "square", "feedstock_dimension_inches": 0.5
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

# Legacy constant for backward compatibility
SCATTER_3D_HEIGHT = '75vh'  # Updated from fixed 80vh for better desktop optimization

# Initialize current theme for the application
CURRENT_THEME = APP_CONFIG.get("default_theme", "Cerulean (Default)")

# Responsive plot configuration functions
def get_responsive_plot_style(plot_type='scatter_3d', viewport_width=1920):
    """
    Get responsive plot style based on viewport width and plot type.
    Optimized for desktop environments only.
    
    Args:
        plot_type (str): Type of plot ('scatter_3d', 'volume_mesh', etc.)
        viewport_width (int): Browser viewport width in pixels
    
    Returns:
        dict: Style configuration with responsive height and constraints
    """
    from .constants import RESPONSIVE_PLOT_CONFIG, PLOT_TYPE_MODIFIERS
    
    # Determine desktop category based on viewport width
    if viewport_width >= 1920:
        config = RESPONSIVE_PLOT_CONFIG['desktop_large']
    elif viewport_width >= 1440:
        config = RESPONSIVE_PLOT_CONFIG['desktop_medium']
    elif viewport_width >= 1280:
        config = RESPONSIVE_PLOT_CONFIG['desktop_small']
    else:
        config = RESPONSIVE_PLOT_CONFIG['desktop_compact']
    
    # Apply plot type modifier
    modifier = PLOT_TYPE_MODIFIERS.get(plot_type, 1.0)
    
    # Calculate responsive height with CSS calc for type-specific adjustments
    if modifier != 1.0:
        height = f"calc({config['height']} * {modifier})"
    else:
        height = config['height']
    
    return {
        'height': height,
        'minHeight': config['min_height'],
        'maxHeight': config['max_height'],
        'width': '100%',
        'resize': 'both',
        'overflow': 'hidden'
    }

def get_responsive_plotly_config(plot_type='scatter_3d'):
    """
    Get responsive Plotly figure configuration for desktop optimization.
    
    Args:
        plot_type (str): Type of plot for specific optimizations
    
    Returns:
        dict: Plotly config with responsive settings
    """
    base_config = {
        'responsive': True,
        'displayModeBar': True,
        'displaylogo': False,
        'modeBarButtonsToRemove': [
            'pan2d', 'select2d', 'lasso2d', 'autoScale2d'
        ] if plot_type == 'time_series_2d' else [],
        'doubleClick': 'reset+autosize',
        'scrollZoom': True
    }
    
    # 3D plot specific optimizations
    if plot_type in ['scatter_3d', 'volume_mesh', 'toolpath_3d', 'custom_3d', 'gcode_viz']:
        base_config.update({
            'modeBarButtonsToAdd': ['resetCameraDefault3d', 'resetCameraLastSave3d']
        })
    
    return base_config