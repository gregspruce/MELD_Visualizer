"""
Unit tests for service layer.
Tests cache service, data service, and file service.
"""

import pytest
import pandas as pd
import numpy as np
import time
import json
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from src.meld_visualizer.services import (
    CacheService, DataService, FileService,
    get_cache, get_data_service
)
from src.meld_visualizer.services.cache_service import cached


class TestCacheService:
    """Test cache service functionality."""
    
    @pytest.fixture
    def cache(self):
        """Create a cache instance for testing."""
        return CacheService(max_size_mb=1, ttl_seconds=2)
    
    def test_cache_set_and_get(self, cache):
        """Test basic cache set and get operations."""
        cache.set("test_key", {"data": "test_value"})
        result = cache.get("test_key")
        
        assert result == {"data": "test_value"}
        assert cache.hits == 1
        assert cache.misses == 0
    
    def test_cache_miss(self, cache):
        """Test cache miss."""
        result = cache.get("nonexistent_key")
        
        assert result is None
        assert cache.hits == 0
        assert cache.misses == 1
    
    def test_cache_ttl_expiration(self, cache):
        """Test that cache entries expire after TTL."""
        cache.set("expiring_key", "value")
        
        # Should retrieve before expiration
        assert cache.get("expiring_key") == "value"
        
        # Wait for expiration
        time.sleep(2.1)
        
        # Should be expired
        assert cache.get("expiring_key") is None
        assert cache.misses == 1
    
    def test_cache_lru_eviction(self, cache):
        """Test LRU eviction when cache is full."""
        # Fill cache with data
        for i in range(100):
            large_data = "x" * 10000  # ~10KB each
            cache.set(f"key_{i}", large_data)
        
        # Oldest entries should be evicted
        assert cache.get("key_0") is None  # Evicted
        assert cache.get("key_99") is not None  # Still present
    
    def test_cache_dataframe(self, cache):
        """Test caching DataFrames."""
        df = pd.DataFrame({
            'A': [1, 2, 3],
            'B': [4, 5, 6]
        })
        
        key = cache.cache_dataframe(df, "test_df")
        retrieved = cache.get_dataframe("test_df")
        
        assert retrieved is not None
        pd.testing.assert_frame_equal(df, retrieved)
    
    def test_cache_stats(self, cache):
        """Test cache statistics."""
        cache.set("key1", "value1")
        cache.get("key1")  # Hit
        cache.get("key2")  # Miss
        
        stats = cache.get_stats()
        
        assert stats['entries'] == 1
        assert stats['hits'] == 1
        assert stats['misses'] == 1
        assert stats['hit_rate'] == 0.5
    
    def test_cache_clear(self, cache):
        """Test cache clearing."""
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        cache.clear()
        
        assert cache.get("key1") is None
        assert cache.get("key2") is None
        assert cache.current_size_bytes == 0
    
    def test_cached_decorator(self, cache):
        """Test the @cached decorator."""
        call_count = 0
        
        @cached("test")
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # First call - should execute
        result1 = expensive_function(5)
        assert result1 == 10
        assert call_count == 1
        
        # Second call - should use cache
        result2 = expensive_function(5)
        assert result2 == 10
        assert call_count == 1  # Not incremented
    
    def test_global_cache_singleton(self):
        """Test that get_cache returns singleton."""
        cache1 = get_cache()
        cache2 = get_cache()
        
        assert cache1 is cache2


