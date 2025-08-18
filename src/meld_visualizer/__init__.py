"""MELD Visualizer - A Dash web application for visualizing 3D process data from MELD manufacturing.

This package provides interactive visualization capabilities for:
- CSV data upload and processing
- G-code visualization and toolpath simulation
- 3D scatter plots and volume meshes
- Theme support and configurable UI

Author: MELD Manufacturing Team
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "MELD Manufacturing Team"

# Optional app import - only import if dependencies are available
try:
    from .app import app
    __all__ = ["app"]
except ImportError:
    __all__ = []