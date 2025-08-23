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
    Input("init-pyvista-btn", "n_clicks"),
    State("store-main-df", "data"),
    prevent_initial_call=True
)
def initialize_pyvista_simple(n_clicks, data_json):
    """Initialize PyVista visualization in a lightweight manner."""
    if not n_clicks or not data_json:
        raise PreventUpdate
    
    try:
        # Import here to avoid initialization at module load
        import pandas as pd
        from ..components.pyvista_simple import simple_pyvista_integration
        from ..services.data_service import DataService
        
        # Parse the JSON data
        df = pd.read_json(data_json, orient='split')
        
        # Get data service
        data_service = DataService()
        
        if df is None or df.empty:
            return "No data available for visualization", False, True
        
        # Generate mesh data
        mesh_data = data_service.generate_mesh(df, level_of_detail="medium")
        
        if not mesh_data:
            return "Failed to generate mesh data", False, True
        
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
                # Also create a screenshot as proof it worked
                screenshot_file = "pyvista_preview.png"
                if simple_pyvista_integration.server:
                    simple_pyvista_integration.server.export_screenshot(screenshot_file)
                    msg = f"PyVista initialized with {len(vertices):,} vertices. Preview saved to {screenshot_file}"
                else:
                    msg = f"PyVista initialized with {len(vertices):,} vertices"
                return msg, True, False
            else:
                return "Failed to update mesh", False, True
        else:
            return "Failed to initialize PyVista server", False, True
            
    except Exception as e:
        logger.error(f"Error initializing PyVista: {e}")
        return f"Error: {str(e)}", False, True


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