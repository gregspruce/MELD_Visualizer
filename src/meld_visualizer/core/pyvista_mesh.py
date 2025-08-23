"""
PyVista-based 3D mesh generation and processing module for MELD Visualizer.

This module provides high-performance mesh generation using PyVista,
replacing the Plotly-based visualization with more advanced capabilities.
"""

import numpy as np
import pandas as pd
import pyvista as pv
from typing import Dict, Optional, List, Tuple, Any, Union
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class MeshConfig:
    """Configuration for mesh generation."""
    points_per_section: int = 12
    bead_length: float = 2.0
    bead_radius: float = 1.0
    width_multiplier: float = 1.0
    smooth_mesh: bool = True
    compute_normals: bool = True
    decimate_ratio: Optional[float] = None


class PyVistaMeshGenerator:
    """
    High-performance 3D mesh generator using PyVista.
    
    Provides advanced mesh generation with built-in optimization,
    decimation, and filtering capabilities.
    """
    
    def __init__(self, config: Optional[MeshConfig] = None):
        """
        Initialize PyVista mesh generator.
        
        Args:
            config: Mesh generation configuration
        """
        self.config = config or MeshConfig()
        self._mesh_cache = {}
        
    def create_capsule_profile(self,
                               n_points: int = 12,
                               radius: float = 1.0,
                               length: float = 2.0) -> pv.PolyData:
        """
        Create a capsule-shaped profile for extrusion.
        
        Args:
            n_points: Number of points in the profile
            radius: Radius of semi-circular ends
            length: Length of straight section
            
        Returns:
            PolyData representing the capsule profile
        """
        points = []
        half_n = n_points // 2
        
        # Left semi-circle
        for i in range(half_n):
            angle = np.pi/2 + (np.pi * i) / (half_n - 1)
            x = -length/2 + radius * np.cos(angle)
            y = radius * np.sin(angle)
            points.append([x, y, 0])
        
        # Right semi-circle
        for i in range(half_n):
            angle = -np.pi/2 + (np.pi * i) / (half_n - 1)
            x = length/2 + radius * np.cos(angle)
            y = radius * np.sin(angle)
            points.append([x, y, 0])
        
        # Create closed polygon
        points = np.array(points)
        lines = np.column_stack([
            np.arange(n_points),
            np.roll(np.arange(n_points), -1)
        ])
        
        profile = pv.PolyData(points)
        profile.lines = lines
        
        return profile
    
    def generate_toolpath_spline(self,
                                 df: pd.DataFrame,
                                 smooth_factor: int = 100) -> pv.PolyData:
        """
        Generate smooth spline from toolpath points.
        
        Args:
            df: DataFrame with XPos, YPos, ZPos columns
            smooth_factor: Number of points in smoothed spline
            
        Returns:
            PolyData representing the toolpath spline
        """
        points = df[['XPos', 'YPos', 'ZPos']].values.astype(np.float32)
        
        # Create polyline
        polyline = pv.PolyData(points)
        polyline.lines = np.column_stack([
            np.full(len(points) - 1, 2),
            np.arange(len(points) - 1),
            np.arange(1, len(points))
        ]).ravel()
        
        # Smooth the path if needed
        if smooth_factor > len(points):
            try:
                spline = polyline.tube(radius=0.01).extract_surface()
                spline = spline.decimate_boundary(target_reduction=0.95)
                return spline.extract_feature_edges(feature_angle=15)
            except:
                logger.warning("Spline smoothing failed, using raw polyline")
                return polyline
        
        return polyline
    
    def generate_swept_mesh(self,
                           df: pd.DataFrame,
                           color_column: str,
                           lod: str = 'high') -> pv.PolyData:
        """
        Generate swept mesh along toolpath using PyVista.
        
        Args:
            df: DataFrame with position, thickness, and color data
            color_column: Column name for mesh coloring
            lod: Level of detail ('low', 'medium', 'high')
            
        Returns:
            PyVista PolyData mesh with scalar data
        """
        # Validate input data
        required_cols = ['XPos', 'YPos', 'ZPos', 'Bead_Thickness_mm']
        if not all(col in df.columns for col in required_cols):
            logger.error(f"Missing required columns: {required_cols}")
            return None
        
        # LOD settings
        lod_config = {
            'low': {'points': 6, 'skip': 4, 'decimate': 0.5},
            'medium': {'points': 8, 'skip': 2, 'decimate': 0.3},
            'high': {'points': 12, 'skip': 1, 'decimate': None}
        }
        
        settings = lod_config.get(lod, lod_config['high'])
        
        # Downsample data for lower LOD
        if settings['skip'] > 1:
            df_sampled = df.iloc[::settings['skip']].copy()
            if len(df) > 0 and df.index[-1] not in df_sampled.index:
                df_sampled = pd.concat([df_sampled, df.iloc[[-1]]])
        else:
            df_sampled = df
        
        # Create path points
        points = df_sampled[['XPos', 'YPos', 'ZPos']].values.astype(np.float32)
        
        # Create segments and accumulate meshes
        meshes = []
        colors = []
        
        for i in range(len(points) - 1):
            # Get segment properties
            p1, p2 = points[i], points[i + 1]
            thickness1 = df_sampled.iloc[i]['Bead_Thickness_mm']
            thickness2 = df_sampled.iloc[i + 1]['Bead_Thickness_mm']
            
            # Skip invalid segments
            if np.linalg.norm(p2 - p1) < 1e-6:
                continue
            
            # Create cylinder segment with varying radius
            try:
                # Create a tapered cylinder
                direction = p2 - p1
                height = np.linalg.norm(direction)
                
                # Average thickness with width multiplier
                avg_thickness = (thickness1 + thickness2) / 2 * self.config.width_multiplier
                
                # Create cylinder
                cylinder = pv.Cylinder(
                    center=(p1 + p2) / 2,
                    direction=direction,
                    radius=avg_thickness / 2,
                    height=height,
                    resolution=settings['points']
                )
                
                # Add color scalar
                color_value = df_sampled.iloc[i][color_column]
                cylinder[color_column] = np.full(cylinder.n_points, color_value)
                
                meshes.append(cylinder)
                
            except Exception as e:
                logger.warning(f"Failed to create segment {i}: {e}")
                continue
        
        # Combine all segments
        if not meshes:
            logger.error("No valid mesh segments generated")
            return None
        
        # Merge meshes
        combined_mesh = meshes[0]
        for mesh in meshes[1:]:
            combined_mesh = combined_mesh.merge(mesh)
        
        # Apply decimation for LOD
        if settings['decimate']:
            combined_mesh = combined_mesh.decimate(settings['decimate'])
        
        # Smooth mesh if configured
        if self.config.smooth_mesh:
            combined_mesh = combined_mesh.smooth(n_iter=50)
        
        # Compute normals for better lighting
        if self.config.compute_normals:
            combined_mesh = combined_mesh.compute_normals()
        
        logger.info(f"Generated PyVista mesh: {combined_mesh.n_points} points, {combined_mesh.n_cells} cells")
        
        return combined_mesh
    
    def generate_advanced_mesh(self,
                              df: pd.DataFrame,
                              color_column: str,
                              method: str = 'tube') -> pv.PolyData:
        """
        Generate mesh using advanced PyVista methods.
        
        Args:
            df: DataFrame with position and property data
            color_column: Column for coloring
            method: Generation method ('tube', 'ribbon', 'sweep')
            
        Returns:
            PyVista PolyData mesh
        """
        # Create path
        points = df[['XPos', 'YPos', 'ZPos']].values.astype(np.float32)
        path = pv.PolyData(points)
        
        # Create line connections
        lines = np.column_stack([
            np.full(len(points) - 1, 2),
            np.arange(len(points) - 1),
            np.arange(1, len(points))
        ]).ravel()
        path.lines = lines
        
        # Add scalar data
        path[color_column] = df[color_column].values
        
        if 'Bead_Thickness_mm' in df.columns:
            path['thickness'] = df['Bead_Thickness_mm'].values
        
        # Generate mesh based on method
        if method == 'tube':
            # Variable radius tube
            if 'thickness' in path.array_names:
                mesh = path.tube(radius=0.5, scalars='thickness', radius_factor=10)
            else:
                mesh = path.tube(radius=self.config.bead_radius)
                
        elif method == 'ribbon':
            # Create ribbon mesh
            mesh = path.ribbon(width=self.config.bead_length, scalars=color_column)
            
        elif method == 'sweep':
            # Create profile and sweep
            profile = self.create_capsule_profile(
                n_points=self.config.points_per_section,
                radius=self.config.bead_radius,
                length=self.config.bead_length
            )
            
            # PyVista doesn't have direct sweep, so we approximate
            mesh = path.tube(radius=self.config.bead_radius)
        
        else:
            logger.warning(f"Unknown method {method}, using tube")
            mesh = path.tube(radius=self.config.bead_radius)
        
        # Post-process mesh
        if self.config.smooth_mesh:
            mesh = mesh.smooth(n_iter=100)
        
        if self.config.compute_normals:
            mesh = mesh.compute_normals()
        
        # Ensure color data is preserved
        if color_column in path.array_names and color_column not in mesh.array_names:
            # Interpolate colors from path to mesh
            mesh = mesh.interpolate(path, radius=5.0)
        
        return mesh
    
    def apply_filters(self,
                     mesh: pv.PolyData,
                     filters: Dict[str, Any]) -> pv.PolyData:
        """
        Apply various filters to the mesh.
        
        Args:
            mesh: Input mesh
            filters: Dictionary of filter configurations
            
        Returns:
            Filtered mesh
        """
        result = mesh.copy()
        
        # Decimation
        if filters.get('decimate'):
            ratio = filters.get('decimate_ratio', 0.5)
            result = result.decimate(ratio)
            logger.info(f"Decimated mesh to {result.n_points} points")
        
        # Smoothing
        if filters.get('smooth'):
            iterations = filters.get('smooth_iterations', 100)
            result = result.smooth(n_iter=iterations)
        
        # Subdivision
        if filters.get('subdivide'):
            levels = filters.get('subdivide_levels', 1)
            result = result.subdivide(levels)
        
        # Clean
        if filters.get('clean'):
            result = result.clean()
        
        # Extract largest region
        if filters.get('extract_largest'):
            result = result.extract_largest()
        
        return result
    
    def compute_mesh_properties(self, mesh: pv.PolyData) -> Dict[str, Any]:
        """
        Compute various mesh properties.
        
        Args:
            mesh: Input mesh
            
        Returns:
            Dictionary of mesh properties
        """
        properties = {
            'n_points': mesh.n_points,
            'n_cells': mesh.n_cells,
            'bounds': mesh.bounds,
            'center': mesh.center,
            'volume': mesh.volume if mesh.is_all_triangles else None,
            'area': mesh.area,
            'length': mesh.length,
            'memory_size': mesh.actual_memory_size,
        }
        
        # Add scalar ranges
        for name in mesh.array_names:
            scalar_range = mesh.get_data_range(name)
            properties[f'{name}_range'] = scalar_range
        
        return properties
    
    def export_mesh(self,
                   mesh: pv.PolyData,
                   filename: str,
                   binary: bool = True) -> bool:
        """
        Export mesh to various formats.
        
        Args:
            mesh: Mesh to export
            filename: Output filename
            binary: Use binary format where applicable
            
        Returns:
            Success status
        """
        try:
            mesh.save(filename, binary=binary)
            logger.info(f"Exported mesh to {filename}")
            return True
        except Exception as e:
            logger.error(f"Failed to export mesh: {e}")
            return False
    
    def create_mesh_from_plotly_data(self,
                                     vertices: np.ndarray,
                                     faces: np.ndarray,
                                     scalars: Optional[np.ndarray] = None,
                                     scalar_name: str = 'values') -> pv.PolyData:
        """
        Convert existing Plotly mesh data to PyVista format.
        
        Args:
            vertices: Nx3 array of vertex positions
            faces: Mx3 array of face indices
            scalars: Optional array of scalar values
            scalar_name: Name for scalar data
            
        Returns:
            PyVista PolyData mesh
        """
        # Create faces array in VTK format
        # VTK expects [n_verts, v1, v2, v3, n_verts, v1, v2, v3, ...]
        vtk_faces = np.column_stack([
            np.full(len(faces), 3),  # 3 vertices per face
            faces
        ]).ravel()
        
        # Create mesh
        mesh = pv.PolyData(vertices, vtk_faces)
        
        # Add scalar data if provided
        if scalars is not None:
            mesh[scalar_name] = scalars
        
        # Compute normals for better rendering
        mesh = mesh.compute_normals()
        
        return mesh


