#!/usr/bin/env python
"""
Debug test to check if PyVista callback is working.
"""

import sys
import os
import time
import subprocess

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_callback():
    """Test PyVista callback directly."""
    print("\n" + "="*60)
    print("PyVista Callback Debug Test")
    print("="*60)
    
    # Start the app
    print("\n1. Starting MELD Visualizer app...")
    app_process = subprocess.Popen(
        [sys.executable, "-m", "meld_visualizer"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    # Monitor output for a few seconds
    print("\n2. Monitoring app output for callback registration...")
    start_time = time.time()
    callback_found = False
    
    while time.time() - start_time < 10:
        line = app_process.stdout.readline()
        if line:
            print(f"   APP: {line.strip()}")
            if "pyvista" in line.lower() and "callback" in line.lower():
                callback_found = True
                print("   [OK] PyVista callback registration detected!")
        
        # Check if app is running
        if "Dash is running on" in line:
            print("   [OK] App started successfully")
            break
    
    if not callback_found:
        print("   [WARNING] No explicit PyVista callback registration message found")
    
    # Keep app running for manual testing
    print("\n3. App is running. You can now:")
    print("   - Open http://localhost:8050 in your browser")
    print("   - Load the test CSV file")
    print("   - Navigate to PyVista tab")
    print("   - Click 'Initialize PyVista Renderer'")
    print("   - Watch the console output below for errors")
    print("\n4. Monitoring app output (Ctrl+C to stop)...")
    print("-" * 60)
    
    try:
        while True:
            line = app_process.stdout.readline()
            if line:
                print(f"APP: {line.strip()}")
                
                # Look for specific error patterns
                if "error" in line.lower():
                    print(f">>> ERROR DETECTED: {line.strip()}")
                if "traceback" in line.lower():
                    print(f">>> TRACEBACK DETECTED - Error details follow:")
                if "pyvista" in line.lower():
                    print(f">>> PYVISTA MESSAGE: {line.strip()}")
                    
    except KeyboardInterrupt:
        print("\n\n5. Shutting down...")
        app_process.terminate()
        print("   App terminated")
    
    print("\n" + "="*60)
    print("Debug test complete")
    print("="*60)

if __name__ == "__main__":
    test_callback()