import json
import logging
import os
import sys

import pandas as pd

# Add parent directory to path to allow importing from src.meld_visualizer
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.meld_visualizer.core.volume_calculations import (  # noqa: E402
    BeadGeometry,
    FeedstockParameters,
    VolumeCalculator,
)

# Set the logging level for the root logger to WARNING
logging.basicConfig(level=logging.WARNING)

# Also set the logging level for the "src.meld_visualizer" logger and its children
# This ensures that messages from within the meld_visualizer package are suppressed
logging.getLogger("src.meld_visualizer").setLevel(logging.WARNING)

# VolumePlotter is not used in the calibration logic, so it's not strictly needed for this interactive script
# from src.meld_visualizer.core.volume_mesh import VolumePlotter


def load_calibration_config(config_path="config/volume_calibration.json"):
    """Load calibration configuration from JSON file."""
    # Adjust path for interactive script if necessary, assuming config is relative to project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    full_config_path = os.path.join(project_root, config_path)

    if os.path.exists(full_config_path):
        with open(full_config_path, "r") as f:
            config = json.load(f)
        print(f"Loaded configuration from {full_config_path}")
        return config
    else:
        print(f"No configuration file found at {full_config_path}, using defaults")
        return None


def save_calibration_config(config, config_path="config/volume_calibration.json"):
    """Save calibration configuration to JSON file."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    full_config_path = os.path.join(project_root, config_path)
    os.makedirs(os.path.dirname(full_config_path), exist_ok=True)  # Ensure config directory exists

    with open(full_config_path, "w") as f:
        json.dump(config, f, indent=2)
    print(f"Saved configuration to {full_config_path}")


def calibrate_from_physical_measurement(csv_file_path, actual_volume_cm3):
    """
    Calibrate volume calculations based on physical measurement.

    Args:
        csv_file_path: Path to CSV file from MELD print
        actual_volume_cm3: Measured volume of physical print in cm³

    Returns:
        Calibrated VolumeCalculator instance
    """
    print("\n=== Volume Calibration Workflow ===")
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
    if config and "feedstock" in config and "bead_geometry" in config:
        calc.feedstock = FeedstockParameters(
            dimension_inches=config["feedstock"]["dimension_inches"],
            shape=config["feedstock"]["shape"],
        )
        calc.bead_geometry = BeadGeometry(
            length_mm=config["bead_geometry"]["length_mm"],
            radius_mm=config["bead_geometry"]["radius_mm"],
            max_thickness_mm=config["bead_geometry"]["max_thickness_mm"],
        )
        print("Using feedstock and bead geometry from config.")
    else:
        print("Using default feedstock and bead geometry.")

    print(f'\nFeedstock: {calc.feedstock.dimension_inches}" {calc.feedstock.shape}')
    print(f"Feedstock Area: {calc.feedstock.cross_sectional_area_mm2:.2f} mm²")

    # Calculate theoretical volume (uncalibrated)
    print("\n--- Step 1: Calculate Theoretical Volume ---")
    df_processed = calc.process_dataframe(df)
    stats = calc.get_statistics(df_processed)

    theoretical_volume_cm3 = 0.0
    if "total_volume" in stats:
        theoretical_volume_cm3 = stats["total_volume"]["cm3"]
        print(f"Theoretical Volume: {theoretical_volume_cm3:.2f} cm³")
    else:
        print(
            "Warning: Could not calculate total volume (missing position data?). Estimating from feed rate."
        )
        total_time_min = df_processed["TimeInSeconds"].max() / 60.0
        avg_volume_rate = (
            stats["process"]["feed_vel_mean"] * calc.feedstock.cross_sectional_area_mm2
        )
        theoretical_volume_cm3 = (avg_volume_rate * total_time_min) / 1000.0
        print(f"Estimated from feed rate: {theoretical_volume_cm3:.2f} cm³")

    print(f"Bead Area: {stats['bead_area']['mean']:.2f} ± {stats['bead_area']['std']:.2f} mm²")
    print(f"Thickness: {stats['thickness']['mean']:.2f} ± {stats['thickness']['std']:.2f} mm")

    # Calculate correction factor
    print("\n--- Step 2: Calculate Correction Factor ---")
    if theoretical_volume_cm3 == 0:
        print("Error: Theoretical volume is zero, cannot calculate correction factor.")
        return None

    correction_factor = actual_volume_cm3 / theoretical_volume_cm3
    print(
        f"Correction Factor = {actual_volume_cm3:.2f} / {theoretical_volume_cm3:.2f} = {correction_factor:.4f}"
    )

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

    calibrated_volume_cm3 = 0.0
    if "total_volume" in stats_calibrated:
        calibrated_volume_cm3 = stats_calibrated["total_volume"]["cm3"]
    else:
        # Recalculate estimated volume with correction factor
        total_time_min = df_calibrated["TimeInSeconds"].max() / 60.0
        avg_volume_rate = (
            stats_calibrated["process"]["feed_vel_mean"] * calc.feedstock.cross_sectional_area_mm2
        )
        calibrated_volume_cm3 = (avg_volume_rate * total_time_min * correction_factor) / 1000.0

    print(f"Calibrated Volume: {calibrated_volume_cm3:.2f} cm³")
    print(f"Target Volume: {actual_volume_cm3:.2f} cm³")

    error = abs(calibrated_volume_cm3 - actual_volume_cm3)
    error_percent = (error / actual_volume_cm3) * 100 if actual_volume_cm3 != 0 else 0
    print(f"Remaining Error: {error:.3f} cm³ ({error_percent:.2f}%)")

    if error_percent < 5.0:
        print("✓ Calibration successful! (< 5% error)")
    else:
        print("⚠ Consider fine-tuning with area_offset parameter")

    # Save calibration
    print("\n--- Step 5: Save Calibration ---")
    new_config = {
        "feedstock": {
            "dimension_inches": calc.feedstock.dimension_inches,
            "shape": calc.feedstock.shape,
            "comments": f"Calibrated from {os.path.basename(csv_file_path)}",
        },
        "bead_geometry": {
            "length_mm": calc.bead_geometry.length_mm,
            "radius_mm": calc.bead_geometry.radius_mm,
            "max_thickness_mm": calc.bead_geometry.max_thickness_mm,
            "comments": "Default capsule geometry",
        },
        "calibration": {
            "correction_factor": correction_factor,
            "area_offset": 0.0,
            "comments": f"Calibrated to match {actual_volume_cm3} cm³ physical measurement",
        },
    }

    save_calibration_config(new_config)

    return calc


def analyze_volume_distribution(csv_file_path):
    """
    Analyze volume distribution throughout the print.

    This helps identify if calibration needs to be non-uniform.
    """
    print("\n=== Volume Distribution Analysis ===")

    # Load data
    try:
        df = pd.read_csv(csv_file_path)
        print(f"Loaded {len(df)} rows from CSV")
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return

    # Load calibrated calculator
    config = load_calibration_config()
    calc = VolumeCalculator()

    if config and "calibration" in config:
        calc.set_calibration(
            correction_factor=config["calibration"]["correction_factor"],
            area_offset=config["calibration"]["area_offset"],
        )
        print(
            f"Using calibration from config (factor: {config['calibration']['correction_factor']:.4f})."
        )
    else:
        print("No calibration found in config, using uncalibrated calculator.")

    # Process data
    df_processed = calc.process_dataframe(df)

    # Analyze by layer (Z position)
    if "ZPos" in df_processed.columns:
        # Group by Z layer (round to nearest 0.5mm)
        df_processed["Layer"] = (df_processed["ZPos"] / 0.5).round() * 0.5

        layer_stats = df_processed.groupby("Layer").agg(
            {
                "Bead_Area_mm2": ["mean", "std"],
                "Bead_Thickness_mm": ["mean", "std"],
                "FeedVel": "mean",
                "PathVel": "mean",
            }
        )

        print("\nLayer-by-layer analysis:")
        print(layer_stats.head(10))

        # Check for variations
        if not df_processed["Bead_Area_mm2"].empty:
            area_mean = df_processed["Bead_Area_mm2"].mean()
            area_std = df_processed["Bead_Area_mm2"].std()
            area_variation = area_std / area_mean if area_mean != 0 else 0
        else:
            area_variation = 0

        if not df_processed["Bead_Thickness_mm"].empty:
            thickness_mean = df_processed["Bead_Thickness_mm"].mean()
            thickness_std = df_processed["Bead_Thickness_mm"].std()
            thickness_variation = thickness_std / thickness_mean if thickness_mean != 0 else 0
        else:
            thickness_variation = 0

        print("\nOverall Variations:")
        print(f"  Bead Area CV: {area_variation*100:.1f}%")
        print(f"  Thickness CV: {thickness_variation*100:.1f}%")

        if area_variation > 0.2:
            print("⚠ High variation in bead area - consider segment-specific calibration")
        else:
            print("✓ Bead area is relatively consistent")
    else:
        print("No 'ZPos' column found in data for layer-by-layer analysis.")


def main_menu():
    while True:
        print("\n" + "=" * 40)
        print("MELD Volume Calibration Tool (Interactive)")
        print("=" * 40)
        print("1. Perform Volume Calibration")
        print("2. Analyze Volume Distribution")
        print("3. Exit")
        print("=" * 40)

        choice = input("Enter your choice (1-3): ")

        if choice == "1":
            csv_path = input("Enter path to CSV file (e.g., data/csv/20250707144618.csv): ")
            try:
                actual_volume_cm3 = float(input("Enter measured physical volume in cm³: "))
                calibrate_from_physical_measurement(csv_path, actual_volume_cm3)
            except ValueError:
                print("Invalid volume. Please enter a number.")
            except Exception as e:
                print(f"An error occurred during calibration: {e}")
        elif choice == "2":
            csv_path = input("Enter path to CSV file (e.g., data/csv/20250707144618.csv): ")
            try:
                analyze_volume_distribution(csv_path)
            except Exception as e:
                print(f"An error occurred during analysis: {e}")
        elif choice == "3":
            print("Exiting MELD Volume Calibration Tool. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")


if __name__ == "__main__":
    main_menu()
