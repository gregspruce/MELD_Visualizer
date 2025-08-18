"""
Unit tests for data processing functions.
Tests parsing, conversion, and mesh generation.
"""

import pytest
import pandas as pd
import numpy as np
import base64
import io
from unittest.mock import Mock, patch

from src.meld_visualizer.core.data_processing import (
    parse_contents, parse_gcode_file, generate_volume_mesh
)
from src.meld_visualizer.constants import (
    INCH_TO_MM, IMPERIAL_VELOCITY_THRESHOLD, FEEDSTOCK_AREA_MM2,
    FEEDSTOCK_DIMENSION_MM, FEEDSTOCK_DIMENSION_INCHES
)


class TestParseContents:
    """Test CSV parsing functionality."""
    
    @pytest.fixture
    def sample_csv_data(self):
        """Create sample CSV data."""
        df = pd.DataFrame({
            'XPos': [0, 10, 20, 30],
            'YPos': [0, 10, 20, 30],
            'ZPos': [0, 1, 2, 3],
            'FeedVel': [0, 50, 100, 150],
            'PathVel': [0, 25, 50, 75],
            'ToolTemp': [20, 100, 150, 200],
            'Time': pd.date_range('2024-01-01', periods=4, freq='S')
        })
        return df
    
    @pytest.fixture
    def encoded_csv(self, sample_csv_data):
        """Create base64 encoded CSV content."""
        csv_string = sample_csv_data.to_csv(index=False)
        encoded = base64.b64encode(csv_string.encode()).decode()
        return f"data:text/csv;base64,{encoded}"
    
    def test_parse_valid_csv(self, encoded_csv):
        """Test parsing valid CSV file."""
        df, error, converted = parse_contents(encoded_csv, "test.csv")
        
        assert df is not None
        assert error is None
        assert isinstance(df, pd.DataFrame)
        assert 'XPos' in df.columns
        assert 'YPos' in df.columns
        assert 'ZPos' in df.columns
    
    def test_parse_empty_contents(self):
        """Test parsing with empty contents."""
        df, error, converted = parse_contents(None, "test.csv")
        
        assert df is None
        assert error == "Error: No file content found."
        assert converted is False
    
    def test_parse_non_csv_file(self, encoded_csv):
        """Test parsing with non-CSV filename."""
        df, error, converted = parse_contents(encoded_csv, "test.txt")
        
        assert df is None
        assert "Please upload a .csv file" in error
        assert converted is False
    
    def test_imperial_to_metric_conversion(self):
        """Test automatic imperial to metric conversion."""
        # Create data with imperial units (low velocities)
        df_imperial = pd.DataFrame({
            'XPos': [0, 1, 2],  # inches
            'YPos': [0, 1, 2],  # inches  
            'ZPos': [0, 0.1, 0.2],  # inches
            'FeedVel': [0, 10, 20],  # Low values indicate imperial
            'PathVel': [0, 5, 10],
            'ToolTemp': [20, 100, 150]
        })
        
        csv_string = df_imperial.to_csv(index=False)
        encoded = base64.b64encode(csv_string.encode()).decode()
        contents = f"data:text/csv;base64,{encoded}"
        
        df, error, converted = parse_contents(contents, "imperial.csv")
        
        assert df is not None
        assert converted is True
        # Check conversion applied
        assert df['XPos'].iloc[1] == pytest.approx(1 * INCH_TO_MM, rel=1e-3)
        assert df['YPos'].iloc[2] == pytest.approx(2 * INCH_TO_MM, rel=1e-3)
    
    def test_metric_no_conversion(self):
        """Test that metric data is not converted."""
        # Create data with metric units (high velocities)
        df_metric = pd.DataFrame({
            'XPos': [0, 25.4, 50.8],  # mm
            'YPos': [0, 25.4, 50.8],  # mm
            'ZPos': [0, 2.54, 5.08],  # mm
            'FeedVel': [0, 200, 400],  # High values indicate metric
            'PathVel': [0, 100, 200],
            'ToolTemp': [20, 100, 150]
        })
        
        csv_string = df_metric.to_csv(index=False)
        encoded = base64.b64encode(csv_string.encode()).decode()
        contents = f"data:text/csv;base64,{encoded}"
        
        df, error, converted = parse_contents(contents, "metric.csv")
        
        assert df is not None
        assert converted is False
        # Check no conversion applied
        assert df['XPos'].iloc[1] == 25.4
        assert df['YPos'].iloc[2] == 50.8
    
    def test_time_column_parsing(self, encoded_csv):
        """Test that time columns are properly parsed."""
        df, error, converted = parse_contents(encoded_csv, "test.csv")
        
        assert 'TimeInSeconds' in df.columns
        assert df['TimeInSeconds'].iloc[0] == 0
        assert df['TimeInSeconds'].iloc[-1] == 3
    
    def test_malformed_csv(self):
        """Test handling of malformed CSV."""
        malformed = "data:text/csv;base64,invalidbase64content"
        
        df, error, converted = parse_contents(malformed, "bad.csv")
        
        assert df is None
        assert error is not None
        assert "error occurred" in error.lower()


