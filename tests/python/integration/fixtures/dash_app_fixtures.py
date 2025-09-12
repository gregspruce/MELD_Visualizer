"""
Enhanced UI Integration Test Fixtures
Provides reusable test components for Dash callback chain integration testing.
"""

import base64
import io
from contextlib import contextmanager
from typing import Any, Dict, List, Optional
from unittest.mock import Mock, patch

import pandas as pd
import pytest


class CallbackChainTester:
    """
    Framework for testing Dash callback chains without browser automation.
    Supports multi-step workflow validation with state capture.
    """

    def __init__(self, app=None):
        """Initialize the callback chain tester."""
        self.app = app
        self.state_history = []
        self.callback_registry = {}

    def register_callback(self, callback_id: str, callback_func):
        """Register a callback function for testing."""
        self.callback_registry[callback_id] = callback_func

    def invoke_callback(
        self, callback_id: str, inputs: Dict[str, Any], states: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Invoke a callback directly with given inputs and states.

        Args:
            callback_id: Identifier for the callback
            inputs: Dictionary of input values
            states: Dictionary of state values

        Returns:
            The callback output(s)
        """
        if callback_id not in self.callback_registry:
            raise ValueError(f"Callback '{callback_id}' not registered")

        callback_func = self.callback_registry[callback_id]

        # Capture state before execution
        pre_state = {
            "inputs": inputs.copy(),
            "states": states.copy() if states else {},
            "timestamp": pd.Timestamp.now(),
        }

        try:
            # Execute callback
            if states:
                result = callback_func(**inputs, **states)
            else:
                result = callback_func(**inputs)

            # Capture state after execution
            post_state = {
                "result": result,
                "success": True,
                "error": None,
                "timestamp": pd.Timestamp.now(),
            }

            self.state_history.append(
                {"callback_id": callback_id, "pre_state": pre_state, "post_state": post_state}
            )

            return result

        except Exception as e:
            # Capture error state
            error_state = {
                "result": None,
                "success": False,
                "error": str(e),
                "timestamp": pd.Timestamp.now(),
            }

            self.state_history.append(
                {"callback_id": callback_id, "pre_state": pre_state, "post_state": error_state}
            )

            raise

    def chain_callbacks(self, callback_sequence: List[Dict[str, Any]]) -> List[Any]:
        """
        Execute a sequence of callbacks, passing outputs as inputs to subsequent callbacks.

        Args:
            callback_sequence: List of callback configurations

        Returns:
            List of results from each callback in the chain
        """
        results = []
        chain_state = {}

        for step in callback_sequence:
            callback_id = step["callback_id"]
            inputs = step.get("inputs", {})
            states = step.get("states", {})

            # Allow referencing previous results
            if "use_previous_result" in step:
                prev_key = step["use_previous_result"]
                if results:
                    inputs[prev_key] = results[-1]

            # Merge chain state
            if "chain_state_keys" in step:
                for key in step["chain_state_keys"]:
                    if key in chain_state:
                        inputs[key] = chain_state[key]

            # Execute callback
            result = self.invoke_callback(callback_id, inputs, states)
            results.append(result)

            # Update chain state
            if "output_to_chain_state" in step:
                chain_state[step["output_to_chain_state"]] = result

        return results

    def get_state_history(self) -> List[Dict[str, Any]]:
        """Get the complete state history."""
        return self.state_history.copy()

    def clear_history(self):
        """Clear the state history."""
        self.state_history.clear()


class MockFileUpload:
    """Mock file upload data for testing."""

    @staticmethod
    def create_csv_upload(data: pd.DataFrame, filename: str = "test_data.csv") -> str:
        """
        Create mock file upload content from DataFrame.

        Args:
            data: DataFrame to convert to upload format
            filename: Name of the file

        Returns:
            Base64 encoded file content in Dash upload format
        """
        csv_string = data.to_csv(index=False)
        csv_bytes = csv_string.encode("utf-8")
        b64_content = base64.b64encode(csv_bytes).decode("ascii")
        return f"data:text/csv;base64,{b64_content}"

    @staticmethod
    def create_invalid_csv_upload(filename: str = "invalid_data.csv") -> str:
        """Create an invalid CSV upload for error testing."""
        invalid_content = "Invalid,CSV,Content\nMissing,Headers"
        csv_bytes = invalid_content.encode("utf-8")
        b64_content = base64.b64encode(csv_bytes).decode("ascii")
        return f"data:text/csv;base64,{b64_content}"

    @staticmethod
    def create_large_csv_upload(rows: int = 10000, filename: str = "large_data.csv") -> str:
        """Create a large CSV upload for performance testing."""
        # Import from conftest or generate inline
        try:
            from pathlib import Path

            conftest_path = Path(__file__).parent.parent / "conftest.py"
            if conftest_path.exists():
                import importlib.util

                spec = importlib.util.spec_from_file_location("conftest", conftest_path)
                conftest = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(conftest)
                large_df = conftest.generate_large_dataframe(rows)
            else:
                # Generate inline if conftest not available
                large_df = MockFileUpload._generate_large_dataframe_inline(rows)
        except Exception:
            # Fallback to inline generation
            large_df = MockFileUpload._generate_large_dataframe_inline(rows)

        return MockFileUpload.create_csv_upload(large_df, filename)

    @staticmethod
    def _generate_large_dataframe_inline(rows: int = 10000) -> pd.DataFrame:
        """Generate large DataFrame inline for testing."""
        import numpy as np

        np.random.seed(42)  # For reproducible tests

        return pd.DataFrame(
            {
                "Date": ["2024-01-15"] * rows,
                "Time": [f"10:{i//60:02d}:{i % 60:02d}.00" for i in range(rows)],
                "SpinVel": np.random.normal(100, 10, rows),
                "XPos": np.random.normal(5, 2, rows),
                "YPos": np.random.normal(10, 3, rows),
                "ZPos": np.random.normal(2, 0.5, rows),
                "ToolTemp": np.random.normal(150, 20, rows),
                "Gcode": np.random.randint(30, 50, rows),
            }
        )


class MockServices:
    """Mock service instances for integration testing."""

    def __init__(self):
        self.data_service = Mock()
        self.cache_service = Mock()
        self.file_service = Mock()

        self._setup_default_behaviors()

    def _setup_default_behaviors(self):
        """Setup default mock behaviors."""
        # Data service defaults
        self.data_service.parse_file.return_value = (
            pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]}),
            None,
            False,
        )
        self.data_service.filter_by_range.side_effect = self._mock_filter_by_range
        self.data_service.get_column_statistics.return_value = {
            "A": {"min": 1, "max": 3, "mean": 2},
            "B": {"min": 4, "max": 6, "mean": 5},
        }

        # Cache service defaults
        self.cache_service.get.return_value = None
        self.cache_service.set.return_value = True
        self.cache_service.cache_dataframe.return_value = True

        # File service defaults
        self.file_service.validate_file.return_value = (True, None)

    def _mock_filter_by_range(self, df: pd.DataFrame, column: str, low: float, high: float):
        """Mock filter by range behavior."""
        if column not in df.columns:
            return pd.DataFrame()
        return df[(df[column] >= low) & (df[column] <= high)]

    @contextmanager
    def patch_services(self):
        """Context manager to patch all services."""
        with patch(
            "meld_visualizer.services.get_data_service", return_value=self.data_service
        ), patch(
            "meld_visualizer.services.get_cache_service", return_value=self.cache_service
        ), patch(
            "meld_visualizer.services.get_file_service", return_value=self.file_service
        ):
            yield self


@pytest.fixture
def callback_tester():
    """Provide CallbackChainTester instance."""
    return CallbackChainTester()


@pytest.fixture
def mock_services():
    """Provide MockServices instance."""
    return MockServices()


@pytest.fixture
def sample_meld_upload_data():
    """Sample MELD data in upload format."""
    data = pd.DataFrame(
        {
            "Date": ["2024-01-15"] * 5,
            "Time": ["10:00:00.00", "10:00:01.00", "10:00:02.00", "10:00:03.00", "10:00:04.00"],
            "SpinVel": [100.0, 101.0, 102.0, 103.0, 104.0],
            "SpinTrq": [5.5, 5.55, 5.6, 5.65, 5.7],
            "SpinPwr": [550.0, 556.55, 571.2, 581.95, 592.8],
            "XPos": [5.0, 5.01, 5.02, 5.03, 5.04],
            "YPos": [10.0, 10.01, 10.02, 10.03, 10.04],
            "ZPos": [2.0, 2.001, 2.002, 2.003, 2.004],
            "ToolTemp": [150.0, 151.0, 152.0, 153.0, 154.0],
            "Gcode": [35, 35, 36, 36, 37],
        }
    )
    return MockFileUpload.create_csv_upload(data, "sample_meld.csv")


@pytest.fixture
def large_meld_upload_data():
    """Large MELD data for performance testing."""
    return MockFileUpload.create_large_csv_upload(5000, "large_meld.csv")


@pytest.fixture
def invalid_upload_data():
    """Invalid upload data for error testing."""
    return MockFileUpload.create_invalid_csv_upload("invalid.csv")


@pytest.fixture
def integration_test_config():
    """Configuration for integration tests."""
    return {
        "performance_thresholds": {
            "callback_execution_time": 2.0,  # seconds
            "memory_usage_mb": 100,  # MB
            "file_processing_time": 5.0,  # seconds
        },
        "test_scenarios": {
            "normal_file_size": 1000,  # rows
            "large_file_size": 10000,  # rows
            "stress_file_size": 50000,  # rows
        },
    }


class CallbackAssertions:
    """Assertion helpers for callback testing."""

    @staticmethod
    def assert_callback_success(result, expected_type=None):
        """Assert callback executed successfully."""
        assert result is not None, "Callback should return a result"
        if expected_type:
            assert isinstance(
                result, expected_type
            ), f"Expected {expected_type}, got {type(result)}"

    @staticmethod
    def assert_figure_valid(figure):
        """Assert Plotly figure is valid."""
        assert isinstance(figure, dict), "Figure should be a dictionary"
        assert "data" in figure or "layout" in figure, "Figure should have data or layout"

    @staticmethod
    def assert_dataframe_processed(df_json):
        """Assert DataFrame was processed correctly."""
        assert df_json is not None, "DataFrame JSON should not be None"
        if df_json:
            df = pd.read_json(io.StringIO(df_json), orient="split")
            assert len(df) > 0, "DataFrame should have data"
            assert len(df.columns) > 0, "DataFrame should have columns"

    @staticmethod
    def assert_chain_state_valid(tester: CallbackChainTester, min_steps: int = 1):
        """Assert callback chain executed properly."""
        history = tester.get_state_history()
        assert len(history) >= min_steps, f"Expected at least {min_steps} callback steps"

        # Check all steps succeeded
        for step in history:
            assert step["post_state"][
                "success"
            ], f"Callback {step['callback_id']} failed: {step['post_state']['error']}"


@pytest.fixture
def callback_assertions():
    """Provide callback assertion helpers."""
    return CallbackAssertions()
