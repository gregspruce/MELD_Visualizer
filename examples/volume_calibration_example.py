"""
Example script for volume calibration workflow.

This script demonstrates how to:
1. Load CSV data from a MELD print
2. Calculate theoretical volume
3. Compare with physical measurements
4. Apply calibration factors
5. Validate the calibration
"""

import sys
import os
import pandas as pd
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.meld_visualizer.core.volume_calculations import (
    VolumeCalculator, FeedstockParameters, BeadGeometry
)
from src.meld_visualizer.core.volume_mesh import VolumePlotter


def load_calibration_config(config_path='config/volume_calibration.json'):
    """Load calibration configuration from JSON file."""
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
        print(f"Loaded configuration from {config_path}")
        return config
    else:
        print(f"No configuration file found at {config_path}, using defaults")
        return None


def save_calibration_config(config, config_path='config/volume_calibration.json'):
    """Save calibration configuration to JSON file."""
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    print(f"Saved configuration to {config_path}")


def calibrate_from_physical_measurement(csv_file_path, actual_volume_cm3):
    """
    Calibrate volume calculations based on physical measurement.
    
    Args:
        csv_file_path: Path to CSV file from MELD print
        actual_volume_cm3: Measured volume of physical print in cm³
    
    Returns:
        Calibrated VolumeCalculator instance
    """
    print(f"\n=== Volume Calibration Workflow ===")
    print(f"CSV File: {csv_file_path}")
    print(f"Measured Volume: {actual_volume_cm3} cm³")
    
    # Load CSV data
    try:
        df = pd.read_csv(csv_file_path)
        print(f"Loaded {len(df)} rows from CSV")
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return None
    
    # Load existing configuration
    config = load_calibration_config()
    
    # Initialize calculator with configuration
    calc = VolumeCalculator()
    if config:
        calc.feedstock = FeedstockParameters(
            dimension_inches=config['feedstock']['dimension_inches'],
            shape=config['feedstock']['shape']
        )
        calc.bead_geometry = BeadGeometry(
            length_mm=config['bead_geometry']['length_mm'],
            radius_mm=config['bead_geometry']['radius_mm'],
            max_thickness_mm=config['bead_geometry']['max_thickness_mm']
        )
    
    print(f"\nFeedstock: {calc.feedstock.dimension_inches}\" {calc.feedstock.shape}")
    print(f"Feedstock Area: {calc.feedstock.cross_sectional_area_mm2:.2f} mm²")
    
    # Calculate theoretical volume (uncalibrated)
    print("\n--- Step 1: Calculate Theoretical Volume ---")
    df_processed = calc.process_dataframe(df)
    stats = calc.get_statistics(df_processed)
    
    if 'total_volume' not in stats:
        print("Warning: Could not calculate total volume (missing position data?)")
        # Calculate approximate volume from feed rate
        total_time_min = df_processed['TimeInSeconds'].max() / 60.0
        avg_volume_rate = stats['process']['feed_vel_mean'] * calc.feedstock.cross_sectional_area_mm2
        theoretical_volume_cm3 = (avg_volume_rate * total_time_min) / 1000.0
        print(f"Estimated from feed rate: {theoretical_volume_cm3:.2f} cm³")
    else:
        theoretical_volume_cm3 = stats['total_volume']['cm3']
        print(f"Theoretical Volume: {theoretical_volume_cm3:.2f} cm³")
    
    print(f"Bead Area: {stats['bead_area']['mean']:.2f} ± {stats['bead_area']['std']:.2f} mm²")
    print(f"Thickness: {stats['thickness']['mean']:.2f} ± {stats['thickness']['std']:.2f} mm")
    
    # Calculate correction factor
    print("\n--- Step 2: Calculate Correction Factor ---")
    correction_factor = actual_volume_cm3 / theoretical_volume_cm3
    print(f"Correction Factor = {actual_volume_cm3:.2f} / {theoretical_volume_cm3:.2f} = {correction_factor:.4f}")
    
    percentage_error = (correction_factor - 1.0) * 100
    if percentage_error > 0:
        print(f"Theoretical volume was {abs(percentage_error):.1f}% too LOW")
    else:
        print(f"Theoretical volume was {abs(percentage_error):.1f}% too HIGH")
    
    # Apply calibration
    print("\n--- Step 3: Apply Calibration ---")
    calc.set_calibration(correction_factor=correction_factor, area_offset=0.0)
    
    # Validate calibration
    print("\n--- Step 4: Validate Calibration ---")
    df_calibrated = calc.process_dataframe(df)
    stats_calibrated = calc.get_statistics(df_calibrated)
    
    if 'total_volume' in stats_calibrated:
        calibrated_volume_cm3 = stats_calibrated['total_volume']['cm3']
    else:
        total_time_min = df_calibrated['TimeInSeconds'].max() / 60.0
        avg_volume_rate = stats_calibrated['process']['feed_vel_mean'] * calc.feedstock.cross_sectional_area_mm2
        calibrated_volume_cm3 = (avg_volume_rate * total_time_min * correction_factor) / 1000.0
    
    print(f"Calibrated Volume: {calibrated_volume_cm3:.2f} cm³")
    print(f"Target Volume: {actual_volume_cm3:.2f} cm³")
    
    error = abs(calibrated_volume_cm3 - actual_volume_cm3)
    error_percent = (error / actual_volume_cm3) * 100
    print(f"Remaining Error: {error:.3f} cm³ ({error_percent:.2f}%)")
    
    if error_percent < 5.0:
        print("✓ Calibration successful! (< 5% error)")
    else:
        print("⚠ Consider fine-tuning with area_offset parameter")
    
    # Save calibration
    print("\n--- Step 5: Save Calibration ---")
    new_config = {
        'feedstock': {
            'dimension_inches': calc.feedstock.dimension_inches,
            'shape': calc.feedstock.shape,
            'comments': f"Calibrated from {os.path.basename(csv_file_path)}"
        },
        'bead_geometry': {
            'length_mm': calc.bead_geometry.length_mm,
            'radius_mm': calc.bead_geometry.radius_mm,
            'max_thickness_mm': calc.bead_geometry.max_thickness_mm,
            'comments': "Default capsule geometry"
        },
        'calibration': {
            'correction_factor': correction_factor,
            'area_offset': 0.0,
            'comments': f"Calibrated to match {actual_volume_cm3} cm³ physical measurement"
        }
    }
    
    save_calibration_config(new_config)
    
    return calc


