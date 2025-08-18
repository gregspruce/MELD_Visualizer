"""
Test runner with coverage reporting for MELD Visualizer.
Runs all test suites and generates comprehensive coverage report.
"""

import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime


def run_tests_with_coverage():
    """Run all tests with coverage measurement."""
    print("=" * 70)
    print("MELD VISUALIZER TEST SUITE WITH COVERAGE")
    print("=" * 70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Ensure pytest and coverage are installed
    required_packages = ['pytest', 'pytest-cov', 'coverage']
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            print(f"Installing {package}...")
            subprocess.run([sys.executable, "-m", "pip", "install", package])
    
    # Test categories
    test_suites = {
        "Unit Tests - Data Processing": "tests/test_data_processing.py",
        "Unit Tests - Services": "tests/test_services.py", 
        "Unit Tests - Validation": "tests/test_validation.py",
        "Integration Tests": "tests/test_integration.py",
        "Performance Tests": "tests/test_performance.py"
    }
    
    # Modules to measure coverage for
    source_modules = [
        "data_processing",
        "services",
        "callbacks",
        "config",
        "constants",
        "security_utils",
        "logging_config"
    ]
    
    results = {}
    
    # Run each test suite
    for suite_name, test_file in test_suites.items():
        print(f"\n{'=' * 50}")
        print(f"Running: {suite_name}")
        print(f"{'=' * 50}")
        
        if not Path(test_file).exists():
            print(f"[SKIP] Test file not found: {test_file}")
            results[suite_name] = {"status": "SKIPPED", "reason": "File not found"}
            continue
        
        # Run tests with coverage
        cmd = [
            sys.executable, "-m", "pytest",
            test_file,
            "--cov=" + ",".join(source_modules),
            "--cov-report=term-missing",
            "--cov-report=json",
            "--cov-append",
            "-v",
            "--tb=short"
        ]
        
        # Skip performance tests if requested
        if "Performance" in suite_name and "--skip-performance" in sys.argv:
            print("[SKIP] Skipping performance tests (use --run-all to include)")
            results[suite_name] = {"status": "SKIPPED", "reason": "Performance tests skipped"}
            continue
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Parse results
        if result.returncode == 0:
            print(f"[PASS] {suite_name}: PASSED")
            results[suite_name] = {"status": "PASSED"}
        else:
            print(f"[FAIL] {suite_name}: FAILED")
            results[suite_name] = {"status": "FAILED"}
            if result.stdout:
                print("Output:", result.stdout[-500:])  # Last 500 chars
    
    # Generate HTML coverage report
    print(f"\n{'=' * 50}")
    print("Generating Coverage Report")
    print(f"{'=' * 50}")
    
    subprocess.run([
        sys.executable, "-m", "coverage", "html",
        "--omit=*/tests/*,*/test_*.py"
    ])
    
    # Generate text report
    result = subprocess.run([
        sys.executable, "-m", "coverage", "report",
        "--omit=*/tests/*,*/test_*.py"
    ], capture_output=True, text=True)
    
    print(result.stdout)
    
    # Parse coverage.json if it exists
    coverage_file = Path("coverage.json")
    if coverage_file.exists():
        with open(coverage_file) as f:
            coverage_data = json.load(f)
        
        total_coverage = coverage_data.get("totals", {}).get("percent_covered", 0)
        
        print(f"\n{'=' * 50}")
        print("Coverage Summary")
        print(f"{'=' * 50}")
        print(f"Total Coverage: {total_coverage:.1f}%")
        
        # Module-level coverage
        files = coverage_data.get("files", {})
        module_coverage = {}
        
        for file_path, file_data in files.items():
            module_name = Path(file_path).stem
            if module_name not in ["__init__", "test_"] and not module_name.startswith("test_"):
                coverage_pct = file_data["summary"]["percent_covered"]
                module_coverage[module_name] = coverage_pct
        
        print("\nModule Coverage:")
        for module, coverage in sorted(module_coverage.items(), key=lambda x: x[1], reverse=True):
            bar = "█" * int(coverage / 5) + "░" * (20 - int(coverage / 5))
            print(f"  {module:25} {bar} {coverage:5.1f}%")
    
    # Test results summary
    print(f"\n{'=' * 50}")
    print("Test Results Summary")
    print(f"{'=' * 50}")
    
    passed = sum(1 for r in results.values() if r["status"] == "PASSED")
    failed = sum(1 for r in results.values() if r["status"] == "FAILED")
    skipped = sum(1 for r in results.values() if r["status"] == "SKIPPED")
    
    for suite, result in results.items():
        status_icon = {"PASSED": "[PASS]", "FAILED": "[FAIL]", "SKIPPED": "[SKIP]"}.get(result["status"], "?")
        print(f"{status_icon} {suite}: {result['status']}")
        if "reason" in result:
            print(f"   Reason: {result['reason']}")
    
    print(f"\nTotal: {passed} passed, {failed} failed, {skipped} skipped")
    
    # Generate markdown report
    generate_markdown_report(results, module_coverage if 'module_coverage' in locals() else {}, total_coverage if 'total_coverage' in locals() else 0)
    
    print(f"\n{'=' * 50}")
    print("Reports Generated:")
    print(f"{'=' * 50}")
    print("HTML Report: htmlcov/index.html")
    print("Markdown Report: test_coverage_report.md")
    print("JSON Data: coverage.json")
    
    return 0 if failed == 0 else 1


def generate_markdown_report(results, module_coverage, total_coverage):
    """Generate markdown coverage report."""
    report = []
    report.append("# MELD Visualizer Test Coverage Report")
    report.append(f"\n**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"\n**Total Coverage**: {total_coverage:.1f}%")
    
    # Test results
    report.append("\n## Test Suite Results\n")
    report.append("| Test Suite | Status | Notes |")
    report.append("|------------|--------|-------|")
    
    for suite, result in results.items():
        status = result["status"]
        notes = result.get("reason", "-")
        report.append(f"| {suite} | {status} | {notes} |")
    
    # Module coverage
    if module_coverage:
        report.append("\n## Module Coverage\n")
        report.append("| Module | Coverage | Visualization |")
        report.append("|--------|----------|---------------|")
        
        for module, coverage in sorted(module_coverage.items(), key=lambda x: x[1], reverse=True):
            bar = "#" * int(coverage / 10) + "-" * (10 - int(coverage / 10))
            report.append(f"| {module} | {coverage:.1f}% | {bar} |")
    
    # Coverage targets
    report.append("\n## Coverage Analysis\n")
    
    if total_coverage >= 80:
        report.append("**Excellent**: Coverage exceeds 80% target")
    elif total_coverage >= 60:
        report.append("**Good**: Coverage is acceptable but could be improved")
    else:
        report.append("**Needs Improvement**: Coverage below 60% threshold")
    
    # Recommendations
    report.append("\n## Recommendations\n")
    
    if module_coverage:
        low_coverage = [m for m, c in module_coverage.items() if c < 60]
        if low_coverage:
            report.append(f"- **Low Coverage Modules**: {', '.join(low_coverage)}")
            report.append("  - Add more unit tests for these modules")
    
    report.append("- Run tests regularly during development")
    report.append("- Aim for 80%+ coverage on critical modules")
    report.append("- Focus on edge cases and error handling")
    
    # Write report
    with open("test_coverage_report.md", "w") as f:
        f.write("\n".join(report))


if __name__ == "__main__":
    sys.exit(run_tests_with_coverage())