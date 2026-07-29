#!/usr/bin/env bash
#
# Pull the course model roster defined in models/roster.yaml.
#
# Reads tags straight from the roster so this script never drifts from the
# documented list. Optional models (the stretch rung) are skipped unless you
# pass --include-optional, because they may not fit on a 16 GB machine.
#
# Usage:
#   bash scripts/pull-roster.sh                  # core roster
#   bash scripts/pull-roster.sh --include-optional
#   bash scripts/pull-roster.sh --dry-run        # print what it would pull

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ROSTER="$REPO_ROOT/models/roster.yaml"

INCLUDE_OPTIONAL=0
DRY_RUN=0
for arg in "$@"; do
  case "$arg" in
    --include-optional) INCLUDE_OPTIONAL=1 ;;
    --dry-run)          DRY_RUN=1 ;;
    -h|--help)          sed -n '2,14p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown option: $arg" >&2; exit 2 ;;
  esac
done

if [ ! -r "$ROSTER" ]; then
  echo "error: cannot read $ROSTER" >&2
  exit 1
fi

if ! command -v ollama >/dev/null 2>&1; then
  echo "error: ollama is not installed." >&2
  echo "  See modules/01-local-model-lab/README.md for the install step." >&2
  exit 1
fi

if ! curl -fsS --max-time 3 http://localhost:11434/api/version >/dev/null 2>&1; then
  echo "error: ollama is not responding on http://localhost:11434" >&2
  echo "  Start it with:  ollama serve" >&2
  exit 1
fi

# Walk the `models:` list. Each entry starts with "  - id:" and we care about
# the ollama_tag plus whether it is marked optional. Awk keeps this dependency
# free -- no yq required just to read six strings.
mapfile -t ENTRIES < <(
  awk -v want_optional="$INCLUDE_OPTIONAL" '
    /^models:/        { in_models = 1; next }
    /^[a-z_]+:/       { if ($1 != "models:") in_models = 0 }
    !in_models        { next }
    /^  - id:/        { if (tag != "") emit(); tag = ""; optional = 0 }
    /^    ollama_tag:/ { gsub(/"/, "", $2); tag = $2 }
    /^    optional:/   { if ($2 == "true") optional = 1 }
    END               { if (tag != "") emit() }
    function emit() {
      if (optional == 0 || want_optional == 1) print tag
    }
  ' "$ROSTER"
)

if [ "${#ENTRIES[@]}" -eq 0 ]; then
  echo "error: no model tags parsed from $ROSTER" >&2
  exit 1
fi

echo "Models to pull (${#ENTRIES[@]}):"
for tag in "${ENTRIES[@]}"; do
  echo "  $tag"
done
echo

if [ "$INCLUDE_OPTIONAL" -eq 0 ]; then
  echo "(Stretch models skipped. Re-run with --include-optional to add them.)"
  echo
fi

if [ "$DRY_RUN" -eq 1 ]; then
  echo "--dry-run: nothing pulled."
  exit 0
fi

FAILED=()
for tag in "${ENTRIES[@]}"; do
  echo "==> ollama pull $tag"
  if ! ollama pull "$tag"; then
    echo "    FAILED: $tag" >&2
    FAILED+=("$tag")
  fi
  echo
done

if [ "${#FAILED[@]}" -gt 0 ]; then
  echo "Failed to pull ${#FAILED[@]} model(s):" >&2
  for tag in "${FAILED[@]}"; do
    echo "  $tag" >&2
  done
  cat >&2 <<'EOF'

A tag that 404s usually means the roster is stale rather than that anything is
broken -- vendors rename and retag models constantly.

  1. Check the real tag at https://ollama.com/library
  2. Fix ollama_tag in models/roster.yaml and set tag_verified: true
  3. Re-render the docs:  uv run scripts/render-roster.py

Or run /update-models to have that done for you.
EOF
  exit 1
fi

echo "All models pulled. Disk used by Ollama:"
ollama list
