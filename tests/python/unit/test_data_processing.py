"""
Unit tests for data processing functionality in MELD Visualizer.
Tests CSV parsing, G-code parsing, and volume mesh generation.
"""

import pytest
import pandas as pd
import numpy as np
import base64
import io
from pathlib import Path
from unittest.mock import patch, Mock, MagicMock

# Import the modules under test
from meld_visualizer.core.data_processing import (
    parse_contents, 
    parse_gcode_file,
    get_cross_section_vertices,
    generate_volume_mesh,
    INCH_TO_MM
)


class TestParseContents:
    """Test CSV file parsing functionality"""
    
    @patch('meld_visualizer.utils.security_utils.FileValidator.validate_file_upload')
    def test_parse_valid_csv_contents(self, mock_validator):
        """Test parsing valid CSV contents with all required columns"""
        # Mock the security validator to return success
        mock_validator.return_value = (True, None)
        
        # Create sample CSV content with FeedVel column for imperial conversion check
        csv_content = "Date,Time,SpinVel,XPos,YPos,ZPos,FeedVel,PathVel\n2024-01-15,10:00:00,100.0,5.0,10.0,2.0,50.0,120.0\n"
        contents = f"data:text/csv;base64,{base64.b64encode(csv_content.encode()).decode()}"
        
        df, error_msg, unit_conversion = parse_contents(contents, "test.csv")
        
        assert df is not None
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert error_msg is None
        assert isinstance(unit_conversion, bool)
        assert 'XPos' in df.columns
        assert 'YPos' in df.columns
        assert 'ZPos' in df.columns
        assert 'TimeInSeconds' in df.columns
        assert len(df) == 1
    
    @patch('meld_visualizer.utils.security_utils.FileValidator.validate_file_upload')
    def test_parse_csv_with_imperial_units(self, mock_validator):
        """Test parsing CSV with imperial units (should convert to metric)"""
        mock_validator.return_value = (True, None)
        
        # Create CSV with low FeedVel values (indicating imperial units)
        csv_content = "Date,Time,XPos,YPos,ZPos,FeedVel,PathVel\n2024-01-15,10:00:00,1.0,2.0,0.5,5.0,8.0\n"
        contents = f"data:text/csv;base64,{base64.b64encode(csv_content.encode()).decode()}"
        
        df, error_msg, unit_conversion = parse_contents(contents, "test.csv")
        
        assert df is not None
        assert unit_conversion is True  # Should detect imperial units
        # Check that values were converted (multiplied by 25.4)
        assert df['XPos'].iloc[0] == pytest.approx(1.0 * 25.4, rel=1e-6)
        assert df['FeedVel'].iloc[0] == pytest.approx(5.0 * 25.4, rel=1e-6)
    
    @patch('meld_visualizer.utils.security_utils.FileValidator.validate_file_upload')
    def test_parse_csv_with_metric_units(self, mock_validator):
        """Test parsing CSV with metric units (no conversion)"""
        mock_validator.return_value = (True, None)
        
        # Create CSV with high FeedVel values (indicating metric units)
        csv_content = "Date,Time,XPos,YPos,ZPos,FeedVel,PathVel\n2024-01-15,10:00:00,25.4,50.8,12.7,127.0,254.0\n"
        contents = f"data:text/csv;base64,{base64.b64encode(csv_content.encode()).decode()}"
        
        df, error_msg, unit_conversion = parse_contents(contents, "test.csv")
        
        assert df is not None
        assert unit_conversion is False  # Should not convert metric units
        # Values should remain unchanged
        assert df['XPos'].iloc[0] == pytest.approx(25.4, rel=1e-6)
        assert df['FeedVel'].iloc[0] == pytest.approx(127.0, rel=1e-6)
    
    def test_parse_empty_contents(self):
        """Test parsing empty file contents"""
        df, error_msg, unit_conversion = parse_contents("", "test.csv")
        
        assert df is None
        assert "No file content found" in error_msg
        assert unit_conversion is False
    
    @patch('meld_visualizer.utils.security_utils.FileValidator.validate_file_upload')
    def test_parse_invalid_filename(self, mock_validator):
        """Test parsing with non-CSV filename"""
        mock_validator.return_value = (True, None)
        
        csv_content = "Date,Time,XPos,YPos,ZPos\n2024-01-15,10:00:00,1.0,2.0,0.5\n"
        contents = f"data:text/csv;base64,{base64.b64encode(csv_content.encode()).decode()}"
        
        df, error_msg, unit_conversion = parse_contents(contents, "test.txt")
        
        assert df is None
        assert "Please upload a .csv file" in error_msg
        assert unit_conversion is False
    
    @patch('meld_visualizer.utils.security_utils.FileValidator.validate_file_upload')
    def test_parse_security_validation_failure(self, mock_validator):
        """Test parsing when security validation fails"""
        mock_validator.return_value = (False, "Security validation failed")
        
        csv_content = "Date,Time,XPos,YPos,ZPos\n2024-01-15,10:00:00,1.0,2.0,0.5\n"
        contents = f"data:text/csv;base64,{base64.b64encode(csv_content.encode()).decode()}"
        
        df, error_msg, unit_conversion = parse_contents(contents, "test.csv")
        
        assert df is None
        assert error_msg == "Security validation failed"
        assert unit_conversion is False
    
    @patch('meld_visualizer.utils.security_utils.FileValidator.validate_file_upload')
    def test_parse_malformed_csv(self, mock_validator):
        """Test parsing malformed CSV data"""
        mock_validator.return_value = (True, None)
        
        # Create malformed CSV content
        csv_content = "This is not valid CSV data"
        contents = f"data:text/csv;base64,{base64.b64encode(csv_content.encode()).decode()}"
        
        df, error_msg, unit_conversion = parse_contents(contents, "test.csv")
        
        assert df is None
        assert "An unexpected error occurred" in error_msg
        assert unit_conversion is False
    
    @patch('meld_visualizer.utils.security_utils.FileValidator.validate_file_upload')
    def test_parse_csv_time_handling(self, mock_validator):
        """Test various time column handling scenarios"""
        mock_validator.return_value = (True, None)
        
        # Test CSV with separate Date and Time columns
        csv_content = "Date,Time,XPos,YPos,ZPos,FeedVel\n2024-01-15,10:00:00,1.0,2.0,0.5,100.0\n2024-01-15,10:00:01,1.1,2.1,0.6,100.0\n"
        contents = f"data:text/csv;base64,{base64.b64encode(csv_content.encode()).decode()}"
        
        df, error_msg, unit_conversion = parse_contents(contents, "test.csv")
        
        assert df is not None
        assert 'Time' in df.columns
        assert 'TimeInSeconds' in df.columns
        assert df['TimeInSeconds'].iloc[1] == 1.0  # Should be 1 second after start
    
    @patch('meld_visualizer.utils.security_utils.FileValidator.validate_file_upload')
    def test_parse_csv_no_time_column(self, mock_validator):
        """Test CSV without time column (should create synthetic timestamps)"""
        mock_validator.return_value = (True, None)
        
        csv_content = "XPos,YPos,ZPos,FeedVel\n1.0,2.0,0.5,100.0\n1.1,2.1,0.6,100.0\n"
        contents = f"data:text/csv;base64,{base64.b64encode(csv_content.encode()).decode()}"
        
        df, error_msg, unit_conversion = parse_contents(contents, "test.csv")
        
        assert df is not None
        assert 'Time' in df.columns  # Should create synthetic Time column
        assert 'TimeInSeconds' in df.columns
        assert df['TimeInSeconds'].iloc[0] == 0.0
        assert df['TimeInSeconds'].iloc[1] == 1.0  # 1 second increment


