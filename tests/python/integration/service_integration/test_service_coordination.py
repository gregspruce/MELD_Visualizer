"""
Service Coordination Integration Tests
Tests service-to-service communication and data flow coordination.
"""

import os
import tempfile
import time

import numpy as np
import pandas as pd
import pytest

from meld_visualizer.services.cache_service import CacheService

# Import services for testing
from meld_visualizer.services.data_service import DataService
from meld_visualizer.services.file_service import FileService

from ..fixtures.dash_app_fixtures import (
    CallbackAssertions,
    MockFileUpload,
)


class TestServiceCoordination:
    """Test coordination between DataService, CacheService, and FileService."""

    @pytest.fixture(autouse=True)
    def setup(self, callback_tester, mock_services):
        """Setup test environment with real service instances."""
        self.tester = callback_tester
        self.mock_services = mock_services
        self.assertions = CallbackAssertions()

        # Create real service instances for integration testing
        self.data_service = DataService()
        self.cache_service = CacheService()
        self.file_service = FileService()

        # Sample test data
        self.test_df = pd.DataFrame(
            {
                "Date": ["2024-01-15"] * 10,
                "Time": [f"10:00:{i:02d}.00" for i in range(10)],
                "XPos": np.linspace(0, 10, 10),
                "YPos": np.linspace(0, 20, 10),
                "ZPos": np.linspace(0, 5, 10),
                "SpinVel": np.linspace(100, 200, 10),
                "ToolTemp": np.linspace(150, 250, 10),
            }
        )

    def test_data_service_cache_service_coordination(self):
        """Test coordination between DataService and CacheService."""

        # Test caching DataFrame
        cache_key = "test_dataframe_key"

        # Cache data through DataService
        success = self.data_service.cache.cache_dataframe(self.test_df, cache_key)
        assert success, "DataFrame should be cached successfully"

        # Retrieve cached data
        cached_df = self.data_service.cache.get_dataframe(cache_key)
        assert cached_df is not None, "Cached DataFrame should be retrievable"
        assert len(cached_df) == len(self.test_df), "Cached DataFrame should have same length"
        assert list(cached_df.columns) == list(
            self.test_df.columns
        ), "Cached DataFrame should have same columns"

        # Test cache statistics through DataService
        stats = self.data_service.get_column_statistics(self.test_df)
        assert isinstance(stats, dict), "Statistics should be returned as dictionary"
        assert "XPos" in stats, "Statistics should include numeric columns"
        assert "min" in stats["XPos"], "Statistics should include min values"
        assert "max" in stats["XPos"], "Statistics should include max values"

        # Cache statistics
        stats_key = f"{cache_key}_stats"
        self.cache_service.set(stats_key, stats)

        # Retrieve cached statistics
        cached_stats = self.cache_service.get(stats_key)
        assert cached_stats is not None, "Statistics should be cacheable"
        assert cached_stats == stats, "Cached statistics should match original"

    def test_file_service_data_service_coordination(self):
        """Test coordination between FileService and DataService."""

        # Create temporary CSV file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as tmp_file:
            self.test_df.to_csv(tmp_file.name, index=False)
            tmp_path = tmp_file.name

        try:
            # Validate file through FileService
            is_valid, error_msg = self.file_service.validate_file(tmp_path)
            assert is_valid, f"File should be valid: {error_msg}"

            # Read file content for DataService
            with open(tmp_path, "r") as f:
                csv_content = f.read()

            # Convert to base64 for upload simulation
            import base64

            csv_bytes = csv_content.encode("utf-8")
            b64_content = base64.b64encode(csv_bytes).decode("ascii")
            upload_content = f"data:text/csv;base64,{b64_content}"

            # Parse through DataService
            df, error_msg, converted = self.data_service.parse_file(upload_content, "test.csv")

            assert df is not None, f"DataFrame should be parsed successfully: {error_msg}"
            assert error_msg is None, "No error should occur during parsing"
            assert not converted, "No unit conversion should occur for this test data"
            assert len(df) == len(self.test_df), "Parsed DataFrame should have correct length"

        finally:
            # Cleanup
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_full_service_chain_file_to_cache(self):
        """Test complete service chain: File → DataService → CacheService."""

        # Create test file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as tmp_file:
            # Add some variation to test filtering
            extended_df = pd.DataFrame(
                {
                    "Date": ["2024-01-15"] * 50,
                    "Time": [f"10:{i//60:02d}:{i%60:02d}.00" for i in range(50)],
                    "XPos": np.random.normal(5, 2, 50),
                    "YPos": np.random.normal(10, 3, 50),
                    "ZPos": np.random.normal(2, 0.5, 50),
                    "SpinVel": np.random.normal(150, 25, 50),
                    "ToolTemp": np.random.normal(200, 30, 50),
                }
            )
            extended_df.to_csv(tmp_file.name, index=False)
            tmp_path = tmp_file.name

        try:
            # Step 1: File validation
            is_valid, error = self.file_service.validate_file(tmp_path)
            assert is_valid, f"File validation failed: {error}"

            # Step 2: File to upload format
            upload_content = MockFileUpload.create_csv_upload(extended_df, "extended_test.csv")

            # Step 3: Parse through DataService
            start_time = time.time()
            df, error_msg, converted = self.data_service.parse_file(
                upload_content, "extended_test.csv"
            )
            parse_time = time.time() - start_time

            assert df is not None, f"Parsing failed: {error_msg}"
            assert parse_time < 2.0, f"Parsing took too long: {parse_time:.2f}s"

            # Step 4: Cache parsed data
            cache_key = "extended_test_data"
            cache_success = self.data_service.cache.cache_dataframe(df, cache_key)
            assert cache_success, "Caching should succeed"

            # Step 5: Generate and cache statistics
            stats = self.data_service.get_column_statistics(df)
            stats_key = f"{cache_key}_statistics"
            self.cache_service.set(stats_key, stats)

            # Step 6: Test filtering with cached data
            filtered_df = self.data_service.filter_by_range(df, "ZPos", 1.5, 2.5)
            assert len(filtered_df) < len(df), "Filtering should reduce data size"
            assert len(filtered_df) > 0, "Filtering should leave some data"

            # Step 7: Cache filtered results
            filtered_key = f"{cache_key}_filtered"
            filter_cache_success = self.data_service.cache.cache_dataframe(
                filtered_df, filtered_key
            )
            assert filter_cache_success, "Filtered data should be cacheable"

            # Step 8: Verify end-to-end retrieval
            retrieved_original = self.cache_service.get_dataframe(cache_key)
            retrieved_filtered = self.cache_service.get_dataframe(filtered_key)
            retrieved_stats = self.cache_service.get(stats_key)

            assert retrieved_original is not None, "Original data should be retrievable"
            assert retrieved_filtered is not None, "Filtered data should be retrievable"
            assert retrieved_stats is not None, "Statistics should be retrievable"

            assert len(retrieved_filtered) < len(
                retrieved_original
            ), "Cache should preserve filtering"

        finally:
            # Cleanup
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_service_error_handling_coordination(self):
        """Test error handling coordination between services."""

        # Test FileService error propagation to DataService
        invalid_content = "data:text/csv;base64,aW52YWxpZA=="  # "invalid" in base64

        df, error_msg, converted = self.data_service.parse_file(invalid_content, "invalid.csv")
        assert df is None, "Invalid file should not produce DataFrame"
        assert error_msg is not None, "Error message should be provided"
        assert not converted, "No conversion should occur on invalid data"

        # Test CacheService error handling
        invalid_cache_key = None
        cache_result = self.cache_service.get(invalid_cache_key)
        assert cache_result is None, "Invalid cache key should return None"

        # Test DataService with corrupted data
        corrupted_df = pd.DataFrame({"invalid": [float("nan")] * 5})
        stats = self.data_service.get_column_statistics(corrupted_df)
        assert isinstance(stats, dict), "Statistics should handle corrupted data gracefully"

    def test_concurrent_service_operations(self):
        """Test concurrent operations across multiple services."""

        # Setup multiple datasets
        datasets = []
        for i in range(3):
            df = pd.DataFrame(
                {
                    "XPos": np.random.rand(100) * (i + 1),
                    "YPos": np.random.rand(100) * (i + 1),
                    "ZPos": np.random.rand(100) * (i + 1),
                    "Value": np.random.rand(100) * 100,
                }
            )
            datasets.append((df, f"dataset_{i}"))

        # Concurrent caching operations
        cache_results = []
        stats_results = []

        start_time = time.time()
        for df, name in datasets:
            # Cache dataset
            cache_success = self.data_service.cache.cache_dataframe(df, name)
            cache_results.append(cache_success)

            # Generate and cache statistics
            stats = self.data_service.get_column_statistics(df)
            stats_key = f"{name}_stats"
            self.cache_service.set(stats_key, stats)
            stats_results.append(stats)

            # Filter and cache filtered data
            filtered_df = self.data_service.filter_by_range(df, "Value", 25, 75)
            filtered_key = f"{name}_filtered"
            self.data_service.cache.cache_dataframe(filtered_df, filtered_key)

        concurrent_time = time.time() - start_time

        # Verify all operations succeeded
        assert all(cache_results), "All caching operations should succeed"
        assert len(stats_results) == 3, "All statistics should be generated"
        assert concurrent_time < 5.0, f"Concurrent operations too slow: {concurrent_time:.2f}s"

        # Verify all cached data is retrievable
        for df, name in datasets:
            cached_original = self.cache_service.get_dataframe(name)
            cached_filtered = self.cache_service.get_dataframe(f"{name}_filtered")
            cached_stats = self.cache_service.get(f"{name}_stats")

            assert cached_original is not None, f"Original data {name} should be cached"
            assert cached_filtered is not None, f"Filtered data {name} should be cached"
            assert cached_stats is not None, f"Statistics {name} should be cached"

    def test_memory_management_across_services(self):
        """Test memory management coordination between services."""

        # Create large dataset
        large_df = pd.DataFrame(
            {
                "XPos": np.random.rand(10000),
                "YPos": np.random.rand(10000),
                "ZPos": np.random.rand(10000),
                "SpinVel": np.random.rand(10000) * 200 + 100,
                "ToolTemp": np.random.rand(10000) * 100 + 150,
            }
        )

        # Test memory-efficient operations
        cache_key = "large_dataset"

        # Cache large dataset
        cache_success = self.data_service.cache.cache_dataframe(large_df, cache_key)
        assert cache_success, "Large dataset should be cacheable"

        # Generate statistics without loading full dataset
        stats = self.data_service.get_column_statistics(large_df)
        assert len(stats) > 0, "Statistics should be generated for large dataset"

        # Filter large dataset efficiently
        filtered_large = self.data_service.filter_by_range(large_df, "ZPos", 0.4, 0.6)
        assert len(filtered_large) < len(large_df), "Filtering should reduce dataset size"
        assert len(filtered_large) > 0, "Filtering should preserve some data"

        # Verify memory cleanup (implicit test - would need memory profiling for explicit)
        del large_df  # Release original reference

        # Cached data should still be accessible
        retrieved_large = self.cache_service.get_dataframe(cache_key)
        assert retrieved_large is not None, "Cached large dataset should remain accessible"

    def test_service_configuration_coordination(self):
        """Test how services coordinate configuration changes."""

        # Test cache timeout configuration
        original_timeout = self.cache_service.default_timeout

        # Simulate configuration update
        new_timeout = original_timeout * 2
        self.cache_service.default_timeout = new_timeout

        # Test that new timeout is used
        test_key = "timeout_test"
        test_data = {"test": "data"}

        # Cache with new timeout
        cache_success = self.cache_service.set(test_key, test_data, timeout=new_timeout)
        assert cache_success, "Caching with new timeout should succeed"

        # Verify retrieval works
        cached_data = self.cache_service.get(test_key)
        assert cached_data == test_data, "Data should be retrievable with new timeout"

        # Reset to original timeout
        self.cache_service.default_timeout = original_timeout

    def test_service_health_check_coordination(self):
        """Test service health check coordination."""

        # Check DataService health
        test_df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        stats = self.data_service.get_column_statistics(test_df)
        assert len(stats) > 0, "DataService should be healthy"

        # Check CacheService health
        health_key = "health_check"
        health_data = {"status": "healthy"}

        cache_success = self.cache_service.set(health_key, health_data)
        assert cache_success, "CacheService should be healthy"

        retrieved_health = self.cache_service.get(health_key)
        assert retrieved_health == health_data, "CacheService should retrieve correctly"

        # Check FileService health
        temp_content = "test,data\n1,2\n"
        upload_content = MockFileUpload.create_csv_upload(
            pd.DataFrame({"test": [1], "data": [2]}), "health_check.csv"
        )

        df, error, converted = self.data_service.parse_file(upload_content, "health_check.csv")
        assert df is not None, "FileService parsing should work"
        assert error is None, "No errors should occur in healthy services"


