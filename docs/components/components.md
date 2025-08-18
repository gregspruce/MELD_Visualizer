# MELD Visualizer Component Documentation

## Technology Stack

### Core Framework
- **Dash**: Interactive web application framework (v2.14+)
- **Plotly**: 3D visualization library (v5.18+)
- **Pandas**: Data manipulation and analysis (v2.0+)
- **NumPy**: Numerical computing (v1.24+)

### UI Components
- **Dash Bootstrap Components**: Responsive UI components (v1.5+)
- **Dash Core Components**: Interactive controls
- **Dash HTML Components**: HTML elements

### Backend Services
- **Python**: Core language (v3.8+)
- **JSON**: Configuration management
- **Base64**: File encoding/decoding
- **IO**: File operations

### Security & Validation
- **Custom Security Module**: Input validation and sanitization
- **Path Validation**: Directory traversal protection
- **Content Inspection**: Malicious code detection

### Testing Framework
- **Pytest**: Testing framework
- **Selenium**: E2E testing
- **Coverage.py**: Code coverage
- **Unittest.mock**: Mocking framework

## Component Breakdown

### 1. Main Application (src/meld_visualizer/app.py)
**Purpose**: Entry point and application initialization

**Key Functions**:
- `create_app()`: Creates and configures Dash application
- `register_callbacks()`: Registers all callback modules
- `load_initial_config()`: Loads startup configuration
- `main()`: Entry point for command-line execution

**Dependencies**:
- Dash framework
- `meld_visualizer.core.layout`
- `meld_visualizer.callbacks.*`
- `meld_visualizer.config`

**Import Examples**:
```python
from meld_visualizer.core.layout import create_main_layout
from meld_visualizer.callbacks import register_all_callbacks
from meld_visualizer.config import load_config
```

**Configuration**:
```python
DEBUG = os.getenv("DEBUG", "0") == "1"
HOST = "127.0.0.1"
PORT = 8050
```

### 2. Layout Module (src/meld_visualizer/core/layout.py)
**Purpose**: UI structure and component definitions

**Components**:
- **Header**: Application title and branding
- **Upload Section**: File upload interface
- **Visualization Tabs**: 3D plots, 2D graphs, mesh views
- **Settings Tab**: Configuration interface
- **Data Tab**: Data display and filtering

**Key Features**:
- Responsive design with Bootstrap
- Tab-based navigation
- Interactive controls (sliders, dropdowns, inputs)
- Real-time updates

### 3. Data Processing (src/meld_visualizer/core/data_processing.py)
**Purpose**: File parsing and data transformation

**Import Path**:
```python
from meld_visualizer.core.data_processing import (
    parse_contents,
    parse_csv_data,
    parse_gcode,
    generate_volume_mesh,
    check_and_convert_units
)
```

**Core Functions**:
```python
def parse_contents(contents, filename):
    """Parse uploaded file contents"""
    
def parse_csv_data(decoded):
    """Parse CSV data with validation"""
    
def parse_gcode(contents):
    """Parse G-code files"""
    
def generate_volume_mesh(df, color_column):
    """Generate 3D mesh from data"""
    
def check_and_convert_units(df):
    """Convert imperial to metric units"""
```

**Features**:
- CSV and G-code parsing
- Automatic unit conversion
- Data validation
- Mesh generation algorithms
- Error handling

### 4. Callback Modules (src/meld_visualizer/callbacks/)

**Import Paths**:
```python
from meld_visualizer.callbacks.data_callbacks import register_data_callbacks
from meld_visualizer.callbacks.graph_callbacks import register_graph_callbacks
# etc.
```

#### Data Callbacks (src/meld_visualizer/callbacks/data_callbacks.py)
**Handles**: File uploads and data management
- File validation and parsing
- Data storage and retrieval
- Format conversion
- Error handling

#### Graph Callbacks (src/meld_visualizer/callbacks/graph_callbacks.py)
**Handles**: Main visualization updates
- 3D scatter plots
- Color mapping
- Axis configuration
- Plot updates

#### Visualization Callbacks (src/meld_visualizer/callbacks/visualization_callbacks.py)
**Handles**: Advanced visualizations
- 3D mesh generation
- Line plots
- Toolpath visualization
- Z-axis scaling

#### Filter Callbacks (src/meld_visualizer/callbacks/filter_callbacks.py)
**Handles**: Data filtering controls
- Range sliders
- Custom filters
- Data subsetting
- Filter synchronization

#### Config Callbacks (src/meld_visualizer/callbacks/config_callbacks.py)
**Handles**: Settings management
- Theme selection
- Plot options
- Save/load configuration
- UI customization

### 5. Service Layer (src/meld_visualizer/services/)