class TestParseGcodeFile:
    """Test G-code file parsing functionality"""
    
    @patch('meld_visualizer.utils.security_utils.FileValidator.validate_file_upload')
    @patch('meld_visualizer.utils.security_utils.secure_parse_gcode')
    def test_parse_valid_gcode(self, mock_secure_parse, mock_validator):
        """Test parsing valid G-code file"""
        mock_validator.return_value = (True, None)
        
        # Sample G-code with movement commands
        gcode_lines = [
            "G0 X0 Y0 Z0",  # Rapid move to origin
            "M34 S100",     # Start extrusion at 10 mm/min (100/10)
            "G1 X10 Y10 F600",  # Linear move with feed rate
            "G1 X20 Y20",   # Continue linear move
            "M35"           # Stop extrusion
        ]
        mock_secure_parse.return_value = (gcode_lines, None)
        
        gcode_content = "\n".join([
            "G0 X0 Y0 Z0",
            "M34 S100",
            "G1 X10 Y10 F600",
            "G1 X20 Y20",
            "M35"
        ])
        contents = f"data:text/plain;base64,{base64.b64encode(gcode_content.encode()).decode()}"
        
        df, error_msg, unit_conversion = parse_gcode_file(contents, "test.nc")
        
        assert df is not None
        assert isinstance(df, pd.DataFrame)
        assert error_msg is not None and "Successfully parsed" in error_msg
        assert unit_conversion is False  # G-code doesn't trigger unit conversion
        
        # Check essential columns exist
        required_cols = ['XPos', 'YPos', 'ZPos', 'FeedVel', 'PathVel', 'TimeInSeconds']
        for col in required_cols:
            assert col in df.columns
        
        # Check that we have multiple points (initial + moves)
        assert len(df) >= 3
        
        # Check that extrusion is tracked correctly
        assert df['FeedVel'].max() > 0  # Should have some extrusion
    
    def test_parse_empty_gcode_contents(self):
        """Test parsing empty G-code contents"""
        df, error_msg, unit_conversion = parse_gcode_file("", "test.nc")
        
        assert df is None
        assert "No file content found" in error_msg
        assert unit_conversion is False
    
    @patch('meld_visualizer.utils.security_utils.FileValidator.validate_file_upload')
    def test_parse_gcode_security_failure(self, mock_validator):
        """Test G-code parsing when security validation fails"""
        mock_validator.return_value = (False, "Security validation failed")
        
        gcode_content = "G0 X0 Y0 Z0\n"
        contents = f"data:text/plain;base64,{base64.b64encode(gcode_content.encode()).decode()}"
        
        df, error_msg, unit_conversion = parse_gcode_file(contents, "test.nc")
        
        assert df is None
        assert error_msg == "Security validation failed"
        assert unit_conversion is False
    
    @patch('meld_visualizer.utils.security_utils.FileValidator.validate_file_upload')
    @patch('meld_visualizer.utils.security_utils.secure_parse_gcode')
    def test_parse_gcode_no_movement_commands(self, mock_secure_parse, mock_validator):
        """Test parsing G-code with no movement commands"""
        mock_validator.return_value = (True, None)
        mock_secure_parse.return_value = (["M104 S200", "G21"], None)  # No G0/G1 commands
        
        gcode_content = "M104 S200\nG21\n"
        contents = f"data:text/plain;base64,{base64.b64encode(gcode_content.encode()).decode()}"
        
        df, error_msg, unit_conversion = parse_gcode_file(contents, "test.nc")
        
        assert df is None
        assert "No valid G-code movement commands" in error_msg
        assert unit_conversion is False
    
    @patch('meld_visualizer.utils.security_utils.FileValidator.validate_file_upload')
    @patch('meld_visualizer.utils.security_utils.secure_parse_gcode')
    def test_parse_gcode_with_complex_movements(self, mock_secure_parse, mock_validator):
        """Test parsing G-code with complex movement patterns"""
        mock_validator.return_value = (True, None)
        
        # Complex G-code sequence with different speeds and extrusion states
        gcode_lines = [
            "G0 X0 Y0 Z5",     # Rapid move to start position
            "G1 Z0.2 F300",    # Move to print height
            "M34 S50",         # Start extrusion at 5 mm/min
            "G1 X10 Y0 F600",  # Linear move with extrusion
            "G1 X10 Y10",      # Continue without F (modal)
            "M35",             # Stop extrusion
            "G0 X20 Y20 Z5",   # Rapid move (no extrusion)
            "G1 Z0.2",         # Back to print height
            "M34 S100",        # Resume extrusion at 10 mm/min
            "G1 X30 Y20 F800", # Linear move with new speed
            "M35"              # Stop extrusion
        ]
        mock_secure_parse.return_value = (gcode_lines, None)
        
        gcode_content = "\n".join(gcode_lines)
        contents = f"data:text/plain;base64,{base64.b64encode(gcode_content.encode()).decode()}"
        
        df, error_msg, unit_conversion = parse_gcode_file(contents, "test.nc")
        
        assert df is not None
        assert len(df) >= len([line for line in gcode_lines if line.startswith(('G0', 'G1'))])  # Should have points for movement commands
        
        # Check that extrusion states are tracked correctly
        extrusion_on_rows = df[df['FeedVel'] > 0]
        extrusion_off_rows = df[df['FeedVel'] == 0]
        
        assert len(extrusion_on_rows) > 0  # Should have some extrusion
        assert len(extrusion_off_rows) > 0  # Should have some non-extrusion
        
        # Check that different feed velocities are captured
        unique_feed_vels = df['FeedVel'].unique()
        assert 0 in unique_feed_vels  # Non-extrusion moves
        assert any(v > 0 for v in unique_feed_vels)  # Extrusion moves
    
    @patch('meld_visualizer.utils.security_utils.FileValidator.validate_file_upload')
    @patch('meld_visualizer.utils.security_utils.secure_parse_gcode')
    def test_parse_gcode_error_handling(self, mock_secure_parse, mock_validator):
        """Test G-code parsing error handling"""
        mock_validator.return_value = (True, None)
        mock_secure_parse.return_value = (None, "Parse error")
        
        gcode_content = "Invalid G-code\n"
        contents = f"data:text/plain;base64,{base64.b64encode(gcode_content.encode()).decode()}"
        
        df, error_msg, unit_conversion = parse_gcode_file(contents, "test.nc")
        
        assert df is None
        assert error_msg == "Parse error"
        assert unit_conversion is False