class TestDataService:
    """Test data service functionality."""
    
    @pytest.fixture
    def data_service(self):
        """Create a data service instance for testing."""
        service = DataService()
        service.cache.clear()  # Start with clean cache
        return service
    
    @pytest.fixture
    def sample_df(self):
        """Create sample DataFrame."""
        return pd.DataFrame({
            'XPos': np.random.randn(100),
            'YPos': np.random.randn(100),
            'ZPos': np.random.randn(100),
            'FeedVel': np.random.rand(100) * 100,
            'PathVel': np.random.rand(100) * 50,
            'ToolTemp': np.random.rand(100) * 200
        })
    
    @patch('services.data_service.FileValidator')
    @patch('services.data_service.parse_contents_impl')
    def test_parse_file_with_caching(self, mock_parse, mock_validator, data_service, sample_df):
        """Test file parsing with caching."""
        mock_validator.validate_file_upload.return_value = (True, None)
        mock_parse.return_value = (sample_df, None, False)
        
        contents = "data:text/csv;base64,test"
        filename = "test.csv"
        
        # First call - should parse
        df1, error1, converted1 = data_service.parse_file(contents, filename)
        assert df1 is not None
        assert mock_parse.call_count == 1
        
        # Second call - should use cache
        df2, error2, converted2 = data_service.parse_file(contents, filename)
        assert df2 is not None
        assert mock_parse.call_count == 1  # Not called again
    
    def test_filter_active_data(self, data_service, sample_df):
        """Test filtering active data."""
        # Set some velocities to zero
        sample_df.loc[:10, 'FeedVel'] = 0
        sample_df.loc[:20, 'PathVel'] = 0
        
        active_df = data_service.filter_active_data(sample_df)
        
        assert len(active_df) < len(sample_df)
        assert all(active_df['FeedVel'] > 0)
        assert all(active_df['PathVel'] > 1e-6)
    
    def test_filter_by_range(self, data_service, sample_df):
        """Test range filtering."""
        filtered = data_service.filter_by_range(
            sample_df, 'ZPos', -1.0, 1.0
        )
        
        assert all(filtered['ZPos'] >= -1.0)
        assert all(filtered['ZPos'] <= 1.0)
        assert len(filtered) <= len(sample_df)
    
    def test_filter_invalid_column(self, data_service, sample_df):
        """Test filtering with invalid column."""
        filtered = data_service.filter_by_range(
            sample_df, 'NonExistent', 0, 100
        )
        
        # Should return original DataFrame
        pd.testing.assert_frame_equal(filtered, sample_df)
    
    @patch('services.data_service.generate_mesh_impl')
    def test_generate_mesh_with_caching(self, mock_generate, data_service, sample_df):
        """Test mesh generation with caching."""
        mock_mesh = {
            'vertices': np.array([[0, 0, 0], [1, 1, 1]]),
            'faces': np.array([[0, 1, 2]]),
            'vertex_colors': np.array([100, 200])
        }
        mock_generate.return_value = mock_mesh
        
        # First call
        mesh1 = data_service.generate_mesh(sample_df, 'ToolTemp', 'high')
        assert mesh1 is not None
        assert mock_generate.call_count == 1
        
        # Second call - should use cache
        mesh2 = data_service.generate_mesh(sample_df, 'ToolTemp', 'high')
        assert mesh2 is not None
        assert mock_generate.call_count == 1  # Not called again
    
    def test_get_column_statistics(self, data_service, sample_df):
        """Test column statistics generation."""
        stats = data_service.get_column_statistics(sample_df)
        
        assert 'XPos' in stats
        assert 'min' in stats['XPos']
        assert 'max' in stats['XPos']
        assert 'mean' in stats['XPos']
        assert 'std' in stats['XPos']
        assert 'count' in stats['XPos']
    
    def test_validate_columns(self, data_service, sample_df):
        """Test column validation."""
        # Valid columns
        valid, missing = data_service.validate_columns(
            sample_df, ['XPos', 'YPos', 'ZPos']
        )
        assert valid is True
        assert missing == []
        
        # Invalid columns
        valid, missing = data_service.validate_columns(
            sample_df, ['XPos', 'NonExistent']
        )
        assert valid is False
        assert 'NonExistent' in missing
    
    def test_process_in_chunks(self, data_service):
        """Test chunked processing."""
        large_df = pd.DataFrame({
            'value': range(1000)
        })
        
        def double_values(df):
            df['value'] = df['value'] * 2
            return df
        
        result = data_service.process_in_chunks(
            large_df, double_values, chunk_size=100
        )
        
        assert all(result['value'] == large_df.index * 2)
    
    def test_global_data_service_singleton(self):
        """Test that get_data_service returns singleton."""
        service1 = get_data_service()
        service2 = get_data_service()
        
        assert service1 is service2


