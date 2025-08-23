"""
Simplified Trame server for PyVista visualization.

This is a minimal working implementation that avoids initialization issues.
"""

import logging
from typing import Optional, Any
import numpy as np
import pyvista as pv
import os

logger = logging.getLogger(__name__)


class SimplifiedTrameServer:
    """Minimal Trame server with robust fallback."""
    
    def __init__(self, port: int = 8051):
        """Initialize without creating UI."""
        self.port = port
        self.plotter = None
        self.mesh = None
        self.initialized = False
        self.server = None
        self.mode = "unknown"  # "interactive", "offscreen", or "failed"
        
    def initialize(self) -> bool:
        """Initialize PyVista plotter with appropriate fallback."""
        # Try interactive mode first
        if self._try_interactive_mode():
            self.mode = "interactive"
            logger.info(f"PyVista initialized in interactive mode on port {self.port}")
            return True
        
        # Fall back to off-screen mode
        if self._try_offscreen_mode():
            self.mode = "offscreen"
            logger.info("PyVista initialized in off-screen mode (screenshots only)")
            return True
        
        # Complete failure
        self.mode = "failed"
        logger.error("Failed to initialize PyVista in any mode")
        return False
    
    def _try_interactive_mode(self) -> bool:
        """Try to initialize interactive Trame server."""
        try:
            # Set environment for better compatibility
            os.environ['PYVISTA_OFF_SCREEN'] = 'false'
            
            # Import Trame components
            from trame.app import get_server
            from trame.widgets import vtk
            from trame.ui.vuetify import SinglePageLayout
            
            # Try to create plotter with specific backend
            try:
                # Try with Qt backend first (if available)
                self.plotter = pv.Plotter(off_screen=False, notebook=False)
            except:
                # Fall back to default backend
                self.plotter = pv.Plotter(off_screen=True, window_size=[800, 600])
                
            # Create Trame server
            self.server = get_server(f"pyvista_server_{self.port}")
            self.server.client_type = "vue2"
            self.ctrl = self.server.controller
            self.state = self.server.state
            
            # Build simple UI
            with SinglePageLayout(self.server) as layout:
                layout.title.set_text("PyVista 3D Viewer")
                
                with layout.content:
                    with vtk.VtkView() as view:
                        self.ctrl.view_update = view.update
                        self.ctrl.view_reset_camera = view.reset_camera
                        
                        # Connect render window
                        view.set_render_window(self.plotter.ren_win)
            
            # Start server in background thread
            import threading
            import asyncio
            
            def start_server():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    self.server.start(
                        port=self.port, 
                        show=False, 
                        open_browser=False,
                        exec_mode='task'  # Use task mode for better compatibility
                    )
                except Exception as e:
                    logger.error(f"Server start error: {e}")
            
            server_thread = threading.Thread(target=start_server, daemon=True)
            server_thread.start()
            
            # Give it a moment to start
            import time
            time.sleep(2)
            
            # Test if server is actually running
            import requests
            try:
                response = requests.get(f"http://localhost:{self.port}/", timeout=2)
                if response.status_code == 200:
                    self.initialized = True
                    return True
            except:
                pass
                
            # Server didn't start properly
            if self.plotter:
                self.plotter.close()
            if self.server:
                try:
                    self.server.stop()
                except:
                    pass
            return False
            
        except Exception as e:
            logger.debug(f"Interactive mode failed: {e}")
            return False
    
    def _try_offscreen_mode(self) -> bool:
        """Try to initialize in off-screen mode for screenshots."""
        try:
            # Clean up any previous attempts
            if self.plotter:
                try:
                    self.plotter.close()
                except:
                    pass
                self.plotter = None
                
            # Set environment for off-screen
            os.environ['PYVISTA_OFF_SCREEN'] = 'true'
            
            # Create off-screen plotter
            self.plotter = pv.Plotter(
                off_screen=True,
                window_size=[800, 600],
                notebook=False
            )
            
            self.initialized = True
            self.server = None  # No server in off-screen mode
            return True
            
        except Exception as e:
            logger.error(f"Off-screen mode failed: {e}")
            return False
    
    def get_mode(self) -> str:
        """Get the current operating mode."""
        return self.mode
    
    def load_mesh(self, mesh: pv.PolyData) -> bool:
        """Load a mesh for visualization."""
        if not self.initialized:
            if not self.initialize():
                return False
        
        try:
            self.mesh = mesh
            self.plotter.clear()
            
            # Add mesh with good defaults
            self.plotter.add_mesh(
                mesh,
                scalars=mesh.active_scalars_name if mesh.active_scalars_name else None,
                cmap="viridis",
                show_scalar_bar=True if mesh.active_scalars_name else False,
                smooth_shading=True,
                edge_color='black',
                line_width=0.5,
                show_edges=False
            )
            
            # Set up camera
            self.plotter.reset_camera()
            self.plotter.camera.zoom(1.2)
            
            # Update view if server is running (interactive mode)
            if self.server and hasattr(self, 'ctrl'):
                try:
                    self.ctrl.view_update()
                except:
                    pass  # Ignore update errors
                    
            return True
        except Exception as e:
            logger.error(f"Failed to load mesh: {e}")
            return False
    
    def export_screenshot(self, filename: str = "screenshot.png") -> bool:
        """Export a screenshot."""
        if not self.plotter or not self.mesh:
            return False
        
        try:
            # Ensure plotter is ready
            if self.mode == "offscreen":
                self.plotter.show(auto_close=False, screenshot=filename)
            else:
                self.plotter.screenshot(filename)
            return True
        except Exception as e:
            logger.error(f"Failed to export screenshot: {e}")
            return False
    
    def get_iframe_src(self) -> Optional[str]:
        """Get iframe source if in interactive mode."""
        if self.mode == "interactive" and self.initialized:
            return f"http://localhost:{self.port}/"
        return None
    
    def close(self):
        """Close the plotter and server."""
        if self.plotter:
            try:
                self.plotter.close()
            except:
                pass
            self.plotter = None
            
        if self.server:
            try:
                self.server.stop()
            except:
                pass
            self.server = None
            
        self.initialized = False
        self.mode = "unknown"