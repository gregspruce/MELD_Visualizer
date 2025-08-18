"""
Configuration and settings callbacks.
Handles UI configuration, settings management, and column selection.
"""

import logging
from dash import Input, Output, State, callback, no_update
from dash.exceptions import PreventUpdate

from ..utils.security_utils import ConfigurationManager
from ..config import APP_CONFIG
from ..constants import SUCCESS_CONFIG_SAVED

logger = logging.getLogger(__name__)


def register_config_callbacks(app=None):
    """Register configuration-related callbacks."""
    
    @callback(
        Output('config-graph-1-dropdown', 'options'),
        Output('config-graph-2-dropdown', 'options'),
        Output('config-2d-y-dropdown', 'options'),
        Output('config-2d-color-dropdown', 'options'),
        Input('store-layout-config', 'data')
    )
    def update_config_tab_options(layout_config):
        """Populate dropdowns in the Settings tab with columns from uploaded file."""
        if layout_config is None:
            return [], [], [], []
        
        axis_options = layout_config.get('axis_options', [])
        return axis_options, axis_options, axis_options, axis_options

    @callback(
        Output('config-graph-1-dropdown', 'value'),
        Output('config-graph-2-dropdown', 'value'),
        Output('config-2d-y-dropdown', 'value'),
        Output('config-2d-color-dropdown', 'value'),
        Input('store-layout-config', 'data'),
        prevent_initial_call=True
    )
    def populate_config_tab_values(layout_config):
        """Set default selected values in Settings tab based on config."""
        if layout_config is None:
            raise PreventUpdate
        
        valid_columns = layout_config.get('axis_options', [])
        
        val1 = [opt for opt in APP_CONFIG.get('graph_1_options', []) 
                if opt in valid_columns]
        val2 = [opt for opt in APP_CONFIG.get('graph_2_options', []) 
                if opt in valid_columns]
        val3 = [opt for opt in APP_CONFIG.get('plot_2d_y_options', []) 
                if opt in valid_columns]
        val4 = [opt for opt in APP_CONFIG.get('plot_2d_color_options', []) 
                if opt in valid_columns]
        
        return val1, val2, val3, val4

    @callback(
        Output('save-config-alert', 'is_open'),
        Output('save-config-alert', 'children'),
        Output('store-config-updated', 'data'),
        Input('save-config-button', 'n_clicks'),
        [State('config-theme-dropdown', 'value'),
         State('config-template-dropdown', 'value'),
         State('config-graph-1-dropdown', 'value'),
         State('config-graph-2-dropdown', 'value'),
         State('config-2d-y-dropdown', 'value'),
         State('config-2d-color-dropdown', 'value')],
        prevent_initial_call=True
    )
    def save_config_and_advise_restart(n_clicks, theme, template, 
                                      g1_opts, g2_opts, y_2d_opts, color_2d_opts):
        """Save current UI settings to config.json."""
        if not n_clicks:
            raise PreventUpdate
        
        new_config = {
            "default_theme": theme,
            "plotly_template": template,
            "graph_1_options": g1_opts,
            "graph_2_options": g2_opts,
            "plot_2d_y_options": y_2d_opts,
            "plot_2d_color_options": color_2d_opts,
        }
        
        # Use secure configuration saving
        success, message = ConfigurationManager.save_config(new_config)
        
        if success:
            logger.info("Configuration saved successfully")
            return True, SUCCESS_CONFIG_SAVED, n_clicks
        else:
            logger.error(f"Failed to save configuration: {message}")
            return True, f"Error: {message}", no_update

    @callback(
        Output('radio-buttons-1', 'options'),
        Output('radio-buttons-1', 'value'),
        Output('radio-buttons-2', 'options'),
        Output('radio-buttons-2', 'value'),
        Input('store-column-ranges', 'data')
    )
    def update_main_graph_radios(column_ranges):
        """Populate radio items for main graphs based on config and available columns."""
        if not column_ranges:
            return [], None, [], None
        
        df_cols = list(column_ranges.keys())
        
        valid_opts_1 = [opt for opt in APP_CONFIG['graph_1_options'] 
                       if opt in df_cols]
        valid_opts_2 = [opt for opt in APP_CONFIG['graph_2_options'] 
                       if opt in df_cols]
        
        default_1 = valid_opts_1[0] if valid_opts_1 else None
        default_2 = valid_opts_2[0] if valid_opts_2 else None
        
        return valid_opts_1, default_1, valid_opts_2, default_2

    @callback(
        Output('radio-2d-y', 'options'),
        Output('radio-2d-y', 'value'),
        Output('radio-2d-color', 'options'),
        Output('radio-2d-color', 'value'),
        Input('store-column-ranges', 'data')
    )
    def update_2d_plot_radios(column_ranges):
        """Populate radio items for 2D plot based on config and available columns."""
        if not column_ranges:
            return [], None, [], None
        
        df_cols = list(column_ranges.keys())
        
        valid_y_opts = [opt for opt in APP_CONFIG['plot_2d_y_options'] 
                       if opt in df_cols]
        valid_color_opts = [opt for opt in APP_CONFIG['plot_2d_color_options'] 
                           if opt in df_cols]
        
        default_y = valid_y_opts[0] if valid_y_opts else None
        default_color = valid_color_opts[0] if valid_color_opts else None
        
        return valid_y_opts, default_y, valid_color_opts, default_color

    @callback(
        Output('custom-dropdown-x', 'options'),
        Output('custom-dropdown-y', 'options'),
        Output('custom-dropdown-z', 'options'),
        Output('custom-dropdown-color', 'options'),
        Output('custom-dropdown-filter', 'options'),
        Output('custom-dropdown-x', 'value'),
        Output('custom-dropdown-y', 'value'),
        Output('custom-dropdown-z', 'value'),
        Output('custom-dropdown-color', 'value'),
        Output('custom-dropdown-filter', 'value'),
        Output('mesh-plot-color-dropdown', 'options'),
        Output('mesh-plot-color-dropdown', 'value'),
        Input('store-layout-config', 'data')
    )
    def update_custom_and_mesh_plot_controls(layout_config):
        """Populate all dropdowns for Custom Plot and Mesh Plot tabs."""
        if not layout_config:
            return [[]]*7 + [None]*5
        
        axis_options = layout_config['axis_options']
        
        # Import default selections from constants
        from ..constants import (
            DEFAULT_X_AXIS, DEFAULT_Y_AXIS, DEFAULT_Z_AXIS,
            DEFAULT_COLOR_COLUMN, DEFAULT_FILTER_COLUMN
        )
        
        # Set defaults based on available columns
        default_x = DEFAULT_X_AXIS if DEFAULT_X_AXIS in axis_options else (
            axis_options[0] if axis_options else None
        )
        default_y = DEFAULT_Y_AXIS if DEFAULT_Y_AXIS in axis_options else (
            axis_options[1] if len(axis_options) > 1 else None
        )
        default_z = DEFAULT_Z_AXIS if DEFAULT_Z_AXIS in axis_options else (
            axis_options[2] if len(axis_options) > 2 else None
        )
        default_color = DEFAULT_COLOR_COLUMN if DEFAULT_COLOR_COLUMN in axis_options else (
            axis_options[3] if len(axis_options) > 3 else default_x
        )
        default_filter = DEFAULT_FILTER_COLUMN if DEFAULT_FILTER_COLUMN in axis_options else default_x
        
        mesh_color_options = axis_options
        mesh_color_value = DEFAULT_COLOR_COLUMN if DEFAULT_COLOR_COLUMN in axis_options else (
            axis_options[0] if axis_options else None
        )
        
        return (axis_options, axis_options, axis_options, axis_options, axis_options,
                default_x, default_y, default_z, default_color, default_filter,
                mesh_color_options, mesh_color_value)