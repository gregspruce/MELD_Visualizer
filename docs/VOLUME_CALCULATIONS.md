# MELD Volume Calculations Documentation

## Overview

The MELD Visualizer volume calculation system provides accurate 3D visualization of extruded material volume based on process parameters. This document explains the physics, implementation, and calibration of the volume calculation system.

## Physical Principles

### Conservation of Mass

The fundamental principle is conservation of mass:
```
Volume_in = Volume_out
Feed_velocity × Feedstock_area = Path_velocity × Bead_area
```

Therefore:
```python
Bead_area = (Feed_velocity × Feedstock_area) / Path_velocity
```

### Feedstock Geometry

MELD uses **square rod feedstock**, not circular wire:
- Dimension: 0.5" × 0.5" (12.7mm × 12.7mm)
- Cross-sectional area: 161.3 mm²

### Bead Geometry Model

The extruded bead is modeled as a **capsule shape**:
- Rectangular center section with length L (default: 2.0 mm)
- Semi-circular ends with radius R (default: 1.0 mm)
- Variable thickness T calculated from conservation of mass

Total bead area formula:
```
Bead_Area = π × R² + L × T
```

Solving for thickness:
```
T = (Bead_Area - π × R²) / L
```

## Module Structure

### 1. `volume_calculations.py`
Handles all physics calculations:
- `FeedstockParameters`: Defines feedstock material properties
- `BeadGeometry`: Defines bead shape parameters
- `VolumeCalculator`: Performs volume calculations with calibration support

### 2. `volume_mesh.py`
Generates 3D mesh for visualization:
- `MeshGenerator`: Creates 3D geometry from calculated volumes
- `VolumePlotter`: High-level interface combining calculations and mesh generation

### 3. `data_service.py`
Integrates volume components with the main application:
- Provides caching for performance
- Handles data validation
- Manages calibration settings

## Usage Examples

### Basic Volume Calculation

```python
from meld_visualizer.core.volume_calculations import VolumeCalculator

# Initialize calculator with default parameters
calc = VolumeCalculator()

# Process a DataFrame
df_with_volumes = calc.process_dataframe(df)

# Get statistics
stats = calc.get_statistics(df_with_volumes)
print(f"Total volume: {stats['total_volume']['cm3']:.2f} cm³")
```

### Custom Feedstock Parameters

```python
from meld_visualizer.core.volume_calculations import FeedstockParameters, VolumeCalculator

# Define custom feedstock (e.g., different size)
feedstock = FeedstockParameters(
    dimension_inches=0.375,  # 3/8" square rod
    shape='square'
)

calc = VolumeCalculator(feedstock=feedstock)
```

### Calibration for Physical Validation

```python
# After comparing with physical print results
calc.set_calibration(
    correction_factor=1.05,  # 5% increase to match actual volume
    area_offset=2.0  # Add 2 mm² systematic offset
)
```

### Mesh Generation with LOD

```python
from meld_visualizer.core.volume_mesh import VolumePlotter

plotter = VolumePlotter()

# Prepare data
df_prepared = plotter.prepare_data(df)

# Generate mesh with different LOD settings
mesh_high = plotter.generate_plot_data(df_prepared, 'ZPos', lod='high')
mesh_low = plotter.generate_plot_data(df_prepared, 'ZPos', lod='low')
```

## Calibration Process

### Step 1: Baseline Measurement
1. Print a test part with known, constant parameters
2. Record feed velocity and path velocity from CSV
3. Measure actual deposited volume or mass

### Step 2: Calculate Theoretical Volume
```python
calc = VolumeCalculator()
df_test = calc.process_dataframe(df_from_csv)
stats = calc.get_statistics(df_test)
calculated_volume = stats['total_volume']['cm3']
```

### Step 3: Determine Correction Factor
```python
actual_volume = 125.5  # cm³ (measured)
calculated_volume = 119.2  # cm³ (from CSV)

correction_factor = actual_volume / calculated_volume  # 1.053
```

