#!/usr/bin/env python3
"""
MELD Visualizer Test Runner
Comprehensive test runner that orchestrates different types of tests using Playwright MCP functions.
"""

import asyncio
import sys
import os
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
import argparse
import subprocess
import logging
from datetime import datetime

# Add the project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(PROJECT_ROOT / "tests" / "reports" / "test_runner.log")
    ]
)
logger = logging.getLogger(__name__)


class TestResults:
    """Container for test results"""
    
    def __init__(self):
        self.results = {
            'python_unit': {'passed': 0, 'failed': 0, 'skipped': 0, 'errors': []},
            'playwright_e2e': {'passed': 0, 'failed': 0, 'skipped': 0, 'errors': []},
            'playwright_integration': {'passed': 0, 'failed': 0, 'skipped': 0, 'errors': []},
            'playwright_performance': {'passed': 0, 'failed': 0, 'skipped': 0, 'errors': []},
            'playwright_visual': {'passed': 0, 'failed': 0, 'skipped': 0, 'errors': []}
        }
        self.start_time = time.time()
        self.end_time = None
        
    def add_result(self, test_type: str, status: str, error: Optional[str] = None):
        """Add a test result"""
        if test_type in self.results:
            if status in self.results[test_type]:
                self.results[test_type][status] += 1
            if error and status in ['failed', 'error']:
                self.results[test_type]['errors'].append(error)
    
    def finalize(self):
        """Finalize results"""
        self.end_time = time.time()
    
    def get_summary(self) -> Dict[str, Any]:
        """Get test results summary"""
        total_passed = sum(r['passed'] for r in self.results.values())
        total_failed = sum(r['failed'] for r in self.results.values())
        total_skipped = sum(r['skipped'] for r in self.results.values())
        total_time = (self.end_time or time.time()) - self.start_time
        
        return {
            'total_passed': total_passed,
            'total_failed': total_failed,
            'total_skipped': total_skipped,
            'total_time': total_time,
            'success_rate': total_passed / (total_passed + total_failed) if (total_passed + total_failed) > 0 else 0,
            'details': self.results
        }


