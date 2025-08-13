import importlib.util
import pytest

MODULES = ["app", "layout", "callbacks", "data_processing", "config"]

@pytest.mark.parametrize("name", MODULES)
def test_module_imports_if_present(name):
    # Only enforce import for modules that actually exist in the repo
    if importlib.util.find_spec(name) is None:
        pytest.skip(f"Optional module '{name}' not found; skipping import check.")
    __import__(name)
