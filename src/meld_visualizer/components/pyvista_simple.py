"""
Simplified PyVista integration for MELD Visualizer.

This module provides a lightweight PyVista integration that doesn't
initialize components at import time.
"""

import logging
from typing import Optional, Dict, Any
import numpy as np
import pandas as pd
from dash import html, dcc

logger = logging.getLogger(__name__)


class SimplePyVistaIntegration:
    """Simplified PyVista integration that initializes lazily."""
    
    def __init__(self):
        """Initialize without creating any Trame servers."""
        self.server = None
        self.mesh = None
        self.initialized = False
        
    def get_placeholder_component(self):
        """Get a placeholder component for the PyVista visualization."""
        return html.Div([
            html.H5("PyVista 3D Visualization", className="text-center mb-3"),
            html.Div(
                id="pyvista-viz-container",
                children=[
                    html.Div(
                        id="pyvista-placeholder-text",
                        children=[
                            html.I(className="bi bi-cube me-2"),
                            html.Span("Click 'Initialize PyVista Renderer' to start the high-performance 3D viewer.")
                        ],
                        className="text-muted text-center d-flex align-items-center justify-content-center h-100",
                        style={"minHeight": "700px"}
                    ),
                    html.Iframe(
                        id="pyvista-iframe",
                        src="",  # Empty initially
                        style={
                            "width": "100%",
                            "height": "700px",
                            "border": "1px solid #ddd",
                            "display": "none"  # Hidden initially
                        }
                    )
                ],
                style={"minHeight": "700px", "backgroundColor": "#f8f9fa", "position": "relative"}
            )
        ])
    
    def initialize_server(self, port: int = 8051) -> bool:
        """Initialize the Trame server lazily when needed."""
        if self.initialized:
            return True
            
        try:
            # Only import when actually needed
            from ..core.trame_server_simple import SimplifiedTrameServer
            
            # Create simplified server
            self.server = SimplifiedTrameServer(port)
            self.port = port
            
            # Initialize the server
            if self.server.initialize():
                self.initialized = True
                logger.info(f"PyVista server initialized on port {port}")
                return True
            else:
                logger.error("Failed to initialize PyVista server")
                return False
            
        except Exception as e:
            logger.error(f"Failed to initialize PyVista server: {e}")
            return False
    
    def update_mesh_from_data(self, 
                             vertices: np.ndarray,
                             faces: np.ndarray,
                             scalars: Optional[np.ndarray] = None) -> bool:
        """Update the mesh with new data."""
        if not self.initialized:
            if not self.initialize_server():
                return False
        
        try:
            import pyvista as pv
            
            # Create PyVista mesh
            if faces is not None and len(faces) > 0:
                # PyVista expects faces in format [n_vertices, v1, v2, v3, ...]
                # Convert from simple triangle array to PyVista format
                pv_faces = []
                for face in faces:
                    pv_faces.extend([3] + list(face))  # 3 vertices per triangle
                self.mesh = pv.PolyData(vertices, np.array(pv_faces))
            else:
                # Point cloud
                self.mesh = pv.PolyData(vertices)
            
            # Add scalars if provided
            if scalars is not None:
                self.mesh["values"] = scalars
            
            # Update server if available
            if self.server:
                self.server.load_mesh(self.mesh)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update mesh: {e}")
            return False
    
    def get_iframe_src(self) -> str:
        """Get the iframe source URL."""
        if self.initialized and self.server:
            src = self.server.get_iframe_src()
            return src if src else ""
        return ""
    
    def get_mode(self) -> str:
        """Get the current operating mode."""
        if self.server:
            return self.server.get_mode()
        return "unknown"
    
    def export_mesh(self, filename: str) -> bool:
        """Export the current mesh to a file."""
        if not self.mesh:
            return False
            
        try:
            self.mesh.save(filename)
            return True
        except Exception as e:
            logger.error(f"Failed to export mesh: {e}")
            return False


# Global instance that doesn't initialize at import
simple_pyvista_integration = SimplePyVistaIntegration()