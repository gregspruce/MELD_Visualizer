# MELD Visualizer User Guide

## Getting Started

### Installation

```bash
# Install the package
pip install meld-visualizer

# Run the application
meld-visualizer
```

### First Launch

1.  Open your browser and navigate to `http://127.0.0.1:8050`.
2.  The application will load with the default theme.

## File Upload

### Supported File Types

- **CSV Files:** Comma-separated values files with columns for `XPos`, `YPos`, and `ZPos`.
- **G-code Files (.nc):** Standard G-code files.

### Upload Process

1.  Drag and drop your file onto the upload area, or click to browse for a file.
2.  The application will automatically process the file and display the data.

## 3D Visualizations

### Main 3D Scatter Plot

- **Navigation:** Rotate, zoom, and pan the 3D view with your mouse.
- **Customization:** Change the color of the points, adjust the Z-axis scaling, and filter the data by time.

### 3D Mesh Visualization

- **Generation:** Generate a 3D mesh from your data to visualize the volume of the printed part.
- **Options:** Adjust the level of detail, color scale, and opacity of the mesh.

## 2D Plots

- **Time Series Plots:** Plot any two columns of your data against each other to see how they change over time.
- **Histograms:** View the distribution of your data to identify trends and outliers.

## Data Filtering

- **Range Filtering:** Filter your data by a range of values for any column.
- **Active Data Filtering:** Automatically filter out inactive periods to focus on the most important data.

## Settings & Configuration

- **Themes:** Choose from over 20 different themes to customize the look and feel of the application.
- **Feedstock Geometry:** Configure the feedstock geometry to ensure accurate volume calculations.
- **Plot Options:** Customize the default columns and other options for each plot.

## Volume Calculations

For a detailed explanation of the physics, implementation, and calibration of the volume calculation system, please see the [Volume Calculations Documentation](../VOLUME_CALCULATIONS.md).
