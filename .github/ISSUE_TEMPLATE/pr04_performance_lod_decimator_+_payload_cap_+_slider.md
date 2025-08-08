---
name: "PR4: Performance/LOD (decimator + payload cap + slider)"
about: "Scaffold tasks for PR4 - Performance/LOD (decimator + payload cap + slider)"
title: "PR4 - Performance/LOD (decimator + payload cap + slider)"
labels: "performance,ux"
assignees: ""
---

## Branch
`perf/lod-decimator`

## Goal
Implement the scoped changes for PR4: Performance/LOD (decimator + payload cap + slider).

## Tasks
- [ ] Implement src/meldviz/lod.py with deterministic sampling
- [ ] Enforce payload cap (~6 MB) and show point-count/payload estimates
- [ ] Add Performance slider that adjusts sample percent

## Acceptance Criteria
- 100k interactions stay <800 ms median
- Slider affects latency and point budget as expected

## Notes
- Link benchmarks and screenshots (if UI is touched).
- Follow Conventional Commits.

