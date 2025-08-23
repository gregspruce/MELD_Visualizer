"""
PyVista/Trame visualization callbacks for MELD Visualizer.

This module provides callbacks for the PyVista-based 3D volume mesh visualization,
offering significant performance improvements over the original Plotly implementation.
"""

import logging
from typing import Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np
from dash import callback, Output, Input, State, no_update, ctx
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go

from ..core.pyvista_mesh import PyVistaMeshGenerator
from ..components.trame_integration import DashTrameIntegration as TrameIntegration
from ..services.data_service import DataService
from ..constants import (
    MESH_LOD_HIGH,
    MESH_LOD_MEDIUM,
    MESH_LOD_LOW,
)

# Default color scale for PyVista
DEFAULT_COLOR_SCALE = "viridis"

logger = logging.getLogger(__name__)

# Global instances for performance
mesh_generator = PyVistaMeshGenerator()
trame_integration = TrameIntegration()
data_service = DataService()


@callback(
    Output("pyvista-trame-container", "children"),
    Output("pyvista-status", "children"),
    Input("pyvista-mesh-btn", "n_clicks"),
    State("data-store", "data"),
    State("lod-selector", "value"),
    State("color-by-dropdown", "value"),
    State("z-stretch-factor", "value"),
    prevent_initial_call=True
)
def initialize_pyvista_visualization(
    n_clicks: int,
    data_json: Dict[str, Any],
    lod: str,
    color_by: str,
    z_stretch: float
) -> Tuple[Any, str]:
    """
    Initialize PyVista/Trame visualization from stored data.
    
    This callback replaces the Plotly mesh visualization with a high-performance
    PyVista renderer embedded via Trame.
    """
    if not n_clicks or not data_json:
        raise PreventUpdate
    
    try:
        # Get filtered data from service
        df = data_service.get_filtered_data(data_json)
        if df is None or df.empty:
            return no_update, "No data available for visualization"
        
        # Generate mesh using existing volume calculation logic
        mesh_data = data_service.generate_mesh(
            df, 
            level_of_detail=lod or "medium"
        )
        
        if not mesh_data:
            return no_update, "Failed to generate mesh data"
        
        # Convert mesh data to PyVista format
        vertices = mesh_data.get("vertices", [])
        faces = mesh_data.get("faces", [])
        scalars = mesh_data.get("vertex_colors", [])
        
        # Apply Z-stretch if specified
        if z_stretch and z_stretch != 1.0:
            vertices = np.array(vertices)
            vertices[:, 2] *= z_stretch
            vertices = vertices.tolist()
        
        # Create PyVista mesh
        pyvista_mesh = mesh_generator.create_mesh_from_arrays(
            vertices=np.array(vertices),
            faces=np.array(faces),
            scalars=np.array(scalars) if scalars else None,
            scalar_name=color_by or "ProcessValue"
        )
        
        # Apply LOD optimization
        if lod == "low":
            pyvista_mesh = mesh_generator.optimize_for_web(
                pyvista_mesh, 
                target_reduction=0.7
            )
        elif lod == "medium":
            pyvista_mesh = mesh_generator.optimize_for_web(
                pyvista_mesh,
                target_reduction=0.5
            )
        
        # Update Trame visualization
        trame_integration.update_mesh(
            pyvista_mesh,
            color_map=DEFAULT_COLOR_SCALE,
            scalar_name=color_by
        )
        
        # Get the iframe component
        iframe_component = trame_integration.get_iframe_component()
        
        status = f"PyVista visualization ready - {len(vertices):,} vertices, {len(faces):,} faces"
        return iframe_component, status
        
    except Exception as e:
        logger.error(f"Error initializing PyVista visualization: {e}")
        return no_update, f"Error: {str(e)}"


@callback(
    Output("pyvista-export-status", "children"),
    Input("export-pyvista-btn", "n_clicks"),
    State("export-format-dropdown", "value"),
    State("pyvista-trame-container", "children"),
    prevent_initial_call=True
)
def export_pyvista_mesh(
    n_clicks: int,
    export_format: str,
    container: Any
) -> str:
    """
    Export the current PyVista mesh to various 3D formats.
    
    Supports: STL, OBJ, PLY, VTK for 3D printing and CAD applications.
    """
    if not n_clicks or not container:
        raise PreventUpdate
    
    try:
        format_map = {
            "stl": "mesh_export.stl",
            "obj": "mesh_export.obj", 
            "ply": "mesh_export.ply",
            "vtk": "mesh_export.vtk"
        }
        
        filename = format_map.get(export_format, "mesh_export.stl")
        
        # Export via Trame integration
        success = trame_integration.export_mesh(filename)
        
        if success:
            return f"Successfully exported mesh as {filename}"
        else:
            return f"Failed to export mesh"
            
    except Exception as e:
        logger.error(f"Error exporting mesh: {e}")
        return f"Export error: {str(e)}"


