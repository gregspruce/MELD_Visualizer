"""
Basic Integration Test
Simple test to validate the integration test framework works correctly.
"""

import time

import pandas as pd
import pytest

from meld_visualizer.callbacks.data_callbacks import update_data_and_configs

# Import callback functions for testing
from meld_visualizer.callbacks.graph_callbacks import create_empty_figure

from .fixtures.dash_app_fixtures import (
    CallbackAssertions,
    MockFileUpload,
)


class TestBasicIntegration:
    """Basic integration tests to validate the framework."""

    @pytest.fixture(autouse=True)
    def setup(self, callback_tester, mock_services):
        """Setup basic test environment."""
        self.tester = callback_tester
        self.mock_services = mock_services
        self.assertions = CallbackAssertions()

    def test_callback_tester_framework(self):
        """Test that the CallbackChainTester framework works correctly."""

        # Define a simple test callback
        def simple_callback(input_value):
            return f"processed_{input_value}"

        # Register the callback
        self.tester.register_callback("simple_test", simple_callback)

        # Invoke the callback
        result = self.tester.invoke_callback("simple_test", {"input_value": "test_data"})

        # Verify result
        assert result == "processed_test_data", "Simple callback should work"

        # Verify state history
        history = self.tester.get_state_history()
        assert len(history) == 1, "Should have one history entry"
        assert history[0]["post_state"]["success"] is True, "Callback should succeed"
        assert (
            history[0]["post_state"]["result"] == "processed_test_data"
        ), "Result should be recorded"

    def test_mock_services_framework(self):
        """Test that the MockServices framework works correctly."""

        with self.mock_services.patch_services():
            # Test data service mock
            test_df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
            upload_content = MockFileUpload.create_csv_upload(test_df, "test.csv")

            # Use the mock data service
            df, error, converted = self.mock_services.data_service.parse_file(
                upload_content, "test.csv"
            )

            assert df is not None, "Mock data service should return DataFrame"
            assert error is None, "Mock should not return errors by default"
            assert not converted, "Mock should not indicate conversion by default"

            # Test cache service mock
            cache_success = self.mock_services.cache_service.set("test_key", "test_value")
            assert cache_success is True, "Mock cache should succeed"

            cached_value = self.mock_services.cache_service.get("test_key")
            # Mock returns None by default, which is expected behavior
            assert cached_value is None, "Mock cache returns None by default (as expected)"

    def test_callback_assertions_framework(self):
        """Test that the CallbackAssertions framework works correctly."""

        # Test successful callback assertion
        test_result = {"key": "value"}
        self.assertions.assert_callback_success(test_result, dict)

        # Test figure validation
        test_figure = {"data": [{"x": [1, 2, 3], "y": [4, 5, 6]}], "layout": {"title": "Test"}}
        self.assertions.assert_figure_valid(test_figure)

        # Test DataFrame processing assertion
        test_df = pd.DataFrame({"A": [1, 2, 3]})
        df_json = test_df.to_json(orient="split")
        self.assertions.assert_dataframe_processed(df_json)

        # All assertions should pass without exception
        assert True, "All assertions completed successfully"

    def test_data_upload_callback_integration(self, sample_meld_upload_data):
        """Test integration with actual data upload callback."""

        # Register the actual data upload callback
        self.tester.register_callback("data_upload", update_data_and_configs)

        with self.mock_services.patch_services():
            # Setup mock to return realistic data
            sample_df = pd.DataFrame(
                {
                    "XPos": [1, 2, 3, 4, 5],
                    "YPos": [10, 11, 12, 13, 14],
                    "ZPos": [2.0, 2.1, 2.2, 2.3, 2.4],
                    "SpinVel": [100, 101, 102, 103, 104],
                }
            )

            self.mock_services.data_service.parse_file.return_value = (sample_df, None, False)
            self.mock_services.data_service.get_column_statistics.return_value = {
                col: {
                    "min": sample_df[col].min(),
                    "max": sample_df[col].max(),
                    "mean": sample_df[col].mean(),
                }
                for col in sample_df.select_dtypes(include=["number"]).columns
            }

            # Time the callback execution
            start_time = time.time()
            result = self.tester.invoke_callback(
                "data_upload",
                {"contents": sample_meld_upload_data, "filename": "test_integration.csv"},
            )
            execution_time = time.time() - start_time

            # Verify result structure
            assert len(result) == 5, "Data upload callback should return 5 values"
            df_json, filename_msg, layout_config, warnings, column_ranges = result

            # Use assertion helpers
            self.assertions.assert_dataframe_processed(df_json)
            assert "test_integration.csv" in filename_msg, "Filename should be in message"
            assert isinstance(layout_config, dict), "Layout config should be dict"
            assert isinstance(column_ranges, dict), "Column ranges should be dict"

            # Performance check
            assert execution_time < 2.0, f"Callback execution too slow: {execution_time:.2f}s"

            # Verify callback chain state
            self.assertions.assert_chain_state_valid(self.tester, min_steps=1)

    def test_graph_callback_integration(self):
        """Test integration with graph callback functions."""

        # Test the create_empty_figure function
        empty_fig = create_empty_figure("Test message")
        self.assertions.assert_figure_valid(empty_fig)

        # Verify the figure structure
        assert "layout" in empty_fig, "Empty figure should have layout"
        assert "annotations" in empty_fig["layout"], "Empty figure should have annotations"

        # Test with custom message
        custom_fig = create_empty_figure("Custom test message")
        self.assertions.assert_figure_valid(custom_fig)
        assert custom_fig != empty_fig, "Different messages should produce different figures"

    def test_mock_file_upload_utilities(self):
        """Test the MockFileUpload utility functions."""

        # Test CSV upload creation
        test_data = pd.DataFrame(
            {"col1": [1, 2, 3], "col2": ["a", "b", "c"], "col3": [1.1, 2.2, 3.3]}
        )

        upload_content = MockFileUpload.create_csv_upload(test_data, "test.csv")

        # Verify upload format
        assert upload_content.startswith(
            "data:text/csv;base64,"
        ), "Upload should be base64 CSV format"

        # Test invalid CSV upload
        invalid_upload = MockFileUpload.create_invalid_csv_upload("invalid.csv")
        assert invalid_upload.startswith(
            "data:text/csv;base64,"
        ), "Invalid upload should still be properly formatted"

        # Test large CSV upload
        large_upload = MockFileUpload.create_large_csv_upload(100, "large.csv")
        assert large_upload.startswith(
            "data:text/csv;base64,"
        ), "Large upload should be properly formatted"

        # Large upload should be significantly longer than small upload
        assert len(large_upload) > len(upload_content), "Large upload should be larger"

    def test_performance_characteristics(self):
        """Test performance characteristics of the integration framework."""

        # Test many callback registrations
        callbacks = {}
        for i in range(100):

            def make_callback(num):
                return lambda x: f"result_{num}_{x}"

            callback_name = f"callback_{i}"
            self.tester.register_callback(callback_name, make_callback(i))
            callbacks[callback_name] = make_callback(i)

        # Verify all callbacks were registered
        assert len(self.tester.callback_registry) == 100, "Should have 100 registered callbacks"

        # Test rapid callback execution
        start_time = time.time()
        for i in range(10):  # Test subset for performance
            callback_name = f"callback_{i}"
            result = self.tester.invoke_callback(callback_name, {"x": "test"})
            assert result == f"result_{i}_test", f"Callback {i} should work correctly"

        execution_time = time.time() - start_time

        # Performance assertion
        assert execution_time < 1.0, f"Rapid callback execution too slow: {execution_time:.2f}s"

        # Verify history management
        assert len(self.tester.get_state_history()) == 10, "Should have 10 history entries"

        # Test history clearing
        self.tester.clear_history()
        assert len(self.tester.get_state_history()) == 0, "History should be cleared"


