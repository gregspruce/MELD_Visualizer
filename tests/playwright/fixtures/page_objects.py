"""
Page Objects for MELD Visualizer
=================================
Reusable page components and actions for Playwright MCP tests.
"""

from typing import Optional, Dict, Any, List
import os
import sys

# Add parent directory to path for config import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.playwright_config import config


class BasePage:
    """Base page object with common functionality."""
    
    def __init__(self):
        self.url = config.BASE_URL
        self.selectors = config.SELECTORS
    
    def navigate(self, browser_type: str = "chromium", headless: bool = None):
        """Navigate to the application."""
        # This will be called via MCP
        return {
            "action": "mcp__playwright__playwright_navigate",
            "params": {
                "url": self.url,
                "browserType": browser_type,
                "headless": headless if headless is not None else config.HEADLESS,
                "width": config.VIEWPORT_WIDTH,
                "height": config.VIEWPORT_HEIGHT,
                "timeout": config.NAVIGATION_TIMEOUT
            }
        }
    
    def wait_for_load(self):
        """Wait for page to fully load."""
        return {
            "action": "mcp__playwright__playwright_evaluate",
            "params": {
                "script": "document.readyState === 'complete'"
            }
        }
    
    def take_screenshot(self, name: str, full_page: bool = None):
        """Take a screenshot."""
        return {
            "action": "mcp__playwright__playwright_screenshot",
            "params": {
                "name": name,
                "fullPage": full_page if full_page is not None else config.SCREENSHOT_FULL_PAGE,
                "savePng": True,
                "downloadsDir": config.SCREENSHOT_PATH
            }
        }
    
    def check_console_errors(self):
        """Check for console errors."""
        return {
            "action": "mcp__playwright__playwright_console_logs",
            "params": {
                "type": "error",
                "clear": True
            }
        }


class FileUploadComponent(BasePage):
    """Page object for file upload functionality."""
    
    def upload_file(self, file_path: str):
        """Upload a file to the application."""
        full_path = os.path.abspath(file_path)
        return {
            "action": "mcp__playwright__playwright_upload_file",
            "params": {
                "selector": self.selectors["upload_input"],
                "filePath": full_path
            }
        }
    
    def verify_upload_success(self):
        """Verify file upload was successful."""
        return {
            "action": "mcp__playwright__playwright_evaluate",
            "params": {
                "script": f"document.querySelector('{self.selectors['upload_success']}') !== null"
            }
        }
    
    def get_upload_error(self):
        """Get upload error message if present."""
        return {
            "action": "mcp__playwright__playwright_evaluate",
            "params": {
                "script": f"""
                    const error = document.querySelector('{self.selectors['error_alert']}');
                    error ? error.textContent : null;
                """
            }
        }


class NavigationComponent(BasePage):
    """Page object for tab navigation."""
    
    def switch_to_3d_tab(self):
        """Switch to 3D visualization tab."""
        return {
            "action": "mcp__playwright__playwright_click",
            "params": {
                "selector": self.selectors["tab_3d"]
            }
        }
    
    def switch_to_2d_tab(self):
        """Switch to 2D visualization tab."""
        return {
            "action": "mcp__playwright__playwright_click",
            "params": {
                "selector": self.selectors["tab_2d"]
            }
        }
    
    def switch_to_volume_tab(self):
        """Switch to volume visualization tab."""
        return {
            "action": "mcp__playwright__playwright_click",
            "params": {
                "selector": self.selectors["tab_volume"]
            }
        }
    
    def switch_to_overlap_tab(self):
        """Switch to bead overlap tab."""
        return {
            "action": "mcp__playwright__playwright_click",
            "params": {
                "selector": self.selectors["tab_overlap"]
            }
        }
    
    def get_active_tab(self):
        """Get the currently active tab."""
        return {
            "action": "mcp__playwright__playwright_evaluate",
            "params": {
                "script": "document.querySelector('.nav-link.active').textContent"
            }
        }


class ThemeComponent(BasePage):
    """Page object for theme selection."""
    
    def select_theme(self, theme_name: str):
        """Select a theme from the dropdown."""
        return {
            "action": "mcp__playwright__playwright_select",
            "params": {
                "selector": self.selectors["theme_dropdown"],
                "value": theme_name
            }
        }
    
    def get_current_theme(self):
        """Get the currently selected theme."""
        return {
            "action": "mcp__playwright__playwright_evaluate",
            "params": {
                "script": f"""
                    const selector = document.querySelector('{self.selectors['theme_dropdown']}');
                    selector ? selector.value : null;
                """
            }
        }
    
    def verify_theme_applied(self, theme_name: str):
        """Verify theme has been applied to the page."""
        return {
            "action": "mcp__playwright__playwright_evaluate",
            "params": {
                "script": f"document.documentElement.getAttribute('data-bs-theme') === '{theme_name}'"
            }
        }


