# --- layout.py ---

from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
from config import APP_CONFIG, THEMES, PLOTLY_TEMPLATE, SCATTER_3D_HEIGHT

# --- Reusable Layout Functions ---
def build_header():
    """Builds the header section with file upload and status messages."""
    return dbc.Row([
        html.Div(id='output-filename', className="text-primary text-center fs-3 mb-2", children="Please upload a CSV file to begin."),
        dbc.Alert(id='config-warning-alert', color="warning", is_open=False, className="w-75 mx-auto"),
        dcc.Upload(
            id='upload-data',
            children=html.Div(['Drag and Drop or ', html.A('Select a CSV File')]),
            style={
                'width': '100%', 'height': '60px', 'lineHeight': '60px',
                'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px',
                'textAlign': 'center', 'margin': '10px 0'
            }
        )
    ])

def create_filter_controls(control_id_prefix, filter_label):
    """Creates a standardized set of filter controls (slider, inputs)."""
    return html.Div([
        html.H6(f"Filter by {filter_label}"),
        dcc.RangeSlider(
            id={'type': 'range-slider', 'index': control_id_prefix},
            min=0, max=1, step=0.1, value=[0, 1],
            tooltip={"placement": "bottom", "always_visible": True}, marks=None
        ),
        dbc.Row([
            dbc.Col(dbc.InputGroup([dbc.InputGroupText("Lower Bound"), dbc.Input(id={'type': 'lower-bound-input', 'index': control_id_prefix}, type="number", step=0.1, debounce=True)]), width=6),
            dbc.Col(dbc.InputGroup([dbc.InputGroupText("Upper Bound"), dbc.Input(id={'type': 'upper-bound-input', 'index': control_id_prefix}, type="number", step=0.1, debounce=True)]), width=6),
        ], className="mt-2"),
        dbc.Row([
            dbc.Col(dbc.InputGroup([dbc.InputGroupText("Slider Min"), dbc.Input(id={'type': 'slider-min-input', 'index': control_id_prefix}, type="number", step=0.1, debounce=True)]), width=6),
            dbc.Col(dbc.InputGroup([dbc.InputGroupText("Slider Max"), dbc.Input(id={'type': 'slider-max-input', 'index': control_id_prefix}, type="number", step=0.1, debounce=True)]), width=6),
        ], className="mt-2"),
    ])

def create_color_scale_controls(control_id_prefix):
    """Creates a pair of inputs for setting min/max of a color scale."""
    return dbc.Row([
        dbc.Col(dbc.InputGroup([dbc.InputGroupText("Color Min"), dbc.Input(id={'type': 'color-min-input', 'index': control_id_prefix}, type="number", debounce=True)])),
        dbc.Col(dbc.InputGroup([dbc.InputGroupText("Color Max"), dbc.Input(id={'type': 'color-max-input', 'index': control_id_prefix}, type="number", debounce=True)])),
    ], className="mb-2")

# --- Tab-Specific Layout Functions ---
def build_main_controls_and_graphs():
    """Builds the layout for the 'Main 3D Plots' tab."""
    return [
        dbc.Row([
            dbc.Col([html.H5("Graph 1 Controls"), dcc.RadioItems(id='radio-buttons-1', options=[], value=None, inline=True), create_filter_controls('zpos-1', 'ZPos')], width=6),
            dbc.Col([html.H5("Graph 2 Controls"), dcc.RadioItems(id='radio-buttons-2', options=[], value=None, inline=True), create_filter_controls('zpos-2', 'ZPos')], width=6)
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(id='graph-1', style={'height': SCATTER_3D_HEIGHT}), width=6),
            dbc.Col(dcc.Graph(id='graph-2', style={'height': SCATTER_3D_HEIGHT}), width=6)
        ]),
    ]

def build_2d_plotter():
    """Builds the layout for the '2D Time Plot' tab."""
    return [
        dbc.Row([html.H4("2D Scatter Plot", className="text-center"), dbc.Col(create_filter_controls('time-2d', 'Time'), width=12)], className="mb-2"),
        dbc.Row([
            dbc.Col([html.H6("Y-Axis"), dcc.RadioItems(id='radio-2d-y', options=[], value=None, inline=True)], width=6),
            dbc.Col([html.H6("Color Scale"), dcc.RadioItems(id='radio-2d-color', options=[], value=None, inline=True)], width=6),
        ], align="center", className="mb-2"),
        dbc.Row(dbc.Col(dcc.Graph(id='graph-2d'), width=12)),
    ]

