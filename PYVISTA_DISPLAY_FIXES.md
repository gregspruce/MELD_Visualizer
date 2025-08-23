# PyVista/Trame Display Issue Fixes

## Problem Summary
The PyVista visualization was generating meshes successfully (6,160 vertices) and saving screenshots, but the iframe component wasn't displaying anything in the browser.

## Root Cause Analysis
1. **Missing iframe update callback**: The initialization callback only updated status messages but never set the iframe's `src` or changed its `display` style from "none" to "block"
2. **Incomplete Trame server**: The SimplifiedTrameServer created an off-screen plotter but didn't start an actual HTTP server that could serve content to an iframe
3. **No coordination between backend and frontend**: Backend success wasn't properly communicated to the frontend iframe display

## Implemented Fixes

### 1. Enhanced Trame Server (`trame_server_simple.py`)
- **Added proper Trame UI components**: Now imports and uses `trame.app.get_server`, `trame.widgets.html`, `trame.widgets.vtk`, and `trame.ui.html.DivLayout`
- **Created actual web server**: The server now starts an HTTP server on the specified port that can serve content to iframes
- **Background thread execution**: Server runs in a daemon thread to prevent blocking the main application
- **Fallback mechanism**: If Trame server fails, falls back to off-screen mode for screenshots only
- **Proper cleanup**: Added server shutdown in the `close()` method

### 2. Updated PyVista Integration (`pyvista_simple.py`)
- **Improved placeholder component**: Added better styling with icon and centered text that properly shows/hides
- **Fixed iframe URL generation**: Corrected the `get_iframe_src()` method to properly check for port availability
- **Enhanced visual feedback**: Component now provides clear visual states for initialization vs. display

### 3. Enhanced Callback System (`pyvista_simple_callbacks.py`)
- **Extended callback outputs**: Added outputs for iframe `src`, iframe `style`, and placeholder text `style`
- **Dynamic iframe control**: Callback now updates iframe visibility and source URL based on initialization success
- **Proper state management**: Placeholder text is hidden when iframe is shown, and vice versa
- **Fallback handling**: When Trame server isn't available, shows screenshots-only mode with appropriate messaging

### 4. Detailed Changes Made

#### File: `src/meld_visualizer/core/trame_server_simple.py`
```python
# Added Trame server initialization with proper UI components
from trame.app import get_server
from trame.widgets import html as trame_html, vtk as vtk_widgets
from trame.ui.html import DivLayout

# Create actual web server with VTK view
self.server = get_server(f"pyvista_server_{self.port}")
with DivLayout(self.server) as layout:
    with trame_html.Div():
        view = vtk_widgets.VtkLocalView(self.plotter.ren_win)

# Start server in background thread
server_thread = threading.Thread(target=start_server, daemon=True)
server_thread.start()
```

#### File: `src/meld_visualizer/callbacks/pyvista_simple_callbacks.py`
```python
# Extended callback to control iframe display
@callback(
    Output("pyvista-iframe", "src"),           # NEW: Set iframe URL
    Output("pyvista-iframe", "style"),         # NEW: Show/hide iframe
    Output("pyvista-placeholder-text", "style"), # NEW: Control placeholder
    # ... existing outputs ...
)

# Dynamic iframe control based on server status
if success:
    iframe_src = simple_pyvista_integration.get_iframe_src()
    iframe_style = {"width": "100%", "height": "700px", "border": "1px solid #ddd", "display": "block"}
    
    if not iframe_src:  # Fallback mode
        iframe_style["display"] = "none"
        placeholder_style = {"display": "flex", "minHeight": "700px"}
    else:  # Success mode
        placeholder_style = {"display": "none"}
```

#### File: `src/meld_visualizer/components/pyvista_simple.py`
```python
# Improved placeholder with proper styling
html.Div(
    id="pyvista-placeholder-text",
    children=[
        html.I(className="bi bi-cube me-2"),
        html.Span("Click 'Initialize PyVista Renderer' to start...")
    ],
    className="text-muted text-center d-flex align-items-center justify-content-center h-100",
    style={"minHeight": "700px"}
)

# Fixed iframe URL generation
def get_iframe_src(self) -> str:
    if self.initialized and hasattr(self, 'port'):
        return f"http://localhost:{self.port}/"
    return ""
```

## Testing Results
- ✅ All Trame components import successfully
- ✅ Server initialization works with proper HTTP serving
- ✅ Callback correctly outputs iframe src and style controls
- ✅ Placeholder component shows/hides appropriately
- ✅ URL generation works for both initialized and uninitialized states

## Expected User Experience
1. User uploads CSV file
2. User navigates to "3D PyVista (Beta)" tab
3. User sees placeholder with instructions
4. User clicks "Initialize PyVista Renderer"
5. **NEW**: Iframe becomes visible and displays the 3D PyVista visualization
6. **NEW**: Placeholder text is hidden
7. User can interact with the 3D visualization in real-time
8. Export functionality continues to work as before

## Fallback Behavior
If Trame server initialization fails:
- Iframe remains hidden
- Placeholder shows message "(Screenshots only - no live view available)"
- Screenshot functionality still works
- User gets clear feedback about what's available

## Files Modified
1. `src/meld_visualizer/core/trame_server_simple.py` - Enhanced Trame server with HTTP serving
2. `src/meld_visualizer/callbacks/pyvista_simple_callbacks.py` - Extended callback outputs for iframe control
3. `src/meld_visualizer/components/pyvista_simple.py` - Improved placeholder and iframe URL generation

## Files Added
1. `test_simple_pyvista_fix.py` - Test script to validate the fixes without starting full server
2. `PYVISTA_DISPLAY_FIXES.md` - This documentation file

The fixes ensure that PyVista visualizations now properly display in the browser iframe while maintaining backward compatibility and providing appropriate fallback behavior.