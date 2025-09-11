"""
Tune the bead width to match physical overlap observed in prints.
Based on analysis of 20250722163434 build.
"""

import sys
import os
import pandas as pd
import numpy as np
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.meld_visualizer.core.volume_calculations import (
    VolumeCalculator, FeedstockParameters, BeadGeometry
)

def calculate_optimal_parameters(track_spacing_mm, desired_overlap_percent=20):
    """
    Calculate optimal bead geometry parameters for proper overlap.

    The issue: Current model creates beads that are too narrow.
    Solution: Adjust the bead geometry to be wider while maintaining volume.
    """

    print("\n=== Calculating Optimal Bead Parameters ===")
    print(f"Track Spacing: {track_spacing_mm:.2f} mm")
    print(f"Desired Overlap: {desired_overlap_percent}%")

    # Calculate required bead width for desired overlap
    # If tracks are spaced S mm apart and we want O% overlap:
    # Bead width W = S / (1 - O/100)
    required_width = track_spacing_mm / (1 - desired_overlap_percent/100)
    print(f"Required Bead Width: {required_width:.2f} mm")

    # Current default parameters
    default_radius = 1.0  # mm
    default_length = 2.0  # mm

    # The actual bead is wider than our capsule model suggests
    # This is because the material spreads more during deposition
    # We need to adjust our model to account for this spreading

    # Strategy: Increase the bead radius to make it wider
    # The capsule width = thickness + 2*radius
    # We need to find radius that gives us the required width

    # From the CSV analysis, average bead area is ~70.8 mm²
    # This is the cross-sectional area we need to maintain
    target_area = 70.8  # mm²

    print("\n--- Solving for Optimal Geometry ---")
    print(f"Target Cross-sectional Area: {target_area:.2f} mm²")

    # For a capsule shape: Area = π*R² + L*T
    # And Width = T + 2*R
    # We need Width = required_width

    # Let's try different radius values and solve for the rest
    best_config = None
    best_error = float('inf')

    for radius_factor in np.linspace(3.0, 10.0, 50):
        new_radius = radius_factor
        new_length = radius_factor * 1.5  # Keep aspect ratio reasonable

        # From Width = T + 2*R, we get T = Width - 2*R
        thickness_for_width = required_width - 2 * new_radius

        if thickness_for_width <= 0:
            continue

        # Check if this gives us the right area
        # Area = π*R² + L*T
        calculated_area = np.pi * new_radius**2 + new_length * thickness_for_width

        area_error = abs(calculated_area - target_area)

        if area_error < best_error:
            best_error = area_error
            best_config = {
                'radius': new_radius,
                'length': new_length,
                'thickness': thickness_for_width,
                'width': required_width,
                'area': calculated_area
            }

    if best_config:
        print("\nOptimal Configuration Found:")
        print(f"  Bead Radius: {best_config['radius']:.2f} mm (was {default_radius:.2f} mm)")
        print(f"  Bead Length: {best_config['length']:.2f} mm (was {default_length:.2f} mm)")
        print(f"  Resulting Thickness: {best_config['thickness']:.2f} mm")
        print(f"  Resulting Width: {best_config['width']:.2f} mm")
        print(f"  Cross-sectional Area: {best_config['area']:.2f} mm² (target: {target_area:.2f} mm²)")
        print(f"  Area Error: {best_error:.2f} mm² ({(best_error/target_area)*100:.1f}%)")

        return best_config

    return None