def build_custom_plotter():
    """Builds the layout for the 'Custom 3D Plot' tab."""
    return [
        dbc.Row(html.H4("Custom 3D Scatter Plot", className="text-center")),
        dbc.Row([
            dbc.Col([html.H6("X-Axis"), dcc.Dropdown(id='custom-dropdown-x', options=[], value=None, clearable=False)], width=3),
            dbc.Col([html.H6("Y-Axis"), dcc.Dropdown(id='custom-dropdown-y', options=[], value=None, clearable=False)], width=3),
            dbc.Col([html.H6("Z-Axis"), dcc.Dropdown(id='custom-dropdown-z', options=[], value=None, clearable=False)], width=3),
            dbc.Col([html.H6("Color"), dcc.Dropdown(id='custom-dropdown-color', options=[], value=None, clearable=False)], width=3),
        ], className="mb-2"),
        dbc.Row([
            dbc.Col([html.H6("Filter By"), dcc.Dropdown(id='custom-dropdown-filter', options=[], value=None, clearable=False)], width=3),
            dbc.Col(create_filter_controls('custom', 'Selected Filter'), width=9),
        ]),
        dbc.Row(dbc.Col(dcc.Graph(id='custom-graph', style={'height': SCATTER_3D_HEIGHT}), width=12)),
    ]

def build_data_table():
    """Builds the layout for the 'Data Table' tab."""
    return dbc.Row([
        dash_table.DataTable(id='data-table', page_size=25, style_table={'overflowX': 'auto'})
    ])

def build_config_tab():
    """Builds the layout for the 'Settings' tab."""
    theme_options = [{"label": name, "value": name} for name in THEMES.keys()]
    template_options = ["plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none"]
    return html.Div(className="mt-4", children=[
        dbc.Row([
            dbc.Col([
                html.H4("Application Appearance"), html.Hr(), dbc.Label("Application Theme"),
                dcc.Dropdown(id='config-theme-dropdown', options=theme_options, value=APP_CONFIG['default_theme']), html.Br(),
                dbc.Label("Plot Background Template"), dcc.Dropdown(id='config-template-dropdown', options=template_options, value=PLOTLY_TEMPLATE),
                html.P("Note: If you select a dark theme, this should be 'plotly_dark'.", className="text-muted small mt-1"),
            ], md=6),
            dbc.Col([
                html.H4("Default Graph Options"), html.Hr(), dbc.Label("Graph 1 Options (Color Dropdown)"),
                dcc.Dropdown(id='config-graph-1-dropdown', options=[], value=APP_CONFIG['graph_1_options'], multi=True), html.Br(),
                dbc.Label("Graph 2 Options (Color Dropdown)"),
                dcc.Dropdown(id='config-graph-2-dropdown', options=[], value=APP_CONFIG['graph_2_options'], multi=True), html.Br(),
                dbc.Label("2D Plot Y-Axis Options"),
                dcc.Dropdown(id='config-2d-y-dropdown', options=[], value=APP_CONFIG['plot_2d_y_options'], multi=True), html.Br(),
                dbc.Label("2D Plot Color Options"),
                dcc.Dropdown(id='config-2d-color-dropdown', options=[], value=APP_CONFIG['plot_2d_color_options'], multi=True),
            ], md=6)
        ]), html.Hr(),
        dbc.Row(dbc.Col([
            dbc.Button("Save Configuration", id="save-config-button", color="primary", n_clicks=0),
            dbc.Alert(id='save-config-alert', is_open=False, duration=10000, color="success", className="mt-3"),
            html.P("Important: Changes will only be applied after you close and restart the application.", className="text-danger small mt-2")
        ]))
    ])

def build_line_plot_tab():
    """Builds the layout for the '3D Toolpath Plot' tab."""
    return html.Div(className="mt-4", children=[
        html.H4("3D Toolpath Plot (Active Extrusion)"),
        dbc.Row([
            dbc.Col(
                dbc.InputGroup(
                    [
                        dbc.InputGroupText("Z-Axis Stretch Factor"),
                        dbc.Input(id='line-plot-z-stretch-input', type='number', value=1.0, min=0.1, step=0.1),
                    ],
                    className="mb-3",
                ),
                width="auto"
            ),
            dbc.Col(
                dbc.Button("Generate Toolpath Plot", id="generate-line-plot-button", color="primary", className="mb-3"),
                width="auto"
            )
        ], align="center"),
        dcc.Loading(id="loading-line-plot", type="circle", children=dcc.Graph(id='line-plot-3d', style={'height': SCATTER_3D_HEIGHT}))
    ])

