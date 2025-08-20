# MELD Visualizer Architecture Documentation

## System Architecture

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[Dash UI Components]
        Layout[layout.py]
        Assets[Static Assets]
        EUI[Enhanced UI Components]
        EUJS[enhanced-ui.js]
        EUCSS[enhanced-desktop-ui.css]
    end
    
    subgraph "Controller Layer"
        CB[src/meld_visualizer/callbacks/]
        DC[data_callbacks.py]
        GC[graph_callbacks.py]
        VC[visualization_callbacks.py]
        FC[filter_callbacks.py]
        CC[config_callbacks.py]
        EUC[enhanced_ui_callbacks.py]
    end
    
    subgraph "Service Layer"
        DS[src/meld_visualizer/services/data_service.py]
        CS[src/meld_visualizer/services/cache_service.py]
        FS[src/meld_visualizer/services/file_service.py]
    end
    
    subgraph "Data Processing Layer"
        DP[src/meld_visualizer/core/data_processing.py]
        SU[src/meld_visualizer/utils/security_utils.py]
        Const[src/meld_visualizer/constants.py]
    end
    
    subgraph "Storage Layer"
        Config[config/config.json]
        Cache[In-Memory Cache]
        Logs[reports/logs]
    end
    
    UI --> CB
    EUI --> Layout
    EUJS --> EUI
    EUCSS --> EUI
    Layout --> UI
    CB --> DC
    CB --> GC
    CB --> VC
    CB --> FC
    CB --> CC
    CB --> EUC
    EUC --> EUI
    
    DC --> DS
    GC --> DS
    VC --> DS
    FC --> DS
    
    DS --> CS
    DS --> FS
    DS --> DP
    
    DP --> SU
    DP --> Const
    
    CS --> Cache
    CC --> Config
    DP --> Logs
```

## Data Flow Diagram

```mermaid
flowchart LR
    subgraph "File Upload"
        CSV[CSV File]
        GCode[G-code File]
    end
    
    subgraph "Processing"
        Val[Validation]
        Parse[Parsing]
        Conv[Unit Conversion]
        FeedGeom[Feedstock Geometry]
        San[Sanitization]
    end
    
    subgraph "Caching"
        CacheCheck{Cache Hit?}
        Store[Store in Cache]
        Retrieve[Retrieve from Cache]
    end
    
    subgraph "Visualization"
        Scatter[3D Scatter]
        Mesh[3D Mesh]
        Line[3D Line]
        Plot2D[2D Plots]
    end
    
    CSV --> Val
    GCode --> Val
    Val --> Parse
    Parse --> Conv
    Conv --> FeedGeom
    FeedGeom --> San
    San --> CacheCheck
    
    CacheCheck -->|No| Store
    CacheCheck -->|Yes| Retrieve
    
    Store --> Scatter
    Store --> Mesh
    Store --> Line
    Store --> Plot2D
    
    Retrieve --> Scatter
    Retrieve --> Mesh
    Retrieve --> Line
    Retrieve --> Plot2D
```

## Component Interaction Diagram

```mermaid
sequenceDiagram
    participant User
    participant UI
    participant Callback
    participant Service
    participant Cache
    participant DataProc
    
    User->>UI: Upload File
    UI->>Callback: Trigger upload_callback
    Callback->>DataProc: Validate file
    DataProc-->>Callback: Validation result
    
    alt Valid File
        Callback->>DataProc: Parse contents
        DataProc-->>Callback: DataFrame
        Callback->>Service: Process data
        Service->>Cache: Check cache
        
        alt Cache Miss
            Cache-->>Service: Not found
            Service->>DataProc: Generate statistics
            DataProc-->>Service: Statistics
            Service->>Cache: Store result
        else Cache Hit
            Cache-->>Service: Cached data
        end
        
        Service-->>Callback: Processed data
        Callback->>UI: Update visualization
        UI-->>User: Display result
    else Invalid File
        Callback->>UI: Show error
        UI-->>User: Display error message
    end
