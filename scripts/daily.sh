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

# Exploration candidates: shadow forecasts only, never an order
# (docs/exploration_plan.md section 9).
if uv run pytest -q; then
  uv run compute-curve explore round1 shadow \
    || echo "warning: exploration shadow step failed; data is still committed"
else
  echo "warning: tests failed; exploration shadow step skipped"
fi

# Claim 4 runs only when the Alpaca paper keys are in the environment. The
# code refuses any base URL other than the paper endpoint. Use either this
# script or the GitHub Actions workflow (.github/workflows/daily.yml), not both.
if [ -n "${APCA_API_KEY_ID:-}" ] && [ -n "${APCA_API_SECRET_KEY:-}" ]; then
  export APCA_API_BASE_URL="https://paper-api.alpaca.markets"
  if uv run pytest -q; then
    uv run compute-curve claim4 evaluate && uv run compute-curve claim4 daily \
      || echo "warning: claim 4 step failed; data is still committed"
  else
    echo "warning: tests failed; claim 4 skipped"
  fi
fi

git add data/raw data/collection_log.jsonl reports
if ! git diff --cached --quiet; then
  git commit --quiet -m "Daily snapshot $(date -u +%Y-%m-%d)"
  if [ "${COMPUTE_CURVE_PUSH:-1}" = "1" ]; then
    git push --quiet
  fi
fi
