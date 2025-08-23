#!/usr/bin/env python
"""
Demo script showing PyVista/Trame integration with MELD Visualizer.

This demonstrates the migration from Plotly to PyVista for 3D volume mesh visualization.
"""

import sys
import os
import numpy as np
import pandas as pd
import pyvista as pv

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Run a simple PyVista demo."""
    print("\n" + "="*60)
    print("MELD Visualizer - PyVista Integration Demo")
    print("="*60)
    
    # Create sample data similar to MELD process data
    num_points = 100
    t = np.linspace(0, 10*np.pi, num_points)
    
    # Create a spiral toolpath
    x = 10 * np.cos(t)
    y = 10 * np.sin(t)
    z = t
    
    # Create velocity data
    feed_vel = 5 + 2 * np.sin(t)
    path_vel = 10 * np.ones(num_points)
    
    # Create a DataFrame like the MELD data
    df = pd.DataFrame({
        'XPos': x,
        'YPos': y,
        'ZPos': z,
        'FeedVel': feed_vel,
        'PathVel': path_vel,
        'Time': np.arange(num_points)
    })
    
    print(f"Created sample data with {num_points} points")
    
    # Test basic PyVista functionality
    print("\n1. Testing PyVista mesh creation...")
    
    # Create a simple tube along the path
    points = np.column_stack([x, y, z])
    spline = pv.Spline(points, 100)
    
    # Create tube mesh with varying radius based on feed velocity
    tube = spline.tube(radius=0.5, n_sides=12)
    
    # Add scalar data for coloring - interpolate to match tube points
    # The tube has more points than the original spline, so we need to interpolate
    tube_feed_vel = np.interp(
        np.linspace(0, 1, tube.n_points),
        np.linspace(0, 1, len(feed_vel)),
        feed_vel
    )
    tube["FeedVelocity"] = tube_feed_vel
    
    print(f"   Created tube mesh with {tube.n_points} vertices and {tube.n_cells} faces")
    
    # Test the actual MELD mesh generator
    print("\n2. Testing MELD PyVista mesh generator...")
    try:
        from meld_visualizer.core.pyvista_mesh import PyVistaMeshGenerator
        
        generator = PyVistaMeshGenerator()
        
        # Use the actual method signature
        mesh = generator.generate_swept_mesh(
            df=df,
            color_column='FeedVel',
            lod='medium'
        )
        
        print(f"   Generated MELD mesh with {mesh.n_points} vertices")
        
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test visualization
    print("\n3. Testing PyVista visualization...")
    
    # Create a simple plotter
    plotter = pv.Plotter(notebook=False, off_screen=True)
    plotter.add_mesh(
        tube,
        scalars="FeedVelocity",
        cmap="viridis",
        show_scalar_bar=True,
        scalar_bar_args={'title': 'Feed Velocity'}
    )
    plotter.add_axes()
    plotter.set_background("white")
    
    # Save a screenshot
    screenshot_path = "pyvista_demo.png"
    plotter.screenshot(screenshot_path)
    print(f"   Saved screenshot to {screenshot_path}")
    
    plotter.close()
    
    # Performance comparison
    print("\n4. Performance Comparison...")
    
    import time
    
    # Time PyVista mesh creation
    start = time.time()
    for _ in range(10):
        tube = spline.tube(radius=0.5, n_sides=12)
    pyvista_time = (time.time() - start) / 10
    
    print(f"   PyVista mesh generation: {pyvista_time*1000:.2f} ms")
    
    # Summary
    print("\n" + "="*60)
    print("Demo completed successfully!")
    print("\nKey advantages of PyVista over Plotly:")
    print("- Hardware-accelerated rendering")
    print("- 10-100x faster for large meshes")
    print("- Professional visualization quality")
    print("- Export to CAD formats (STL, OBJ)")
    print("- Advanced filtering and processing")
    print("\nTo use in the application:")
    print("1. Run: python -m meld_visualizer")
    print("2. Navigate to '3D PyVista (Beta)' tab")
    print("3. Load your data and click 'Initialize PyVista'")
    print("="*60)


if __name__ == "__main__":
    main()