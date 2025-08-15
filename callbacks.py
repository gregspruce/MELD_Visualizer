# --- callbacks.py ---

import io
import json
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from dash import (Input, Output, State, callback, no_update, MATCH, ctx, html)
from dash.exceptions import PreventUpdate

# Import the main app instance
# App instance will be passed to register_callbacks function
# Import shared configuration and constants
from config import APP_CONFIG, PLOTLY_TEMPLATE, TABLE_STYLE_DARK, TABLE_STYLE_LIGHT
# Import data processing functions
from data_processing import parse_contents, generate_volume_mesh, parse_gcode_file


def create_empty_figure(message="Upload a file and configure options."):
    """Creates a blank Plotly figure with a text message."""
    fig = go.Figure()
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        xaxis={'visible': False},
        yaxis={'visible': False},
        annotations=[{
            "text": message, "xref": "paper", "yref": "paper",
            "showarrow": False, "font": {"size": 16}
        }]
    )
    return fig

# --- Data Loading and Config Setup Callbacks ---
@callback(
    Output('store-main-df', 'data'),
    Output('output-filename', 'children'),
    Output('store-layout-config', 'data'),
    Output('store-config-warnings', 'data'),
    Output('store-column-ranges', 'data'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def update_data_and_configs(contents, filename):
    """
    Primary callback triggered on file upload. This function is responsible for:
    1. Parsing the uploaded CSV file using the `parse_contents` utility.
    2. Storing the main DataFrame in a dcc.Store as JSON.
    3. Updating the filename display.
    4. Storing configuration data for the layout (e.g., available columns for dropdowns).
    5. Storing the min/max ranges for all numeric columns.
    6. Generating warnings if columns specified in `config.json` are not found in the file.
    """
    if contents is None:
        return no_update, "Please upload a CSV file to begin.", no_update, no_update, no_update

    df, error_message, converted = parse_contents(contents, filename)
    if error_message:
        return no_update, error_message, no_update, no_update, no_update

    filename_message = f"Current file: {filename}"
    if converted:
        filename_message += " (Imperial units detected and converted to mm)"

    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    column_ranges = {col: [df[col].min(), df[col].max()] for col in numeric_cols}
    layout_config = {'axis_options': numeric_cols}
    df_columns_set = set(df.columns)

    # Check if columns from the config file are present in the uploaded data
    warnings = []
    for key, options in APP_CONFIG.items():
        if 'options' in key and isinstance(options, list):
            missing_cols = [col for col in options if col not in df_columns_set]
            if missing_cols:
                warnings.append(f"Warning: Columns from 'config.json' not found in '{filename}': {', '.join(missing_cols)}.")

    return df.to_json(date_format='iso', orient='split'), filename_message, layout_config, warnings, column_ranges

@callback(
    Output('config-warning-alert', 'children'),
    Output('config-warning-alert', 'is_open'),
    Input('store-config-warnings', 'data')
)
def display_config_warnings(warnings):
    """Displays warnings if config columns are missing from the uploaded file."""
    if warnings:
        return html.Ul([html.Li(w) for w in warnings]), True
    return "", False

# --- UI Population Callbacks (dynamic dropdowns/radios) ---
@callback(
    Output('config-graph-1-dropdown', 'options'),
    Output('config-graph-2-dropdown', 'options'),
    Output('config-2d-y-dropdown', 'options'),
    Output('config-2d-color-dropdown', 'options'),
    Input('store-layout-config', 'data')
)
def update_config_tab_options(layout_config):
    """Populates dropdowns in the 'Settings' tab with columns from the uploaded file."""
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
    """Sets the default selected values in the Settings tab based on config and available columns."""
    if layout_config is None: raise PreventUpdate
    valid_columns = layout_config.get('axis_options', [])
    val1 = [opt for opt in APP_CONFIG.get('graph_1_options', []) if opt in valid_columns]
    val2 = [opt for opt in APP_CONFIG.get('graph_2_options', []) if opt in valid_columns]
    val3 = [opt for opt in APP_CONFIG.get('plot_2d_y_options', []) if opt in valid_columns]
    val4 = [opt for opt in APP_CONFIG.get('plot_2d_color_options', []) if opt in valid_columns]
    return val1, val2, val3, val4

@callback(
    Output('radio-buttons-1', 'options'), Output('radio-buttons-1', 'value'),
    Output('radio-buttons-2', 'options'), Output('radio-buttons-2', 'value'),
    Input('store-column-ranges', 'data')
)
def update_main_graph_radios(column_ranges):
    """Populates radio items for the main graphs based on config and available columns."""
    if not column_ranges: return [], None, [], None
    df_cols = list(column_ranges.keys())
    valid_opts_1 = [opt for opt in APP_CONFIG['graph_1_options'] if opt in df_cols]
    valid_opts_2 = [opt for opt in APP_CONFIG['graph_2_options'] if opt in df_cols]
    return valid_opts_1, valid_opts_1[0] if valid_opts_1 else None, valid_opts_2, valid_opts_2[0] if valid_opts_2 else None

@callback(
    Output('radio-2d-y', 'options'), Output('radio-2d-y', 'value'),
    Output('radio-2d-color', 'options'), Output('radio-2d-color', 'value'),
    Input('store-column-ranges', 'data')
)
def update_2d_plot_radios(column_ranges):
    """Populates radio items for the 2D plot based on config and available columns."""
    if not column_ranges: return [], None, [], None
    df_cols = list(column_ranges.keys())
    valid_y_opts = [opt for opt in APP_CONFIG['plot_2d_y_options'] if opt in df_cols]
    valid_color_opts = [opt for opt in APP_CONFIG['plot_2d_color_options'] if opt in df_cols]
    return valid_y_opts, valid_y_opts[0] if valid_y_opts else None, valid_color_opts, valid_color_opts[0] if valid_color_opts else None

@callback(
    Output('custom-dropdown-x', 'options'), Output('custom-dropdown-y', 'options'),
    Output('custom-dropdown-z', 'options'), Output('custom-dropdown-color', 'options'),
    Output('custom-dropdown-filter', 'options'),
    Output('custom-dropdown-x', 'value'), Output('custom-dropdown-y', 'value'),
    Output('custom-dropdown-z', 'value'), Output('custom-dropdown-color', 'value'),
    Output('custom-dropdown-filter', 'value'),
    Output('mesh-plot-color-dropdown', 'options'), Output('mesh-plot-color-dropdown', 'value'),
    Input('store-layout-config', 'data')
)
def update_custom_and_mesh_plot_controls(layout_config):
    """
    Populates all dropdowns for the Custom Plot and Mesh Plot tabs.
    It also sets sensible default values for the custom plot axes.
    """
    if not layout_config: return [[]]*7 + [None]*5
    axis_options = layout_config['axis_options']
    # Set default axes to standard positional columns if they exist, otherwise fallback to the first available columns.
    default_x = 'XPos' if 'XPos' in axis_options else (axis_options[0] if axis_options else None)
    default_y = 'YPos' if 'YPos' in axis_options else (axis_options[1] if len(axis_options) > 1 else None)
    default_z = 'ZPos' if 'ZPos' in axis_options else (axis_options[2] if len(axis_options) > 2 else None)
    default_color = 'ToolTemp' if 'ToolTemp' in axis_options else (axis_options[3] if len(axis_options) > 3 else default_x)
    default_filter = 'ZPos' if 'ZPos' in axis_options else default_x
    mesh_color_options = axis_options
    mesh_color_value = 'ToolTemp' if 'ToolTemp' in axis_options else (axis_options[0] if axis_options else None)

    return (axis_options, axis_options, axis_options, axis_options, axis_options,
            default_x, default_y, default_z, default_color, default_filter,
            mesh_color_options, mesh_color_value)

# --- Settings Management Callback ---
@callback(
    Output('save-config-alert', 'is_open'),
    Output('save-config-alert', 'children'),
    Output('store-config-updated', 'data'),
    Input('save-config-button', 'n_clicks'),
    [State('config-theme-dropdown', 'value'), State('config-template-dropdown', 'value'),
     State('config-graph-1-dropdown', 'value'), State('config-graph-2-dropdown', 'value'),
     State('config-2d-y-dropdown', 'value'), State('config-2d-color-dropdown', 'value')],
    prevent_initial_call=True
)
def save_config_and_advise_restart(n_clicks, theme, template, g1_opts, g2_opts, y_2d_opts, color_2d_opts):
    """Saves the current UI settings from the 'Settings' tab to config.json."""
    if not n_clicks: raise PreventUpdate
    # Import security utilities for safe configuration handling
    from security_utils import ConfigurationManager
    
    new_config = {
        "default_theme": theme, "plotly_template": template, "graph_1_options": g1_opts,
        "graph_2_options": g2_opts, "plot_2d_y_options": y_2d_opts, "plot_2d_color_options": color_2d_opts,
    }
    
    # Use secure configuration saving
    success, message = ConfigurationManager.save_config(new_config)
    
    if success:
        message = "Success! Your settings have been saved. Please restart the application to see the changes."
        return True, message, n_clicks
    else:
        return True, f"Error: {message}", no_update

# --- Filter Synchronization Callback ---
@callback(
    Output({'type': 'range-slider', 'index': MATCH}, 'min'),
    Output({'type': 'range-slider', 'index': MATCH}, 'max'),
    Output({'type': 'range-slider', 'index': MATCH}, 'value'),
    Output({'type': 'lower-bound-input', 'index': MATCH}, 'value'),
    Output({'type': 'upper-bound-input', 'index': MATCH}, 'value'),
    Output({'type': 'slider-min-input', 'index': MATCH}, 'value'),
    Output({'type': 'slider-max-input', 'index': MATCH}, 'value'),
    Input({'type': 'range-slider', 'index': MATCH}, 'value'),
    Input({'type': 'lower-bound-input', 'index': MATCH}, 'value'),
    Input({'type': 'upper-bound-input', 'index': MATCH}, 'value'),
    Input({'type': 'slider-min-input', 'index': MATCH}, 'value'),
    Input({'type': 'slider-max-input', 'index': MATCH}, 'value'),
    Input('store-column-ranges', 'data'),
    State('custom-dropdown-filter', 'value'),
    prevent_initial_call=True
)
def sync_filter_controls(slider_val, lower_in, upper_in, s_min_in, s_max_in, column_ranges, custom_filter_col):
    """
    Synchronizes all filter components (slider and input boxes) with each other
    and updates them when new data is loaded. Uses a pattern-matching callback
    to handle multiple sets of filter controls with a single function.
    """
    if not column_ranges: raise PreventUpdate

    # Identify which component triggered the callback
    triggered_id = ctx.triggered_id if isinstance(ctx.triggered_id, dict) else {'index': 'init', 'type': 'store'}
    triggered_prop_str = ctx.triggered[0]['prop_id']
    index = triggered_id.get('index')

    # Determine which data column to filter based on the component's 'index'
    if index.startswith('zpos'): col_name = 'ZPos'
    elif index == 'time-2d': col_name = 'TimeInSeconds'
    elif index == 'custom': col_name = custom_filter_col
    else: col_name = 'ZPos' # Fallback

    if not col_name: return no_update

    # Get the absolute min/max for the relevant column from stored data
    abs_min, abs_max = column_ranges.get(col_name, [0, 1])

    # Initialize output values with current state or defaults
    out_s_min = s_min_in if s_min_in is not None else abs_min
    out_s_max = s_max_in if s_max_in is not None else abs_max
    out_l_bound, out_u_bound = slider_val

    # Logic to handle which input triggered the callback and update state accordingly
    if triggered_prop_str.startswith('store-column-ranges'):
        # A new file was loaded, so reset all filter controls to the full range.
        out_s_min, out_s_max, out_l_bound, out_u_bound = abs_min, abs_max, abs_min, abs_max
    elif 'range-slider' in triggered_prop_str:
        # The main slider was moved.
        out_l_bound, out_u_bound = slider_val
    elif 'lower-bound-input' in triggered_prop_str and lower_in is not None:
        # The "Lower Bound" input box was changed.
        out_l_bound = max(min(lower_in, out_u_bound), abs_min)
        out_s_min = min(out_l_bound, out_s_min)
    elif 'upper-bound-input' in triggered_prop_str and upper_in is not None:
        # The "Upper Bound" input box was changed.
        out_u_bound = min(max(upper_in, out_l_bound), abs_max)
        out_s_max = max(out_u_bound, out_s_max)
    elif 'slider-min-input' in triggered_prop_str and s_min_in is not None:
        # The "Slider Min" input box was changed.
        out_s_min = max(s_min_in, abs_min)
    elif 'slider-max-input' in triggered_prop_str and s_max_in is not None:
        # The "Slider Max" input box was changed.
        out_s_max = min(s_max_in, abs_max)

    # Final validation to ensure all values are consistent and within bounds
    if out_s_min > out_s_max: out_s_min = out_s_max
    out_l_bound = max(out_l_bound, out_s_min)
    out_u_bound = min(out_u_bound, out_s_max)
    if out_l_bound > out_u_bound: out_l_bound = out_u_bound

    return out_s_min, out_s_max, [out_l_bound, out_u_bound], out_l_bound, out_u_bound, out_s_min, out_s_max

# --- Graph Generation Callbacks ---
@callback(
    Output("graph-1", "figure"),
    [Input('store-main-df', 'data'),
     Input("radio-buttons-1", "value"),
     Input({'type': 'range-slider', 'index': 'zpos-1'}, "value"),
     Input('store-config-updated', 'data')]
)
def update_graph_1(jsonified_df, col_chosen, slider_range, config_updated):
    """Updates the first main 3D scatter plot based on the selected color and ZPos filter."""
    if not all([jsonified_df, col_chosen, slider_range]): return create_empty_figure()
    df = pd.read_json(io.StringIO(jsonified_df), orient='split')
    if col_chosen not in df.columns: return create_empty_figure(f"Error: Column '{col_chosen}' not in file.")
    low, high = slider_range
    dff = df[(df['ZPos'] >= low) & (df['ZPos'] <= high)]
    if dff.empty: return create_empty_figure("No data in selected ZPos range")
    fig = px.scatter_3d(dff, x='XPos', y='YPos', z='ZPos', color=col_chosen, template=PLOTLY_TEMPLATE)
    return fig.update_layout(margin=dict(l=0, r=0, b=0, t=0), scene_aspectmode='data')

@callback(
    Output("graph-2", "figure"),
    [Input('store-main-df', 'data'),
     Input("radio-buttons-2", "value"),
     Input({'type': 'range-slider', 'index': 'zpos-2'}, "value"),
     Input('store-config-updated', 'data')]
)
def update_graph_2(jsonified_df, col_chosen, slider_range, config_updated):
    """Updates the second main 3D scatter plot based on the selected color and ZPos filter."""
    if not all([jsonified_df, col_chosen, slider_range]): return create_empty_figure()
    df = pd.read_json(io.StringIO(jsonified_df), orient='split')
    if col_chosen not in df.columns: return create_empty_figure(f"Error: Column '{col_chosen}' not in file.")
    low, high = slider_range
    dff = df[(df['ZPos'] >= low) & (df['ZPos'] <= high)]
    if dff.empty: return create_empty_figure("No data in selected ZPos range")
    fig = px.scatter_3d(dff, x='XPos', y='YPos', z='ZPos', color=col_chosen, template=PLOTLY_TEMPLATE)
    return fig.update_layout(margin=dict(l=0, r=0, b=0, t=0), scene_aspectmode='data')

@callback(
    Output('graph-2d', 'figure'),
    [Input('store-main-df', 'data'),
     Input({'type': 'range-slider', 'index': 'time-2d'}, 'value'),
     Input('radio-2d-y', 'value'),
     Input('radio-2d-color', 'value')]
)
def update_2d_scatter(jsonified_df, time_range, y_col, color_col):
    """Updates the 2D time-series scatter plot based on the selected Y-axis, color, and time filter."""
    if not all([jsonified_df, time_range, y_col, color_col]): return create_empty_figure()
    df = pd.read_json(io.StringIO(jsonified_df), orient='split')
    df['Time'] = pd.to_datetime(df['Time'])
    if not {y_col, color_col}.issubset(df.columns): return create_empty_figure(f"Error: Column from config not in file.")
    low, high = time_range
    dff = df[(df['TimeInSeconds'] >= low) & (df['TimeInSeconds'] <= high)]
    if dff.empty: return create_empty_figure("No data in selected Time range")
    fig = px.scatter(dff, x='Time', y=y_col, color=color_col, template=PLOTLY_TEMPLATE)
    return fig

@callback(
    Output('custom-graph', 'figure'),
    [Input('store-main-df', 'data'),
     Input('custom-dropdown-x', 'value'), Input('custom-dropdown-y', 'value'),
     Input('custom-dropdown-z', 'value'), Input('custom-dropdown-color', 'value'),
     Input('custom-dropdown-filter', 'value'),
     Input({'type': 'range-slider', 'index': 'custom'}, 'value')]
)
def update_custom_graph(jsonified_df, x_col, y_col, z_col, color_col, filter_col, filter_range):
    """Updates the fully customizable 3D scatter plot based on user selections for all axes and filters."""
    if not all([jsonified_df, x_col, y_col, z_col, color_col, filter_col, filter_range]):
        return create_empty_figure("Select all dropdown values to render graph.")
    df = pd.read_json(io.StringIO(jsonified_df), orient='split')
    all_cols = {x_col, y_col, z_col, color_col, filter_col}
    if not all_cols.issubset(df.columns): return create_empty_figure("Error: One or more selected columns not in file.")
    low, high = filter_range
    dff = df[(df[filter_col] >= low) & (df[filter_col] <= high)]
    if dff.empty: return create_empty_figure("No data in selected filter range")
    fig = px.scatter_3d(dff, x=x_col, y=y_col, z=z_col, color=color_col, template=PLOTLY_TEMPLATE)
    return fig.update_layout(margin=dict(l=0, r=0, b=0, t=0), scene_aspectmode='data')

@callback(
    Output('data-table', 'columns'),
    Output('data-table', 'data'),
    Output('data-table', 'style_header'),
    Output('data-table', 'style_data'),
    Output('data-table', 'style_cell'),
    Input('store-main-df', 'data')
)
def update_data_table(jsonified_df):
    """Updates the data table with the content of the uploaded file and applies the correct theme."""
    if jsonified_df is None: return [], [], {}, {}, {}
    df = pd.read_json(io.StringIO(jsonified_df), orient='split')
    columns = [{"name": i, "id": i} for i in df.columns]
    data = df.to_dict('records')
    style = TABLE_STYLE_DARK if PLOTLY_TEMPLATE == 'plotly_dark' else TABLE_STYLE_LIGHT
    return columns, data, style['style_header'], style['style_data'], style['style_cell']

@callback(
    Output('line-plot-3d', 'figure'),
    Input('generate-line-plot-button', 'n_clicks'),
    [State('store-main-df', 'data'),
     State('line-plot-z-stretch-input', 'value')], # <-- ADDED State input
    prevent_initial_call=True
)
def update_line_plot(n_clicks, jsonified_df, z_stretch_factor):
    """Generates the 3D toolpath line plot from active extrusion data."""
    if n_clicks is None or jsonified_df is None:
        return create_empty_figure("Upload a file and click 'Generate'.")

    df = pd.read_json(io.StringIO(jsonified_df), orient='split')
    df_active = df[(df['FeedVel'] > 0) & (df['PathVel'] > 1e-6)].copy()

    if df_active.empty:
        return create_empty_figure("No active printing data found (FeedVel > 0).")

    # --- NEW: Dynamic aspect ratio logic ---
    if not z_stretch_factor or float(z_stretch_factor) <= 0:
        z_stretch_factor = 1.0
    aspect_ratio = dict(x=1, y=1, z=float(z_stretch_factor))

    fig = go.Figure(data=[go.Scatter3d(
        x=df_active['XPos'], y=df_active['YPos'], z=df_active['ZPos'],
        mode='lines+markers', marker=dict(size=2), line=dict(width=4)
    )])
    fig.update_layout(
        title='3D Toolpath Visualization (Active Extrusion Only)', template=PLOTLY_TEMPLATE,
        scene=dict(
            xaxis_title='X Position (mm)', yaxis_title='Y Position (mm)', zaxis_title='Z Position (mm)',
            aspectmode='data' if z_stretch_factor == 1.0 else 'manual', # Use 'data' for true scale, 'manual' for stretch
            aspectratio=aspect_ratio
        )
    )
    return fig

@callback(
    Output({'type': 'color-min-input', 'index': 'mesh-plot'}, 'value'),
    Output({'type': 'color-max-input', 'index': 'mesh-plot'}, 'value'),
    Input('mesh-plot-color-dropdown', 'value'),
    State('store-column-ranges', 'data'),
    prevent_initial_call=True
)
def update_color_range_for_mesh_plot(color_col, ranges):
    """Automatically updates the min/max color range inputs when the color dropdown changes."""
    if not color_col or not ranges: raise PreventUpdate
    min_val, max_val = ranges.get(color_col, [None, None])
    return min_val, max_val

@callback(
    Output('mesh-plot-3d', 'figure'),
    Input('generate-mesh-plot-button', 'n_clicks'),
    [State('store-main-df', 'data'),
     State('mesh-plot-color-dropdown', 'value'),
     State({'type': 'color-min-input', 'index': 'mesh-plot'}, 'value'),
     State({'type': 'color-max-input', 'index': 'mesh-plot'}, 'value'),
     State('mesh-plot-z-stretch-input', 'value')], # <-- ADDED State input
    prevent_initial_call=True
)
def update_mesh_plot(n_clicks, jsonified_df, color_col, cmin, cmax, z_stretch_factor):
    """Generates the 3D volume mesh plot by calling the data processing function."""
    if n_clicks is None or jsonified_df is None or color_col is None:
        return create_empty_figure("Upload a file, select a color, and click 'Generate'.")

    df = pd.read_json(io.StringIO(jsonified_df), orient='split')
    df_active = df[(df['FeedVel'] > 0) & (df['PathVel'] > 1e-6)].copy()
    if df_active.empty:
        return create_empty_figure("No active printing data for mesh generation.")

    mesh_data = generate_volume_mesh(df_active, color_col)

    if mesh_data is None:
        return create_empty_figure("Could not generate mesh from the data.")

    # --- NEW: Dynamic aspect ratio logic ---
    if not z_stretch_factor or float(z_stretch_factor) <= 0:
        z_stretch_factor = 1.0
    aspect_ratio = dict(x=1, y=1, z=float(z_stretch_factor))

    fig = go.Figure(data=[go.Mesh3d(
        x=mesh_data['vertices'][:, 0], y=mesh_data['vertices'][:, 1], z=mesh_data['vertices'][:, 2],
        i=mesh_data['faces'][:, 0], j=mesh_data['faces'][:, 1], k=mesh_data['faces'][:, 2],
        colorscale='Viridis', intensity=mesh_data['vertex_colors'],
        colorbar=dict(title=color_col), showscale=True,
        cmin=cmin, cmax=cmax
    )])
    fig.update_layout(
        title='3D Mesh Visualization of the Print', template=PLOTLY_TEMPLATE,
        scene=dict(
            xaxis_title='X Position (mm)', yaxis_title='Y Position (mm)', zaxis_title='Z Position (mm)',
            aspectmode='data' if z_stretch_factor == 1.0 else 'manual', # Use 'data' for true scale, 'manual' for stretch
            aspectratio=aspect_ratio
        )
    )
    return fig

# --- NEW G-CODE VISUALIZATION CALLBACKS ---

@callback(
    Output('store-gcode-df', 'data'),
    Output('gcode-filename-alert', 'children'),
    Output('gcode-filename-alert', 'is_open'),
    Input('upload-gcode', 'contents'),
    State('upload-gcode', 'filename'),
    prevent_initial_call=True
)
def handle_gcode_upload(contents, filename):
    """
    Triggered on G-code file upload. This function parses the file and stores
    the resulting DataFrame in the dedicated dcc.Store.
    """
    if contents is None:
        raise PreventUpdate

    df, message, _ = parse_gcode_file(contents, filename)
    if df is None:
        return no_update, message, True # Show error message

    return df.to_json(date_format='iso', orient='split'), message, True

@callback(
    Output('gcode-graph', 'figure'),
    Input('generate-gcode-viz-button', 'n_clicks'),
    [State('store-gcode-df', 'data'),
     State('gcode-view-selector', 'value'),
     State('gcode-z-stretch-input', 'value')],
    prevent_initial_call=True
)
def update_gcode_visualization(n_clicks, jsonified_df, view_mode, z_stretch_factor):
    """
    Generates the G-code visualization (either toolpath or mesh) when the
    'Generate Visualization' button is clicked.
    """
    if n_clicks is None or jsonified_df is None:
        return create_empty_figure("Please upload a G-code file and click 'Generate'.")

    df = pd.read_json(io.StringIO(jsonified_df), orient='split')
    df_active = df[df['FeedVel'] > 0].copy()

    if df_active.empty:
        return create_empty_figure("No active extrusion moves (M34) found in G-code file.")

    # --- CORRECTED: Use the stretch factor directly for the z-value ---
    if not z_stretch_factor or float(z_stretch_factor) <= 0:
        z_stretch_factor = 1.0
    custom_aspect_ratio = dict(x=1, y=1, z=float(z_stretch_factor))

    if view_mode == 'toolpath':
        fig = go.Figure(data=[go.Scatter3d(
            x=df_active['XPos'], y=df_active['YPos'], z=df_active['ZPos'],
            mode='lines+markers', marker=dict(size=2), line=dict(width=4)
        )])
        fig.update_layout(
            title='Simulated 3D Toolpath (Active Extrusion Only)', template=PLOTLY_TEMPLATE,
            scene=dict(
                xaxis_title='X Position (mm)', yaxis_title='Y Position (mm)', zaxis_title='Z Position (mm)',
                aspectmode='manual',
                aspectratio=custom_aspect_ratio
            )
        )
        return fig

    elif view_mode == 'mesh':
        color_col = 'ZPos'
        mesh_data = generate_volume_mesh(df_active, color_col)

        if mesh_data is None:
            return create_empty_figure("Could not generate mesh from the G-code data.")

        fig = go.Figure(data=[go.Mesh3d(
            x=mesh_data['vertices'][:, 0], y=mesh_data['vertices'][:, 1], z=mesh_data['vertices'][:, 2],
            i=mesh_data['faces'][:, 0], j=mesh_data['faces'][:, 1], k=mesh_data['faces'][:, 2],
            colorscale='Viridis', intensity=mesh_data['vertex_colors'],
            colorbar=dict(title=color_col), showscale=True
        )])
        fig.update_layout(
            title='Simulated 3D Volume Mesh from G-code', template=PLOTLY_TEMPLATE,
            scene=dict(
                xaxis_title='X Position (mm)', yaxis_title='Y Position (mm)', zaxis_title='Z Position (mm)',
                aspectmode='manual',
                aspectratio=custom_aspect_ratio
            )
        )
        return fig

    return create_empty_figure("Invalid view selected.")