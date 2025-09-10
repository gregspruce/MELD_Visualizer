# MELD Visualizer Application Guide

## 1. Introduction

Welcome to the MELD Visualizer! This application is a web-based tool built with Dash to visualize 3D process data from MELD manufacturing. It allows users to upload CSV and G-code files, process the data, and render interactive 3D scatter plots, volume meshes, and toolpaths. This guide is designed to help developers with a basic understanding of Python to get acquainted with the codebase and start contributing.

## 2. Core Concepts: A Quick Intro to Dash

This application is built using [Dash](https://dash.plotly.com/), a Python framework for building analytical web applications. You don't need to be a web development expert to work with Dash. Here are the two core concepts:

### Layout

The layout is the structure of the user interface. It's a tree of components, like `html.Div`, `dcc.Graph`, or `dbc.Button`, that describe what the application looks like. In our application, the layout is primarily defined in `src/meld_visualizer/core/layout.py`. It uses `dash_bootstrap_components` for styling.

**Example from `src/meld_visualizer/core/layout.py`:**

```python
def create_main_layout():
    """Creates the main layout of the application."""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1("MELD Data Visualizer"),
                dcc.Upload(
                    id='upload-data',
                    children=html.Div([
                        'Drag and Drop or ',
                        html.A('Select Files')
                    ]),
                    # ...
                )
            ])
        ]),
        dbc.Row([
            dbc.Col([
                dcc.Graph(id='3d-scatter-plot')
            ])
        ])
    ], fluid=True)
```

### Callbacks

Callbacks are Python functions that are automatically called by Dash whenever an input component's property changes. Callbacks are the heart of the application's interactivity. For example, a callback might update a graph when a user selects a new dataset from a dropdown. In our app, all callbacks are located in the `src/meld_visualizer/callbacks/` directory, organized into modules based on their functionality.

**Example of a callback from `src/meld_visualizer/callbacks/graph_callbacks.py`:**

```python
from dash import dcc, html, Input, Output, State, callback

@callback(
    Output('3d-scatter-plot', 'figure'),
    [Input('processed-data-store', 'data')]
)
def update_3d_scatter_plot(json_data):
    if not json_data:
        return go.Figure()

    df = pd.read_json(json_data, orient='split')

    figure = px.scatter_3d(
        df,
        x='XPos',
        y='YPos',
        z='ZPos',
        color='ToolTemp',
        # ...
    )
    return figure
```
In this example, the `update_3d_scatter_plot` function is decorated with `@callback`. This tells Dash to call this function whenever the `data` property of the component with the ID `processed-data-store` changes. The function then returns a new figure, which updates the `figure` property of the `3d-scatter-plot` component.

## 3. Callback Chains and Data Flow

A common source of confusion is how callbacks interact with each other. In Dash, it's common to have **callback chains**, where the output of one callback is the input to another. This creates a data flow pipeline within the application.

### Using `dcc.Store` for State Management

To manage state and share data between callbacks, we use `dcc.Store`. This component allows you to store data in the user's browser without displaying it. It acts as an intermediary data store.

**Example of a callback chain:**

1.  **`data_callbacks.py`**: A callback is triggered when a user uploads a file. This callback processes the file and stores the resulting DataFrame (as JSON) in a `dcc.Store` component with the ID `processed-data-store`.

    ```python
    @callback(
        Output('processed-data-store', 'data'),
        Input('upload-data', 'contents'),
        State('upload-data', 'filename')
    )
    def update_store(contents, filename):
        if contents is None:
            return None
        df = parse_contents(contents, filename)
        return df.to_json(date_format='iso', orient='split')
    ```

2.  **`graph_callbacks.py`**: Another callback listens for changes to the `processed-data-store`. When the data changes, this callback is triggered, and it updates the graph.

    ```python
    @callback(
        Output('3d-scatter-plot', 'figure'),
        Input('processed-data-store', 'data')
    )
    def update_graph(json_data):
        if json_data is None:
            return {}
        df = pd.read_json(json_data, orient='split')
        # ... create figure ...
        return figure
    ```

Understanding these chains is crucial for debugging. If a graph is not updating, you should trace the data flow back through the callback chain to see where the data is being lost or incorrectly processed.

## 4. UI and Styling

### UI Creation

The UI of the MELD Visualizer is built entirely in Python using Dash components. The main layout is defined in `src/meld_visualizer/core/layout.py`. This file contains the functions that create the different parts of the UI, such as the header, the control panels, and the graph components.

### Styling with CSS and the `static` folder

The `static` folder (`src/meld_visualizer/static/`) is used for custom CSS and JavaScript files that are not part of the standard Dash or Bootstrap libraries. Dash automatically serves the files in the `assets` folder (which is configured to be our `static` folder in `app.py`).

-   **`static/css`**: This folder can contain custom CSS files to override the default styles of the components.
-   **`static/js`**: This folder can contain custom JavaScript files to add client-side interactivity.

To add a custom CSS file, simply create a new `.css` file in the `static/css` directory. Dash will automatically include it in the application's header.

## 5. Project Structure

The project is organized into the following main directories and files:

```
MELD_Visualizer/
├── src/
│   └── meld_visualizer/
│       ├── __init__.py           # Initializes the package
│       ├── __main__.py           # Main entry point for python -m
│       ├── app.py                # Creates the Dash app instance
│       ├── config.py             # Handles theme and configuration loading
│       ├── constants.py          # Application-wide constants
│       ├── callbacks/            # All Dash callbacks (interactivity)
│       ├── core/                 # Core application logic
│       ├── services/             # Application services
│       ├── static/               # Static assets (CSS, JS)
│       └── utils/                # Utility functions
├── config/
│   └── config.json             # User configuration file
├── data/                       # Sample data files
└── tests/                      # Application tests
```

## 6. Application Flow

1.  **Initialization**: The application is started by running `python -m src.meld_visualizer`.
2.  **Dash App Creation**: `create_app()` in `app.py` creates the Dash app instance.
3.  **Configuration Loading**: `config.py` loads settings from `config/config.json`.
4.  **Layout Definition**: `_build_layout()` in `app.py` calls `get_layout()` from `core/layout.py` to build the UI.
5.  **Callback Registration**: `_register_callbacks()` in `app.py` registers all callbacks from the `callbacks/` directory.
6.  **Server Start**: `app.run()` starts the web server.
7.  **User Interaction**: An interaction triggers a callback, which can update `dcc.Store` components or UI components like graphs.

## 7. Key Modules

(Sections on Key Modules, How to Run, Configuration, and Contributing remain the same as the previous version)

## 8. Contributing

If you want to contribute to the project, here are some tips:

-   **Adding a new UI component**:
    1.  Add the component to the `layout.py` file.
    2.  If the component is interactive, give it a unique `id`.
-   **Adding interactivity**:
    1.  Create a new callback function in the appropriate file in the `callbacks` directory.
    2.  Use the `@callback` decorator to define the `Input`, `Output`, and `State` of the callback.
    3.  If you need to share data between callbacks, use a `dcc.Store` component.
-   **Modifying data processing**:
    1.  Open the `data_processing.py` file in the `core` module.
-   **Changing the theme**:
    1.  You can change the default theme in `config/config.json`.

We hope this guide helps you get started with the MELD Visualizer codebase!
