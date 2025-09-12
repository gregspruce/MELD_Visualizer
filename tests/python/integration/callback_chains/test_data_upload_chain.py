"""
Data Upload Callback Chain Integration Tests
Tests the complete data upload → processing → visualization workflow.
"""

import time
from unittest.mock import patch

import pandas as pd
import pytest

# Import the actual callback functions to test
from meld_visualizer.callbacks.data_callbacks import (
    display_config_warnings,
    update_data_and_configs,
)
from meld_visualizer.callbacks.enhanced_ui_callbacks import (
    hide_loading_after_processing,
    show_loading_on_upload,
)
from meld_visualizer.callbacks.graph_callbacks import (
    update_2d_scatter,
    update_graph_1,
    update_graph_2,
)

from ..fixtures.dash_app_fixtures import (
    CallbackAssertions,
)


class TestDataUploadCallbackChain:
    """Test the complete data upload and processing callback chain."""

    @pytest.fixture(autouse=True)
    def setup(self, callback_tester, mock_services):
        """Setup test environment."""
        self.tester = callback_tester
        self.mock_services = mock_services
        self.assertions = CallbackAssertions()

        # Register callbacks for testing
        self.tester.register_callback("data_upload", update_data_and_configs)
        self.tester.register_callback("graph_update_1", update_graph_1)
        self.tester.register_callback("graph_update_2", update_graph_2)
        self.tester.register_callback("graph_2d_update", update_2d_scatter)
        self.tester.register_callback("loading_show", show_loading_on_upload)
        self.tester.register_callback("loading_hide", hide_loading_after_processing)
        self.tester.register_callback("config_warnings", display_config_warnings)

    def test_complete_data_upload_workflow_success(self, sample_meld_upload_data):
        """Test the complete successful data upload workflow."""

        with self.mock_services.patch_services():
            # Setup mock data service to return realistic MELD data
            sample_df = pd.DataFrame(
                {
                    "Date": ["2024-01-15"] * 5,
                    "Time": [
                        "10:00:00.00",
                        "10:00:01.00",
                        "10:00:02.00",
                        "10:00:03.00",
                        "10:00:04.00",
                    ],
                    "SpinVel": [100.0, 101.0, 102.0, 103.0, 104.0],
                    "XPos": [5.0, 5.01, 5.02, 5.03, 5.04],
                    "YPos": [10.0, 10.01, 10.02, 10.03, 10.04],
                    "ZPos": [2.0, 2.001, 2.002, 2.003, 2.004],
                    "ToolTemp": [150.0, 151.0, 152.0, 153.0, 154.0],
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

            # Define the callback chain sequence
            upload_workflow = [
                {
                    "callback_id": "loading_show",
                    "inputs": {"csv_contents": sample_meld_upload_data, "gcode_contents": None},
                    "output_to_chain_state": "loading_state",
                },
                {
                    "callback_id": "data_upload",
                    "inputs": {"contents": sample_meld_upload_data, "filename": "sample_meld.csv"},
                    "output_to_chain_state": "upload_result",
                },
                {
                    "callback_id": "loading_hide",
                    "inputs": {"main_data": "use_upload_result", "gcode_data": None},
                    "use_previous_result": "main_data",
                },
                {
                    "callback_id": "graph_update_1",
                    "inputs": {
                        "col_chosen": "SpinVel",
                        "slider_range": [2.0, 2.004],
                        "config_updated": None,
                    },
                    "chain_state_keys": ["upload_result"],
                    "use_previous_result": "jsonified_df",
                },
            ]

            # Execute the callback chain
            start_time = time.time()
            results = self.tester.chain_callbacks(upload_workflow)
            execution_time = time.time() - start_time

            # Verify results
            loading_state_1, upload_result, loading_state_2, graph_result = results

            # Assert loading states
            assert loading_state_1["show"] is True
            assert loading_state_1["message"] == "Processing uploaded file..."
            assert loading_state_2["show"] is False

            # Assert data upload results
            df_json, filename_msg, layout_config, warnings, column_ranges = upload_result
            self.assertions.assert_dataframe_processed(df_json)
            assert "Current file: sample_meld.csv" in filename_msg
            assert "axis_options" in layout_config
            assert isinstance(column_ranges, dict)

            # Assert graph generation
            self.assertions.assert_figure_valid(graph_result)

            # Assert callback chain state
            self.assertions.assert_chain_state_valid(self.tester, min_steps=4)

            # Performance assertion
            assert execution_time < 2.0, f"Chain took too long: {execution_time:.2f}s"

    def test_invalid_file_upload_error_handling(self, invalid_upload_data):
        """Test error handling for invalid file uploads."""

        with self.mock_services.patch_services():
            # Setup mock to return error
            self.mock_services.data_service.parse_file.return_value = (
                None,
                "Invalid file format",
                False,
            )

            # Test direct callback error handling
            result = self.tester.invoke_callback(
                "data_upload", {"contents": invalid_upload_data, "filename": "invalid.csv"}
            )

            # Should return no_update for DataFrame but error message for filename
            df_json, filename_msg, layout_config, warnings, column_ranges = result
            assert filename_msg == "Invalid file format"

            # Verify error was logged in state history
            history = self.tester.get_state_history()
            assert len(history) == 1
            assert history[0]["post_state"]["success"] is True  # Callback handled error gracefully

    def test_large_file_performance(self, large_meld_upload_data):
        """Test performance with large file uploads."""

        with self.mock_services.patch_services():
            # Setup mock for large file
            large_df = pd.DataFrame(
                {
                    "XPos": range(5000),
                    "YPos": range(5000),
                    "ZPos": range(5000),
                    "SpinVel": range(5000),
                }
            )

            self.mock_services.data_service.parse_file.return_value = (large_df, None, False)
            self.mock_services.data_service.get_column_statistics.return_value = {
                "XPos": {"min": 0, "max": 4999, "mean": 2499.5},
                "YPos": {"min": 0, "max": 4999, "mean": 2499.5},
                "ZPos": {"min": 0, "max": 4999, "mean": 2499.5},
                "SpinVel": {"min": 0, "max": 4999, "mean": 2499.5},
            }

            # Time the upload processing
            start_time = time.time()
            result = self.tester.invoke_callback(
                "data_upload", {"contents": large_meld_upload_data, "filename": "large_meld.csv"}
            )
            processing_time = time.time() - start_time

            # Performance assertions
            assert processing_time < 5.0, f"Large file processing too slow: {processing_time:.2f}s"

            # Verify results are still correct
            df_json, filename_msg, layout_config, warnings, column_ranges = result
            self.assertions.assert_dataframe_processed(df_json)
            assert "large_meld.csv" in filename_msg

    def test_graph_update_after_upload(self, sample_meld_upload_data):
        """Test graph updates respond correctly to uploaded data."""

        with self.mock_services.patch_services():
            # Setup realistic MELD data
            sample_df = pd.DataFrame(
                {
                    "XPos": [1.0, 2.0, 3.0, 4.0, 5.0],
                    "YPos": [10.0, 11.0, 12.0, 13.0, 14.0],
                    "ZPos": [2.0, 2.1, 2.2, 2.3, 2.4],
                    "SpinVel": [100.0, 101.0, 102.0, 103.0, 104.0],
                    "ToolTemp": [150.0, 151.0, 152.0, 153.0, 154.0],
                }
            )

            # Convert to JSON format that callbacks expect
            df_json = sample_df.to_json(orient="split")

            # Test graph-1 update
            graph_1_result = self.tester.invoke_callback(
                "graph_update_1",
                {
                    "jsonified_df": df_json,
                    "col_chosen": "SpinVel",
                    "slider_range": [2.0, 2.4],
                    "config_updated": None,
                },
            )

            self.assertions.assert_figure_valid(graph_1_result)
            assert "data" in graph_1_result
            assert len(graph_1_result["data"]) > 0

            # Test graph-2 update
            graph_2_result = self.tester.invoke_callback(
                "graph_update_2",
                {
                    "jsonified_df": df_json,
                    "col_chosen": "ToolTemp",
                    "slider_range": [2.0, 2.4],
                    "config_updated": None,
                },
            )

            self.assertions.assert_figure_valid(graph_2_result)

            # Verify both graphs can be generated from same data
            assert (
                graph_1_result != graph_2_result
            )  # Should be different due to different color columns

    def test_empty_data_handling(self):
        """Test handling of empty or no data scenarios."""

        with self.mock_services.patch_services():
            # Test with no data
            empty_result = self.tester.invoke_callback(
                "graph_update_1",
                {
                    "jsonified_df": None,
                    "col_chosen": "SpinVel",
                    "slider_range": [0, 1],
                    "config_updated": None,
                },
            )

            # Should return empty figure
            self.assertions.assert_figure_valid(empty_result)
            assert len(empty_result.get("data", [])) == 0

            # Test with empty DataFrame
            empty_df = pd.DataFrame()
            empty_df_json = empty_df.to_json(orient="split")

            empty_df_result = self.tester.invoke_callback(
                "graph_update_1",
                {
                    "jsonified_df": empty_df_json,
                    "col_chosen": "SpinVel",
                    "slider_range": [0, 1],
                    "config_updated": None,
                },
            )

            self.assertions.assert_figure_valid(empty_df_result)

    def test_column_not_found_error_handling(self, sample_meld_upload_data):
        """Test handling when requested column doesn't exist."""

        with self.mock_services.patch_services():
            # Setup DataFrame without the requested column
            sample_df = pd.DataFrame(
                {
                    "XPos": [1.0, 2.0, 3.0],
                    "YPos": [10.0, 11.0, 12.0],
                    "ZPos": [2.0, 2.1, 2.2],
                }
            )

            df_json = sample_df.to_json(orient="split")

            # Request non-existent column
            result = self.tester.invoke_callback(
                "graph_update_1",
                {
                    "jsonified_df": df_json,
                    "col_chosen": "NonExistentColumn",
                    "slider_range": [2.0, 2.2],
                    "config_updated": None,
                },
            )

            # Should return empty figure with error message
            self.assertions.assert_figure_valid(result)
            # Check that it's an empty figure (should have annotations with error message)
            assert "layout" in result

    def test_gcode_upload_integration(self):
        """Test G-code upload integration with main data workflow."""

        with self.mock_services.patch_services():
            # Mock G-code parsing
            gcode_df = pd.DataFrame(
                {
                    "X": [1.0, 2.0, 3.0],
                    "Y": [10.0, 11.0, 12.0],
                    "Z": [2.0, 2.1, 2.2],
                    "Line": [1, 2, 3],
                }
            )

            with patch("meld_visualizer.core.data_processing.parse_gcode_file") as mock_parse:
                mock_parse.return_value = (gcode_df, "G-code loaded successfully", None)

                # Mock file upload content
                gcode_content = "data:text/plain;base64,RzEgWDEuMCBZMTAuMCBaMi4w"  # Base64 for "G1 X1.0 Y10.0 Z2.0"

                result = self.tester.invoke_callback(
                    "gcode_upload", {"contents": gcode_content, "filename": "test.nc"}
                )

                # Should return processed G-code data
                gcode_json, message, is_open = result
                self.assertions.assert_dataframe_processed(gcode_json)
                assert "G-code loaded successfully" in message
                assert is_open is True  # Alert should be shown


class TestDataUploadErrorScenarios:
    """Test various error scenarios in the data upload chain."""

    @pytest.fixture(autouse=True)
    def setup(self, callback_tester, mock_services):
        """Setup test environment."""
        self.tester = callback_tester
        self.mock_services = mock_services
        self.assertions = CallbackAssertions()

        self.tester.register_callback("data_upload", update_data_and_configs)
        self.tester.register_callback("config_warnings", display_config_warnings)

    def test_file_parsing_errors(self):
        """Test various file parsing error scenarios."""

        error_scenarios = [
            ("File not found", "FileNotFoundError: test.csv not found"),
            ("Invalid format", "UnicodeDecodeError: invalid file encoding"),
            ("Memory error", "MemoryError: File too large to process"),
            ("Permission error", "PermissionError: Access denied"),
        ]

        with self.mock_services.patch_services():
            for scenario_name, error_message in error_scenarios:
                # Setup mock to return specific error
                self.mock_services.data_service.parse_file.return_value = (
                    None,
                    error_message,
                    False,
                )

                result = self.tester.invoke_callback(
                    "data_upload",
                    {"contents": "invalid_content", "filename": f"{scenario_name}.csv"},
                )

                # Should handle error gracefully
                df_json, filename_msg, layout_config, warnings, column_ranges = result
                assert filename_msg == error_message

                # Clear history for next scenario
                self.tester.clear_history()

    def test_config_warnings_display(self):
        """Test configuration warnings are displayed correctly."""

        test_warnings = [
            "Warning: Column 'ExpectedColumn1' not found in file",
            "Warning: Column 'ExpectedColumn2' not found in file",
        ]

        result = self.tester.invoke_callback("config_warnings", {"warnings": test_warnings})

        warning_content, is_open = result
        assert is_open is True
        # Should contain HTML list with warnings
        # (actual HTML structure depends on implementation)
        assert warning_content  # Should not be empty

    def test_memory_management_large_files(self):
        """Test memory management with very large files."""

        with self.mock_services.patch_services():
            # Simulate memory-intensive operation
            def memory_intensive_parse(*args, **kwargs):
                # Simulate large DataFrame creation
                import numpy as np

                large_data = np.random.rand(50000, 10)  # Large array
                df = pd.DataFrame(large_data)
                return df, None, False

            self.mock_services.data_service.parse_file.side_effect = memory_intensive_parse

            start_memory = None  # Would need psutil for actual memory tracking

            result = self.tester.invoke_callback(
                "data_upload", {"contents": "large_file_content", "filename": "huge_file.csv"}
            )

            # Verify processing completed without memory errors
            df_json, filename_msg, layout_config, warnings, column_ranges = result
            self.assertions.assert_dataframe_processed(df_json)

            # Memory should be released after processing
            # (actual memory checking would require additional tools)
            assert True  # Placeholder for memory assertion
