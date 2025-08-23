"""
Simplified PyVista callbacks for MELD Visualizer.

This module provides lightweight callbacks that don't initialize
heavy components at import time.
"""

import logging
from dash import callback, Output, Input, State, no_update
from dash.exceptions import PreventUpdate

logger = logging.getLogger(__name__)


@callback(
    Output("pyvista-status-message", "children"),
    Output("pyvista-initialized", "data"),
    Output("export-pyvista-stl-btn", "disabled"),
    Output("pyvista-iframe", "src"),
    Output("pyvista-iframe", "style"),
    Output("pyvista-placeholder-text", "style"),
    Input("init-pyvista-btn", "n_clicks"),
    State("store-main-df", "data"),
    prevent_initial_call=True
)
def initialize_pyvista_simple(n_clicks, data_json):
    """Initialize PyVista visualization in a lightweight manner."""
    if not n_clicks or not data_json:
        raise PreventUpdate
    
    from dash import html
    
    try:
        # Import here to avoid initialization at module load
        import pandas as pd
        from ..components.pyvista_simple import simple_pyvista_integration
        from ..services.data_service import DataService
        
        # Parse the JSON data (use StringIO to avoid future warning)
        from io import StringIO
        df = pd.read_json(StringIO(data_json), orient='split')
        
        # Get data service
        data_service = DataService()
        
        if df is None or df.empty:
            msg = html.Div([
                html.I(className="bi bi-info-circle me-2"),
                html.Span("No data available for visualization")
            ], className="text-warning")
            return msg, False, True, "", {"display": "none"}, {"display": "flex", "minHeight": "700px"}
        
        # Generate mesh data - need to provide color_column and lod parameters
        # Use a default color column from the data
        color_column = 'FeedVel' if 'FeedVel' in df.columns else df.columns[0]
        mesh_data = data_service.generate_mesh(df, color_column=color_column, lod="medium")
        
        if not mesh_data:
            msg = html.Div([
                html.I(className="bi bi-exclamation-triangle me-2"),
                html.Span("Failed to generate mesh data")
            ], className="text-danger")
            return msg, False, True, "", {"display": "none"}, {"display": "flex", "minHeight": "700px"}
        
        # Get mesh arrays
        import numpy as np
        vertices = np.array(mesh_data.get("vertices", []))
        faces = np.array(mesh_data.get("faces", []))
        scalars = np.array(mesh_data.get("vertex_colors", []))
        
        # Initialize PyVista
        if simple_pyvista_integration.initialize_server():
            # Update mesh
            success = simple_pyvista_integration.update_mesh_from_data(
                vertices, faces, scalars
            )
            
            if success:
                # Get iframe URL
                iframe_src = simple_pyvista_integration.get_iframe_src()
                
                # Create iframe style to show it
                iframe_style = {
                    "width": "100%",
                    "height": "700px", 
                    "border": "1px solid #ddd",
                    "display": "block"
                }
                
                # Get the operating mode
                mode = simple_pyvista_integration.get_mode()
                
                # Create appropriate message based on mode
                if mode == "interactive":
                    msg_text = f"PyVista initialized with {len(vertices):,} vertices in interactive mode"
                    placeholder_style = {"display": "none"}
                    msg = html.Div([
                        html.I(className="bi bi-check-circle me-2"),
                        html.Span(msg_text)
                    ], className="text-success")
                elif mode == "offscreen":
                    msg_text = f"PyVista initialized with {len(vertices):,} vertices (screenshot mode only - OpenGL not available)"
                    iframe_style["display"] = "none"
                    placeholder_style = {"display": "flex", "minHeight": "700px", "flexDirection": "column", "alignItems": "center", "justifyContent": "center"}
                    
                    # Create a screenshot to show
                    screenshot_file = "pyvista_preview.png"
                    if simple_pyvista_integration.server and simple_pyvista_integration.server.plotter:
                        simple_pyvista_integration.server.export_screenshot(screenshot_file)
                        msg_text += f". Preview saved to {screenshot_file}"
                    
                    msg = html.Div([
                        html.I(className="bi bi-info-circle me-2"),
                        html.Span(msg_text)
                    ], className="text-info")
                else:
                    msg_text = f"PyVista initialized with {len(vertices):,} vertices"
                    if not iframe_src:
                        iframe_style["display"] = "none"
                        placeholder_style = {"display": "flex", "minHeight": "700px"}
                    
                    msg = html.Div([
                        html.I(className="bi bi-check-circle me-2"),
                        html.Span(msg_text)
                    ], className="text-success")
                    
                return msg, True, False, iframe_src, iframe_style, placeholder_style
            else:
                msg = html.Div([
                    html.I(className="bi bi-exclamation-triangle me-2"),
                    html.Span("Failed to update mesh")
                ], className="text-danger")
                return msg, False, True, "", {"display": "none"}, {"display": "flex", "minHeight": "700px"}
        else:
            msg = html.Div([
                html.I(className="bi bi-exclamation-triangle me-2"),
                html.Span("Failed to initialize PyVista server")
            ], className="text-danger")
            return msg, False, True, "", {"display": "none"}, {"display": "flex", "minHeight": "700px"}
            
    except Exception as e:
        logger.error(f"Error initializing PyVista: {e}", exc_info=True)
        error_msg = html.Div([
            html.I(className="bi bi-exclamation-circle me-2"),
            html.Span(f"Error: {str(e)}")
        ], className="text-danger")
        return error_msg, False, True, "", {"display": "none"}, {"display": "flex", "minHeight": "700px"}


@callback(
    Output("pyvista-export-status", "children", allow_duplicate=True),
    Input("export-pyvista-stl-btn", "n_clicks"),
    State("pyvista-initialized", "data"),
    prevent_initial_call=True
)
def export_mesh_stl(n_clicks, initialized):
    """Export the mesh to STL format."""
    if not n_clicks or not initialized:
        raise PreventUpdate
    
    try:
        from ..components.pyvista_simple import simple_pyvista_integration
        
        filename = "meld_mesh_export.stl"
        if simple_pyvista_integration.export_mesh(filename):
            return f"Mesh exported to {filename}"
        else:
            return "Failed to export mesh"
            
    except Exception as e:
        logger.error(f"Error exporting mesh: {e}")
        return f"Export error: {str(e)}"


def register_pyvista_simple_callbacks(app):
    """Register simplified PyVista callbacks."""
    logger.info("Simplified PyVista callbacks registered")
    return True