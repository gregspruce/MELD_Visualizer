#!/usr/bin/env python3
"""
Test script to validate the PyVista/Trame display fixes.

This script tests the core functionality without running the full Dash app.
"""

import sys
import os
import logging

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_trame_server_creation():
    """Test that the Trame server can be created and initialized."""
    print("Testing Trame server creation...")
    
    try:
        from src.meld_visualizer.core.trame_server_simple import SimplifiedTrameServer
        
        # Create server
        server = SimplifiedTrameServer(port=8052)  # Different port for testing
        
        # Try to initialize
        success = server.initialize()
        print(f"Server initialization: {'SUCCESS' if success else 'FAILED'}")
        
        if success:
            print(f"Server created on port {server.port}")
            print(f"Plotter available: {server.plotter is not None}")
            print(f"Trame server available: {server.server is not None}")
            
            # Test URL generation
            if server.server:
                url = f"http://localhost:{server.port}/"
                print(f"Expected iframe URL: {url}")
            
            # Clean up
            server.close()
            print("Server closed successfully")
            
        return success
        
    except Exception as e:
        print(f"Error testing Trame server: {e}")
        return False

def test_pyvista_integration():
    """Test the PyVista integration component."""
    print("\nTesting PyVista integration...")
    
    try:
        from src.meld_visualizer.components.pyvista_simple import SimplePyVistaIntegration
        
        # Create integration instance
        integration = SimplePyVistaIntegration()
        
        # Test placeholder component creation
        component = integration.get_placeholder_component()
        print(f"Placeholder component created: {component is not None}")
        
        # Test server initialization
        success = integration.initialize_server(port=8053)  # Different port for testing
        print(f"Integration initialization: {'SUCCESS' if success else 'FAILED'}")
        
        if success:
            # Test iframe URL generation
            url = integration.get_iframe_src()
            print(f"Iframe URL: {url}")
            print(f"URL is valid: {bool(url and 'localhost' in url)}")
        
        return success
        
    except Exception as e:
        print(f"Error testing PyVista integration: {e}")
        return False

def test_mesh_creation():
    """Test mesh creation with sample data."""
    print("\nTesting mesh creation with sample data...")
    
    try:
        import numpy as np
        from src.meld_visualizer.components.pyvista_simple import SimplePyVistaIntegration
        
        # Create sample mesh data
        vertices = np.array([
            [0, 0, 0],
            [1, 0, 0], 
            [1, 1, 0],
            [0, 1, 0]
        ])
        faces = np.array([[0, 1, 2], [0, 2, 3]])
        scalars = np.array([0, 1, 2, 3])
        
        print(f"Sample data: {len(vertices)} vertices, {len(faces)} faces")
        
        # Create integration and test mesh update
        integration = SimplePyVistaIntegration()
        success = integration.update_mesh_from_data(vertices, faces, scalars)
        
        print(f"Mesh creation: {'SUCCESS' if success else 'FAILED'}")
        
        if success and integration.mesh:
            print(f"Mesh points: {integration.mesh.n_points}")
            print(f"Mesh cells: {integration.mesh.n_cells}")
            
            # Test screenshot export
            screenshot_success = False
            if integration.server and integration.server.plotter:
                screenshot_success = integration.server.export_screenshot("test_screenshot.png")
                print(f"Screenshot export: {'SUCCESS' if screenshot_success else 'FAILED'}")
        
        return success
        
    except Exception as e:
        print(f"Error testing mesh creation: {e}")
        return False

def main():
    """Run all tests."""
    print("=== Testing PyVista/Trame Display Fixes ===\n")
    
    tests = [
        ("Trame Server Creation", test_trame_server_creation),
        ("PyVista Integration", test_pyvista_integration),
        ("Mesh Creation", test_mesh_creation)
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"EXCEPTION in {test_name}: {e}")
            results[test_name] = False
    
    # Summary
    print("\n=== Test Results Summary ===")
    for test_name, success in results.items():
        status = "PASS" if success else "FAIL"
        print(f"{test_name}: {status}")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    print(f"\nPassed: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! The PyVista display fixes should work.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()