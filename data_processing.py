# --- data_processing.py ---

import base64
import io
import pandas as pd
import numpy as np

def parse_contents(contents, filename):
    """
    Parses the contents of an uploaded CSV file.

    Args:
        contents (str): The base64 encoded string of the file content.
        filename (str): The name of the uploaded file.

    Returns:
        tuple: A tuple containing (DataFrame, error_message, unit_conversion_flag).
               The DataFrame is None if an error occurs.
    """
    if not contents:
        return None, "Error: No file content found.", False

    _, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' not in filename:
            return None, "Error: Please upload a .csv file.", False

        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        df['Time'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])
        df['TimeInSeconds'] = (df['Time'] - df['Time'].min()).dt.total_seconds()

        converted_units = False
        # Check for imperial units (inches/sec) and convert to metric (mm/sec)
        df_active_check = df[df['FeedVel'] > 0]
        if not df_active_check.empty and df_active_check['FeedVel'].max() <= 100:
            converted_units = True
            cols_to_convert = ['XPos', 'YPos', 'ZPos', 'FeedVel', 'PathVel', 'XVel', 'YVel', 'ZVel']
            for col in [c for c in cols_to_convert if c in df.columns]:
                df[col] *= 25.4
        return df, None, converted_units
    except Exception as e:
        return None, f"An unexpected error occurred: {e}", False

def get_cross_section_vertices(p, v_dir, T, L, R, N=12):
    """
    Calculates the vertices of a single cross-section for the mesh.
    This defines the shape of the extruded bead at a single point.
    """
    if np.linalg.norm(v_dir) > 1e-9:
        v_dir = v_dir / np.linalg.norm(v_dir)
    else:
        # Default to a vertical direction if the direction vector is zero
        v_dir = np.array([0, 1, 0])

    z_axis = np.array([0, 0, 1])
    h_vec = np.cross(v_dir, z_axis)
    if np.linalg.norm(h_vec) < 1e-6:
        h_vec = np.array([1, 0, 0]) # Fallback for vertical toolpaths
    h_vec = h_vec / np.linalg.norm(h_vec)
    u_vec = np.cross(h_vec, v_dir)

    vertices = []
    half_N = N // 2
    # First semi-circle
    center_s1 = p - h_vec * T / 2.0
    for i in range(half_N):
        angle = np.pi/2 + (np.pi * i) / (half_N - 1)
        vertex = center_s1 + R * (np.cos(angle) * h_vec + np.sin(angle) * u_vec)
        vertices.append(vertex)
    # Second semi-circle
    center_s2 = p + h_vec * T / 2.0
    for i in range(half_N):
        angle = -np.pi/2 + (np.pi * i) / (half_N - 1)
        vertex = center_s2 + R * (np.cos(angle) * h_vec + np.sin(angle) * u_vec)
        vertices.append(vertex)

    return np.array(vertices)

def generate_volume_mesh(df_active, color_col):
    """
    Generates the vertices, faces, and color data for a 3D mesh plot.

    Args:
        df_active (pd.DataFrame): DataFrame containing only active extrusion data.
        color_col (str): The name of the column to use for the mesh's color intensity.

    Returns:
        dict: A dictionary containing 'vertices', 'faces', and 'vertex_colors'.
              Returns None if the data is insufficient for mesh generation.
    """
    if df_active.empty:
        return None

    # Check for required columns for geometry calculation
    required_cols = {'XPos', 'YPos', 'ZPos', 'FeedVel', 'PathVel'}
    if not required_cols.issubset(df_active.columns):
        missing_cols = required_cols - set(df_active.columns)
        print(f"Error: Missing required columns for mesh generation: {', '.join(missing_cols)}")
        return None

    # Constants for bead shape calculation
    L = 2.0
    R = L / 2.0
    W_Bar_mm = 0.5 * 25.4
    Area_M = W_Bar_mm**2

    # Make a copy to avoid SettingWithCopyWarning, although the calling function already does.
    df_calc = df_active.copy()

    # Calculate bead geometry based on process parameters
    df_calc['L'] = L
    df_calc['R'] = R
    df_calc['Bead_Area'] = (df_calc['FeedVel'] * Area_M) / df_calc['PathVel']
    df_calc['T'] = (df_calc['Bead_Area'] - (np.pi * R**2)) / L
    df_calc['T_clipped'] = df_calc['T'].clip(0.0, 25.4) # Clip to a reasonable max thickness

    points = df_calc[['XPos', 'YPos', 'ZPos']].values
    # No need to rename columns, just select them in the correct order for indexing.
    geometries = df_calc[['T_clipped', 'L', 'R']].values
    color_data = df_calc[color_col].values

    all_vertices, all_faces, vertex_colors = [], [], []
    vertex_offset = 0
    N_points_per_section = 12 # Number of vertices in each cross-section circle

    for i in range(len(points) - 1):
        p1, p2 = points[i], points[i+1]
        g1, g2 = geometries[i], geometries[i+1]
        v_direction = p2 - p1

        # Skip if points are identical (no direction)
        if np.linalg.norm(v_direction) < 1e-6:
            continue

        verts1 = get_cross_section_vertices(p1, v_direction, g1[0], g1[1], g1[2], N=N_points_per_section)
        verts2 = get_cross_section_vertices(p2, v_direction, g2[0], g2[1], g2[2], N=N_points_per_section)

        all_vertices.extend(verts1)
        all_vertices.extend(verts2)

        # Assign color data to the vertices
        vertex_colors.extend([color_data[i]] * N_points_per_section)
        vertex_colors.extend([color_data[i+1]] * N_points_per_section)

        # Create faces connecting the two cross-sections
        for j in range(N_points_per_section):
            v1 = vertex_offset + j
            v2 = vertex_offset + (j + 1) % N_points_per_section
            v3 = vertex_offset + N_points_per_section + j
            v4 = vertex_offset + N_points_per_section + (j + 1) % N_points_per_section
            # Create two triangles for each quad
            all_faces.append([v1, v3, v4])
            all_faces.append([v1, v4, v2])
        vertex_offset += 2 * N_points_per_section

    if not all_vertices:
        return None

    return {
        "vertices": np.array(all_vertices),
        "faces": np.array(all_faces),
        "vertex_colors": np.array(vertex_colors)
    }