```

## Module Dependencies

```mermaid
graph LR
    subgraph "Core Modules"
        App[src/meld_visualizer/app.py]
        Layout[src/meld_visualizer/core/layout.py]
        Callbacks[src/meld_visualizer/callbacks/]
    end
    
    subgraph "Data Layer"
        DataProc[src/meld_visualizer/core/data_processing.py]
        Security[src/meld_visualizer/utils/security_utils.py]
        Constants[src/meld_visualizer/constants.py]
    end
    
    subgraph "Service Layer"
        Services[src/meld_visualizer/services/]
        Cache[cache_service.py]
        Data[data_service.py]
        File[file_service.py]
    end
    
    subgraph "Configuration"
        Config[src/meld_visualizer/config.py]
        Logging[src/meld_visualizer/utils/logging_config.py]
    end
    
    App --> Layout
    App --> Callbacks
    App --> Config
    
    Callbacks --> Services
    Callbacks --> DataProc
    Callbacks --> Security
    
    Services --> Cache
    Services --> Data
    Services --> File
    
    DataProc --> Constants
    DataProc --> Security
    
    Security --> Constants
    Security --> Logging
    
    Config --> Constants
```

## Security Architecture

```mermaid
flowchart TB
    subgraph "Input Layer"
        FileIn[File Input]
        ConfigIn[Config Input]
        UserIn[User Input]
    end
    
    subgraph "Validation Layer"
        FileVal[File Validator]
        InputVal[Input Validator]
        ConfigVal[Config Validator]
    end
    
    subgraph "Sanitization"
        PathSan[Path Sanitization]
        DataSan[Data Sanitization]
        GCodeSan[G-code Sanitization]
    end
    
    subgraph "Security Checks"
        SizeCheck[Size Limits]
        ExtCheck[Extension Check]
        ContentCheck[Content Inspection]
        ReDoSCheck[ReDoS Protection]
    end
    
    subgraph "Error Handling"
        ErrorLog[Error Logging]
        UserMsg[User Messages]
        Fallback[Fallback Actions]
    end
    
    FileIn --> FileVal
    ConfigIn --> ConfigVal
    UserIn --> InputVal
    
    FileVal --> SizeCheck
    FileVal --> ExtCheck
    FileVal --> ContentCheck
    
    InputVal --> DataSan
    InputVal --> ReDoSCheck
    
    ConfigVal --> PathSan
    
    SizeCheck --> ErrorLog
    ExtCheck --> ErrorLog
    ContentCheck --> ErrorLog
    ReDoSCheck --> ErrorLog
    
    ErrorLog --> UserMsg
    UserMsg --> Fallback
```

## Caching Strategy

```mermaid
graph TB
    subgraph "Cache Layers"
        L1[L1: DataFrame Cache]
        L2[L2: Statistics Cache]
        L3[L3: Plot Cache]
    end
    
    subgraph "Eviction Policies"
        LRU[LRU Eviction]
        TTL[TTL Expiration]
        Size[Size Limits]
    end
    
    subgraph "Cache Operations"
        Get[Get Operation]
        Set[Set Operation]
        Clear[Clear Operation]
    end
    
    Get --> L1
    L1 -->|Miss| L2
    L2 -->|Miss| L3
    L3 -->|Miss| Generate[Generate New]
    
    Generate --> Set
    Set --> L1
    Set --> LRU
    Set --> TTL
    Set --> Size
    
    LRU --> Clear
    TTL --> Clear
    Size --> Clear
```

## Performance Optimization Flow

```mermaid
flowchart LR
    subgraph "Data Input"
        Small[Small Dataset<br/>< 1MB]
        Medium[Medium Dataset<br/>1-10MB]
        Large[Large Dataset<br/>> 10MB]
    end
    
    subgraph "Processing Strategy"
        Direct[Direct Processing]
        Cached[Cached Processing]
        Chunked[Chunked Processing]
    end
    
    subgraph "Visualization"
        Full[Full Resolution]
        Sampled[Sampled Data]
        LOD[Level of Detail]
    end
    
    Small --> Direct
    Medium --> Cached
    Large --> Chunked
    
    Direct --> Full
    Cached --> Full
    Chunked --> Sampled
    
    Sampled --> LOD
