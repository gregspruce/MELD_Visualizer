# MELD Visualizer - Context Index

## Quick Navigation

### By Topic

#### 🏗️ Architecture & Design
- [Project Overview](#project-overview) → `project_context.md#1-project-overview`
- [MVC Architecture](#mvc-architecture) → `project_context.md#3-design-decisions`
- [File Structure](#file-structure) → `quick_reference.json#file_structure`
- [Package Layout](#package-layout) → `agent_briefing.md#file-structure`

#### 🔧 Critical Fixes & Constants
- [Volume Calculation Fix](#volume-fix) → `project_context.md#recent-critical-fixes-summary`
- [Feedstock Constants](#constants) → `quick_reference.json#critical_constants`
- [Import Error Fixes](#imports) → `project_context.md#2-current-state`
- [Repository URL Corrections](#urls) → `quick_reference.json#recent_fixes`

#### 💻 Development
- [Quick Commands](#commands) → `quick_reference.json#quick_commands`
- [Testing Strategy](#testing) → `project_context.md#4-code-patterns`
- [Callback Patterns](#callbacks) → `agent_briefing.md#key-patterns`
- [Error Handling](#errors) → `project_context.md#4-code-patterns`

#### 📊 Data Processing
- [Processing Pipeline](#pipeline) → `project_context.md#4-code-patterns`
- [Unit Conversion](#conversion) → `agent_briefing.md#data-processing`
- [G-code Parsing](#gcode) → `project_context.md#1-project-overview`
- [Volume Mesh Generation](#mesh) → `project_context.md#2-current-state`

#### 🎨 UI & Visualization
- [Theme System](#themes) → `project_context.md#1-project-overview`
- [3D Plots](#plots) → `agent_briefing.md#current-focus-areas`
- [Layout Components](#layout) → `agent_briefing.md#making-changes`
- [Interactive Features](#interactive) → `project_context.md#1-project-overview`

#### 🔐 Security
- [Input Validation](#validation) → `project_context.md#3-design-decisions`
- [File Upload Security](#uploads) → `agent_briefing.md#security-considerations`
- [Error Handling](#security-errors) → `project_context.md#4-code-patterns`

#### 🤖 Agent Coordination
- [Agent History](#agent-history) → `project_context.md#5-agent-coordination-history`
- [Specialized Agents](#agents) → `quick_reference.json#agent_context`
- [Coordination Protocol](#protocol) → `agent_briefing.md#communication-protocol`
- [Recent Activity](#activity) → `agent_briefing.md#recent-agent-activity`

#### 🚀 Future Development
- [Roadmap](#roadmap) → `project_context.md#6-future-roadmap`
- [Known Issues](#issues) → `quick_reference.json#known_issues`
- [Performance Opportunities](#performance) → `project_context.md#6-future-roadmap`
- [Technical Debt](#debt) → `project_context.md#6-future-roadmap`

### By File Location

#### Context Documents
- `project_context.md` - Comprehensive project documentation
- `quick_reference.json` - Structured quick lookup data
- `agent_briefing.md` - New agent onboarding guide
- `context_index.md` - This navigation index

#### Source Code
- `src/meld_visualizer/app.py` - Main application entry
- `src/meld_visualizer/layout.py` - UI components
- `src/meld_visualizer/callbacks/` - Event handlers
- `src/meld_visualizer/data_processing.py` - Data operations
- `src/meld_visualizer/constants.py` - Critical constants
- `src/meld_visualizer/config.py` - Configuration management

#### Configuration
- `config.json` - User settings and themes
- `pytest.ini` - Test configuration
- `requirements.txt` - Production dependencies
- `requirements-dev.txt` - Development dependencies

#### Testing
- `tests/` - Unit tests
- `tests/e2e/` - End-to-end tests
- `run_tests.sh` - Test runner script

### By Use Case

#### "I need to fix a bug"
1. Check `quick_reference.json#recent_fixes` for similar issues
2. Review `agent_briefing.md#known-limitations`
3. Run tests: `quick_reference.json#quick_commands`
4. Follow patterns: `project_context.md#4-code-patterns`

#### "I need to add a feature"
1. Review architecture: `project_context.md#3-design-decisions`
2. Check roadmap: `project_context.md#6-future-roadmap`
3. Follow conventions: `project_context.md#4-code-patterns`
4. Update tests: `agent_briefing.md#testing-strategy`

#### "I need to understand the codebase"
1. Start with: `agent_briefing.md`
2. Deep dive: `project_context.md`
3. Quick lookups: `quick_reference.json`
4. Navigation: This index

#### "I need to deploy/build"
1. Commands: `quick_reference.json#quick_commands`
2. Build process: `project_context.md#1-project-overview`
3. Dependencies: `quick_reference.json#tech_stack`

#### "I need to fix performance issues"
1. Current baselines: `project_context.md#2-current-state`
2. Opportunities: `project_context.md#6-future-roadmap`
3. Caching: `project_context.md#2-current-state`

### Critical Information Lookup

#### Constants (MUST USE THESE)
```python
FEEDSTOCK_DIMENSION_INCHES = 0.5  # Square rod
FEEDSTOCK_AREA_MM2 = 161.29       # NOT 126.7 (old circular)
```

#### Repository
```
https://github.com/gregspruce/MELD_Visualizer
NOT: MELD-labs/meld-visualizer (hallucinated)
```

#### Main Entry Point
```bash
python app.py  # From project root
# OR
python src/meld_visualizer/app.py
```

### Version History
- **v1.0** (2025-08-18): Initial context capture after critical fixes
- Repository restructured to professional src/ layout
- Volume calculation corrected (27% accuracy improvement)
- All import errors fixed
- GitHub URLs corrected

### Search Keywords
#architecture #mvc #dash #plotly #bootstrap #themes #3d-visualization
#volume-calculation #feedstock #square-rod #gcode #csv-processing
#testing #pytest #selenium #e2e #unit-tests #integration
#callbacks #pattern-matching #error-handling #security #validation
#performance #caching #optimization #memory #hot-reload
#agent-coordination #context #briefing #roadmap #technical-debt
