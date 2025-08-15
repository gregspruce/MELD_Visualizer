"""
Constants module for MELD Visualizer application.
Contains all magic numbers, thresholds, and configuration constants.
"""

# Unit Conversion Constants
INCH_TO_MM = 25.4
MM_TO_INCH = 1.0 / 25.4

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
WIRE_DIAMETER_MM = 0.5 * INCH_TO_MM  # Wire feed diameter

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

# Error Messages
ERROR_NO_FILE = "Please upload a file to begin."
ERROR_INVALID_FILE = "Error: Please upload a valid CSV or G-code file."
ERROR_NO_DATA = "No data in selected range."
ERROR_COLUMN_NOT_FOUND = "Error: Column '{}' not found in file."
ERROR_MESH_GENERATION = "Could not generate mesh from the data."
ERROR_NO_ACTIVE_DATA = "No active printing data found (FeedVel > 0)."

# Success Messages
SUCCESS_FILE_LOADED = "File loaded successfully."
SUCCESS_CONFIG_SAVED = "Settings saved. Please restart the application."
SUCCESS_UNITS_CONVERTED = "Imperial units detected and converted to metric."