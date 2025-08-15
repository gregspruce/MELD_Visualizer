# MELD Visualizer Architecture Documentation

## System Architecture

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[Dash UI Components]
        Layout[layout.py]
        Assets[Static Assets]
    end
    
    subgraph "Controller Layer"
        CB[Callbacks Module]
        DC[Data Callbacks]
        GC[Graph Callbacks]
        VC[Visualization Callbacks]
        FC[Filter Callbacks]
        CC[Config Callbacks]
    end
    
    subgraph "Service Layer"
        DS[Data Service]
        CS[Cache Service]
        FS[File Service]
    end
    
    subgraph "Data Processing Layer"
        DP[data_processing.py]
        SU[security_utils.py]
        Const[constants.py]
    end
    
    subgraph "Storage Layer"
        Config[config.json]
        Cache[In-Memory Cache]
        Logs[Log Files]
    end
    
    UI --> CB
    CB --> DC
    CB --> GC
    CB --> VC
    CB --> FC
    CB --> CC
    
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
    Conv --> San
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
        App[app.py]
        Layout[layout.py]
        Callbacks[callbacks/]
    end
    
    subgraph "Data Layer"
        DataProc[data_processing.py]
        Security[security_utils.py]
        Constants[constants.py]
    end
    
    subgraph "Service Layer"
        Services[services/]
        Cache[cache_service.py]
        Data[data_service.py]
        File[file_service.py]
    end
    
    subgraph "Configuration"
        Config[config.py]
        Logging[logging_config.py]
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
        Unit[Unit Tests]
        Integration[Integration Tests]
        E2E[E2E Tests]
        Perf[Performance Tests]
        Sec[Security Tests]
    end
    
    subgraph "Test Coverage"
        DataTests[Data Processing]
        ServiceTests[Service Layer]
        CallbackTests[Callbacks]
        ValidationTests[Validation]
    end
    
    subgraph "Test Infrastructure"
        Pytest[Pytest Framework]
        Coverage[Coverage.py]
        Selenium[Selenium WebDriver]
        Fixtures[Test Fixtures]
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
        Dev[Local Development]
        Debug[Debug Mode]
        HotReload[Hot Reloading]
    end
    
    subgraph "Testing"
        CI[CI Pipeline]
        TestEnv[Test Environment]
        Coverage[Coverage Reports]
    end
    
    subgraph "Production"
        Build[PyInstaller Build]
        Exec[Standalone Executable]
        Deploy[Deployment]
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