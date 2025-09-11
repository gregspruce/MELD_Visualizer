"""
Data loading and processing callbacks.
Handles file uploads, data parsing, and initial data storage.
"""

import logging

import numpy as np
from dash import Input, Output, State, callback, html, no_update
from dash.exceptions import PreventUpdate

from ..constants import ERROR_NO_FILE, SUCCESS_UNITS_CONVERTED
from ..services import get_data_service

logger = logging.getLogger(__name__)


def register_data_callbacks(app=None):
    """Register data-related callbacks."""

    @callback(
        Output("store-main-df", "data"),
        Output("output-filename", "children"),
        Output("store-layout-config", "data"),
        Output("store-config-warnings", "data"),
        Output("store-column-ranges", "data"),
        Input("upload-data", "contents"),
        State("upload-data", "filename"),
    )
    def update_data_and_configs(contents, filename):
        """
        Primary callback triggered on file upload.
        Parses the uploaded file and stores configuration data.
        """
        if contents is None:
            return no_update, ERROR_NO_FILE, no_update, no_update, no_update

        # Use data service for processing
        data_service = get_data_service()
        df, error_message, converted = data_service.parse_file(contents, filename)

        if error_message and df is None:
            return no_update, error_message, no_update, no_update, no_update

        # Prepare success message
        filename_message = f"Current file: {filename}"
        if converted:
            filename_message += f" ({SUCCESS_UNITS_CONVERTED})"

        # Get column information
        numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
        column_ranges = data_service.get_column_statistics(df)

        # Simplify column ranges for UI
        simple_ranges = {col: [stats["min"], stats["max"]] for col, stats in column_ranges.items()}

        layout_config = {"axis_options": numeric_cols}

        # Check for missing config columns
        from ..config import APP_CONFIG

        df_columns_set = set(df.columns)
        warnings = []

        for key, options in APP_CONFIG.items():
            if "options" in key and isinstance(options, list):
                missing_cols = [col for col in options if col not in df_columns_set]
                if missing_cols:
                    warnings.append(
                        f"Warning: Columns from 'config.json' not found in '{filename}': "
                        f"{', '.join(missing_cols)}."
                    )

        # Return serialized DataFrame
        df_json = df.to_json(date_format="iso", orient="split")

        logger.info(
            f"Loaded file: {filename} ({len(df)} rows, {len(numeric_cols)} numeric columns)"
        )

        return df_json, filename_message, layout_config, warnings, simple_ranges

    @callback(
        Output("config-warning-alert", "children"),
        Output("config-warning-alert", "is_open"),
        Input("store-config-warnings", "data"),
    )
    def display_config_warnings(warnings):
        """Display warnings if config columns are missing from the uploaded file."""
        if warnings:
            return html.Ul([html.Li(w) for w in warnings]), True
        return "", False

    @callback(
        Output("store-gcode-df", "data"),
        Output("gcode-filename-alert", "children"),
        Output("gcode-filename-alert", "is_open"),
        Input("upload-gcode", "contents"),
        State("upload-gcode", "filename"),
        prevent_initial_call=True,
    )
    def handle_gcode_upload(contents, filename):
        """
        Handle G-code file upload and parsing.
        """
        if contents is None:
            raise PreventUpdate

        # Use data service for G-code parsing
        data_service = get_data_service()

        # Import the G-code parser
        from ..core.data_processing import parse_gcode_file

        df, message, _ = parse_gcode_file(contents, filename)

        if df is None:
            return no_update, message, True  # Show error message

        # Cache the G-code DataFrame
        data_service.cache.cache_dataframe(df, f"gcode_{filename}")

        logger.info(f"Loaded G-code file: {filename} ({len(df)} points)")

        return df.to_json(date_format="iso", orient="split"), message, True
