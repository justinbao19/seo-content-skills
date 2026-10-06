#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
QA_DIR="${SEO_QA_SKILL_DIR:-$SCRIPT_DIR/../../seo-geo-qa}"
RUNNER="$QA_DIR/scripts/seo_qa_runner.py"
if [ ! -f "$RUNNER" ]; then
  echo "seo-geo-qa is not available; set SEO_QA_SKILL_DIR to its installed directory. Editorial review can continue with technical checks marked not run." >&2
  exit 2
fi
exec python3 "$RUNNER" "$@"
