# MELD Volume Calculations Documentation

## Overview

The MELD Visualizer volume calculation system provides accurate 3D visualization of extruded material volume based on process parameters. This document explains the physics, implementation, and calibration of the volume calculation system.

## Physical Principles

The fundamental principle is the conservation of mass:

`Volume_in = Volume_out`

`Feed_velocity × Feedstock_area = Path_velocity × Bead_area`

Therefore, the bead area can be calculated as:

`Bead_area = (Feed_velocity × Feedstock_area) / Path_velocity`

## Module Structure

The volume calculation system is organized into the following modules:

- **`src/meld_visualizer/core/volume_calculations.py`:** Handles the core physics calculations, including bead area and thickness.
- **`src/meld_visualizer/core/volume_mesh.py`:** Generates the 3D mesh for visualization based on the calculated volumes.
- **`src/meld_visualizer/services/data_service.py`:** Integrates the volume calculation components with the main application, providing caching and data management.

## Calibration

The system can be calibrated to match the physical output of the MELD machine. The calibration process involves:

1.  **Printing a test part:** A test part with known parameters is printed.
2.  **Measuring the actual volume:** The actual volume of the printed part is measured.
3.  **Calculating the theoretical volume:** The theoretical volume is calculated based on the process parameters.
4.  **Determining the correction factor:** The correction factor is calculated by dividing the actual volume by the theoretical volume.
5.  **Applying the correction factor:** The correction factor is applied to all subsequent volume calculations.

## Configuration

The volume calculation system is configured through the `config/volume_calibration.json` file. This file allows you to specify the feedstock parameters, bead geometry, and calibration settings.

## Performance

The system includes several performance optimizations:

- **Caching:** The results of the mesh generation are cached to improve performance.
- **Level of Detail (LOD):** The system supports multiple levels of detail for the 3D mesh, allowing you to trade off between performance and visual quality.
- **Memory Optimization:** The system is designed to be memory-efficient, allowing it to handle large datasets.
