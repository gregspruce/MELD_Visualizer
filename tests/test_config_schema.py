import json
from pathlib import Path
import pytest

def test_config_json_parses_if_present():
    p = Path("config.json")
    if not p.exists():
        pytest.skip("config.json not present; skipping schema check.")
    data = json.loads(p.read_text(encoding="utf-8"))
    assert isinstance(data, dict), "config.json must be a JSON object"
