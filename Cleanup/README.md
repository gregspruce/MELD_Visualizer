# Cleanup Folder

## Purpose
This folder contains files that were moved during the repository reorganization on 2025-08-22. These files are pending review for:
- **Archival** - Historical documentation that may be valuable for reference
- **Relocation** - Files that belong in a different directory
- **Deletion** - Outdated or duplicate files no longer needed

## Contents

### 📄 Documentation (`/documentation/`)
Historical documentation and reports from the root directory that may contain valuable context:
- Project context and AI assistant configurations
- UI/UX analysis reports
- Performance reports
- Implementation summaries

### 📁 Assets (`/assets/`)
Duplicate static files (CSS/JS) that were consolidated into `src/meld_visualizer/static/`

### ⚙️ Configuration (`/config/`)
- Older or intermediate configuration files
- Previous versions of volume calibration settings

### 🔧 Temporary Files (`/temp/`)
- Utility scripts that may belong in `/scripts/` or `/tools/`
- Test data files
- Cleanup utilities

### 📊 Logs (`/logs/`)
- Duplicate log directories that were consolidated

## Review Guidelines

When reviewing files in this folder:

1. **Check for historical value** - Does this document provide important context?
2. **Verify no active dependencies** - Ensure no code references these files
3. **Consider archival** - Would this be useful for future reference?
4. **Identify proper location** - Should this file be moved elsewhere?

## Important Files

### REORGANIZATION_SUMMARY.md
Contains a detailed breakdown of:
- What was moved and why
- Code changes made to accommodate the reorganization
- Recommendations for each file/folder

## Next Steps

1. Review each subdirectory
2. Make decisions on keep/move/delete
3. Update this README with decisions
4. Remove files after team consensus

## Note
This folder is **intentionally tracked in Git** to facilitate collaborative review and maintain transparency about the reorganization process.