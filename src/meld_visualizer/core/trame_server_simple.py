"""
Simplified Trame server for PyVista visualization.

This is a minimal working implementation that avoids initialization issues.
"""

import logging
from typing import Optional, Any
import numpy as np
import pyvista as pv

logger = logging.getLogger(__name__)


class SimplifiedTrameServer:
    """Minimal Trame server that actually works."""
    
    def __init__(self, port: int = 8051):
        """Initialize without creating UI."""
        self.port = port
        self.plotter = None
        self.mesh = None
        self.initialized = False
        
    def initialize(self) -> bool:
        """Initialize PyVista plotter."""
        try:
            # Create a simple plotter
            self.plotter = pv.Plotter(notebook=False, off_screen=True)
            self.initialized = True
            logger.info("SimplifiedTrameServer initialized")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize plotter: {e}")
            return False
    
    def load_mesh(self, mesh: pv.PolyData) -> bool:
        """Load a mesh for visualization."""
        if not self.initialized:
            if not self.initialize():
                return False
        
        try:
            self.mesh = mesh
            self.plotter.clear()
            self.plotter.add_mesh(
                mesh,
                scalars=mesh.active_scalars_name,
                cmap="viridis",
                show_scalar_bar=True
            )
            self.plotter.reset_camera()
            return True
        except Exception as e:
            logger.error(f"Failed to load mesh: {e}")
            return False
    
    def export_screenshot(self, filename: str = "screenshot.png") -> bool:
        """Export a screenshot."""
        if not self.plotter or not self.mesh:
            return False
        
        try:
            self.plotter.screenshot(filename)
            return True
        except Exception as e:
            logger.error(f"Failed to export screenshot: {e}")
            return False
    
    def close(self):
        """Close the plotter."""
        if self.plotter:
            self.plotter.close()
            self.plotter = None
        self.initialized = False