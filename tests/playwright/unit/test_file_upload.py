"""
File Upload Component Tests
============================
Tests for file upload functionality using Playwright MCP.
"""

import os
import sys
import time

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fixtures.page_objects import MELDVisualizerApp
from test_helpers import (
    PlaywrightMCPExecutor, 
    TestDataGenerator,
    TestValidator,
    TestReporter,
    PerformanceTimer,
    TestPaths,
    timed_test
)
from config.playwright_config import config


class TestFileUpload:
    """Test suite for file upload functionality."""
    
    def __init__(self):
        self.app = MELDVisualizerApp()
        self.executor = PlaywrightMCPExecutor(debug=True)
        self.reporter = TestReporter()
        self.validator = TestValidator()
    
    @timed_test
    def test_upload_valid_csv(self):
        """Test uploading a valid CSV file."""
        test_name = "test_upload_valid_csv"
        timer = PerformanceTimer(test_name)
        
        try:
            with timer:
                # Navigate to application
                nav_action = self.app.base.navigate()
                self.executor.execute(nav_action)
                
                # Upload CSV file
                csv_path = TestPaths.get_test_data_file("sample_meld_data.csv")
                upload_action = self.app.upload.upload_file(csv_path)
                result = self.executor.execute(upload_action)
                
                # Verify upload success
                verify_action = self.app.upload.verify_upload_success()
                success = self.executor.execute(verify_action)
                
                # Take screenshot
                screenshot_action = self.app.base.take_screenshot("upload_success")
                self.executor.execute(screenshot_action)
                
                # Check console for errors
                console_action = self.app.base.check_console_errors()
                console_result = self.executor.execute(console_action)
                
                # Validate results
                assert success.get("result") == True, "Upload verification failed"
                assert self.validator.validate_console_logs(
                    console_result.get("logs", [])
                ), "Console errors detected"
            
            self.reporter.add_test_result(
                test_name, 
                "passed", 
                timer.duration,
                {"file": "sample_meld_data.csv"}
            )
            print(f"[PASS] {test_name}")
            
        except Exception as e:
            self.reporter.add_test_result(
                test_name, 
                "failed", 
                timer.duration if timer.duration else 0,
                {"error": str(e)}
            )
            print(f"[FAIL] {test_name}: {e}")
            raise
    
    @timed_test
    def test_upload_gcode_file(self):
        """Test uploading a G-code (.nc) file."""
        test_name = "test_upload_gcode_file"
        timer = PerformanceTimer(test_name)
        
        try:
            with timer:
                # Navigate to application
                nav_action = self.app.base.navigate()
                self.executor.execute(nav_action)
                
                # Upload G-code file
                nc_path = TestPaths.get_test_data_file("sample_gcode.nc")
                upload_action = self.app.upload.upload_file(nc_path)
                result = self.executor.execute(upload_action)
                
                # Switch to appropriate tab for G-code visualization
                tab_action = self.app.navigation.switch_to_3d_tab()
                self.executor.execute(tab_action)
                
                # Wait for graph render
                wait_action = self.app.graph.wait_for_graph_render("graph_3d")
                render_result = self.executor.execute(wait_action)
                
                # Take screenshot
                screenshot_action = self.app.base.take_screenshot("gcode_upload")
                self.executor.execute(screenshot_action)
                
                assert render_result.get("result") == True, "Graph rendering failed"
            
            self.reporter.add_test_result(
                test_name,
                "passed",
                timer.duration,
                {"file": "sample_gcode.nc"}
            )
            print(f"[PASS] {test_name}")
            
        except Exception as e:
            self.reporter.add_test_result(
                test_name,
                "failed", 
                timer.duration if timer.duration else 0,
                {"error": str(e)}
            )
            print(f"[FAIL] {test_name}: {e}")
            raise
    
    @timed_test
    def test_upload_invalid_file(self):
        """Test uploading an invalid file type."""
        test_name = "test_upload_invalid_file"
        timer = PerformanceTimer(test_name)
        
        try:
            with timer:
                # Navigate to application
                nav_action = self.app.base.navigate()
                self.executor.execute(nav_action)
                
                # Create invalid test file
                invalid_file = TestPaths.get_test_data_file("invalid.txt")
                with open(invalid_file, 'w') as f:
                    f.write("This is not valid MELD data")
                
                # Attempt upload
                upload_action = self.app.upload.upload_file(invalid_file)
                self.executor.execute(upload_action)
                
                # Check for error message
                error_action = self.app.upload.get_upload_error()
                error_result = self.executor.execute(error_action)
                
                # Clean up test file
                os.remove(invalid_file)
                
                # Verify error was shown
                assert error_result.get("result") is not None, "No error message shown for invalid file"
            
            self.reporter.add_test_result(
                test_name,
                "passed",
                timer.duration,
                {"file": "invalid.txt", "expected": "error"}
            )
            print(f"[PASS] {test_name}")
            
        except Exception as e:
            self.reporter.add_test_result(
                test_name,
                "failed",
                timer.duration if timer.duration else 0,
                {"error": str(e)}
            )
            print(f"[FAIL] {test_name}: {e}")
            raise
    
    @timed_test
    def test_upload_large_file(self):
        """Test uploading a large CSV file."""
        test_name = "test_upload_large_file"
        timer = PerformanceTimer(test_name)
        
        try:
            with timer:
                # Generate large test file
                large_csv = TestDataGenerator.generate_csv_data(rows=10000)
                large_file = TestPaths.get_test_data_file("large_test.csv")
                with open(large_file, 'w') as f:
                    f.write(large_csv)
                
                # Navigate to application
                nav_action = self.app.base.navigate()
                self.executor.execute(nav_action)
                
                # Upload large file
                upload_action = self.app.upload.upload_file(large_file)
                upload_start = time.time()
                result = self.executor.execute(upload_action)
                upload_duration = time.time() - upload_start
                
                # Verify performance
                assert self.validator.validate_performance(
                    upload_start,
                    time.time(),
                    config.FILE_UPLOAD_TIMEOUT / 1000  # Convert to seconds
                ), f"Upload took too long: {upload_duration}s"
                
                # Clean up
                os.remove(large_file)
            
            self.reporter.add_test_result(
                test_name,
                "passed",
                timer.duration,
                {"rows": 10000, "upload_time": upload_duration}
            )
            print(f"[PASS] {test_name}")
            
        except Exception as e:
            self.reporter.add_test_result(
                test_name,
                "failed",
                timer.duration if timer.duration else 0,
                {"error": str(e)}
            )
            print(f"[FAIL] {test_name}: {e}")
            raise
    
    def run_all_tests(self):
        """Run all file upload tests."""
        print("\n" + "="*60)
        print("FILE UPLOAD COMPONENT TESTS")
        print("="*60 + "\n")
        
        tests = [
            self.test_upload_valid_csv,
            self.test_upload_gcode_file,
            self.test_upload_invalid_file,
            self.test_upload_large_file,
        ]
        
        for test in tests:
            try:
                test()
            except Exception:
                pass  # Continue with other tests
        
        # Generate report
        summary = self.reporter.generate_summary()
        report_path = TestPaths.get_report_path("file_upload_tests")
        self.reporter.save_report(report_path)
        
        # Print summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed']}")
        print(f"Failed: {summary['failed']}")
        print(f"Pass Rate: {summary['pass_rate']:.1f}%")
        print(f"Total Duration: {summary['total_duration']:.2f}s")
        print(f"Report saved to: {report_path}")
        print("="*60 + "\n")
        
        # Print execution log for debugging
        if self.executor.debug:
            print("\nExecution Summary:")
            exec_summary = self.executor.get_execution_summary()
            print(f"  Total Actions: {exec_summary['total_actions']}")
            print(f"  Screenshots: {', '.join(exec_summary['screenshots'])}")
            if exec_summary['console_errors']:
                print(f"  Console Errors: {len(exec_summary['console_errors'])}")
        
        return summary['failed'] == 0


if __name__ == "__main__":
    # Run tests
    import time
    test_suite = TestFileUpload()
    success = test_suite.run_all_tests()
    sys.exit(0 if success else 1)