### Step 4: Apply Calibration
```python
calc.set_calibration(correction_factor=1.053)
```

### Step 5: Validate
Re-process the data and verify the calculated volume matches the physical measurement.

## Configuration File

The system uses `config/volume_calibration.json` for persistent calibration:

```json
{
  "feedstock": {
    "dimension_inches": 0.5,
    "shape": "square"
  },
  "bead_geometry": {
    "length_mm": 2.0,
    "radius_mm": 1.0,
    "max_thickness_mm": 25.4
  },
  "calibration": {
    "correction_factor": 1.0,
    "area_offset": 0.0
  }
}
```

## Data Columns Added

When processing a DataFrame, the following columns are added:

| Column | Description | Units |
|--------|-------------|-------|
| `Bead_Area_mm2` | Cross-sectional area of the bead | mm² |
| `Bead_Thickness_mm` | Thickness of the bead (T parameter) | mm |
| `Feedstock_Area_mm2` | Cross-sectional area of feedstock | mm² |
| `Volume_Rate_mm3_per_min` | Volumetric flow rate | mm³/min |
| `Segment_Length_mm` | Length of each toolpath segment | mm |
| `Segment_Time_min` | Time to traverse segment | minutes |
| `Segment_Volume_mm3` | Volume deposited in segment | mm³ |

## Performance Considerations

### Caching
- Mesh generation results are cached by the data service
- Cache key includes DataFrame size, color column, and LOD setting

### Level of Detail (LOD)
Three LOD settings optimize performance:
- **High**: 12 points per cross-section, every segment
- **Medium**: 8 points per cross-section, every 2nd segment
- **Low**: 6 points per cross-section, every 4th segment

### Memory Optimization
- Uses float32 for numerical data
- Pre-allocates arrays for mesh generation
- Processes large datasets in chunks

## Troubleshooting

### Common Issues

1. **Calculated volume doesn't match physical print**
   - Solution: Calibrate using the process described above
   - Check feedstock dimensions are correct

2. **Mesh generation is slow**
   - Solution: Use lower LOD for initial visualization
   - Enable caching in data service

3. **Missing volume columns**
   - Solution: Ensure DataFrame has `FeedVel` and `PathVel` columns
   - Call `calc.process_dataframe()` before mesh generation

## API Reference

### VolumeCalculator Methods

- `calculate_bead_area(feed_velocity, path_velocity)`: Calculate bead cross-sectional area
- `calculate_bead_thickness(feed_velocity, path_velocity)`: Calculate bead thickness
- `process_dataframe(df, inplace=False)`: Add volume columns to DataFrame
- `get_statistics(df)`: Get volume statistics
- `set_calibration(correction_factor, area_offset)`: Set calibration factors
- `export_parameters()`: Export all parameters for persistence

### MeshGenerator Methods

- `generate_cross_section(position, direction, thickness, bead_length, bead_radius)`: Generate single cross-section
- `generate_mesh(df, color_column, bead_length, bead_radius)`: Generate complete mesh
- `generate_mesh_lod(df, color_column, lod, bead_length, bead_radius)`: Generate mesh with LOD

### VolumePlotter Methods

- `prepare_data(df, min_feed_velocity, min_path_velocity)`: Filter and prepare data
- `generate_plot_data(df, color_column, lod)`: Generate plot-ready mesh
- `get_statistics(df)`: Get volume statistics
- `set_calibration(correction_factor, area_offset)`: Set calibration
- `export_config()`: Export configuration

## Future Enhancements

1. **Variable bead geometry**: Support for different bead shapes based on process parameters
2. **Material density**: Calculate mass from volume using material properties
3. **Multi-material support**: Handle different feedstock materials in same print
4. **Real-time validation**: Compare calculated vs. measured volume during printing
5. **Machine learning calibration**: Automatic calibration based on historical data