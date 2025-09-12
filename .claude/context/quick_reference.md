# MELD Visualizer - Quick Reference
*For rapid agent onboarding*

## Current Status
- ✅ Application fully functional
- ✅ All callbacks working (79+ conflicts resolved)
- ⚠️ Enhanced UI rolled back (needs proper integration)

## Key Files
- **Main Layout**: `C:\VSCode\MELD\MELD_Visualizer\meld_visualizer\core\layout.py`
- **Callbacks**: `C:\VSCode\MELD\MELD_Visualizer\meld_visualizer\core\callbacks\*.py`
- **Data Processing**: `C:\VSCode\MELD\MELD_Visualizer\meld_visualizer\core\data_processing.py`
- **Config**: `C:\VSCode\MELD\MELD_Visualizer\config.json`

## Critical Constants
- **Plot Heights**: 350-500px (NOT vh units!)
- **Width Multiplier**: 1.654 (for volume calculations)
- **Feedstock**: 0.5" × 0.5" square

## Common Pitfalls to Avoid
1. **Don't** register callbacks for non-existent components
2. **Don't** use viewport-relative heights (vh) for plots
3. **Don't** create circular dependencies in callbacks
4. **Don't** break existing functionality when adding features

## Callback Registration Order
```python
1. data_callbacks
2. config_callbacks
3. filter_callbacks
4. graph_callbacks
5. visualization_callbacks
```

## Testing Checklist
- [ ] No browser console errors
- [ ] Plots render at correct height
- [ ] File upload works
- [ ] Theme switching works
- [ ] All plots interactive

## Import Pattern
```python
from meld_visualizer.core import module_name
```

## Error Handling Pattern
```python
return (data, error_message, conversion_flag)
```

---
*Use full context document for detailed information*
