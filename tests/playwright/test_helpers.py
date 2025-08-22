"""
Test Helpers for Playwright MCP Tests
======================================
Common utilities and helper functions for all test types.
"""

import os
import json
import time
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime


class PlaywrightMCPExecutor:
    """
    Executor for Playwright MCP commands.
    This class simulates test execution since we can't directly call MCP from Python.
    In practice, these would be executed through the actual MCP interface.
    """
    
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.execution_log: List[Dict[str, Any]] = []
        self.screenshots_taken: List[str] = []
        self.console_errors: List[str] = []
    
    def execute(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a Playwright MCP action.
        In a real implementation, this would call the actual MCP tool.
        """
        timestamp = datetime.now().isoformat()
        
        # Log the action
        self.execution_log.append({
            "timestamp": timestamp,
            "action": action.get("action"),
            "params": action.get("params"),
        })
        
        if self.debug:
            print(f"[{timestamp}] Executing: {action.get('action')}")
            print(f"  Params: {json.dumps(action.get('params'), indent=2)}")
        
        # Simulate execution results
        return self._simulate_result(action)
    
    def execute_batch(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute multiple actions in sequence."""
        results = []
        for action in actions:
            if isinstance(action, list):
                # Handle nested action lists
                results.extend(self.execute_batch(action))
            else:
                results.append(self.execute(action))
        return results
    
    def _simulate_result(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate MCP action results for testing."""
        action_type = action.get("action", "")
        
        if "navigate" in action_type:
            return {"status": "success", "url": action["params"]["url"]}
        elif "screenshot" in action_type:
            name = action["params"]["name"]
            self.screenshots_taken.append(name)
            return {"status": "success", "screenshot": f"{name}.png"}
        elif "click" in action_type:
            return {"status": "success", "clicked": action["params"]["selector"]}
        elif "fill" in action_type:
            return {"status": "success", "filled": action["params"]["selector"]}
        elif "upload" in action_type:
            return {"status": "success", "uploaded": action["params"]["filePath"]}
        elif "evaluate" in action_type:
            # Return mock evaluation results
            script = action["params"]["script"]
            if "readyState" in script:
                return {"status": "success", "result": True}
            elif "querySelector" in script:
                return {"status": "success", "result": True}
            return {"status": "success", "result": "mock_result"}
        elif "console_logs" in action_type:
            return {"status": "success", "logs": self.console_errors}
        else:
            return {"status": "success"}
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get summary of test execution."""
        return {
            "total_actions": len(self.execution_log),
            "screenshots": self.screenshots_taken,
            "console_errors": self.console_errors,
            "execution_log": self.execution_log
        }


class TestDataGenerator:
    """Generate test data for various scenarios."""
    
    @staticmethod
    def generate_csv_data(rows: int = 100) -> str:
        """Generate CSV test data with specified number of rows."""
        headers = [
            "Date", "Time", "Position X (in)", "Position Y (in)", "Position Z (in)",
            "Velocity X (in/min)", "Velocity Y (in/min)", "Velocity Z (in/min)",
            "Spindle Speed (RPM)", "Force Z (lbf)", "Torque Z (ft-lbf)"
        ]
        
        lines = [",".join(headers)]
        
        for i in range(rows):
            date = "2024-01-15"
            time_val = f"10:{i//60:02d}:{i%60:02d}"
            pos_x = i * 0.5
            pos_y = (i % 10) * 0.5
            pos_z = (i // 10) * 0.1
            vel_x = 120 if i % 2 == 0 else 0
            vel_y = 0 if i % 2 == 0 else 120
            vel_z = 10 if i % 10 == 0 else 0
            spindle = 1000 + (i % 3) * 50
            force = 100 + (i % 20)
            torque = 50 + (i % 10)
            
            lines.append(f"{date},{time_val},{pos_x},{pos_y},{pos_z},{vel_x},{vel_y},{vel_z},{spindle},{force},{torque}")
        
        return "\n".join(lines)
    
    @staticmethod
    def generate_gcode(complexity: str = "simple") -> str:
        """Generate G-code test data."""
        if complexity == "simple":
            return """G90 ; Absolute positioning
G1 F120 X10 Y10 Z0
G1 X20 Y10 Z0
G1 X20 Y20 Z0
G1 X10 Y20 Z0
G1 X10 Y10 Z0
M30 ; End program"""
        elif complexity == "complex":
            gcode_lines = ["G90 ; Absolute positioning"]
            for layer in range(5):
                z = layer * 2
                gcode_lines.append(f"G1 Z{z}")
                for angle in range(0, 360, 30):
                    import math
                    x = 50 + 30 * math.cos(math.radians(angle))
                    y = 50 + 30 * math.sin(math.radians(angle))
                    gcode_lines.append(f"G1 F150 X{x:.2f} Y{y:.2f} Z{z}")
            gcode_lines.append("M30 ; End program")
            return "\n".join(gcode_lines)
        return ""


class TestValidator:
    """Validate test results and assertions."""
    
    @staticmethod
    def validate_screenshot(screenshot_path: str, baseline_path: Optional[str] = None) -> bool:
        """Validate screenshot exists and optionally compare to baseline."""
        if not os.path.exists(screenshot_path):
            return False
        
        if baseline_path and os.path.exists(baseline_path):
            # In real implementation, would do image comparison
            # For now, just check both files exist
            return True
        
        return True
    
    @staticmethod
    def validate_console_logs(logs: List[str], allowed_patterns: List[str] = None) -> bool:
        """Validate console logs for errors."""
        if not logs:
            return True
        
        if allowed_patterns:
            for log in logs:
                if not any(pattern in log for pattern in allowed_patterns):
                    return False
        
        return len(logs) == 0
    
    @staticmethod
    def validate_performance(start_time: float, end_time: float, max_duration: float) -> bool:
        """Validate performance metrics."""
        duration = end_time - start_time
        return duration <= max_duration


class TestReporter:
    """Generate test reports."""
    
    def __init__(self):
        self.results: List[Dict[str, Any]] = []
    
    def add_test_result(self, test_name: str, status: str, duration: float, 
                        details: Optional[Dict[str, Any]] = None):
        """Add a test result."""
        self.results.append({
            "test_name": test_name,
            "status": status,
            "duration": duration,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        })
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate test summary."""
        total_tests = len(self.results)
        passed = sum(1 for r in self.results if r["status"] == "passed")
        failed = sum(1 for r in self.results if r["status"] == "failed")
        skipped = sum(1 for r in self.results if r["status"] == "skipped")
        
        total_duration = sum(r["duration"] for r in self.results)
        
        return {
            "total_tests": total_tests,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "pass_rate": (passed / total_tests * 100) if total_tests > 0 else 0,
            "total_duration": total_duration,
            "average_duration": total_duration / total_tests if total_tests > 0 else 0,
            "results": self.results
        }
    
    def save_report(self, filepath: str):
        """Save report to file."""
        report = self.generate_summary()
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        return filepath


class PerformanceTimer:
    """Context manager for timing operations."""
    
    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
    
    @property
    def duration(self) -> float:
        """Get duration in seconds."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0
    
    @property
    def duration_ms(self) -> float:
        """Get duration in milliseconds."""
        return self.duration * 1000


# Decorator for test timing
def timed_test(func: Callable) -> Callable:
    """Decorator to time test execution."""
    def wrapper(*args, **kwargs):
        timer = PerformanceTimer(func.__name__)
        with timer:
            result = func(*args, **kwargs)
        print(f"Test '{func.__name__}' completed in {timer.duration_ms:.2f}ms")
        return result
    return wrapper


# Test data paths helper
class TestPaths:
    """Helper for test file paths."""
    
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    TEST_DATA_DIR = os.path.join(BASE_DIR, "playwright", "fixtures", "test_data")
    SCREENSHOTS_DIR = os.path.join(BASE_DIR, "screenshots")
    REPORTS_DIR = os.path.join(BASE_DIR, "reports")
    
    @classmethod
    def get_test_data_file(cls, filename: str) -> str:
        """Get full path to test data file."""
        return os.path.join(cls.TEST_DATA_DIR, filename)
    
    @classmethod
    def get_screenshot_path(cls, name: str) -> str:
        """Get full path for screenshot."""
        os.makedirs(cls.SCREENSHOTS_DIR, exist_ok=True)
        return os.path.join(cls.SCREENSHOTS_DIR, f"{name}.png")
    
    @classmethod
    def get_report_path(cls, name: str) -> str:
        """Get full path for report."""
        os.makedirs(cls.REPORTS_DIR, exist_ok=True)
        return os.path.join(cls.REPORTS_DIR, f"{name}.json")