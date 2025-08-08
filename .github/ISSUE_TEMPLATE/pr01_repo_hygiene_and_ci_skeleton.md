---
name: "PR1: Repo hygiene & CI skeleton"
about: "Scaffold tasks for PR1 - Repo hygiene & CI skeleton"
title: "PR1 - Repo hygiene & CI skeleton"
labels: "infra,ci,good-first-issue"
assignees: ""
---

## Branch
`infra/repo-hygiene-ci`

## Goal
Implement the scoped changes for PR1: Repo hygiene & CI skeleton.

## Tasks
- [ ] Create pyproject.toml with runtime and dev dependencies
- [ ] Configure ruff, black, mypy in pyproject
- [ ] Add GitHub Actions CI (Python 3.10-3.12): lint, type-check, tests
- [ ] Add .gitignore and remove tracked artifacts (__pycache__, build, etc.)
- [ ] Add LICENSE, CHANGELOG.md, repo description/topics
- [ ] Add .github/pull_request_template.md and basic issue templates

## Acceptance Criteria
- CI green on PR and main
- Lint/format/type/tests pass locally and in CI
- PR template shows by default

## Notes
- Link benchmarks and screenshots (if UI is touched).
- Follow Conventional Commits.

