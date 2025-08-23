#!/usr/bin/env python
"""
Test script to verify PyVista/Trame integration with MELD Visualizer.

This script tests the complete migration from Plotly to PyVista for 3D volume mesh visualization.
"""

import sys
import os
import time
import numpy as np
import pandas as pd

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_pyvista_mesh_generation():
    """Test PyVista mesh generation module."""
    print("\n" + "="*60)
    print("Testing PyVista Mesh Generation")
    print("="*60)
    
    try:
        from meld_visualizer.core.pyvista_mesh import PyVistaMeshGenerator
        
        # Create mesh generator
        generator = PyVistaMeshGenerator()
        print("[OK] PyVistaMeshGenerator imported successfully")
        
        # Test with sample data
        num_points = 100
        points = np.random.rand(num_points, 3) * 100
        feedstock_area = 0.5 * 0.5 * 25.4 * 25.4  # Square rod
        velocities = np.random.rand(num_points) * 10
        
        # Test swept mesh generation
        mesh = generator.generate_swept_mesh(
            points=points,
            feedstock_area=feedstock_area,
            velocities=velocities
        )
        
        print(f"[OK] Created swept mesh with {mesh.n_points} vertices and {mesh.n_cells} faces")
        
        # Test optimization
        optimized = generator.optimize_for_web(mesh, target_reduction=0.5)
        print(f"[OK] Optimized mesh to {optimized.n_points} vertices ({(1-optimized.n_points/mesh.n_points)*100:.1f}% reduction)")
        
        # Test conversion from Plotly format
        vertices = np.random.rand(50, 3) * 100
        faces = np.array([[i, i+1, i+2] for i in range(0, 47, 3)])
        scalars = np.random.rand(50)
        
        plotly_mesh = generator.create_mesh_from_plotly_data(
            vertices=vertices,
            faces=faces,
            scalars=scalars
        )
        
        print(f"[OK] Converted Plotly mesh format successfully")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False


def test_trame_server():
    """Test Trame server module."""
    print("\n" + "="*60)
    print("Testing Trame Server")
    print("="*60)
    
    try:
        from meld_visualizer.core.trame_server import TrameVisualizationServer
        
        # Create server instance
        server = TrameVisualizationServer(port=8051)
        print("[OK] TrameServer imported successfully")
        
        # Test mesh loading
        import pyvista as pv
        sphere = pv.Sphere()
        server.load_mesh(sphere)
        print("[OK] Loaded test mesh into server")
        
        # Test state management
        server.update_color_map("viridis")
        print("[OK] Updated color map")
        
        server.set_lod("medium")
        print("[OK] Set level of detail")
        
        # Don't actually start the server in test mode
        print("[OK] Server ready (not started in test mode)")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False


def test_dash_integration():
    """Test Dash integration component."""
    print("\n" + "="*60)
    print("Testing Dash Integration")
    print("="*60)
    
    try:
        from meld_visualizer.components.trame_integration import DashTrameIntegration
        
        # Create integration instance
        integration = DashTrameIntegration()
        print("[OK] TrameIntegration imported successfully")
        
        # Test iframe component generation
        iframe = integration.get_iframe_component()
        print(f"[OK] Generated iframe component")
        
        # Test mesh update
        import pyvista as pv
        test_mesh = pv.Cube()
        integration.update_mesh(test_mesh)
        print("[OK] Updated mesh through integration")
        
        # Test export functionality
        success = integration.export_mesh("test_export.stl")
        if success:
            print("[OK] Export functionality available")
            # Clean up test file
            if os.path.exists("test_export.stl"):
                os.remove("test_export.stl")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False


def test_performance_comparison():
    """Compare Plotly vs PyVista performance."""
    print("\n" + "="*60)
    print("Performance Comparison: Plotly vs PyVista")
    print("="*60)
    
    try:
        from meld_visualizer.core.volume_mesh import MeshGenerator as PlotlyMeshGenerator
        from meld_visualizer.core.pyvista_mesh import PyVistaMeshGenerator
        
        # Generate test data
        num_points = 1000
        points = np.random.rand(num_points, 3) * 100
        feedstock_area = 0.5 * 0.5 * 25.4 * 25.4
        velocities = np.random.rand(num_points) * 10
        
        # Create sample DataFrame for Plotly
        df = pd.DataFrame({
            'XPos': points[:, 0],
            'YPos': points[:, 1],
            'ZPos': points[:, 2],
            'FeedVel': velocities,
            'PathVel': np.ones(num_points) * 5
        })
        
        # Time Plotly mesh generation
        plotly_gen = PlotlyMeshGenerator()
        start = time.time()
        # Use the generate_mesh method that exists
        plotly_mesh = plotly_gen.generate_mesh(
            df,
            points_per_section=8
        )
        plotly_time = time.time() - start
        
        # Time PyVista mesh generation
        pyvista_gen = PyVistaMeshGenerator()
        start = time.time()
        pyvista_mesh = pyvista_gen.generate_swept_mesh(
            points=points,
            feedstock_area=feedstock_area,
            velocities=velocities
        )
        pyvista_time = time.time() - start
        
        # Calculate speedup
        speedup = plotly_time / pyvista_time if pyvista_time > 0 else 0
        
        print(f"Dataset size: {num_points} points")
        print(f"Plotly generation time: {plotly_time:.3f}s")
        print(f"PyVista generation time: {pyvista_time:.3f}s")
        print(f"Speedup: {speedup:.1f}x faster")
        
        if speedup > 1:
            print(f"[OK] PyVista is {speedup:.1f}x faster than Plotly")
        else:
            print(f"[WARNING] Performance comparison inconclusive")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False


def test_callback_integration():
    """Test PyVista callbacks integration."""
    print("\n" + "="*60)
    print("Testing PyVista Callbacks")
    print("="*60)
    
    try:
        from meld_visualizer.callbacks.pyvista_callbacks import (
            mesh_generator,
            trame_integration,
            data_service
        )
        
        print("[OK] PyVista callbacks imported successfully")
        print(f"[OK] Mesh generator instance: {type(mesh_generator).__name__}")
        print(f"[OK] Trame integration instance: {type(trame_integration).__name__}")
        print(f"[OK] Data service instance: {type(data_service).__name__}")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("MELD Visualizer PyVista Integration Test Suite")
    print("="*60)
    
    results = []
    
    # Run tests
    results.append(("PyVista Mesh Generation", test_pyvista_mesh_generation()))
    results.append(("Trame Server", test_trame_server()))
    results.append(("Dash Integration", test_dash_integration()))
    results.append(("Performance Comparison", test_performance_comparison()))
    results.append(("Callback Integration", test_callback_integration()))
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "[OK] PASSED" if result else "[FAIL] FAILED"
        print(f"{name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[SUCCESS] All tests passed! PyVista integration is ready.")
        print("\nNext steps:")
        print("1. Run the application: python -m meld_visualizer")
        print("2. Navigate to the '3D PyVista (Beta)' tab")
        print("3. Load data and click 'Initialize PyVista'")
        print("4. The Trame server will run on http://localhost:8051")
    else:
        print("\n[WARNING] Some tests failed. Please review the errors above.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)