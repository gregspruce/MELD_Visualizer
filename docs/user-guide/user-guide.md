# MELD Visualizer User Guide

## Table of Contents
1. [Getting Started](#getting-started)
2. [File Upload](#file-upload)
3. [3D Visualizations](#3d-visualizations)
4. [2D Plots](#2d-plots)
5. [Data Filtering](#data-filtering)
6. [Settings & Configuration](#settings-configuration)
7. [Tips & Tricks](#tips-tricks)
8. [Troubleshooting](#troubleshooting)

## Getting Started

### System Requirements
- **Operating System**: Windows 10/11, macOS 10.14+, Linux (Ubuntu 20.04+)
- **Python**: 3.8 or higher
- **Browser**: Chrome, Firefox, Safari, or Edge (latest versions)
- **RAM**: Minimum 4GB, recommended 8GB+
- **Storage**: 500MB for application + space for data files

### Installation

#### Option 1: From PyPI (Recommended)
```bash
# Install the package
pip install meld-visualizer

# Run the application
meld-visualizer
```

#### Option 2: From Source
```bash
# Clone the repository
git clone https://github.com/MELD-labs/meld-visualizer.git
cd meld-visualizer

# Install in development mode
pip install -e .

# Run the application
python -m meld_visualizer
# OR
meld-visualizer
```

#### Option 3: Legacy Installation
```bash
# For older setup or specific requirements
pip install -r requirements.txt

# Run from source
python -m src.meld_visualizer.app
```

#### Option 4: Standalone Executable
1. Download the latest release from GitHub
2. Extract the ZIP file
3. Run `MELD-Visualizer.exe` (Windows) or `MELD-Visualizer` (macOS/Linux)

### First Launch
1. Open your browser and navigate to `http://127.0.0.1:8050`
2. The application will load with the default theme
3. You'll see the main interface with upload section and visualization tabs

## File Upload

### Supported File Types

#### CSV Files
- **Format**: Comma-separated values
- **Required Columns**: XPos, YPos, ZPos
- **Optional Columns**: FeedVel, PathVel, ToolTemp, Time, etc.
- **Size Limit**: 10MB

#### G-code Files (.nc)
- **Format**: Standard G-code with MELD extensions
- **Supported Commands**: G0, G1, G2, G3, M34, M35
- **Comments**: Semicolon (;) or parentheses ()

### Upload Process

#### Step 1: Select File Type
1. Click on the appropriate upload area
2. CSV files → "Drop CSV files or Click to Select"
3. G-code files → "Drop .nc files or Click to Select"

#### Step 2: Choose File
- **Drag & Drop**: Drag file directly onto upload area
- **Browse**: Click to open file browser

#### Step 3: Wait for Processing
- Progress indicator shows during upload
- Unit conversion happens automatically
- Success message appears when complete

### Unit Conversion
The application automatically detects and converts imperial units to metric:
- **Detection**: Based on velocity ranges
- **Conversion**: Inches → Millimeters
- **Notification**: Banner shows when conversion occurs

### Data Validation
Files are validated for:
- Correct file extension
- Valid data format
- Required columns present
- No malicious content
- Size within limits

## 3D Visualizations

### Main 3D Scatter Plot

#### Navigation Controls
- **Rotate**: Click and drag
- **Zoom**: Scroll wheel or pinch
- **Pan**: Right-click and drag
- **Reset**: Double-click

#### Customization Options

##### Color Column Selection
1. Navigate to Graph 1 tab
2. Select column from "Choose a color column" dropdown
3. Common options: ToolTemp, FeedVel, PathVel
4. Plot updates automatically

##### Z-Axis Scaling
1. Locate "Z-axis Stretch Factor" slider
2. Adjust value (0.1 to 10)
3. Higher values exaggerate vertical features
4. Useful for viewing layer details

##### Time Range Filtering
1. Use the time range slider
2. Drag handles to select time window
3. Or enter values in input boxes
4. Click "Update" to apply

### 3D Mesh Visualization

#### Generating the Mesh
1. Navigate to "3D Graph" tab
2. Click "Generate 3D Mesh Plot" button
3. Select color column for mesh coloring
4. Adjust color scale if needed

#### Mesh Options
- **Level of Detail**: High/Medium/Low
- **Color Scale**: Min/Max values
- **Z-Stretch**: Vertical exaggeration
- **Opacity**: Transparency level

### 3D Line Plot

#### Creating Line Plots
1. Go to "3D Graph" tab
2. Click "Generate 3D Line Plot"
3. Shows toolpath as connected lines
4. Color represents selected parameter

#### Line Plot Features
- Shows sequential tool movement
- Highlights path continuity
- Reveals toolpath patterns
- Useful for path analysis

## 2D Plots

### Time Series Plots

#### Setup
1. Navigate to "2D Plot" tab
2. Select Y-axis parameter
3. Choose color parameter (optional)
4. Plot generates automatically

#### Interactive Features
- **Zoom**: Select area to zoom
- **Pan**: Drag to move view
- **Hover**: See exact values
- **Export**: Save as image

### Histogram Plots

#### Creating Histograms
1. Select "Histogram" plot type
2. Choose parameter to analyze
3. Adjust bin count if needed
4. View distribution

#### Analysis Features
- Distribution shape
- Outlier detection
- Statistical summary
- Frequency analysis

## Data Filtering

### Range Filtering

#### Using the Range Slider
1. Locate filter section in sidebar
2. Select column to filter
3. Drag slider handles or enter values
4. Click "Apply Filter"

#### Custom Column Filtering
1. Choose column from dropdown
2. Set minimum value
3. Set maximum value
4. Apply to all plots

### Active Data Filtering

#### Feed Velocity Filter
- Automatically filters inactive periods
- Shows only when FeedVel > 0
- Toggle on/off in settings

#### Time-Based Filtering
- Select specific time ranges
- Filter by date/time
- Useful for batch analysis

## Settings & Configuration

### Theme Selection

#### Changing Themes
1. Go to "Settings" tab
2. Select theme from dropdown
3. Choose matching Plotly template
4. Click "Save Configuration"
5. Restart application

#### Available Themes
- **Light Themes**: Cerulean, Cosmo, Flatly, Journal
- **Dark Themes**: Cyborg, Darkly, Slate, Solar
- **Professional**: Lux, Materia, Pulse, Sandstone

### Plot Options

#### Configuring Default Columns
1. Navigate to Settings
2. Select default columns for each plot type
3. Save configuration
4. New defaults apply on restart

#### Custom Column Mappings
- Map your data columns to standard names
- Useful for non-standard CSV formats
- Saves time on repeated uploads

### Saving Configuration

#### Export Settings
1. Click "Export Configuration"
2. Save config.json file
3. Share with team members

#### Import Settings
1. Replace config.json in app directory
2. Restart application
3. Settings applied automatically

## Tips & Tricks

### Performance Optimization

#### Large Files
- Use sampling for initial exploration
- Apply filters to reduce data
- Lower mesh detail for faster rendering
- Close unnecessary plots

#### Smooth Navigation
- Disable auto-rotate in 3D plots
- Use keyboard shortcuts
- Reduce marker size for many points
- Turn off shadows for speed

### Visualization Best Practices

#### Color Selection
- Use temperature for thermal data
- Velocity for motion analysis
- Time for sequential viewing
- Custom columns for specific analysis

#### Z-Axis Scaling
- Start with 1.0 (no scaling)
- Increase to 2-5 for layer visibility
- Use 10+ for extreme detail
- Match to your data characteristics

### Keyboard Shortcuts
- **Ctrl+O**: Open file (when supported)
- **Ctrl+S**: Save configuration
- **Ctrl+R**: Reset view
- **Esc**: Cancel operation
- **F11**: Fullscreen mode

## Troubleshooting

### Common Issues

#### Application Won't Start
```bash
# Check Python version
python --version  # Should be 3.8+

# Reinstall dependencies
pip install -r requirements.txt --upgrade

# Run in debug mode
DEBUG=1 meld-visualizer
# OR
DEBUG=1 python -m meld_visualizer
```

#### File Upload Fails
- Check file size (< 10MB)
- Verify file format (CSV or .nc)
- Ensure required columns present
- Look for error messages

#### Slow Performance
1. Reduce data points (filter/sample)
2. Lower mesh detail
3. Close other applications
4. Clear browser cache
5. Restart application

#### Plot Not Updating
- Click "Update" button explicitly
- Check if data is filtered out
- Verify column selection
- Refresh browser page

### Error Messages

#### "File too large"
- Reduce file size below 10MB
- Split into multiple files
- Use data sampling

#### "Invalid file format"
- Check file extension
- Verify CSV structure
- Ensure UTF-8 encoding

#### "Missing required columns"
- Add XPos, YPos, ZPos columns
- Check column naming
- Use column mapping in settings

#### "Units converted to mm"
- Informational only
- Data automatically converted
- Original file unchanged

### Getting Help

#### Resources
- **GitHub Issues**: Report bugs at https://github.com/MELD-labs/meld-visualizer/issues
- **Documentation**: This guide and others in `docs/` directory
- **Sample Files**: Available in `data/csv/` and `data/nc/` directories
- **API Documentation**: See `docs/api/` for technical specifications
- **Community Forum**: Coming soon

#### Debug Information
When reporting issues, include:
1. Error message (exact text)
2. File that caused issue (if shareable)
3. Browser and OS version
4. Steps to reproduce
5. Screenshots if applicable

### Advanced Features

#### Custom Workflows
- Chain multiple filters
- Export filtered data
- Batch processing scripts
- API integration (future)

#### Data Analysis
- Statistical summaries
- Correlation analysis
- Pattern detection
- Anomaly identification

## Best Practices Summary

### Do's
- Save configuration regularly
- Use appropriate Z-scaling
- Filter large datasets
- Keep files under 10MB
- Use consistent column naming

### Don'ts
- Don't upload sensitive data
- Don't ignore error messages
- Don't use incompatible formats
- Don't bypass security warnings
- Don't modify system files

## Appendix

### Sample Data Format

#### CSV Example
```csv
XPos,YPos,ZPos,FeedVel,PathVel,ToolTemp,Time
0.0,0.0,0.0,0.0,0.0,20.0,2024-01-01 00:00:00
10.5,10.5,0.5,50.0,25.0,150.0,2024-01-01 00:00:01
20.0,20.0,1.0,100.0,50.0,200.0,2024-01-01 00:00:02
```

#### G-code Example
```gcode
; MELD Program Start
G0 X0 Y0 Z0 ; Rapid to origin
G1 X10 Y10 F100 ; Linear move
M34 S4200 ; Start material feed
G1 X20 Y20 Z5 ; Continue path
M35 ; Stop material feed
```

### Configuration Reference
See `config/config.json` for all available options and their default values. The configuration file is located in the `config/` directory within your installation.