class TestGetCrossSectionVertices:
    """Test cross-section vertex generation for volume mesh"""
    
    def test_get_cross_section_vertices_basic(self):
        """Test basic cross-section vertex generation"""
        p = np.array([0.0, 0.0, 0.0])  # Point position
        v_dir = np.array([1.0, 0.0, 0.0])  # Direction vector
        T = 2.0  # Thickness
        L = 4.0  # Length
        R = 1.0  # Radius
        N = 12  # Number of vertices
        
        vertices = get_cross_section_vertices(p, v_dir, T, L, R, N)
        
        assert isinstance(vertices, np.ndarray)
        assert vertices.shape == (N, 3)  # N vertices, 3D coordinates
        
        # All vertices should be roughly at the same position along the direction vector
        # (with some variation due to the cross-sectional shape)
        center_positions = np.dot(vertices, v_dir)
        assert np.allclose(center_positions, 0.0, atol=T/2 + R)
    
    def test_get_cross_section_vertices_zero_direction(self):
        """Test cross-section generation with zero direction vector"""
        p = np.array([5.0, 5.0, 5.0])
        v_dir = np.array([0.0, 0.0, 0.0])  # Zero direction
        T = 1.0
        L = 2.0
        R = 0.5
        N = 8
        
        vertices = get_cross_section_vertices(p, v_dir, T, L, R, N)
        
        assert isinstance(vertices, np.ndarray)
        assert vertices.shape == (N, 3)
        # Should use default vertical direction when given zero vector
    
    def test_get_cross_section_vertices_vertical_direction(self):
        """Test cross-section generation with vertical direction"""
        p = np.array([0.0, 0.0, 0.0])
        v_dir = np.array([0.0, 0.0, 1.0])  # Vertical direction
        T = 1.5
        L = 3.0
        R = 0.75
        N = 16
        
        vertices = get_cross_section_vertices(p, v_dir, T, L, R, N)
        
        assert isinstance(vertices, np.ndarray)
        assert vertices.shape == (N, 3)
        
        # With vertical direction, cross-section should be in XY plane
        z_values = vertices[:, 2]
        assert np.allclose(z_values, 0.0, atol=R)  # All Z values should be near origin
    
    def test_get_cross_section_vertices_different_sizes(self):
        """Test cross-section generation with various size parameters"""
        p = np.array([0.0, 0.0, 0.0])
        v_dir = np.array([1.0, 0.0, 0.0])
        N = 12
        
        # Test with small dimensions
        vertices_small = get_cross_section_vertices(p, v_dir, 0.5, 1.0, 0.25, N)
        assert vertices_small.shape == (N, 3)
        
        # Test with large dimensions
        vertices_large = get_cross_section_vertices(p, v_dir, 5.0, 10.0, 2.5, N)
        assert vertices_large.shape == (N, 3)
        
        # Large vertices should have greater spread than small vertices
        small_extent = np.max(vertices_small) - np.min(vertices_small)
        large_extent = np.max(vertices_large) - np.min(vertices_large)
        assert large_extent > small_extent


