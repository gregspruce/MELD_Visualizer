"""
Constants module for MELD Visualizer application.
Contains all magic numbers, thresholds, and configuration constants.
"""

# Unit Conversion Constants
INCH_TO_MM = 25.4
MM_TO_INCH = 1.0 / 25.4

# Processing and Calculation Constants
MELD_FEED_VELOCITY_SCALE_FACTOR = 10.0  # Scale factor for feed velocity processing
SECONDS_PER_MINUTE = 60.0  # Conversion factor for time calculations
MM3_TO_CM3 = 1000.0  # Volume conversion factor
MESH_VERTICES_PER_CROSS_SECTION = 12  # Number of vertices in mesh cross-sections

# Network Configuration
DEFAULT_HOST = "127.0.0.1"  # Default server host address
DEFAULT_PORT = 8050  # Default server port

# Performance Monitoring
PERFORMANCE_WARNING_THRESHOLD_SECONDS = 2.0  # Warning threshold for slow operations

# Data Processing Thresholds
IMPERIAL_VELOCITY_THRESHOLD = 100  # Max velocity in imperial units (inch/min)
MIN_PATH_VELOCITY = 1e-6  # Minimum path velocity to consider as active
MIN_FEED_VELOCITY = 0  # Minimum feed velocity for active extrusion
EPSILON_TOLERANCE = 1e-9  # Small value for floating point comparisons

# Mesh Generation Parameters
BEAD_LENGTH_MM = 2.0  # Length of each bead segment in mm
BEAD_RADIUS_MM = BEAD_LENGTH_MM / 2.0
ANGLE_STEP_DEGREES = 30  # Angular step for mesh generation
POINTS_PER_SECTION = int(360 / ANGLE_STEP_DEGREES)
MAX_BEAD_THICKNESS_MM = 1.0 * INCH_TO_MM  # Maximum bead thickness
BEAD_THICKNESS_RATIO = 0.8  # Ratio of actual to maximum thickness

# Feedstock Geometry Constants
# MELD uses 0.5" × 0.5" square rod feedstock, not circular wire
FEEDSTOCK_DIMENSION_INCHES = 0.5  # Square rod dimension (inches)
FEEDSTOCK_DIMENSION_MM = FEEDSTOCK_DIMENSION_INCHES * INCH_TO_MM  # Convert to mm
FEEDSTOCK_AREA_MM2 = FEEDSTOCK_DIMENSION_MM ** 2  # Square rod area (mm²)

# Legacy constants for backward compatibility
WIRE_DIAMETER_MM = FEEDSTOCK_DIMENSION_MM  # For backward compatibility (now represents square dimension)

# Feedstock type configuration
FEEDSTOCK_TYPES = {
    'square': {
        'dimension_mm': FEEDSTOCK_DIMENSION_MM,
        'area_mm2': FEEDSTOCK_AREA_MM2,
        'description': 'Square rod feedstock (0.5" × 0.5")'
    },
    'circular': {
        'diameter_mm': FEEDSTOCK_DIMENSION_MM,
        'area_mm2': 3.14159 * (FEEDSTOCK_DIMENSION_MM / 2) ** 2,
        'description': 'Circular wire feedstock (0.5" diameter)'
    }
}
DEFAULT_FEEDSTOCK_TYPE = 'square'  # MELD uses square rod

# File Processing Limits
MAX_FILE_SIZE_MB = 10  # Maximum upload file size
MAX_GCODE_LINES = 100000  # Maximum number of G-code lines to process
MAX_GCODE_LINE_LENGTH = 1000  # Maximum length of a single G-code line
MAX_CONFIG_SIZE_KB = 100  # Maximum configuration file size
ALLOWED_FILE_EXTENSIONS = {'.csv', '.nc', '.gcode', '.txt'}  # Allowed upload file types

# UI Display Constants
DEFAULT_GRAPH_MARGIN = dict(l=0, r=0, b=0, t=0)
DEFAULT_ASPECT_MODE = 'data'
DEFAULT_Z_STRETCH_FACTOR = 1.0
MIN_Z_STRETCH_FACTOR = 0.1
MAX_Z_STRETCH_FACTOR = 10.0

# UI Timing Constants (milliseconds)
UI_DEBOUNCE_DELAY_MS = 300  # Debounce delay for UI interactions
VIEWPORT_CHECK_INTERVAL_MS = 5000  # Interval for viewport dimension checks
CONFIG_ALERT_DURATION_MS = 10000  # Duration for configuration alert messages
ALERT_DURATION_SUCCESS_MS = 4000  # Success alert duration
ALERT_DURATION_ERROR_MS = 6000  # Error alert duration
ALERT_DURATION_INFO_MS = 3000  # Info alert duration
ALERT_DURATION_DEFAULT_MS = 5000  # Default alert duration

# UI Dimensions and Scaling
DEFAULT_VIEWPORT_WIDTH = 1920  # Default viewport width in pixels
DEFAULT_VIEWPORT_HEIGHT = 1080  # Default viewport height in pixels
UI_SCROLL_AMOUNT_PX = 200  # Amount to scroll in pixels
UI_SCROLL_WIDTH_RATIO = 0.3  # Ratio of container width for scrolling
UI_NUMERIC_INPUT_STEP = 0.1  # Step size for numeric inputs

