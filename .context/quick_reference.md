# MELD Visualizer - Quick Reference

## Critical Constants
```python
FEEDSTOCK_DIMENSION_INCHES = 0.5  # Square rod dimension
FEEDSTOCK_AREA_MM2 = 161.29       # Corrected square area (was 126.7 circular)
```

## Launch Commands
```bash
# CORRECT - Use module execution
python -m meld_visualizer

# CORRECT - If installed with pip
meld-visualizer

# WRONG - Direct script execution (causes import errors)
python src/meld_visualizer/app.py
```

## Repository Information
- **GitHub**: https://github.com/gregspruce/MELD_Visualizer
- **NOT**: ~~MELD-labs/meld-visualizer~~ (hallucinated URL)

## Hot-Reload Features
| Feature | Status | Method |
|---------|--------|--------|
| Theme Switching | ✅ Instant | Clientside CSS injection |
| Graph Options | ✅ Instant | Runtime config update |
| Manual config.json edits | ⚠️ Requires restart | File not watched |

## Project Structure
```
MELD_Visualizer/
├── src/
│   └── meld_visualizer/        # Main package
│       ├── __main__.py         # Module execution
│       ├── app.py             # Entry point
│       ├── callbacks/         # Modular callbacks
│       └── utils/             # Utilities
│           └── hot_reload.py  # Hot-reload system
├── tests/                     # Test suite
├── config.json               # User configuration
└── CLAUDE.md                 # AI assistant guide
```

## Common Commands
```bash
# Run application
python -m meld_visualizer

# Run tests
pytest                      # All tests
pytest -m "not e2e"        # Unit tests only
pytest -m "e2e"            # E2E tests only

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Build executable
pyinstaller VolumetricPlotter.spec
```

## Key Files and Their Purposes
| File | Purpose |
|------|---------|
| `app.py` | Main application entry, creates Dash app |
| `layout.py` | UI components and structure |
| `callbacks/*.py` | Modular callback handlers |
| `data_processing.py` | CSV/G-code parsing, mesh generation |
| `config.py` | Configuration management |
| `utils/hot_reload.py` | Dynamic theme/config updates |
| `utils/security_utils.py` | Input validation and sanitization |

## Error Handling Pattern
```python
# Standard return format
return data, error_message, conversion_flag
# Example: (df, None, False) for success
# Example: (None, "Parse error", False) for failure
```

## Callback Pattern
```python
@callback(
    Output('component', 'property'),
    Input('trigger', 'property'),
    State('state', 'property'),
    allow_duplicate=True  # For hot-reload
)
```

## Testing Quick Reference
```python
# Test markers
@pytest.mark.unit         # Fast, isolated tests
@pytest.mark.integration  # Component interaction
@pytest.mark.e2e         # Browser automation

# Test structure
tests/
├── unit/           # Function tests
├── integration/    # Component tests
└── e2e/           # User workflow tests
```

## Configuration Structure
```json
{
  "theme": {
    "bootstrap": "cosmo",
    "plotly": "plotly_white"
  },
  "graph_options": {
    "show_grid": true,
    "z_stretch_factor": 5.0
  }
}
```

## Recent Critical Fixes
1. **Volume Calculation**: Fixed 27% error (circular → square geometry)
2. **Import Errors**: Added `__main__.py` for module execution
3. **Hot-Reload**: Implemented instant theme/config updates
4. **GitHub URLs**: Corrected all repository references

## Performance Benchmarks
- File Load: <2 seconds for typical CSV
- Hot-Reload: <100ms for theme switch
- Memory: <500MB for standard datasets
- 3D Rendering: 60 FPS target

## Security Measures
- Input validation on all uploads
- File size limits (100MB default)
- Path traversal prevention
- No code execution from uploads

## Debug Tips
```python
# Enable debug mode
DEBUG="1" python -m meld_visualizer

# Check imports
python -c "from meld_visualizer import app"

# Verify config
python -c "from meld_visualizer.config import load_config; print(load_config())"
```

## Common Issues and Solutions
| Issue | Solution |
|-------|----------|
| Import errors | Use `python -m meld_visualizer` |
| Theme not updating | Check if using in-app settings (manual edits need restart) |
| Volume looks wrong | Verify using square rod formula (161.29mm²) |
| Config not loading | Check config.json syntax |

## Environment Requirements
- Python 3.8+
- Chrome/Chromium (for E2E tests)
- 4GB RAM minimum
- Modern browser with JavaScript enabled

## Contact and Support
- Repository: https://github.com/gregspruce/MELD_Visualizer
- Issues: GitHub Issues page
- Documentation: README.md, CLAUDE.md