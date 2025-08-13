#!/usr/bin/env bash
set -euo pipefail

BRANCH="${1:-ci-e2e-tabs}"
git checkout -b "$BRANCH"

# Ensure executable bit on scripts
git update-index --chmod=+x run_tests.sh || true

git add -A
git commit -m "CI+E2E: localhost bind, tab assertions, and merged docs"
git push -u origin "$BRANCH"

echo
echo "Branch pushed: $BRANCH"
echo "Open a PR at: https://github.com/${GITHUB_REPOSITORY:-<your-user>/<your-repo>}/compare/$BRANCH?expand=1"
