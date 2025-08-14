# --- data_processing.py ---

import base64
import io
import re  # <-- Added import for regular expressions
import pandas as pd
import numpy as np

# --- Constants ---
INCH_TO_MM = 25.4

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

def parse_gcode_file(contents, filename):
    """
    Parses the contents of an uploaded G-code (.nc) file and simulates the toolpath.
    This creates a DataFrame compatible with the existing plotting functions.

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
        gcode_text = decoded.decode('utf-8')
        lines = io.StringIO(gcode_text).readlines()
    except Exception as e:
        return None, f"An error occurred while decoding the file: {e}", False

    # Regex to find G-code words (e.g., G1, X10.5, S4200)
    gcode_word_re = re.compile(r'([A-Z])([-+]?\d*\.?\d+)')

    # Machine state
    state = {
        'current_pos': {'X': 0.0, 'Y': 0.0, 'Z': 0.0},
        'feed_vel': 0.0,      # Material feed velocity (from M34 S...)
        'path_vel': 0.0,      # Tool head velocity (from G1 F...)
        'extrusion_on': False,
        'time_counter': 0.0,
        'gcode_mode': 0,      # 0 for G0 (rapid), 1 for G1 (linear feed)
    }
    path_points = []
    
    # Add an initial point at the origin to start the path
    initial_point = {
        'XPos': state['current_pos']['X'], 'YPos': state['current_pos']['Y'], 'ZPos': state['current_pos']['Z'],
        'FeedVel': 0, 'PathVel': 0, 'TimeInSeconds': 0,
    }
    path_points.append(initial_point)

    try:
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            # Strip comments and ignore empty lines/metadata
            if '(' in line:
                line = line[:line.find('(')].strip()
            if not line or line.startswith('%'):
                continue

            words = dict(gcode_word_re.findall(line.upper()))
            
            # Handle state-changing M-Codes and G-Codes
            if 'M' in words:
                m_code = int(float(words['M']))
                if m_code == 34:
                    state['extrusion_on'] = True
                    if 'S' in words:
                        # Per documentation: S value is mm/min x 10
                        state['feed_vel'] = float(words['S']) / 10.0
                elif m_code == 35:
                    state['extrusion_on'] = False

            if 'G' in words:
                g_code = int(float(words['G']))
                if g_code in [0, 1]:
                    state['gcode_mode'] = g_code
                    
                    # This is a movement command, so we generate a new point in the path
                    target_pos = state['current_pos'].copy()
                    
                    # Update target position based on modal X, Y, Z, and F values
                    if 'X' in words: target_pos['X'] = float(words['X'])
                    if 'Y' in words: target_pos['Y'] = float(words['Y'])
                    if 'Z' in words: target_pos['Z'] = float(words['Z'])
                    if 'F' in words: state['path_vel'] = float(words['F'])

                    p1 = np.array(list(state['current_pos'].values()))
                    p2 = np.array(list(target_pos.values()))
                    distance = np.linalg.norm(p2 - p1)

                    time_segment_seconds = 0
                    if distance > 1e-9 and state['path_vel'] > 1e-9:
                        # F is in mm/min, so we convert segment time to seconds
                        time_segment_seconds = (distance / state['path_vel']) * 60.0
                    state['time_counter'] += time_segment_seconds

                    # Extrusion only occurs during G1 moves
                    current_feed = state['feed_vel'] if state['extrusion_on'] and state['gcode_mode'] == 1 else 0

                    # Create the new data point for our DataFrame
                    new_point = {
                        'XPos': target_pos['X'],
                        'YPos': target_pos['Y'],
                        'ZPos': target_pos['Z'],
                        'FeedVel': current_feed,
                        'PathVel': state['path_vel'],
                        'TimeInSeconds': state['time_counter']
                    }
                    path_points.append(new_point)

                    # Update the machine's current position for the next iteration
                    state['current_pos'] = target_pos

    except Exception as e:
        return None, f"An error occurred while parsing G-code on line {line_num}: {e}", False

    if len(path_points) <= 1:
        return None, "Error: No valid G-code movement commands (G0/G1) were found.", False

    df = pd.DataFrame(path_points)
    
    # Add synthetic Date/Time columns for compatibility with the 2D time plotter
    start_time = pd.to_datetime('2025-01-01T00:00:00')
    df['Time'] = df['TimeInSeconds'].apply(lambda s: start_time + pd.to_timedelta(s, unit='s'))
    df['Date'] = df['Time'].dt.strftime('%Y-%m-%d')
    
    # Add placeholder columns that exist in the CSV but not G-code, for compatibility
    for col in ['SpinVel', 'ToolTemp', 'SpinTrq', 'SpinPwr', 'FeedTrq', 'FRO']:
        if col not in df.columns:
            df[col] = 0

    return df, f"Successfully parsed G-code file: {filename}", False


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

    # --- Bead Geometry Constants ---
    # These values define the physical properties of the extrusion material.
    BEAD_LENGTH = 2.0  # Length of the rectangular part of the bead cross-section (mm)
    BEAD_RADIUS = BEAD_LENGTH / 2.0 # Radius of the semi-circular ends (mm)
    WIRE_DIAMETER_MM = 0.5 * INCH_TO_MM # Diameter of the feedstock wire (mm)
    WIRE_AREA = WIRE_DIAMETER_MM**2 # Area of the feedstock wire (mm^2)
    MAX_BEAD_THICKNESS = 1.0 * INCH_TO_MM # Safety clip for bead thickness (mm)
    POINTS_PER_SECTION = 12 # Number of vertices in each cross-section circle

    # --- Bead Geometry Calculation ---
    # This section calculates the cross-sectional geometry of the bead at each point
    # based on the principle of conservation of mass (volume in = volume out).
    # Bead Area = (Feed Velocity * Wire Area) / Path Velocity
    df_active = df_active.copy()
    df_active['Bead_Area'] = (df_active['FeedVel'] * WIRE_AREA) / df_active['PathVel']
    # The thickness T is derived from the area of the idealized bead shape (rectangle + circle)
    df_active['T'] = (df_active['Bead_Area'] - (np.pi * BEAD_RADIUS**2)) / BEAD_LENGTH
    df_active['T_clipped'] = df_active['T'].clip(0.0, MAX_BEAD_THICKNESS)

    # --- Vertex and Face Generation ---
    points = df_active[['XPos', 'YPos', 'ZPos']].values
    geometries = df_active[['T_clipped']].rename(columns={'T_clipped': 'T'}).values
    color_data = df_active[color_col].values

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

        # Generate the vertices for the cross-sections at the start and end of the segment
        verts1 = get_cross_section_vertices(p1, v_direction, g1[0], BEAD_LENGTH, BEAD_RADIUS, N=POINTS_PER_SECTION)
        verts2 = get_cross_section_vertices(p2, v_direction, g2[0], BEAD_LENGTH, BEAD_RADIUS, N=POINTS_PER_SECTION)

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