def build_mesh_plot_tab():
    """Builds the layout for the '3D Volume Mesh' tab."""
    return html.Div(className="mt-4", children=[
        html.H4("3D Volume Mesh Plot (Active Extrusion)"),
        dbc.Row([
            dbc.Col([html.H6("Color by"), dcc.Dropdown(id='mesh-plot-color-dropdown')], width=4),
            dbc.Col(create_color_scale_controls('mesh-plot'), width=8)
        ], className="mb-3"),
        dbc.Row([
            dbc.Col(
                dbc.InputGroup(
                    [
                        dbc.InputGroupText("Z-Axis Stretch Factor"),
                        dbc.Input(id='mesh-plot-z-stretch-input', type='number', value=1.0, min=0.1, step=0.1),
                    ],
                    className="mb-3",
                ),
                width="auto"
            ),
            dbc.Col(
                dbc.Button("Generate Volume Mesh", id="generate-mesh-plot-button", color="primary", className="mb-3"),
                width="auto"
            )
        ], align="center"),
        dcc.Loading(id="loading-mesh-plot", type="circle", children=dcc.Graph(id='mesh-plot-3d', style={'height': SCATTER_3D_HEIGHT}))
    ])

def build_gcode_tab():
    """Builds the layout for the new G-code visualization tab."""
    return html.Div(className="mt-4", children=[
        html.H4("G-code Program Visualization"),
        dbc.Alert(id='gcode-filename-alert', color="info", is_open=False, className="w-75 mx-auto"),
        dcc.Upload(
            id='upload-gcode',
            children=html.Div(['Drag and Drop or ', html.A('Select a G-code File (.nc)')]),
            style={
                'width': '100%', 'height': '60px', 'lineHeight': '60px',
                'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px',
                'textAlign': 'center', 'margin': '10px 0'
            }
        ),
        dbc.Row([
            dbc.Col(
                dbc.RadioItems(
                    id='gcode-view-selector',
                    options=[
                        {'label': 'Simulated Toolpath', 'value': 'toolpath'},
                        {'label': 'Simulated Volume Mesh', 'value': 'mesh'},
                    ],
                    value='toolpath',
                    inline=True
                ),
                width="auto"
            ),
            dbc.Col(
                dbc.InputGroup(
                    [
                        dbc.InputGroupText("Z-Axis Stretch Factor"),
                        dbc.Input(id='gcode-z-stretch-input', type='number', value=2.0, min=0.1, step=0.1),
                    ],
                    className="mb-3",
                ),
                width="auto"
            ),
            dbc.Col(
                dbc.Button("Generate Visualization", id="generate-gcode-viz-button", color="primary", className="mb-3"),
                width="auto"
            )
        ], align="center", justify="start", className="mb-3"),
        dcc.Loading(
            id="loading-gcode-plot",
            type="circle",
            children=dcc.Graph(id='gcode-graph', style={'height': SCATTER_3D_HEIGHT})
        )
    ])

def build_app_body_with_tabs():
    """Constructs the main tab structure of the app."""
    return dbc.Tabs([
        dbc.Tab(label="Main 3D Plots", children=[html.Div(className="mt-4", children=[*build_main_controls_and_graphs()])]),
        dbc.Tab(label="2D Time Plot", children=[html.Div(className="mt-4", children=[*build_2d_plotter()])]),
        dbc.Tab(label="Custom 3D Plot", children=[html.Div(className="mt-4", children=[*build_custom_plotter()])]),
        dbc.Tab(label="Data Table", children=[html.Div(className="mt-4", children=[build_data_table()])]),
        dbc.Tab(label="3D Toolpath Plot", children=[build_line_plot_tab()]),
        dbc.Tab(label="3D Volume Mesh", children=[build_mesh_plot_tab()]),
        dbc.Tab(label="G-code Visualization", children=[build_gcode_tab()]),  # <-- New Tab Added Here
        dbc.Tab(label="Settings", children=[build_config_tab()])
    ])

def get_layout(app):
    """
    Creates the master layout for the entire application.
    This function is called by app.py.
    The 'app' argument is unused but required by the dynamic loader.
    """
    return html.Div([
        dbc.Container([
            # Add the new store for G-code data
            dcc.Store(id='store-main-df'), dcc.Store(id='store-gcode-df'),
            dcc.Store(id='store-layout-config'), dcc.Store(id='store-config-warnings'),
            dcc.Store(id='store-column-ranges'), dcc.Store(id='store-config-updated'),
            build_header(),
            build_app_body_with_tabs(),
        ], fluid=True)
    ])