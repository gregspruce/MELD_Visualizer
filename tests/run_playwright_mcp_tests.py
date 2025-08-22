#!/usr/bin/env python3
"""
Playwright MCP Test Runner for MELD Visualizer
Integrates Python test orchestration with Playwright MCP browser automation
"""

import os
import sys
import json
import subprocess
import argparse
import time
from pathlib import Path
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PlaywrightMCPRunner:
    """Main runner for Playwright MCP tests"""
    
    def __init__(self, project_root=None):
        self.project_root = Path(project_root or os.getcwd())
        self.playwright_dir = self.project_root / "tests" / "playwright"
        self.reports_dir = self.project_root / "tests" / "reports"
        self.config_path = self.playwright_dir / "config" / "playwright.config.js"
        
        # Ensure directories exist
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
    def check_prerequisites(self):
        """Check if all prerequisites are met"""
        logger.info("🔍 Checking prerequisites...")
        
        # Check Node.js
        try:
            result = subprocess.run(['node', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"✅ Node.js version: {result.stdout.strip()}")
            else:
                raise Exception("Node.js not found")
        except:
            logger.error("❌ Node.js is required but not installed")
            return False
            
        # Check if Playwright is installed
        package_json_path = self.playwright_dir / "package.json"
        if not package_json_path.exists():
            logger.error("❌ package.json not found in playwright directory")
            return False
            
        # Check if MELD Visualizer server is running
        import requests
        try:
            response = requests.get("http://localhost:8050", timeout=5)
            if response.status_code == 200:
                logger.info("✅ MELD Visualizer server is running")
            else:
                logger.warning("⚠️  MELD Visualizer server responded with non-200 status")
        except:
            logger.error("❌ MELD Visualizer server not accessible at http://localhost:8050")
            logger.error("   Please start the server with: python -m meld_visualizer")
            return False
            
        return True
    
    def install_dependencies(self):
        """Install Node.js dependencies and Playwright browsers"""
        logger.info("📦 Installing dependencies...")
        
        # Change to playwright directory
        os.chdir(self.playwright_dir)
        
        # Install npm dependencies
        try:
            subprocess.run(['npm', 'install'], check=True)
            logger.info("✅ npm dependencies installed")
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to install npm dependencies: {e}")
            return False
            
        # Install Playwright browsers
        try:
            subprocess.run(['npx', 'playwright', 'install'], check=True)
            logger.info("✅ Playwright browsers installed")
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to install Playwright browsers: {e}")
            return False
            
        return True
    
    def run_tests(self, test_type="all", project=None, headed=False, debug=False, workers=None):
        """Run Playwright MCP tests"""
        logger.info(f"🚀 Starting Playwright MCP tests ({test_type})...")
        
        # Change to playwright directory
        os.chdir(self.playwright_dir)
        
        # Build command
        cmd = ['npx', 'playwright', 'test']
        
        # Add configuration
        cmd.extend(['--config', 'config/playwright.config.js'])
        
        # Test type selection
        if test_type != "all":
            if test_type == "e2e":
                cmd.append('e2e/')
            elif test_type == "integration":
                cmd.append('integration/')
            elif test_type == "performance":
                cmd.append('performance/')
            elif test_type == "visual":
                cmd.append('visual/')
            else:
                logger.warning(f"Unknown test type: {test_type}, running all tests")
        
        # Project selection
        if project:
            cmd.extend(['--project', project])
            
        # Headed mode
        if headed:
            cmd.append('--headed')
            
        # Debug mode
        if debug:
            cmd.append('--debug')
            
        # Workers
        if workers:
            cmd.extend(['--workers', str(workers)])
            
        # Additional MCP-specific options
        cmd.extend([
            '--reporter=html,json,junit',
            f'--output-dir={self.reports_dir}/test-results'
        ])
        
        logger.info(f"📋 Command: {' '.join(cmd)}")
        
        # Run tests
        start_time = time.time()
        try:
            result = subprocess.run(cmd, check=False)
            end_time = time.time()
            
            duration = end_time - start_time
            logger.info(f"⏱️  Test execution completed in {duration:.2f} seconds")
            
            # Generate summary report
            self.generate_summary_report(result.returncode, duration, test_type)
            
            return result.returncode == 0
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Test execution failed: {e}")
            return False
    
    def generate_summary_report(self, exit_code, duration, test_type):
        """Generate a summary report of the test run"""
        timestamp = datetime.now().isoformat()
        
        # Read test results if available
        results_file = self.reports_dir / "test-results.json"
        test_results = {}
        if results_file.exists():
            try:
                with open(results_file, 'r') as f:
                    test_results = json.load(f)
            except:
                pass
        
        # Create summary
        summary = {
            "timestamp": timestamp,
            "test_type": test_type,
            "exit_code": exit_code,
            "duration_seconds": duration,
            "success": exit_code == 0,
            "playwright_mcp_version": "1.0.0",
            "test_results": test_results,
            "reports": {
                "html": f"{self.reports_dir}/playwright-report/index.html",
                "json": f"{self.reports_dir}/test-results.json",
                "junit": f"{self.reports_dir}/junit-results.xml",
                "videos": f"{self.reports_dir}/videos/",
                "screenshots": f"{self.reports_dir}/screenshots/",
                "network_logs": f"{self.reports_dir}/network/"
            }
        }
        
        # Write summary
        summary_file = self.reports_dir / "mcp-test-summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
            
        # Print summary
        status = "✅ PASSED" if exit_code == 0 else "❌ FAILED"
        logger.info(f"📊 Test Summary ({status}):")
        logger.info(f"   Duration: {duration:.2f}s")
        logger.info(f"   Reports: {self.reports_dir}")
        
        if test_results.get('stats'):
            stats = test_results['stats']
            logger.info(f"   Tests: {stats.get('expected', 0)} passed, {stats.get('failed', 0)} failed")
    
    def run_codegen(self, url=None):
        """Run Playwright code generation"""
        logger.info("🎬 Starting Playwright MCP code generation...")
        
        os.chdir(self.playwright_dir)
        
        cmd = ['npx', 'playwright', 'codegen']
        if url:
            cmd.append(url)
        else:
            cmd.append('http://localhost:8050')
            
        try:
            subprocess.run(cmd, check=True)
            logger.info("✅ Code generation completed")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Code generation failed: {e}")
            return False
    
    def show_report(self):
        """Show the HTML test report"""
        report_path = self.reports_dir / "playwright-report" / "index.html"
        if report_path.exists():
            logger.info(f"📊 Opening test report: {report_path}")
            os.chdir(self.playwright_dir)
            subprocess.run(['npx', 'playwright', 'show-report'], check=False)
        else:
            logger.warning("❌ No test report found. Run tests first.")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Playwright MCP Test Runner for MELD Visualizer")
    parser.add_argument("--type", choices=["all", "e2e", "integration", "performance", "visual"], 
                       default="all", help="Type of tests to run")
    parser.add_argument("--project", help="Specific browser project to run")
    parser.add_argument("--headed", action="store_true", help="Run tests in headed mode")
    parser.add_argument("--debug", action="store_true", help="Run tests in debug mode")
    parser.add_argument("--workers", type=int, help="Number of parallel workers")
    parser.add_argument("--install", action="store_true", help="Install dependencies and browsers")
    parser.add_argument("--codegen", action="store_true", help="Run code generation")
    parser.add_argument("--url", help="URL for code generation")
    parser.add_argument("--report", action="store_true", help="Show test report")
    parser.add_argument("--project-root", help="Project root directory")
    
    args = parser.parse_args()
    
    # Initialize runner
    runner = PlaywrightMCPRunner(args.project_root)
    
    # Handle specific actions
    if args.install:
        logger.info("🔧 Installing Playwright MCP dependencies...")
        if not runner.install_dependencies():
            sys.exit(1)
        logger.info("✅ Installation completed")
        return
    
    if args.codegen:
        if not runner.run_codegen(args.url):
            sys.exit(1)
        return
        
    if args.report:
        runner.show_report()
        return
    
    # Check prerequisites
    if not runner.check_prerequisites():
        logger.error("❌ Prerequisites not met")
        sys.exit(1)
    
    # Run tests
    success = runner.run_tests(
        test_type=args.type,
        project=args.project,
        headed=args.headed,
        debug=args.debug,
        workers=args.workers
    )
    
    if not success:
        logger.error("❌ Test execution failed")
        sys.exit(1)
    
    logger.info("✅ All tests completed successfully")

if __name__ == "__main__":
    main()