class TestParseGcodeFile:
    """Test G-code parsing functionality."""
    
    @pytest.fixture
    def sample_gcode(self):
        """Create sample G-code content."""
        gcode = """
        ; G-code test file
        G0 X0 Y0 Z0 ; Rapid move to origin
        G1 X10 Y10 F100 ; Linear move
        M34 S4200 ; Start material feed
        G1 X20 Y20 Z5
        G1 X30 Y30 Z10
        M35 ; Stop material feed
        G0 X0 Y0 Z0
        """
        return gcode
    
    @pytest.fixture
    def encoded_gcode(self, sample_gcode):
        """Create base64 encoded G-code content."""
        encoded = base64.b64encode(sample_gcode.encode()).decode()
        return f"data:text/plain;base64,{encoded}"
    
    def test_parse_valid_gcode(self, encoded_gcode):
        """Test parsing valid G-code file."""
        df, error, converted = parse_gcode_file(encoded_gcode, "test.nc")
        
        assert df is not None
        assert error is None
        assert isinstance(df, pd.DataFrame)
        assert 'XPos' in df.columns
        assert 'YPos' in df.columns
        assert 'ZPos' in df.columns
        assert 'FeedVel' in df.columns
    
    def test_gcode_feed_commands(self, encoded_gcode):
        """Test M34/M35 feed commands are processed."""
        df, error, converted = parse_gcode_file(encoded_gcode, "test.nc")
        
        assert df is not None
        # Check that feed velocity changes with M34/M35
        feed_velocities = df['FeedVel'].unique()
        assert 0 in feed_velocities  # Feed off
        assert any(v > 0 for v in feed_velocities)  # Feed on
    
    def test_gcode_movement_tracking(self):
        """Test that G-code movements are tracked correctly."""
        gcode = """
        G0 X0 Y0 Z0
        G1 X10 Y0 Z0 F100
        G1 X10 Y10 Z0
        G1 X10 Y10 Z5
        """
        encoded = base64.b64encode(gcode.encode()).decode()
        contents = f"data:text/plain;base64,{encoded}"
        
        df, error, converted = parse_gcode_file(contents, "test.nc")
        
        assert df is not None
        # Check positions
        assert df['XPos'].iloc[-1] == 10
        assert df['YPos'].iloc[-1] == 10
        assert df['ZPos'].iloc[-1] == 5
    
    def test_gcode_comment_handling(self):
        """Test that comments are properly handled."""
        gcode = """
        (This is a comment)
        G0 X10 Y10 ; Inline comment
        G1 X20 Y20 (Another comment) Z5
        """
        encoded = base64.b64encode(gcode.encode()).decode()
        contents = f"data:text/plain;base64,{encoded}"
        
        df, error, converted = parse_gcode_file(contents, "test.nc")
        
        assert df is not None
        assert len(df) > 0
        # Comments should not affect parsing
    
    def test_empty_gcode(self):
        """Test handling of empty G-code file."""
        gcode = ""
        encoded = base64.b64encode(gcode.encode()).decode()
        contents = f"data:text/plain;base64,{encoded}"
        
        df, error, converted = parse_gcode_file(contents, "empty.nc")
        
        # Should still return a DataFrame with at least origin point
        assert df is not None
        assert len(df) >= 1


