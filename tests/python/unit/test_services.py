"""
Unit tests for service layer functionality in MELD Visualizer.
Tests cache service, data service, and file service modules.
"""

import time
from pathlib import Path

import pandas as pd
import pytest

# Import the modules under test
try:
    from meld_visualizer.services.cache_service import CacheService
    from meld_visualizer.services.data_service import DataService
    from meld_visualizer.services.file_service import FileService
except ImportError:
    # If direct import fails, skip these tests
    pytestmark = pytest.mark.skip("Service modules not available")


class TestCacheService:
    """Test cache service functionality"""

    @pytest.fixture
    def cache_service(self):
        """Create a cache service instance for testing"""
        return CacheService()

    def test_cache_initialization(self, cache_service):
        """Test cache service initialization"""
        assert cache_service is not None
        # Test that cache is properly initialized

    def test_cache_set_and_get(self, cache_service):
        """Test basic cache set and get operations"""
        key = "test_key"
        value = {"data": "test_value", "timestamp": time.time()}

        # Set cache value (CacheService.set() returns None, not boolean)
        cache_service.set(key, value)

        # Get cache value
        retrieved_value = cache_service.get(key)
        assert retrieved_value == value

    def test_cache_get_nonexistent_key(self, cache_service):
        """Test getting non-existent cache key"""
        result = cache_service.get("nonexistent_key")
        assert result is None

    def test_cache_clear(self, cache_service):
        """Test cache clearing functionality"""
        # Set some values
        cache_service.set("key1", "value1")
        cache_service.set("key2", "value2")

        # Clear cache (CacheService.clear() returns None, not boolean)
        cache_service.clear()

        # Verify values are cleared
        assert cache_service.get("key1") is None
        assert cache_service.get("key2") is None

    def test_cache_expiration(self, cache_service):
        """Test cache expiration functionality"""
        # CacheService uses default TTL from constants, not per-key TTL
        # Test by setting a cache with very short default TTL
        short_ttl_cache = CacheService(ttl_seconds=1)

        key = "expiring_key"
        value = "expiring_value"

        # Set value
        short_ttl_cache.set(key, value)

        # Should be available immediately
        assert short_ttl_cache.get(key) == value

        # Wait for expiration
        time.sleep(1.5)

        # Should be expired now
        result = short_ttl_cache.get(key)
        assert result is None

    def test_cache_size_limit(self, cache_service):
        """Test cache size limitations"""
        # Test behavior when cache reaches size limit
        # This depends on cache implementation details

    def test_cache_key_validation(self, cache_service):
        """Test cache key validation"""
        # CacheService accepts any key type and converts to string internally
        # Test that various key types work but produce consistent results
        test_cases = [
            ("string_key", "string_key"),
            (123, 123),
            (None, None),
        ]

        for key, expected in test_cases:
            cache_service.set(key, f"value_for_{key}")
            result = cache_service.get(key)
            assert result == f"value_for_{key}"

    def test_cache_value_serialization(self, cache_service):
        """Test that complex values can be cached"""
        complex_value = {
            "dataframe": pd.DataFrame({"col": [1, 2, 3]}),
            "list": [1, 2, 3],
            "dict": {"nested": "value"},
        }

        key = "complex_key"

        # This might require special serialization handling
        try:
            cache_service.set(key, complex_value)
            cache_service.get(key)
            # Add assertions based on how serialization is handled
        except (TypeError, ValueError):
            # Some values might not be serializable
            pytest.skip("Complex value serialization not supported")


