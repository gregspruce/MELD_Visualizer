# Enhanced UI Developer Guide

## Quick Start Guide

This guide provides practical examples and patterns for developers working with the Enhanced UI components in the MELD Visualizer.

## Table of Contents

1. [Setup and Installation](#setup-and-installation)
2. [Basic Component Usage](#basic-component-usage)
3. [Creating Enhanced Layouts](#creating-enhanced-layouts)
4. [Implementing User Feedback](#implementing-user-feedback)
5. [Responsive Design Patterns](#responsive-design-patterns)
6. [Callback Integration](#callback-integration)
7. [Best Practices](#best-practices)
8. [Code Examples](#code-examples)

---

## Setup and Installation

### 1. Import Required Components

```python
# Core imports
from dash import dcc, html, callback, Input, Output, State
import dash_bootstrap_components as dbc

# Enhanced UI imports
from meld_visualizer.core.enhanced_ui import (
    EnhancedUIComponents,
    UserFeedbackManager,
    ResponsiveLayoutManager
)
from meld_visualizer.callbacks.enhanced_ui_callbacks import register_enhanced_ui_callbacks
```

### 2. Initialize Enhanced UI in Your Layout

```python
def create_app_layout():
    return html.Div([
        # Essential Enhanced UI includes
        add_enhanced_ui_scripts(),
        add_viewport_detection(),
        
        # UI State stores
        dcc.Store(id='ui-state-store', data={}),
        dcc.Store(id='loading-state-store', data={'show': False}),
        dcc.Store(id='toast-trigger-store', data=0),
        
        # Toast container for notifications
        EnhancedUIComponents.create_toast_container(),
        
        # Your app content
        build_app_content()
    ])
```

### 3. Register Enhanced UI Callbacks

```python
def create_app():
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    
    # Set layout
    app.layout = create_app_layout()
    
    # Register callbacks
    register_enhanced_ui_callbacks(app)
    register_your_callbacks(app)
    
    return app
```

---

## Basic Component Usage

### Creating Enhanced Tabs

```python
# Basic tab creation
tabs = EnhancedUIComponents.create_enhanced_tabs(
    tabs_config=[
        {
            'id': 'data-tab',
            'label': 'Data Analysis',
            'content': html.Div([
                html.H3("Data Analysis Panel"),
                # Your data components here
            ])
        },
        {
            'id': 'viz-tab',
            'label': 'Visualization',
            'content': html.Div([
                html.H3("Visualization Panel"),
                # Your visualization components here
            ])
        },
        {
            'id': 'settings-tab',
            'label': 'Settings',
            'content': html.Div([
                html.H3("Settings Panel"),
                # Your settings components here
            ])
        }
    ],
    active_tab='data-tab'  # Set initial active tab
)
```

### Creating Control Panels

```python
# Collapsible control panel with grouped controls
control_panel = EnhancedUIComponents.create_control_panel(
    title="Filter Controls",
    panel_id="filter-panel",
    collapsible=True,
    initial_collapsed=False,
    controls=[
        # Group 1: Time filters
        EnhancedUIComponents.create_control_group(
            title="Time Range",
            controls=[
                dcc.DatePickerRange(
                    id='date-range',
                    start_date='2024-01-01',
                    end_date='2024-12-31',
                    display_format='YYYY-MM-DD'
                ),
                dcc.RangeSlider(
                    id='time-slider',
                    min=0, max=24,
                    value=[8, 17],
                    marks={i: f'{i}:00' for i in range(0, 25, 6)}
                )
            ]
        ),
        
        # Group 2: Data filters
        EnhancedUIComponents.create_control_group(
            title="Data Selection",
            controls=[
                dcc.Dropdown(
                    id='data-source',
                    options=[
                        {'label': 'Sensor A', 'value': 'sensor_a'},
                        {'label': 'Sensor B', 'value': 'sensor_b'},
                        {'label': 'Sensor C', 'value': 'sensor_c'}
                    ],
                    multi=True,
                    placeholder="Select data sources"
                ),
                dcc.Checklist(
                    id='data-options',
                    options=[
                        {'label': 'Include outliers', 'value': 'outliers'},
                        {'label': 'Show averages', 'value': 'averages'},
                        {'label': 'Display trends', 'value': 'trends'}
                    ],
                    value=['averages']
                )
            ]
        ),
        
        # Action buttons
        html.Div([
            dbc.Button("Apply Filters", id="apply-filters", color="primary", className="me-2"),
            dbc.Button("Reset", id="reset-filters", color="secondary")
        ], className="mt-3")
    ]
)
```

### Creating Enhanced Input Groups

```python
# Input group with label and help text
input_group = EnhancedUIComponents.create_enhanced_input_group(
    label="Threshold Value",
    input_component=dcc.Input(
        id='threshold-input',
        type='number',
        min=0, max=100,
        value=50,
        step=1
    ),
    help_text="Enter a value between 0 and 100"
)

# Multiple input groups in a form
form_layout = html.Div([
    EnhancedUIComponents.create_enhanced_input_group(
        label="Sample Name",
        input_component=dcc.Input(
            id='sample-name',
            type='text',
            placeholder='Enter sample name'
        )
    ),
    
    EnhancedUIComponents.create_enhanced_input_group(
        label="Temperature (°C)",
        input_component=dcc.Input(
            id='temperature',
            type='number',
            placeholder='20.0'
        ),
        help_text="Operating temperature in Celsius"
    ),
    
    EnhancedUIComponents.create_enhanced_input_group(
        label="Comments",
        input_component=dcc.Textarea(
            id='comments',
            placeholder='Additional notes...',
            style={'width': '100%', 'height': 100}
        )
    )
])
```

### Creating Upload Areas

```python
# Enhanced file upload area
upload_area = EnhancedUIComponents.create_enhanced_upload_area(
    upload_id='file-upload',
    message='Drag and Drop or Click to Select Files',
    accepted_types='.csv,.xlsx,.json'
)

# Complete upload section with feedback
upload_section = html.Div([
    html.H4("Data Import"),
    upload_area,
    html.Div(id='upload-output', className='mt-3'),
    dcc.Store(id='uploaded-data')
])
```

---

## Creating Enhanced Layouts

### Full Page Layout Example

```python
def create_full_layout():
    return html.Div([
        # Header section
        dbc.Row([
            dbc.Col([
                html.H1("MELD Visualizer", className="text-primary"),
                html.P("Enhanced Desktop Interface", className="text-muted")
            ])
        ], className="mb-4"),
        
        # Main content with sidebar
        dbc.Row([
            # Sidebar with control panels
            dbc.Col([
                EnhancedUIComponents.create_control_panel(
                    title="Data Controls",
                    panel_id="data-controls",
                    controls=[create_data_controls()]
                ),
                EnhancedUIComponents.create_control_panel(
                    title="Display Options",
                    panel_id="display-options",
                    controls=[create_display_options()],
                    initial_collapsed=True
                )
            ], width=3),
            
            # Main content area with tabs
            dbc.Col([
                EnhancedUIComponents.create_enhanced_tabs(
                    tabs_config=create_main_tabs(),
                    active_tab='overview'
                )
            ], width=9)
        ]),
        
        # Hidden components
        EnhancedUIComponents.create_toast_container(),
        create_stores(),
        add_enhanced_ui_scripts()
    ])
```

### Responsive Layout with Breakpoints

```python
def create_responsive_layout():
    return html.Div([
        # Store for viewport dimensions
        dcc.Store(id='viewport-dimensions'),
        
        # Layout container that adjusts based on viewport
        html.Div(id='responsive-container')
    ])

@callback(
    Output('responsive-container', 'children'),
    Input('viewport-dimensions', 'data')
)
def update_responsive_layout(viewport_data):
    if not viewport_data:
        viewport_data = {'width': 1920, 'height': 1080}
    
    # Get responsive configuration
    layout_config = ResponsiveLayoutManager.get_layout_config(
        viewport_data['width']
    )
    
    # Build layout based on configuration
    if layout_config['columns_per_row'] == 2:
        # Two-column layout for larger screens
        return dbc.Row([
            dbc.Col(create_sidebar(), width=layout_config['control_panel_width']),
            dbc.Col(create_main_content(), width=layout_config['plot_width'])
        ])
    else:
        # Single column for smaller screens
        return html.Div([
            create_collapsible_sidebar(
                collapsed=layout_config['sidebar_collapsed']
            ),
            create_main_content()
        ])
```

---

## Implementing User Feedback

### Toast Notifications

```python
# Success toast after file upload
@callback(
    [Output('toast-trigger-store', 'data'),
     Output('ui-state-store', 'data')],
    Input('file-upload', 'contents'),
    [State('file-upload', 'filename'),
     State('toast-trigger-store', 'data'),
     State('ui-state-store', 'data')],
    prevent_initial_call=True
)
def handle_file_upload(contents, filename, trigger, ui_state):
    if not contents:
        raise PreventUpdate
    
    try:
        # Process file
        data = process_uploaded_file(contents, filename)
        
        # Create success toast
        toast = UserFeedbackManager.create_toast_component(
            toast_type="success",
            title="Upload Complete",
            message=f"Successfully loaded {filename}",
            duration=4000
        )
        
        ui_state['last_toast'] = toast
        return trigger + 1, ui_state
        
    except Exception as e:
        # Create error toast
        toast = UserFeedbackManager.create_toast_component(
            toast_type="error",
            title="Upload Failed",
            message=str(e),
            duration=6000
        )
        
        ui_state['last_toast'] = toast
        return trigger + 1, ui_state
```

### Loading States

```python
# Show loading overlay during processing
@callback(
    [Output('loading-state-store', 'data'),
     Output('processed-data', 'data')],
    Input('process-button', 'n_clicks'),
    State('raw-data', 'data'),
    prevent_initial_call=True
)
def process_with_loading(n_clicks, raw_data):
    if not n_clicks or not raw_data:
        raise PreventUpdate
    
    # Show loading overlay
    yield {'show': True, 'message': 'Processing data...'}, dash.no_update
    
    # Perform processing
    processed_data = perform_heavy_processing(raw_data)
    
    # Hide loading and return data
    yield {'show': False, 'message': ''}, processed_data
```

### Progress Indicators

```python
# Multi-stage progress indicator
@callback(
    [Output('progress-container', 'children'),
     Output('processing-complete', 'data')],
    Input('start-processing', 'n_clicks'),
    prevent_initial_call=True
)
def process_with_progress(n_clicks):
    if not n_clicks:
        raise PreventUpdate
    
    stages = [
        ("Loading data", 0.2),
        ("Preprocessing", 0.3),
        ("Analysis", 0.3),
        ("Generating output", 0.2)
    ]
    
    total_progress = 0
    
    for stage_name, stage_weight in stages:
        # Update progress indicator
        progress_component = EnhancedUIComponents.create_progress_indicator(
            title=stage_name,
            progress_id="processing-progress",
            initial_value=int(total_progress * 100),
            max_value=100
        )
        
        yield progress_component, False
        
        # Simulate processing
        time.sleep(1)  # Replace with actual processing
        total_progress += stage_weight
    
    # Final update
    final_progress = EnhancedUIComponents.create_progress_indicator(
        title="Complete!",
        progress_id="processing-progress",
        initial_value=100,
        max_value=100
    )
    
    yield final_progress, True
```

---

## Responsive Design Patterns

### Viewport-Aware Components

```python
@callback(
    Output('plot-container', 'children'),
    Input('viewport-dimensions', 'data'),
    State('plot-data', 'data')
)
def create_responsive_plot(viewport, data):
    if not viewport or not data:
        raise PreventUpdate
    
    width = viewport.get('width', 1920)
    height = viewport.get('height', 1080)
    
    # Adjust plot dimensions based on viewport
    plot_height = min(height * 0.7, 600)
    plot_width = width - 300 if width > 1440 else width - 100
    
    figure = create_plot_figure(data)
    figure.update_layout(
        height=plot_height,
        width=plot_width,
        margin=dict(l=50, r=50, t=50, b=50)
    )
    
    return dcc.Graph(figure=figure, config={'responsive': True})
```

### Adaptive Control Panels

```python
def create_adaptive_controls(viewport_width):
    """Create control panels that adapt to screen size"""
    
    # Determine layout based on width
    if viewport_width >= 1920:
        # Large screen: Expanded controls
        return create_expanded_controls()
    elif viewport_width >= 1440:
        # Medium screen: Standard controls
        return create_standard_controls()
    else:
        # Small screen: Compact controls
        return create_compact_controls()

def create_expanded_controls():
    return EnhancedUIComponents.create_control_panel(
        title="Advanced Controls",
        collapsible=False,
        controls=[
            # Multiple columns of controls
            dbc.Row([
                dbc.Col(create_filter_controls(), width=6),
                dbc.Col(create_display_controls(), width=6)
            ]),
            dbc.Row([
                dbc.Col(create_analysis_controls(), width=12)
            ])
        ]
    )

def create_compact_controls():
    return EnhancedUIComponents.create_control_panel(
        title="Controls",
        collapsible=True,
        initial_collapsed=True,
        controls=[
            # Single column, essential controls only
            create_essential_controls()
        ]
    )
```

---

## Callback Integration

### Complex Callback with Multiple UI Updates

```python
@callback(
    [Output('data-table', 'data'),
     Output('summary-stats', 'children'),
     Output('toast-trigger-store', 'data'),
     Output('ui-state-store', 'data'),
     Output('loading-state-store', 'data')],
    [Input('analyze-button', 'n_clicks'),
     Input('filter-dropdown', 'value')],
    [State('raw-data', 'data'),
     State('toast-trigger-store', 'data'),
     State('ui-state-store', 'data')],
    prevent_initial_call=True
)
def analyze_data_with_feedback(n_clicks, filter_value, raw_data, trigger, ui_state):
    """Complex callback with multiple UI feedback elements"""
    
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate
    
    # Show loading state
    loading_state = {'show': True, 'message': 'Analyzing data...'}
    
    try:
        # Filter data
        filtered_data = apply_filters(raw_data, filter_value)
        
        # Calculate statistics
        stats = calculate_statistics(filtered_data)
        
        # Create summary display
        summary = create_summary_display(stats)
        
        # Success notification
        toast = UserFeedbackManager.create_toast_component(
            toast_type="success",
            title="Analysis Complete",
            message=f"Analyzed {len(filtered_data)} records",
            duration=3000
        )
        ui_state['last_toast'] = toast
        
        # Hide loading
        loading_state = {'show': False, 'message': ''}
        
        return filtered_data, summary, trigger + 1, ui_state, loading_state
        
    except Exception as e:
        # Error handling with user feedback
        toast = UserFeedbackManager.create_toast_component(
            toast_type="error",
            title="Analysis Failed",
            message=str(e),
            duration=5000
        )
        ui_state['last_toast'] = toast
        loading_state = {'show': False, 'message': ''}
        
        return dash.no_update, html.Div("Error occurred"), trigger + 1, ui_state, loading_state
```

### Chained Callbacks with Progress

```python
# Store for tracking multi-step process
@callback(
    Output('process-state', 'data'),
    Input('start-process', 'n_clicks'),
    prevent_initial_call=True
)
def initiate_process(n_clicks):
    if not n_clicks:
        raise PreventUpdate
    
    return {
        'status': 'started',
        'step': 1,
        'total_steps': 4,
        'timestamp': datetime.now().isoformat()
    }

# Step 1: Load data
@callback(
    [Output('process-state', 'data', allow_duplicate=True),
     Output('step1-output', 'data')],
    Input('process-state', 'data'),
    prevent_initial_call=True
)
def step1_load_data(process_state):
    if not process_state or process_state.get('step') != 1:
        raise PreventUpdate
    
    # Load data
    data = load_data_from_source()
    
    # Update state
    process_state['step'] = 2
    process_state['step1_complete'] = True
    
    return process_state, data

# Continue with remaining steps...
```

---

## Best Practices

### 1. Component Organization

```python
# Organize components in logical functions
def create_data_section():
    """Create the data management section"""
    return html.Div([
        create_upload_area(),
        create_data_table(),
        create_data_controls()
    ])

def create_visualization_section():
    """Create the visualization section"""
    return html.Div([
        create_plot_controls(),
        create_plot_area(),
        create_export_options()
    ])
```

### 2. State Management

```python
# Use consistent state structure
UI_STATE_SCHEMA = {
    'viewport': {
        'width': int,
        'height': int,
        'breakpoint': str
    },
    'panels': {
        'panel_id': {
            'collapsed': bool,
            'last_updated': str
        }
    },
    'notifications': {
        'last_toast': dict,
        'toast_queue': list
    },
    'performance': {
        'last_render_time': float,
        'component_metrics': dict
    }
}

# Validate state updates
def update_ui_state(current_state, updates):
    """Safely update UI state with validation"""
    if not current_state:
        current_state = create_default_state()
    
    # Merge updates
    new_state = {**current_state, **updates}
    
    # Validate against schema
    validate_state(new_state, UI_STATE_SCHEMA)
    
    return new_state
```

### 3. Error Handling

```python
def safe_component_render(component_func, *args, **kwargs):
    """Safely render components with error handling"""
    try:
        return component_func(*args, **kwargs)
    except Exception as e:
        logger.error(f"Component render failed: {e}")
        return html.Div([
            html.I(className="fas fa-exclamation-triangle text-warning me-2"),
            html.Span("Component failed to load"),
            html.Small(str(e), className="d-block text-muted")
        ], className="alert alert-warning")
```

### 4. Performance Optimization

```python
# Use memoization for expensive computations
from functools import lru_cache

@lru_cache(maxsize=128)
def create_complex_layout(config_hash):
    """Cache complex layout generation"""
    config = deserialize_config(config_hash)
    return generate_layout(config)

# Debounce rapid updates
from dash import ctx
import time

last_update_time = {}

@callback(
    Output('debounced-output', 'children'),
    Input('rapid-input', 'value')
)
def debounced_update(value):
    trigger_id = ctx.triggered_id
    current_time = time.time()
    
    # Check if we should debounce
    if trigger_id in last_update_time:
        if current_time - last_update_time[trigger_id] < 0.5:
            raise PreventUpdate
    
    last_update_time[trigger_id] = current_time
    
    return process_value(value)
```

### 5. Accessibility

```python
def create_accessible_component(content, label, description=None):
    """Create component with accessibility attributes"""
    component_id = f"component-{uuid.uuid4().hex[:8]}"
    
    return html.Div([
        html.Label(label, htmlFor=component_id, className="visually-hidden"),
        html.Div(
            content,
            id=component_id,
            role="region",
            **{'aria-label': label, 'aria-describedby': f"{component_id}-desc" if description else None}
        ),
        html.Span(description, id=f"{component_id}-desc", className="visually-hidden") if description else None
    ])
```

---

## Code Examples

### Complete Dashboard Example

```python
import dash
from dash import dcc, html, callback, Input, Output, State
import dash_bootstrap_components as dbc
from meld_visualizer.core.enhanced_ui import EnhancedUIComponents, UserFeedbackManager

def create_dashboard():
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    
    # Create layout
    app.layout = html.Div([
        # Enhanced UI includes
        add_enhanced_ui_scripts(),
        add_viewport_detection(),
        
        # Header
        dbc.NavbarSimple(
            brand="MELD Dashboard",
            brand_href="#",
            color="primary",
            dark=True,
            className="mb-4"
        ),
        
        # Main container
        dbc.Container([
            # Row 1: Controls
            dbc.Row([
                dbc.Col([
                    EnhancedUIComponents.create_control_panel(
                        title="Data Source",
                        panel_id="data-source-panel",
                        controls=[
                            EnhancedUIComponents.create_enhanced_upload_area(
                                upload_id='data-upload',
                                message='Upload CSV or Excel file',
                                accepted_types='.csv,.xlsx'
                            )
                        ]
                    )
                ], width=12)
            ], className="mb-4"),
            
            # Row 2: Main content
            dbc.Row([
                dbc.Col([
                    EnhancedUIComponents.create_enhanced_tabs([
                        {
                            'id': 'overview-tab',
                            'label': 'Overview',
                            'content': create_overview_content()
                        },
                        {
                            'id': 'analysis-tab',
                            'label': 'Analysis',
                            'content': create_analysis_content()
                        },
                        {
                            'id': 'reports-tab',
                            'label': 'Reports',
                            'content': create_reports_content()
                        }
                    ])
                ], width=12)
            ])
        ], fluid=True),
        
        # Hidden components
        EnhancedUIComponents.create_toast_container(),
        dcc.Store(id='app-data'),
        dcc.Store(id='ui-state-store', data={}),
        dcc.Store(id='toast-trigger-store', data=0)
    ])
    
    # Register callbacks
    register_dashboard_callbacks(app)
    
    return app

def register_dashboard_callbacks(app):
    """Register all dashboard callbacks"""
    
    @app.callback(
        [Output('app-data', 'data'),
         Output('toast-trigger-store', 'data'),
         Output('ui-state-store', 'data')],
        Input('data-upload', 'contents'),
        [State('data-upload', 'filename'),
         State('toast-trigger-store', 'data'),
         State('ui-state-store', 'data')],
        prevent_initial_call=True
    )
    def handle_upload(contents, filename, trigger, ui_state):
        if not contents:
            raise PreventUpdate
        
        try:
            # Process upload
            data = process_file(contents, filename)
            
            # Success feedback
            toast = UserFeedbackManager.create_toast_component(
                toast_type="success",
                title="Data Loaded",
                message=f"Successfully loaded {len(data)} records from {filename}",
                duration=4000
            )
            ui_state['last_toast'] = toast
            
            return data, trigger + 1, ui_state
            
        except Exception as e:
            # Error feedback
            toast = UserFeedbackManager.create_toast_component(
                toast_type="error",
                title="Upload Failed",
                message=str(e),
                duration=6000
            )
            ui_state['last_toast'] = toast
            
            return None, trigger + 1, ui_state

if __name__ == '__main__':
    app = create_dashboard()
    app.run_server(debug=True)
```

---

*Developer Guide Version: 1.0.0*  
*Last Updated: January 2025*  
*For MELD Visualizer Enhanced UI v2.0*