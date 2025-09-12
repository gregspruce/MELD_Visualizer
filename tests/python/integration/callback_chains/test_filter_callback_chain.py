"""
Filter Callback Chain Integration Tests
Tests data filtering workflows and graph updating chains.
"""

import time

import numpy as np
import pandas as pd
import pytest

from meld_visualizer.callbacks.enhanced_ui_callbacks import (
    hide_loading_after_processing,
    show_loading_on_upload,
)

# Import callback functions
from meld_visualizer.callbacks.graph_callbacks import (
    update_2d_scatter,
    update_custom_graph,
    update_graph_1,
    update_graph_2,
)

from ..fixtures.dash_app_fixtures import CallbackAssertions


class TestFilterCallbackChain:
    """Test filtering and graph update callback chains."""

    @pytest.fixture(autouse=True)
    def setup(self, callback_tester, mock_services):
        """Setup test environment."""
        self.tester = callback_tester
        self.mock_services = mock_services
        self.assertions = CallbackAssertions()

        # Register callbacks
        self.tester.register_callback("graph_1", update_graph_1)
        self.tester.register_callback("graph_2", update_graph_2)
        self.tester.register_callback("graph_2d", update_2d_scatter)
        self.tester.register_callback("graph_custom", update_custom_graph)
        self.tester.register_callback("loading_show", show_loading_on_upload)
        self.tester.register_callback("loading_hide", hide_loading_after_processing)

        # Setup test data
        self.test_data = pd.DataFrame(
            {
                "XPos": np.linspace(0, 10, 100),
                "YPos": np.linspace(0, 20, 100),
                "ZPos": np.linspace(0, 5, 100),
                "SpinVel": np.linspace(100, 200, 100),
                "ToolTemp": np.linspace(150, 250, 100),
                "Time": pd.date_range("2024-01-01", periods=100, freq="1s"),
                "TimeInSeconds": np.linspace(0, 99, 100),
            }
        )
        self.test_data_json = self.test_data.to_json(orient="split")

    def test_range_filter_chain_workflow(self):
        """Test the complete range filtering workflow across multiple graphs."""

        with self.mock_services.patch_services():
            # Setup filter chain workflow
            filter_workflow = [
                {
                    "callback_id": "graph_1",
                    "inputs": {
                        "jsonified_df": self.test_data_json,
                        "col_chosen": "SpinVel",
                        "slider_range": [2.0, 3.0],  # Z-range filter
                        "config_updated": None,
                    },
                    "output_to_chain_state": "graph_1_result",
                },
                {
                    "callback_id": "graph_2",
                    "inputs": {
                        "jsonified_df": self.test_data_json,
                        "col_chosen": "ToolTemp",
                        "slider_range": [2.0, 3.0],  # Same Z-range filter
                        "config_updated": None,
                    },
                    "output_to_chain_state": "graph_2_result",
                },
                {
                    "callback_id": "graph_2d",
                    "inputs": {
                        "jsonified_df": self.test_data_json,
                        "time_range": [20, 60],  # Time range filter
                        "y_col": "SpinVel",
                        "color_col": "ToolTemp",
                    },
                    "output_to_chain_state": "graph_2d_result",
                },
            ]

            # Execute filter chain
            start_time = time.time()
            results = self.tester.chain_callbacks(filter_workflow)
            execution_time = time.time() - start_time

            # Verify all graphs were generated
            graph_1_result, graph_2_result, graph_2d_result = results

            # Assert all results are valid figures
            self.assertions.assert_figure_valid(graph_1_result)
            self.assertions.assert_figure_valid(graph_2_result)
            self.assertions.assert_figure_valid(graph_2d_result)

            # Verify different color columns produce different graphs
            assert graph_1_result != graph_2_result

            # Performance check
            assert execution_time < 3.0, f"Filter chain too slow: {execution_time:.2f}s"

            # Verify callback chain integrity
            self.assertions.assert_chain_state_valid(self.tester, min_steps=3)

    def test_dynamic_range_updates(self):
        """Test dynamic range slider updates affecting graph rendering."""

        with self.mock_services.patch_services():
            # Test different range combinations
            range_scenarios = [
                ([0, 1], "Lower range"),
                ([2, 3], "Middle range"),
                ([4, 5], "Upper range"),
                ([0, 5], "Full range"),
                ([2.5, 2.6], "Narrow range"),
            ]

            for slider_range, scenario_name in range_scenarios:
                result = self.tester.invoke_callback(
                    "graph_1",
                    {
                        "jsonified_df": self.test_data_json,
                        "col_chosen": "SpinVel",
                        "slider_range": slider_range,
                        "config_updated": None,
                    },
                )

                self.assertions.assert_figure_valid(result)

                # Verify graph data exists (filtered data should produce points)
                if "data" in result and result["data"]:
                    # Should have scatter data
                    assert result["data"][0]["type"] == "scatter3d"

                # Clear history for next iteration
                self.tester.clear_history()

    def test_custom_graph_multi_parameter_filtering(self):
        """Test the custom graph with multiple filter parameters."""

        with self.mock_services.patch_services():
            # Test complex custom graph configuration
            custom_configs = [
                {
                    "x_col": "XPos",
                    "y_col": "YPos",
                    "z_col": "ZPos",
                    "color_col": "SpinVel",
                    "filter_col": "ToolTemp",
                    "filter_range": [150, 200],
                },
                {
                    "x_col": "XPos",
                    "y_col": "ZPos",
                    "z_col": "YPos",
                    "color_col": "ToolTemp",
                    "filter_col": "SpinVel",
                    "filter_range": [120, 180],
                },
                {
                    "x_col": "TimeInSeconds",
                    "y_col": "SpinVel",
                    "z_col": "ToolTemp",
                    "color_col": "XPos",
                    "filter_col": "YPos",
                    "filter_range": [5, 15],
                },
            ]

            for config in custom_configs:
                result = self.tester.invoke_callback(
                    "graph_custom",
                    {
                        "jsonified_df": self.test_data_json,
                        "x_col": config["x_col"],
                        "y_col": config["y_col"],
                        "z_col": config["z_col"],
                        "color_col": config["color_col"],
                        "filter_col": config["filter_col"],
                        "filter_range": config["filter_range"],
                    },
                )

                self.assertions.assert_figure_valid(result)

                # Verify 3D scatter structure
                if "data" in result and result["data"]:
                    scatter_data = result["data"][0]
                    assert scatter_data["type"] == "scatter3d"
                    assert "x" in scatter_data
                    assert "y" in scatter_data
                    assert "z" in scatter_data

                self.tester.clear_history()

    def test_edge_case_filtering(self):
        """Test edge cases in filtering operations."""

        with self.mock_services.patch_services():
            # Test empty filter ranges
            empty_range_result = self.tester.invoke_callback(
                "graph_1",
                {
                    "jsonified_df": self.test_data_json,
                    "col_chosen": "SpinVel",
                    "slider_range": [100, 50],  # Invalid range (min > max)
                    "config_updated": None,
                },
            )

            # Should still return a valid figure (possibly empty)
            self.assertions.assert_figure_valid(empty_range_result)

            # Test extreme ranges
            extreme_range_result = self.tester.invoke_callback(
                "graph_1",
                {
                    "jsonified_df": self.test_data_json,
                    "col_chosen": "SpinVel",
                    "slider_range": [-1000, 1000],  # Far outside data range
                    "config_updated": None,
                },
            )

            self.assertions.assert_figure_valid(extreme_range_result)

            # Test null/None ranges
            null_range_result = self.tester.invoke_callback(
                "graph_1",
                {
                    "jsonified_df": self.test_data_json,
                    "col_chosen": "SpinVel",
                    "slider_range": None,
                    "config_updated": None,
                },
            )

            self.assertions.assert_figure_valid(null_range_result)

    def test_time_series_filtering_chain(self):
        """Test time-based filtering in 2D graphs."""

        with self.mock_services.patch_services():
            # Test different time ranges
            time_scenarios = [
                ([0, 20], "Early time period"),
                ([30, 70], "Middle time period"),
                ([80, 99], "Late time period"),
                ([0, 99], "Full time period"),
            ]

            for time_range, scenario in time_scenarios:
                result = self.tester.invoke_callback(
                    "graph_2d",
                    {
                        "jsonified_df": self.test_data_json,
                        "time_range": time_range,
                        "y_col": "SpinVel",
                        "color_col": "ToolTemp",
                    },
                )

                self.assertions.assert_figure_valid(result)

                # Verify it's a 2D scatter plot
                if "data" in result and result["data"]:
                    assert result["data"][0]["type"] == "scatter"

                self.tester.clear_history()

    def test_concurrent_filter_operations(self):
        """Test multiple graphs updating simultaneously with different filters."""

        with self.mock_services.patch_services():
            # Simulate concurrent graph updates
            concurrent_workflow = [
                {
                    "callback_id": "loading_show",
                    "inputs": {"csv_contents": "new_data", "gcode_contents": None},
                    "output_to_chain_state": "loading_state",
                },
                {
                    "callback_id": "graph_1",
                    "inputs": {
                        "jsonified_df": self.test_data_json,
                        "col_chosen": "SpinVel",
                        "slider_range": [1, 2],
                        "config_updated": None,
                    },
                },
                {
                    "callback_id": "graph_2",
                    "inputs": {
                        "jsonified_df": self.test_data_json,
                        "col_chosen": "ToolTemp",
                        "slider_range": [3, 4],
                        "config_updated": None,
                    },
                },
                {
                    "callback_id": "graph_2d",
                    "inputs": {
                        "jsonified_df": self.test_data_json,
                        "time_range": [10, 50],
                        "y_col": "SpinVel",
                        "color_col": "ToolTemp",
                    },
                },
                {
                    "callback_id": "loading_hide",
                    "inputs": {"main_data": self.test_data_json, "gcode_data": None},
                },
            ]

            # Execute concurrent operations
            start_time = time.time()
            results = self.tester.chain_callbacks(concurrent_workflow)
            execution_time = time.time() - start_time

            # Verify all operations completed successfully
            assert len(results) == 5

            # Check loading states
            loading_start, graph_1, graph_2, graph_2d, loading_end = results
            assert loading_start["show"] is True
            assert loading_end["show"] is False

            # Check all graphs are valid
            self.assertions.assert_figure_valid(graph_1)
            self.assertions.assert_figure_valid(graph_2)
            self.assertions.assert_figure_valid(graph_2d)

            # Performance check for concurrent operations
            assert execution_time < 5.0, f"Concurrent operations too slow: {execution_time:.2f}s"

    def test_filter_error_handling(self):
        """Test error handling in filtering operations."""

        with self.mock_services.patch_services():
            # Test missing columns
            missing_column_result = self.tester.invoke_callback(
                "graph_custom",
                {
                    "jsonified_df": self.test_data_json,
                    "x_col": "NonExistentX",
                    "y_col": "NonExistentY",
                    "z_col": "NonExistentZ",
                    "color_col": "NonExistentColor",
                    "filter_col": "NonExistentFilter",
                    "filter_range": [0, 1],
                },
            )

            # Should return empty figure with error handling
            self.assertions.assert_figure_valid(missing_column_result)

            # Test malformed data
            malformed_data = '{"invalid": "json"}'
            malformed_result = self.tester.invoke_callback(
                "graph_1",
                {
                    "jsonified_df": malformed_data,
                    "col_chosen": "SpinVel",
                    "slider_range": [0, 1],
                    "config_updated": None,
                },
            )

            # Should handle gracefully and return empty figure
            self.assertions.assert_figure_valid(malformed_result)

    def test_performance_with_large_datasets(self):
        """Test filtering performance with large datasets."""

        with self.mock_services.patch_services():
            # Create large dataset
            large_data = pd.DataFrame(
                {
                    "XPos": np.random.rand(10000) * 100,
                    "YPos": np.random.rand(10000) * 100,
                    "ZPos": np.random.rand(10000) * 10,
                    "SpinVel": np.random.rand(10000) * 200 + 100,
                    "ToolTemp": np.random.rand(10000) * 100 + 150,
                    "TimeInSeconds": np.arange(10000),
                }
            )
            large_data_json = large_data.to_json(orient="split")

            # Test filtering performance
            start_time = time.time()
            result = self.tester.invoke_callback(
                "graph_1",
                {
                    "jsonified_df": large_data_json,
                    "col_chosen": "SpinVel",
                    "slider_range": [2, 8],  # Should filter significant portion
                    "config_updated": None,
                },
            )
            processing_time = time.time() - start_time

            # Performance assertion
            assert (
                processing_time < 10.0
            ), f"Large dataset filtering too slow: {processing_time:.2f}s"

            # Verify result is still valid
            self.assertions.assert_figure_valid(result)

    def test_multi_column_filter_combinations(self):
        """Test various column combinations in custom graphs."""

        with self.mock_services.patch_services():
            # Define valid column combinations
            column_combinations = [
                ("XPos", "YPos", "ZPos", "SpinVel", "ToolTemp"),
                ("TimeInSeconds", "XPos", "YPos", "ZPos", "SpinVel"),
                ("XPos", "ZPos", "ToolTemp", "YPos", "SpinVel"),
                ("YPos", "ToolTemp", "XPos", "SpinVel", "ZPos"),
            ]

            for x_col, y_col, z_col, color_col, filter_col in column_combinations:
                result = self.tester.invoke_callback(
                    "graph_custom",
                    {
                        "jsonified_df": self.test_data_json,
                        "x_col": x_col,
                        "y_col": y_col,
                        "z_col": z_col,
                        "color_col": color_col,
                        "filter_col": filter_col,
                        "filter_range": [
                            self.test_data[filter_col].min(),
                            self.test_data[filter_col].max(),
                        ],
                    },
                )

                self.assertions.assert_figure_valid(result)

                # Verify graph has the expected structure
                if "data" in result and result["data"]:
                    scatter_data = result["data"][0]
                    assert scatter_data["type"] == "scatter3d"
                    # Should have data points after filtering
                    assert len(scatter_data.get("x", [])) > 0

                self.tester.clear_history()
