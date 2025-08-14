# Decisions
- Selenium 4 Manager, not chromedriver pins.
- Runtime vs test deps split.
- Repo-controlled test switch + env override.
- Jules setup idempotent; Chrome optional.
- Local bind 127.0.0.1 by default.
- Support both get_layout(app) and create_layout().
- E2E asserts title, upload control, and tab labels.
- Implemented G-code parser to produce a DataFrame compatible with existing mesh/toolpath generation logic, maximizing code reuse.
- G-code mesh is colored by Z-position as a sensible default, since process data is unavailable in the source file.