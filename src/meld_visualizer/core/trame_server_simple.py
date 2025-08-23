"""
Simplified Trame server for PyVista visualization.

This is a minimal working implementation that avoids initialization issues.
"""

import logging
from typing import Optional, Any
import numpy as np
import pyvista as pv
import os
import threading

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
        self.server_thread = None
        self.pending_mesh = None  # Store mesh to be loaded after initialization
        
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
            os.environ['PYVISTA_TRAME_SERVER_PROXY_PREFIX'] = ''
            
            # Import Trame components
            from trame.app import get_server
            from trame.widgets import vtk
            from trame.ui.vuetify import SinglePageLayout
            import asyncio
            
            # Create event to signal when server is ready
            server_ready = threading.Event()
            server_error = threading.Event()
            
            def start_server():
                """Start server in its own thread with proper context."""
                try:
                    # Create new event loop for this thread
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    # Create PyVista plotter IN THIS THREAD to avoid OpenGL context issues
                    self.plotter = pv.Plotter(
                        off_screen=False,
                        notebook=False,
                        window_size=[800, 600]
                    )
                    
                    # Create Trame server
                    self.server = get_server(f"pyvista_server_{self.port}")
                    self.server.client_type = "vue2"
                    self.ctrl = self.server.controller
                    self.state = self.server.state
                    
                    # Build simple UI
                    with SinglePageLayout(self.server) as layout:
                        layout.title.set_text("PyVista 3D Viewer")
                        
                        with layout.content:
                            with vtk.VtkLocalView(self.plotter.ren_win) as view:
                                self.ctrl.view_update = view.update
                                self.ctrl.view_reset_camera = view.reset_camera
                    
                    # Signal that server is ready
                    server_ready.set()
                    
                    # If there's a pending mesh, load it now
                    if self.pending_mesh is not None:
                        self._load_mesh_internal(self.pending_mesh)
                        self.pending_mesh = None
                    
                    # Start the server
                    self.server.start(
                        port=self.port, 
                        show=False, 
                        open_browser=False,
                        exec_mode='task'
                    )
                except Exception as e:
                    logger.error(f"Server start error: {e}")
                    server_error.set()
            
            # Start server thread
            self.server_thread = threading.Thread(target=start_server, daemon=True)
            self.server_thread.start()
            
            # Wait for server to be ready or error
            if server_ready.wait(timeout=5):
                self.initialized = True
                logger.info(f"Trame server initialized on port {self.port}")
                return True
            elif server_error.is_set():
                logger.error("Server failed to start due to error")
                return False
            else:
                logger.error("Server initialization timeout")
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
    
    def _load_mesh_internal(self, mesh: pv.PolyData) -> bool:
        """Internal method to load mesh - must be called in server thread."""
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
            
            # Update view if in interactive mode
            if hasattr(self, 'ctrl') and hasattr(self.ctrl, 'view_update'):
                if callable(self.ctrl.view_update):
                    self.ctrl.view_update()
                    
            return True
        except Exception as e:
            logger.error(f"Failed to load mesh: {e}")
            return False
    
    def load_mesh(self, mesh: pv.PolyData) -> bool:
        """Load a mesh for visualization."""
        if not self.initialized:
            if not self.initialize():
                return False
        
        if self.mode == "interactive":
            # Store mesh to be loaded by server thread
            self.pending_mesh = mesh
            # Wait a bit for it to be processed
            import time
            time.sleep(0.5)
            return True
        else:
            # Off-screen mode - load directly
            return self._load_mesh_internal(mesh)
    
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