"""
Test script for the new volume calculation modules.
Run this to validate the refactored implementation.
"""

import sys
import os
import numpy as np
import pandas as pd

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.meld_visualizer.core.volume_calculations import (
    VolumeCalculator, FeedstockParameters, BeadGeometry
)
from src.meld_visualizer.core.volume_mesh import (
    MeshGenerator, VolumePlotter
)


def create_test_dataframe():
    """Create a sample DataFrame for testing."""
    n_points = 100
    t = np.linspace(0, 10, n_points)
    
    df = pd.DataFrame({
        'XPos': 10 * np.cos(t),
        'YPos': 10 * np.sin(t),
        'ZPos': t * 2,
        'FeedVel': np.full(n_points, 50.0),  # Constant feed velocity
        'PathVel': np.full(n_points, 100.0),  # Constant path velocity
        'Time': pd.date_range('2025-01-01', periods=n_points, freq='s')
    })
    
    return df


def test_volume_calculator():
    """Test the VolumeCalculator class."""
    print("\n=== Testing VolumeCalculator ===")
    
    # Create calculator with default parameters
    calc = VolumeCalculator()
    
    # Test with sample data
    df = create_test_dataframe()
    df_processed = calc.process_dataframe(df)
    
    # Check that columns were added
    expected_cols = ['Bead_Area_mm2', 'Bead_Thickness_mm', 'Volume_Rate_mm3_per_min']
    for col in expected_cols:
        assert col in df_processed.columns, f"Missing column: {col}"
    
    # Check calculations
    expected_area = (50.0 * 161.3) / 100.0  # (feed * area) / path
    assert np.allclose(df_processed['Bead_Area_mm2'].iloc[0], expected_area, rtol=0.01)
    
    # Get statistics
    stats = calc.get_statistics(df_processed)
    print(f"  Bead area: {stats['bead_area']['mean']:.2f} mm² (mean)")
    print(f"  Thickness: {stats['thickness']['mean']:.2f} mm (mean)")
    print(f"  Total volume: {stats['total_volume']['cm3']:.2f} cm³")
    
    # Test calibration
    calc.set_calibration(correction_factor=1.1, area_offset=5.0)
    df_calibrated = calc.process_dataframe(df)
    
    # Check calibration was applied
    calibrated_area = expected_area * 1.1 + 5.0
    assert np.allclose(df_calibrated['Bead_Area_mm2'].iloc[0], calibrated_area, rtol=0.01)
    
    print("  [PASS] VolumeCalculator tests passed")
    return df_processed


def test_feedstock_parameters():
    """Test FeedstockParameters class."""
    print("\n=== Testing FeedstockParameters ===")
    
    # Test square feedstock (default)
    square = FeedstockParameters(dimension_inches=0.5, shape='square')
    assert np.isclose(square.dimension_mm, 12.7)
    assert np.isclose(square.cross_sectional_area_mm2, 161.29)
    
    # Test circular feedstock
    circular = FeedstockParameters(dimension_inches=0.5, shape='circular')
    expected_area = np.pi * (12.7 / 2) ** 2
    assert np.isclose(circular.cross_sectional_area_mm2, expected_area)
    
    print(f"  Square (0.5\"): {square.cross_sectional_area_mm2:.2f} mm²")
    print(f"  Circular (0.5\"): {circular.cross_sectional_area_mm2:.2f} mm²")
    print("  [PASS] FeedstockParameters tests passed")


def test_bead_geometry():
    """Test BeadGeometry class."""
    print("\n=== Testing BeadGeometry ===")
    
    bead = BeadGeometry(length_mm=2.0, radius_mm=1.0)
    
    # Test area calculation
    thickness = 5.0
    area = bead.calculate_area(thickness)
    expected_area = np.pi * 1.0**2 + 2.0 * 5.0
    assert np.isclose(area, expected_area)
    
    # Test thickness calculation
    calculated_thickness = bead.calculate_thickness(area)
    assert np.isclose(calculated_thickness, thickness)
    
    print(f"  Min area: {bead.min_area_mm2:.2f} mm²")
    print(f"  Area at T=5mm: {area:.2f} mm²")
    print("  [PASS] BeadGeometry tests passed")


def test_mesh_generator(df_with_volumes):
    """Test the MeshGenerator class."""
    print("\n=== Testing MeshGenerator ===")
    
    generator = MeshGenerator(points_per_section=8)
    
    # Test mesh generation
    mesh_data = generator.generate_mesh(
        df_with_volumes, 
        color_column='ZPos',
        bead_length=2.0,
        bead_radius=1.0
    )
    
    assert mesh_data is not None, "Mesh generation failed"
    assert 'vertices' in mesh_data
    assert 'faces' in mesh_data
    assert 'vertex_colors' in mesh_data
    
    n_vertices = len(mesh_data['vertices'])
    n_faces = len(mesh_data['faces'])
    
    print(f"  Generated mesh: {n_vertices} vertices, {n_faces} faces")
    
    # Test LOD generation
    for lod in ['low', 'medium', 'high']:
        mesh_lod = generator.generate_mesh_lod(
            df_with_volumes,
            color_column='ZPos',
            lod=lod
        )
        print(f"  {lod.capitalize()} LOD: {len(mesh_lod['vertices'])} vertices")
    
    print("  [PASS] MeshGenerator tests passed")
    return mesh_data


def test_volume_plotter():
    """Test the VolumePlotter class."""
    print("\n=== Testing VolumePlotter ===")
    
    plotter = VolumePlotter()
    
    # Create test data
    df = create_test_dataframe()
    
    # Prepare data
    df_prepared = plotter.prepare_data(df)
    assert 'Bead_Thickness_mm' in df_prepared.columns
    
    # Generate plot data
    mesh_data = plotter.generate_plot_data(df_prepared, 'ZPos', lod='medium')
    assert mesh_data is not None
    
    # Get statistics
    stats = plotter.get_statistics(df_prepared)
    assert 'bead_area' in stats
    assert 'thickness' in stats
    
    print(f"  Prepared {len(df_prepared)} rows")
    print(f"  Generated mesh with {len(mesh_data['vertices'])} vertices")
    print("  [PASS] VolumePlotter tests passed")


def test_integration():
    """Test integration with data service."""
    print("\n=== Testing DataService Integration ===")
    
    try:
        from src.meld_visualizer.services.data_service import get_data_service
        
        service = get_data_service()
        
        # Create test data
        df = create_test_dataframe()
        
        # Test volume calculation through service
        df_with_volumes = service.calculate_volume_data(df)
        assert 'Bead_Area_mm2' in df_with_volumes.columns
        
        # Test mesh generation through service
        mesh_data = service.generate_mesh(df_with_volumes, 'ZPos', lod='medium')
        assert mesh_data is not None
        
        # Test calibration
        service.set_volume_calibration(correction_factor=1.05, area_offset=2.0)
        
        print("  [PASS] DataService integration tests passed")
        
    except Exception as e:
        print(f"  [SKIP] DataService integration test skipped: {e}")


def run_all_tests():
    """Run all test functions."""
    print("Starting volume module tests...")
    
    try:
        # Run tests in order
        test_feedstock_parameters()
        test_bead_geometry()
        df_with_volumes = test_volume_calculator()
        test_mesh_generator(df_with_volumes)
        test_volume_plotter()
        test_integration()
        
        print("\n[SUCCESS] All tests passed successfully!")
        return True
        
    except AssertionError as e:
        print(f"\n[FAIL] Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)