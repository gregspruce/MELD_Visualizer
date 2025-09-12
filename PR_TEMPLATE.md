# Pull Request: Fix Volume Plot Bead Overlap Calibration

**Branch**: `fix/bead-overlap-calibration`
**Target**: `main`

## Summary
This PR fixes a critical visualization issue where the volume plot showed gaps between beads while physical prints showed proper overlap and fusion. The solution implements a width multiplier calibration system that accounts for material spreading during the MELD deposition process.

## Problem Description
- **Issue**: Volume plots showed 8.86mm gaps between tracks
- **Reality**: Physical build (20250722163434) showed overlapping, merged beads
- **Impact**: Made it difficult to validate process parameters and trust visualizations

## Root Cause Analysis
The theoretical capsule model for bead geometry underestimated actual bead width. The physical MELD process causes material to spread ~65% wider than conservation of mass predicts due to:
- Material flow under pressure during deposition
- Thermal spreading and surface tension effects
- Mechanical deformation from the tool

## Solution Implemented

### 1. Width Multiplier System
- Added `width_multiplier` parameter to `VolumeCalculator` class
- Calibrated to 1.654 based on physical measurements
- Increases effective bead width from 27.4mm to 45.3mm
- Achieves realistic 20% overlap between adjacent tracks

### 2. Auto-Loading Calibration
- System automatically loads calibration from `config/volume_calibration.json`
- No manual intervention required for standard operations
- Calibration persists across sessions

### 3. Analysis Tools
Created comprehensive analysis and calibration scripts:
- `analyze_bead_overlap.py` - Analyzes track spacing and bead dimensions
- `apply_width_calibration.py` - Calculates and applies calibration
- `test_overlap_calibration.py` - Validates calibration effectiveness

## Changes Made

### Core Module Updates
- **volume_calculations.py**:
  - Added `width_multiplier` parameter with default 1.0
  - New `calculate_effective_bead_width()` method
  - Updated `set_calibration()` to accept width multiplier
  - Added `Bead_Width_mm` column to processed DataFrames

- **volume_mesh.py**:
  - Updated `generate_cross_section()` to apply width multiplier
  - Modified all mesh generation methods to use calibrated width
  - Ensures visual representation matches physical reality

- **data_service.py**:
  - Added `_load_calibration()` method for automatic loading
  - Applies calibration to both calculator and mesh generator
  - Logs calibration loading for transparency

### Configuration Files
- `config/volume_calibration.json` - Main calibration file
- `config/volume_calibration_final.json` - Detailed calibration with validation data
- `BEAD_OVERLAP_CALIBRATION.md` - Comprehensive documentation

## Validation Results

### Before Calibration:
- Calculated Bead Width: 27.40 mm
- Track Spacing: 36.26 mm
- **Result**: 8.86 mm GAP (incorrect)

### After Calibration:
- Calculated Bead Width: 45.33 mm
- Track Spacing: 36.26 mm
- **Result**: 9.07 mm OVERLAP / 20% (matches physical build)

## Test Plan
- [x] Run unit tests: `python tests/test_volume_modules.py`
- [x] Validate calibration: `python scripts/test_overlap_calibration.py`
- [x] Visual comparison with physical build images
- [x] Test auto-loading of calibration on app startup
- [x] Verify backward compatibility with existing data

## Visual Evidence
The calibration was validated against:
- Physical build photo: `data/csv/20250722163434.jpg`
- Original volume plot: `data/csv/VOLUME_20250722163434.PNG`
- Toolpath plot: `data/csv/TOOLPATH_20250722163434.PNG`

## Breaking Changes
None - The change is backward compatible with a default multiplier of 1.0

## Future Improvements
- Variable width multipliers for different process parameters
- Layer-specific calibration for first layer spreading
- Material database with calibrations per material type
- Automatic calibration from image analysis

## How to Test
1. Check out this branch
2. Run: `python scripts/test_overlap_calibration.py`
3. Expected output: "Beads are overlapping as expected!"
4. Generate a volume plot with test data to see visual overlap

## Files Changed
- **Modified Core Modules**:
  - `src/meld_visualizer/core/volume_calculations.py`
  - `src/meld_visualizer/core/volume_mesh.py`
  - `src/meld_visualizer/services/data_service.py`

- **New Configuration Files**:
  - `config/volume_calibration.json` (modified)
  - `config/volume_calibration_corrected.json`
  - `config/volume_calibration_final.json`

- **New Scripts**:
  - `scripts/analyze_bead_overlap.py`
  - `scripts/apply_width_calibration.py`
  - `scripts/test_overlap_calibration.py`
  - `scripts/tune_bead_width.py`

- **Documentation**:
  - `BEAD_OVERLAP_CALIBRATION.md`
  - `PR_TEMPLATE.md` (this file)

## Review Checklist
- [ ] Code follows project style guidelines
- [ ] Tests pass successfully
- [ ] Documentation is updated
- [ ] Calibration values are reasonable
- [ ] Visual output matches physical reality
- [ ] No breaking changes to existing functionality

## Screenshots/Evidence
Please refer to the files in `data/csv/`:
- `20250722163434.jpg` - Physical build showing overlapping beads
- `VOLUME_20250722163434.PNG` - Original volume plot with gaps
- After applying this fix, the volume plot now shows proper overlap

---

**To create this PR on GitHub:**
1. Go to: https://github.com/gregspruce/MELD_Visualizer/pull/new/fix/bead-overlap-calibration
2. Copy and paste this content into the PR description
3. Set the title to: "Fix: Volume plot bead overlap calibration to match physical prints"
4. Submit the pull request
