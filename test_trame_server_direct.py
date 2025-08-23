#!/usr/bin/env python
"""
Direct test of Trame server to verify it's serving content properly.
"""

import sys
import os
import time
import requests

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_trame_server():
    """Test that Trame server starts and serves content."""
    print("\n" + "="*60)
    print("Direct Trame Server Test")
    print("="*60)
    
    # Import and create server
    from src.meld_visualizer.core.trame_server_simple import SimplifiedTrameServer
    
    print("\n1. Creating Trame server...")
    server = SimplifiedTrameServer(port=8051)
    
    print("2. Initializing server...")
    if server.initialize():
        print("   ✓ Server initialized successfully")
    else:
        print("   ✗ Server initialization failed")
        return
    
    # Give server time to start
    print("3. Waiting for server to start...")
    time.sleep(3)
    
    # Test if server is responding
    print("4. Testing server response...")
    try:
        response = requests.get("http://localhost:8051/", timeout=5)
        print(f"   Status code: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('Content-Type', 'Not set')}")
        print(f"   Content length: {len(response.content)} bytes")
        
        # Check if it's HTML
        if response.status_code == 200:
            print("   ✓ Server is responding")
            
            # Check for Trame/VTK content
            content = response.text
            if "trame" in content.lower() or "vtk" in content.lower():
                print("   ✓ Response contains Trame/VTK content")
            else:
                print("   ⚠ Response doesn't contain expected Trame/VTK content")
                
            # Save response for inspection
            with open("trame_response.html", "w") as f:
                f.write(content)
            print("   Response saved to trame_response.html for inspection")
        else:
            print(f"   ✗ Server returned status {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("   ✗ Cannot connect to server on port 8051")
    except requests.exceptions.Timeout:
        print("   ✗ Server request timed out")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print("\n5. Creating test mesh...")
    try:
        import pyvista as pv
        import numpy as np
        
        # Create simple test mesh
        vertices = np.array([
            [0, 0, 0],
            [1, 0, 0],
            [1, 1, 0],
            [0, 1, 0],
            [0, 0, 1],
            [1, 0, 1],
            [1, 1, 1],
            [0, 1, 1]
        ])
        
        # Create a simple cube
        mesh = pv.PolyData(vertices)
        mesh = mesh.delaunay_3d()
        
        print(f"   Created mesh with {mesh.n_points} points")
        
        # Load mesh into server
        if server.load_mesh(mesh):
            print("   ✓ Mesh loaded into server")
        else:
            print("   ✗ Failed to load mesh")
            
    except Exception as e:
        print(f"   ✗ Error creating mesh: {e}")
    
    # Test server again after loading mesh
    print("\n6. Testing server after mesh load...")
    time.sleep(2)
    
    try:
        response = requests.get("http://localhost:8051/", timeout=5)
        if response.status_code == 200:
            print("   ✓ Server still responding after mesh load")
        else:
            print(f"   ✗ Server returned status {response.status_code}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print("\n7. Checking server internals...")
    print(f"   Server initialized: {server.initialized}")
    print(f"   Has plotter: {server.plotter is not None}")
    print(f"   Has mesh: {server.mesh is not None}")
    print(f"   Has server object: {server.server is not None}")
    
    if server.server:
        print(f"   Server state: {getattr(server.server, 'state', 'No state attr')}")
    
    # Keep server running for manual inspection
    print("\n" + "="*60)
    print("Server is running on http://localhost:8051/")
    print("Press Ctrl+C to stop...")
    print("="*60)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.close()
        print("Server closed.")

if __name__ == "__main__":
    test_trame_server()