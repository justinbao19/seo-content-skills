#!/usr/bin/env bash
# Thin wrapper: calls the generic seo-geo-qa runner with Filo-specific config.
# Usage: ./run_qa.sh path/to/article.md --keyword "best email apps" [extra args...]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
GENERIC_RUNNER="$WORKSPACE_ROOT/skills/seo-geo-qa/scripts/seo_qa_runner.py"
FILO_CONFIG="$WORKSPACE_ROOT/filomail/seo-qa-config.json"

if [ ! -f "$GENERIC_RUNNER" ]; then
    echo "Error: Generic seo-geo-qa runner not found at $GENERIC_RUNNER" >&2
    echo "Install seo-geo-qa skill first: clawhub install seo-geo-qa" >&2
    exit 1
fi

exec python3 "$GENERIC_RUNNER" --config "$FILO_CONFIG" "$@"