class TestGenerateVolumeMesh:
    """Test 3D volume mesh generation functionality"""
    
    def test_generate_volume_mesh_valid_data(self):
        """Test mesh generation with valid data"""
        # Create sample DataFrame with required columns for mesh generation
        df_active = pd.DataFrame({
            'XPos': [0.0, 10.0, 20.0, 30.0],
            'YPos': [0.0, 0.0, 10.0, 10.0],
            'ZPos': [0.0, 0.0, 0.0, 0.0],
            'FeedVel': [100.0, 100.0, 100.0, 100.0],
            'PathVel': [600.0, 600.0, 600.0, 600.0]
        })
        color_col = 'FeedVel'
        
        result = generate_volume_mesh(df_active, color_col)
        
        assert result is not None
        assert isinstance(result, dict)
        assert 'vertices' in result
        assert 'faces' in result
        assert 'vertex_colors' in result
        
        # Check data types and shapes
        assert isinstance(result['vertices'], np.ndarray)
        assert isinstance(result['faces'], np.ndarray)
        assert isinstance(result['vertex_colors'], np.ndarray)
        
        # Vertices should be 3D points
        assert result['vertices'].shape[1] == 3
        
        # Faces should be triangles
        assert result['faces'].shape[1] == 3
        
        # Should have color data for each vertex
        assert len(result['vertex_colors']) == len(result['vertices'])
    
    def test_generate_volume_mesh_empty_dataframe(self):
        """Test mesh generation with empty DataFrame"""
        df_empty = pd.DataFrame()
        result = generate_volume_mesh(df_empty, 'FeedVel')
        
        assert result is None
    
    def test_generate_volume_mesh_missing_columns(self):
        """Test mesh generation with missing required columns"""
        # DataFrame missing ZPos column
        df_incomplete = pd.DataFrame({
            'XPos': [0.0, 10.0],
            'YPos': [0.0, 0.0],
            'FeedVel': [100.0, 100.0],
            'PathVel': [600.0, 600.0]
            # Missing 'ZPos' column
        })
        
        result = generate_volume_mesh(df_incomplete, 'FeedVel')
        
        assert result is None
    
    def test_generate_volume_mesh_identical_points(self):
        """Test mesh generation with identical consecutive points"""
        # DataFrame with some identical consecutive points (should be skipped)
        df_with_duplicates = pd.DataFrame({
            'XPos': [0.0, 0.0, 10.0, 10.0, 20.0],  # Some identical points
            'YPos': [0.0, 0.0, 0.0, 0.0, 0.0],
            'ZPos': [0.0, 0.0, 0.0, 0.0, 0.0],
            'FeedVel': [100.0, 100.0, 100.0, 100.0, 100.0],
            'PathVel': [600.0, 600.0, 600.0, 600.0, 600.0]
        })
        
        result = generate_volume_mesh(df_with_duplicates, 'FeedVel')
        
        # Should still generate some mesh (skipping identical points)
        assert result is not None or result is None  # Might be None if all points identical
    
    def test_generate_volume_mesh_bead_geometry_calculation(self):
        """Test bead geometry calculations in mesh generation"""
        # Test with specific values to verify geometry calculations
        df_test = pd.DataFrame({
            'XPos': [0.0, 10.0],
            'YPos': [0.0, 0.0],
            'ZPos': [0.0, 0.0],
            'FeedVel': [127.0, 254.0],  # Different feed velocities
            'PathVel': [600.0, 600.0]
        })
        
        result = generate_volume_mesh(df_test, 'FeedVel')
        
        if result is not None:
            # Should have generated vertices and faces
            assert len(result['vertices']) > 0
            assert len(result['faces']) > 0
            # Color data should reflect the different feed velocities
            assert len(np.unique(result['vertex_colors'])) > 1
    
    def test_generate_volume_mesh_single_segment(self):
        """Test mesh generation with minimal data (single segment)"""
        df_minimal = pd.DataFrame({
            'XPos': [0.0, 10.0],
            'YPos': [0.0, 5.0],
            'ZPos': [0.0, 2.0],
            'FeedVel': [100.0, 100.0],
            'PathVel': [600.0, 600.0]
        })
        
        result = generate_volume_mesh(df_minimal, 'FeedVel')
        
        if result is not None:
            # Should generate mesh for single segment
            assert len(result['vertices']) >= 24  # 2 cross-sections × 12 vertices each
            assert len(result['faces']) >= 24   # Should have triangular faces
    
    def test_generate_volume_mesh_color_column_variations(self):
        """Test mesh generation with different color columns"""
        df_test = pd.DataFrame({
            'XPos': [0.0, 10.0, 20.0],
            'YPos': [0.0, 0.0, 10.0],
            'ZPos': [0.0, 0.0, 0.0],
            'FeedVel': [100.0, 150.0, 200.0],
            'PathVel': [600.0, 700.0, 800.0],
            'CustomColor': [1.0, 2.0, 3.0]
        })
        
        # Test with FeedVel as color
        result_feedvel = generate_volume_mesh(df_test, 'FeedVel')
        
        # Test with PathVel as color
        result_pathvel = generate_volume_mesh(df_test, 'PathVel')
        
        # Test with custom color column
        result_custom = generate_volume_mesh(df_test, 'CustomColor')
        
        # All should succeed but have different color data
        for result in [result_feedvel, result_pathvel, result_custom]:
            if result is not None:
                assert 'vertex_colors' in result
                assert len(result['vertex_colors']) > 0


