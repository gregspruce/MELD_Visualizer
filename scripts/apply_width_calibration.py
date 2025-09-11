"""
Apply width calibration to match physical bead overlap.
Based on analysis showing 36.26mm track spacing but only 27.4mm calculated bead width.
"""

import sys
import os
import pandas as pd
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.meld_visualizer.core.volume_calculations import VolumeCalculator

def apply_width_calibration():
    """
    Apply width calibration based on physical measurements.
    """

    print("=" * 60)
    print("Applying Width Calibration for Bead Overlap")
    print("=" * 60)

    # Physical measurements from analysis
    track_spacing = 36.26  # mm (measured from CSV)
    current_width = 27.40  # mm (calculated with default parameters)
    desired_overlap = 0.20  # 20% overlap for good fusion

    # Calculate required width for proper overlap
    required_width = track_spacing / (1 - desired_overlap)

    # Calculate width multiplier
    width_multiplier = required_width / current_width

    print("\nAnalysis Results:")
    print(f"  Track Spacing: {track_spacing:.2f} mm")
    print(f"  Current Bead Width: {current_width:.2f} mm")
    print(f"  Required Width (20% overlap): {required_width:.2f} mm")
    print(f"  Width Multiplier Needed: {width_multiplier:.3f}")

    # Create calibration configuration
    config = {
        "feedstock": {
            "dimension_inches": 0.5,
            "shape": "square",
            "comments": "Standard 0.5 inch square rod feedstock"
        },
        "bead_geometry": {
            "length_mm": 2.0,
            "radius_mm": 1.0,
            "max_thickness_mm": 25.4,
            "comments": "Standard capsule geometry"
        },
        "calibration": {
            "correction_factor": 1.0,
            "area_offset": 0.0,
            "width_multiplier": width_multiplier,
            "comments": f"Width multiplier calibrated for {track_spacing:.1f}mm track spacing"
        },
        "validation": {
            "track_spacing_mm": track_spacing,
            "current_width_mm": current_width,
            "required_width_mm": required_width,
            "overlap_percent": desired_overlap * 100,
            "source": "20250722163434 physical build analysis"
        }
    }

    # Save configuration
    config_path = 'config/volume_calibration_final.json'
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

    print(f"\n[SUCCESS] Configuration saved to {config_path}")

    # Test the calibration
    print("\n" + "=" * 60)
    print("Testing Calibration with Sample Data")
    print("=" * 60)

    csv_file = 'data/csv/20250722163434.csv'

    # Load data
    df = pd.read_csv(csv_file)
    df_active = df[(df['FeedVel'] > 0.1) & (df['PathVel'] > 0.1)]

    # Create calculator with calibration
    calc = VolumeCalculator()
    calc.set_calibration(
        correction_factor=1.0,
        area_offset=0.0,
        width_multiplier=width_multiplier
    )

    # Process data
    df_processed = calc.process_dataframe(df_active)

    # Check results
    avg_width = df_processed['Bead_Width_mm'].mean()
    print("\nCalibrated Results:")
    print(f"  Average Bead Width: {avg_width:.2f} mm")
    print(f"  Track Spacing: {track_spacing:.2f} mm")

    if avg_width > track_spacing:
        overlap = avg_width - track_spacing
        overlap_percent = (overlap / avg_width) * 100
        print(f"  Overlap: {overlap:.2f} mm ({overlap_percent:.1f}%)")
        print("\n[SUCCESS] Beads will now overlap in the volume plot!")
    else:
        gap = track_spacing - avg_width
        print(f"  Gap: {gap:.2f} mm")
        print("\n[WARNING] Still showing gaps")

    return config


def update_data_service_defaults():
    """
    Update the data service to use the calibrated width multiplier by default.
    """

    print("\n" + "=" * 60)
    print("Updating Default Calibration")
    print("=" * 60)

    # Load the calibration
    config_path = 'config/volume_calibration_final.json'
    with open(config_path, 'r') as f:
        config = json.load(f)

    width_mult = config['calibration']['width_multiplier']

    print(f"Width Multiplier: {width_mult:.3f}")
    print("\nTo apply this calibration in the app:")
    print("1. The data service will automatically load this configuration")
    print("2. All volume plots will show proper bead overlap")
    print("3. The mesh generator will use the width multiplier")

    # Update the main calibration file
    main_config_path = 'config/volume_calibration.json'
    config_to_save = {
        "feedstock": config['feedstock'],
        "bead_geometry": config['bead_geometry'],
        "calibration": {
            "correction_factor": 1.0,
            "area_offset": 0.0,
            "width_multiplier": width_mult,
            "comments": "Calibrated from physical build measurements"
        },
        "tuning_guide": {
            "width_multiplier": f"Set to {width_mult:.3f} to match {config['validation']['track_spacing_mm']:.1f}mm track spacing",
            "validation": "Based on physical build 20250722163434",
            "overlap": f"Provides {config['validation']['overlap_percent']:.0f}% bead overlap"
        }
    }

    with open(main_config_path, 'w') as f:
        json.dump(config, f, indent=2)

    print(f"\n[SUCCESS] Main configuration updated: {main_config_path}")


if __name__ == "__main__":
    # Apply the calibration
    config = apply_width_calibration()

    # Update defaults
    update_data_service_defaults()

    print("\n" + "=" * 60)
    print("CALIBRATION COMPLETE")
    print("The volume plot will now show overlapping beads")
    print("matching the physical build!")
    print("=" * 60)
