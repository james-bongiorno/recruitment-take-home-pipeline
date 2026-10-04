#!/usr/bin/env bash
# Stop if this repository is public. The pipeline commits candidates' names, GitHub usernames,
# activity logs and code into candidates/, which must never be public.
# Set the repository variable ALLOW_PUBLIC_REPO=true only if you really mean it.
set -euo pipefail

if [ "${ALLOW_PUBLIC_REPO:-}" = "true" ]; then
  echo "ALLOW_PUBLIC_REPO=true, skipping the private-repo check."
  exit 0
fi

private=$(gh api "repos/${GITHUB_REPOSITORY}" --jq .private)
if [ "$private" != "true" ]; then
  msg="This repository is public. The pipeline stores candidate names, usernames, logs and code in candidates/, so it only runs in a private repository. Make a private copy (Use this template → Private) and run it there."
  echo "::error::$msg"
  echo "### Stopped: public repository" >> "${GITHUB_STEP_SUMMARY:-/dev/null}"
  echo "$msg" >> "${GITHUB_STEP_SUMMARY:-/dev/null}"
  exit 1
fi
echo "Repository is private."
