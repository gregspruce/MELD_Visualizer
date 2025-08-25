# --- layout.py ---

from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
from ..config import APP_CONFIG, THEMES, PLOTLY_TEMPLATE, SCATTER_3D_HEIGHT, get_responsive_plot_style
# Temporarily disabled - components not integrated properly
# from .enhanced_ui import EnhancedUIComponents, UserFeedbackManager

# --- Responsive Plot Utilities ---
def create_responsive_graph(graph_id, plot_type='scatter_3d', **kwargs):
    """
    Create a responsive graph component optimized for desktop resolutions.
    
    Args:
        graph_id (str): Unique identifier for the graph component
        plot_type (str): Type of plot for specific optimizations
        **kwargs: Additional properties for the dcc.Graph component
    
    Returns:
        dcc.Graph: Configured graph component with responsive styling
    """
    from ..config import get_responsive_plotly_config
    
    # Get responsive style configuration
    default_style = get_responsive_plot_style(plot_type)
    
    # Get responsive Plotly configuration
    plot_config = get_responsive_plotly_config(plot_type)
    
    # Merge with any user-provided style
    if 'style' in kwargs:
        default_style.update(kwargs['style'])
        del kwargs['style']
    
    # Merge with any user-provided config
    if 'config' in kwargs:
        plot_config.update(kwargs['config'])
        del kwargs['config']
    
    # Import here to avoid circular imports
    from ..callbacks.graph_callbacks import create_empty_figure
    
    return dcc.Graph(
        id=graph_id,
        style=default_style,
        config=plot_config,
        className='responsive-plot',
        figure=kwargs.pop('figure', create_empty_figure()),
        **kwargs
    )

def add_viewport_detection():
    """Add client-side viewport detection for responsive plot scaling."""
    return html.Div([
        dcc.Store(id='viewport-dimensions', data={'width': 1920, 'height': 1080}),
        dcc.Interval(id='viewport-check-interval', interval=5000, n_intervals=0, disabled=True),
        html.Script("""
        // Detect initial viewport size and update on resize
        function updateViewportDimensions() {
            const width = window.innerWidth;
            const height = window.innerHeight;
            
            // Store dimensions in dcc.Store component
            if (window.dash_clientside) {
                window.dash_clientside.set_props('viewport-dimensions', {
                    data: {width: width, height: height}
                });
            }
        }
        
        // Update on page load and window resize
        window.addEventListener('load', updateViewportDimensions);
        window.addEventListener('resize', updateViewportDimensions);
        
        // Initial update
        updateViewportDimensions();
        """)
    ], id='viewport-detector', style={'display': 'none'})

def add_enhanced_ui_scripts():
    """Add enhanced UI JavaScript and CSS includes."""
    return html.Div([
        html.Link(
            rel="stylesheet",
            href="/static/css/enhanced-desktop-ui.css",
            id="enhanced-ui-css"
        ),
        html.Script(
            src="/static/js/enhanced-ui.js",
            id="enhanced-ui-js"
        ),
        html.Link(
            rel="stylesheet",
            href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css",
            id="font-awesome-css"
        )
    ], id='enhanced-ui-includes', style={'display': 'none'})

# --- Reusable Layout Functions ---
def build_header():
    """Builds the header section with enhanced file upload and status messages."""
    return dbc.Row([
        html.Div(id='output-filename', className="text-primary text-center fs-3 mb-2", children="Please upload a CSV file to begin."),
        dbc.Alert(id='config-warning-alert', color="warning", is_open=False, className="w-75 mx-auto"),
        # Enhanced upload area with better visual feedback
        dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Drag and Drop or Select a CSV File'
            ]),
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
            multiple=False
        )
    ])

