---
name: "PR5: Voxelization + Isosurface Mode"
about: "Scaffold tasks for PR5 - Voxelization + Isosurface Mode"
title: "PR5 - Voxelization + Isosurface Mode"
labels: "feature,performance,3d"
assignees: ""
---

## Branch
`feat/voxel-isosurface`

## Goal
Implement the scoped changes for PR5: Voxelization + Isosurface Mode.

## Tasks
- [ ] Implement src/meldviz/voxel.py using histogramdd (64^3 default)
- [ ] UI toggle Points <-> Voxels and resolution control
- [ ] Render isosurfaces for selected scalar with threshold slider

## Acceptance Criteria
- 1M rows voxelize to 64^3 in <=2.5 s baseline
- Toggle and threshold updates work smoothly

## Notes
- Link benchmarks and screenshots (if UI is touched).
- Follow Conventional Commits.