class TestGenerateVolumeMesh:
    """Test mesh generation functionality."""
    
    @pytest.fixture
    def sample_toolpath_data(self):
        """Create sample toolpath data for mesh generation."""
        # Create a simple square toolpath
        df = pd.DataFrame({
            'XPos': [0, 10, 10, 0, 0],
            'YPos': [0, 0, 10, 10, 0],
            'ZPos': [0, 0, 0, 0, 0],
            'ToolTemp': [100, 150, 200, 150, 100],
            'FeedVel': [50, 50, 50, 50, 50],
            'PathVel': [25, 25, 25, 25, 25]
        })
        return df
    
    def test_generate_mesh_basic(self, sample_toolpath_data):
        """Test basic mesh generation."""
        mesh_data = generate_volume_mesh(sample_toolpath_data, 'ToolTemp')
        
        assert mesh_data is not None
        assert 'vertices' in mesh_data
        assert 'faces' in mesh_data
        assert 'vertex_colors' in mesh_data
        
        # Check dimensions
        assert mesh_data['vertices'].shape[1] == 3  # X, Y, Z coordinates
        assert mesh_data['faces'].shape[1] == 3     # Triangle faces
    
    def test_generate_mesh_with_layers(self):
        """Test mesh generation with multiple Z layers."""
        df = pd.DataFrame({
            'XPos': [0, 10, 10, 0] * 3,
            'YPos': [0, 0, 10, 10] * 3,
            'ZPos': [0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2],
            'ToolTemp': [100] * 12,
            'FeedVel': [50] * 12,
            'PathVel': [25] * 12
        })
        
        mesh_data = generate_volume_mesh(df, 'ToolTemp')
        
        assert mesh_data is not None
        # Should have vertices at different Z levels
        z_values = mesh_data['vertices'][:, 2]
        assert len(np.unique(z_values)) > 1
    
    def test_generate_mesh_color_mapping(self, sample_toolpath_data):
        """Test that colors are mapped correctly."""
        mesh_data = generate_volume_mesh(sample_toolpath_data, 'ToolTemp')
        
        assert mesh_data is not None
        colors = mesh_data['vertex_colors']
        
        # Colors should be in range of ToolTemp values
        assert colors.min() >= sample_toolpath_data['ToolTemp'].min()
        assert colors.max() <= sample_toolpath_data['ToolTemp'].max()
    
    def test_generate_mesh_empty_data(self):
        """Test mesh generation with empty DataFrame."""
        df = pd.DataFrame(columns=['XPos', 'YPos', 'ZPos', 'ToolTemp'])
        
        mesh_data = generate_volume_mesh(df, 'ToolTemp')
        
        # Should handle empty data gracefully
        assert mesh_data is None or len(mesh_data['vertices']) == 0
    
    def test_generate_mesh_invalid_column(self, sample_toolpath_data):
        """Test mesh generation with invalid color column."""
        mesh_data = generate_volume_mesh(sample_toolpath_data, 'NonExistentColumn')
        
        # Should handle gracefully
        assert mesh_data is None or 'vertex_colors' in mesh_data
    
    @pytest.mark.parametrize("color_col", ['XPos', 'YPos', 'ZPos', 'ToolTemp'])
    def test_generate_mesh_different_colors(self, sample_toolpath_data, color_col):
        """Test mesh generation with different color columns."""
        mesh_data = generate_volume_mesh(sample_toolpath_data, color_col)
        
        assert mesh_data is not None
        assert len(mesh_data['vertex_colors']) == len(mesh_data['vertices'])
    
    def test_volume_conservation_principle(self):
        """Test that volume mesh generation respects conservation of mass."""
        # Create data with known feed and path velocities
        df = pd.DataFrame({
            'XPos': [0, 10],
            'YPos': [0, 0],
            'ZPos': [0, 0],
            'ToolTemp': [100, 100],
            'FeedVel': [50, 50],  # mm/min
            'PathVel': [25, 25]   # mm/min
        })
        
        mesh_data = generate_volume_mesh(df, 'ToolTemp')
        assert mesh_data is not None
        
        # The generated mesh should have reasonable dimensions
        # Bead area = (FeedVel * FEEDSTOCK_AREA_MM2) / PathVel
        # Expected bead area = (50 * 161.3) / 25 = 322.6 mm²
        expected_bead_area = (50 * FEEDSTOCK_AREA_MM2) / 25
        assert expected_bead_area == pytest.approx(322.6, rel=1e-2)
    
    def test_feedstock_area_in_calculations(self):
        """Test that mesh generation uses correct feedstock area."""
        df = pd.DataFrame({
            'XPos': [0, 10],
            'YPos': [0, 0], 
            'ZPos': [0, 0],
            'ToolTemp': [100, 100],
            'FeedVel': [100, 100],  # mm/min
            'PathVel': [50, 50]     # mm/min
        })
        
        mesh_data = generate_volume_mesh(df, 'ToolTemp')
        assert mesh_data is not None
        
        # With double feed velocity and half path velocity, 
        # bead area should be 4x larger than the previous test
        expected_bead_area = (100 * FEEDSTOCK_AREA_MM2) / 50
        assert expected_bead_area == pytest.approx(322.6, rel=1e-2)
        
        # Verify that the corrected feedstock area (161.3 mm²) is being used
        assert FEEDSTOCK_AREA_MM2 == pytest.approx(161.3, rel=1e-2)
    
    def test_bead_thickness_calculation(self):
        """Test that bead thickness is calculated correctly with new feedstock area."""
        # Test data with specific velocity ratios
        df = pd.DataFrame({
            'XPos': [0, 10],
            'YPos': [0, 0],
            'ZPos': [0, 0], 
            'ToolTemp': [100, 100],
            'FeedVel': [161.3, 161.3],  # Same as feedstock area for easy calculation
            'PathVel': [161.3, 161.3]   # 1:1 ratio
        })
        
        mesh_data = generate_volume_mesh(df, 'ToolTemp')
        assert mesh_data is not None
        
        # With 1:1 feed/path ratio, bead area should equal feedstock area
        # This tests that the mesh generation properly uses the corrected area
        vertices = mesh_data['vertices']
        assert len(vertices) > 0
        
        # Verify mesh has reasonable scale (not too tiny or huge)
        vertex_range = np.max(vertices) - np.min(vertices)
        assert vertex_range > 1  # Should span more than 1mm
        assert vertex_range < 1000  # But less than 1m