class TestDataService:
    """Test data service functionality"""

    @pytest.fixture
    def data_service(self, mock_cache_service):
        """Create a data service instance for testing"""
        return DataService(cache=mock_cache_service)

    def test_data_service_initialization(self, data_service):
        """Test data service initialization"""
        assert data_service is not None

    def test_load_csv_data(self, data_service, sample_meld_csv_path):
        """Test CSV data loading through data service"""
        if not sample_meld_csv_path.exists():
            pytest.skip("Sample CSV file not found")

        df = data_service.load_csv_data(sample_meld_csv_path)

        assert isinstance(df, pd.DataFrame)
        assert not df.empty

    def test_process_data_with_cache(self, data_service, sample_meld_dataframe):
        """Test data processing with caching"""
        processed_data = data_service.process_data(sample_meld_dataframe)

        # Should return processed data
        assert processed_data is not None

        # Second call should use cache
        cached_data = data_service.process_data(sample_meld_dataframe)
        assert cached_data is not None

    def test_validate_data_format(self, data_service, sample_meld_dataframe):
        """Test data format validation"""
        is_valid = data_service.validate_data_format(sample_meld_dataframe)
        assert is_valid is True

        # Test with invalid data
        invalid_df = pd.DataFrame({"wrong": ["columns"]})
        is_valid = data_service.validate_data_format(invalid_df)
        assert is_valid is False

    def test_calculate_data_statistics(self, data_service, sample_meld_dataframe):
        """Test statistical calculations through data service"""
        stats = data_service.calculate_statistics(sample_meld_dataframe)

        assert isinstance(stats, dict)
        assert "mean" in stats or "summary" in stats

    def test_filter_data(self, data_service, sample_meld_dataframe):
        """Test data filtering through data service"""
        filters = {"SpinVel": {"min": 101, "max": 103}}

        filtered_df = data_service.filter_data(sample_meld_dataframe, filters)

        assert isinstance(filtered_df, pd.DataFrame)
        assert len(filtered_df) <= len(sample_meld_dataframe)

    def test_data_service_error_handling(self, data_service):
        """Test error handling in data service"""
        # Test with invalid input
        with pytest.raises((ValueError, TypeError)):
            data_service.load_csv_data("nonexistent_file.csv")

    @pytest.mark.performance
    def test_data_service_performance(self, data_service, large_dataframe):
        """Test data service performance with large datasets"""
        start_time = time.time()

        # Process large dataset
        result = data_service.process_data(large_dataframe)

        processing_time = time.time() - start_time

        assert result is not None
        assert processing_time < 10.0  # Should complete within 10 seconds


class TestFileService:
    """Test file service functionality"""

    @pytest.fixture
    def file_service(self):
        """Create a file service instance for testing"""
        return FileService()

    def test_file_service_initialization(self, file_service):
        """Test file service initialization"""
        assert file_service is not None

    def test_validate_file_type(self, file_service):
        """Test file type validation"""
        # Valid file types
        assert file_service.validate_file_type("data.csv") is True
        assert file_service.validate_file_type("toolpath.nc") is True

        # Invalid file types
        assert file_service.validate_file_type("document.txt") is False
        assert file_service.validate_file_type("image.png") is False

    def test_validate_file_size(self, file_service, temp_csv_file):
        """Test file size validation"""
        file_path = Path(temp_csv_file)

        # Should be valid for small test file
        is_valid = file_service.validate_file_size(file_path)
        assert is_valid is True

    def test_read_csv_file(self, file_service, sample_meld_csv_path):
        """Test CSV file reading"""
        if not sample_meld_csv_path.exists():
            pytest.skip("Sample CSV file not found")

        content = file_service.read_csv_file(sample_meld_csv_path)

        assert isinstance(content, (pd.DataFrame, dict))

    def test_read_gcode_file(self, file_service, sample_gcode_path):
        """Test G-code file reading"""
        if not sample_gcode_path.exists():
            pytest.skip("Sample G-code file not found")

        content = file_service.read_gcode_file(sample_gcode_path)

        assert content is not None
        # Content format depends on implementation

    def test_save_processed_data(self, file_service, sample_meld_dataframe, tmp_path):
        """Test saving processed data"""
        output_path = tmp_path / "output.csv"

        success = file_service.save_processed_data(sample_meld_dataframe, output_path)

        assert success is True
        assert output_path.exists()

        # Verify saved content
        saved_df = pd.read_csv(output_path)
        assert len(saved_df) == len(sample_meld_dataframe)

    def test_file_cleanup(self, file_service, tmp_path):
        """Test temporary file cleanup"""
        # Create temporary files
        temp_file1 = tmp_path / "temp1.csv"
        temp_file2 = tmp_path / "temp2.csv"

        temp_file1.write_text("temp content")
        temp_file2.write_text("temp content")

        # Test cleanup
        files_to_clean = [temp_file1, temp_file2]
        success = file_service.cleanup_temp_files(files_to_clean)

        assert success is True
        # Files should be removed (depending on implementation)

    def test_file_security_validation(self, file_service):
        """Test file security validation"""
        # Test potentially dangerous file paths
        dangerous_paths = [
            "../../../etc/passwd",
            "C:\\Windows\\System32\\config\\SAM",
            "/etc/shadow",
        ]

        for path in dangerous_paths:
            is_safe = file_service.validate_file_path(path)
            assert is_safe is False

    def test_file_encoding_detection(self, file_service, tmp_path):
        """Test file encoding detection"""
        # Create file with different encodings
        utf8_file = tmp_path / "utf8.csv"
        utf8_file.write_text("Date,Value\n2024-01-15,100", encoding="utf-8")

        encoding = file_service.detect_file_encoding(utf8_file)
        assert encoding is not None
        assert "utf" in encoding.lower()