class TestFileService:
    """Test file service functionality."""
    
    def test_get_file_extension(self):
        """Test file extension detection."""
        assert FileService.get_file_extension("test.csv") == ".csv"
        assert FileService.get_file_extension("file.NC") == ".nc"
        assert FileService.get_file_extension("path/to/file.txt") == ".txt"
    
    def test_is_csv_file(self):
        """Test CSV file detection."""
        assert FileService.is_csv_file("data.csv") is True
        assert FileService.is_csv_file("data.CSV") is True
        assert FileService.is_csv_file("data.txt") is False
    
    def test_is_gcode_file(self):
        """Test G-code file detection."""
        assert FileService.is_gcode_file("program.nc") is True
        assert FileService.is_gcode_file("program.gcode") is True
        assert FileService.is_gcode_file("program.txt") is True
        assert FileService.is_gcode_file("program.csv") is False
    
    def test_decode_file_contents(self):
        """Test file content decoding."""
        test_data = b"Hello, World!"
        encoded = base64.b64encode(test_data).decode()
        contents = f"data:text/plain;base64,{encoded}"
        
        decoded, error = FileService.decode_file_contents(contents)
        
        assert decoded == test_data
        assert error is None
    
    def test_decode_invalid_contents(self):
        """Test decoding invalid contents."""
        decoded, error = FileService.decode_file_contents("invalid")
        
        assert decoded is None
        assert error is not None
    
    def test_validate_file_size(self):
        """Test file size validation."""
        # Small file
        small_data = b"x" * 1000
        encoded = base64.b64encode(small_data).decode()
        contents = f"data:text/plain;base64,{encoded}"
        
        valid, error = FileService.validate_file_size(contents)
        assert valid is True
        assert error is None
        
        # Large file (simulate)
        # Note: Actually creating 11MB of data would be slow
        # So we'll patch the decode function
        with patch.object(FileService, 'decode_file_contents') as mock_decode:
            mock_decode.return_value = (b"x" * (11 * 1024 * 1024), None)
            valid, error = FileService.validate_file_size("fake_contents")
            
            assert valid is False
            assert "too large" in error.lower()
    
    def test_detect_delimiter(self):
        """Test CSV delimiter detection."""
        # Comma delimiter
        csv_comma = "a,b,c\n1,2,3\n4,5,6"
        assert FileService.detect_delimiter(csv_comma) == ','
        
        # Tab delimiter
        csv_tab = "a\tb\tc\n1\t2\t3\n4\t5\t6"
        assert FileService.detect_delimiter(csv_tab) == '\t'
        
        # Semicolon delimiter
        csv_semi = "a;b;c\n1;2;3\n4;5;6"
        assert FileService.detect_delimiter(csv_semi) == ';'
    
    def test_get_file_info(self):
        """Test file information extraction."""
        test_data = b"Test file content"
        encoded = base64.b64encode(test_data).decode()
        contents = f"data:text/csv;base64,{encoded}"
        
        info = FileService.get_file_info(contents, "test.csv")
        
        assert info['filename'] == "test.csv"
        assert info['extension'] == ".csv"
        assert info['size_bytes'] == len(test_data)
        assert info['is_csv'] is True
        assert info['is_gcode'] is False


class TestServiceIntegration:
    """Test integration between services."""
    
    def test_data_service_uses_cache(self):
        """Test that data service properly uses cache service."""
        data_service = DataService()
        data_service.clear_cache()
        
        # Check cache is empty
        stats = data_service.get_cache_stats()
        assert stats['entries'] == 0
        
        # Add some data
        df = pd.DataFrame({'A': [1, 2, 3]})
        data_service.cache.cache_dataframe(df, "test")
        
        # Check cache has data
        stats = data_service.get_cache_stats()
        assert stats['entries'] == 1
    
    @patch('services.data_service.FileValidator')
    def test_file_validation_integration(self, mock_validator):
        """Test that file validation is properly integrated."""
        mock_validator.validate_file_upload.return_value = (False, "Invalid file")
        
        data_service = DataService()
        df, error, converted = data_service.parse_file("contents", "file.txt")
        
        assert df is None
        assert error == "Invalid file"
        assert converted is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])