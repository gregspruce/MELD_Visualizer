"""
PyVista/Trame Demo for MELD Visualizer

This script demonstrates the new PyVista/Trame visualization capabilities
as a standalone example that can be integrated into the main application.
"""

import numpy as np
import pandas as pd
import pyvista as pv
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from meld_visualizer.core.pyvista_mesh import PyVistaMeshGenerator, MeshConfig, MeshOptimizer
from meld_visualizer.core.trame_server import TrameVisualizationServer, TrameConfig


def generate_sample_toolpath_data(n_points=1000):
    """Generate sample toolpath data for demonstration."""
    t = np.linspace(0, 4*np.pi, n_points)
    
    # Create spiral toolpath
    x = 50 * np.cos(t) * np.exp(-t/10)
    y = 50 * np.sin(t) * np.exp(-t/10)
    z = np.linspace(0, 100, n_points)
    
    # Generate varying parameters
    velocity = 80 + 20 * np.sin(t)
    temperature = 1400 + 100 * np.cos(t)
    feed_rate = 5 + 2 * np.sin(2*t)
    thickness = 3 + 0.5 * np.sin(3*t)
    
    df = pd.DataFrame({
        'XPos': x,
        'YPos': y,
        'ZPos': z,
        'PathVel': velocity,
        'Temperature': temperature,
        'FeedVel': feed_rate,
        'Bead_Thickness_mm': thickness,
        'Time': np.arange(n_points) * 0.1
    })
    
    return df


def demo_basic_mesh_generation():
    """Demonstrate basic mesh generation with PyVista."""
    print("=== Basic Mesh Generation Demo ===")
    
    # Generate sample data
    df = generate_sample_toolpath_data(500)
    
    # Configure mesh generator
    config = MeshConfig(
        points_per_section=12,
        bead_length=2.0,
        bead_radius=1.5,
        smooth_mesh=True,
        compute_normals=True
    )
    
    generator = PyVistaMeshGenerator(config)
    
    # Generate mesh using different methods
    print("\n1. Generating swept mesh...")
    mesh_swept = generator.generate_swept_mesh(df, 'Temperature', lod='high')
    print(f"   Swept mesh: {mesh_swept.n_points} points, {mesh_swept.n_cells} cells")
    
    print("\n2. Generating tube mesh...")
    mesh_tube = generator.generate_advanced_mesh(df, 'PathVel', method='tube')
    print(f"   Tube mesh: {mesh_tube.n_points} points, {mesh_tube.n_cells} cells")
    
    print("\n3. Generating ribbon mesh...")
    mesh_ribbon = generator.generate_advanced_mesh(df, 'FeedVel', method='ribbon')
    print(f"   Ribbon mesh: {mesh_ribbon.n_points} points, {mesh_ribbon.n_cells} cells")
    
    return mesh_swept, mesh_tube, mesh_ribbon


def demo_mesh_optimization():
    """Demonstrate mesh optimization techniques."""
    print("\n=== Mesh Optimization Demo ===")
    
    # Generate high-resolution data
    df = generate_sample_toolpath_data(2000)
    
    generator = PyVistaMeshGenerator()
    optimizer = MeshOptimizer()
    
    # Generate initial high-res mesh
    print("\n1. Generating high-resolution mesh...")
    mesh_high = generator.generate_swept_mesh(df, 'Temperature', lod='high')
    print(f"   Original: {mesh_high.n_points} points, {mesh_high.actual_memory_size/1e6:.2f} MB")
    
    # Apply adaptive decimation
    print("\n2. Applying adaptive decimation...")
    mesh_decimated = optimizer.adaptive_decimation(mesh_high, target_points=10000)
    print(f"   Decimated: {mesh_decimated.n_points} points, {mesh_decimated.actual_memory_size/1e6:.2f} MB")
    
    # Create LOD chain
    print("\n3. Creating LOD chain...")
    lod_meshes = optimizer.create_lod_chain(mesh_high, levels=[1.0, 0.5, 0.25, 0.1])
    for i, (level, mesh) in enumerate(zip([1.0, 0.5, 0.25, 0.1], lod_meshes)):
        print(f"   LOD {level}: {mesh.n_points} points")
    
    # Optimize for web
    print("\n4. Optimizing for web transmission...")
    mesh_web = optimizer.optimize_for_web(mesh_high, max_size_mb=5.0)
    print(f"   Web-optimized: {mesh_web.n_points} points, {mesh_web.actual_memory_size/1e6:.2f} MB")
    
    return mesh_high, mesh_decimated, lod_meshes


