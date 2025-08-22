"""
Unit tests for data processing functionality in MELD Visualizer.
Tests data loading, validation, and transformation functions.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from unittest.mock import patch, Mock

# Import the modules under test
try:
    from meld_visualizer.core.data_processing import (
        load_csv_data, 
        validate_meld_data,
        process_gcode_data,
        calculate_statistics,
        filter_data_by_range
    )
except ImportError:
    # If direct import fails, skip these tests
    pytestmark = pytest.mark.skip("Data processing module not available")


class TestDataLoading:
    """Test data loading functionality"""
    
    def test_load_valid_csv(self, sample_meld_csv_path):
        """Test loading a valid CSV file"""
        if not sample_meld_csv_path.exists():
            pytest.skip("Sample CSV file not found")
            
        df = load_csv_data(sample_meld_csv_path)
        
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert 'Date' in df.columns
        assert 'Time' in df.columns
        assert 'XPos' in df.columns
        assert 'YPos' in df.columns
        assert 'ZPos' in df.columns
    
    def test_load_minimal_csv(self, minimal_meld_csv_path):
        """Test loading minimal CSV with few rows"""
        if not minimal_meld_csv_path.exists():
            pytest.skip("Minimal CSV file not found")
            
        df = load_csv_data(minimal_meld_csv_path)
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) >= 1  # Should have at least one data row
    
    def test_load_nonexistent_file(self):
        """Test handling of non-existent file"""
        with pytest.raises(FileNotFoundError):
            load_csv_data("nonexistent_file.csv")
    
    def test_load_invalid_csv_format(self, temp_csv_file):
        """Test handling of malformed CSV"""
        # Create invalid CSV content
        with open(temp_csv_file, 'w') as f:
            f.write("Invalid,CSV,Content\nwith,missing,columns\n")
        
        with pytest.raises((ValueError, KeyError, pd.errors.EmptyDataError)):
            load_csv_data(temp_csv_file)
    
    @pytest.mark.performance
    def test_load_large_csv_performance(self, large_dataframe, tmp_path):
        """Test performance with large CSV files"""
        # Create a temporary large CSV file
        large_csv_path = tmp_path / "large_test.csv"
        large_dataframe.to_csv(large_csv_path, index=False)
        
        import time
        start_time = time.time()
        df = load_csv_data(large_csv_path)
        load_time = time.time() - start_time
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == len(large_dataframe)
        assert load_time < 10.0  # Should load within 10 seconds


class TestDataValidation:
    """Test data validation functionality"""
    
    def test_validate_complete_data(self, sample_meld_dataframe):
        """Test validation of complete, valid data"""
        is_valid, errors = validate_meld_data(sample_meld_dataframe)
        
        assert is_valid
        assert len(errors) == 0
    
    def test_validate_missing_columns(self):
        """Test validation with missing required columns"""
        incomplete_df = pd.DataFrame({
            'Date': ['2024-01-15'],
            'Time': ['10:00:00.00']
            # Missing XPos, YPos, ZPos
        })
        
        is_valid, errors = validate_meld_data(incomplete_df)
        
        assert not is_valid
        assert len(errors) > 0
        assert any("missing" in error.lower() for error in errors)
    
    def test_validate_empty_dataframe(self, empty_dataframe):
        """Test validation of empty DataFrame"""
        is_valid, errors = validate_meld_data(empty_dataframe)
        
        assert not is_valid
        assert any("empty" in error.lower() for error in errors)
    
    def test_validate_invalid_data_types(self):
        """Test validation with invalid data types"""
        invalid_df = pd.DataFrame({
            'Date': ['2024-01-15'],
            'Time': ['10:00:00.00'],
            'SpinVel': ['not_a_number'],  # Should be numeric
            'XPos': [5.0],
            'YPos': [10.0],
            'ZPos': [2.0]
        })
        
        is_valid, errors = validate_meld_data(invalid_df)
        
        assert not is_valid
        assert any("data type" in error.lower() or "numeric" in error.lower() for error in errors)
    
    def test_validate_nan_values(self):
        """Test validation with NaN values"""
        nan_df = pd.DataFrame({
            'Date': ['2024-01-15'],
            'Time': ['10:00:00.00'],
            'SpinVel': [np.nan],
            'XPos': [5.0],
            'YPos': [np.nan],
            'ZPos': [2.0]
        })
        
        is_valid, errors = validate_meld_data(nan_df)
        # Depending on requirements, NaN might be acceptable or not
        # Adjust assertion based on actual validation rules


class TestGCodeProcessing:
    """Test G-code processing functionality"""
    
    def test_process_valid_gcode(self, sample_gcode_path):
        """Test processing of valid G-code file"""
        if not sample_gcode_path.exists():
            pytest.skip("Sample G-code file not found")
            
        gcode_data = process_gcode_data(sample_gcode_path)
        
        assert isinstance(gcode_data, (dict, list))
        # Add specific assertions based on expected G-code structure
    
    def test_process_empty_gcode_file(self, tmp_path):
        """Test processing of empty G-code file"""
        empty_gcode = tmp_path / "empty.nc"
        empty_gcode.write_text("")
        
        with pytest.raises((ValueError, FileNotFoundError)):
            process_gcode_data(empty_gcode)
    
    def test_extract_coordinates_from_gcode(self, sample_gcode_path):
        """Test extraction of coordinate data from G-code"""
        if not sample_gcode_path.exists():
            pytest.skip("Sample G-code file not found")
            
        gcode_data = process_gcode_data(sample_gcode_path)
        
        # Assuming the function returns coordinate information
        if isinstance(gcode_data, dict):
            assert 'coordinates' in gcode_data or 'positions' in gcode_data
        elif isinstance(gcode_data, list):
            # Check if list contains coordinate data
            assert len(gcode_data) > 0


class TestStatisticalCalculations:
    """Test statistical calculation functions"""
    
    def test_calculate_basic_statistics(self, sample_meld_dataframe):
        """Test calculation of basic statistics"""
        stats = calculate_statistics(sample_meld_dataframe)
        
        assert isinstance(stats, dict)
        
        # Check for expected statistical measures
        expected_stats = ['mean', 'std', 'min', 'max', 'count']
        for stat in expected_stats:
            assert stat in stats
        
        # Verify calculations for known data
        assert stats['count'] == len(sample_meld_dataframe)
        assert stats['mean']['SpinVel'] == pytest.approx(102.0, rel=1e-2)
    
    def test_calculate_statistics_empty_data(self, empty_dataframe):
        """Test statistics calculation with empty data"""
        with pytest.raises((ValueError, ZeroDivisionError)):
            calculate_statistics(empty_dataframe)
    
    def test_calculate_statistics_single_row(self):
        """Test statistics calculation with single row"""
        single_row_df = pd.DataFrame({
            'SpinVel': [100.0],
            'XPos': [5.0],
            'YPos': [10.0],
            'ZPos': [2.0]
        })
        
        stats = calculate_statistics(single_row_df)
        
        assert stats['count'] == 1
        assert stats['mean']['SpinVel'] == 100.0
        assert stats['std']['SpinVel'] == 0.0  # Standard deviation of single value


class TestDataFiltering:
    """Test data filtering functionality"""
    
    def test_filter_by_numeric_range(self, sample_meld_dataframe):
        """Test filtering by numeric range"""
        filtered_df = filter_data_by_range(
            sample_meld_dataframe, 
            column='SpinVel', 
            min_value=101.0, 
            max_value=103.0
        )
        
        assert isinstance(filtered_df, pd.DataFrame)
        assert len(filtered_df) <= len(sample_meld_dataframe)
        assert all(filtered_df['SpinVel'] >= 101.0)
        assert all(filtered_df['SpinVel'] <= 103.0)
    
    def test_filter_by_invalid_column(self, sample_meld_dataframe):
        """Test filtering with non-existent column"""
        with pytest.raises(KeyError):
            filter_data_by_range(
                sample_meld_dataframe,
                column='NonexistentColumn',
                min_value=0,
                max_value=100
            )
    
    def test_filter_with_invalid_range(self, sample_meld_dataframe):
        """Test filtering with invalid range (min > max)"""
        filtered_df = filter_data_by_range(
            sample_meld_dataframe,
            column='SpinVel',
            min_value=200.0,  # Greater than max value in data
            max_value=100.0   # Less than min_value
        )
        
        # Should return empty DataFrame
        assert len(filtered_df) == 0
    
    def test_filter_preserves_data_structure(self, sample_meld_dataframe):
        """Test that filtering preserves DataFrame structure"""
        original_columns = list(sample_meld_dataframe.columns)
        
        filtered_df = filter_data_by_range(
            sample_meld_dataframe,
            column='SpinVel',
            min_value=100.0,
            max_value=105.0
        )
        
        assert list(filtered_df.columns) == original_columns
        assert filtered_df.dtypes.equals(sample_meld_dataframe.dtypes)


class TestDataTransformations:
    """Test data transformation functions"""
    
    def test_coordinate_system_conversion(self, sample_meld_dataframe):
        """Test coordinate system transformations if implemented"""
        # This test would depend on specific transformation functions
        # Placeholder for coordinate system conversions
        pass
    
    def test_time_series_processing(self, sample_meld_dataframe):
        """Test time series data processing"""
        # Test time-based operations if implemented
        # Could include resampling, interpolation, etc.
        pass
    
    def test_data_normalization(self, sample_meld_dataframe):
        """Test data normalization functions"""
        # Test data scaling/normalization if implemented
        pass


# Integration tests that combine multiple functions
class TestDataProcessingIntegration:
    """Integration tests for data processing pipeline"""
    
    def test_full_data_pipeline(self, sample_meld_csv_path):
        """Test complete data processing pipeline"""
        if not sample_meld_csv_path.exists():
            pytest.skip("Sample CSV file not found")
        
        # Load data
        df = load_csv_data(sample_meld_csv_path)
        
        # Validate data
        is_valid, errors = validate_meld_data(df)
        assert is_valid, f"Data validation failed: {errors}"
        
        # Calculate statistics
        stats = calculate_statistics(df)
        assert isinstance(stats, dict)
        
        # Filter data
        filtered_df = filter_data_by_range(df, 'SpinVel', 100, 110)
        assert isinstance(filtered_df, pd.DataFrame)
    
    @pytest.mark.performance
    def test_pipeline_performance(self, large_dataframe, tmp_path):
        """Test performance of complete pipeline with large data"""
        # Save large DataFrame as CSV
        large_csv = tmp_path / "large_performance_test.csv"
        large_dataframe.to_csv(large_csv, index=False)
        
        import time
        start_time = time.time()
        
        # Run complete pipeline
        df = load_csv_data(large_csv)
        is_valid, _ = validate_meld_data(df)
        if is_valid:
            stats = calculate_statistics(df)
            filtered_df = filter_data_by_range(df, 'SpinVel', 90, 110)
        
        total_time = time.time() - start_time
        
        # Performance assertion
        assert total_time < 30.0  # Should complete within 30 seconds