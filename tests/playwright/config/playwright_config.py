"""
Playwright MCP Configuration for MELD Visualizer Testing
=========================================================
This module provides configuration settings for all Playwright-based tests.
"""

import os
from typing import Dict, List, Optional


class PlaywrightConfig:
    """Configuration for Playwright MCP tests."""
    
    # Application settings
    BASE_URL: str = os.getenv("TEST_BASE_URL", "http://localhost:8050")
    APP_TITLE: str = "MELD Visualizer"
    
    # Browser settings
    DEFAULT_BROWSER: str = "chromium"  # chromium, firefox, webkit
    HEADLESS: bool = os.getenv("HEADLESS", "false").lower() == "true"
    SLOW_MO: int = int(os.getenv("SLOW_MO", "0"))  # Milliseconds between actions
    
    # Viewport settings
    VIEWPORT_WIDTH: int = 1280
    VIEWPORT_HEIGHT: int = 720
    MOBILE_WIDTH: int = 375
    MOBILE_HEIGHT: int = 667
    
    # Timeout settings (in milliseconds)
    DEFAULT_TIMEOUT: int = 30000  # 30 seconds
    NAVIGATION_TIMEOUT: int = 60000  # 60 seconds
    FILE_UPLOAD_TIMEOUT: int = 120000  # 2 minutes for large files
    GRAPH_RENDER_TIMEOUT: int = 45000  # 45 seconds for 3D graphs
    
    # Screenshot settings
    SCREENSHOT_PATH: str = "tests/screenshots"
    SCREENSHOT_FULL_PAGE: bool = True
    SCREENSHOT_FORMAT: str = "png"  # png or jpeg
    
    # Test data paths
    TEST_DATA_PATH: str = "tests/playwright/fixtures/test_data"
    SAMPLE_CSV: str = "sample_meld_data.csv"
    SAMPLE_NC: str = "sample_gcode.nc"
    LARGE_DATASET: str = "large_meld_data.csv"
    
    # Visual regression settings
    VISUAL_THRESHOLD: float = 0.95  # 95% similarity threshold
    BASELINE_PATH: str = "tests/playwright/visual/baselines"
    DIFF_PATH: str = "tests/playwright/visual/diffs"
    
    # Network settings
    OFFLINE_MODE: bool = False
    THROTTLE_NETWORK: Optional[str] = None  # "slow-3g", "fast-3g", etc.
    
    # Parallel execution
    PARALLEL_WORKERS: int = int(os.getenv("PARALLEL_WORKERS", "3"))
    
    # Retry settings
    MAX_RETRIES: int = 2
    RETRY_DELAY: int = 1000  # 1 second between retries
    
    # Console monitoring
    MONITOR_CONSOLE: bool = True
    FAIL_ON_CONSOLE_ERROR: bool = True
    IGNORED_CONSOLE_MESSAGES: List[str] = [
        "Download the React DevTools",
        "Deprecation warning",
    ]
    
    # Selectors for common elements
    SELECTORS: Dict[str, str] = {
        # File upload
        "upload_button": "#upload-data",
        "upload_input": "input[type='file']",
        "upload_success": ".upload-success-message",
        
        # Navigation
        "tab_3d": "#controlled-tab-3d",
        "tab_2d": "#controlled-tab-2d",
        "tab_volume": "#controlled-tab-volume",
        "tab_overlap": "#controlled-tab-overlap",
        
        # Theme selector
        "theme_dropdown": "#theme-selector",
        "theme_option": ".theme-option",
        
        # Graph controls
        "graph_3d": "#3d-scatter-plot",
        "graph_2d": "#2d-line-plot",
        "graph_volume": "#volume-mesh-plot",
        
        # Control panel
        "velocity_min": "#velocity-min-input",
        "velocity_max": "#velocity-max-input",
        "position_slider": "#position-range-slider",
        "update_button": "#update-graph-button",
        
        # Export
        "export_button": "#export-button",
        "export_html": "#export-html",
        "export_csv": "#export-csv",
        
        # Loading indicators
        "loading_spinner": ".dash-spinner",
        "loading_overlay": ".dash-loading-overlay",
        
        # Error messages
        "error_alert": ".alert-danger",
        "warning_alert": ".alert-warning",
        "info_alert": ".alert-info",
    }
    
    # Test categories for filtering
    TEST_CATEGORIES = {
        "smoke": ["test_app_loads", "test_basic_navigation"],
        "critical": ["test_file_upload", "test_data_processing"],
        "regression": ["test_theme_switching", "test_graph_interactions"],
        "performance": ["test_large_file_handling", "test_render_speed"],
    }
    
    @classmethod
    def get_browser_args(cls) -> List[str]:
        """Get browser launch arguments."""
        args = []
        if cls.HEADLESS:
            args.append("--headless")
        if os.getenv("CI"):
            args.extend([
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
            ])
        return args
    
    @classmethod
    def get_viewport(cls, mobile: bool = False) -> Dict[str, int]:
        """Get viewport configuration."""
        if mobile:
            return {"width": cls.MOBILE_WIDTH, "height": cls.MOBILE_HEIGHT}
        return {"width": cls.VIEWPORT_WIDTH, "height": cls.VIEWPORT_HEIGHT}
    
    @classmethod
    def get_test_file_path(cls, filename: str) -> str:
        """Get full path to test data file."""
        return os.path.join(cls.TEST_DATA_PATH, filename)
    
    @classmethod
    def should_ignore_console_message(cls, message: str) -> bool:
        """Check if console message should be ignored."""
        return any(ignored in message for ignored in cls.IGNORED_CONSOLE_MESSAGES)


# Export config instance
config = PlaywrightConfig()