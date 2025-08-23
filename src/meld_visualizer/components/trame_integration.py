"""
Dash-Trame integration component for MELD Visualizer.

This module provides seamless integration between Dash and Trame,
enabling PyVista-based 3D visualization within the Dash application.
"""

import logging
from typing import Dict, Optional, Any, Callable
from dash import html, dcc, Input, Output, State, callback, ClientsideFunction
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np

from ..core.trame_server import TrameVisualizationServer, TrameConfig
from ..core.pyvista_mesh import PyVistaMeshGenerator, MeshConfig, MeshOptimizer

logger = logging.getLogger(__name__)


class DashTrameIntegration:
    """
    Integration layer between Dash and Trame for 3D visualization.
    
    Manages Trame server lifecycle, provides Dash components,
    and handles bidirectional communication.
    """
    
    def __init__(self, 
                 trame_config: Optional[TrameConfig] = None,
                 mesh_config: Optional[MeshConfig] = None):
        """
        Initialize Dash-Trame integration.
        
        Args:
            trame_config: Trame server configuration
            mesh_config: Mesh generation configuration
        """
        self.trame_config = trame_config or TrameConfig()
        self.mesh_config = mesh_config or MeshConfig()
        
        # Components
        self.trame_server = TrameVisualizationServer(self.trame_config)
        self.mesh_generator = PyVistaMeshGenerator(self.mesh_config)
        self.mesh_optimizer = MeshOptimizer()
        
        # State management
        self.current_df = None
        self.current_mesh = None
        self.lod_meshes = {}
        
        # Start Trame server
        self.trame_server.start()
        
    def get_visualization_component(self, height: str = "800px") -> html.Div:
        """
        Get Dash component for embedding Trame visualization.
        
        Args:
            height: Height of the visualization container
            
        Returns:
            Dash HTML component containing iframe
        """
        return html.Div([
            # Hidden stores for state management
            dcc.Store(id='trame-mesh-state', data={}),
            dcc.Store(id='trame-camera-state', data={}),
            dcc.Store(id='trame-interaction-state', data={}),
            
            # Iframe embedding Trame server
            html.Iframe(
                id='trame-3d-viewer',
                src=self.trame_server.get_embed_url(),
                style={
                    'width': '100%',
                    'height': height,
                    'border': 'none',
                    'borderRadius': '8px',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
                }
            ),
            
            # Client-side script for iframe communication
            html.Script("""
                // Establish communication with Trame iframe
                window.trameInterface = {
                    postMessage: function(action, data) {
                        const iframe = document.getElementById('trame-3d-viewer');
                        if (iframe && iframe.contentWindow) {
                            iframe.contentWindow.postMessage({
                                action: action,
                                data: data
                            }, '*');
                        }
                    },
                    
                    updateMesh: function(meshData) {
                        this.postMessage('updateMesh', meshData);
                    },
                    
                    updateCamera: function(cameraData) {
                        this.postMessage('updateCamera', cameraData);
                    },
                    
                    updateVisualization: function(vizData) {
                        this.postMessage('updateVisualization', vizData);
                    }
                };
                
                // Listen for messages from Trame
                window.addEventListener('message', function(event) {
                    if (event.origin !== window.location.origin) return;
                    
                    const { action, data } = event.data;
                    
                    // Update Dash stores based on Trame events
                    if (action === 'pointPicked') {
                        window.dash_clientside.set_props('trame-interaction-state', {
                            data: { picked_point: data }
                        });
                    } else if (action === 'cameraChanged') {
                        window.dash_clientside.set_props('trame-camera-state', {
                            data: data
                        });
                    }
                });
            """)
        ], className='trame-visualization-container')
    
    def get_control_panel(self) -> dbc.Card:
        """
        Get Dash control panel for PyVista/Trame settings.
        
        Returns:
            Dash Bootstrap Card with controls
        """
        return dbc.Card([
            dbc.CardHeader("3D Visualization Controls"),
            dbc.CardBody([
                # LOD Control
                dbc.FormGroup([
                    dbc.Label("Level of Detail"),
                    dbc.RadioItems(
                        id='pyvista-lod-selector',
                        options=[
                            {'label': 'Low', 'value': 'low'},
                            {'label': 'Medium', 'value': 'medium'},
                            {'label': 'High', 'value': 'high'},
                            {'label': 'Auto', 'value': 'auto'}
                        ],
                        value='auto',
                        inline=True
                    )
                ]),
                
                # Mesh Generation Method
                dbc.FormGroup([
                    dbc.Label("Mesh Method"),
                    dbc.Select(
                        id='pyvista-mesh-method',
                        options=[
                            {'label': 'Swept (Accurate)', 'value': 'swept'},
                            {'label': 'Tube (Fast)', 'value': 'tube'},
                            {'label': 'Ribbon', 'value': 'ribbon'}
                        ],
                        value='swept'
                    )
                ]),
                
                # Performance Options
                dbc.FormGroup([
                    dbc.Label("Performance"),
                    dbc.Checklist(
                        id='pyvista-performance-options',
                        options=[
                            {'label': 'Smooth Mesh', 'value': 'smooth'},
                            {'label': 'Compute Normals', 'value': 'normals'},
                            {'label': 'Auto-Decimate', 'value': 'decimate'}
                        ],
                        value=['normals'],
                        inline=True
                    )
                ]),
                
                # Export Options
                dbc.ButtonGroup([
                    dbc.Button(
                        "Export STL",
                        id='export-stl-button',
                        color='secondary',
                        size='sm'
                    ),
                    dbc.Button(
                        "Export OBJ",
                        id='export-obj-button',
                        color='secondary',
                        size='sm'
                    ),
                    dbc.Button(
                        "Screenshot",
                        id='trame-screenshot-button',
                        color='secondary',
                        size='sm'
                    )
                ], className='mt-3')
            ])
        ])
    
    def update_mesh_from_dataframe(self,
                                   df: pd.DataFrame,
                                   color_column: str,
                                   lod: str = 'auto',
                                   method: str = 'swept') -> bool:
        """
        Update 3D mesh from DataFrame.
        
        Args:
            df: DataFrame with mesh data
            color_column: Column for coloring
            lod: Level of detail
            method: Mesh generation method
            
        Returns:
            Success status
        """
        try:
            self.current_df = df
            
            # Auto LOD based on data size
            if lod == 'auto':
                n_points = len(df)
                if n_points > 10000:
                    lod = 'low'
                elif n_points > 5000:
                    lod = 'medium'
                else:
                    lod = 'high'
            
            # Generate mesh based on method
            if method == 'swept':
                mesh = self.mesh_generator.generate_swept_mesh(df, color_column, lod)
            else:
                mesh = self.mesh_generator.generate_advanced_mesh(df, color_column, method)
            
            if mesh is None:
                logger.error("Failed to generate mesh")
                return False
            
            # Optimize for web if needed
            if mesh.n_points > 100000:
                mesh = self.mesh_optimizer.optimize_for_web(mesh, max_size_mb=10.0)
            
            # Store mesh
            self.current_mesh = mesh
            
            # Generate LOD chain for progressive loading
            if lod == 'high':
                self.lod_meshes = {
                    'high': mesh,
                    'medium': self.mesh_optimizer.adaptive_decimation(mesh, 50000),
                    'low': self.mesh_optimizer.adaptive_decimation(mesh, 10000)
                }
            
            # Update Trame visualization
            self.trame_server.update_mesh(
                mesh,
                scalar=color_column,
                cmap='viridis',
                clim=mesh.get_data_range(color_column) if color_column in mesh.array_names else None
            )
            
            logger.info(f"Updated mesh with {mesh.n_points} points, {mesh.n_cells} cells")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update mesh: {e}")
            return False
    
    def update_from_plotly_mesh(self,
                                mesh_data: Dict[str, Any],
                                color_column: str = 'values') -> bool:
        """
        Update visualization from existing Plotly mesh data.
        
        Args:
            mesh_data: Dictionary with vertices, faces, vertex_colors
            color_column: Name for color data
            
        Returns:
            Success status
        """
        try:
            # Convert Plotly data to PyVista
            mesh = self.mesh_generator.create_mesh_from_plotly_data(
                vertices=mesh_data['vertices'],
                faces=mesh_data['faces'],
                scalars=mesh_data.get('vertex_colors'),
                scalar_name=color_column
            )
            
            # Optimize if needed
            if mesh.n_points > 100000:
                mesh = self.mesh_optimizer.optimize_for_web(mesh)
            
            self.current_mesh = mesh
            
            # Update visualization
            self.trame_server.update_mesh(
                mesh,
                scalar=color_column if color_column in mesh.array_names else None
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to convert Plotly mesh: {e}")
            return False
    
    def register_callbacks(self, app):
        """
        Register Dash callbacks for Trame integration.
        
        Args:
            app: Dash application instance
        """
        
        @app.callback(
            Output('trame-mesh-state', 'data'),
            Input('generate-mesh-plot-button', 'n_clicks'),
            [State('store-main-df', 'data'),
             State('mesh-plot-color-dropdown', 'value'),
             State('pyvista-lod-selector', 'value'),
             State('pyvista-mesh-method', 'value')],
            prevent_initial_call=True
        )
        def update_trame_mesh(n_clicks, jsonified_df, color_col, lod, method):
            """Update Trame mesh from Dash controls."""
            if not jsonified_df or not color_col:
                return {}
            
            import io
            df = pd.read_json(io.StringIO(jsonified_df), orient='split')
            
            # Filter active data
            mask = (df['FeedVel'] > 0.1) & (df['PathVel'] > 0.1)
            df_active = df[mask].copy()
            
            if df_active.empty:
                return {'error': 'No active data'}
            
            # Update mesh
            success = self.update_mesh_from_dataframe(
                df_active,
                color_col,
                lod=lod,
                method=method
            )
            
            if success:
                return {
                    'status': 'success',
                    'n_points': self.current_mesh.n_points,
                    'n_cells': self.current_mesh.n_cells
                }
            else:
                return {'error': 'Mesh generation failed'}
        
        @app.callback(
            Output('export-stl-output', 'children'),
            Input('export-stl-button', 'n_clicks'),
            prevent_initial_call=True
        )
        def export_stl(n_clicks):
            """Export current mesh as STL."""
            if self.current_mesh:
                filename = 'meld_mesh.stl'
                success = self.mesh_generator.export_mesh(
                    self.current_mesh,
                    filename,
                    binary=True
                )
                return f"Exported to {filename}" if success else "Export failed"
            return "No mesh to export"
        
        @app.callback(
            Output('export-obj-output', 'children'),
            Input('export-obj-button', 'n_clicks'),
            prevent_initial_call=True
        )
        def export_obj(n_clicks):
            """Export current mesh as OBJ."""
            if self.current_mesh:
                filename = 'meld_mesh.obj'
                success = self.mesh_generator.export_mesh(
                    self.current_mesh,
                    filename,
                    binary=False
                )
                return f"Exported to {filename}" if success else "Export failed"
            return "No mesh to export"
        
        # Register Trame callbacks for Dash communication
        self.trame_server.register_dash_callback(
            'lod_change',
            lambda lod: self._handle_lod_change(lod)
        )
        
        self.trame_server.register_dash_callback(
            'screenshot',
            lambda img: self._handle_screenshot(img)
        )
        
        self.trame_server.register_dash_callback(
            'point_picked',
            lambda point: logger.info(f"Point picked: {point}")
        )
        
        self.trame_server.register_dash_callback(
            'measurement',
            lambda data: logger.info(f"Measurement: {data['distance']:.2f} mm")
        )
    
    def _handle_lod_change(self, lod: str):
        """Handle LOD change from Trame UI."""
        if lod in self.lod_meshes:
            mesh = self.lod_meshes[lod]
            self.trame_server.update_mesh(mesh)
            logger.info(f"Switched to {lod} LOD: {mesh.n_points} points")
    
    def _handle_screenshot(self, image_array):
        """Handle screenshot from Trame."""
        # Could save to file or return to user
        logger.info("Screenshot captured")
    
    def get_mesh_statistics(self) -> Dict[str, Any]:
        """Get current mesh statistics."""
        if not self.current_mesh:
            return {}
        
        return self.mesh_generator.compute_mesh_properties(self.current_mesh)
    
    def shutdown(self):
        """Shutdown Trame server and cleanup."""
        self.trame_server.stop()
        logger.info("Dash-Trame integration shutdown complete")


def create_pyvista_visualization_tab() -> dbc.Tab:
    """
    Create a complete PyVista visualization tab for Dash.
    
    Returns:
        Bootstrap Tab component with PyVista/Trame visualization
    """
    # Initialize integration
    integration = DashTrameIntegration()
    
    tab_content = dbc.Card([
        dbc.CardBody([
            dbc.Row([
                # Left side - Controls
                dbc.Col([
                    integration.get_control_panel(),
                    
                    # Statistics card
                    dbc.Card([
                        dbc.CardHeader("Mesh Statistics"),
                        dbc.CardBody(id='mesh-statistics-display')
                    ], className='mt-3'),
                    
                    # Output messages
                    html.Div(id='export-stl-output'),
                    html.Div(id='export-obj-output')
                ], width=3),
                
                # Right side - 3D Viewer
                dbc.Col([
                    integration.get_visualization_component(height="85vh")
                ], width=9)
            ])
        ])
    ])
    
    return dbc.Tab(
        tab_content,
        label="PyVista 3D View",
        tab_id="pyvista-3d-tab"
    )