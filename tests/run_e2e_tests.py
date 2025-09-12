#!/usr/bin/env python3
"""
MELD Visualizer E2E Test Runner
Comprehensive test runner for end-to-end testing with Playwright MCP integration.
"""

import argparse
import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class E2ETestRunner:
    """Comprehensive E2E test runner for MELD Visualizer."""

    def __init__(self, project_root=None):
        self.project_root = Path(project_root or os.getcwd())
        self.tests_dir = self.project_root / "tests"
        self.e2e_dir = self.tests_dir / "playwright" / "e2e"
        self.reports_dir = self.tests_dir / "reports"

        # Ensure directories exist
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        (self.reports_dir / "e2e").mkdir(exist_ok=True)

    def check_prerequisites(self):
        """Check if all prerequisites are met for E2E testing."""
        logger.info("🔍 Checking E2E test prerequisites...")

        # Check Python environment
        python_version = sys.version_info
        if python_version < (3, 8):
            logger.error(
                f"❌ Python 3.8+ required, found {python_version.major}.{python_version.minor}"
            )
            return False
        logger.info(
            f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}"
        )

        # Check required packages
        required_packages = ["pytest", "pytest-asyncio", "playwright"]
        missing_packages = []

        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
                logger.info(f"✅ {package} installed")
            except ImportError:
                missing_packages.append(package)
                logger.error(f"❌ {package} not found")

        if missing_packages:
            logger.error(f"❌ Missing packages: {', '.join(missing_packages)}")
            logger.info("Install with: pip install pytest pytest-asyncio playwright")
            return False

        # Check if MELD Visualizer server is running
        try:
            import requests

            response = requests.get("http://127.0.0.1:8050", timeout=5)
            if response.status_code == 200:
                logger.info("✅ MELD Visualizer server is running")
            else:
                logger.warning(
                    f"⚠️  MELD Visualizer server responded with status {response.status_code}"
                )
        except Exception:
            logger.error("❌ MELD Visualizer server not accessible at http://127.0.0.1:8050")
            logger.error("   Please start the server with: python -m meld_visualizer")
            return False

        # Check test files exist
        test_files = [
            "test_critical_user_journeys.py",
            "test_enhanced_ui_functionality.py",
            "test_performance_benchmarks.py",
            "test_error_scenarios.py",
            "test_responsive_design.py",
        ]

        missing_files = []
        for test_file in test_files:
            test_path = self.e2e_dir / test_file
            if test_path.exists():
                logger.info(f"✅ {test_file}")
            else:
                missing_files.append(test_file)
                logger.error(f"❌ {test_file} not found")

        if missing_files:
            logger.error(f"❌ Missing test files: {', '.join(missing_files)}")
            return False

        return True

    def install_playwright_browsers(self):
        """Install Playwright browsers if needed."""
        logger.info("📦 Installing Playwright browsers...")

        try:
            # Install Playwright browsers
            result = subprocess.run(
                [sys.executable, "-m", "playwright", "install"],
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode == 0:
                logger.info("✅ Playwright browsers installed successfully")
                return True
            else:
                logger.error(f"❌ Failed to install Playwright browsers: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.error("❌ Playwright browser installation timed out")
            return False
        except Exception as e:
            logger.error(f"❌ Playwright browser installation failed: {e}")
            return False

    def run_e2e_tests(
        self,
        test_suite="all",
        browser="chromium",
        headed=False,
        parallel=True,
        verbose=False,
        markers=None,
        max_failures=None,
    ):
        """
        Run E2E tests with specified configuration.

        Args:
            test_suite: Which test suite to run ('all', 'smoke', 'critical', 'performance', etc.)
            browser: Browser to use ('chromium', 'firefox', 'webkit', 'all')
            headed: Run tests in headed mode
            parallel: Run tests in parallel
            verbose: Verbose output
            markers: Pytest markers to filter tests
            max_failures: Maximum number of failures before stopping
        """
        logger.info(f"🚀 Starting E2E test suite: {test_suite}")

        # Build pytest command
        cmd = [sys.executable, "-m", "pytest"]

        # Test directory
        if test_suite == "all":
            cmd.append(str(self.e2e_dir))
        elif test_suite == "smoke":
            cmd.extend([str(self.e2e_dir), "-m", "smoke"])
        elif test_suite == "critical":
            cmd.append(str(self.e2e_dir / "test_critical_user_journeys.py"))
        elif test_suite == "enhanced_ui":
            cmd.append(str(self.e2e_dir / "test_enhanced_ui_functionality.py"))
        elif test_suite == "performance":
            cmd.append(str(self.e2e_dir / "test_performance_benchmarks.py"))
        elif test_suite == "error_handling":
            cmd.append(str(self.e2e_dir / "test_error_scenarios.py"))
        elif test_suite == "responsive":
            cmd.append(str(self.e2e_dir / "test_responsive_design.py"))
        else:
            # Treat as specific test file or pattern
            test_path = self.e2e_dir / test_suite
            if test_path.exists():
                cmd.append(str(test_path))
            else:
                cmd.extend([str(self.e2e_dir), "-k", test_suite])

        # Browser configuration
        if browser != "all":
            os.environ["BROWSER"] = browser

        # Headed/headless mode
        if headed:
            os.environ["HEADLESS"] = "false"
        else:
            os.environ["HEADLESS"] = "true"

        # Parallel execution
        if parallel and test_suite != "performance":  # Performance tests run better sequentially
            try:
                pass

                cmd.extend(["-n", "auto"])
                logger.info("✅ Running tests in parallel")
            except ImportError:
                logger.warning("⚠️  pytest-xdist not installed, running sequentially")

        # Verbose output
        if verbose:
            cmd.append("-v")

        # Additional markers
        if markers:
            cmd.extend(["-m", markers])

        # Max failures
        if max_failures:
            cmd.extend(["--maxfail", str(max_failures)])

        # Output configuration
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.reports_dir / "e2e" / f"e2e_report_{timestamp}.html"
        json_report = self.reports_dir / "e2e" / f"e2e_report_{timestamp}.json"

        cmd.extend(
            [
                f"--html={report_file}",
                "--self-contained-html",
                f"--json-report",
                f"--json-report-file={json_report}",
                "--tb=short",
                "--capture=no" if verbose else "--capture=sys",
            ]
        )

        # Screenshots and videos
        os.environ["SCREENSHOT"] = "only-on-failure"
        os.environ["VIDEO"] = "retain-on-failure"

        logger.info(f"📋 Command: {' '.join(str(x) for x in cmd)}")

        # Run tests
        start_time = time.time()
        try:
            # Set environment variables
            env = os.environ.copy()
            env["PYTHONPATH"] = str(self.project_root / "src")

            result = subprocess.run(cmd, cwd=self.project_root, env=env, timeout=3600)
            end_time = time.time()

            duration = end_time - start_time
            success = result.returncode == 0

            # Generate summary report
            self.generate_e2e_summary(
                test_suite, browser, duration, success, result.returncode, report_file, json_report
            )

            return success

        except subprocess.TimeoutExpired:
            logger.error("❌ E2E tests timed out (1 hour limit)")
            return False
        except KeyboardInterrupt:
            logger.warning("⚠️  E2E tests interrupted by user")
            return False
        except Exception as e:
            logger.error(f"❌ E2E test execution failed: {e}")
            return False

    def generate_e2e_summary(
        self, test_suite, browser, duration, success, exit_code, html_report, json_report
    ):
        """Generate a comprehensive E2E test summary."""
        timestamp = datetime.now().isoformat()

        # Try to read JSON report for detailed stats
        test_stats = {}
        if json_report.exists():
            try:
                with open(json_report, "r") as f:
                    report_data = json.load(f)
                    test_stats = report_data.get("summary", {})
            except Exception as e:
                logger.warning(f"Could not read test stats: {e}")

        # Create summary
        summary = {
            "timestamp": timestamp,
            "test_suite": test_suite,
            "browser": browser,
            "duration_seconds": round(duration, 2),
            "success": success,
            "exit_code": exit_code,
            "test_stats": test_stats,
            "reports": {
                "html": str(html_report),
                "json": str(json_report),
                "screenshots": str(self.reports_dir / "screenshots"),
                "videos": str(self.reports_dir / "videos"),
            },
            "environment": {
                "python_version": sys.version,
                "working_directory": str(self.project_root),
                "base_url": "http://127.0.0.1:8050",
            },
        }

        # Write summary
        summary_file = (
            self.reports_dir
            / "e2e"
            / f"e2e_summary_{test_suite}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2)

        # Print summary
        status = "✅ PASSED" if success else "❌ FAILED"
        logger.info(f"📊 E2E Test Summary ({status}):")
        logger.info(f"   Suite: {test_suite}")
        logger.info(f"   Browser: {browser}")
        logger.info(f"   Duration: {duration:.1f}s")

        if test_stats:
            total = test_stats.get("total", 0)
            passed = test_stats.get("passed", 0)
            failed = test_stats.get("failed", 0)
            skipped = test_stats.get("skipped", 0)

            logger.info(
                f"   Tests: {total} total, {passed} passed, {failed} failed, {skipped} skipped"
            )

        logger.info(f"   HTML Report: {html_report}")
        logger.info(f"   Summary: {summary_file}")

        return summary_file

    def run_browser_compatibility_tests(self):
        """Run tests across multiple browsers for compatibility."""
        logger.info("🌐 Running cross-browser compatibility tests...")

        browsers = ["chromium", "firefox", "webkit"]
        results = {}

        for browser in browsers:
            logger.info(f"Testing with {browser}...")
            success = self.run_e2e_tests(
                test_suite="critical", browser=browser, headed=False, parallel=False, verbose=False
            )
            results[browser] = success

        # Summary
        logger.info("🌐 Cross-Browser Compatibility Results:")
        for browser, success in results.items():
            status = "✅ PASSED" if success else "❌ FAILED"
            logger.info(f"   {browser}: {status}")

        return all(results.values())

    def run_performance_suite(self):
        """Run comprehensive performance test suite."""
        logger.info("⚡ Running performance test suite...")

        # Run performance tests with specific configuration
        return self.run_e2e_tests(
            test_suite="performance",
            browser="chromium",
            headed=False,
            parallel=False,  # Performance tests run better sequentially
            verbose=True,
        )

    def run_smoke_tests(self):
        """Run smoke tests for quick validation."""
        logger.info("💨 Running smoke tests...")

        return self.run_e2e_tests(
            test_suite="critical",
            browser="chromium",
            headed=False,
            parallel=True,
            markers="smoke or not slow",
        )

    def cleanup_old_reports(self, days_to_keep=7):
        """Clean up old test reports."""
        logger.info(f"🧹 Cleaning up reports older than {days_to_keep} days...")

        cutoff_time = time.time() - (days_to_keep * 24 * 60 * 60)

        for report_dir in [
            self.reports_dir / "e2e",
            self.reports_dir / "screenshots",
            self.reports_dir / "videos",
        ]:
            if report_dir.exists():
                for file_path in report_dir.glob("*"):
                    if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                        try:
                            file_path.unlink()
                            logger.info(f"Deleted old report: {file_path.name}")
                        except Exception as e:
                            logger.warning(f"Could not delete {file_path}: {e}")


def main():
    """Main entry point for E2E test runner."""
    parser = argparse.ArgumentParser(description="MELD Visualizer E2E Test Runner")

    # Test suite options
    parser.add_argument(
        "--suite",
        choices=[
            "all",
            "smoke",
            "critical",
            "enhanced_ui",
            "performance",
            "error_handling",
            "responsive",
        ],
        default="smoke",
        help="Test suite to run",
    )

    # Browser options
    parser.add_argument(
        "--browser",
        choices=["chromium", "firefox", "webkit", "all"],
        default="chromium",
        help="Browser to use for testing",
    )

    # Execution options
    parser.add_argument("--headed", action="store_true", help="Run tests in headed mode")
    parser.add_argument(
        "--no-parallel", action="store_true", help="Disable parallel test execution"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--markers", help="Pytest markers to filter tests")
    parser.add_argument("--max-failures", type=int, help="Maximum failures before stopping")

    # Special test modes
    parser.add_argument(
        "--cross-browser", action="store_true", help="Run cross-browser compatibility tests"
    )
    parser.add_argument(
        "--performance-only", action="store_true", help="Run only performance tests"
    )
    parser.add_argument(
        "--install-browsers", action="store_true", help="Install Playwright browsers"
    )

    # Utility options
    parser.add_argument(
        "--cleanup", type=int, metavar="DAYS", help="Clean up reports older than DAYS"
    )
    parser.add_argument("--project-root", help="Project root directory")

    args = parser.parse_args()

    # Initialize runner
    runner = E2ETestRunner(args.project_root)

    # Handle utility actions
    if args.cleanup:
        runner.cleanup_old_reports(args.cleanup)
        return

    if args.install_browsers:
        success = runner.install_playwright_browsers()
        sys.exit(0 if success else 1)

    # Check prerequisites
    if not runner.check_prerequisites():
        logger.error("❌ Prerequisites not met")
        sys.exit(1)

    # Handle special test modes
    if args.cross_browser:
        success = runner.run_browser_compatibility_tests()
        sys.exit(0 if success else 1)

    if args.performance_only:
        success = runner.run_performance_suite()
        sys.exit(0 if success else 1)

    # Run standard E2E tests
    success = runner.run_e2e_tests(
        test_suite=args.suite,
        browser=args.browser,
        headed=args.headed,
        parallel=not args.no_parallel,
        verbose=args.verbose,
        markers=args.markers,
        max_failures=args.max_failures,
    )

    if success:
        logger.info("✅ E2E tests completed successfully!")
        sys.exit(0)
    else:
        logger.error("❌ E2E tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
