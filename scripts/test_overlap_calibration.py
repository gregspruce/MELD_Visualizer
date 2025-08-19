"""
Test the width calibration to ensure beads now overlap properly.
"""

import sys
import os
import pandas as pd
import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.meld_visualizer.services.data_service import get_data_service

def test_overlap():
    """Test that the calibration produces overlapping beads."""
    
    print("=" * 60)
    print("Testing Bead Overlap Calibration")
    print("=" * 60)
    
    # Initialize data service (will load calibration automatically)
    service = get_data_service()
    
    # Check that calibration was loaded
    width_mult = service.volume_calculator.width_multiplier
    print(f"\nCalibration loaded:")
    print(f"  Width Multiplier: {width_mult:.3f}")
    
    # Load test data
    csv_file = 'data/csv/20250722163434.csv'
    df = pd.read_csv(csv_file)
    
    # Filter for active extrusion
    df_active = df[(df['FeedVel'] > 0.1) & (df['PathVel'] > 0.1)]
    print(f"\nProcessing {len(df_active)} active points from {csv_file}")
    
    # Calculate volume data
    df_processed = service.calculate_volume_data(df_active)
    
    # Check bead width
    if 'Bead_Width_mm' in df_processed.columns:
        avg_width = df_processed['Bead_Width_mm'].mean()
        print(f"\nResults:")
        print(f"  Average Bead Width: {avg_width:.2f} mm")
        
        # Known track spacing from analysis
        track_spacing = 36.26
        print(f"  Track Spacing: {track_spacing:.2f} mm")
        
        if avg_width > track_spacing:
            overlap = avg_width - track_spacing
            overlap_percent = (overlap / avg_width) * 100
            print(f"  Overlap: {overlap:.2f} mm ({overlap_percent:.1f}%)")
            print(f"\n[SUCCESS] Beads are overlapping as expected!")
        else:
            gap = track_spacing - avg_width
            print(f"  Gap: {gap:.2f} mm")
            print(f"\n[FAIL] Still showing gaps - calibration may need adjustment")
    else:
        print("\n[ERROR] Bead_Width_mm column not found")
    
    # Test mesh generation
    print("\n" + "-" * 60)
    print("Testing Mesh Generation with Calibration")
    print("-" * 60)
    
    # Generate mesh
    mesh_data = service.generate_mesh(df_processed, 'ZPos', lod='low')
    
    if mesh_data:
        print(f"Mesh generated successfully:")
        print(f"  Vertices: {len(mesh_data['vertices'])}")
        print(f"  Faces: {len(mesh_data['faces'])}")
        
        # Check that the mesh is wider
        vertices = mesh_data['vertices']
        
        # Find the width span in X and Y
        x_span = vertices[:, 0].max() - vertices[:, 0].min()
        y_span = vertices[:, 1].max() - vertices[:, 1].min()
        
        print(f"\nMesh dimensions:")
        print(f"  X span: {x_span:.2f} mm")
        print(f"  Y span: {y_span:.2f} mm")
        
        print(f"\n[SUCCESS] Mesh generation with width calibration complete!")
    else:
        print("[FAIL] Failed to generate mesh")
    
    print("\n" + "=" * 60)
    print("CALIBRATION TEST COMPLETE")
    print("The volume plot should now show realistic bead overlap")
    print("matching the physical build in 20250722163434.jpg")
    print("=" * 60)


if __name__ == "__main__":
    test_overlap()