"""
Analyze bead overlap issue from 20250722163434 build.
The physical print shows overlapping beads but the volume plot shows gaps.
"""

import sys
import os
import pandas as pd
import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.meld_visualizer.core.volume_calculations import VolumeCalculator
from src.meld_visualizer.core.volume_mesh import MeshGenerator

def analyze_track_spacing(csv_path):
    """Analyze the track-to-track spacing in the CSV data."""
    
    print(f"\n=== Analyzing Track Spacing for {os.path.basename(csv_path)} ===\n")
    
    # Load the CSV data
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} rows from CSV")
    
    # Filter for active extrusion
    df_active = df[(df['FeedVel'] > 0.1) & (df['PathVel'] > 0.1)].copy()
    print(f"Active extrusion points: {len(df_active)}")
    
    # Calculate volume data
    calc = VolumeCalculator()
    df_processed = calc.process_dataframe(df_active)
    
    # Get basic statistics
    stats = calc.get_statistics(df_processed)
    print(f"\n--- Current Volume Calculations ---")
    print(f"Bead Area: {stats['bead_area']['mean']:.2f} ± {stats['bead_area']['std']:.2f} mm²")
    print(f"Bead Thickness: {stats['thickness']['mean']:.2f} ± {stats['thickness']['std']:.2f} mm")
    
    # Analyze track-to-track transitions
    print(f"\n--- Track Spacing Analysis ---")
    
    # Detect layer changes (significant Z changes)
    z_diff = df_active['ZPos'].diff()
    layer_changes = df_active[z_diff.abs() > 0.5].index
    print(f"Found {len(layer_changes)} layer changes")
    
    # For each layer, analyze the parallel tracks
    layers = []
    for i in range(len(layer_changes) - 1):
        start_idx = layer_changes[i]
        end_idx = layer_changes[i + 1]
        layer_data = df_active.loc[start_idx:end_idx]
        
        # Find the dominant movement direction (X or Y)
        x_range = layer_data['XPos'].max() - layer_data['XPos'].min()
        y_range = layer_data['YPos'].max() - layer_data['YPos'].min()
        
        if x_range > y_range:
            # Tracks run mainly in X direction, spaced in Y
            track_coord = 'YPos'
            along_coord = 'XPos'
        else:
            # Tracks run mainly in Y direction, spaced in X
            track_coord = 'XPos'
            along_coord = 'YPos'
        
        # Detect track changes (reversals in the along direction)
        along_diff = layer_data[along_coord].diff()
        direction_changes = along_diff * along_diff.shift(1) < 0
        track_starts = layer_data[direction_changes].index
        
        if len(track_starts) > 1:
            # Calculate track-to-track spacing
            track_positions = []
            for idx in track_starts:
                track_positions.append(layer_data.loc[idx, track_coord])
            
            track_spacings = np.diff(sorted(track_positions))
            if len(track_spacings) > 0:
                avg_spacing = np.mean(np.abs(track_spacings))
                layers.append({
                    'layer': i,
                    'z_pos': layer_data['ZPos'].mean(),
                    'track_spacing': avg_spacing,
                    'num_tracks': len(track_starts)
                })
    
    if layers:
        avg_track_spacing = np.mean([l['track_spacing'] for l in layers])
        print(f"Average track-to-track spacing: {avg_track_spacing:.2f} mm")
        
        # Sample a few layers for detail
        print(f"\nSample layer details:")
        for layer in layers[:5]:
            print(f"  Layer {layer['layer']}: Z={layer['z_pos']:.2f}mm, "
                  f"Spacing={layer['track_spacing']:.2f}mm, "
                  f"Tracks={layer['num_tracks']}")
    
    # Calculate theoretical bead width based on volume
    print(f"\n--- Bead Width Analysis ---")
    
    # Current bead geometry (capsule shape)
    bead_length = calc.bead_geometry.length_mm  # 2.0 mm
    bead_radius = calc.bead_geometry.radius_mm  # 1.0 mm
    avg_thickness = stats['thickness']['mean']
    
    # Effective bead width (capsule width)
    # Width = thickness + 2 * radius
    current_bead_width = avg_thickness + 2 * bead_radius
    print(f"Current calculated bead width: {current_bead_width:.2f} mm")
    print(f"  (Thickness: {avg_thickness:.2f} + 2×Radius: {2*bead_radius:.2f})")
    
    if layers and avg_track_spacing > 0:
        print(f"Track spacing: {avg_track_spacing:.2f} mm")
        
        # Calculate overlap
        if current_bead_width > avg_track_spacing:
            overlap = current_bead_width - avg_track_spacing
            overlap_percent = (overlap / current_bead_width) * 100
            print(f"Theoretical overlap: {overlap:.2f} mm ({overlap_percent:.1f}%)")
        else:
            gap = avg_track_spacing - current_bead_width
            print(f"GAP between beads: {gap:.2f} mm")
            print("[WARNING] This explains why the volume plot shows gaps!")
            
            # Calculate required bead width for overlap
            desired_overlap_percent = 20  # Typical overlap for good fusion
            required_bead_width = avg_track_spacing / (1 - desired_overlap_percent/100)
            print(f"\nRequired bead width for {desired_overlap_percent}% overlap: {required_bead_width:.2f} mm")
            
            # Calculate new bead geometry parameters
            # For a capsule: width = T + 2*R
            # If we want width = required_bead_width
            # We need to adjust either T (through calibration) or R (bead shape)
            
            # Option 1: Increase effective thickness through calibration
            required_thickness = required_bead_width - 2 * bead_radius
            thickness_factor = required_thickness / avg_thickness
            print(f"\nOption 1: Increase thickness calibration")
            print(f"  Required thickness: {required_thickness:.2f} mm")
            print(f"  Calibration factor: {thickness_factor:.3f}")
            
            # Option 2: Increase bead radius (wider bead shape)
            # Assuming we keep the same cross-sectional area
            # Area = π*R² + L*T
            current_area = stats['bead_area']['mean']
            
            # Try different radius values
            print(f"\nOption 2: Adjust bead shape parameters")
            for test_radius in [1.5, 2.0, 2.5, 3.0]:
                test_length = test_radius * 2  # Keep proportional
                # Solve for T: T = (Area - π*R²) / L
                test_thickness = (current_area - np.pi * test_radius**2) / test_length
                test_width = test_thickness + 2 * test_radius
                print(f"  R={test_radius:.1f}mm, L={test_length:.1f}mm -> Width={test_width:.2f}mm")
                if test_width >= required_bead_width:
                    print(f"    [OK] This would provide sufficient overlap!")
                    return test_radius, test_length, avg_track_spacing
    
    return None, None, avg_track_spacing if layers else None