class MeshOptimizer:
    """Optimization utilities for large meshes."""
    
    @staticmethod
    def adaptive_decimation(mesh: pv.PolyData,
                           target_points: int = 50000,
                           preserve_topology: bool = True) -> pv.PolyData:
        """
        Adaptively decimate mesh to target point count.
        
        Args:
            mesh: Input mesh
            target_points: Target number of points
            preserve_topology: Preserve mesh topology
            
        Returns:
            Decimated mesh
        """
        if mesh.n_points <= target_points:
            return mesh
        
        reduction = 1.0 - (target_points / mesh.n_points)
        reduction = np.clip(reduction, 0.0, 0.99)
        
        decimated = mesh.decimate(
            reduction,
            volume_preservation=True,
            attribute_error=False,
            scalars=True,
            vectors=True,
            normals=True,
            tcoords=True,
            tensors=True,
            scalars_weight=0.1,
            vectors_weight=0.1,
            normals_weight=0.1,
            tcoords_weight=0.1,
            tensors_weight=0.1,
            preserve_topology=preserve_topology
        )
        
        logger.info(f"Decimated mesh from {mesh.n_points} to {decimated.n_points} points")
        return decimated
    
    @staticmethod
    def create_lod_chain(mesh: pv.PolyData,
                        levels: List[float] = [1.0, 0.5, 0.25, 0.1]) -> List[pv.PolyData]:
        """
        Create LOD chain for progressive rendering.
        
        Args:
            mesh: High-resolution input mesh
            levels: List of retention ratios
            
        Returns:
            List of meshes at different LOD levels
        """
        lod_meshes = []
        
        for level in levels:
            if level >= 1.0:
                lod_meshes.append(mesh.copy())
            else:
                reduction = 1.0 - level
                lod_mesh = mesh.decimate(reduction)
                lod_meshes.append(lod_mesh)
                logger.info(f"Created LOD level {level}: {lod_mesh.n_points} points")
        
        return lod_meshes
    
    @staticmethod
    def optimize_for_web(mesh: pv.PolyData,
                        max_size_mb: float = 10.0) -> pv.PolyData:
        """
        Optimize mesh for web transmission.
        
        Args:
            mesh: Input mesh
            max_size_mb: Maximum size in MB
            
        Returns:
            Optimized mesh
        """
        current_size_mb = mesh.actual_memory_size / (1024 * 1024)
        
        if current_size_mb <= max_size_mb:
            return mesh
        
        # Calculate required reduction
        reduction = 1.0 - (max_size_mb / current_size_mb)
        reduction = np.clip(reduction, 0.0, 0.95)
        
        # Decimate
        optimized = mesh.decimate(reduction)
        
        # Further optimize
        optimized = optimized.clean()
        optimized = optimized.remove_duplicate_points()
        
        final_size_mb = optimized.actual_memory_size / (1024 * 1024)
        logger.info(f"Optimized mesh from {current_size_mb:.2f}MB to {final_size_mb:.2f}MB")
        
        return optimized