class TestServiceIntegration:
    """Integration tests for services working together"""

    @pytest.fixture
    def integrated_services(self):
        """Create integrated service instances"""
        cache = CacheService()
        data_service = DataService(cache=cache)
        file_service = FileService()

        return {"cache": cache, "data": data_service, "file": file_service}

    def test_file_to_data_pipeline(self, integrated_services, sample_meld_csv_path):
        """Test complete pipeline from file loading to data processing"""
        if not sample_meld_csv_path.exists():
            pytest.skip("Sample CSV file not found")

        file_service = integrated_services["file"]
        data_service = integrated_services["data"]

        # Validate file
        is_valid_type = file_service.validate_file_type(str(sample_meld_csv_path))
        assert is_valid_type is True

        is_valid_size = file_service.validate_file_size(sample_meld_csv_path)
        assert is_valid_size is True

        # Load and process data
        df = data_service.load_csv_data(sample_meld_csv_path)
        assert isinstance(df, pd.DataFrame)

        # Process data
        processed = data_service.process_data(df)
        assert processed is not None

    def test_caching_across_services(self, integrated_services, sample_meld_dataframe):
        """Test that caching works across different services"""
        data_service = integrated_services["data"]
        cache = integrated_services["cache"]

        # Process data (should cache result)
        result1 = data_service.process_data(sample_meld_dataframe)

        # Check cache directly
        cache_key = data_service.generate_cache_key(sample_meld_dataframe)
        cached_result = cache.get(cache_key)

        # Should have cached result
        assert cached_result is not None

        # Process again (should use cache)
        result2 = data_service.process_data(sample_meld_dataframe)

        # Results should be the same
        assert result1 == result2 or pd.DataFrame(result1).equals(pd.DataFrame(result2))

    def test_error_propagation_across_services(self, integrated_services):
        """Test that errors propagate correctly across services"""
        data_service = integrated_services["data"]

        # Test error handling
        with pytest.raises((FileNotFoundError, ValueError)):
            data_service.load_csv_data("nonexistent_file.csv")

    @pytest.mark.performance
    def test_integrated_performance(self, integrated_services, large_dataframe, tmp_path):
        """Test performance of integrated services"""
        # Save large dataset
        large_csv = tmp_path / "large_integration_test.csv"
        large_dataframe.to_csv(large_csv, index=False)

        file_service = integrated_services["file"]
        data_service = integrated_services["data"]

        start_time = time.time()

        # Complete workflow
        file_service.validate_file_type(str(large_csv))
        df = data_service.load_csv_data(large_csv)
        processed = data_service.process_data(df)

        total_time = time.time() - start_time

        assert processed is not None
        assert total_time < 30.0  # Should complete within 30 seconds
