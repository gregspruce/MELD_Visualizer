# MELD Visualizer User Guide

This guide provides comprehensive information for users of the MELD Visualizer application.

## 1. Overview

The MELD Visualizer is a powerful tool for engineers, technicians, and researchers to analyze and understand the data generated during the MELD manufacturing process. It provides interactive 3D visualizations of toolpaths, material deposition, and process parameters, enabling users to gain insights into the quality and characteristics of the manufactured part.

### Key Features

*   **Interactive 3D Visualization:** Explore toolpaths and volumetric data in a fully interactive 3D environment.
*   **G-Code and CSV Support:** Load and visualize data from standard G-code files or detailed CSV process logs.
*   **Volumetric Mesh Generation:** Accurately visualizes the volume of deposited material based on process parameters.
*   **Data Filtering and Analysis:** Filter data by time, layer, and other parameters to isolate and inspect specific regions of the part.
*   **Enhanced Desktop UI:** A modern, responsive user interface optimized for desktop use, featuring tabbed navigation, organized control panels, and real-time user feedback.
*   **Customizable Plots:** Adjust plot settings, such as Z-axis scaling, to enhance visualization and analysis.

## 2. Getting Started

### Prerequisites

*   Python 3.8+
*   Git

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/gregspruce/MELD_Visualizer.git
    cd MELD_Visualizer
    ```

2.  **Install dependencies:**
    Install the project in editable mode with all development, testing, and build dependencies.
    ```bash
    pip install -e ".[dev,test,playwright,build]"
    ```

### Running the Application

Once installed, you can run the application using the following command:

```bash
meld-visualizer
```

The application will be available at `http://127.0.0.1:8050`.

To run in debug mode for development, use:
```bash
DEBUG=1 meld-visualizer
```

## 3. Enhanced Desktop User Interface

The MELD Visualizer features an enhanced desktop UI designed for improved usability and responsiveness.

### Core Components

The Enhanced UI is composed of several key components:

*   **Enhanced Tabs:** A tab navigation system with overflow handling and keyboard navigation.
*   **Control Panels:** Collapsible and organized panels for grouping UI controls.
*   **User Feedback System:** A system for providing users with feedback, including toast notifications, loading overlays, and progress indicators.

### Key Features

*   **Responsive Design:** The UI is optimized for a range of desktop resolutions, from 1024x768 to 2560x1440 and beyond.
*   **Accessibility:** The system is designed to be WCAG 2.1 compliant, with features like keyboard navigation, ARIA labels, and high-contrast-friendly styling.
*   **Performance:** The system is designed to be performant, with client-side optimizations to reduce server load and provide a smooth user experience.

### Component Creation (for advanced users/developers)

*   **Enhanced Tabs**
    ```python
    from src.meld_visualizer.core import layout

    tabs = layout.create_enhanced_tabs(
        tabs_config=[
            {'id': 'tab1', 'label': 'Tab 1', 'content': content1},
            {'id': 'tab2', 'label': 'Tab 2', 'content': content2}
        ],
        active_tab='tab1'
    )
    ```

*   **Control Panel**
    ```python
    from src.meld_visualizer.core import layout

    panel = layout.create_control_panel(
        title="Settings",
        controls=[...],
        collapsible=True,
        initial_collapsed=False
    )
    ```

## 4. Interactive Volume Calibration Tool

This section provides instructions for using the interactive volume calibration tool, `interactive_volume_calibration.py`.

### Purpose

The `interactive_volume_calibration.py` script provides a terminal-based interactive interface for performing volume calibration and analyzing volume distribution of MELD prints. It leverages the core volume calculation logic from the `src/meld_visualizer` package.

### Script Location

The script is located at:
`c:\VSCode\AFSD_Programs\MELD_Visualizer\tools\interactive_volume_calibration.py`

### How to Run

To run the interactive tool, execute the script from your terminal. It is recommended to suppress the default logging from the `meld_visualizer` package for a cleaner console output by setting the `MELD_LOGGING` environment variable to `false`.

**On Windows (PowerShell):**

```powershell
$env:MELD_LOGGING="false"; python c:\VSCode\AFSD_Programs\MELD_Visualizer\tools\interactive_volume_calibration.py
```

**On Windows (Command Prompt):**

```cmd
set MELD_LOGGING=false && python c:\VSCode\AFSD_Programs\MELD_Visualizer\tools\interactive_volume_calibration.py
```

**On Linux/macOS:**

```bash
MELD_LOGGING=false python c:\VSCode\AFSD_Programs\MELD_Visualizer\tools\interactive_volume_calibration.py
```

### Usage

Upon running the script, you will be presented with a main menu:

```
========================================
MELD Volume Calibration Tool (Interactive)
========================================
1. Perform Volume Calibration
2. Analyze Volume Distribution
3. Exit
========================================
Enter your choice (1-3):
```

#### Option 1: Perform Volume Calibration

This option guides you through calibrating the volume calculations based on a physical measurement. You will be prompted to provide:

*   **Path to CSV file:** The path to a CSV file generated from a MELD print (e.g., `data/csv/20250707144618.csv`).
*   **Measured physical volume in cm³:** The actual measured volume of the physical print in cubic centimeters.

The script will then calculate a correction factor, validate the calibration, and save the updated calibration configuration to `config/volume_calibration.json`.

#### Option 2: Analyze Volume Distribution

This option allows you to analyze the volume distribution throughout a MELD print. You will be prompted to provide:

*   **Path to CSV file:** The path to a CSV file generated from a MELD print.

The script will process the data and provide layer-by-layer analysis, including bead area and thickness variations, which can help identify if non-uniform calibration is needed.

#### Option 3: Exit

Exits the interactive tool.

### Dependencies and Configuration

*   The script relies on the `pandas` library for data handling and modules within the `src/meld_visualizer/core` package for volume calculations.
*   Calibration settings are loaded from and saved to `config/volume_calibration.json`. Ensure this file exists or is created in the `config/` directory relative to the project root. If the file does not exist, default values will be used for feedstock and bead geometry.

## 5. Configuration

The MELD Visualizer can be configured through `config/config.json`. This file allows you to specify various application settings, including themes, plot options, and column mappings.

## 6. Troubleshooting

(Placeholder for common user issues and solutions)