class TestIntegrationErrorHandling:
    """Test error handling in the integration framework."""

    @pytest.fixture(autouse=True)
    def setup(self, callback_tester):
        """Setup error handling test environment."""
        self.tester = callback_tester
        self.assertions = CallbackAssertions()

    def test_callback_error_handling(self):
        """Test callback error handling and recording."""

        # Define a callback that raises an exception
        def error_callback(input_value):
            if input_value == "error":
                raise ValueError("Test error")
            return f"success_{input_value}"

        # Register the callback
        self.tester.register_callback("error_test", error_callback)

        # Test successful execution
        success_result = self.tester.invoke_callback("error_test", {"input_value": "success"})
        assert success_result == "success_success", "Successful callback should work"

        # Test error handling
        with pytest.raises(ValueError, match="Test error"):
            self.tester.invoke_callback("error_test", {"input_value": "error"})

        # Verify error was recorded in history
        history = self.tester.get_state_history()
        assert len(history) == 2, "Should have two history entries"

        success_entry = history[0]
        error_entry = history[1]

        assert (
            success_entry["post_state"]["success"] is True
        ), "Success entry should be marked successful"
        assert error_entry["post_state"]["success"] is False, "Error entry should be marked failed"
        assert (
            "Test error" in error_entry["post_state"]["error"]
        ), "Error message should be recorded"

    def test_unregistered_callback_error(self):
        """Test error handling for unregistered callbacks."""

        with pytest.raises(ValueError, match="Callback 'nonexistent' not registered"):
            self.tester.invoke_callback("nonexistent", {"input": "value"})

    def test_assertion_error_handling(self):
        """Test assertion error handling."""

        # Test assertion failures
        with pytest.raises(AssertionError):
            self.assertions.assert_callback_success(None)

        with pytest.raises(AssertionError):
            self.assertions.assert_figure_valid({})  # Empty dict without required keys

        with pytest.raises(AssertionError):
            self.assertions.assert_dataframe_processed(None)

        with pytest.raises(AssertionError):
            self.assertions.assert_chain_state_valid(self.tester, min_steps=1)  # No history entries