def demo_interactive_visualization():
    """Demonstrate interactive visualization with Trame."""
    print("\n=== Interactive Visualization Demo ===")
    
    # Generate sample data
    df = generate_sample_toolpath_data(1000)
    
    # Configure Trame server
    trame_config = TrameConfig(
        port=8051,
        title="MELD PyVista Demo",
        theme="dark",
        enable_picking=True,
        enable_measurements=True,
        enable_clipping=True
    )
    
    # Create server and mesh generator
    server = TrameVisualizationServer(trame_config)
    generator = PyVistaMeshGenerator()
    
    # Generate mesh
    print("\nGenerating demonstration mesh...")
    mesh = generator.generate_swept_mesh(df, 'Temperature', lod='medium')
    
    # Add multiple scalar fields for switching
    mesh['Velocity'] = df['PathVel'].values[:mesh.n_points]
    mesh['FeedRate'] = df['FeedVel'].values[:mesh.n_points]
    
    # Update server with mesh
    server.create_plotter()
    server.update_mesh(mesh, scalar='Temperature', cmap='plasma')
    
    print(f"\nTrame server starting at http://localhost:{trame_config.port}")
    print("Features available:")
    print("  - Camera controls: Click and drag to rotate")
    print("  - Color mapping: Change colormap and scalar field")
    print("  - Picking: Click points to get coordinates")
    print("  - Measurements: Enable tool to measure distances")
    print("  - Clipping: Enable plane to slice through mesh")
    print("\nPress Ctrl+C to stop the server")
    
    # Start server (blocking)
    try:
        server.server.start(
            port=trame_config.port,
            open=True,
            debug=True
        )
    except KeyboardInterrupt:
        print("\nServer stopped")


def demo_export_capabilities():
    """Demonstrate mesh export capabilities."""
    print("\n=== Export Capabilities Demo ===")
    
    # Generate sample data
    df = generate_sample_toolpath_data(500)
    
    generator = PyVistaMeshGenerator()
    
    # Generate mesh
    mesh = generator.generate_swept_mesh(df, 'Temperature', lod='high')
    
    # Export to various formats
    export_dir = Path("exports")
    export_dir.mkdir(exist_ok=True)
    
    formats = [
        ('stl', True),   # STL binary
        ('obj', False),  # OBJ ASCII
        ('ply', True),   # PLY binary
        ('vtk', False),  # VTK ASCII
    ]
    
    for fmt, binary in formats:
        filename = export_dir / f"meld_mesh.{fmt}"
        success = generator.export_mesh(mesh, str(filename), binary=binary)
        status = "✓" if success else "✗"
        print(f"  {status} Exported to {filename}")
    
    # Compute and display mesh properties
    print("\nMesh Properties:")
    properties = generator.compute_mesh_properties(mesh)
    for key, value in properties.items():
        if value is not None:
            if isinstance(value, (list, tuple, np.ndarray)):
                print(f"  {key}: {value}")
            elif isinstance(value, (int, float)):
                if 'memory' in key:
                    print(f"  {key}: {value/1e6:.2f} MB")
                else:
                    print(f"  {key}: {value:.2f}")


def demo_plotly_conversion():
    """Demonstrate conversion from existing Plotly mesh data."""
    print("\n=== Plotly Data Conversion Demo ===")
    
    # Simulate existing Plotly mesh data structure
    n_vertices = 1000
    n_faces = 500
    
    # Random vertices
    vertices = np.random.randn(n_vertices, 3) * 10
    
    # Random triangular faces
    faces = np.random.randint(0, n_vertices, size=(n_faces, 3))
    
    # Random scalar values
    vertex_colors = np.random.rand(n_vertices) * 100
    
    plotly_data = {
        'vertices': vertices,
        'faces': faces,
        'vertex_colors': vertex_colors
    }
    
    print(f"Original Plotly data: {n_vertices} vertices, {n_faces} faces")
    
    # Convert to PyVista
    generator = PyVistaMeshGenerator()
    pv_mesh = generator.create_mesh_from_plotly_data(
        vertices=plotly_data['vertices'],
        faces=plotly_data['faces'],
        scalars=plotly_data['vertex_colors'],
        scalar_name='intensity'
    )
    
    print(f"Converted PyVista mesh: {pv_mesh.n_points} points, {pv_mesh.n_cells} cells")
    print(f"Scalar fields available: {pv_mesh.array_names}")
    
    # Apply filters
    print("\nApplying filters...")
    filters = {
        'smooth': True,
        'smooth_iterations': 50,
        'clean': True,
        'compute_normals': True
    }
    
    filtered_mesh = generator.apply_filters(pv_mesh, filters)
    print(f"Filtered mesh: {filtered_mesh.n_points} points, {filtered_mesh.n_cells} cells")
    
    return pv_mesh, filtered_mesh


def main():
    """Run all demonstrations."""
    print("=" * 60)
    print("MELD Visualizer - PyVista/Trame Demonstration")
    print("=" * 60)
    
    # Run demos
    demos = [
        ("Basic Mesh Generation", demo_basic_mesh_generation),
        ("Mesh Optimization", demo_mesh_optimization),
        ("Export Capabilities", demo_export_capabilities),
        ("Plotly Conversion", demo_plotly_conversion),
        ("Interactive Visualization", demo_interactive_visualization),  # Run last as it blocks
    ]
    
    for i, (name, demo_func) in enumerate(demos, 1):
        print(f"\n[{i}/{len(demos)}] Running: {name}")
        print("-" * 40)
        
        try:
            result = demo_func()
            print(f"✓ {name} completed successfully")
        except Exception as e:
            print(f"✗ {name} failed: {e}")
            import traceback
            traceback.print_exc()
        
        if i < len(demos):
            input("\nPress Enter to continue to next demo...")
    
    print("\n" + "=" * 60)
    print("All demonstrations completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()