def create_tuned_volume_config(csv_path):
    """Create a tuned configuration based on the analysis."""
    
    result = analyze_track_spacing(csv_path)
    if result[0] is not None:
        new_radius, new_length, track_spacing = result
        
        print(f"\n=== Recommended Configuration ===")
        print(f"Bead Radius: {new_radius:.2f} mm (was 1.0 mm)")
        print(f"Bead Length: {new_length:.2f} mm (was 2.0 mm)")
        print(f"Track Spacing: {track_spacing:.2f} mm")
        
        # Create configuration
        config = {
            "feedstock": {
                "dimension_inches": 0.5,
                "shape": "square",
                "comments": "Standard 0.5 inch square rod"
            },
            "bead_geometry": {
                "length_mm": new_length,
                "radius_mm": new_radius,
                "max_thickness_mm": 25.4,
                "comments": f"Tuned for {track_spacing:.2f}mm track spacing with overlap"
            },
            "calibration": {
                "correction_factor": 1.0,
                "area_offset": 0.0,
                "comments": f"Tuned from {os.path.basename(csv_path)}"
            }
        }
        
        # Save to a new config file
        import json
        config_path = 'config/volume_calibration_tuned.json'
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"\nSaved tuned configuration to {config_path}")
        
        return config
    
    return None


if __name__ == "__main__":
    csv_file = "data/csv/20250722163434.csv"
    
    # Analyze the track spacing
    analyze_track_spacing(csv_file)
    
    # Create tuned configuration
    config = create_tuned_volume_config(csv_file)
    
    if config:
        print("\n=== Testing New Configuration ===")
        
        # Test with new parameters
        from src.meld_visualizer.core.volume_calculations import BeadGeometry
        
        calc = VolumeCalculator()
        calc.bead_geometry = BeadGeometry(
            length_mm=config['bead_geometry']['length_mm'],
            radius_mm=config['bead_geometry']['radius_mm']
        )
        
        # Reprocess data
        df = pd.read_csv(csv_file)
        df_active = df[(df['FeedVel'] > 0.1) & (df['PathVel'] > 0.1)]
        df_processed = calc.process_dataframe(df_active)
        
        stats = calc.get_statistics(df_processed)
        avg_thickness = stats['thickness']['mean']
        
        # Calculate new bead width
        new_width = avg_thickness + 2 * config['bead_geometry']['radius_mm']
        print(f"New bead width: {new_width:.2f} mm")
        print(f"This should now show overlapping beads in the volume plot!")