# Enhanced UI Quick Reference

## Component Creation

### Enhanced Tabs
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

### Control Panel
```python
from src.meld_visualizer.core import layout

panel = layout.create_control_panel(
    title="Settings",
    controls=[...],
    collapsible=True,
    initial_collapsed=False
)
```

## Callback Patterns

### Show Toast Notification
```python
@callback(
    Output('toast-trigger-store', 'data'),
    Input('button', 'n_clicks'),
    State('toast-trigger-store', 'data')
)
def show_toast(n_clicks, trigger):
    if not n_clicks:
        raise PreventUpdate
    # ... logic to create toast ...
    return trigger + 1
```

### Loading State
```python
@callback(
    Output('loading-state-store', 'data'),
    Input('process-btn', 'n_clicks')
)
def process_with_loading(n_clicks):
    if not n_clicks:
        raise PreventUpdate
    yield {'show': True, 'message': 'Processing...'}
    # ... do work ...
    yield {'show': False, 'message': ''}
```

## CSS Classes

- `.enhanced-tabs-container`: The main container for the enhanced tabs.
- `.enhanced-control-panel`: The main container for a control panel.
- `.toast`: A toast notification.
- `.loading-overlay`: The loading overlay.

## File Locations

- **UI Layout:** `src/meld_visualizer/core/layout.py`
- **Callbacks:** `src/meld_visualizer/callbacks/`
- **CSS:** `src/meld_visualizer/static/css/enhanced-desktop-ui.css`
- **JavaScript:** `src/meld_visualizer/static/js/enhanced-ui.js`
