import importlib.util
import pytest

# Update module paths for new package structure
MODULES = [
    "src.meld_visualizer.app",
    "src.meld_visualizer.core.layout", 
    "src.meld_visualizer.callbacks",
    "src.meld_visualizer.core.data_processing",
    "src.meld_visualizer.config"
]

@pytest.mark.parametrize("name", MODULES)
def test_module_imports_if_present(name):
    if importlib.util.find_spec(name) is None:
        pytest.skip(f"Optional module '{name}' not found; skipping import check.")
    __import__(name)
