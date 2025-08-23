#!/usr/bin/env python
"""
Test PyVista's direct show() method with Trame backend.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_direct_show():
    """Test PyVista's direct show method."""
    print("\n" + "="*60)
    print("PyVista Direct Show Test")
    print("="*60)
    
    import pyvista as pv
    import numpy as np
    
    # Set backend
    pv.set_jupyter_backend('trame')
    
    print("\n1. Creating test mesh...")
    # Create a simple test mesh
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
    
    # Create faces (PyVista format)
    faces = []
    # Bottom face
    faces.extend([4, 0, 1, 2, 3])
    # Top face
    faces.extend([4, 4, 5, 6, 7])
    # Front face
    faces.extend([4, 0, 1, 5, 4])
    # Back face
    faces.extend([4, 2, 3, 7, 6])
    # Left face
    faces.extend([4, 0, 3, 7, 4])
    # Right face
    faces.extend([4, 1, 2, 6, 5])
    
    mesh = pv.PolyData(vertices, faces)
    
    # Add scalars for coloring
    mesh["height"] = vertices[:, 2]
    
    print(f"   Created mesh with {mesh.n_points} points and {mesh.n_faces} faces")
    
    print("\n2. Creating plotter...")
    plotter = pv.Plotter(
        notebook=True,  # This enables Trame backend
        window_size=[800, 600]
    )
    
    print("3. Adding mesh to plotter...")
    plotter.add_mesh(
        mesh,
        scalars="height",
        cmap="viridis",
        show_edges=True,
        edge_color='black',
        line_width=1
    )
    
    print("\n4. Starting interactive viewer...")
    print("   This should open in your browser at http://localhost:8051")
    print("   You should be able to:")
    print("   - Rotate: Left click and drag")
    print("   - Zoom: Scroll or right click and drag")
    print("   - Pan: Middle click and drag")
    
    # Show with Trame backend
    plotter.show(
        jupyter_backend='trame',
        return_viewer=False
    )
    
    print("\n" + "="*60)
    print("Test complete")
    print("="*60)

if __name__ == "__main__":
    test_direct_show()