```

## Testing Architecture

```mermaid
graph TB
    subgraph "Test Types"
        Unit[tests/unit/]
        Integration[tests/integration/]
        E2E[tests/e2e/]
        Perf[Performance Tests]
        Sec[Security Tests]
    end
    
    subgraph "Test Coverage"
        DataTests[tests/unit/test_data_processing.py]
        ServiceTests[tests/unit/test_services.py]
        CallbackTests[tests/integration/test_integration.py]
        ValidationTests[tests/unit/test_validation.py]
    end
    
    subgraph "Test Infrastructure"
        Pytest[Pytest Framework + pyproject.toml]
        Coverage[Coverage.py → reports/]
        Selenium[Selenium WebDriver]
        Fixtures[tests/conftest.py]
    end
    
    Unit --> DataTests
    Unit --> ServiceTests
    Integration --> CallbackTests
    Sec --> ValidationTests
    
    DataTests --> Pytest
    ServiceTests --> Pytest
    CallbackTests --> Pytest
    ValidationTests --> Pytest
    
    Pytest --> Coverage
    E2E --> Selenium
    All[All Tests] --> Fixtures
```

## Deployment Architecture

```mermaid
graph TB
    subgraph "Development"
        Dev[pip install -e .]
        Debug[python -m meld_visualizer]
        HotReload[Hot Reloading]
        Quality[black/flake8/mypy]
    end
    
    subgraph "Testing"
        CI[GitHub Actions]
        TestEnv[pytest + coverage]
        Coverage[reports/htmlcov/]
    end
    
    subgraph "Production"
        Build[python -m build + PyInstaller]
        Exec[meld-visualizer command]
        Deploy[pip install meld-visualizer]
    end
    
    Dev --> Debug
    Debug --> HotReload
    HotReload --> CI
    
    CI --> TestEnv
    TestEnv --> Coverage
    Coverage --> Build
    
    Build --> Exec
    Exec --> Deploy
```

## Feedstock Geometry and Volume Calculation Architecture

### Corrected Volume Mesh Generation

The MELD Visualizer has been updated with mathematically correct feedstock geometry assumptions:

```mermaid
graph TB
    subgraph "Feedstock Geometry"
        SqRod[0.5" × 0.5" Square Rod]
        SqDim[12.7mm × 12.7mm]
        SqArea[161.3 mm² Cross-Section]
    end
    
    subgraph "Previous (Incorrect) Assumption"
        CircWire[Circular Wire Assumption]
        CircArea[~126.7 mm² Area]
        Error[21.5% Volume Underestimation]
    end
    
    subgraph "Volume Calculation Process"
        FeedVel[Feed Velocity]
        PathVel[Path Velocity]
        ConsMass[Conservation of Mass]
        BeadArea[Bead Cross-Section Area]
        VolMesh[3D Volume Mesh]
    end
    
    SqRod --> SqDim
    SqDim --> SqArea
    
    FeedVel --> ConsMass
    PathVel --> ConsMass
    SqArea --> ConsMass
    ConsMass --> BeadArea
    BeadArea --> VolMesh
    
    CircWire --> CircArea
    CircArea --> Error
```

### Mathematical Corrections

#### Volume Conservation Principle
```
Bead Area = (Feed Velocity × Feedstock Area) / Path Velocity

Where:
- Feedstock Area = 161.3 mm² (0.5" × 0.5" square rod)
- Previous incorrect area = 126.7 mm² (circular assumption)
- Improvement = 27% more accurate volume calculations
```

### Configuration Architecture

```mermaid
graph LR
    subgraph "Configuration System"
        Config[config.json]
        FeedType[feedstock_type]
        FeedDim[feedstock_dimension_inches]
    end
    
    subgraph "Feedstock Types"
        Square["square" (default)]
        Circular["circular" (legacy)]
    end
    
    subgraph "Calculations"
        SqCalc[Square: side²]
        CircCalc[Circular: π × (d/2)²]
    end
    
    Config --> FeedType
    Config --> FeedDim
    
    FeedType --> Square
    FeedType --> Circular
    
    Square --> SqCalc
    Circular --> CircCalc
```

### Data Processing Pipeline Updates

The volume mesh generation pipeline now includes:

1. **Feedstock Configuration Loading**: Reads geometry from config.json
2. **Type-Specific Area Calculation**: Square vs circular geometry
3. **Volume Conservation**: Mathematically correct bead area calculations
4. **Mesh Generation**: Accurate 3D volume representations
5. **Backward Compatibility**: Legacy wire variables maintained

### Performance and Accuracy Impact

- **Volume Accuracy**: 27% improvement in volume calculations
- **Material Flow**: Correct representation of feedstock consumption
- **Process Analysis**: More accurate process parameter relationships
- **Backward Compatibility**: Existing configurations continue to work