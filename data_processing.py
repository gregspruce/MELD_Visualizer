# --- data_processing.py ---

import base64
import io
import pandas as pd
import numpy as np

# --- Constants ---
# A set of columns that are expected to be in inches and need conversion to mm.
IMPERIAL_COLUMNS_TO_CONVERT = {'XPos', 'YPos', 'ZPos', 'FeedVel', 'PathVel', 'XVel', 'YVel', 'ZVel'}
INCH_TO_MM = 25.4

# --- Functions ---
def parse_contents(contents, filename):
    """
    Parses the contents of an uploaded CSV file, handling base64 decoding,
    unit conversion, and time calculations.

    Args:
        contents (str): The base64 encoded string of the file content from a dcc.Upload component.
        filename (str): The name of the uploaded file.

    Returns:
        tuple: A tuple containing (pd.DataFrame, str, bool) representing the
               parsed data, an error message (or None), and a flag indicating
               if unit conversion was performed.
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
        # Heuristic to detect if the data is in imperial units (inches) vs. metric (mm).
        # If the max feed velocity is a small number (e.g., <= 100), it's likely inches/sec.
        df_active_check = df[df['FeedVel'] > 0]
        if not df_active_check.empty and df_active_check['FeedVel'].max() <= 100:
            converted_units = True
            for col in IMPERIAL_COLUMNS_TO_CONVERT:
                if col in df.columns:
                    df[col] *= INCH_TO_MM
        return df, None, converted_units
    except Exception as e:
        return None, f"An unexpected error occurred while parsing the CSV: {e}", False

def get_cross_section_vertices(p, v_dir, T, L, R, N=12):
    """
    Calculates the vertices of a single cross-section for the mesh.
    This defines the shape of the extruded bead at a single point, which is
    modeled as a rectangle with a semi-circle at each end.

    Args:
        p (np.array): The center point of the cross-section.
        v_dir (np.array): The direction vector of the toolpath.
        T (float): The thickness of the bead (height of the rectangular part).
        L (float): The length of the rectangular part of the bead.
        R (float): The radius of the semi-circular ends of the bead.
        N (int): The number of vertices to generate for the cross-section.

    Returns:
        np.array: A NumPy array of shape (N, 3) containing the vertex coordinates.
    """
    if np.linalg.norm(v_dir) > 1e-9:
        v_dir = v_dir / np.linalg.norm(v_dir)
    else:
        # Default to a safe direction if the direction vector is zero
        v_dir = np.array([0, 1, 0])

    # Define the plane of the cross-section using two orthogonal vectors.
    # h_vec is the horizontal vector in the XY plane, perpendicular to the direction.
    z_axis = np.array([0, 0, 1])
    h_vec = np.cross(v_dir, z_axis)
    if np.linalg.norm(h_vec) < 1e-6:
        h_vec = np.array([1, 0, 0]) # Fallback for purely vertical toolpaths
    h_vec = h_vec / np.linalg.norm(h_vec)
    # u_vec is the "up" vector, perpendicular to both direction and horizontal.
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
    if df_active.empty or len(df_active) < 2:
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

    for i in range(len(points) - 1):
        # Get data for the start and end of the segment
        p1, p2 = points[i], points[i+1]
        g1, g2 = geometries[i], geometries[i+1]
        v_direction = p2 - p1

        # Skip segment if the points are identical (no direction/movement)
        if np.linalg.norm(v_direction) < 1e-6:
            continue

        # Generate the vertices for the cross-sections at the start and end of the segment
        verts1 = get_cross_section_vertices(p1, v_direction, g1[0], BEAD_LENGTH, BEAD_RADIUS, N=POINTS_PER_SECTION)
        verts2 = get_cross_section_vertices(p2, v_direction, g2[0], BEAD_LENGTH, BEAD_RADIUS, N=POINTS_PER_SECTION)
        all_vertices.extend(verts1)
        all_vertices.extend(verts2)

        # Assign color data to the newly created vertices
        vertex_colors.extend([color_data[i]] * POINTS_PER_SECTION)
        vertex_colors.extend([color_data[i+1]] * POINTS_PER_SECTION)

        # Create the triangular faces connecting the two cross-sections
        for j in range(POINTS_PER_SECTION):
            v1 = vertex_offset + j
            v2 = vertex_offset + (j + 1) % POINTS_PER_SECTION
            v3 = vertex_offset + POINTS_PER_SECTION + j
            v4 = vertex_offset + POINTS_PER_SECTION + (j + 1) % POINTS_PER_SECTION
            # Create two triangles to form a quad between the vertices
            all_faces.append([v1, v3, v4])
            all_faces.append([v1, v4, v2])

        # Increment the offset for the next set of vertices
        vertex_offset += 2 * POINTS_PER_SECTION

    if not all_vertices:
        return None

    return {
        "vertices": np.array(all_vertices),
        "faces": np.array(all_faces),
        "vertex_colors": np.array(vertex_colors)
    }
