"""
Test script for the standalone PyVista viewer.

This demonstrates how to use the standalone viewer without any threading issues.
The viewer runs in the main thread and provides full OpenGL functionality.
"""

import sys
import numpy as np
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from meld_visualizer.core.standalone_viewer import StandaloneViewer
import pyvista as pv


def create_sample_mesh():
    """Create a sample mesh for testing."""
    # Create a sphere with some scalar data
    mesh = pv.Sphere(radius=1.0, center=(0, 0, 0), theta_resolution=30, phi_resolution=30)
    
    # Add scalar data based on z-coordinate
    mesh["elevation"] = mesh.points[:, 2]
    
    # Add some noise
    mesh["noise"] = np.random.randn(mesh.n_points) * 0.1
    
    return mesh


def test_standalone_viewer():
    """Test the standalone viewer functionality."""
    print("Testing Standalone PyVista Viewer")
    print("-" * 40)
    
    # Create viewer
    viewer = StandaloneViewer()
    print("✓ Viewer created")
    
    # Create sample mesh
    mesh = create_sample_mesh()
    print(f"✓ Sample mesh created: {mesh.n_points} points, {mesh.n_cells} cells")
    
    # Load mesh
    if viewer.load_mesh(mesh):
        print("✓ Mesh loaded successfully")
    else:
        print("✗ Failed to load mesh")
        return
    
    # Test screenshot export (off-screen rendering)
    print("\nTesting screenshot export...")
    screenshot_path = viewer.export_screenshot()
    if screenshot_path:
        print(f"✓ Screenshot saved to: {screenshot_path}")
    else:
        print("✗ Screenshot export failed")
    
    # Test HTML export
    print("\nTesting HTML export...")
    html_path = viewer.export_html()
    if html_path:
        print(f"✓ Interactive HTML saved to: {html_path}")
    else:
        print("✗ HTML export failed")
    
    # Show interactive viewer (this will block until window is closed)
    print("\nOpening interactive viewer...")
    print("Controls:")
    print("  - Left Click + Drag: Rotate")
    print("  - Right Click + Drag: Zoom")
    print("  - Middle Click + Drag: Pan")
    print("  - E: Toggle edges")
    print("  - S: Save screenshot")
    print("  - Q: Quit")
    print("-" * 40)
    
    viewer.show_interactive(
        window_size=(1024, 768),
        title="MELD Standalone Viewer Test"
    )
    
    print("\n✓ Viewer closed successfully")
    
    # Clean up
    viewer.close()
    print("✓ Resources cleaned up")


def test_with_real_mesh(filepath: str):
    """Test with a real mesh file."""
    print(f"Testing with mesh file: {filepath}")
    print("-" * 40)
    
    viewer = StandaloneViewer()
    
    try:
        # Load mesh from file
        mesh = pv.read(filepath)
        print(f"✓ Mesh loaded from file: {mesh.n_points} points, {mesh.n_cells} cells")
        
        # Load into viewer
        viewer.load_mesh(mesh)
        
        # Show interactive viewer
        viewer.show_interactive(
            window_size=(1280, 960),
            title=f"MELD Viewer - {Path(filepath).name}"
        )
        
    except Exception as e:
        print(f"✗ Error: {e}")
    finally:
        viewer.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test standalone PyVista viewer")
    parser.add_argument("--file", help="Path to mesh file to load", default=None)
    args = parser.parse_args()
    
    if args.file:
        test_with_real_mesh(args.file)
    else:
        test_standalone_viewer()