# 3D Visualization Defaults
DEFAULT_CAMERA_POSITION = {'x': 1.5, 'y': 1.5, 'z': 1.5}  # Default 3D camera position

# Responsive Plot Scaling Constants for Desktop Environments
# Optimized for standard desktop resolutions: 1920x1080, 1440x900, 1366x768, 1280x1024
RESPONSIVE_PLOT_CONFIG = {
    'desktop_large': {     # 1920x1080+, 2560x1440+
        'height': '700px',  # Fixed height for consistent appearance
        'min_height': '450px',
        'max_height': '1550px',
        'breakpoint': 1920
    },
    'desktop_medium': {    # 1440x900, 1600x900, 1680x1050
        'height': '450px',  # Fixed height for consistent appearance
        'min_height': '400px',
        'max_height': '500px',
        'breakpoint': 1440
    },
    'desktop_small': {     # 1366x768, 1280x1024, 1280x800
        'height': '400px',  # Fixed height for consistent appearance
        'min_height': '350px',
        'max_height': '450px', 
        'breakpoint': 1280
    },
    'desktop_compact': {   # 1024x768, smaller desktop displays
        'height': '350px',  # Fixed height for consistent appearance
        'min_height': '300px',
        'max_height': '400px',
        'breakpoint': 1024
    }
}

# Plot Type Specific Adjustments
PLOT_TYPE_MODIFIERS = {
    'scatter_3d': 1.0,        # Standard height
    'volume_mesh': 1.1,       # Slightly taller for complex 3D data
    'toolpath_3d': 1.0,       # Standard height 
    'time_series_2d': 0.8,    # Shorter for 2D plots
    'gcode_viz': 1.0,         # Standard height
    'custom_3d': 1.0          # Standard height
}

# Plotly Visualization Constants
DEFAULT_MARKER_SIZE = 2
DEFAULT_LINE_WIDTH = 4
DEFAULT_COLORSCALE = 'Viridis'
DEFAULT_FONT_SIZE = 16

# Data Table Display
MAX_TABLE_ROWS = 1000  # Maximum rows to display in data table
TABLE_PAGE_SIZE = 50  # Rows per page in data table

# Cache Configuration
CACHE_TTL_SECONDS = 300  # Cache time-to-live (5 minutes)
MAX_CACHE_SIZE_MB = 100  # Maximum cache size in memory

# Performance Optimization
CHUNK_SIZE = 10000  # Rows to process at once for large datasets
MESH_LOD_HIGH = 30  # High quality mesh angle step
MESH_LOD_MEDIUM = 45  # Medium quality mesh angle step
MESH_LOD_LOW = 60  # Low quality mesh angle step

# Column Name Mappings (commonly used)
POSITION_COLUMNS = ['XPos', 'YPos', 'ZPos']
VELOCITY_COLUMNS = ['FeedVel', 'PathVel']
TEMPERATURE_COLUMNS = ['ToolTemp', 'SubstrateTemp']
FORCE_COLUMNS = ['ForceZ', 'ForceX', 'ForceY']
SPINDLE_COLUMNS = ['SpinVel', 'SpinTrq', 'SpinPwr']
TIME_COLUMNS = ['Time', 'TimeInSeconds']

# Default Column Selections
DEFAULT_X_AXIS = 'XPos'
DEFAULT_Y_AXIS = 'YPos'
DEFAULT_Z_AXIS = 'ZPos'
DEFAULT_COLOR_COLUMN = 'ToolTemp'
DEFAULT_FILTER_COLUMN = 'ZPos'

# G-code Processing Constants
GCODE_FEED_ON_CMD = 'M34'  # Material feed on
GCODE_FEED_OFF_CMD = 'M35'  # Material feed off
GCODE_RAPID_MOVE = 'G0'  # Rapid positioning
GCODE_LINEAR_MOVE = 'G1'  # Linear interpolation
GCODE_COMMENT_CHARS = ['(', ';']  # Comment indicators

# Security Configuration
MAX_GCODE_WORD_LENGTH = 20  # Reasonable max length for a G-code word
MAX_CONFIG_LIST_LENGTH = 50  # Maximum length for configuration list values
SAFE_CONFIG_KEYS = {
    'default_theme', 'plotly_template', 'graph_1_options', 
    'graph_2_options', 'plot_2d_y_options', 'plot_2d_color_options',
    'feedstock_type', 'feedstock_dimension_inches'
}

# Logging Configuration Constants
LOG_FILE_MAX_BYTES = 10 * 1024 * 1024  # 10MB maximum log file size
ERROR_LOG_FILE_MAX_BYTES = 5 * 1024 * 1024  # 5MB maximum error log file size
LOG_BACKUP_COUNT = 10  # Number of backup log files to retain

# Error Messages
ERROR_NO_FILE = "Please upload a file to begin."
ERROR_INVALID_FILE = "Error: Please upload a valid CSV or G-code file."
ERROR_NO_DATA = "No data in selected range."
ERROR_COLUMN_NOT_FOUND = "Error: Column '{}' not found in file."
ERROR_MESH_GENERATION = "Could not generate mesh from the data."
ERROR_NO_ACTIVE_DATA = "No active printing data found (FeedVel > 0)."

# Success Messages
SUCCESS_FILE_LOADED = "File loaded successfully."
SUCCESS_CONFIG_SAVED = "Settings saved successfully!"
SUCCESS_UNITS_CONVERTED = "Imperial units detected and converted to metric."