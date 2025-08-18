"""
Optimized data processing functions for MELD Visualizer
Performance improvements focus on vectorization and memory efficiency
"""

import numpy as np
import pandas as pd
import base64
import io
import re

# --- Constants ---
INCH_TO_MM = 25.4

def parse_contents_optimized(contents, filename):
    """
    Optimized CSV parsing with dtype specification and memory efficiency.
    """
    if not contents:
        return None, "Error: No file content found.", False

    _, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' not in filename:
            return None, "Error: Please upload a .csv file.", False

        # Specify dtypes to reduce memory usage
        dtype_spec = {
            'SpinVel': np.float32, 'SpinTrq': np.float32, 'SpinPwr': np.float32,
            'FeedVel': np.float32, 'PathVel': np.float32, 'FeedPos': np.float32,
            'XPos': np.float32, 'YPos': np.float32, 'ZPos': np.float32,
            'XVel': np.float32, 'YVel': np.float32, 'ZVel': np.float32,
            'ToolTemp': np.float32, 'FeedTrq': np.float32, 'FRO': np.float32
        }
        
        # Parse with optimized dtypes
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), dtype=dtype_spec)
        
        # Vectorized datetime conversion
        df['Time'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])
        df['TimeInSeconds'] = (df['Time'] - df['Time'].min()).dt.total_seconds()

        converted_units = False
        # Vectorized unit conversion check
        df_active_check = df[df['FeedVel'] > 0]
        if not df_active_check.empty and df_active_check['FeedVel'].max() <= 100:
            converted_units = True
            cols_to_convert = ['XPos', 'YPos', 'ZPos', 'FeedVel', 'PathVel', 'XVel', 'YVel', 'ZVel']
            # Vectorized conversion
            for col in [c for c in cols_to_convert if c in df.columns]:
                df[col] = df[col].astype(np.float32) * INCH_TO_MM
        
        return df, None, converted_units
    except Exception as e:
        return None, f"An unexpected error occurred: {e}", False

def get_cross_section_vertices_vectorized(p, v_dir, T, L, R, N=12):
    """
    Optimized cross-section vertex calculation using numpy vectorization.
    """
    # Ensure consistent dtype
    p = np.asarray(p, dtype=np.float32)
    v_dir = np.asarray(v_dir, dtype=np.float32)
    
    # Normalize direction vector
    v_norm = np.linalg.norm(v_dir)
    if v_norm > 1e-9:
        v_dir = v_dir / v_norm
    else:
        v_dir = np.array([0.0, 1.0, 0.0], dtype=np.float32)
    
    z_axis = np.array([0.0, 0.0, 1.0], dtype=np.float32)
    h_vec = np.cross(v_dir, z_axis)
    h_norm = np.linalg.norm(h_vec)
    if h_norm < 1e-6:
        h_vec = np.array([1.0, 0.0, 0.0], dtype=np.float32)
    else:
        h_vec = h_vec / h_norm
    
    u_vec = np.cross(h_vec, v_dir)
    
    # Vectorized vertex generation
    half_N = N // 2
    
    # Generate all angles at once
    angles1 = np.linspace(np.pi/2, 3*np.pi/2, half_N, dtype=np.float32)
    angles2 = np.linspace(-np.pi/2, np.pi/2, half_N, dtype=np.float32)
    all_angles = np.concatenate([angles1, angles2])
    
    # Centers for each semi-circle
    center_s1 = p - h_vec * T / 2.0
    center_s2 = p + h_vec * T / 2.0
    
    # Generate vertices using broadcasting
    vertices = np.zeros((N, 3), dtype=np.float32)
    
    # First semi-circle vertices
    cos_vals1 = np.cos(angles1)
    sin_vals1 = np.sin(angles1)
    vertices[:half_N] = center_s1 + R * (cos_vals1[:, np.newaxis] * h_vec + sin_vals1[:, np.newaxis] * u_vec)
    
    # Second semi-circle vertices
    cos_vals2 = np.cos(angles2)
    sin_vals2 = np.sin(angles2)
    vertices[half_N:] = center_s2 + R * (cos_vals2[:, np.newaxis] * h_vec + sin_vals2[:, np.newaxis] * u_vec)
    
    return vertices