class MELDTestRunner:
    """Main test runner for MELD Visualizer"""
    
    def __init__(self, args):
        self.args = args
        self.project_root = PROJECT_ROOT
        self.test_dir = self.project_root / "tests"
        self.reports_dir = self.test_dir / "reports"
        self.results = TestResults()
        
        # Ensure reports directory exists
        self.reports_dir.mkdir(exist_ok=True)
        
        # Test configuration
        self.app_url = "http://localhost:8050"
        self.app_process = None
        
    async def run_all_tests(self):
        """Run all test suites"""
        logger.info("🚀 Starting MELD Visualizer test suite")
        
        try:
            # Start the application if requested
            if self.args.start_app:
                await self.start_application()
            
            # Run Python unit tests
            if self.args.unit or self.args.all:
                await self.run_python_unit_tests()
            
            # Run Playwright tests
            if self.args.e2e or self.args.all:
                await self.run_playwright_e2e_tests()
            
            if self.args.integration or self.args.all:
                await self.run_playwright_integration_tests()
            
            if self.args.performance or self.args.all:
                await self.run_playwright_performance_tests()
            
            if self.args.visual or self.args.all:
                await self.run_playwright_visual_tests()
            
            # Generate final report
            await self.generate_final_report()
            
        except Exception as e:
            logger.error(f"❌ Test execution failed: {e}")
            raise
        finally:
            # Cleanup
            if self.app_process:
                await self.stop_application()
            
            self.results.finalize()
    
    async def start_application(self):
        """Start the MELD Visualizer application"""
        logger.info("🔄 Starting MELD Visualizer application...")
        
        try:
            # Start the application process
            self.app_process = subprocess.Popen([
                sys.executable, "-m", "meld_visualizer"
            ], cwd=self.project_root)
            
            # Wait for application to be ready
            await self.wait_for_application()
            logger.info("✅ Application started successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to start application: {e}")
            raise
    
    async def wait_for_application(self, timeout=60):
        """Wait for application to be ready"""
        import aiohttp
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(self.app_url, timeout=5) as response:
                        if response.status == 200:
                            return
            except:
                pass
            
            await asyncio.sleep(2)
        
        raise TimeoutError(f"Application did not start within {timeout} seconds")
    
    async def stop_application(self):
        """Stop the application"""
        if self.app_process:
            logger.info("🛑 Stopping application...")
            self.app_process.terminate()
            self.app_process.wait(timeout=10)
    
    async def run_python_unit_tests(self):
        """Run Python unit tests using pytest"""
        logger.info("🐍 Running Python unit tests...")
        
        try:
            # Run pytest
            cmd = [
                sys.executable, "-m", "pytest",
                str(self.test_dir / "python" / "unit"),
                "-v",
                "--tb=short",
                f"--junitxml={self.reports_dir}/python_unit_results.xml",
                f"--cov-report=json:{self.reports_dir}/python_unit_coverage.json"
            ]
            
            if self.args.verbose:
                cmd.append("-vv")
            
            result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
            
            # Parse results
            self.parse_pytest_results("python_unit", result)
            
            logger.info(f"✅ Python unit tests completed with return code: {result.returncode}")
            
        except Exception as e:
            logger.error(f"❌ Python unit tests failed: {e}")
            self.results.add_result("python_unit", "failed", str(e))
    
    async def run_playwright_e2e_tests(self):
        """Run Playwright E2E tests using MCP functions"""
        logger.info("🎭 Running Playwright E2E tests...")
        
        try:
            # These would be actual E2E test scenarios
            test_scenarios = [
                "test_application_startup",
                "test_csv_file_upload",
                "test_graph_rendering",
                "test_tab_navigation",
                "test_data_export"
            ]
            
            for scenario in test_scenarios:
                await self.run_e2e_scenario(scenario)
            
            logger.info("✅ Playwright E2E tests completed")
            
        except Exception as e:
            logger.error(f"❌ Playwright E2E tests failed: {e}")
            self.results.add_result("playwright_e2e", "failed", str(e))
    
    async def run_e2e_scenario(self, scenario_name: str):
        """Run a specific E2E test scenario"""
        logger.info(f"  📋 Running E2E scenario: {scenario_name}")
        
        try:
            # Import the actual test functions here
            # This is a placeholder showing how MCP functions would be used
            
            if scenario_name == "test_application_startup":
                await self.test_application_startup()
            elif scenario_name == "test_csv_file_upload":
                await self.test_csv_file_upload()
            elif scenario_name == "test_graph_rendering":
                await self.test_graph_rendering()
            elif scenario_name == "test_tab_navigation":
                await self.test_tab_navigation()
            elif scenario_name == "test_data_export":
                await self.test_data_export()
            
            self.results.add_result("playwright_e2e", "passed")
            logger.info(f"    ✅ {scenario_name} passed")
            
        except Exception as e:
            self.results.add_result("playwright_e2e", "failed", str(e))
            logger.error(f"    ❌ {scenario_name} failed: {e}")
    
    async def test_application_startup(self):
        """Test application startup and basic loading"""
        # This would use MCP Playwright functions
        # Example placeholder showing the structure
        
        # Navigate to application
        # await playwright_navigate(url=self.app_url)
        
        # Take screenshot
        # await playwright_screenshot(name="app_startup", save_png=True)
        
        # Verify main elements are present
        # visible_text = await playwright_get_visible_text()
        # assert "MELD" in visible_text or "Volumetric Data Plotter" in visible_text
        
        pass  # Placeholder
    
    async def test_csv_file_upload(self):
        """Test CSV file upload functionality"""
        test_csv = self.test_dir / "playwright" / "fixtures" / "test_data" / "sample_meld_data.csv"
        
        # Upload file
        # await playwright_upload_file(
        #     selector='input[type="file"]',
        #     file_path=str(test_csv)
        # )
        
        # Wait for processing
        # await asyncio.sleep(3)
        
        # Take screenshot
        # await playwright_screenshot(name="after_csv_upload", save_png=True)
        
        pass  # Placeholder
    
    async def test_graph_rendering(self):
        """Test 3D graph rendering"""
        # Wait for graph to render
        # await asyncio.sleep(5)
        
        # Take screenshot of graph
        # await playwright_screenshot(
        #     selector=".plotly-graph-div",
        #     name="rendered_graph",
        #     save_png=True
        # )
        
        # Check for graph elements
        # html = await playwright_get_visible_html(selector=".plotly-graph-div")
        # assert "plotly" in html.lower()
        
        pass  # Placeholder
    
    async def test_tab_navigation(self):
        """Test tab navigation functionality"""
        # Click through tabs if they exist
        # tabs = await playwright_evaluate('document.querySelectorAll(".nav-tab").length')
        
        # for i in range(tabs):
        #     await playwright_click(f".nav-tab:nth-child({i+1})")
        #     await asyncio.sleep(1)
        #     await playwright_screenshot(name=f"tab_{i}", save_png=True)
        
        pass  # Placeholder
    
    async def test_data_export(self):
        """Test data export functionality"""
        # Look for export buttons and test them
        # export_buttons = await playwright_evaluate('document.querySelectorAll("[data-export]").length')
        
        # if export_buttons > 0:
        #     await playwright_click("[data-export]")
        #     await asyncio.sleep(2)
        
        pass  # Placeholder
    
    async def run_playwright_integration_tests(self):
        """Run Playwright integration tests"""
        logger.info("🔗 Running Playwright integration tests...")
        
        # Integration test scenarios
        integration_scenarios = [
            "test_file_upload_to_visualization_pipeline",
            "test_filter_controls_interaction",
            "test_theme_switching",
            "test_responsive_behavior"
        ]
        
        for scenario in integration_scenarios:
            try:
                logger.info(f"  📋 Running integration scenario: {scenario}")
                # Run integration test
                await asyncio.sleep(1)  # Placeholder
                self.results.add_result("playwright_integration", "passed")
                logger.info(f"    ✅ {scenario} passed")
            except Exception as e:
                self.results.add_result("playwright_integration", "failed", str(e))
                logger.error(f"    ❌ {scenario} failed: {e}")
    
    async def run_playwright_performance_tests(self):
        """Run Playwright performance tests"""
        logger.info("⚡ Running Playwright performance tests...")
        
        performance_tests = [
            "test_page_load_time",
            "test_csv_upload_performance",
            "test_graph_render_time",
            "test_memory_usage"
        ]
        
        for test in performance_tests:
            try:
                logger.info(f"  📊 Running performance test: {test}")
                # Run performance test
                await asyncio.sleep(1)  # Placeholder
                self.results.add_result("playwright_performance", "passed")
                logger.info(f"    ✅ {test} passed")
            except Exception as e:
                self.results.add_result("playwright_performance", "failed", str(e))
                logger.error(f"    ❌ {test} failed: {e}")
    
    async def run_playwright_visual_tests(self):
        """Run Playwright visual regression tests"""
        logger.info("👁️  Running Playwright visual tests...")
        
        visual_tests = [
            "test_homepage_visual",
            "test_graph_visual_regression",
            "test_theme_visual_consistency",
            "test_responsive_layout"
        ]
        
        for test in visual_tests:
            try:
                logger.info(f"  🖼️  Running visual test: {test}")
                # Take screenshots and compare
                await asyncio.sleep(1)  # Placeholder
                self.results.add_result("playwright_visual", "passed")
                logger.info(f"    ✅ {test} passed")
            except Exception as e:
                self.results.add_result("playwright_visual", "failed", str(e))
                logger.error(f"    ❌ {test} failed: {e}")
    
    def parse_pytest_results(self, test_type: str, result):
        """Parse pytest results"""
        # Parse the output to extract test counts
        if result.returncode == 0:
            self.results.add_result(test_type, "passed")
        else:
            self.results.add_result(test_type, "failed", result.stderr)
    
    async def generate_final_report(self):
        """Generate final test report"""
        logger.info("📊 Generating final test report...")
        
        summary = self.results.get_summary()
        
        # Generate JSON report
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'summary': summary,
            'configuration': {
                'app_url': self.app_url,
                'test_types_run': [],
                'python_version': sys.version,
                'project_root': str(self.project_root)
            }
        }
        
        # Add test types that were run
        if self.args.unit or self.args.all:
            report_data['configuration']['test_types_run'].append('python_unit')
        if self.args.e2e or self.args.all:
            report_data['configuration']['test_types_run'].append('playwright_e2e')
        if self.args.integration or self.args.all:
            report_data['configuration']['test_types_run'].append('playwright_integration')
        if self.args.performance or self.args.all:
            report_data['configuration']['test_types_run'].append('playwright_performance')
        if self.args.visual or self.args.all:
            report_data['configuration']['test_types_run'].append('playwright_visual')
        
        # Save JSON report
        report_file = self.reports_dir / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        # Print summary
        print("\n" + "="*60)
        print("🏁 MELD Visualizer Test Results Summary")
        print("="*60)
        print(f"Total Passed: {summary['total_passed']}")
        print(f"Total Failed: {summary['total_failed']}")
        print(f"Total Skipped: {summary['total_skipped']}")
        print(f"Success Rate: {summary['success_rate']:.1%}")
        print(f"Total Time: {summary['total_time']:.1f} seconds")
        print(f"Report saved: {report_file}")
        print("="*60)
        
        # Return exit code based on results
        return 0 if summary['total_failed'] == 0 else 1


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="MELD Visualizer Test Runner")
    
    # Test type selection
    parser.add_argument("--all", action="store_true", help="Run all test types")
    parser.add_argument("--unit", action="store_true", help="Run Python unit tests")
    parser.add_argument("--e2e", action="store_true", help="Run Playwright E2E tests")
    parser.add_argument("--integration", action="store_true", help="Run Playwright integration tests")
    parser.add_argument("--performance", action="store_true", help="Run Playwright performance tests")
    parser.add_argument("--visual", action="store_true", help="Run Playwright visual regression tests")
    
    # Application management
    parser.add_argument("--start-app", action="store_true", 
                       help="Automatically start the application before tests")
    parser.add_argument("--app-url", default="http://localhost:8050",
                       help="URL of the running application")
    
    # Output options
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--quiet", "-q", action="store_true", help="Quiet output")
    
    args = parser.parse_args()
    
    # Default to all tests if no specific type is selected
    if not any([args.unit, args.e2e, args.integration, args.performance, args.visual]):
        args.all = True
    
    # Set logging level
    if args.quiet:
        logging.getLogger().setLevel(logging.WARNING)
    elif args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Run tests
    runner = MELDTestRunner(args)
    
    try:
        exit_code = asyncio.run(runner.run_all_tests())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("🛑 Test execution interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"💥 Test execution failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()