class TestServiceIntegrationPerformance:
    """Test performance characteristics of service integration."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup performance test environment."""
        self.data_service = DataService()
        self.cache_service = CacheService()

    def test_bulk_caching_performance(self):
        """Test performance of bulk caching operations."""

        # Generate multiple datasets
        datasets = {}
        for i in range(10):
            df = pd.DataFrame(
                {
                    "X": np.random.rand(1000),
                    "Y": np.random.rand(1000),
                    "Z": np.random.rand(1000),
                }
            )
            datasets[f"perf_test_{i}"] = df

        # Time bulk caching
        start_time = time.time()
        for key, df in datasets.items():
            cache_success = self.data_service.cache.cache_dataframe(df, key)
            assert cache_success, f"Caching {key} should succeed"
        caching_time = time.time() - start_time

        # Time bulk retrieval
        start_time = time.time()
        for key in datasets.keys():
            cached_df = self.cache_service.get_dataframe(key)
            assert cached_df is not None, f"Retrieving {key} should succeed"
        retrieval_time = time.time() - start_time

        # Performance assertions
        assert caching_time < 10.0, f"Bulk caching too slow: {caching_time:.2f}s"
        assert retrieval_time < 5.0, f"Bulk retrieval too slow: {retrieval_time:.2f}s"

        # Verify cache efficiency
        cache_ratio = retrieval_time / caching_time
        assert cache_ratio < 0.5, f"Cache should be faster than initial storage: {cache_ratio:.2f}"

    def test_filtering_performance_scaling(self):
        """Test filtering performance with increasing dataset sizes."""

        dataset_sizes = [100, 1000, 5000, 10000]
        filter_times = []

        for size in dataset_sizes:
            # Generate dataset
            df = pd.DataFrame(
                {
                    "XPos": np.random.rand(size) * 100,
                    "YPos": np.random.rand(size) * 100,
                    "ZPos": np.random.rand(size) * 10,
                    "Value": np.random.rand(size) * 1000,
                }
            )

            # Time filtering operation
            start_time = time.time()
            filtered_df = self.data_service.filter_by_range(df, "Value", 250, 750)
            filter_time = time.time() - start_time
            filter_times.append(filter_time)

            # Basic validation
            assert len(filtered_df) <= len(df), "Filtered data should not exceed original"
            assert filter_time < 5.0, f"Filtering {size} rows took too long: {filter_time:.2f}s"

        # Check that filtering scales reasonably (not exponentially)
        # Allow for some variance but ensure it's not completely unreasonable
        for i in range(1, len(filter_times)):
            scale_factor = dataset_sizes[i] / dataset_sizes[i - 1]
            time_ratio = filter_times[i] / filter_times[i - 1]

            # Time ratio should not exceed scale factor squared (quadratic is acceptable upper bound)
            assert (
                time_ratio <= scale_factor**2
            ), f"Filtering performance degraded too much at size {dataset_sizes[i]}"
