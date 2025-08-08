---
name: "PR9: Test Suite Upgrade"
about: "Scaffold tasks for PR9 - Test Suite Upgrade"
title: "PR9 - Test Suite Upgrade"
labels: "test,quality"
assignees: ""
---

## Branch
`test/suite-upgrade`

## Goal
Implement the scoped changes for PR9: Test Suite Upgrade.

## Tasks
- [ ] Add tests/generators.py for synthetic data
- [ ] JSON snapshot tests for scatter3d, isosurface, ROI flow
- [ ] Dash E2E: upload -> map -> filter -> toggle -> export
- [ ] Perf markers for 10k/100k/1M (CI runs 10k/100k)

## Acceptance Criteria
- CI completes all tests under 10 minutes
- Flaky tests quarantined with marker

## Notes
- Link benchmarks and screenshots (if UI is touched).
- Follow Conventional Commits.

