#!/usr/bin/env bash
# Daily cycle for compute-curve: collect, rebuild the index, run the paper
# account, evaluate, and commit the new immutable raw data and reports.
#
# Run it once a day, either from the GitHub Actions workflow
# (.github/workflows/daily.yml) or from cron on your own machine. Use one
# scheduler, not both, so two runs never race on the same branch.
#
# Idempotent: a second run on the same UTC day collects nothing, rewrites
# identical reports, and makes no commit.
#
# Environment:
#   COMPUTE_CURVE_PUSH=0   commit locally without pushing (default 1)
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_DIR"

branch="${GITHUB_REF_NAME:-$(git rev-parse --abbrev-ref HEAD)}"
if [ "$branch" = "HEAD" ]; then
  echo "error: detached HEAD; check out a branch first" >&2
  exit 1
fi

git pull --ff-only --quiet origin "$branch" || echo "warning: git pull failed; continuing with local copy"

uv sync --quiet
uv run compute-curve daily
uv run compute-curve evaluate

git add data/raw data/collection_log.jsonl reports
if git diff --cached --quiet; then
  echo "no new data or report changes; nothing to commit"
  exit 0
fi
git commit --quiet -m "Daily snapshot $(date -u +%Y-%m-%d)"

if [ "${COMPUTE_CURVE_PUSH:-1}" != "1" ]; then
  echo "committed locally; push disabled"
  exit 0
fi

# Retry if the branch moved during the run (for example a commit pushed
# meanwhile). Raw files are new and append-only, so a rebase normally applies
# cleanly; a real conflict stops the run with an error instead of forcing.
for attempt in 1 2 3; do
  if git push --quiet origin "HEAD:${branch}"; then
    echo "pushed to ${branch}"
    exit 0
  fi
  echo "push rejected (attempt ${attempt}); rebasing on origin/${branch}" >&2
  if ! git pull --rebase --quiet origin "$branch"; then
    git rebase --abort || true
    echo "error: rebase conflict; resolve by hand" >&2
    exit 1
  fi
  sleep $((attempt * 5))
done
echo "error: push failed after 3 attempts" >&2
exit 1
