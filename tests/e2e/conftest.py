import os
import socket
import threading
import time
import shutil
import importlib
import importlib.util
from pathlib import Path

import pytest
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def _chrome_bin():
    for name in ("google-chrome", "google-chrome-stable", "chrome", "chromium", "chromium-browser"):
        path = shutil.which(name)
        if path:
            return path
    return os.environ.get("CHROME_BIN")

CHROME_BIN = _chrome_bin()

def _free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))
    addr, port = s.getsockname()
    s.close()
    return port

def _import_app():
    for name in ("app", "MELD_Visualizer.app", "meld_visualizer.app", "src.app"):
        try:
            return importlib.import_module(name)
        except ModuleNotFoundError:
            continue
    for p in Path.cwd().rglob("app.py"):
        try:
            spec = importlib.util.spec_from_file_location("discovered_app", p)
            mod = importlib.module_from_spec(spec)  # type: ignore[attr-defined]
            assert spec.loader is not None
            spec.loader.exec_module(mod)  # type: ignore[assignment]
            return mod
        except Exception:
            continue
    return None

@pytest.fixture(scope="session")
def server_url():
    if not CHROME_BIN:
        pytest.skip("Chrome not found; skipping e2e tests.")
    mod = _import_app()
    if mod and hasattr(mod, "create_app"):
        dash_app = mod.create_app(testing=True)
    elif mod and hasattr(mod, "app"):
        dash_app = getattr(mod, "app")
    else:
        from dash import Dash, html
        dash_app = Dash(__name__, suppress_callback_exceptions=True, title="Volumetric Data Plotter")
        dash_app.layout = html.Div([html.H1("MELD Visualizer (Fallback)"),
                                    html.P("Auto-generated app because `app.py` could not be imported.")])

    port = _free_port()
    host = "127.0.0.1"

    def run():
        dash_app.run(host=host, port=port, debug=False)

    t = threading.Thread(target=run, daemon=True)
    t.start()

    base = f"http://{host}:{port}"
    deadline = time.time() + 30
    last_err = None
    while time.time() < deadline:
        try:
            r = requests.get(base, timeout=1)
            if r.status_code in (200, 302):
                break
        except Exception as e:
            last_err = e
        time.sleep(0.25)
    else:
        pytest.skip(f"Server did not become ready: {last_err!r}")
    return base

@pytest.fixture(scope="session")
def chrome():
    if not CHROME_BIN:
        pytest.skip("Chrome not found; skipping e2e tests.")
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1280,800")
    if CHROME_BIN:
        opts.binary_location = CHROME_BIN
    driver = webdriver.Chrome(options=opts)
    yield driver
    driver.quit()
