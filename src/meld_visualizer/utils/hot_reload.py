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
        try:
            from ..config import APP_CONFIG
            current_theme = APP_CONFIG.get("default_theme", "Cerulean (Default)")
            theme_url = get_theme_css_url(current_theme)
            logger.info(f"Initializing theme on startup: {current_theme}")
            return theme_url, current_theme
        except Exception as e:
            logger.error(f"Error initializing theme: {e}")
            raise PreventUpdate
    
    @callback(
        Output('dynamic-theme-link', 'href'),
        Output('current-theme-store', 'data'),
        Input('config-theme-dropdown', 'value'),
        State('current-theme-store', 'data'),
        prevent_initial_call=True
    )
    def update_theme_dynamically(new_theme, current_theme):
        """Update theme CSS dynamically without restart."""
        try:
            if not new_theme or new_theme == current_theme:
                raise PreventUpdate
            
            theme_url = get_theme_css_url(new_theme)
            logger.info(f"Switching theme from {current_theme} to {new_theme}")
            
            return theme_url, new_theme
        except PreventUpdate:
            raise
        except Exception as e:
            logger.error(f"Error updating theme dynamically: {e}")
            raise PreventUpdate
    
    
    @callback(
        Output('config-reload-trigger', 'data'),
        Output('hot-config-store', 'data'),
        Input('save-config-button', 'n_clicks'),
        State('config-reload-trigger', 'data'),
        prevent_initial_call=True
    )
    def trigger_config_reload(n_clicks, current_trigger):
        """Reload configuration after save without restart."""
        try:
            if not n_clicks:
                raise PreventUpdate
            
            # Reload config from file
            new_config = load_config()
            logger.info("Configuration reloaded for hot-update")
            
            return current_trigger + 1, new_config
            
        except PreventUpdate:
            raise
        except Exception as e:
            logger.error(f"Error reloading configuration: {e}")
            return current_trigger, {}
    
    
    
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