def create_calibrated_config(track_spacing_mm=36.26):
    """
    Create a calibrated configuration file based on the physical measurements.
    """

    # Calculate optimal parameters
    optimal = calculate_optimal_parameters(track_spacing_mm, desired_overlap_percent=20)

    if not optimal:
        print("Failed to find optimal configuration")
        return None

    # Create configuration
    config = {
        "feedstock": {
            "dimension_inches": 0.5,
            "shape": "square",
            "comments": "Standard 0.5 inch square rod feedstock"
        },
        "bead_geometry": {
            "length_mm": optimal['length'],
            "radius_mm": optimal['radius'],
            "max_thickness_mm": 50.0,  # Increased to accommodate wider beads
            "comments": f"Calibrated for {track_spacing_mm:.1f}mm track spacing with 20% overlap"
        },
        "calibration": {
            "correction_factor": 1.0,
            "area_offset": 0.0,
            "comments": "Geometry adjusted to match physical bead spreading"
        },
        "validation": {
            "track_spacing_mm": track_spacing_mm,
            "calculated_width_mm": optimal['width'],
            "overlap_percent": 20,
            "source_file": "20250722163434.csv"
        }
    }

    # Save configuration
    config_path = 'config/volume_calibration_corrected.json'
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

    print("\n=== Configuration Saved ===")
    print(f"File: {config_path}")

    return config


def test_calibration(csv_file='data/csv/20250722163434.csv'):
    """
    Test the calibrated configuration with actual data.
    """

    print("\n=== Testing Calibrated Configuration ===")

    # Load the calibrated configuration
    config_path = 'config/volume_calibration_corrected.json'
    if not os.path.exists(config_path):
        print(f"Configuration file not found: {config_path}")
        return

    with open(config_path, 'r') as f:
        config = json.load(f)

    # Create calculator with calibrated parameters
    calc = VolumeCalculator()
    calc.bead_geometry = BeadGeometry(
        length_mm=config['bead_geometry']['length_mm'],
        radius_mm=config['bead_geometry']['radius_mm'],
        max_thickness_mm=config['bead_geometry']['max_thickness_mm']
    )

    # Load and process CSV data
    df = pd.read_csv(csv_file)
    df_active = df[(df['FeedVel'] > 0.1) & (df['PathVel'] > 0.1)]

    print(f"Processing {len(df_active)} active extrusion points...")
    df_processed = calc.process_dataframe(df_active)

    # Calculate statistics
    stats = calc.get_statistics(df_processed)

    print("\n--- Results with Calibrated Parameters ---")
    print(f"Bead Geometry:")
    print(f"  Radius: {calc.bead_geometry.radius_mm:.2f} mm")
    print(f"  Length: {calc.bead_geometry.length_mm:.2f} mm")

    print("\nCalculated Values:")
    print(f"  Bead Area: {stats['bead_area']['mean']:.2f} mm²")
    print(f"  Bead Thickness: {stats['thickness']['mean']:.2f} mm")

    # Calculate effective bead width
    avg_thickness = stats['thickness']['mean']
    bead_width = avg_thickness + 2 * calc.bead_geometry.radius_mm

    print(f"  Effective Bead Width: {bead_width:.2f} mm")

    # Compare with track spacing
    track_spacing = config['validation']['track_spacing_mm']
    print("\nValidation:")
    print(f"  Track Spacing: {track_spacing:.2f} mm")

    if bead_width > track_spacing:
        overlap = bead_width - track_spacing
        overlap_percent = (overlap / bead_width) * 100
        print(f"  Overlap: {overlap:.2f} mm ({overlap_percent:.1f}%)")
        print("  [SUCCESS] Beads will now overlap in volume plot!")
    else:
        gap = track_spacing - bead_width
        print(f"  Gap: {gap:.2f} mm")
        print("  [NEEDS ADJUSTMENT] Still showing gaps")

    return df_processed


def main():
    """
    Main calibration workflow.
    """

    print("=" * 60)
    print("MELD Bead Width Calibration")
    print("Based on physical build 20250722163434")
    print("=" * 60)

    # Track spacing from the analysis
    track_spacing = 36.26  # mm

    # Create calibrated configuration
    config = create_calibrated_config(track_spacing)

    if config:
        # Test the calibration
        test_calibration()

        print("\n" + "=" * 60)
        print("CALIBRATION COMPLETE")
        print("The volume plot should now show overlapping beads")
        print("matching the physical build.")
        print("=" * 60)


if __name__ == "__main__":
    main()
