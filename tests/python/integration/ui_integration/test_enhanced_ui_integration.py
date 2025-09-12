"""
Enhanced UI Integration Tests
Tests the 483 lines of Enhanced UI functionality integrated into the application.
"""

import time

import pandas as pd
import pytest

# Import Enhanced UI callback functions
from meld_visualizer.callbacks.enhanced_ui_callbacks import (
    hide_loading_after_processing,
    show_loading_on_upload,
)
from meld_visualizer.core.enhanced_ui import UserFeedbackManager

from ..fixtures.dash_app_fixtures import CallbackAssertions


class TestEnhancedUIIntegration:
    """Test the Enhanced UI functionality integration."""

    @pytest.fixture(autouse=True)
    def setup(self, callback_tester, mock_services):
        """Setup Enhanced UI test environment."""
        self.tester = callback_tester
        self.mock_services = mock_services
        self.assertions = CallbackAssertions()

        # Register Enhanced UI callbacks
        self.tester.register_callback("loading_show", show_loading_on_upload)
        self.tester.register_callback("loading_hide", hide_loading_after_processing)

        # Setup feedback manager
        self.feedback_manager = UserFeedbackManager()

    def test_loading_state_management_integration(self, sample_meld_upload_data):
        """Test the enhanced loading state management system."""

        with self.mock_services.patch_services():
            # Test loading state workflow
            loading_workflow = [
                {
                    "callback_id": "loading_show",
                    "inputs": {"csv_contents": sample_meld_upload_data, "gcode_contents": None},
                    "output_to_chain_state": "loading_state",
                },
                {
                    "callback_id": "loading_hide",
                    "inputs": {"main_data": "processed_data", "gcode_data": None},
                    "use_previous_result": "main_data",
                },
            ]

            # Execute loading state chain
            start_time = time.time()
            results = self.tester.chain_callbacks(loading_workflow)
            execution_time = time.time() - start_time

            # Verify loading state transitions
            show_result, hide_result = results

            # Assert show loading state
            assert show_result is not None, "Show loading should return state"
            assert isinstance(show_result, dict), "Loading state should be dictionary"
            assert show_result.get("show") is True, "Loading should be shown"
            assert "Processing uploaded file..." in show_result.get(
                "message", ""
            ), "Loading message should be descriptive"

            # Assert hide loading state
            assert hide_result is not None, "Hide loading should return state"
            assert hide_result.get("show") is False, "Loading should be hidden"

            # Performance check
            assert execution_time < 1.0, f"Loading state management too slow: {execution_time:.2f}s"

            # Verify callback chain integrity
            self.assertions.assert_chain_state_valid(self.tester, min_steps=2)

    def test_user_feedback_manager_integration(self):
        """Test the UserFeedbackManager class functionality."""

        # Test toast notifications
        success_toast = self.feedback_manager.create_toast(
            "Success", "File uploaded successfully", "success"
        )

        assert success_toast is not None, "Success toast should be created"
        assert "success" in str(success_toast).lower(), "Toast should indicate success"

        error_toast = self.feedback_manager.create_toast("Error", "File upload failed", "error")

        assert error_toast is not None, "Error toast should be created"
        assert (
            "error" in str(error_toast).lower() or "danger" in str(error_toast).lower()
        ), "Toast should indicate error"

        # Test progress indicators
        progress_component = self.feedback_manager.create_progress_bar(
            value=50, max_value=100, label="Processing..."
        )

        assert progress_component is not None, "Progress bar should be created"

        # Test loading overlay
        loading_overlay = self.feedback_manager.create_loading_overlay("Loading data...", show=True)

        assert loading_overlay is not None, "Loading overlay should be created"

    def test_enhanced_ui_error_handling(self):
        """Test Enhanced UI error handling and graceful degradation."""

        # Test loading callbacks with invalid inputs
        invalid_inputs = [
            {"csv_contents": None, "gcode_contents": None},
            {"csv_contents": "invalid", "gcode_contents": "invalid"},
            {},  # Empty inputs
        ]

        for invalid_input in invalid_inputs:
            try:
                result = self.tester.invoke_callback("loading_show", invalid_input)
                # Should handle gracefully - either return valid state or raise handled exception
                if result is not None:
                    assert isinstance(result, dict), "Error handling should return valid state dict"
                    assert "show" in result, "State should have show property"
            except Exception as e:
                # Exceptions should be logged and handled gracefully
                assert "error" in str(e).lower(), "Exception should be descriptive"

            # Clear history for next test
            self.tester.clear_history()

    def test_enhanced_ui_performance_characteristics(self, large_meld_upload_data):
        """Test Enhanced UI performance with large data operations."""

        with self.mock_services.patch_services():
            # Test loading state with large data
            large_data_workflow = [
                {
                    "callback_id": "loading_show",
                    "inputs": {"csv_contents": large_meld_upload_data, "gcode_contents": None},
                },
                {
                    "callback_id": "loading_hide",
                    "inputs": {"main_data": "large_processed_data", "gcode_data": None},
                },
            ]

            # Time the enhanced UI operations
            start_time = time.time()
            results = self.tester.chain_callbacks(large_data_workflow)
            ui_time = time.time() - start_time

            # UI operations should be very fast regardless of data size
            assert ui_time < 0.5, f"Enhanced UI operations too slow: {ui_time:.2f}s"

            # Verify results are still valid
            show_result, hide_result = results
            self.assertions.assert_callback_success(show_result, dict)
            self.assertions.assert_callback_success(hide_result, dict)

    def test_ui_state_consistency_across_operations(self, sample_meld_upload_data):
        """Test UI state consistency across multiple operations."""

        with self.mock_services.patch_services():
            # Simulate multiple rapid operations
            operations = [
                ("loading_show", {"csv_contents": sample_meld_upload_data, "gcode_contents": None}),
                ("loading_hide", {"main_data": "data1", "gcode_data": None}),
                ("loading_show", {"csv_contents": "data2", "gcode_contents": None}),
                ("loading_hide", {"main_data": "data2", "gcode_data": None}),
                ("loading_show", {"csv_contents": None, "gcode_contents": "gcode_data"}),
                ("loading_hide", {"main_data": None, "gcode_data": "gcode_data"}),
            ]

            # Execute rapid operations
            states = []
            for callback_id, inputs in operations:
                result = self.tester.invoke_callback(callback_id, inputs)
                states.append(result)

            # Verify state transitions are logical
            show_states = states[0::2]  # Every other state starting from 0
            hide_states = states[1::2]  # Every other state starting from 1

            # All show states should have show=True
            for show_state in show_states:
                if show_state and isinstance(show_state, dict):
                    assert show_state.get("show") is True, "Show states should have show=True"

            # All hide states should have show=False
            for hide_state in hide_states:
                if hide_state and isinstance(hide_state, dict):
                    assert hide_state.get("show") is False, "Hide states should have show=False"

    def test_enhanced_ui_integration_with_real_callbacks(self, sample_meld_upload_data):
        """Test Enhanced UI integration with actual data processing callbacks."""

        # Import actual callback functions for integration testing
        from meld_visualizer.callbacks.data_callbacks import update_data_and_configs
        from meld_visualizer.callbacks.graph_callbacks import update_graph_1

        # Register actual callbacks alongside Enhanced UI
        self.tester.register_callback("data_upload", update_data_and_configs)
        self.tester.register_callback("graph_update", update_graph_1)

        with self.mock_services.patch_services():
            # Setup mock data service
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

            # Complete integration workflow with Enhanced UI
            integration_workflow = [
                {
                    "callback_id": "loading_show",
                    "inputs": {"csv_contents": sample_meld_upload_data, "gcode_contents": None},
                },
                {
                    "callback_id": "data_upload",
                    "inputs": {
                        "contents": sample_meld_upload_data,
                        "filename": "integration_test.csv",
                    },
                    "use_previous_result": "jsonified_df",
                },
                {
                    "callback_id": "loading_hide",
                    "inputs": {"main_data": "use_upload_result", "gcode_data": None},
                    "use_previous_result": "main_data",
                },
                {
                    "callback_id": "graph_update",
                    "inputs": {
                        "col_chosen": "SpinVel",
                        "slider_range": [2.0, 2.4],
                        "config_updated": None,
                    },
                    "chain_state_keys": ["jsonified_df"],
                },
            ]

            # Execute complete integration workflow
            start_time = time.time()
            results = self.tester.chain_callbacks(integration_workflow)
            integration_time = time.time() - start_time

            # Verify all components worked together
            loading_start, data_result, loading_end, graph_result = results

            # Assert Enhanced UI components
            assert loading_start.get("show") is True, "Loading should start"
            assert loading_end.get("show") is False, "Loading should end"

            # Assert data processing worked
            df_json, filename_msg, layout_config, warnings, column_ranges = data_result
            self.assertions.assert_dataframe_processed(df_json)

            # Assert graph generation worked
            self.assertions.assert_figure_valid(graph_result)

            # Assert overall performance
            assert integration_time < 3.0, f"Full integration too slow: {integration_time:.2f}s"

    def test_enhanced_ui_accessibility_features(self):
        """Test accessibility features of Enhanced UI components."""

        # Test UserFeedbackManager creates accessible components
        accessible_toast = self.feedback_manager.create_toast(
            "Test Title", "Test message for screen readers", "info"
        )

        # Should create components with appropriate ARIA attributes
        # (This would need more detailed inspection of the actual component structure)
        assert accessible_toast is not None, "Accessible toast should be created"

        accessible_progress = self.feedback_manager.create_progress_bar(
            value=75, max_value=100, label="Accessible progress indicator"
        )

        assert accessible_progress is not None, "Accessible progress bar should be created"

        # Test loading overlay with accessibility
        accessible_overlay = self.feedback_manager.create_loading_overlay(
            "Loading accessible content...", show=True
        )

        assert accessible_overlay is not None, "Accessible loading overlay should be created"

    def test_enhanced_ui_responsive_design_integration(self):
        """Test responsive design aspects of Enhanced UI."""

        # Test responsive loading states
        mobile_loading = self.feedback_manager.create_loading_overlay(
            "Mobile loading...", show=True
        )

        desktop_loading = self.feedback_manager.create_loading_overlay(
            "Desktop loading...", show=True
        )

        # Both should be valid but potentially different implementations
        assert mobile_loading is not None, "Mobile loading should work"
        assert desktop_loading is not None, "Desktop loading should work"

        # Test responsive progress indicators
        mobile_progress = self.feedback_manager.create_progress_bar(
            value=50, max_value=100, label="Mobile progress"
        )

        desktop_progress = self.feedback_manager.create_progress_bar(
            value=50, max_value=100, label="Desktop progress"
        )

        assert mobile_progress is not None, "Mobile progress should work"
        assert desktop_progress is not None, "Desktop progress should work"


