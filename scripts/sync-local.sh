#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

TARGET_BRANCH="${1:-main}"

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "This script must be run from a Git checkout." >&2
  exit 1
fi

if [ -n "$(git status --porcelain)" ]; then
  echo "Local working tree has uncommitted changes." >&2
  echo "Commit or stash local changes before syncing." >&2
  exit 1
fi

git fetch origin "$TARGET_BRANCH"

CURRENT_BRANCH="$(git branch --show-current)"
if [ "$CURRENT_BRANCH" != "$TARGET_BRANCH" ]; then
  git switch "$TARGET_BRANCH"
fi

git pull --ff-only origin "$TARGET_BRANCH"

echo "Synced $TARGET_BRANCH from origin."
