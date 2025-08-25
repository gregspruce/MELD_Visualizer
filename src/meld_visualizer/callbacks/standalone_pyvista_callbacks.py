"""
Callbacks for standalone PyVista viewer integration.

This module handles the interaction between Dash and the standalone PyVista viewer.
"""

import logging
from dash import callback, Output, Input, State, no_update, html
from dash.exceptions import PreventUpdate

logger = logging.getLogger(__name__)


@callback(
    Output("pyvista-mesh-ready", "data"),
    Input("store-main-df", "data"),
    prevent_initial_call=True
)
def prepare_mesh_data(data_json):
    """Prepare mesh data when main data is loaded."""
    if not data_json:
        return False
    
    try:
        # Import here to avoid initialization at module load
        import pandas as pd
        import numpy as np
        from io import StringIO
        from ..components.standalone_integration import standalone_integration
        from ..services.data_service import DataService
        
        # Parse the JSON data
        df = pd.read_json(StringIO(data_json), orient='split')
        
        if df is None or df.empty:
            logger.warning("No data available for mesh generation")
            return False
        
        # Get data service
        data_service = DataService()
        
        # Generate mesh data
        color_column = 'FeedVel' if 'FeedVel' in df.columns else df.columns[0]
        mesh_data = data_service.generate_mesh(df, color_column=color_column, lod="medium")
        
        if not mesh_data:
            logger.error("Failed to generate mesh data")
            return False
        
        # Get mesh arrays
        vertices = np.array(mesh_data.get("vertices", []))
        faces = np.array(mesh_data.get("faces", []))
        scalars = np.array(mesh_data.get("vertex_colors", []))
        
        # Update the standalone integration with mesh data
        success = standalone_integration.update_mesh_from_data(vertices, faces, scalars)
        
        if success:
            logger.info(f"Mesh prepared with {len(vertices):,} vertices")
            return True
        else:
            logger.error("Failed to update mesh in standalone integration")
            return False
            
    except Exception as e:
        logger.error(f"Error preparing mesh data: {e}", exc_info=True)
        return False


@callback(
    Output("viewer-status", "children", allow_duplicate=True),
    Input("pyvista-mesh-ready", "data"),
    prevent_initial_call=True
)
def update_status_on_mesh_ready(mesh_ready):
    """Update status message when mesh is ready."""
    if mesh_ready:
        return [
            html.I(className="bi bi-check-circle me-2"),
            "Mesh data loaded and ready. Click 'Open 3D Viewer' to visualize."
        ]
    else:
        return no_update


def register_standalone_pyvista_callbacks(app):
    """Register standalone PyVista callbacks."""
    # Set up callbacks for the standalone integration
    from ..components.standalone_integration import standalone_integration
    standalone_integration.setup_callbacks(app)
    
    logger.info("Standalone PyVista callbacks registered")
    return True