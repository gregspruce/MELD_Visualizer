# MELD Visualizer - Quick Context Reference

## 🚀 CRITICAL LAUNCH COMMAND
```bash
# ALWAYS USE THIS:
export PYTHONPATH=C:\VSCode\MELD\MELD_Visualizer\src
python -m meld_visualizer
```

## ✅ Recent Critical Fixes (ALL COMPLETE)
1. **Volume Calculation**: Fixed 27% error (square rod, not wire)
2. **Import Errors**: Added `__main__.py`, fixed relative imports
3. **Repository URLs**: Corrected to `gregspruce/MELD_Visualizer`

## 📁 Project Structure
```
src/meld_visualizer/
├── __main__.py         # NEW: Module entry point
├── app.py              # Main application
├── callbacks/          # Modular callbacks (split)
├── utils/              # Security and helpers
└── data_processing.py  # FIXED: Volume calculations
```

## 🔑 Key Values
- **FEEDSTOCK_AREA_MM2**: 161.29 (was 126.7 - FIXED)
- **Square Rod**: 0.5 inches (12.7mm) per side
- **Repository**: https://github.com/gregspruce/MELD_Visualizer

## 🎯 Current Status
- **Branch**: main (clean)
- **State**: Fully functional
- **Tests**: All passing
- **Blockers**: None

## 🛠️ Common Commands
```bash
# Run app
python -m meld_visualizer

# Test
pytest                  # All tests
pytest -m "not e2e"    # Unit only
pytest -m "e2e"        # E2E only

# Install for development
pip install -e .
```

## ⚠️ Remember
- NEVER use `python src/meld_visualizer/app.py` directly
- config.json changes need restart
- All fixes are merged to main
- Volume calculations now accurate (27% improvement)