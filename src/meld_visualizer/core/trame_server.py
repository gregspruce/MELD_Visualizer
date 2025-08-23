"""
Trame server module for web-based PyVista visualization in MELD Visualizer.

This module provides a Trame server that integrates with Dash,
enabling high-performance 3D visualization with PyVista backend.
"""

import asyncio
import threading
import logging
from typing import Dict, Optional, Any, Callable, List
from dataclasses import dataclass, field
import numpy as np
import pandas as pd

import pyvista as pv
# For PyVista >= 0.44, get_cmap is available from matplotlib
import matplotlib.pyplot as plt

from trame.app import get_server
from trame.ui.vuetify import SinglePageLayout
from trame.widgets import vuetify, vtk, client
# Note: serialize module location may vary by trame_vtk version
try:
    from trame_vtk.modules.vtk import serialize
except ImportError:
    try:
        from trame_vtk.modules import serialize
    except ImportError:
        # Fallback for newer versions - serialize may not be needed
        serialize = None

logger = logging.getLogger(__name__)


@dataclass
class TrameConfig:
    """Configuration for Trame server."""
    port: int = 8051
    host: str = "localhost"
    debug: bool = False
    hot_reload: bool = False
    title: str = "MELD 3D Visualizer"
    theme: str = "dark"
    width: int = 1200
    height: int = 800
    
    # Rendering options
    background: tuple = (0.1, 0.1, 0.1)
    show_axes: bool = True
    show_grid: bool = True
    show_scalar_bar: bool = True
    
    # Camera defaults
    camera_position: str = 'iso'
    parallel_projection: bool = False
    
    # Interaction settings
    enable_picking: bool = True
    enable_measurements: bool = True
    enable_clipping: bool = True