def create_filter_controls(control_id_prefix, filter_label):
    """Creates a standardized set of filter controls."""
    return html.Div([
        html.H6(f"Filter by {filter_label}"),
            dcc.RangeSlider(
                id={'type': 'range-slider', 'index': control_id_prefix},
                min=0, max=1, step=0.1, value=[0, 1],
                tooltip={"placement": "bottom", "always_visible": True}, 
                marks=None,
                className="mb-3"
            ),
            dbc.Row([
                dbc.Col(
                    dbc.InputGroup([
                        dbc.InputGroupText("Lower Bound"),
                        dbc.Input(
                            id={'type': 'lower-bound-input', 'index': control_id_prefix}, 
                            type="number", step=0.1, debounce=True
                        )
                    ]), width=6
                ),
                dbc.Col(
                    dbc.InputGroup([
                        dbc.InputGroupText("Upper Bound"),
                        dbc.Input(
                            id={'type': 'upper-bound-input', 'index': control_id_prefix}, 
                            type="number", step=0.1, debounce=True
                        )
                    ]), width=6
                ),
            ]),
            dbc.Row([
                dbc.Col(
                    dbc.InputGroup([
                        dbc.InputGroupText("Slider Min"),
                        dbc.Input(
                            id={'type': 'slider-min-input', 'index': control_id_prefix}, 
                            type="number", step=0.1, debounce=True
                        )
                    ]), width=6
                ),
                dbc.Col(
                    dbc.InputGroup([
                        dbc.InputGroupText("Slider Max"),
                        dbc.Input(
                            id={'type': 'slider-max-input', 'index': control_id_prefix}, 
                            type="number", step=0.1, debounce=True
                        )
                    ]), width=6
                ),
            ]),
    ])

def create_color_scale_controls(control_id_prefix):
    """Creates color scale controls."""
    return html.Div([
        html.H6("Color Scale Range"),
        dbc.Row([
            dbc.Col(
                dbc.InputGroup([
                    dbc.InputGroupText("Color Min"),
                    dbc.Input(
                            id={'type': 'color-min-input', 'index': control_id_prefix}, 
                            type="number", debounce=True
                        )
                    ]), width=6
                ),
                dbc.Col(
                    dbc.InputGroup([
                        dbc.InputGroupText("Color Max"),
                        dbc.Input(
                            id={'type': 'color-max-input', 'index': control_id_prefix}, 
                            type="number", debounce=True
                        )
                    ]), width=6
                ),
            ])
    ])

# --- Tab-Specific Layout Functions ---
def build_main_controls_and_graphs():
    """Builds the enhanced layout for the 'Main 3D Plots' tab with organized controls."""
    return [
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H5("Graph 1 Controls"),
                    dcc.RadioItems(
                        id='radio-buttons-1', 
                        options=[], 
                        value=None, 
                        inline=True,
                        className="mb-3"
                    ),
                    create_filter_controls('zpos-1', 'ZPos')
                ])
            ], width=6),
            dbc.Col([
                html.Div([
                    html.H5("Graph 2 Controls"),
                    dcc.RadioItems(
                        id='radio-buttons-2', 
                        options=[], 
                        value=None, 
                        inline=True,
                        className="mb-3"
                    ),
                    create_filter_controls('zpos-2', 'ZPos')
                ])
            ], width=6)
        ], className="mb-3"),
        dbc.Row([
            dbc.Col([
                dcc.Loading(
                    id="loading-graph-1",
                    type="circle",
                    children=create_responsive_graph('graph-1', 'scatter_3d')
                )
            ], width=6),
            dbc.Col([
                dcc.Loading(
                    id="loading-graph-2",
                    type="circle",
                    children=create_responsive_graph('graph-2', 'scatter_3d')
                )
            ], width=6)
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
        dbc.Row(dbc.Col(create_responsive_graph('graph-2d', 'time_series_2d'), width=12)),
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
        dbc.Row(dbc.Col(create_responsive_graph('custom-graph', 'custom_3d'), width=12)),
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
            html.P("📌 Theme changes apply instantly! Graph option changes apply immediately after saving.", className="text-success small mt-2")
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
        dcc.Loading(id="loading-line-plot", type="circle", children=create_responsive_graph('line-plot-3d', 'toolpath_3d'))
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
        dcc.Loading(id="loading-mesh-plot", type="circle", children=create_responsive_graph('mesh-plot-3d', 'volume_mesh'))
    ])

