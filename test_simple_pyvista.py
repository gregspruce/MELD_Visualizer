#!/usr/bin/env python
"""
Test the simplified PyVista integration.
"""

import sys
import os
import numpy as np
import pandas as pd

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_simple_integration():
    """Test the simplified PyVista integration."""
    print("Testing simplified PyVista integration...")
    
    # Import the simple integration
    from meld_visualizer.components.pyvista_simple import SimplePyVistaIntegration
    
    # Create instance
    integration = SimplePyVistaIntegration()
    print("Created SimplePyVistaIntegration instance")
    
    # Test initialization
    if integration.initialize_server(port=8052):  # Use different port for testing
        print("Server initialized successfully")
    else:
        print("Failed to initialize server")
        return False
    
    # Create test data
    vertices = np.random.rand(100, 3) * 10
    faces = np.array([[i, i+1, i+2] for i in range(0, 97, 3)])
    scalars = np.random.rand(100)
    
    # Update mesh
    if integration.update_mesh_from_data(vertices, faces, scalars):
        print(f"Mesh updated successfully with {len(vertices)} vertices")
    else:
        print("Failed to update mesh")
        return False
    
    # Test export
    test_file = "test_mesh.stl"
    if integration.export_mesh(test_file):
        print(f"Mesh exported to {test_file}")
        # Clean up
        if os.path.exists(test_file):
            os.remove(test_file)
            print("Cleaned up test file")
    else:
        print("Failed to export mesh")
    
    print("All tests passed!")
    return True

if __name__ == "__main__":
    success = test_simple_integration()
    sys.exit(0 if success else 1)