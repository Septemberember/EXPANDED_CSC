#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

if ! command -v dot >/dev/null 2>&1; then
  echo "Graphviz dot command not found. Please install Graphviz first." >&2
  exit 1
fi

render_dot() {
  local dot_file="$1"
  [ -f "$dot_file" ] || return 0
  dot -Tsvg "$dot_file" -o "${dot_file%.dot}.svg"
  dot -Tpdf "$dot_file" -o "${dot_file%.dot}.pdf"
  dot -Tpng -Gdpi=200 "$dot_file" -o "${dot_file%.dot}.png"
}

render_dot "SpfTreeSearch_cct.dot"
render_dot "SpfTreeSearch_cct_tbfv_fault.dot"

echo "Rendered CCT artifacts in $(pwd)"
