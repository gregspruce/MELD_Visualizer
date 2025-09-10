"""
Volume mesh generation module for MELD Visualizer.

This module handles 3D mesh generation for volume visualization,
separated from volume calculations for modularity and ease of development.
"""

import numpy as np
import pandas as pd
from typing import Dict, Optional, List, Tuple, Any
import logging

logger = logging.getLogger(__name__)


class MeshGenerator:
    """
    Generates 3D mesh data for volume visualization.
    
    This class creates the actual 3D geometry (vertices and faces)
    for rendering the extruded bead volume.
    """
    
    def __init__(self, points_per_section: int = 12):
        """
        Initialize mesh generator.
        
        Args:
            points_per_section: Number of vertices in each cross-section
        """
        self.points_per_section = points_per_section
        self.use_optimized = True  # Flag to use optimized algorithms
        
    def generate_cross_section(self,
                               position: np.ndarray,
                               direction: np.ndarray,
                               thickness: float,
                               bead_length: float,
                               bead_radius: float,
                               width_multiplier: float = 1.0) -> np.ndarray:
        """
        Generate vertices for a single cross-section of the bead.
        
        The cross-section is a capsule shape (rectangle with semi-circular ends).
        
        Args:
            position: 3D position of the cross-section center
            direction: Direction vector of the toolpath
            thickness: Bead thickness (T) in mm
            bead_length: Length of rectangular section (L) in mm
            bead_radius: Radius of semi-circular ends (R) in mm
            
        Returns:
            Array of vertices defining the cross-section
        """
        # Ensure arrays are float32 for consistency
        position = np.asarray(position, dtype=np.float32)
        direction = np.asarray(direction, dtype=np.float32)
        
        # Normalize direction vector
        dir_norm = np.linalg.norm(direction)
        if dir_norm > 1e-9:
            direction = direction / dir_norm
        else:
            direction = np.array([0.0, 1.0, 0.0], dtype=np.float32)
        
        # Create orthogonal basis vectors
        z_axis = np.array([0.0, 0.0, 1.0], dtype=np.float32)
        h_vec = np.cross(direction, z_axis)
        h_norm = np.linalg.norm(h_vec)
        
        if h_norm < 1e-6:
            # Handle vertical toolpaths
            h_vec = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        else:
            h_vec = h_vec / h_norm
        
        u_vec = np.cross(h_vec, direction)
        
        # Apply width multiplier to effectively widen the bead
        effective_thickness = thickness * width_multiplier
        effective_radius = bead_radius * width_multiplier
        
        # Generate vertices for capsule cross-section
        vertices = []
        half_n = self.points_per_section // 2
        
        # Ensure we have at least 2 points per semi-circle to avoid division by zero
        if half_n < 2:
            half_n = 2
            logger.warning(f"Adjusting points_per_section from {self.points_per_section} to 4 to avoid degenerate geometry")
        
        # First semi-circle (left side)
        center_left = position - h_vec * effective_thickness / 2.0
        for i in range(half_n):
            angle = np.pi/2 + (np.pi * i) / (half_n - 1)
            vertex = center_left + effective_radius * (
                np.cos(angle) * h_vec + np.sin(angle) * u_vec
            )
            vertices.append(vertex)
        
        # Second semi-circle (right side)
        center_right = position + h_vec * effective_thickness / 2.0
        for i in range(half_n):
            angle = -np.pi/2 + (np.pi * i) / (half_n - 1)
            vertex = center_right + effective_radius * (
                np.cos(angle) * h_vec + np.sin(angle) * u_vec
            )
            vertices.append(vertex)
        
        return np.array(vertices, dtype=np.float32)
    
    def generate_segment_mesh(self,
                             p1: np.ndarray,
                             p2: np.ndarray,
                             thickness1: float,
                             thickness2: float,
                             bead_length: float,
                             bead_radius: float,
                             width_multiplier: float = 1.0) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate mesh for a single segment between two points.
        
        Args:
            p1: Start position
            p2: End position
            thickness1: Thickness at start
            thickness2: Thickness at end
            bead_length: Bead length parameter
            bead_radius: Bead radius parameter
            
        Returns:
            Tuple of (vertices, faces) for the segment
        """
        direction = p2 - p1
        
        # Skip if points are too close
        if np.linalg.norm(direction) < 1e-6:
            return np.array([]), np.array([])
        
        # Generate cross-sections at both ends  
        verts1 = self.generate_cross_section(
            p1, direction, thickness1, bead_length, bead_radius, width_multiplier
        )
        verts2 = self.generate_cross_section(
            p2, direction, thickness2, bead_length, bead_radius, width_multiplier
        )
        
        # Combine vertices
        vertices = np.vstack([verts1, verts2])
        
        # Generate faces connecting the cross-sections
        faces = []
        n = self.points_per_section
        
        for j in range(n):
            # Indices for the quad
            v1 = j
            v2 = (j + 1) % n
            v3 = n + j
            v4 = n + (j + 1) % n
            
            # Create two triangles for the quad
            faces.append([v1, v3, v4])
            faces.append([v1, v4, v2])
        
        return vertices, np.array(faces, dtype=np.int32)
    
    def generate_mesh(self,
                     df: pd.DataFrame,
                     color_column: str,
                     bead_length: float = 2.0,
                     bead_radius: float = 1.0,
                     width_multiplier: float = 1.0) -> Optional[Dict[str, Any]]:
        """
        Generate complete mesh from DataFrame.
        
        Args:
            df: DataFrame with position and thickness data
            color_column: Column to use for vertex colors
            bead_length: Bead length parameter in mm
            bead_radius: Bead radius parameter in mm
            
        Returns:
            Dictionary with vertices, faces, and vertex_colors
        """
        # Validate required columns
        required_cols = ['XPos', 'YPos', 'ZPos', 'Bead_Thickness_mm']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            logger.error(f"Missing required columns: {missing_cols}")
            return None
        
        if color_column not in df.columns:
            logger.error(f"Color column '{color_column}' not found")
            return None
        
        # Extract data as numpy arrays
        positions = df[['XPos', 'YPos', 'ZPos']].values.astype(np.float32)
        thicknesses = df['Bead_Thickness_mm'].values.astype(np.float32)
        colors = df[color_column].values.astype(np.float32)
        
        # Validate for NaN/Inf values to prevent invalid mesh generation
        positions_valid = np.isfinite(positions).all(axis=1)
        thicknesses_valid = np.isfinite(thicknesses) & (thicknesses > 0)
        colors_valid = np.isfinite(colors)
        valid_mask = positions_valid & thicknesses_valid & colors_valid
        
        if not np.any(valid_mask):
            logger.warning("No valid data points after filtering NaN/Inf values")
            return None
            
        if np.sum(~valid_mask) > 0:
            logger.info(f"Filtered {np.sum(~valid_mask)} invalid data points (NaN/Inf values)")
        
        # Filter to valid data only
        positions = positions[valid_mask]
        thicknesses = thicknesses[valid_mask]
        colors = colors[valid_mask]
        
        # Pre-allocate lists for efficiency
        all_vertices = []
        all_faces = []
        vertex_colors = []
        vertex_offset = 0
        
        # Process each segment
        n_segments = len(positions) - 1
        for i in range(n_segments):
            # Generate segment mesh
            seg_verts, seg_faces = self.generate_segment_mesh(
                positions[i], positions[i+1],
                thicknesses[i], thicknesses[i+1],
                bead_length, bead_radius,
                width_multiplier
            )
            
            # Skip empty segments
            if len(seg_verts) == 0:
                continue
            
            # Add vertices
            all_vertices.append(seg_verts)
            
            # Add faces with proper offset
            if len(seg_faces) > 0:
                all_faces.append(seg_faces + vertex_offset)
            
            # Add colors for all vertices in segment
            n_verts = len(seg_verts)
            vertex_colors.extend([colors[i]] * (n_verts // 2))
            vertex_colors.extend([colors[i+1]] * (n_verts // 2))
            
            vertex_offset += n_verts
        
        # Combine all data
        if not all_vertices:
            logger.warning("No valid mesh segments generated")
            return None
        
        final_vertices = np.vstack(all_vertices)
        final_faces = np.vstack(all_faces) if all_faces else np.array([])
        final_colors = np.array(vertex_colors, dtype=np.float32)
        
        logger.info(f"Generated mesh: {len(final_vertices)} vertices, {len(final_faces)} faces")
        
        return {
            'vertices': final_vertices,
            'faces': final_faces,
            'vertex_colors': final_colors
        }
    
    def generate_mesh_lod(self,
                         df: pd.DataFrame,
                         color_column: str,
                         lod: str = 'high',
                         bead_length: float = 2.0,
                         bead_radius: float = 1.0,
                         width_multiplier: float = 1.0) -> Optional[Dict[str, Any]]:
        """
        Generate mesh with level-of-detail support.
        
        Args:
            df: DataFrame with position and thickness data
            color_column: Column to use for vertex colors
            lod: Level of detail ('low', 'medium', 'high')
            bead_length: Bead length parameter in mm
            bead_radius: Bead radius parameter in mm
            
        Returns:
            Dictionary with vertices, faces, and vertex_colors
        """
        # Validate geometric parameters to prevent invalid mesh generation
        if bead_length <= 0 or bead_radius <= 0:
            logger.error(f"Invalid geometric parameters: length={bead_length}, radius={bead_radius}")
            return None
            
        if width_multiplier <= 0:
            logger.error(f"Invalid width_multiplier: {width_multiplier}")
            return None
        
        # Adjust points per section based on LOD
        lod_settings = {
            'low': {'points': 6, 'skip': 4},
            'medium': {'points': 8, 'skip': 2},
            'high': {'points': 12, 'skip': 1}
        }
        
        settings = lod_settings.get(lod, lod_settings['high'])
        original_points = self.points_per_section
        
        # Temporarily adjust points per section
        self.points_per_section = settings['points']
        
        # Downsample DataFrame if using lower LOD
        if settings['skip'] > 1:
            df_sampled = df.iloc[::settings['skip']].copy()
            # Ensure we keep the last point
            if len(df) > 0 and df.index[-1] not in df_sampled.index:
                df_sampled = pd.concat([df_sampled, df.iloc[[-1]]])
        else:
            df_sampled = df
        
        # Generate mesh with adjusted settings
        result = self.generate_mesh(df_sampled, color_column, bead_length, bead_radius, width_multiplier)
        
        # Restore original setting
        self.points_per_section = original_points
        
        if result:
            logger.info(f"Generated {lod} LOD mesh with {len(result['vertices'])} vertices")
        
        return result


class VolumePlotter:
    """
    High-level interface for volume plotting with integrated calculations and mesh generation.
    """
    
    def __init__(self):
        """Initialize the volume plotter."""
        from .volume_calculations import VolumeCalculator
        
        self.calculator = VolumeCalculator()
        self.mesh_generator = MeshGenerator()
        
    def prepare_data(self,
                    df: pd.DataFrame,
                    min_feed_velocity: float = 0.1,
                    min_path_velocity: float = 0.1) -> pd.DataFrame:
        """
        Prepare DataFrame for volume plotting.
        
        Args:
            df: Input DataFrame
            min_feed_velocity: Minimum feed velocity threshold
            min_path_velocity: Minimum path velocity threshold
            
        Returns:
            Processed DataFrame with volume calculations
        """
        # Filter for active extrusion
        mask = (df['FeedVel'] > min_feed_velocity) & (df['PathVel'] > min_path_velocity)
        df_active = df[mask].copy()
        
        if df_active.empty:
            logger.warning("No active extrusion data found")
            return df_active
        
        # Add volume calculations
        df_active = self.calculator.process_dataframe(df_active)
        
        return df_active
    
    def generate_plot_data(self,
                          df: pd.DataFrame,
                          color_column: str,
                          lod: str = 'high') -> Optional[Dict[str, Any]]:
        """
        Generate plot-ready mesh data.
        
        Args:
            df: Prepared DataFrame with volume calculations
            color_column: Column for coloring
            lod: Level of detail
            
        Returns:
            Mesh data dictionary ready for plotting
        """
        # Ensure volume calculations are present
        if 'Bead_Thickness_mm' not in df.columns:
            df = self.calculator.process_dataframe(df)
        
        # Generate mesh
        mesh_data = self.mesh_generator.generate_mesh_lod(
            df, 
            color_column, 
            lod,
            self.calculator.bead_geometry.length_mm,
            self.calculator.bead_geometry.radius_mm
        )
        
        return mesh_data
    
    def get_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get volume statistics for the data.
        
        Args:
            df: DataFrame with volume calculations
            
        Returns:
            Dictionary of statistics
        """
        return self.calculator.get_statistics(df)
    
    def set_calibration(self,
                       correction_factor: float = 1.0,
                       area_offset: float = 0.0) -> None:
        """
        Set calibration factors for volume calculations.
        
        Args:
            correction_factor: Multiplicative correction
            area_offset: Additive correction in mm²
        """
        self.calculator.set_calibration(correction_factor, area_offset)
    
    def export_config(self) -> Dict[str, Any]:
        """
        Export configuration for persistence.
        
        Returns:
            Dictionary of all configuration parameters
        """
        return {
            'calculator': self.calculator.export_parameters(),
            'mesh_generator': {
                'points_per_section': self.mesh_generator.points_per_section
            }
        }


# Convenience functions for backward compatibility
def generate_volume_mesh_from_df(df: pd.DataFrame,
                                 color_column: str,
                                 lod: str = 'high') -> Optional[Dict[str, Any]]:
    """
    Generate volume mesh from DataFrame (backward compatible).
    
    Args:
        df: DataFrame with velocity data
        color_column: Column for coloring
        lod: Level of detail
        
    Returns:
        Mesh data dictionary
    """
    plotter = VolumePlotter()
    df_prepared = plotter.prepare_data(df)
    return plotter.generate_plot_data(df_prepared, color_column, lod)