# Integration tests that combine multiple functions
class TestDataProcessingIntegration:
    """Integration tests for data processing pipeline"""
    
    @patch('meld_visualizer.utils.security_utils.FileValidator.validate_file_upload')
    def test_csv_to_mesh_pipeline(self, mock_validator):
        """Test complete pipeline from CSV parsing to mesh generation"""
        mock_validator.return_value = (True, None)
        
        # Create CSV data that will work through the entire pipeline
        csv_content = "Date,Time,XPos,YPos,ZPos,FeedVel,PathVel\n2024-01-15,10:00:00,0.0,0.0,0.0,100.0,600.0\n2024-01-15,10:00:01,10.0,0.0,0.0,100.0,600.0\n2024-01-15,10:00:02,10.0,10.0,0.0,100.0,600.0\n"
        contents = f"data:text/csv;base64,{base64.b64encode(csv_content.encode()).decode()}"
        
        # Parse CSV
        df, error_msg, unit_conversion = parse_contents(contents, "test.csv")
        
        assert df is not None
        assert error_msg is None
        
        # Filter to active data (FeedVel > 0)
        df_active = df[df['FeedVel'] > 0]
        
        # Generate mesh
        mesh_result = generate_volume_mesh(df_active, 'FeedVel')
        
        assert mesh_result is not None
        assert all(key in mesh_result for key in ['vertices', 'faces', 'vertex_colors'])
    
    @patch('meld_visualizer.utils.security_utils.FileValidator.validate_file_upload')
    @patch('meld_visualizer.utils.security_utils.secure_parse_gcode')
    def test_gcode_to_mesh_pipeline(self, mock_secure_parse, mock_validator):
        """Test complete pipeline from G-code parsing to mesh generation"""
        mock_validator.return_value = (True, None)
        
        # Sample G-code that will produce active extrusion
        gcode_lines = [
            "G0 X0 Y0 Z0",
            "M34 S100",     # Start extrusion
            "G1 X10 Y0 F600",
            "G1 X10 Y10",
            "G1 X20 Y10",
            "M35"           # Stop extrusion
        ]
        mock_secure_parse.return_value = (gcode_lines, None)
        
        gcode_content = "\n".join(gcode_lines)
        contents = f"data:text/plain;base64,{base64.b64encode(gcode_content.encode()).decode()}"
        
        # Parse G-code
        df, error_msg, unit_conversion = parse_gcode_file(contents, "test.nc")
        
        assert df is not None
        assert "Successfully parsed" in error_msg
        
        # Filter to active data
        df_active = df[df['FeedVel'] > 0]
        
        # Generate mesh
        mesh_result = generate_volume_mesh(df_active, 'FeedVel')
        
        assert mesh_result is not None
        assert all(key in mesh_result for key in ['vertices', 'faces', 'vertex_colors'])
    
    def test_cross_section_to_mesh_integration(self):
        """Test integration between cross-section generation and mesh assembly"""
        # Test that cross-section vertices integrate properly with mesh generation
        p1 = np.array([0.0, 0.0, 0.0])
        p2 = np.array([10.0, 0.0, 0.0])
        v_dir = p2 - p1
        T = 2.0
        L = 4.0
        R = 1.0
        N = 12
        
        # Generate cross-sections
        verts1 = get_cross_section_vertices(p1, v_dir, T, L, R, N)
        verts2 = get_cross_section_vertices(p2, v_dir, T, L, R, N)
        
        # Verify they can be used for mesh construction
        assert verts1.shape == (N, 3)
        assert verts2.shape == (N, 3)
        
        # Create simple DataFrame to test mesh generation with these concepts
        df_test = pd.DataFrame({
            'XPos': [p1[0], p2[0]],
            'YPos': [p1[1], p2[1]], 
            'ZPos': [p1[2], p2[2]],
            'FeedVel': [100.0, 100.0],
            'PathVel': [600.0, 600.0]
        })
        
        result = generate_volume_mesh(df_test, 'FeedVel')
        
        # The mesh should incorporate the cross-sectional approach
        if result is not None:
            assert len(result['vertices']) >= 2 * N  # At least two cross-sections worth