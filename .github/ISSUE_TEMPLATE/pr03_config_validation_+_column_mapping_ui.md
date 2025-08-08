---
name: "PR3: Config validation + Column Mapping UI"
about: "Scaffold tasks for PR3 - Config validation + Column Mapping UI"
title: "PR3 - Config validation + Column Mapping UI"
labels: "ux,validation"
assignees: ""
---

## Branch
`feat/config-validation-column-mapping`

## Goal
Implement the scoped changes for PR3: Config validation + Column Mapping UI.

## Tasks
- [ ] Add Pydantic models for config.json and runtime settings
- [ ] Implement header mapping persistence (src/meldviz/mapping.py)
- [ ] UI modal to map headers -> canonical fields with preview
- [ ] Apply mapping on load; warn on missing/extra columns

## Acceptance Criteria
- Invalid config yields actionable errors (no crash)
- Mapped CSV renders without code changes; mapping persists

## Notes
- Link benchmarks and screenshots (if UI is touched).
- Follow Conventional Commits.

