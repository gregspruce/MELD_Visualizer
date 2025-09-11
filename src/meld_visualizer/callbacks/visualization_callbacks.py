"""
3D visualization callbacks.
Handles line plots, mesh generation, and G-code visualization.
"""

import io
import logging

import pandas as pd
import plotly.graph_objects as go
from dash import Input, Output, State, callback
from dash.exceptions import PreventUpdate

from ..config import PLOTLY_TEMPLATE, TABLE_STYLE_DARK, TABLE_STYLE_LIGHT
from ..constants import (
    DEFAULT_CAMERA_POSITION,
    DEFAULT_COLORSCALE,
    DEFAULT_LINE_WIDTH,
    DEFAULT_MARKER_SIZE,
    DEFAULT_Z_STRETCH_FACTOR,
    ERROR_MESH_GENERATION,
    ERROR_NO_ACTIVE_DATA,
    MIN_FEED_VELOCITY,
    MIN_Z_STRETCH_FACTOR,
)
from ..services import get_data_service
from .graph_callbacks import create_empty_figure

logger = logging.getLogger(__name__)


def register_visualization_callbacks(app=None):
    """Register 3D visualization callbacks."""

    data_service = get_data_service()

    @callback(
        Output("line-plot-3d", "figure"),
        Input("generate-line-plot-button", "n_clicks"),
        [State("store-main-df", "data"), State("line-plot-z-stretch-input", "value")],
        prevent_initial_call=True,
    )
    def update_line_plot(n_clicks, jsonified_df, z_stretch_factor):
        """Generate 3D toolpath line plot from active extrusion data."""
        if n_clicks is None or jsonified_df is None:
            return create_empty_figure("Upload a file and click 'Generate'.")

        df = pd.read_json(io.StringIO(jsonified_df), orient="split")
        df_active = data_service.filter_active_data(df)

        if df_active.empty:
            return create_empty_figure(ERROR_NO_ACTIVE_DATA)

        # Validate Z-stretch factor
        if not z_stretch_factor or float(z_stretch_factor) <= 0:
            z_stretch_factor = DEFAULT_Z_STRETCH_FACTOR

        z_stretch_factor = max(MIN_Z_STRETCH_FACTOR, float(z_stretch_factor))
        aspect_ratio = dict(x=1, y=1, z=z_stretch_factor)

        fig = go.Figure(
            data=[
                go.Scatter3d(
                    x=df_active["XPos"],
                    y=df_active["YPos"],
                    z=df_active["ZPos"],
                    mode="lines+markers",
                    marker=dict(size=DEFAULT_MARKER_SIZE),
                    line=dict(width=DEFAULT_LINE_WIDTH),
                )
            ]
        )

        fig.update_layout(
            title="3D Toolpath Visualization (Active Extrusion Only)",
            template=PLOTLY_TEMPLATE,
            scene=dict(
                xaxis_title="X Position (mm)",
                yaxis_title="Y Position (mm)",
                zaxis_title="Z Position (mm)",
                aspectmode="data" if z_stretch_factor == 1.0 else "manual",
                aspectratio=aspect_ratio,
                camera=dict(
                    eye=dict(
                        x=DEFAULT_CAMERA_POSITION["x"],
                        y=DEFAULT_CAMERA_POSITION["y"],
                        z=DEFAULT_CAMERA_POSITION["z"],
                    ),
                    center=dict(x=0, y=0, z=0),
                    up=dict(x=0, y=0, z=1),
                ),
            ),
        )

        return fig

    @callback(
        Output({"type": "color-min-input", "index": "mesh-plot"}, "value"),
        Output({"type": "color-max-input", "index": "mesh-plot"}, "value"),
        Input("mesh-plot-color-dropdown", "value"),
        State("store-column-ranges", "data"),
        prevent_initial_call=True,
    )
    def update_color_range_for_mesh_plot(color_col, ranges):
        """Automatically update min/max color range inputs when color dropdown changes."""
        if not color_col or not ranges:
            raise PreventUpdate

        min_val, max_val = ranges.get(color_col, [None, None])
        return min_val, max_val

    @callback(
        Output("mesh-plot-3d", "figure"),
        Input("generate-mesh-plot-button", "n_clicks"),
        [
            State("store-main-df", "data"),
            State("mesh-plot-color-dropdown", "value"),
            State({"type": "color-min-input", "index": "mesh-plot"}, "value"),
            State({"type": "color-max-input", "index": "mesh-plot"}, "value"),
            State("mesh-plot-z-stretch-input", "value"),
        ],
        prevent_initial_call=True,
    )
    def update_mesh_plot(n_clicks, jsonified_df, color_col, cmin, cmax, z_stretch_factor):
        """Generate 3D volume mesh plot."""
        if n_clicks is None or jsonified_df is None or color_col is None:
            return create_empty_figure("Upload a file, select a color, and click 'Generate'.")

        df = pd.read_json(io.StringIO(jsonified_df), orient="split")
        df_active = data_service.filter_active_data(df)

        if df_active.empty:
            return create_empty_figure(ERROR_NO_ACTIVE_DATA)

        # Generate mesh with LOD support
        mesh_data = data_service.generate_mesh(df_active, color_col, lod="high")

        if mesh_data is None:
            return create_empty_figure(ERROR_MESH_GENERATION)

        # Validate Z-stretch factor
        if not z_stretch_factor or float(z_stretch_factor) <= 0:
            z_stretch_factor = DEFAULT_Z_STRETCH_FACTOR

        z_stretch_factor = max(MIN_Z_STRETCH_FACTOR, float(z_stretch_factor))
        aspect_ratio = dict(x=1, y=1, z=z_stretch_factor)

        fig = go.Figure(
            data=[
                go.Mesh3d(
                    x=mesh_data["vertices"][:, 0],
                    y=mesh_data["vertices"][:, 1],
                    z=mesh_data["vertices"][:, 2],
                    i=mesh_data["faces"][:, 0],
                    j=mesh_data["faces"][:, 1],
                    k=mesh_data["faces"][:, 2],
                    colorscale=DEFAULT_COLORSCALE,
                    intensity=mesh_data["vertex_colors"],
                    colorbar=dict(title=color_col),
                    showscale=True,
                    cmin=cmin,
                    cmax=cmax,
                )
            ]
        )

        fig.update_layout(
            title="3D Mesh Visualization of the Print",
            template=PLOTLY_TEMPLATE,
            scene=dict(
                xaxis_title="X Position (mm)",
                yaxis_title="Y Position (mm)",
                zaxis_title="Z Position (mm)",
                aspectmode="data" if z_stretch_factor == 1.0 else "manual",
                aspectratio=aspect_ratio,
                camera=dict(
                    eye=dict(
                        x=DEFAULT_CAMERA_POSITION["x"],
                        y=DEFAULT_CAMERA_POSITION["y"],
                        z=DEFAULT_CAMERA_POSITION["z"],
                    ),
                    center=dict(x=0, y=0, z=0),
                    up=dict(x=0, y=0, z=1),
                ),
            ),
        )

        return fig

    @callback(
        Output("gcode-graph", "figure"),
        Input("generate-gcode-viz-button", "n_clicks"),
        [
            State("store-gcode-df", "data"),
            State("gcode-view-selector", "value"),
            State("gcode-z-stretch-input", "value"),
        ],
        prevent_initial_call=True,
    )
    def update_gcode_visualization(n_clicks, jsonified_df, view_mode, z_stretch_factor):
        """Generate G-code visualization (toolpath or mesh)."""
        if n_clicks is None or jsonified_df is None:
            return create_empty_figure("Please upload a G-code file and click 'Generate'.")

        df = pd.read_json(io.StringIO(jsonified_df), orient="split")
        df_active = df[df["FeedVel"] > MIN_FEED_VELOCITY].copy()

        if df_active.empty:
            return create_empty_figure("No active extrusion moves (M34) found in G-code file.")

        # Validate Z-stretch factor
        if not z_stretch_factor or float(z_stretch_factor) <= 0:
            z_stretch_factor = DEFAULT_Z_STRETCH_FACTOR

        z_stretch_factor = max(MIN_Z_STRETCH_FACTOR, float(z_stretch_factor))
        custom_aspect_ratio = dict(x=1, y=1, z=z_stretch_factor)

        if view_mode == "toolpath":
            fig = go.Figure(
                data=[
                    go.Scatter3d(
                        x=df_active["XPos"],
                        y=df_active["YPos"],
                        z=df_active["ZPos"],
                        mode="lines+markers",
                        marker=dict(size=DEFAULT_MARKER_SIZE),
                        line=dict(width=DEFAULT_LINE_WIDTH),
                    )
                ]
            )

            fig.update_layout(
                title="Simulated 3D Toolpath (Active Extrusion Only)",
                template=PLOTLY_TEMPLATE,
                scene=dict(
                    xaxis_title="X Position (mm)",
                    yaxis_title="Y Position (mm)",
                    zaxis_title="Z Position (mm)",
                    aspectmode="data" if z_stretch_factor == 1.0 else "manual",
                    aspectratio=custom_aspect_ratio,
                    camera=dict(
                        eye=dict(
                            x=DEFAULT_CAMERA_POSITION["x"],
                            y=DEFAULT_CAMERA_POSITION["y"],
                            z=DEFAULT_CAMERA_POSITION["z"],
                        ),
                        center=dict(x=0, y=0, z=0),
                        up=dict(x=0, y=0, z=1),
                    ),
                ),
            )

            return fig

        elif view_mode == "mesh":
            color_col = "ZPos"
            mesh_data = data_service.generate_mesh(df_active, color_col, lod="medium")

            if mesh_data is None:
                return create_empty_figure(ERROR_MESH_GENERATION)

            fig = go.Figure(
                data=[
                    go.Mesh3d(
                        x=mesh_data["vertices"][:, 0],
                        y=mesh_data["vertices"][:, 1],
                        z=mesh_data["vertices"][:, 2],
                        i=mesh_data["faces"][:, 0],
                        j=mesh_data["faces"][:, 1],
                        k=mesh_data["faces"][:, 2],
                        colorscale=DEFAULT_COLORSCALE,
                        intensity=mesh_data["vertex_colors"],
                        colorbar=dict(title=color_col),
                        showscale=True,
                    )
                ]
            )

            fig.update_layout(
                title="Simulated 3D Volume Mesh from G-code",
                template=PLOTLY_TEMPLATE,
                scene=dict(
                    xaxis_title="X Position (mm)",
                    yaxis_title="Y Position (mm)",
                    zaxis_title="Z Position (mm)",
                    aspectmode="data" if z_stretch_factor == 1.0 else "manual",
                    aspectratio=custom_aspect_ratio,
                    camera=dict(
                        eye=dict(
                            x=DEFAULT_CAMERA_POSITION["x"],
                            y=DEFAULT_CAMERA_POSITION["y"],
                            z=DEFAULT_CAMERA_POSITION["z"],
                        ),
                        center=dict(x=0, y=0, z=0),
                        up=dict(x=0, y=0, z=1),
                    ),
                ),
            )

            return fig

        return create_empty_figure("Invalid view selected.")

    @callback(
        Output("data-table", "columns"),
        Output("data-table", "data"),
        Output("data-table", "style_header"),
        Output("data-table", "style_data"),
        Output("data-table", "style_cell"),
        Input("store-main-df", "data"),
    )
    def update_data_table(jsonified_df):
        """Update data table with uploaded file content."""
        if jsonified_df is None:
            return [], [], {}, {}, {}

        df = pd.read_json(io.StringIO(jsonified_df), orient="split")

        columns = [{"name": i, "id": i} for i in df.columns]
        data = df.to_dict("records")

        style = TABLE_STYLE_DARK if PLOTLY_TEMPLATE == "plotly_dark" else TABLE_STYLE_LIGHT

        return (columns, data, style["style_header"], style["style_data"], style["style_cell"])
