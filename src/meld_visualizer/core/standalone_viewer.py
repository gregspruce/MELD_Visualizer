"""
Standalone PyVista viewer that runs in the main thread.

This completely avoids OpenGL context threading issues by using PyVista's
native windowing system instead of Trame server threads.
"""

import logging
from typing import Optional, Tuple
import numpy as np
import pyvista as pv
from pathlib import Path
import tempfile

logger = logging.getLogger(__name__)


class StandaloneViewer:
    """PyVista standalone viewer that runs in the main thread."""
    
    def __init__(self):
        """Initialize the standalone viewer."""
        self.mesh = None
        self.plotter = None
        self.screenshot_dir = Path(tempfile.gettempdir()) / "meld_screenshots"
        self.screenshot_dir.mkdir(exist_ok=True)
        
    def load_mesh(self, mesh: pv.PolyData) -> bool:
        """Load a mesh for visualization."""
        try:
            self.mesh = mesh
            logger.info(f"Mesh loaded: {mesh.n_points} points, {mesh.n_cells} cells")
            return True
        except Exception as e:
            logger.error(f"Failed to load mesh: {e}")
            return False
    
    def show_interactive(self, 
                        window_size: Tuple[int, int] = (1024, 768),
                        title: str = "MELD 3D Viewer") -> bool:
        """
        Show the mesh in an interactive PyVista window.
        
        This runs in the MAIN THREAD and provides full interactivity
        without any threading issues.
        """
        if not self.mesh:
            logger.error("No mesh loaded")
            return False
            
        try:
            # Create a fresh plotter for each show operation
            self.plotter = pv.Plotter(
                window_size=window_size,
                title=title,
                off_screen=False,
                notebook=False
            )
            
            # Add mesh with good defaults
            self.plotter.add_mesh(
                self.mesh,
                scalars=self.mesh.active_scalars_name if self.mesh.active_scalars_name else None,
                cmap="viridis",
                show_scalar_bar=True if self.mesh.active_scalars_name else False,
                smooth_shading=True,
                edge_color='black',
                line_width=0.5,
                show_edges=False,
                lighting=True
            )
            
            # Add axes
            self.plotter.add_axes()
            
            # Set nice camera position
            self.plotter.reset_camera()
            self.plotter.camera.zoom(1.2)
            
            # Enable standard interactions
            self.plotter.enable_eye_dome_lighting()  # Better depth perception
            
            # Add key bindings for common operations
            def toggle_edges():
                """Toggle edge visibility."""
                actor = self.plotter.renderer.actors[0]
                actor.GetProperty().SetEdgeVisibility(
                    not actor.GetProperty().GetEdgeVisibility()
                )
                self.plotter.render()
            
            def save_screenshot():
                """Save a screenshot."""
                filename = self.screenshot_dir / f"screenshot_{np.random.randint(10000)}.png"
                self.plotter.screenshot(str(filename))
                logger.info(f"Screenshot saved to {filename}")
            
            # Add key bindings
            self.plotter.add_key_event('e', toggle_edges)
            self.plotter.add_key_event('s', save_screenshot)
            
            # Show help text
            help_text = (
                "Controls:\n"
                "  Left Click + Drag: Rotate\n"
                "  Right Click + Drag: Zoom\n"
                "  Middle Click + Drag: Pan\n"
                "  E: Toggle edges\n"
                "  S: Save screenshot\n"
                "  Q: Quit"
            )
            self.plotter.add_text(help_text, position='upper_left', font_size=10)
            
            # Show the window (blocks until closed)
            logger.info("Opening interactive PyVista window...")
            self.plotter.show()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to show interactive viewer: {e}")
            return False
    
    def export_screenshot(self, filename: str = None) -> str:
        """
        Export a screenshot using off-screen rendering.
        
        This works reliably even without an interactive window.
        """
        if not self.mesh:
            logger.error("No mesh loaded")
            return None
            
        try:
            # Use provided filename or generate one
            if not filename:
                filename = str(self.screenshot_dir / f"export_{np.random.randint(10000)}.png")
            
            # Create off-screen plotter for screenshot
            plotter = pv.Plotter(
                off_screen=True,
                window_size=(1920, 1080)
            )
            
            # Add mesh
            plotter.add_mesh(
                self.mesh,
                scalars=self.mesh.active_scalars_name if self.mesh.active_scalars_name else None,
                cmap="viridis",
                show_scalar_bar=True if self.mesh.active_scalars_name else False,
                smooth_shading=True,
                lighting=True
            )
            
            # Set camera
            plotter.reset_camera()
            plotter.camera.zoom(1.2)
            
            # Take screenshot
            plotter.show(screenshot=filename, auto_close=True)
            
            logger.info(f"Screenshot saved to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Failed to export screenshot: {e}")
            return None
    
    def export_html(self, filename: str = None) -> str:
        """
        Export the mesh as an interactive HTML file.
        
        This creates a standalone HTML file that can be viewed in any browser
        without requiring a server.
        """
        if not self.mesh:
            logger.error("No mesh loaded")
            return None
            
        try:
            # Use provided filename or generate one
            if not filename:
                filename = str(self.screenshot_dir / f"export_{np.random.randint(10000)}.html")
            
            # Create plotter for HTML export
            plotter = pv.Plotter(
                off_screen=True,
                notebook=False
            )
            
            # Add mesh
            plotter.add_mesh(
                self.mesh,
                scalars=self.mesh.active_scalars_name if self.mesh.active_scalars_name else None,
                cmap="viridis",
                show_scalar_bar=True if self.mesh.active_scalars_name else False,
                smooth_shading=True
            )
            
            # Export to HTML
            plotter.export_html(filename)
            
            logger.info(f"Interactive HTML saved to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Failed to export HTML: {e}")
            return None
    
    def close(self):
        """Clean up resources."""
        if self.plotter:
            try:
                self.plotter.close()
            except:
                pass
            self.plotter = None