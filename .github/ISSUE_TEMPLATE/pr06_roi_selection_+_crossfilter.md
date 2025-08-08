---
name: "PR6: ROI Selection + Crossfilter"
about: "Scaffold tasks for PR6 - ROI Selection + Crossfilter"
title: "PR6 - ROI Selection + Crossfilter"
labels: "feature,ux"
assignees: ""
---

## Branch
`feat/roi-crossfilter`

## Goal
Implement the scoped changes for PR6: ROI Selection + Crossfilter.

## Tasks
- [ ] Add ROI primitives (AABB; optional convex hull) in src/meldviz/roi.py
- [ ] 3D UI controls with debounced updates to server
- [ ] Apply ROI server-side and add 'Export ROI as CSV'

## Acceptance Criteria
- ROI updates linked charts in <1 s at 100k
- Exported CSV matches filtered points

## Notes
- Link benchmarks and screenshots (if UI is touched).
- Follow Conventional Commits.

