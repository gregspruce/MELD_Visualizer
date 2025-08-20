# Enhanced UI Quick Reference

## Component Creation Cheat Sheet

### Enhanced Tabs
```python
tabs = EnhancedUIComponents.create_enhanced_tabs([
    {'id': 'tab1', 'label': 'Tab 1', 'content': content1},
    {'id': 'tab2', 'label': 'Tab 2', 'content': content2}
], active_tab='tab1')
```

### Control Panel
```python
panel = EnhancedUIComponents.create_control_panel(
    title="Settings",
    controls=[...],
    collapsible=True,
    initial_collapsed=False
)
```

### Toast Notification
```python
toast = UserFeedbackManager.create_toast_component(
    toast_type="success",  # success/error/warning/info
    title="Success!",
    message="Operation completed",
    duration=5000
)
```

### Progress Indicator
```python
progress = EnhancedUIComponents.create_progress_indicator(
    title="Processing",
    progress_id="my-progress",
    initial_value=0,
    max_value=100
)
```

### Upload Area
```python
upload = EnhancedUIComponents.create_enhanced_upload_area(
    upload_id='file-upload',
    message='Drop files here',
    accepted_types='.csv,.xlsx'
)
```

## Callback Patterns

### Show Toast on Success
```python
@callback(
    [Output('toast-trigger-store', 'data'),
     Output('ui-state-store', 'data')],
    Input('button', 'n_clicks'),
    [State('toast-trigger-store', 'data'),
     State('ui-state-store', 'data')]
)
def show_success(n_clicks, trigger, ui_state):
    if not n_clicks:
        raise PreventUpdate
    
    toast = UserFeedbackManager.create_toast_component(
        toast_type="success",
        title="Done!",
        message="Task completed"
    )
    ui_state['last_toast'] = toast
    
    return trigger + 1, ui_state
```

### Loading State Pattern
```python
@callback(
    Output('loading-state-store', 'data'),
    Input('process-btn', 'n_clicks')
)
def process_with_loading(n_clicks):
    if not n_clicks:
        raise PreventUpdate
    
    # Show loading
    yield {'show': True, 'message': 'Processing...'}
    
    # Do work
    time.sleep(2)
    
    # Hide loading
    yield {'show': False, 'message': ''}
```

## JavaScript Utilities

### Show Toast (Client-side)
```javascript
window.dashUtils.showToast({
    type: 'success',
    title: 'Success',
    message: 'Operation complete',
    duration: 3000
});
```

### Show/Hide Loading
```javascript
window.dashUtils.showLoading('Processing...');
// ... do work ...
window.dashUtils.hideLoading();
```

### Update Progress
```javascript
window.dashUtils.updateProgress('progress-id', 50, 100);
```

## CSS Classes

### Component Classes
- `.enhanced-tabs-container` - Tab container
- `.enhanced-control-panel` - Control panel
- `.enhanced-toast` - Toast notification
- `.loading-overlay` - Loading overlay
- `.enhanced-progress-bar` - Progress bar

### State Classes
- `.show` - Show element
- `.collapsed` - Collapsed state
- `.active` - Active tab/element
- `.dragover` - Drag over state

### Responsive Classes
- `.desktop-large` - ≥1920px
- `.desktop-medium` - 1440-1919px
- `.desktop-small` - 1280-1439px
- `.desktop-compact` - 1024-1279px

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Tab` | Navigate forward |
| `Shift+Tab` | Navigate backward |
| `Ctrl+→` | Next tab |
| `Ctrl+←` | Previous tab |
| `Escape` | Close modal/toast |
| `Enter` | Activate button |
| `Space` | Toggle checkbox |

## Store IDs

Essential stores for Enhanced UI:
- `ui-state-store` - Main UI state
- `viewport-dimensions` - Window size
- `loading-state-store` - Loading states
- `toast-trigger-store` - Toast triggers

## Common Patterns

### Initialize Enhanced UI
```python
layout = html.Div([
    # Required includes
    add_enhanced_ui_scripts(),
    add_viewport_detection(),
    
    # UI Components
    EnhancedUIComponents.create_toast_container(),
    
    # State stores
    dcc.Store(id='ui-state-store', data={}),
    dcc.Store(id='loading-state-store', data={'show': False}),
    dcc.Store(id='toast-trigger-store', data=0),
    
    # Your content
    your_app_content
])
```

### Register Callbacks
```python
from meld_visualizer.callbacks.enhanced_ui_callbacks import register_enhanced_ui_callbacks

def create_app():
    app = dash.Dash(__name__)
    app.layout = create_layout()
    
    # Register enhanced UI callbacks
    register_enhanced_ui_callbacks(app)
    
    return app
```

### Responsive Layout
```python
@callback(
    Output('layout', 'children'),
    Input('viewport-dimensions', 'data')
)
def update_layout(viewport):
    config = ResponsiveLayoutManager.get_layout_config(
        viewport.get('width', 1920)
    )
    # Build layout based on config
    return create_responsive_layout(config)
```

## Troubleshooting

### Toast not showing?
1. Check `toast-trigger-store` is incrementing
2. Verify `ui-state-store` has `last_toast`
3. Check browser console for errors

### Tabs not scrolling?
1. Verify `.enhanced-tabs-scroll-container` exists
2. Check if tabs overflow container width
3. Ensure scroll buttons are not disabled

### Loading stuck?
1. Ensure callback sets `{'show': False}`
2. Check for errors in callback
3. Use try/finally to guarantee hide

### Panel won't collapse?
1. Check `collapsible=True` in creation
2. Verify Bootstrap JS is loaded
3. Check for ID conflicts

## Performance Tips

1. **Lazy load panels**: Create only when expanded
2. **Debounce inputs**: Prevent rapid callbacks
3. **Use prevent_initial_call**: Skip unnecessary renders
4. **Batch updates**: Combine multiple state changes
5. **Cache components**: Store frequently used components

## File Locations

```
src/meld_visualizer/
├── core/
│   └── enhanced_ui.py          # Component factories
├── callbacks/
│   └── enhanced_ui_callbacks.py # Callback handlers
assets/
├── enhanced-desktop-ui.css     # Styles
└── enhanced-ui.js              # JavaScript
docs/
├── ENHANCED_UI_DOCUMENTATION.md    # Full docs
├── ENHANCED_UI_DEVELOPER_GUIDE.md  # Dev guide
└── ENHANCED_UI_ARCHITECTURE.md     # Architecture
```

---

*Quick Reference v1.0 | Enhanced UI v2.0*