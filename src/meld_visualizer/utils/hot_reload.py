"""
Hot-reload utilities for dynamic theme and configuration updates.
Enables theme and config changes without app restart.
"""

import logging
from dash import html, dcc, Input, Output, State, callback, clientside_callback, ClientsideFunction
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import json
import os

from ..config import THEMES, load_config

logger = logging.getLogger(__name__)


def get_theme_css_url(theme_name):
    """Get CSS URL for a theme name."""
    if theme_name in THEMES:
        theme_url = THEMES[theme_name]
        if isinstance(theme_url, str) and (theme_url.startswith("http://") or theme_url.startswith("https://")):
            return theme_url
        # For dbc theme constants, extract the URL
        return theme_url
    return dbc.themes.BOOTSTRAP


def create_theme_injection_component():
    """Create components needed for dynamic theme injection."""
    return html.Div([
        # Hidden div to store current theme
        dcc.Store(id='current-theme-store', data=''),
        # Dynamic CSS link element
        html.Link(id='dynamic-theme-link', rel='stylesheet', href=''),
        # Config reload trigger
        dcc.Store(id='config-reload-trigger', data=0),
        # Updated config store
        dcc.Store(id='hot-config-store', data={})
    ])


def register_hot_reload_callbacks(app):
    """Register callbacks for hot-reloading themes and config."""
    
    @callback(
        Output('dynamic-theme-link', 'href', allow_duplicate=True),
        Output('current-theme-store', 'data', allow_duplicate=True),
        Input('current-theme-store', 'id'),
        prevent_initial_call='initial_duplicate'
    )
    def initialize_theme_on_startup(_):
        """Initialize theme on app startup."""
        from ..config import APP_CONFIG
        current_theme = APP_CONFIG.get("default_theme", "Cerulean (Default)")
        theme_url = get_theme_css_url(current_theme)
        logger.info(f"Initializing theme on startup: {current_theme}")
        return theme_url, current_theme
    
    @callback(
        Output('dynamic-theme-link', 'href'),
        Output('current-theme-store', 'data'),
        Input('config-theme-dropdown', 'value'),
        State('current-theme-store', 'data'),
        prevent_initial_call=True
    )
    def update_theme_dynamically(new_theme, current_theme):
        """Update theme CSS dynamically without restart."""
        if not new_theme or new_theme == current_theme:
            raise PreventUpdate
        
        theme_url = get_theme_css_url(new_theme)
        logger.info(f"Switching theme from {current_theme} to {new_theme}")
        
        return theme_url, new_theme
    
    @callback(
        Output('config-reload-trigger', 'data'),
        Output('hot-config-store', 'data'),
        Input('save-config-button', 'n_clicks'),
        State('config-reload-trigger', 'data'),
        prevent_initial_call=True
    )
    def trigger_config_reload(n_clicks, current_trigger):
        """Reload configuration after save without restart."""
        if not n_clicks:
            raise PreventUpdate
        
        # Reload config from file
        new_config = load_config()
        logger.info("Configuration reloaded for hot-update")
        
        return current_trigger + 1, new_config
    
    @callback(
        Output('radio-buttons-1', 'options'),
        Output('radio-buttons-1', 'value'),
        Output('radio-buttons-2', 'options'),
        Output('radio-buttons-2', 'value'),
        Input('config-reload-trigger', 'data'),
        State('store-column-ranges', 'data'),
        State('hot-config-store', 'data'),
        prevent_initial_call=True
    )
    def update_graph_options_hot(reload_trigger, column_ranges, hot_config):
        """Update graph options dynamically based on hot-reloaded config."""
        if not column_ranges or not hot_config:
            raise PreventUpdate
        
        df_cols = list(column_ranges.keys())
        
        valid_opts_1 = [opt for opt in hot_config.get('graph_1_options', []) 
                       if opt in df_cols]
        valid_opts_2 = [opt for opt in hot_config.get('graph_2_options', []) 
                       if opt in df_cols]
        
        default_1 = valid_opts_1[0] if valid_opts_1 else None
        default_2 = valid_opts_2[0] if valid_opts_2 else None
        
        logger.info(f"Hot-updated graph options: G1={valid_opts_1}, G2={valid_opts_2}")
        
        return valid_opts_1, default_1, valid_opts_2, default_2
    
    @callback(
        Output('radio-2d-y', 'options'),
        Output('radio-2d-y', 'value'),
        Output('radio-2d-color', 'options'),
        Output('radio-2d-color', 'value'),
        Input('config-reload-trigger', 'data'),
        State('store-column-ranges', 'data'),
        State('hot-config-store', 'data'),
        prevent_initial_call=True
    )
    def update_2d_options_hot(reload_trigger, column_ranges, hot_config):
        """Update 2D plot options dynamically based on hot-reloaded config."""
        if not column_ranges or not hot_config:
            raise PreventUpdate
        
        df_cols = list(column_ranges.keys())
        
        valid_y_opts = [opt for opt in hot_config.get('plot_2d_y_options', []) 
                       if opt in df_cols]
        valid_color_opts = [opt for opt in hot_config.get('plot_2d_color_options', []) 
                           if opt in df_cols]
        
        default_y = valid_y_opts[0] if valid_y_opts else None
        default_color = valid_color_opts[0] if valid_color_opts else None
        
        logger.info(f"Hot-updated 2D options: Y={valid_y_opts}, Color={valid_color_opts}")
        
        return valid_y_opts, default_y, valid_color_opts, default_color
    
    # Add clientside callback for immediate theme switching feedback
    clientside_callback(
        '''
        function(theme_url) {
            if (!theme_url) return window.dash_clientside.no_update;
            
            // Find existing bootstrap link and update it
            const links = document.getElementsByTagName('link');
            for (let i = 0; i < links.length; i++) {
                if (links[i].href && (links[i].href.includes('bootstrap') || 
                    links[i].href.includes('bootswatch'))) {
                    links[i].href = theme_url;
                    break;
                }
            }
            
            // Show brief success message
            const alert = document.querySelector('[role="alert"]');
            if (alert) {
                alert.style.display = 'block';
                setTimeout(() => alert.style.display = 'none', 2000);
            }
            
            return 'Theme updated successfully!';
        }
        ''',
        Output('theme-update-message', 'children'),
        Input('dynamic-theme-link', 'href'),
        prevent_initial_call=True
    )