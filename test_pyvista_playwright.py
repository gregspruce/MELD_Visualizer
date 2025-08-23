#!/usr/bin/env python
"""
Test PyVista display with Playwright to verify the iframe shows correctly.
"""

import asyncio
import sys
import os
import time
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_pyvista_display():
    """Test PyVista display using Playwright."""
    from playwright.async_api import async_playwright
    
    print("\n" + "="*60)
    print("PyVista Display Test with Playwright")
    print("="*60)
    
    # First, start the app in background
    import subprocess
    import threading
    
    print("\n1. Starting MELD Visualizer app...")
    app_process = subprocess.Popen(
        [sys.executable, "-m", "meld_visualizer"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for app to start
    time.sleep(5)
    
    async with async_playwright() as p:
        print("\n2. Launching browser...")
        browser = await p.chromium.launch(headless=False)  # Set to False to see what's happening
        page = await browser.new_page()
        
        # Enable console logging
        page.on("console", lambda msg: print(f"   [Browser Console]: {msg.text}"))
        page.on("pageerror", lambda err: print(f"   [Browser Error]: {err}"))
        
        try:
            print("\n3. Navigating to app...")
            await page.goto("http://localhost:8050", wait_until="networkidle")
            await page.wait_for_timeout(2000)
            
            # Take initial screenshot
            await page.screenshot(path="test_1_initial.png")
            print("   Screenshot saved: test_1_initial.png")
            
            # Find and click file upload to load test data
            print("\n4. Loading test data...")
            # Get the test data file path
            test_data = Path(__file__).parent / "tests" / "playwright" / "fixtures" / "test_data" / "sample_meld_data.csv"
            
            if test_data.exists():
                print(f"   Using test data: {test_data}")
                file_input = await page.query_selector("input[type='file']")
                if file_input:
                    await file_input.set_input_files(str(test_data))
                    await page.wait_for_timeout(2000)
                    print("   Test data loaded")
            else:
                print("   Test data file not found, skipping data load")
            
            # Navigate to PyVista tab
            print("\n5. Navigating to PyVista tab...")
            pyvista_tab = await page.query_selector("text='3D PyVista (Beta)'")
            if pyvista_tab:
                await pyvista_tab.click()
                await page.wait_for_timeout(1000)
                print("   PyVista tab clicked")
                
                # Take screenshot of PyVista tab
                await page.screenshot(path="test_2_pyvista_tab.png")
                print("   Screenshot saved: test_2_pyvista_tab.png")
            else:
                print("   [ERROR] PyVista tab not found!")
                
            # Check iframe initial state
            print("\n6. Checking iframe initial state...")
            iframe = await page.query_selector("#pyvista-iframe")
            if iframe:
                iframe_style = await iframe.get_attribute("style")
                print(f"   Initial iframe style: {iframe_style}")
                
                # Check if iframe is hidden
                is_visible = await iframe.is_visible()
                print(f"   Initial iframe visible: {is_visible}")
            else:
                print("   [ERROR] iframe not found!")
            
            # Click Initialize button
            print("\n7. Clicking Initialize PyVista button...")
            init_button = await page.query_selector("#init-pyvista-btn")
            if init_button:
                await init_button.click()
                print("   Button clicked, waiting for initialization...")
                await page.wait_for_timeout(5000)  # Give it time to initialize
                
                # Check status message
                status_msg = await page.query_selector("#pyvista-status-message")
                if status_msg:
                    status_text = await status_msg.inner_text()
                    print(f"   Status message: {status_text}")
                
                # Take screenshot after initialization
                await page.screenshot(path="test_3_after_init.png")
                print("   Screenshot saved: test_3_after_init.png")
            else:
                print("   [ERROR] Initialize button not found!")
            
            # Check iframe after initialization
            print("\n8. Checking iframe after initialization...")
            if iframe:
                iframe_src = await iframe.get_attribute("src")
                iframe_style = await iframe.get_attribute("style")
                is_visible = await iframe.is_visible()
                
                print(f"   iframe src: {iframe_src}")
                print(f"   iframe style: {iframe_style}")
                print(f"   iframe visible: {is_visible}")
                
                if iframe_src and iframe_src.startswith("http://"):
                    print("   [SUCCESS] iframe has valid src URL!")
                else:
                    print("   [WARNING] iframe src not set properly")
                    
                if is_visible:
                    print("   [SUCCESS] iframe is visible!")
                else:
                    print("   [WARNING] iframe is still hidden")
            
            # Check for any errors in console
            print("\n9. Final state check...")
            await page.screenshot(path="test_4_final.png")
            print("   Final screenshot saved: test_4_final.png")
            
        finally:
            print("\n10. Cleaning up...")
            await browser.close()
            app_process.terminate()
            print("   Browser closed and app terminated")
    
    print("\n" + "="*60)
    print("Test complete! Check the screenshots:")
    print("- test_1_initial.png - App start")
    print("- test_2_pyvista_tab.png - PyVista tab")
    print("- test_3_after_init.png - After initialization")
    print("- test_4_final.png - Final state")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(test_pyvista_display())