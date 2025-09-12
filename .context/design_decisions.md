# MELD Visualizer - Design Decisions

## Architectural Choices and Rationale

### Package Structure Decision
**Choice**: Professional Python package with `src/meld_visualizer/` layout
**Rationale**:
- Prevents namespace conflicts
- Enables proper module imports
- Supports pip installation
- Follows Python packaging standards

### MVC-like Architecture
**Choice**: Separation of concerns with distinct layers
**Components**:
- **View Layer** (`layout.py`): UI components and structure
- **Controller Layer** (`callbacks/`): Interactive logic split into modules
  - `main_callbacks.py`: Core application callbacks
  - `filter_callbacks.py`: Data filtering logic
  - `config_callbacks.py`: Settings management
  - `plot_callbacks.py`: Visualization updates
- **Model Layer** (`data_processing.py`): Data operations
**Rationale**: Maintainability, testability, clear separation of concerns

### Hot-Reload System Architecture
**Choice**: Dynamic configuration without app restart
**Implementation**:
- Clientside JavaScript for instant CSS updates
- Runtime state management with global APP_CONFIG
- Allow_duplicate callbacks for safe updates
- Theme injection components in layout
**Rationale**: Enhanced developer and user experience

### Volume Calculation Method
**Choice**: Square rod geometry (w² = 161.29mm²)
**Previous Error**: Circular wire assumption (π × (d/2)² = 126.7mm²)
**Rationale**: MELD process uses square feedstock rods, not circular wire
**Impact**: 27% more accurate volume representations

## API Design Patterns

### Dash Callback Pattern
```python
@callback(
    Output('component-id', 'property'),
    Input('trigger-id', 'property'),
    State('state-id', 'property'),
    allow_duplicate=True  # For hot-reload callbacks
)
def update_component(trigger_value, state_value):
    return new_value
```

### Pattern Matching IDs
```python
# Component ID structure
id = {'type': 'graph-type', 'index': 'scatter-plot'}

# Callback matching
Output({'type': 'graph-type', 'index': ALL}, 'figure')
```

### Error Handling Pattern
```python
def process_data(file_path):
    try:
        data = parse_file(file_path)
        return data, None, False  # (data, error_msg, conversion_flag)
    except Exception as e:
        return None, str(e), False
```

## Configuration Management

### Config.json Structure
```json
{
  "theme": {
    "bootstrap": "cosmo",
    "plotly": "plotly_white"
  },
  "graph_options": {
    "show_grid": true,
    "show_legend": true,
    "z_stretch_factor": 5.0
  },
  "column_mappings": {
    "time": ["TIME", "Time", "Timestamp"],
    "temperature": ["TEMP", "Temperature", "Melt_Temp_C"]
  }
}
```

### Hot-Reload Configuration Flow
1. User changes setting in UI
2. Callback updates config.json
3. Hot-reload system detects change
4. Runtime APP_CONFIG updated
5. Clientside callback updates theme CSS
6. Components re-render with new config

## Security Implementations

### Input Validation
```python
class InputValidator:
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        # Remove path traversal attempts
        return os.path.basename(filename)

    @staticmethod
    def validate_upload_size(contents: str, max_size_mb: int = 100):
        # Check file size before processing
        size = len(contents) * 0.75 / 1048576  # Base64 to MB
        if size > max_size_mb:
            raise ValueError(f"File too large: {size:.1f}MB")
```

### File Processing Security
- Sanitize all file paths
- Validate file extensions
- Size limits on uploads
- Memory-safe data processing
- No execution of uploaded code

## Performance Optimizations

### Caching Strategy
- Component-level caching for expensive operations
- Memoization of data processing functions
- State management to prevent redundant calculations

### Memory Management
- Streaming processing for large files
- Garbage collection hints after large operations
- Efficient numpy operations for mesh generation

### Hot-Reload Performance
- Clientside callbacks eliminate server round-trips
- CSS injection vs full page reload
- Selective component updates

## Testing Strategy Decisions

### Test Organization
```
tests/
├── unit/           # Isolated function tests
├── integration/    # Component interaction tests
├── e2e/           # Full user workflow tests
└── fixtures/      # Test data and mocks
```

### Test Markers
- `@pytest.mark.unit` - Fast, isolated tests
- `@pytest.mark.integration` - Component tests
- `@pytest.mark.e2e` - Browser automation tests

### Coverage Goals
- Unit: 90% coverage of data processing
- Integration: All callback interactions
- E2E: Critical user workflows