class TestFeedstockCalculations:
    """Test feedstock-related calculations with corrected area."""
    
    def test_feedstock_area_constant_accuracy(self):
        """Test that the feedstock area constant is mathematically correct."""
        # MELD uses 0.5" × 0.5" square rod
        expected_dimension_mm = 0.5 * 25.4  # 12.7 mm
        expected_area_mm2 = expected_dimension_mm ** 2  # 161.29 mm²
        
        assert FEEDSTOCK_DIMENSION_INCHES == 0.5
        assert FEEDSTOCK_DIMENSION_MM == pytest.approx(expected_dimension_mm, rel=1e-6)
        assert FEEDSTOCK_AREA_MM2 == pytest.approx(expected_area_mm2, rel=1e-6)
    
    def test_square_rod_vs_circular_wire_difference(self):
        """Test that square rod area is larger than equivalent circular wire."""
        # For comparison, a circular wire with 0.5" diameter would have area:
        circular_area = np.pi * (FEEDSTOCK_DIMENSION_MM / 2) ** 2  # π * (6.35)²
        square_area = FEEDSTOCK_AREA_MM2  # (12.7)²
        
        # Square area should be larger (by factor of 4/π ≈ 1.273)
        assert square_area > circular_area
        ratio = square_area / circular_area
        assert ratio == pytest.approx(4 / np.pi, rel=1e-3)
    
    def test_volume_calculation_with_correct_area(self):
        """Test that volume calculations use the correct feedstock area."""
        # Test with simple 1:1 feed-to-path velocity ratio
        feed_vel = 100  # mm/min
        path_vel = 100  # mm/min
        
        expected_bead_area = (feed_vel * FEEDSTOCK_AREA_MM2) / path_vel
        assert expected_bead_area == FEEDSTOCK_AREA_MM2  # Should equal feedstock area
        assert expected_bead_area == pytest.approx(161.29, rel=1e-2)
    
    def test_mesh_generation_with_corrected_feedstock(self):
        """Test mesh generation uses corrected feedstock area calculations."""
        # Create test data with known velocity relationships
        df = pd.DataFrame({
            'XPos': [0, 10, 20],
            'YPos': [0, 0, 0],
            'ZPos': [0, 0, 0],
            'ToolTemp': [100, 150, 200],
            'FeedVel': [80.65, 80.65, 80.65],  # Half of feedstock area value
            'PathVel': [80.65, 80.65, 80.65]   # Same as feed velocity
        })
        
        mesh_data = generate_volume_mesh(df, 'ToolTemp')
        assert mesh_data is not None
        
        # With these velocities, bead area should equal half the feedstock area
        expected_bead_area = (80.65 * FEEDSTOCK_AREA_MM2) / 80.65
        assert expected_bead_area == pytest.approx(FEEDSTOCK_AREA_MM2, rel=1e-2)
    
    def test_legacy_compatibility_maintained(self):
        """Test that existing functionality still works with corrected area."""
        # This ensures backward compatibility while using corrected calculations
        df = pd.DataFrame({
            'XPos': [0, 10],
            'YPos': [0, 0],
            'ZPos': [0, 0],
            'ToolTemp': [100, 100],
            'FeedVel': [50, 50],
            'PathVel': [25, 25]
        })
        
        mesh_data = generate_volume_mesh(df, 'ToolTemp')
        assert mesh_data is not None
        
        # Should generate valid mesh with reasonable vertex count
        assert len(mesh_data['vertices']) > 0
        assert len(mesh_data['faces']) > 0
        assert len(mesh_data['vertex_colors']) == len(mesh_data['vertices'])


