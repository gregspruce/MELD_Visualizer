#!/usr/bin/env bash
set -euo pipefail

BRANCH="${1:-ci-e2e-tabs-bootstrap}"
git checkout -b "$BRANCH"
git add -A
git commit -m "UI: Load Bootstrap theme; CI/E2E: add tab assertions and docs notes"
git push -u origin "$BRANCH"

echo
echo "Branch pushed: $BRANCH"
echo "Open a PR at: https://github.com/${GITHUB_REPOSITORY:-<your-user>/<your-repo>}/compare/$BRANCH?expand=1"