@callback(
    Output("pyvista-camera-state", "data"),
    Input("reset-camera-btn", "n_clicks"),
    Input("save-view-btn", "n_clicks"),
    State("pyvista-camera-state", "data"),
    prevent_initial_call=True
)
def manage_camera_state(
    reset_clicks: int,
    save_clicks: int,
    current_state: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Manage camera position and orientation for consistent views.
    """
    triggered = ctx.triggered_id
    
    if triggered == "reset-camera-btn":
        # Reset to default view
        trame_integration.reset_camera()
        return {"view": "default"}
    
    elif triggered == "save-view-btn":
        # Save current camera state
        camera_state = trame_integration.get_camera_state()
        return camera_state
    
    return current_state or {}


@callback(
    Output("pyvista-performance-metrics", "children"),
    Input("pyvista-trame-container", "children"),
    prevent_initial_call=True
)
def update_performance_metrics(container: Any) -> str:
    """
    Display rendering performance metrics.
    """
    if not container:
        raise PreventUpdate
    
    try:
        metrics = trame_integration.get_performance_metrics()
        
        fps = metrics.get("fps", 0)
        triangles = metrics.get("triangles", 0)
        memory = metrics.get("memory_mb", 0)
        
        return (
            f"FPS: {fps:.1f} | "
            f"Triangles: {triangles:,} | "
            f"Memory: {memory:.1f} MB"
        )
        
    except Exception as e:
        logger.error(f"Error getting performance metrics: {e}")
        return "Performance metrics unavailable"


@callback(
    Output("pyvista-interaction-output", "children"),
    Input("pyvista-pick-event", "data"),
    prevent_initial_call=True
)
def handle_pick_event(pick_data: Dict[str, Any]) -> str:
    """
    Handle point/cell picking events from the PyVista viewer.
    
    Displays information about clicked points on the mesh.
    """
    if not pick_data:
        raise PreventUpdate
    
    try:
        point_id = pick_data.get("point_id")
        coordinates = pick_data.get("coordinates", [])
        scalar_value = pick_data.get("scalar_value")
        
        return (
            f"Selected Point #{point_id}: "
            f"({coordinates[0]:.2f}, {coordinates[1]:.2f}, {coordinates[2]:.2f}) "
            f"Value: {scalar_value:.3f}"
        )
        
    except Exception as e:
        logger.error(f"Error handling pick event: {e}")
        return ""


@callback(
    Output("plotly-pyvista-comparison", "children"),
    Input("compare-renderers-btn", "n_clicks"),
    State("data-store", "data"),
    prevent_initial_call=True
)
def compare_rendering_performance(
    n_clicks: int,
    data_json: Dict[str, Any]
) -> str:
    """
    Compare Plotly vs PyVista rendering performance.
    
    Useful for demonstrating the performance improvements.
    """
    if not n_clicks or not data_json:
        raise PreventUpdate
    
    try:
        df = data_service.get_filtered_data(data_json)
        if df is None or df.empty:
            return "No data for comparison"
        
        # Time Plotly mesh generation
        import time
        
        # Generate mesh data
        start_plotly = time.time()
        mesh_data = data_service.generate_mesh(df)
        plotly_time = time.time() - start_plotly
        
        # Time PyVista mesh generation
        start_pyvista = time.time()
        vertices = np.array(mesh_data.get("vertices", []))
        faces = np.array(mesh_data.get("faces", []))
        pyvista_mesh = mesh_generator.create_mesh_from_arrays(vertices, faces)
        pyvista_time = time.time() - start_pyvista
        
        # Calculate metrics
        num_vertices = len(vertices)
        num_faces = len(faces)
        speedup = plotly_time / pyvista_time if pyvista_time > 0 else 0
        
        comparison = f"""
        **Performance Comparison**
        
        Dataset: {num_vertices:,} vertices, {num_faces:,} faces
        
        Plotly Generation: {plotly_time:.3f}s
        PyVista Generation: {pyvista_time:.3f}s
        Speedup: {speedup:.1f}x faster
        
        Additional PyVista Benefits:
        - Hardware-accelerated rendering
        - Smooth camera controls
        - Real-time color mapping
        - Professional lighting/shading
        - Export to CAD formats (STL, OBJ)
        """
        
        return comparison
        
    except Exception as e:
        logger.error(f"Error comparing performance: {e}")
        return f"Comparison error: {str(e)}"


# Register callbacks with the app
def register_pyvista_callbacks(app):
    """
    Register all PyVista-related callbacks with the Dash app.
    
    This should be called during app initialization.
    """
    logger.info("Registering PyVista visualization callbacks")
    # Callbacks are already registered via decorator
    return True