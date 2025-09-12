# MELD Visualizer Project Context
*Last Updated: August 20, 2025*

## Project Overview

**MELD Visualizer**: 3D visualization platform for Manufacturing using Extreme Layer Deposition
- **Technology Stack**: Dash/Plotly web application with Python backend
- **Purpose**: Visualize and analyze MELD manufacturing process data
- **Key Features**:
  - 3D plots with interactive controls
  - Volume calculations with calibrated parameters
  - G-code visualization and processing
  - Responsive design with breakpoint system
  - Theme switching and configuration management

## Current State (August 2025)

### Completed Work
- **FIXED**: Resolved 79+ console callback conflicts through architectural overhaul
- **IMPLEMENTED**: Responsive plot scaling system for desktop (4-tier breakpoints)
- **CALIBRATED**: Volume calculations with width_multiplier=1.654 for accurate bead overlap
- **FUNCTIONAL**: All core features operational with standard Dash components

### Recent Activity
- **ATTEMPTED**: Enhanced UI system with tabs, control panels, and user feedback components
- **ROLLED BACK**: Enhanced UI due to incomplete integration (callbacks registered for non-existent layout components)
- **CURRENT STATUS**: Application fully functional with appropriate plot heights (350-500px range)

## Architecture & Design Decisions

### MVC-like Architecture
- `layout.py`: View layer with Dash components
- `callbacks/*`: Controller layer with modular callback organization
- `data_processing.py`: Model layer for business logic
- Service layer pattern for separating concerns

### Callback System Design
- **Registration Order**: data → config → filter → graph → visualization
- **Pattern Matching IDs**: `{'type': 'component-type', 'index': 'identifier'}`
- **Error Handling Pattern**: Returns tuple `(data, error_message, conversion_flag)`
- **Circular Dependency Prevention**: Removed range-slider from Output in filter_callbacks

### Configuration Management
- **Hot-reload System**:
  - Themes: Instant reload via Settings tab
  - Config: Requires restart for manual config.json edits
- **Theme Support**: PLOTLY_TEMPLATE from config applied to all plots

### Responsive Design
- **Desktop Breakpoints**: 4-tier system for plot scaling
- **Plot Heights**: Fixed pixels (350-500px) for consistency
- **Avoid**: Viewport-relative heights (vh units) cause display issues

## Code Patterns & Standards

### Import Convention
```python
from meld_visualizer.core import module_name
```

### Callback Structure
```python
@callback(
    Output('component-id', 'property'),
    Input('trigger-id', 'property'),
    State('state-id', 'property')
)
def callback_function(trigger_value, state_value):
    # Business logic
    return result
```

### Component Creation
```python
# Standard Dash components
dcc.Graph(id='plot-id', figure=fig)
dbc.Tabs(id='tabs-id', children=[...])
html.Div(id='container-id', children=[...])
```

### Geometry Constants
- **Square Feedstock**: 0.5" × 0.5" cross-section
- **Width Multiplier**: 1.654 (calibrated for bead overlap)

## Agent Coordination History

### Successful Patterns
1. **Callback Architecture Overhaul**: Eliminated circular dependencies
2. **Responsive Plot System**: Properly integrated with existing layout
3. **Modular Callback Organization**: Clear separation by domain

### Lessons Learned
1. **Component-Callback Integration**: Always ensure UI components exist in layout before registering callbacks
2. **Plot Heights**: Use fixed pixel values (350-500px) not viewport-relative units
3. **Progressive Enhancement**: Add features incrementally with full integration
4. **Backward Compatibility**: Maintain existing functionality when adding features

### Agent Roles
- **ui-ux-designer**: UI analysis and design proposals
- **Specialized agents**: Implementation of specific features
- **context-manager**: Project state and knowledge management

## Known Issues & Solutions

### Fixed Issues
- ✅ **Circular Dependencies**: Resolved by removing range-slider from Output
- ✅ **Plot Height Issues**: Changed from 75vh to 500px maximum
- ✅ **Callback Conflicts**: 79+ conflicts resolved through architecture overhaul

### Rolled Back Changes
- ⚠️ **Enhanced UI Components**: Callbacks without matching layout components
  - **Root Cause**: Components referenced in callbacks but not added to layout
  - **Solution**: Ensure complete integration before callback registration

### Working Features
- ✅ File upload and processing
- ✅ Theme switching via Settings tab
- ✅ All plot types (3D, volume, etc.)
- ✅ Data processing and filtering
- ✅ G-code visualization

## Future Roadmap

### Immediate Priorities
1. **Re-implement Enhanced UI**: With proper component-callback integration
2. **Component Verification**: Ensure all UI components exist before callback registration
3. **Maintain Plot Heights**: Keep current 350-500px range that works well

### Development Guidelines
1. **Progressive Enhancement**: Add features incrementally
2. **Integration Testing**: Verify component-callback pairs
3. **Backward Compatibility**: Don't break existing functionality
4. **User Experience**: Keep interface responsive and intuitive

### Potential Enhancements
- Enhanced control panels with better organization
- User feedback system for operations
- Advanced filtering options
- Performance optimizations for large datasets
- Additional visualization types

## Technical Specifications

### File Structure
```
meld_visualizer/
├── core/
│   ├── layout.py          # Main UI layout
│   ├── callbacks/         # Modular callback organization
│   │   ├── data_callbacks.py
│   │   ├── config_callbacks.py
│   │   ├── filter_callbacks.py
│   │   ├── graph_callbacks.py
│   │   └── visualization_callbacks.py
│   ├── data_processing.py # Business logic
│   └── config.py          # Configuration management
├── assets/               # CSS, JS, themes
└── config.json          # User configuration
```

### Key Dependencies
- Dash/Plotly for visualization
- Pandas/NumPy for data processing
- dash-bootstrap-components for UI
- Python 3.8+ for backend

## Testing & Validation

### Critical Test Points
1. Callback registration without errors
2. Plot rendering at appropriate heights
3. Theme switching functionality
4. File upload and processing
5. Volume calculations accuracy
6. Responsive design breakpoints

### Validation Criteria
- No console errors in browser
- Plots visible and interactive
- Data processing completes successfully
- UI responsive across screen sizes
- Configuration changes take effect

## Contact & Resources

- **Project**: MELD Visualizer
- **Domain**: Manufacturing visualization
- **Stack**: Python, Dash, Plotly
- **Status**: Production-ready with enhancement opportunities

---

*This context document serves as the single source of truth for project state and should be updated as significant changes occur.*