class GraphComponent(BasePage):
    """Page object for graph interactions."""
    
    def wait_for_graph_render(self, graph_id: str):
        """Wait for a graph to finish rendering."""
        selector = self.selectors.get(graph_id, graph_id)
        return {
            "action": "mcp__playwright__playwright_evaluate",
            "params": {
                "script": f"""
                    const graph = document.querySelector('{selector}');
                    if (!graph) return false;
                    const plotly = graph._fullLayout;
                    return plotly && !plotly._transitioning;
                """
            }
        }
    
    def interact_with_3d_graph(self, action: str = "rotate"):
        """Interact with 3D graph (rotate, zoom, pan)."""
        actions = {
            "rotate": "event.clientX = 100; event.clientY = 100;",
            "zoom": "event.deltaY = -100;",
            "pan": "event.shiftKey = true; event.clientX = 150;"
        }
        
        return {
            "action": "mcp__playwright__playwright_evaluate",
            "params": {
                "script": f"""
                    const graph = document.querySelector('{self.selectors['graph_3d']}');
                    if (graph) {{
                        const event = new MouseEvent('mousemove', {{
                            bubbles: true,
                            cancelable: true,
                            view: window
                        }});
                        {actions.get(action, actions['rotate'])}
                        graph.dispatchEvent(event);
                        return true;
                    }}
                    return false;
                """
            }
        }
    
    def get_graph_data_points_count(self, graph_id: str):
        """Get the number of data points in a graph."""
        selector = self.selectors.get(graph_id, graph_id)
        return {
            "action": "mcp__playwright__playwright_evaluate",
            "params": {
                "script": f"""
                    const graph = document.querySelector('{selector}');
                    if (graph && graph.data && graph.data[0]) {{
                        return graph.data[0].x ? graph.data[0].x.length : 0;
                    }}
                    return 0;
                """
            }
        }


class ControlPanelComponent(BasePage):
    """Page object for control panel interactions."""
    
    def set_velocity_range(self, min_val: str, max_val: str):
        """Set velocity range values."""
        return [
            {
                "action": "mcp__playwright__playwright_fill",
                "params": {
                    "selector": self.selectors["velocity_min"],
                    "value": min_val
                }
            },
            {
                "action": "mcp__playwright__playwright_fill",
                "params": {
                    "selector": self.selectors["velocity_max"],
                    "value": max_val
                }
            }
        ]
    
    def update_graph(self):
        """Click update graph button."""
        return {
            "action": "mcp__playwright__playwright_click",
            "params": {
                "selector": self.selectors["update_button"]
            }
        }
    
    def set_position_slider(self, value: int):
        """Set position range slider value."""
        return {
            "action": "mcp__playwright__playwright_evaluate",
            "params": {
                "script": f"""
                    const slider = document.querySelector('{self.selectors['position_slider']}');
                    if (slider) {{
                        slider.value = {value};
                        slider.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        return true;
                    }}
                    return false;
                """
            }
        }


class ExportComponent(BasePage):
    """Page object for export functionality."""
    
    def export_as_html(self):
        """Export visualization as HTML."""
        return {
            "action": "mcp__playwright__playwright_click",
            "params": {
                "selector": self.selectors["export_html"]
            }
        }
    
    def export_as_csv(self):
        """Export data as CSV."""
        return {
            "action": "mcp__playwright__playwright_click",
            "params": {
                "selector": self.selectors["export_csv"]
            }
        }
    
    def verify_download_started(self):
        """Verify download has started."""
        return {
            "action": "mcp__playwright__playwright_evaluate",
            "params": {
                "script": """
                    // Check if any download link was clicked
                    const links = document.querySelectorAll('a[download]');
                    return links.length > 0;
                """
            }
        }


class MELDVisualizerApp:
    """Main application page object combining all components."""
    
    def __init__(self):
        self.base = BasePage()
        self.upload = FileUploadComponent()
        self.navigation = NavigationComponent()
        self.theme = ThemeComponent()
        self.graph = GraphComponent()
        self.controls = ControlPanelComponent()
        self.export = ExportComponent()
    
    def perform_complete_workflow(self, test_file: str):
        """Perform a complete user workflow."""
        workflow_steps = []
        
        # Navigate to app
        workflow_steps.append(self.base.navigate())
        
        # Upload file
        workflow_steps.append(self.upload.upload_file(test_file))
        
        # Wait for processing
        workflow_steps.append(self.base.wait_for_load())
        
        # Switch through tabs
        workflow_steps.extend([
            self.navigation.switch_to_3d_tab(),
            self.graph.wait_for_graph_render("graph_3d"),
            self.navigation.switch_to_2d_tab(),
            self.graph.wait_for_graph_render("graph_2d"),
            self.navigation.switch_to_volume_tab(),
        ])
        
        # Take screenshots
        workflow_steps.append(self.base.take_screenshot("complete_workflow"))
        
        # Check for errors
        workflow_steps.append(self.base.check_console_errors())
        
        return workflow_steps


# Export main app object
app = MELDVisualizerApp()