def build_pyvista_tab():
    """Builds the layout for the PyVista 3D visualization tab with standalone viewer."""
    # Import here to avoid initialization at module import time
    from ..components.standalone_integration import standalone_integration
    
    return html.Div(className="mt-4", children=[
        html.H4("3D Volume Mesh (PyVista Standalone Viewer)"),
        dbc.Alert(
            [
                html.I(className="bi bi-info-circle me-2"),
                "High-performance 3D visualization with full OpenGL support. ",
                html.Strong("Interactive viewer opens in separate window"), " for best performance on your NVIDIA RTX 5090."
            ],
            color="info",
            className="mb-3"
        ),
        # Get the standalone integration component
        standalone_integration.get_component(),
        # Store for mesh data readiness
        dcc.Store(id="pyvista-mesh-ready", data=False)
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
            children=create_responsive_graph('gcode-graph', 'gcode_viz')
        )
    ])

def build_app_body_with_tabs():
    """Constructs the enhanced main tab structure with desktop-optimized navigation."""
    tabs_config = [
        {
            'id': 'main-3d-plots',
            'label': 'Main 3D Plots',
            'content': html.Div(className="mt-4", children=[*build_main_controls_and_graphs()])
        },
        {
            'id': '2d-time-plot',
            'label': '2D Time Plot',
            'content': html.Div(className="mt-4", children=[*build_2d_plotter()])
        },
        {
            'id': 'custom-3d-plot',
            'label': 'Custom 3D Plot',
            'content': html.Div(className="mt-4", children=[*build_custom_plotter()])
        },
        {
            'id': 'data-table',
            'label': 'Data Table',
            'content': html.Div(className="mt-4", children=[build_data_table()])
        },
        {
            'id': '3d-toolpath-plot',
            'label': '3D Toolpath Plot',
            'content': build_line_plot_tab()
        },
        {
            'id': '3d-volume-mesh',
            'label': '3D Volume Mesh',
            'content': build_mesh_plot_tab()
        },
        {
            'id': 'pyvista-3d',
            'label': '3D PyVista (Beta)',
            'content': build_pyvista_tab()
        },
        {
            'id': 'gcode-visualization',
            'label': 'G-code Visualization',
            'content': build_gcode_tab()
        },
        {
            'id': 'settings',
            'label': 'Settings',
            'content': build_config_tab()
        }
    ]
    
    return dbc.Tabs(
        [dbc.Tab(label=tab['label'], tab_id=tab['id'], children=tab['content']) for tab in tabs_config],
        id="tabs",
        active_tab='main-3d-plots'
    )

def get_layout(app):
    """
    Creates the enhanced master layout for the entire application with desktop optimizations.
    This function is called by app.py.
    The 'app' argument is unused but required by the dynamic loader.
    """
    from ..utils.hot_reload import create_theme_injection_component
    
    return html.Div([
        # Hot-reload components for dynamic theme/config updates
        create_theme_injection_component(),
        
        # Viewport detection for responsive plot scaling
        add_viewport_detection(),
        
        dbc.Container([
            # Data stores
            dcc.Store(id='store-main-df'), 
            dcc.Store(id='store-gcode-df'),
            dcc.Store(id='store-layout-config'), 
            dcc.Store(id='store-config-warnings'),
            dcc.Store(id='store-column-ranges'), 
            dcc.Store(id='store-config-updated'),
            
            # Theme update feedback message
            html.Div(id='theme-update-message', style={'display': 'none'}),
            
            build_header(),
            build_app_body_with_tabs(),
        ], fluid=True)
    ])