#!/usr/bin/env bash
# Daily cycle for compute-curve: collect, rebuild the index, run the paper
# account, and commit the new immutable raw data and reports.
#
# Schedule it once a day (see README.md, "Scheduling"). It is idempotent:
# running it twice on the same UTC day collects nothing new.
#
# Set COMPUTE_CURVE_PUSH=0 to commit locally without pushing.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_DIR"

git pull --ff-only --quiet || echo "warning: git pull failed; continuing with local copy"

uv sync --quiet
uv run compute-curve daily
uv run compute-curve evaluate

git add data/raw data/collection_log.jsonl reports
if ! git diff --cached --quiet; then
  git commit --quiet -m "Daily snapshot $(date -u +%Y-%m-%d)"
  if [ "${COMPUTE_CURVE_PUSH:-1}" = "1" ]; then
    git push --quiet
  fi
fi