def analyze_volume_distribution(csv_file_path):
    """
    Analyze volume distribution throughout the print.
    
    This helps identify if calibration needs to be non-uniform.
    """
    print(f"\n=== Volume Distribution Analysis ===")
    
    # Load data
    df = pd.read_csv(csv_file_path)
    
    # Load calibrated calculator
    config = load_calibration_config()
    calc = VolumeCalculator()
    
    if config:
        calc.set_calibration(
            correction_factor=config['calibration']['correction_factor'],
            area_offset=config['calibration']['area_offset']
        )
    
    # Process data
    df_processed = calc.process_dataframe(df)
    
    # Analyze by layer (Z position)
    if 'ZPos' in df_processed.columns:
        # Group by Z layer (round to nearest 0.5mm)
        df_processed['Layer'] = (df_processed['ZPos'] / 0.5).round() * 0.5
        
        layer_stats = df_processed.groupby('Layer').agg({
            'Bead_Area_mm2': ['mean', 'std'],
            'Bead_Thickness_mm': ['mean', 'std'],
            'FeedVel': 'mean',
            'PathVel': 'mean'
        })
        
        print("\nLayer-by-layer analysis:")
        print(layer_stats.head(10))
        
        # Check for variations
        area_variation = df_processed['Bead_Area_mm2'].std() / df_processed['Bead_Area_mm2'].mean()
        thickness_variation = df_processed['Bead_Thickness_mm'].std() / df_processed['Bead_Thickness_mm'].mean()
        
        print(f"\nOverall Variations:")
        print(f"  Bead Area CV: {area_variation*100:.1f}%")
        print(f"  Thickness CV: {thickness_variation*100:.1f}%")
        
        if area_variation > 0.2:
            print("⚠ High variation in bead area - consider segment-specific calibration")
        else:
            print("✓ Bead area is relatively consistent")


def example_usage():
    """Example usage of the calibration workflow."""
    print("=" * 60)
    print("MELD Volume Calibration Example")
    print("=" * 60)
    
    # Example 1: Basic calibration
    print("\nExample 1: Basic Calibration")
    print("-" * 30)
    
    # Simulate having a CSV file and physical measurement
    # In real use, replace with actual file path and measurement
    csv_file = "data/test_print_001.csv"
    measured_volume = 125.5  # cm³
    
    print(f"CSV File: {csv_file}")
    print(f"Measured Volume: {measured_volume} cm³")
    print("\nTo calibrate, run:")
    print(f"  calc = calibrate_from_physical_measurement('{csv_file}', {measured_volume})")
    
    # Example 2: Using calibrated calculator
    print("\n\nExample 2: Using Calibrated Calculator")
    print("-" * 30)
    
    print("Load calibration and process new data:")
    print("""
    # Load configuration
    config = load_calibration_config()
    
    # Create calculator with calibration
    calc = VolumeCalculator()
    calc.set_calibration(
        correction_factor=config['calibration']['correction_factor'],
        area_offset=config['calibration']['area_offset']
    )
    
    # Process new data
    df = pd.read_csv('new_print.csv')
    df_processed = calc.process_dataframe(df)
    stats = calc.get_statistics(df_processed)
    print(f"Predicted volume: {stats['total_volume']['cm3']:.2f} cm³")
    """)
    
    # Example 3: Volume distribution analysis
    print("\n\nExample 3: Volume Distribution Analysis")
    print("-" * 30)
    
    print("Analyze volume distribution by layer:")
    print(f"  analyze_volume_distribution('{csv_file}')")
    
    print("\n" + "=" * 60)
    print("For actual calibration, provide:")
    print("1. Path to CSV file from MELD print")
    print("2. Measured volume of physical print (cm³)")
    print("3. Run: calibrate_from_physical_measurement(csv_path, volume)")
    print("=" * 60)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='MELD Volume Calibration Tool')
    parser.add_argument('--csv', type=str, help='Path to CSV file from MELD print')
    parser.add_argument('--volume', type=float, help='Measured volume in cm³')
    parser.add_argument('--analyze', action='store_true', help='Analyze volume distribution')
    
    args = parser.parse_args()
    
    if args.csv and args.volume:
        # Perform calibration
        calc = calibrate_from_physical_measurement(args.csv, args.volume)
        
        if args.analyze and calc:
            analyze_volume_distribution(args.csv)
    
    elif args.csv and args.analyze:
        # Just analyze distribution
        analyze_volume_distribution(args.csv)
    
    else:
        # Show example usage
        example_usage()