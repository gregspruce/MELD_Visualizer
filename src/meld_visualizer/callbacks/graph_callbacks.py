"""
Graph generation callbacks.
Handles all 3D and 2D plot generation and updates.
"""

# Standard library imports
import io
import logging

# Third-party imports
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, callback

# Local imports
from ..config import PLOTLY_TEMPLATE
from ..constants import (
    DEFAULT_ASPECT_MODE,
    DEFAULT_CAMERA_POSITION,
    DEFAULT_FONT_SIZE,
    DEFAULT_GRAPH_MARGIN,
    ERROR_COLUMN_NOT_FOUND,
    ERROR_NO_DATA,
)
from ..services import get_data_service

logger = logging.getLogger(__name__)


def create_empty_figure(message="Upload a file and configure options."):
    """Create a blank Plotly figure with a text message."""
    fig = go.Figure()
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        xaxis={"visible": False},
        yaxis={"visible": False},
        annotations=[
            {
                "text": message,
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {"size": DEFAULT_FONT_SIZE},
            }
        ],
    )
    return fig


def register_graph_callbacks(app=None):
    """Register graph-related callbacks."""

    data_service = get_data_service()

    @callback(
        Output("graph-1", "figure"),
        [
            Input("store-main-df", "data"),
            Input("radio-buttons-1", "value"),
            Input({"type": "range-slider", "index": "zpos-1"}, "value"),
            Input("store-config-updated", "data"),
        ],
        prevent_initial_call=True,
    )
    def update_graph_1(jsonified_df, col_chosen, slider_range, config_updated):
        """Update the first main 3D scatter plot."""
        try:
            if not jsonified_df or not col_chosen:
                return create_empty_figure()

            if not slider_range:
                slider_range = [0, 1]  # Default range

            df = pd.read_json(io.StringIO(jsonified_df), orient="split")

            if col_chosen not in df.columns:
                return create_empty_figure(ERROR_COLUMN_NOT_FOUND.format(col_chosen))

            # Apply range filter
            low, high = slider_range
            dff = data_service.filter_by_range(df, "ZPos", low, high)

            if dff.empty:
                return create_empty_figure(ERROR_NO_DATA)

            fig = px.scatter_3d(
                dff, x="XPos", y="YPos", z="ZPos", color=col_chosen, template=PLOTLY_TEMPLATE
            )

            fig.update_layout(
                margin=DEFAULT_GRAPH_MARGIN,
                scene_aspectmode=DEFAULT_ASPECT_MODE,
                scene_camera=dict(
                    eye=dict(
                        x=DEFAULT_CAMERA_POSITION["x"],
                        y=DEFAULT_CAMERA_POSITION["y"],
                        z=DEFAULT_CAMERA_POSITION["z"],
                    ),
                    center=dict(x=0, y=0, z=0),
                    up=dict(x=0, y=0, z=1),
                ),
            )

            return fig
        except Exception as e:
            logger.error(f"Error in update_graph_1: {e}")
            return create_empty_figure()

    @callback(
        Output("graph-2", "figure"),
        [
            Input("store-main-df", "data"),
            Input("radio-buttons-2", "value"),
            Input({"type": "range-slider", "index": "zpos-2"}, "value"),
            Input("store-config-updated", "data"),
        ],
        prevent_initial_call=True,
    )
    def update_graph_2(jsonified_df, col_chosen, slider_range, config_updated):
        """Update the second main 3D scatter plot."""
        try:
            if not jsonified_df or not col_chosen:
                return create_empty_figure()

            if not slider_range:
                slider_range = [0, 1]  # Default range

            df = pd.read_json(io.StringIO(jsonified_df), orient="split")

            if col_chosen not in df.columns:
                return create_empty_figure(ERROR_COLUMN_NOT_FOUND.format(col_chosen))

            # Apply range filter
            low, high = slider_range
            dff = data_service.filter_by_range(df, "ZPos", low, high)

            if dff.empty:
                return create_empty_figure(ERROR_NO_DATA)

            fig = px.scatter_3d(
                dff, x="XPos", y="YPos", z="ZPos", color=col_chosen, template=PLOTLY_TEMPLATE
            )

            fig.update_layout(
                margin=DEFAULT_GRAPH_MARGIN,
                scene_aspectmode=DEFAULT_ASPECT_MODE,
                scene_camera=dict(
                    eye=dict(
                        x=DEFAULT_CAMERA_POSITION["x"],
                        y=DEFAULT_CAMERA_POSITION["y"],
                        z=DEFAULT_CAMERA_POSITION["z"],
                    ),
                    center=dict(x=0, y=0, z=0),
                    up=dict(x=0, y=0, z=1),
                ),
            )

            return fig
        except Exception as e:
            logger.error(f"Error in update_graph_2: {e}")
            return create_empty_figure()

    @callback(
        Output("graph-2d", "figure"),
        [
            Input("store-main-df", "data"),
            Input({"type": "range-slider", "index": "time-2d"}, "value"),
            Input("radio-2d-y", "value"),
            Input("radio-2d-color", "value"),
        ],
        prevent_initial_call=True,
    )
    def update_2d_scatter(jsonified_df, time_range, y_col, color_col):
        """Update the 2D time-series scatter plot."""
        try:
            if not jsonified_df or not y_col or not color_col:
                return create_empty_figure()

            if not time_range:
                time_range = [0, 1]  # Default range

            df = pd.read_json(io.StringIO(jsonified_df), orient="split")
            df["Time"] = pd.to_datetime(df["Time"])

            if not {y_col, color_col}.issubset(df.columns):
                return create_empty_figure("Error: Selected columns not in file.")

            # Apply time filter
            low, high = time_range
            dff = data_service.filter_by_range(df, "TimeInSeconds", low, high)

            if dff.empty:
                return create_empty_figure(ERROR_NO_DATA)

            fig = px.scatter(dff, x="Time", y=y_col, color=color_col, template=PLOTLY_TEMPLATE)

            # Responsive handled by config, not layout
            return fig
        except Exception as e:
            logger.error(f"Error in update_2d_scatter: {e}")
            return create_empty_figure()

    @callback(
        Output("custom-graph", "figure"),
        [
            Input("store-main-df", "data"),
            Input("custom-dropdown-x", "value"),
            Input("custom-dropdown-y", "value"),
            Input("custom-dropdown-z", "value"),
            Input("custom-dropdown-color", "value"),
            Input("custom-dropdown-filter", "value"),
            Input({"type": "range-slider", "index": "custom"}, "value"),
        ],
        prevent_initial_call=True,
    )
    def update_custom_graph(jsonified_df, x_col, y_col, z_col, color_col, filter_col, filter_range):
        """Update the fully customizable 3D scatter plot."""
        try:
            if not jsonified_df or not all([x_col, y_col, z_col, color_col, filter_col]):
                return create_empty_figure("Select all dropdown values to render graph.")

            if not filter_range:
                filter_range = [0, 1]  # Default range

            df = pd.read_json(io.StringIO(jsonified_df), orient="split")

            all_cols = {x_col, y_col, z_col, color_col, filter_col}
            if not all_cols.issubset(df.columns):
                return create_empty_figure("Error: One or more selected columns not in file.")

            # Apply custom filter
            low, high = filter_range
            dff = data_service.filter_by_range(df, filter_col, low, high)

            if dff.empty:
                return create_empty_figure(ERROR_NO_DATA)

            fig = px.scatter_3d(
                dff, x=x_col, y=y_col, z=z_col, color=color_col, template=PLOTLY_TEMPLATE
            )

            fig.update_layout(
                margin=DEFAULT_GRAPH_MARGIN,
                scene_aspectmode=DEFAULT_ASPECT_MODE,
                scene_camera=dict(
                    eye=dict(
                        x=DEFAULT_CAMERA_POSITION["x"],
                        y=DEFAULT_CAMERA_POSITION["y"],
                        z=DEFAULT_CAMERA_POSITION["z"],
                    ),
                    center=dict(x=0, y=0, z=0),
                    up=dict(x=0, y=0, z=1),
                ),
            )

            return fig
        except Exception as e:
            logger.error(f"Error in update_custom_graph: {e}")
            return create_empty_figure()
