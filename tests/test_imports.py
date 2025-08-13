import importlib.util
import pytest

MODULES = ["app", "layout", "callbacks", "data_processing", "config"]

@pytest.mark.parametrize("name", MODULES)
def test_module_imports_if_present(name):
    if importlib.util.find_spec(name) is None:
        pytest.skip(f"Optional module '{name}' not found; skipping import check.")
    __import__(name)