class TrameVisualizationServer:
    """
    Trame server for PyVista-based 3D visualization.
    
    Provides web-based interface with full interactivity,
    integrates seamlessly with Dash application.
    """
    
    def __init__(self, config: Optional[TrameConfig] = None):
        """
        Initialize Trame server.
        
        Args:
            config: Server configuration
        """
        self.config = config or TrameConfig()
        self.server = get_server(client_type="vue2")
        self.state = self.server.state
        self.ctrl = self.server.controller
        
        # PyVista components
        self.plotter = None
        self.current_mesh = None
        self.scalar_bars = {}
        self.picked_points = []
        self.measurements = []
        
        # Callbacks from Dash
        self.dash_callbacks = {}
        
        # Initialize server state
        self._initialize_state()
        
        # Setup UI
        self._setup_ui()
        
        # Setup controllers
        self._setup_controllers()
        
        # Thread management
        self._server_thread = None
        self._running = False
    
    def _initialize_state(self):
        """Initialize Trame state variables."""
        self.state.active_mesh = None
        self.state.color_map = "viridis"
        self.state.color_range = [0, 1]
        self.state.opacity = 1.0
        self.state.edge_visibility = False
        self.state.lighting = True
        self.state.show_axes = self.config.show_axes
        self.state.show_grid = self.config.show_grid
        self.state.show_scalar_bar = self.config.show_scalar_bar
        
        # Interaction state
        self.state.picking_mode = "point"
        self.state.measurement_mode = False
        self.state.clipping_enabled = False
        self.state.clip_normal = [1, 0, 0]
        self.state.clip_origin = [0, 0, 0]
        
        # Camera state
        self.state.camera_position = [1.5, 1.5, 1.5]
        self.state.camera_focal_point = [0, 0, 0]
        self.state.camera_up = [0, 0, 1]
        
        # LOD state
        self.state.lod_level = "high"
        self.state.auto_lod = True
        
    def _setup_ui(self):
        """Setup Trame UI layout."""
        with SinglePageLayout(self.server) as layout:
            layout.title = self.config.title
            
            # Toolbar
            with layout.toolbar:
                # Logo/Title
                vuetify.VToolbarTitle("MELD 3D Visualizer")
                vuetify.VSpacer()
                
                # View controls
                vuetify.VBtn(
                    "Reset Camera",
                    click="reset_camera",
                    small=True,
                    class_="mx-1"
                )
                
                vuetify.VBtn(
                    "Screenshot",
                    click="take_screenshot",
                    small=True,
                    class_="mx-1"
                )
                
                # Theme toggle
                vuetify.VSwitch(
                    v_model=("dark_theme", True),
                    hide_details=True,
                    dense=True,
                    change="toggle_theme"
                )
            
            # Drawer - Control Panel
            with layout.drawer as drawer:
                drawer.width = 300
                
                # Visualization Controls Card
                with vuetify.VCard(class_="mb-4"):
                    vuetify.VCardTitle("Visualization", class_="py-2")
                    with vuetify.VCardText():
                        # Color map selector
                        vuetify.VSelect(
                            v_model=("color_map", "viridis"),
                            items=["viridis", "plasma", "inferno", "magma", "jet", "rainbow"],
                            label="Color Map",
                            dense=True,
                            hide_details=True,
                            change=self.update_color_map
                        )
                        
                        # Opacity slider
                        vuetify.VSlider(
                            v_model=("opacity", 1.0),
                            min=0.1,
                            max=1.0,
                            step=0.1,
                            label="Opacity",
                            thumb_label="always",
                            hide_details=True,
                            change=self.update_opacity
                        )
                        
                        # Edge visibility
                        vuetify.VSwitch(
                            v_model=("edge_visibility", False),
                            label="Show Edges",
                            dense=True,
                            hide_details=True,
                            change=self.update_edge_visibility
                        )
                        
                        # Scalar bar
                        vuetify.VSwitch(
                            v_model=("show_scalar_bar", True),
                            label="Show Color Bar",
                            dense=True,
                            hide_details=True,
                            change=self.toggle_scalar_bar
                        )
                
                # Interaction Controls Card
                with vuetify.VCard(class_="mb-4"):
                    vuetify.VCardTitle("Interaction", class_="py-2")
                    with vuetify.VCardText():
                        # Picking mode
                        vuetify.VRadioGroup(
                            v_model=("picking_mode", "point"),
                            label="Selection Mode",
                            hide_details=True,
                            dense=True,
                            change=self.update_picking_mode
                        )
                        vuetify.VRadio(label="Point", value="point")
                        vuetify.VRadio(label="Cell", value="cell")
                        vuetify.VRadio(label="None", value="none")
                        
                        # Measurement mode
                        vuetify.VSwitch(
                            v_model=("measurement_mode", False),
                            label="Measurement Tool",
                            dense=True,
                            hide_details=True,
                            change=self.toggle_measurement
                        )
                        
                        # Clear selections
                        vuetify.VBtn(
                            "Clear Selections",
                            click="clear_selections",
                            small=True,
                            block=True,
                            class_="mt-2"
                        )
                
                # Performance Controls Card
                with vuetify.VCard(class_="mb-4"):
                    vuetify.VCardTitle("Performance", class_="py-2")
                    with vuetify.VCardText():
                        # LOD selector
                        vuetify.VSelect(
                            v_model=("lod_level", "high"),
                            items=["low", "medium", "high"],
                            label="Level of Detail",
                            dense=True,
                            hide_details=True,
                            change=self.update_lod
                        )
                        
                        # Auto LOD
                        vuetify.VSwitch(
                            v_model=("auto_lod", True),
                            label="Auto LOD",
                            dense=True,
                            hide_details=True
                        )
                
                # Clipping Controls Card
                with vuetify.VCard():
                    vuetify.VCardTitle("Clipping", class_="py-2")
                    with vuetify.VCardText():
                        # Enable clipping
                        vuetify.VSwitch(
                            v_model=("clipping_enabled", False),
                            label="Enable Clipping",
                            dense=True,
                            hide_details=True,
                            change=self.toggle_clipping
                        )
                        
                        # Clip plane normal
                        vuetify.VSelect(
                            v_model=("clip_plane", "x"),
                            items=["x", "y", "z", "custom"],
                            label="Clip Plane",
                            dense=True,
                            hide_details=True,
                            change=self.update_clip_plane
                        )
            
            # Main content - 3D viewer
            with layout.content:
                with vuetify.VContainer(fluid=True, class_="pa-0 fill-height"):
                    # Create view with vtk.js
                    view = vtk.VtkLocalView(
                        self.plotter.ren_win if self.plotter else None,
                        ref="view",
                        style="width: 100%; height: 100%;"
                    )
                    self.ctrl.view_update = view.update
                    self.ctrl.view_reset_camera = view.reset_camera
    
    def _setup_controllers(self):
        """Setup Trame controllers and callbacks."""
        
        @self.ctrl.set("reset_camera")
        def reset_camera():
            if self.plotter:
                self.plotter.reset_camera()
                self.ctrl.view_update()
        
        @self.ctrl.set("take_screenshot")
        def take_screenshot():
            if self.plotter:
                screenshot = self.plotter.screenshot(return_img=True)
                # Send to Dash via callback
                if 'screenshot' in self.dash_callbacks:
                    self.dash_callbacks['screenshot'](screenshot)
                return screenshot
        
        @self.ctrl.set("update_color_map")
        def update_color_map():
            if self.current_mesh and self.plotter:
                cmap = self.state.color_map
                self.plotter.update_scalar_bar_range(
                    clim=self.state.color_range,
                    cmap=cmap
                )
                self.ctrl.view_update()
        
        @self.ctrl.set("update_opacity")
        def update_opacity():
            if self.current_mesh and self.plotter:
                self.plotter.update_scalar_bar_range(
                    opacity=self.state.opacity
                )
                self.ctrl.view_update()
        
        @self.ctrl.set("update_edge_visibility")
        def update_edge_visibility():
            if self.current_mesh and self.plotter:
                self.plotter.show_edges = self.state.edge_visibility
                self.ctrl.view_update()
        
        @self.ctrl.set("toggle_scalar_bar")
        def toggle_scalar_bar():
            if self.plotter:
                if self.state.show_scalar_bar:
                    self.plotter.show_scalar_bar()
                else:
                    self.plotter.remove_scalar_bar()
                self.ctrl.view_update()
        
        @self.ctrl.set("update_picking_mode")
        def update_picking_mode():
            if self.plotter:
                if self.state.picking_mode == "none":
                    self.plotter.disable_picking()
                elif self.state.picking_mode == "point":
                    self.plotter.enable_point_picking(
                        callback=self._on_point_picked,
                        show_message=True
                    )
                elif self.state.picking_mode == "cell":
                    self.plotter.enable_cell_picking(
                        callback=self._on_cell_picked,
                        show_message=True
                    )
        
        @self.ctrl.set("toggle_measurement")
        def toggle_measurement():
            if self.state.measurement_mode:
                self.enable_measurement_tool()
            else:
                self.disable_measurement_tool()
        
        @self.ctrl.set("clear_selections")
        def clear_selections():
            self.picked_points.clear()
            self.measurements.clear()
            if self.plotter:
                # Remove all annotation actors
                self.plotter.clear_point_actors()
                self.ctrl.view_update()
        
        @self.ctrl.set("update_lod")
        def update_lod():
            if 'lod_change' in self.dash_callbacks:
                self.dash_callbacks['lod_change'](self.state.lod_level)
        
        @self.ctrl.set("toggle_clipping")
        def toggle_clipping():
            if self.plotter and self.current_mesh:
                if self.state.clipping_enabled:
                    self.enable_clipping()
                else:
                    self.disable_clipping()
        
        @self.ctrl.set("update_clip_plane")
        def update_clip_plane():
            if self.state.clipping_enabled:
                self.update_clipping_plane()
        
        @self.ctrl.set("toggle_theme")
        def toggle_theme():
            self.config.theme = "dark" if self.state.dark_theme else "light"
            self._update_theme()
    
    def create_plotter(self):
        """Create PyVista plotter with proper configuration."""
        self.plotter = pv.Plotter(
            off_screen=False,
            notebook=False,
            title=self.config.title,
            window_size=(self.config.width, self.config.height),
            multi_samples=8,
            line_smoothing=True,
            point_smoothing=True,
            polygon_smoothing=True,
            lighting='three_lights'
        )
        
        # Set background
        self.plotter.set_background(self.config.background)
        
        # Add axes
        if self.config.show_axes:
            self.plotter.show_axes()
        
        # Add grid
        if self.config.show_grid:
            self.plotter.show_grid()
        
        # Set camera
        self.plotter.camera_position = self.config.camera_position
        
        return self.plotter
    
    def update_mesh(self,
                   mesh: pv.PolyData,
                   scalar: Optional[str] = None,
                   cmap: str = "viridis",
                   clim: Optional[tuple] = None):
        """
        Update displayed mesh.
        
        Args:
            mesh: PyVista mesh to display
            scalar: Scalar field name for coloring
            cmap: Colormap name
            clim: Color limits
        """
        if not self.plotter:
            self.create_plotter()
        
        # Clear previous mesh
        if self.current_mesh:
            self.plotter.clear()
            if self.config.show_axes:
                self.plotter.show_axes()
            if self.config.show_grid:
                self.plotter.show_grid()
        
        # Add new mesh
        self.current_mesh = mesh
        
        # Determine scalar and color limits
        if scalar and scalar in mesh.array_names:
            if clim is None:
                clim = mesh.get_data_range(scalar)
        else:
            scalar = None
        
        # Add mesh to plotter
        self.plotter.add_mesh(
            mesh,
            scalars=scalar,
            cmap=cmap,
            clim=clim,
            show_scalar_bar=self.config.show_scalar_bar,
            opacity=self.state.opacity,
            show_edges=self.state.edge_visibility,
            edge_color='white',
            lighting=self.state.lighting,
            smooth_shading=True
        )
        
        # Update state
        self.state.active_mesh = "loaded"
        self.state.color_range = list(clim) if clim else [0, 1]
        
        # Update view
        if hasattr(self.ctrl, 'view_update'):
            self.ctrl.view_update()
    
    def update_mesh_from_dataframe(self,
                                   df: pd.DataFrame,
                                   color_column: str,
                                   lod: str = 'high'):
        """
        Update mesh from DataFrame using PyVista generator.
        
        Args:
            df: DataFrame with mesh data
            color_column: Column for coloring
            lod: Level of detail
        """
        from .pyvista_mesh import PyVistaMeshGenerator
        
        generator = PyVistaMeshGenerator()
        mesh = generator.generate_swept_mesh(df, color_column, lod)
        
        if mesh:
            self.update_mesh(mesh, scalar=color_column)
    
    def _on_point_picked(self, picked_point):
        """Handle point picking event."""
        self.picked_points.append(picked_point)
        
        # Add sphere at picked point
        if self.plotter:
            sphere = pv.Sphere(radius=1, center=picked_point)
            self.plotter.add_mesh(sphere, color='red', opacity=0.5)
            self.ctrl.view_update()
        
        # Notify Dash
        if 'point_picked' in self.dash_callbacks:
            self.dash_callbacks['point_picked'](picked_point)
        
        # Handle measurement mode
        if self.state.measurement_mode and len(self.picked_points) >= 2:
            self._calculate_measurement()
    
    def _on_cell_picked(self, picked_cell):
        """Handle cell picking event."""
        if 'cell_picked' in self.dash_callbacks:
            self.dash_callbacks['cell_picked'](picked_cell)
    
    def _calculate_measurement(self):
        """Calculate distance between last two picked points."""
        if len(self.picked_points) >= 2:
            p1 = self.picked_points[-2]
            p2 = self.picked_points[-1]
            distance = np.linalg.norm(np.array(p2) - np.array(p1))
            
            # Add line
            if self.plotter:
                line = pv.Line(p1, p2)
                self.plotter.add_mesh(line, color='yellow', line_width=3)
                
                # Add text
                midpoint = (np.array(p1) + np.array(p2)) / 2
                self.plotter.add_text(
                    f"{distance:.2f} mm",
                    position=midpoint,
                    font_size=10,
                    color='yellow'
                )
                
                self.ctrl.view_update()
            
            # Store measurement
            self.measurements.append({
                'p1': p1,
                'p2': p2,
                'distance': distance
            })
            
            # Notify Dash
            if 'measurement' in self.dash_callbacks:
                self.dash_callbacks['measurement'](self.measurements[-1])
    
    def enable_measurement_tool(self):
        """Enable measurement tool."""
        self.state.measurement_mode = True
        if self.plotter:
            self.plotter.enable_point_picking(
                callback=self._on_point_picked,
                show_message=True,
                use_mesh=True
            )
    
    def disable_measurement_tool(self):
        """Disable measurement tool."""
        self.state.measurement_mode = False
        if self.plotter:
            self.plotter.disable_picking()
    
    def enable_clipping(self):
        """Enable clipping plane."""
        if self.plotter and self.current_mesh:
            normal = self.state.clip_normal
            origin = self.state.clip_origin
            
            self.plotter.add_mesh_clip_plane(
                self.current_mesh,
                normal=normal,
                origin=origin,
                invert=False
            )
            self.ctrl.view_update()
    
    def disable_clipping(self):
        """Disable clipping plane."""
        if self.plotter:
            self.plotter.clear_plane_widgets()
            self.ctrl.view_update()
    
    def update_clipping_plane(self):
        """Update clipping plane orientation."""
        plane_map = {
            'x': [1, 0, 0],
            'y': [0, 1, 0],
            'z': [0, 0, 1]
        }
        
        if self.state.clip_plane in plane_map:
            self.state.clip_normal = plane_map[self.state.clip_plane]
            
            if self.state.clipping_enabled:
                self.disable_clipping()
                self.enable_clipping()
    
    def _update_theme(self):
        """Update theme colors."""
        if self.plotter:
            if self.config.theme == "dark":
                self.plotter.set_background((0.1, 0.1, 0.1))
            else:
                self.plotter.set_background((0.95, 0.95, 0.95))
            self.ctrl.view_update()
    
    def register_dash_callback(self, name: str, callback: Callable):
        """
        Register callback from Dash.
        
        Args:
            name: Callback name
            callback: Callback function
        """
        self.dash_callbacks[name] = callback
    
    def start(self):
        """Start Trame server in separate thread."""
        if not self._running:
            self._running = True
            self._server_thread = threading.Thread(
                target=self._run_server,
                daemon=True
            )
            self._server_thread.start()
            logger.info(f"Trame server started on {self.config.host}:{self.config.port}")
    
    def stop(self):
        """Stop Trame server."""
        if self._running:
            self._running = False
            self.server.stop()
            if self._server_thread:
                self._server_thread.join(timeout=5)
            logger.info("Trame server stopped")
    
    def _run_server(self):
        """Run server in thread."""
        try:
            self.server.start(
                port=self.config.port,
                host=self.config.host,
                debug=self.config.debug,
                open=False,
                disable_logging=not self.config.debug
            )
        except Exception as e:
            logger.error(f"Trame server error: {e}")
            self._running = False
    
    def get_embed_url(self) -> str:
        """Get URL for embedding in iframe."""
        return f"http://{self.config.host}:{self.config.port}"
    
    def export_state(self) -> Dict[str, Any]:
        """Export current visualization state."""
        return {
            'camera': {
                'position': list(self.plotter.camera.position) if self.plotter else None,
                'focal_point': list(self.plotter.camera.focal_point) if self.plotter else None,
                'up': list(self.plotter.camera.up) if self.plotter else None,
            },
            'visualization': {
                'color_map': self.state.color_map,
                'color_range': self.state.color_range,
                'opacity': self.state.opacity,
                'edge_visibility': self.state.edge_visibility,
                'show_scalar_bar': self.state.show_scalar_bar,
            },
            'interaction': {
                'picked_points': self.picked_points,
                'measurements': self.measurements,
            },
            'performance': {
                'lod_level': self.state.lod_level,
                'auto_lod': self.state.auto_lod,
            }
        }
    
    def import_state(self, state: Dict[str, Any]):
        """Import visualization state."""
        if 'camera' in state and self.plotter:
            cam = state['camera']
            if cam['position']:
                self.plotter.camera.position = cam['position']
            if cam['focal_point']:
                self.plotter.camera.focal_point = cam['focal_point']
            if cam['up']:
                self.plotter.camera.up = cam['up']
        
        if 'visualization' in state:
            viz = state['visualization']
            self.state.color_map = viz.get('color_map', 'viridis')
            self.state.color_range = viz.get('color_range', [0, 1])
            self.state.opacity = viz.get('opacity', 1.0)
            self.state.edge_visibility = viz.get('edge_visibility', False)
            self.state.show_scalar_bar = viz.get('show_scalar_bar', True)
        
        if 'performance' in state:
            perf = state['performance']
            self.state.lod_level = perf.get('lod_level', 'high')
            self.state.auto_lod = perf.get('auto_lod', True)
        
        if hasattr(self.ctrl, 'view_update'):
            self.ctrl.view_update()