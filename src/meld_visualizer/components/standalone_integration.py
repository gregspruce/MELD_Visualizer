"""
Standalone PyVista integration for Dash.

This integration uses PyVista's native windowing system to avoid all
threading and OpenGL context issues. The viewer opens in a separate window
when requested by the user.
"""

import logging
from typing import Optional, Dict, Any
import numpy as np
import threading
from pathlib import Path
from dash import html, dcc, Input, Output, State
import base64

logger = logging.getLogger(__name__)


class StandaloneIntegration:
    """Integration of standalone PyVista viewer with Dash."""
    
    def __init__(self):
        """Initialize the integration."""
        self.viewer = None
        self.mesh = None
        self.last_screenshot = None
        self.viewer_thread = None
        
    def get_component(self):
        """Get the Dash component for the standalone viewer interface."""
        return html.Div([
            html.H5("3D Visualization", className="text-center mb-3"),
            
            # Control buttons
            html.Div([
                html.Button(
                    [html.I(className="bi bi-play-fill me-2"), "Open 3D Viewer"],
                    id="open-viewer-btn",
                    className="btn btn-primary me-2",
                    disabled=False
                ),
                html.Button(
                    [html.I(className="bi bi-camera-fill me-2"), "Take Screenshot"],
                    id="take-screenshot-btn",
                    className="btn btn-secondary me-2",
                    disabled=False
                ),
                html.Button(
                    [html.I(className="bi bi-file-earmark-code me-2"), "Export HTML"],
                    id="export-html-btn",
                    className="btn btn-info me-2",
                    disabled=False
                ),
                html.Button(
                    [html.I(className="bi bi-download me-2"), "Export Mesh"],
                    id="export-mesh-btn",
                    className="btn btn-success",
                    disabled=False
                ),
            ], className="d-flex justify-content-center mb-3"),
            
            # Status message
            html.Div(
                id="viewer-status",
                className="alert alert-info text-center",
                children=[
                    html.I(className="bi bi-info-circle me-2"),
                    "Click 'Open 3D Viewer' to launch the interactive visualization in a separate window."
                ]
            ),
            
            # Screenshot preview area
            html.Div([
                html.H6("Preview", className="text-center mt-4 mb-3"),
                html.Div(
                    id="screenshot-container",
                    children=[
                        html.Div(
                            "Screenshot preview will appear here",
                            className="text-muted text-center p-5",
                            style={
                                "border": "2px dashed #dee2e6",
                                "borderRadius": "8px",
                                "minHeight": "400px",
                                "display": "flex",
                                "alignItems": "center",
                                "justifyContent": "center"
                            }
                        )
                    ]
                )
            ]),
            
            # Hidden stores for state management
            dcc.Store(id="viewer-state", data={"mesh_loaded": False}),
            dcc.Download(id="download-component")
        ])
    
    def setup_callbacks(self, app):
        """Set up Dash callbacks for the standalone viewer."""
        
        @app.callback(
            [Output("viewer-status", "children"),
             Output("viewer-state", "data")],
            Input("open-viewer-btn", "n_clicks"),
            State("viewer-state", "data"),
            prevent_initial_call=True
        )
        def open_viewer(n_clicks, state):
            """Open the standalone PyVista viewer."""
            if not self.mesh:
                return [
                    [html.I(className="bi bi-exclamation-triangle me-2"),
                     "No mesh loaded. Please load data first."],
                    state
                ]
            
            # Launch viewer in a separate thread to avoid blocking Dash
            def run_viewer():
                try:
                    from ..core.standalone_viewer import StandaloneViewer
                    viewer = StandaloneViewer()
                    viewer.load_mesh(self.mesh)
                    viewer.show_interactive()
                except Exception as e:
                    logger.error(f"Viewer error: {e}")
            
            # Start viewer thread
            self.viewer_thread = threading.Thread(target=run_viewer, daemon=True)
            self.viewer_thread.start()
            
            return [
                [html.I(className="bi bi-check-circle me-2"),
                 "3D viewer opened in separate window. Use mouse to interact: Left-drag to rotate, Right-drag to zoom, Middle-drag to pan."],
                {"mesh_loaded": True}
            ]
        
        @app.callback(
            [Output("screenshot-container", "children"),
             Output("viewer-status", "children", allow_duplicate=True)],
            Input("take-screenshot-btn", "n_clicks"),
            prevent_initial_call=True
        )
        def take_screenshot(n_clicks):
            """Take a screenshot of the current mesh."""
            if not self.mesh:
                return [
                    html.Div(
                        "No mesh loaded",
                        className="text-muted text-center p-5",
                        style={
                            "border": "2px dashed #dee2e6",
                            "borderRadius": "8px",
                            "minHeight": "400px",
                            "display": "flex",
                            "alignItems": "center",
                            "justifyContent": "center"
                        }
                    ),
                    [html.I(className="bi bi-exclamation-triangle me-2"),
                     "No mesh loaded. Please load data first."]
                ]
            
            try:
                from ..core.standalone_viewer import StandaloneViewer
                viewer = StandaloneViewer()
                viewer.load_mesh(self.mesh)
                screenshot_path = viewer.export_screenshot()
                
                if screenshot_path and Path(screenshot_path).exists():
                    # Read and encode the screenshot
                    with open(screenshot_path, 'rb') as f:
                        encoded = base64.b64encode(f.read()).decode()
                    
                    self.last_screenshot = screenshot_path
                    
                    return [
                        html.Img(
                            src=f"data:image/png;base64,{encoded}",
                            style={
                                "width": "100%",
                                "maxHeight": "600px",
                                "objectFit": "contain",
                                "borderRadius": "8px",
                                "boxShadow": "0 4px 6px rgba(0,0,0,0.1)"
                            }
                        ),
                        [html.I(className="bi bi-check-circle me-2"),
                         f"Screenshot saved to {screenshot_path}"]
                    ]
                else:
                    raise Exception("Screenshot generation failed")
                    
            except Exception as e:
                logger.error(f"Screenshot error: {e}")
                return [
                    html.Div(
                        "Error taking screenshot",
                        className="text-danger text-center p-5",
                        style={
                            "border": "2px dashed #dc3545",
                            "borderRadius": "8px",
                            "minHeight": "400px",
                            "display": "flex",
                            "alignItems": "center",
                            "justifyContent": "center"
                        }
                    ),
                    [html.I(className="bi bi-x-circle me-2"),
                     f"Failed to take screenshot: {str(e)}"]
                ]
        
        @app.callback(
            [Output("download-component", "data"),
             Output("viewer-status", "children", allow_duplicate=True)],
            Input("export-html-btn", "n_clicks"),
            prevent_initial_call=True
        )
        def export_html(n_clicks):
            """Export the mesh as interactive HTML."""
            if not self.mesh:
                return [
                    None,
                    [html.I(className="bi bi-exclamation-triangle me-2"),
                     "No mesh loaded. Please load data first."]
                ]
            
            try:
                from ..core.standalone_viewer import StandaloneViewer
                viewer = StandaloneViewer()
                viewer.load_mesh(self.mesh)
                html_path = viewer.export_html()
                
                if html_path and Path(html_path).exists():
                    return [
                        dcc.send_file(html_path),
                        [html.I(className="bi bi-check-circle me-2"),
                         f"Interactive HTML exported successfully"]
                    ]
                else:
                    raise Exception("HTML export failed")
                    
            except Exception as e:
                logger.error(f"HTML export error: {e}")
                return [
                    None,
                    [html.I(className="bi bi-x-circle me-2"),
                     f"Failed to export HTML: {str(e)}"]
                ]
        
        @app.callback(
            [Output("download-component", "data", allow_duplicate=True),
             Output("viewer-status", "children", allow_duplicate=True)],
            Input("export-mesh-btn", "n_clicks"),
            prevent_initial_call=True
        )
        def export_mesh(n_clicks):
            """Export the mesh as STL file."""
            if not self.mesh:
                return [
                    None,
                    [html.I(className="bi bi-exclamation-triangle me-2"),
                     "No mesh loaded. Please load data first."]
                ]
            
            try:
                import tempfile
                from pathlib import Path
                
                # Create temporary file for export
                temp_dir = Path(tempfile.gettempdir())
                mesh_path = temp_dir / "exported_mesh.stl"
                
                # Save mesh
                self.mesh.save(str(mesh_path))
                
                if mesh_path.exists():
                    return [
                        dcc.send_file(str(mesh_path)),
                        [html.I(className="bi bi-check-circle me-2"),
                         "Mesh exported successfully as STL"]
                    ]
                else:
                    raise Exception("Mesh export failed")
                    
            except Exception as e:
                logger.error(f"Mesh export error: {e}")
                return [
                    None,
                    [html.I(className="bi bi-x-circle me-2"),
                     f"Failed to export mesh: {str(e)}"]
                ]
    
    def update_mesh_from_data(self,
                             vertices: np.ndarray,
                             faces: np.ndarray,
                             scalars: Optional[np.ndarray] = None) -> bool:
        """Update the mesh with new data."""
        try:
            import pyvista as pv
            
            # Create PyVista mesh
            if faces is not None and len(faces) > 0:
                # Convert faces to PyVista format
                pv_faces = []
                for face in faces:
                    pv_faces.extend([3] + list(face))
                self.mesh = pv.PolyData(vertices, np.array(pv_faces))
            else:
                # Point cloud
                self.mesh = pv.PolyData(vertices)
            
            # Add scalars if provided
            if scalars is not None:
                self.mesh["values"] = scalars
            
            logger.info(f"Mesh updated: {self.mesh.n_points} points, {self.mesh.n_cells} cells")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update mesh: {e}")
            return False
    
    def load_mesh_file(self, filepath: str) -> bool:
        """Load a mesh from a file."""
        try:
            import pyvista as pv
            self.mesh = pv.read(filepath)
            logger.info(f"Mesh loaded from {filepath}: {self.mesh.n_points} points, {self.mesh.n_cells} cells")
            return True
        except Exception as e:
            logger.error(f"Failed to load mesh file: {e}")
            return False


# Global instance
standalone_integration = StandaloneIntegration()