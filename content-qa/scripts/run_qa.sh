#!/usr/bin/env bash
# Run the seo-geo-qa QA runner on a content draft.
# Usage: ./run_qa.sh path/to/article.md --keyword "primary keyword" [extra args...]
#
# Optional: pass --config path/to/seo-qa-config.json for project defaults
# (site domain, report dir, QA thresholds — see seo-geo-qa/references/configuration.md)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SUITE_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
RUNNER="$SUITE_ROOT/seo-geo-qa/scripts/seo_qa_runner.py"

if [ ! -f "$RUNNER" ]; then
    echo "Error: seo-geo-qa runner not found at $RUNNER" >&2
    exit 1
fi

exec python3 "$RUNNER" "$@"