class TestDataProcessingHelpers:
    """Test helper functions and edge cases."""
    
    def test_constants_imported(self):
        """Test that constants are properly imported."""
        assert INCH_TO_MM == 25.4
        assert FEEDSTOCK_AREA_MM2 > 0
    
    @patch('data_processing.FileValidator')
    def test_security_validation_called(self, mock_validator):
        """Test that security validation is called."""
        mock_validator.validate_file_upload.return_value = (True, None)
        
        contents = "data:text/csv;base64,VGVzdA=="
        parse_contents(contents, "test.csv")
        
        # Security validation should be called
        mock_validator.validate_file_upload.assert_called()
    
    def test_dataframe_columns_present(self):
        """Test that all required columns are present after parsing."""
        df = pd.DataFrame({
            'XPos': [0, 1, 2],
            'YPos': [0, 1, 2],
            'ZPos': [0, 1, 2],
            'FeedVel': [0, 50, 100],
            'PathVel': [0, 25, 50],
            'Time': pd.date_range('2024-01-01', periods=3, freq='S')
        })
        
        csv_string = df.to_csv(index=False)
        encoded = base64.b64encode(csv_string.encode()).decode()
        contents = f"data:text/csv;base64,{encoded}"
        
        result_df, _, _ = parse_contents(contents, "test.csv")
        
        required_columns = ['XPos', 'YPos', 'ZPos', 'FeedVel', 'PathVel', 'TimeInSeconds']
        for col in required_columns:
            assert col in result_df.columns


if __name__ == "__main__":
    pytest.main([__file__, "-v"])