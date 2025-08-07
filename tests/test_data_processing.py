import pytest
import pandas as pd
import numpy as np
import base64
import os
import sys

# Add the root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data_processing import parse_contents, get_cross_section_vertices, generate_volume_mesh

# --- Fixtures ---

@pytest.fixture
def sample_csv_content():
    """Reads a sample CSV file and returns its base64 encoded content."""
    with open('CSV/20250707144618.csv', 'rb') as f:
        content_bytes = f.read()
    encoded = base64.b64encode(content_bytes)
    return f"data:text/csv;base64,{encoded.decode('utf-8')}"

@pytest.fixture
def sample_malformed_csv_content():
    """Returns a malformed base64 encoded CSV string."""
    content = "header1,header2\nvalue1,value2\nvalue3" # Missing a value
    encoded = base64.b64encode(content.encode('utf-8'))
    return f"data:text/csv;base64,{encoded.decode('utf-8')}"

@pytest.fixture
def active_extrusion_df():
    """Creates a sample DataFrame with active extrusion data for mesh generation tests."""
    data = {
        'XPos': [0, 1, 2, 3],
        'YPos': [0, 0, 0, 0],
        'ZPos': [0, 0, 0, 0],
        'FeedVel': [10, 10, 10, 10],
        'PathVel': [5, 5, 5, 5],
        'ToolTemp': [200, 205, 210, 215]
    }
    return pd.DataFrame(data)

# --- Test Cases for parse_contents ---

def test_parse_contents_success(sample_csv_content):
    """
    Tests successful parsing of a valid CSV file.
    """
    df, error_message, converted = parse_contents(sample_csv_content, "sample.csv")
    assert error_message is None
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert 'TimeInSeconds' in df.columns
    assert pd.api.types.is_numeric_dtype(df['TimeInSeconds'])
    # This specific file should trigger the unit conversion
    assert converted is True
    # Check if a known column was converted (original max is ~1, should now be ~25.4)
    assert df['ZPos'].max() > 20

def test_parse_contents_wrong_file_type():
    """
    Tests that a non-CSV file returns an error.
    """
    # The content needs to be a valid base64-like string for the split to work
    content = "c29tZV9jb250ZW50" # "some_content" base64 encoded
    b64_string = f"data:text/plain;base64,{content}"
    df, error_message, converted = parse_contents(b64_string, "sample.txt")
    assert df is None
    assert "Please upload a .csv file" in error_message
    assert converted is False

def test_parse_contents_malformed_csv(sample_malformed_csv_content):
    """
    Tests that a malformed CSV raises an error.
    """
    df, error_message, converted = parse_contents(sample_malformed_csv_content, "malformed.csv")
    assert df is None
    assert "An unexpected error occurred" in error_message
    assert converted is False

def test_parse_contents_empty_content():
    """
    Tests that empty content returns an error.
    """
    df, error_message, converted = parse_contents(None, "empty.csv")
    assert df is None
    assert "No file content found" in error_message
    assert converted is False

# --- Test Cases for get_cross_section_vertices ---

def test_get_cross_section_vertices_returns_correct_shape():
    """
    Tests that the function returns a NumPy array of the correct shape.
    """
    p = np.array([0, 0, 0])
    v_dir = np.array([0, 1, 0])
    T, L, R = 10, 2, 1
    vertices = get_cross_section_vertices(p, v_dir, T, L, R, N=12)
    assert isinstance(vertices, np.ndarray)
    assert vertices.shape == (12, 3)

def test_get_cross_section_vertices_simple_case():
    """
    Tests the vertex positions for a simple, easily verifiable case.
    Direction is along Y, so the cross-section should be in the X-Z plane.
    """
    p = np.array([0, 0, 0])
    v_dir = np.array([0, 1, 0]) # Direction along Y
    T, L, R = 10, 2, 1
    # With v_dir along Y, h_vec should be along X, and u_vec should be along Z.
    vertices = get_cross_section_vertices(p, v_dir, T, L, R, N=12)
    # Check that the y-coordinates of all vertices are close to 0
    assert np.allclose(vertices[:, 1], 0)
    # Check that x and z coordinates are not all zero
    assert not np.allclose(vertices[:, 0], 0)
    assert not np.allclose(vertices[:, 2], 0)

# --- Test Cases for generate_volume_mesh ---

def test_generate_volume_mesh_success(active_extrusion_df):
    """
    Tests successful mesh generation from a valid active extrusion DataFrame.
    """
    mesh_data = generate_volume_mesh(active_extrusion_df, 'ToolTemp')
    assert mesh_data is not None
    assert 'vertices' in mesh_data
    assert 'faces' in mesh_data
    assert 'vertex_colors' in mesh_data
    assert isinstance(mesh_data['vertices'], np.ndarray)
    assert isinstance(mesh_data['faces'], np.ndarray)
    assert isinstance(mesh_data['vertex_colors'], np.ndarray)
    assert mesh_data['vertices'].shape[1] == 3
    assert mesh_data['faces'].shape[1] == 3
    assert len(mesh_data['vertex_colors']) > 0

def test_generate_volume_mesh_empty_df():
    """
    Tests that the function handles an empty DataFrame gracefully.
    """
    empty_df = pd.DataFrame()
    mesh_data = generate_volume_mesh(empty_df, 'ToolTemp')
    assert mesh_data is None

def test_generate_volume_mesh_no_movement():
    """
    Tests that mesh generation is skipped if points are identical (no movement).
    """
    data = {
        'XPos': [1, 1, 1], 'YPos': [1, 1, 1], 'ZPos': [1, 1, 1],
        'FeedVel': [10, 10, 10], 'PathVel': [5, 5, 5], 'ToolTemp': [200, 205, 210]
    }
    df = pd.DataFrame(data)
    mesh_data = generate_volume_mesh(df, 'ToolTemp')
    assert mesh_data is None