**Import Paths**:
```python
from meld_visualizer.services.cache_service import CacheService
from meld_visualizer.services.data_service import DataService  
from meld_visualizer.services.file_service import FileService
```

#### Cache Service (src/meld_visualizer/services/cache_service.py)
**Purpose**: Performance optimization through caching

**Features**:
- LRU eviction policy
- TTL-based expiration
- Size-based limits
- DataFrame caching
- Statistics caching

**API**:
```python
class CacheService:
    def get(key)
    def set(key, value)
    def clear()
    def get_stats()
    def cache_dataframe(df, key)
```

#### Data Service (src/meld_visualizer/services/data_service.py)
**Purpose**: Data operations and business logic

**Operations**:
- Statistical analysis
- Data filtering
- Column validation
- Data transformation
- Cache integration

#### File Service (src/meld_visualizer/services/file_service.py)
**Purpose**: File operations and management

**Functions**:
- File validation
- Path sanitization
- Extension checking
- Size verification

### 6. Security Module (src/meld_visualizer/utils/security_utils.py)

**Import Path**:
```python
from meld_visualizer.utils.security_utils import (
    validate_file_path,
    sanitize_input,
    check_file_content
)
```
**Purpose**: Input validation and security

**Components**:

#### FileValidator
- Path traversal detection
- Extension validation
- Size limits
- Content inspection

#### InputValidator
- Numeric sanitization
- Column name validation
- G-code line sanitization
- Pattern matching

#### ConfigurationManager
- Safe configuration saving
- Key validation
- Value sanitization

#### ErrorHandler
- Safe error messages
- Logging integration
- User-friendly errors

### 7. Configuration (src/meld_visualizer/config.py)

**Import Path**:
```python
from meld_visualizer.config import (
    load_config,
    get_theme_config,
    save_config
)
```

**Configuration File**: `config/config.json`
**Purpose**: Application configuration management

**Features**:
- JSON-based configuration
- Theme management
- Default settings
- Runtime updates

**Configuration Structure**:
```json
{
    "default_theme": "Cerulean",
    "plotly_template": "plotly_white",
    "graph_1_options": ["XPos", "YPos", "ZPos"],
    "graph_2_options": ["ToolTemp", "FeedVel"],
    "plot_2d_y_options": ["FeedVel", "PathVel"],
    "plot_2d_color_options": ["ToolTemp", "Time"]
}
```

### 8. Constants (constants.py)
**Purpose**: Centralized constant definitions

**Categories**:
- File limits
- Conversion factors
- UI constants
- Validation rules
- Performance thresholds

### 9. Logging Configuration (src/meld_visualizer/utils/logging_config.py)

**Import Path**:
```python
from meld_visualizer.utils.logging_config import setup_logging
```
**Purpose**: Structured logging system

**Loggers**:
- **AppLogger**: General application logging
- **PerformanceLogger**: Performance metrics
- **SecurityLogger**: Security events
- **DataLogger**: Data operations

**Features**:
- Colored console output
- Rotating file handlers
- Multiple log levels
- Structured formatting

## Component Interactions

### Data Flow
1. **Upload**: User uploads file through UI
2. **Validation**: Security module validates input
3. **Processing**: Data processing module parses file
4. **Caching**: Service layer caches results
5. **Visualization**: Callbacks generate plots
6. **Display**: UI renders visualizations

### Event Flow
1. **User Action**: Click, upload, or input
2. **Callback Trigger**: Dash callback activated
3. **Service Call**: Business logic executed
4. **Cache Check**: Results retrieved or generated
5. **UI Update**: Component refreshed

### Error Flow
1. **Error Occurs**: Exception raised
2. **Error Handler**: Catches and logs error
3. **User Message**: Friendly message generated
4. **Fallback**: Safe state restored
5. **Recovery**: Application continues

## Performance Considerations

### Optimization Strategies
- **Caching**: Multi-level caching system
- **Lazy Loading**: Data loaded on demand
- **Chunking**: Large files processed in chunks
- **Sampling**: Data sampled for visualization
- **Memoization**: Results cached for reuse

### Bottlenecks
- Large file parsing
- Mesh generation
- Complex filtering
- Multiple simultaneous users

### Solutions
- Background processing
- Progressive rendering
- Optimized algorithms
- Resource pooling

## Security Considerations

### Input Validation
- All user inputs sanitized
- File uploads validated
- Path traversal prevented
- Size limits enforced

### Error Handling
- Sensitive data scrubbed from errors
- Safe error messages displayed
- Logging without exposing secrets
- Graceful degradation

### Configuration Security
- Whitelisted configuration keys
- Value type validation
- Path restrictions
- Size limitations