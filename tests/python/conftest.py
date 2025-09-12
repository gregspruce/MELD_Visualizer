"""
PyTest configuration for MELD Visualizer Python unit tests.
Contains fixtures and shared test utilities.
"""

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import numpy as np
import pandas as pd
import pytest

# Add the source directory to Python path for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

# Test data directory
TEST_DATA_DIR = Path(__file__).parent.parent / "playwright" / "fixtures" / "test_data"


@pytest.fixture(scope="session")
def test_data_dir():
    """Provide path to test data directory"""
    return TEST_DATA_DIR


@pytest.fixture
def sample_meld_csv_path(test_data_dir):
    """Path to sample MELD CSV file"""
    return test_data_dir / "sample_meld_data.csv"


@pytest.fixture
def minimal_meld_csv_path(test_data_dir):
    """Path to minimal MELD CSV file"""
    return test_data_dir / "minimal_meld_data.csv"


@pytest.fixture
def invalid_meld_csv_path(test_data_dir):
    """Path to invalid MELD CSV file for error testing"""
    return test_data_dir / "invalid_meld_data.csv"


@pytest.fixture
def sample_gcode_path(test_data_dir):
    """Path to sample G-code file"""
    return test_data_dir / "sample_toolpath.nc"


@pytest.fixture
def sample_meld_dataframe():
    """Create a sample MELD DataFrame for testing"""
    data = {
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
    return pd.DataFrame(data)


@pytest.fixture
def empty_dataframe():
    """Create an empty DataFrame with MELD columns"""
    columns = [
        "Date",
        "Time",
        "SpinVel",
        "SpinTrq",
        "SpinPwr",
        "XPos",
        "YPos",
        "ZPos",
        "ToolTemp",
        "Gcode",
    ]
    return pd.DataFrame(columns=columns)


@pytest.fixture
def mock_plotly_figure():
    """Create a mock Plotly figure object"""
    return {
        "data": [
            {
                "x": [1, 2, 3, 4, 5],
                "y": [1, 4, 9, 16, 25],
                "z": [1, 8, 27, 64, 125],
                "type": "scatter3d",
                "mode": "markers",
            }
        ],
        "layout": {
            "title": "Test 3D Plot",
            "scene": {
                "xaxis": {"title": "X Position"},
                "yaxis": {"title": "Y Position"},
                "zaxis": {"title": "Z Position"},
            },
        },
    }


@pytest.fixture
def temp_csv_file():
    """Create a temporary CSV file for testing"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("Date,Time,SpinVel,XPos,YPos,ZPos\n")
        f.write("2024-01-15,10:00:00.00,100.0,5.0,10.0,2.0\n")
        f.write("2024-01-15,10:00:01.00,101.0,5.1,10.1,2.1\n")
        temp_path = f.name

    yield temp_path

    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def temp_config_file():
    """Create a temporary config file for testing"""
    config_data = {
        "default_theme": "BOOTSTRAP",
        "max_file_size_mb": 100,
        "cache_timeout": 300,
        "debug_mode": False,
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(config_data, f)
        temp_path = f.name

    yield temp_path

    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def mock_dash_app():
    """Create a mock Dash app for testing"""
    from unittest.mock import Mock

    app = Mock()
    app.server = Mock()
    app.layout = Mock()
    app.callback = Mock()
    app.run = Mock()

    return app


@pytest.fixture
def mock_file_upload():
    """Mock file upload contents"""
    return {
        "contents": "data:text/csv;base64,VGVzdCBjb250ZW50",
        "filename": "test_data.csv",
        "last_modified": 1642234800000,
    }


@pytest.fixture(autouse=True)
def reset_caches():
    """Reset any module-level caches between tests"""
    # Clear any import caches or module state
    yield
    # Cleanup after test


@pytest.fixture
def capture_logs(caplog):
    """Capture logs during testing"""
    import logging

    caplog.set_level(logging.DEBUG)
    return caplog


# Performance testing fixtures
@pytest.fixture
def performance_threshold():
    """Performance thresholds for testing"""
    return {
        "csv_load_time": 5.0,  # seconds
        "graph_render_time": 2.0,  # seconds
        "memory_usage_mb": 500,  # MB
        "file_size_limit_mb": 100,  # MB
    }


# Mock external dependencies
@pytest.fixture
def mock_pandas_read_csv():
    """Mock pandas read_csv function"""
    with patch("pandas.read_csv") as mock:
        yield mock


@pytest.fixture
def mock_plotly_express():
    """Mock plotly express functions"""
    with patch("plotly.express.scatter_3d") as mock:
        mock.return_value = {"data": [], "layout": {}}
        yield mock


@pytest.fixture
def mock_cache_service():
    """Mock cache service"""
    cache_mock = Mock()
    cache_mock.get.return_value = None
    cache_mock.set.return_value = True
    cache_mock.clear.return_value = True
    return cache_mock


# Database/Storage mocks for future expansion
@pytest.fixture
def mock_database():
    """Mock database connection for future use"""
    db_mock = Mock()
    db_mock.connect.return_value = True
    db_mock.execute.return_value = []
    db_mock.close.return_value = True
    return db_mock


# Error simulation fixtures
@pytest.fixture
def simulate_file_not_found():
    """Simulate FileNotFoundError"""

    def _simulate_error(*args, **kwargs):
        raise FileNotFoundError("Test file not found")

    return _simulate_error


@pytest.fixture
def simulate_memory_error():
    """Simulate MemoryError for large file testing"""

    def _simulate_error(*args, **kwargs):
        raise MemoryError("Insufficient memory for operation")

    return _simulate_error


@pytest.fixture
def simulate_permission_error():
    """Simulate PermissionError"""

    def _simulate_error(*args, **kwargs):
        raise PermissionError("Permission denied")

    return _simulate_error


# Test data generators
def generate_large_dataframe(rows=10000):
    """Generate a large DataFrame for performance testing"""
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


@pytest.fixture
def large_dataframe():
    """Provide large DataFrame for performance testing"""
    return generate_large_dataframe()


# Parametrized fixtures for testing different scenarios
@pytest.fixture(params=["bootstrap", "flatly", "darkly"])
def theme_name(request):
    """Parametrized fixture for different theme names"""
    return request.param


@pytest.fixture(params=[100, 1000, 10000])
def dataframe_size(request):
    """Parametrized fixture for different DataFrame sizes"""
    return generate_large_dataframe(rows=request.param)


# Cleanup utilities
def cleanup_test_files():
    """Clean up any test files created during testing"""
    test_output_dir = Path(__file__).parent.parent / "reports" / "test_outputs"
    if test_output_dir.exists():
        for file in test_output_dir.glob("test_*"):
            file.unlink()


@pytest.fixture(scope="session", autouse=True)
def cleanup_after_tests():
    """Clean up after all tests complete"""
    yield
    cleanup_test_files()
