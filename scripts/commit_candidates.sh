#!/usr/bin/env bash
# Commit any changes under candidates/ to main and push, retrying if main moved meanwhile.
# Usage: scripts/commit_candidates.sh "commit message"
set -euo pipefail

git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"

git add -A candidates
if git diff --cached --quiet; then
  echo "Nothing to commit."
  exit 0
fi
git commit -q -m "$1"

for attempt in 1 2 3; do
  if git pull -q --rebase origin main && git push -q origin HEAD:main; then
    echo "Pushed: $1"
    exit 0
  fi
  echo "Push failed (attempt $attempt), retrying..."
  sleep $((attempt * 5))
done
echo "Could not push to main after 3 attempts." >&2
exit 1
