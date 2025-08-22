#!/usr/bin/env python
"""
Playwright MCP Test Runner
==========================
Main test runner for executing Playwright MCP tests.
"""

import os
import sys
import argparse
import importlib.util
from pathlib import Path
from typing import List, Dict, Any
import json
from datetime import datetime


class PlaywrightTestRunner:
    """Main test runner for Playwright MCP tests."""
    
    def __init__(self, test_dir: str = "tests/playwright"):
        self.test_dir = Path(test_dir)
        self.results = []
        self.start_time = None
        self.end_time = None
    
    def discover_tests(self, pattern: str = "test_*.py") -> List[Path]:
        """Discover all test files matching pattern."""
        test_files = []
        
        # Search in unit, integration, e2e, performance, visual directories
        test_dirs = ["unit", "integration", "e2e", "performance", "visual"]
        
        for test_type in test_dirs:
            test_path = self.test_dir / test_type
            if test_path.exists():
                test_files.extend(test_path.glob(pattern))
        
        return sorted(test_files)
    
    def load_test_module(self, test_file: Path):
        """Dynamically load a test module."""
        spec = importlib.util.spec_from_file_location(
            test_file.stem,
            test_file
        )
        module = importlib.util.module_from_spec(spec)
        sys.modules[test_file.stem] = module
        spec.loader.exec_module(module)
        return module
    
    def run_test_file(self, test_file: Path) -> Dict[str, Any]:
        """Run a single test file."""
        print(f"\nRunning: {test_file.relative_to(self.test_dir.parent)}")
        print("-" * 50)
        
        try:
            # Load the test module
            module = self.load_test_module(test_file)
            
            # Find and instantiate test classes
            test_classes = [
                getattr(module, name) for name in dir(module)
                if name.startswith("Test") and isinstance(getattr(module, name), type)
            ]
            
            file_results = {
                "file": str(test_file.relative_to(self.test_dir.parent)),
                "tests": [],
                "passed": 0,
                "failed": 0,
                "skipped": 0
            }
            
            for test_class in test_classes:
                # Instantiate test class
                test_instance = test_class()
                
                # Run test methods
                test_methods = [
                    method for method in dir(test_instance)
                    if method.startswith("test_") and callable(getattr(test_instance, method))
                ]
                
                for method_name in test_methods:
                    try:
                        method = getattr(test_instance, method_name)
                        method()
                        file_results["passed"] += 1
                        file_results["tests"].append({
                            "name": method_name,
                            "status": "passed"
                        })
                    except Exception as e:
                        file_results["failed"] += 1
                        file_results["tests"].append({
                            "name": method_name,
                            "status": "failed",
                            "error": str(e)
                        })
                
                # Check for run_all_tests method
                if hasattr(test_instance, "run_all_tests"):
                    test_instance.run_all_tests()
            
            return file_results
            
        except Exception as e:
            print(f"Error running test file: {e}")
            return {
                "file": str(test_file.relative_to(self.test_dir.parent)),
                "error": str(e),
                "passed": 0,
                "failed": 1,
                "skipped": 0
            }
    
    def run_tests(self, test_files: List[Path] = None, test_type: str = None):
        """Run specified test files or all discovered tests."""
        self.start_time = datetime.now()
        
        if test_files is None:
            test_files = self.discover_tests()
        
        # Filter by test type if specified
        if test_type:
            test_files = [
                f for f in test_files
                if test_type in str(f.parent.name)
            ]
        
        if not test_files:
            print("No test files found.")
            return False
        
        print(f"\nDiscovered {len(test_files)} test file(s)")
        print("=" * 60)
        
        for test_file in test_files:
            result = self.run_test_file(test_file)
            self.results.append(result)
        
        self.end_time = datetime.now()
        return self.generate_report()
    
    def generate_report(self) -> bool:
        """Generate and display test report."""
        total_passed = sum(r.get("passed", 0) for r in self.results)
        total_failed = sum(r.get("failed", 0) for r in self.results)
        total_skipped = sum(r.get("skipped", 0) for r in self.results)
        total_tests = total_passed + total_failed + total_skipped
        
        duration = (self.end_time - self.start_time).total_seconds()
        
        # Print summary
        print("\n" + "=" * 60)
        print("PLAYWRIGHT MCP TEST RESULTS")
        print("=" * 60)
        print(f"Total Test Files: {len(self.results)}")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {total_passed} [PASSED]")
        print(f"Failed: {total_failed} [FAILED]")
        print(f"Skipped: {total_skipped} [SKIPPED]")
        print(f"Pass Rate: {(total_passed/total_tests*100) if total_tests > 0 else 0:.1f}%")
        print(f"Duration: {duration:.2f}s")
        print("=" * 60)
        
        # Show failed tests
        if total_failed > 0:
            print("\nFailed Tests:")
            for result in self.results:
                if result.get("failed", 0) > 0:
                    print(f"\n  {result['file']}:")
                    for test in result.get("tests", []):
                        if test.get("status") == "failed":
                            print(f"    [X] {test['name']}")
                            if test.get("error"):
                                print(f"      Error: {test['error']}")
        
        # Save detailed report
        report_path = Path("tests/reports/playwright_test_report.json")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        report_data = {
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "duration": duration,
            "summary": {
                "total_files": len(self.results),
                "total_tests": total_tests,
                "passed": total_passed,
                "failed": total_failed,
                "skipped": total_skipped,
                "pass_rate": (total_passed/total_tests*100) if total_tests > 0 else 0
            },
            "results": self.results
        }
        
        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\nDetailed report saved to: {report_path}")
        
        return total_failed == 0


def main():
    """Main entry point for test runner."""
    parser = argparse.ArgumentParser(description="Run Playwright MCP tests")
    parser.add_argument(
        "--type",
        choices=["unit", "integration", "e2e", "performance", "visual", "all"],
        default="all",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--file",
        help="Specific test file to run"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug output"
    )
    
    args = parser.parse_args()
    
    # Set debug environment variable if requested
    if args.debug:
        os.environ["PLAYWRIGHT_DEBUG"] = "1"
    
    runner = PlaywrightTestRunner()
    
    # Run specific file or all tests
    if args.file:
        test_files = [Path(args.file)]
        success = runner.run_tests(test_files)
    elif args.type == "all":
        success = runner.run_tests()
    else:
        success = runner.run_tests(test_type=args.type)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()