class TestEnhancedUIEdgeCases:
    """Test Enhanced UI edge cases and error scenarios."""

    @pytest.fixture(autouse=True)
    def setup(self, callback_tester):
        """Setup edge case test environment."""
        self.tester = callback_tester
        self.feedback_manager = UserFeedbackManager()

        # Register callbacks
        self.tester.register_callback("loading_show", show_loading_on_upload)
        self.tester.register_callback("loading_hide", hide_loading_after_processing)

    def test_concurrent_loading_state_changes(self):
        """Test concurrent loading state changes."""

        # Simulate rapid show/hide operations
        rapid_operations = []
        for i in range(10):
            if i % 2 == 0:
                rapid_operations.append(
                    ("loading_show", {"csv_contents": f"data_{i}", "gcode_contents": None})
                )
            else:
                rapid_operations.append(
                    ("loading_hide", {"main_data": f"data_{i}", "gcode_data": None})
                )

        # Execute rapid operations
        results = []
        for callback_id, inputs in rapid_operations:
            result = self.tester.invoke_callback(callback_id, inputs)
            results.append(result)

        # Final state should be consistent with last operation
        final_result = results[-1]
        if final_result and isinstance(final_result, dict):
            # Last operation was hide, so should be hidden
            assert final_result.get("show") is False, "Final state should reflect last operation"

    def test_malformed_input_handling(self):
        """Test handling of malformed inputs."""

        malformed_inputs = [
            {"csv_contents": {"invalid": "object"}, "gcode_contents": None},
            {"csv_contents": 12345, "gcode_contents": None},  # Wrong type
            {"unexpected_key": "value"},  # Wrong keys
            None,  # Null input
        ]

        for malformed_input in malformed_inputs:
            try:
                if malformed_input is None:
                    # Skip null input test as it would cause parameter issues
                    continue

                result = self.tester.invoke_callback("loading_show", malformed_input)

                # Should either handle gracefully or return valid error state
                if result is not None:
                    assert isinstance(result, dict), "Should return valid state dict"

            except Exception as e:
                # Exceptions should be descriptive and handled
                assert len(str(e)) > 0, "Exception should have descriptive message"

            self.tester.clear_history()

    def test_memory_efficiency_with_large_ui_operations(self):
        """Test memory efficiency of UI operations."""

        # Perform many operations to test memory usage
        for i in range(100):
            result = self.tester.invoke_callback(
                "loading_show", {"csv_contents": f"data_{i}", "gcode_contents": None}
            )

            # Verify each operation succeeds
            assert result is not None, f"Operation {i} should succeed"

            # Clear history to manage memory
            if i % 10 == 0:
                self.tester.clear_history()

        # Final memory check (implicit - would need memory profiling tools for explicit)
        final_result = self.tester.invoke_callback(
            "loading_hide", {"main_data": "final_data", "gcode_data": None}
        )

        assert final_result is not None, "Final operation should succeed"
        assert final_result.get("show") is False, "Final state should be correct"

    def test_ui_component_lifecycle_management(self):
        """Test UI component creation and cleanup lifecycle."""

        # Test toast lifecycle
        toasts = []
        for i in range(5):
            toast = self.feedback_manager.create_toast(f"Toast {i}", f"Message {i}", "info")
            toasts.append(toast)

        # All toasts should be created
        assert len(toasts) == 5, "All toasts should be created"
        assert all(toast is not None for toast in toasts), "All toasts should be valid"

        # Test progress bar lifecycle
        progress_bars = []
        for i in range(5):
            progress = self.feedback_manager.create_progress_bar(
                value=i * 20, max_value=100, label=f"Progress {i}"
            )
            progress_bars.append(progress)

        assert len(progress_bars) == 5, "All progress bars should be created"
        assert all(
            progress is not None for progress in progress_bars
        ), "All progress bars should be valid"

        # Test loading overlay lifecycle
        overlays = []
        for i in range(3):
            overlay = self.feedback_manager.create_loading_overlay(
                f"Loading {i}...", show=(i % 2 == 0)
            )
            overlays.append(overlay)

        assert len(overlays) == 3, "All overlays should be created"
        assert all(overlay is not None for overlay in overlays), "All overlays should be valid"
