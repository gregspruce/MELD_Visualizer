# MELD Visualizer - Agent Briefing

## Quick Start for New Agents

You are working on **MELD Visualizer**, a Dash web application for 3D visualization of MELD manufacturing data.

### Essential Information
- **Repository**: https://github.com/gregspruce/MELD_Visualizer
- **Main Entry**: `src/meld_visualizer/app.py`
- **Architecture**: MVC-like with Dash/Plotly
- **Current Status**: Fully functional, recent critical fixes applied

### Critical Recent Fix (MUST KNOW)
**Volume Calculation Corrected** (2025-08-18):
- **OLD (WRONG)**: Circular wire assumption - Area = π × (d/2)² = 126.7mm²
- **NEW (CORRECT)**: Square rod reality - Area = w² = 161.29mm²
- **Impact**: 27% more accurate volume representations
- **Constant**: `FEEDSTOCK_AREA_MM2 = 161.29` in `constants.py`

### File Structure
```
src/meld_visualizer/
├── app.py              # Main entry point
├── layout.py           # UI components (View)
├── callbacks/          # Event handlers (Controller)
│   ├── __init__.py
│   ├── data_callbacks.py
│   ├── visualization_callbacks.py
│   └── settings_callbacks.py
├── data_processing.py  # Data operations (Model)
├── config.py          # Configuration management
├── constants.py       # Critical constants (FEEDSTOCK dimensions)
└── utils/
    └── security_utils.py  # InputValidator
```

### Common Tasks

#### Running the App
```bash
python app.py
```

#### Testing
```bash
pytest -m "not e2e"  # Unit tests only
pytest -m "e2e"      # E2E tests (requires Chrome)
pytest               # All tests
```

#### Making Changes
1. **Data Processing**: Edit `data_processing.py`
2. **UI Changes**: Edit `layout.py`
3. **Interactivity**: Edit files in `callbacks/`
4. **Configuration**: Edit `config.json` (requires restart)

### Key Patterns
- **Callbacks**: Use `@callback` decorator with Input/Output/State
- **IDs**: Pattern matching `{'type': 'component-type', 'index': 'identifier'}`
- **Error Handling**: Return tuples `(data, error_message, conversion_flag)`
- **Theming**: All plots use `PLOTLY_TEMPLATE` from config

### Current Focus Areas
1. **Volume Accuracy**: Recent fix ensures correct square rod calculations
2. **Import Stability**: All imports fixed after repository restructuring
3. **Performance**: Caching implemented for expensive operations
4. **User Experience**: 20+ themes, configurable UI, interactive 3D plots

### Known Limitations
- Config changes require restart (no hot-reload for JSON)
- Theme changes need full app restart
- Large datasets may need optimization

### Testing Strategy
- **Unit Tests**: Test individual functions in isolation
- **Integration Tests**: Test complete workflows
- **E2E Tests**: Browser automation for user scenarios
- Use appropriate pytest markers for selective testing

### Security Considerations
- `InputValidator` sanitizes all user inputs
- File uploads are validated for type and size
- Safe path handling prevents directory traversal
- Error messages don't expose sensitive information

## Agent Coordination Notes

### If You're Working On:

**Data Processing**:
- Check `constants.py` for feedstock geometry
- Maintain unit conversion (inches → mm)
- Update tests in `tests/test_data_processing.py`

**UI/UX**:
- Follow Bootstrap component patterns
- Maintain theme compatibility
- Test with multiple themes

**Performance**:
- Profile before optimizing
- Consider caching strategies
- Test with large datasets

**Testing**:
- Write tests for new features
- Maintain test markers
- Update E2E tests for UI changes

### Communication Protocol
1. Document significant changes in commit messages
2. Update this briefing if you discover critical information
3. Flag breaking changes prominently
4. Maintain backwards compatibility when possible

### Recent Agent Activity
- **Repository Restructuring**: Completed migration to src/ layout
- **Error Detective**: Fixed all import issues
- **Code Review**: Ensured best practices
- **Performance**: Implemented caching system

## Next Agent Checklist
- [ ] Review recent fixes in `project_context.md`
- [ ] Check current git status
- [ ] Verify app runs with `python app.py`
- [ ] Run unit tests to ensure stability
- [ ] Read relevant module for your task
- [ ] Update context docs after significant changes