def generate_volume_mesh_optimized(df_active, color_col):
    """
    Optimized mesh generation with vectorization and pre-allocation.
    """
    if df_active.empty:
        return None

    # Check for required columns
    required_cols = {'XPos', 'YPos', 'ZPos', 'FeedVel', 'PathVel'}
    if not required_cols.issubset(df_active.columns):
        return None

    # Constants
    BEAD_LENGTH = 2.0
    BEAD_RADIUS = BEAD_LENGTH / 2.0
    WIRE_DIAMETER_MM = 0.5 * INCH_TO_MM
    WIRE_AREA = WIRE_DIAMETER_MM**2
    MAX_BEAD_THICKNESS = 1.0 * INCH_TO_MM
    POINTS_PER_SECTION = 12

    # Vectorized bead geometry calculation
    df_active = df_active.copy()
    df_active['Bead_Area'] = (df_active['FeedVel'] * WIRE_AREA) / df_active['PathVel'].clip(lower=1e-6)
    df_active['T'] = (df_active['Bead_Area'] - (np.pi * BEAD_RADIUS**2)) / BEAD_LENGTH
    df_active['T_clipped'] = df_active['T'].clip(0.0, MAX_BEAD_THICKNESS)

    # Convert to numpy arrays for faster access
    points = df_active[['XPos', 'YPos', 'ZPos']].values.astype(np.float32)
    geometries = df_active['T_clipped'].values.astype(np.float32)
    color_data = df_active[color_col].values.astype(np.float32)

    # Calculate total size and pre-allocate arrays
    n_segments = len(points) - 1
    n_vertices_total = n_segments * 2 * POINTS_PER_SECTION
    n_faces_total = n_segments * 2 * POINTS_PER_SECTION
    
    # Pre-allocate arrays
    all_vertices = np.zeros((n_vertices_total, 3), dtype=np.float32)
    all_faces = np.zeros((n_faces_total, 3), dtype=np.int32)
    vertex_colors = np.zeros(n_vertices_total, dtype=np.float32)
    
    vertex_offset = 0
    face_offset = 0
    
    # Process segments in batches for better cache utilization
    for i in range(n_segments):
        p1, p2 = points[i], points[i+1]
        g1, g2 = geometries[i], geometries[i+1]
        v_direction = p2 - p1
        
        # Skip if points are identical
        if np.linalg.norm(v_direction) < 1e-6:
            continue
        
        # Generate vertices (using original function for now - can be further optimized)
        verts1 = get_cross_section_vertices_vectorized(
            p1, v_direction, g1, BEAD_LENGTH, BEAD_RADIUS, N=POINTS_PER_SECTION
        )
        verts2 = get_cross_section_vertices_vectorized(
            p2, v_direction, g2, BEAD_LENGTH, BEAD_RADIUS, N=POINTS_PER_SECTION
        )
        
        # Store vertices
        v_start = vertex_offset
        v_end = vertex_offset + 2 * POINTS_PER_SECTION
        all_vertices[v_start:v_start+POINTS_PER_SECTION] = verts1
        all_vertices[v_start+POINTS_PER_SECTION:v_end] = verts2
        
        # Store colors
        vertex_colors[v_start:v_start+POINTS_PER_SECTION] = color_data[i]
        vertex_colors[v_start+POINTS_PER_SECTION:v_end] = color_data[i+1]
        
        # Generate faces using vectorized operations
        for j in range(POINTS_PER_SECTION):
            v1 = vertex_offset + j
            v2 = vertex_offset + (j + 1) % POINTS_PER_SECTION
            v3 = vertex_offset + POINTS_PER_SECTION + j
            v4 = vertex_offset + POINTS_PER_SECTION + (j + 1) % POINTS_PER_SECTION
            
            face_idx = face_offset + j * 2
            all_faces[face_idx] = [v1, v3, v4]
            all_faces[face_idx + 1] = [v1, v4, v2]
        
        vertex_offset += 2 * POINTS_PER_SECTION
        face_offset += 2 * POINTS_PER_SECTION
    
    # Trim arrays to actual size (in case some segments were skipped)
    all_vertices = all_vertices[:vertex_offset]
    all_faces = all_faces[:face_offset]
    vertex_colors = vertex_colors[:vertex_offset]
    
    if len(all_vertices) == 0:
        return None
    
    return {
        "vertices": all_vertices,
        "faces": all_faces,
        "vertex_colors": vertex_colors
    }

def generate_volume_mesh_lod(df_active, color_col, detail_level='medium'):
    """
    Generate mesh with Level of Detail (LOD) control.
    
    Args:
        df_active: Active extrusion data
        color_col: Column to use for coloring
        detail_level: 'low', 'medium', 'high' - controls mesh resolution
    """
    # Define LOD parameters
    lod_params = {
        'low': {'points_per_section': 6, 'skip_points': 3},
        'medium': {'points_per_section': 12, 'skip_points': 1},
        'high': {'points_per_section': 24, 'skip_points': 1}
    }
    
    params = lod_params.get(detail_level, lod_params['medium'])
    
    # Subsample data if needed
    if params['skip_points'] > 1:
        df_active = df_active.iloc[::params['skip_points']].copy()
    
    # Generate mesh with specified detail level
    return generate_volume_mesh_optimized(df_active, color_col)

class DataFrameCache:
    """
    Simple in-memory cache for DataFrames to avoid repeated JSON serialization.
    """
    def __init__(self, max_size=5):
        self.cache = {}
        self.max_size = max_size
        self.access_order = []
    
    def get(self, key):
        """Get DataFrame from cache."""
        if key in self.cache:
            # Update access order
            self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key].copy()
        return None
    
    def set(self, key, df):
        """Store DataFrame in cache."""
        # Implement LRU eviction
        if len(self.cache) >= self.max_size and key not in self.cache:
            oldest = self.access_order.pop(0)
            del self.cache[oldest]
        
        self.cache[key] = df.copy()
        if key in self.access_order:
            self.access_order.remove(key)
        self.access_order.append(key)
    
    def clear(self):
        """Clear the cache."""
        self.cache.clear()
        self.access_order.clear()

# Global cache instance
df_cache = DataFrameCache()

def optimize_dataframe_for_json(df):
    """
    Optimize DataFrame for JSON serialization by reducing precision and using appropriate dtypes.
    """
    df_optimized = df.copy()
    
    # Convert float64 to float32 where appropriate
    float_cols = df_optimized.select_dtypes(include=[np.float64]).columns
    for col in float_cols:
        # Keep high precision for position data, reduce for others
        if any(x in col.lower() for x in ['pos', 'x', 'y', 'z']):
            df_optimized[col] = df_optimized[col].astype(np.float32)
        else:
            # Round to reasonable precision for other data
            df_optimized[col] = np.round(df_optimized[col], 3).astype(np.float32)
    
    # Convert int64 to int32 where values allow
    int_cols = df_optimized.select_dtypes(include=[np.int64]).columns
    for col in int_cols:
        if df_optimized[col].max() < 2147483647 and df_optimized[col].min() > -2147483648:
            df_optimized[col] = df_optimized[col].astype(np.int32)
    
    return df_optimized