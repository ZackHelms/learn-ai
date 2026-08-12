#!/usr/bin/env bash
# run.sh - generate and score eval03 candidates with bare headless Claude Code.
# The model receives PROMPT.md + the defective file on stdin, tools disabled,
# empty cwd - it must repair by reading, not by running.
#
# Usage: ./run.sh [-m model] [-e effort] [-f] id [id ...]
#   (aliases haiku45/sonnet5/opus5/fable5; default haiku45 low; ids yours,
#    suggested scheme matches eval01/eval04: r1 = haiku low, u5 = fable max)
#
# Per id: runs/<id>.txt (reply), runs/<id>.gen.json (cost envelope),
# runs/<id>.eval.json (score) + a paste-ready RESULTS.md row.
#
# Any model works:  cat PROMPT.md ashfall-defective-v1.html | ollama run <tag>
#                   > runs/local1.txt && ./eval_repair.py runs/local1.txt   # untested here
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUNS_DIR="$SCRIPT_DIR/runs"
MODEL="claude-haiku-4-5"; EFFORT="low"; FORCE=0
MAX_ATTEMPTS="${MAX_ATTEMPTS:-2}"

while getopts 'm:e:fh' opt; do
  case "$opt" in
    m) MODEL="$OPTARG" ;;
    e) EFFORT="$OPTARG" ;;
    f) FORCE=1 ;;
    h) sed -n '2,13p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) exit 1 ;;
  esac
done
shift $((OPTIND - 1))
[ "$#" -ge 1 ] || { echo "usage: ./run.sh [-m model] [-e effort] [-f] id..." >&2; exit 1; }
case "$MODEL" in
  haiku45|haiku) MODEL="claude-haiku-4-5" ;;
  sonnet5|sonnet) MODEL="claude-sonnet-5" ;;
  opus5|opus) MODEL="claude-opus-5" ;;
  fable5|fable) MODEL="claude-fable-5" ;;
esac
command -v claude >/dev/null || { echo "error: claude CLI not found" >&2; exit 1; }
command -v jq >/dev/null || { echo "error: jq not found" >&2; exit 1; }
mkdir -p "$RUNS_DIR"

PROMPT_TMP="$(mktemp)"; trap 'rm -f "$PROMPT_TMP"' EXIT
cat "$SCRIPT_DIR/PROMPT.md" "$SCRIPT_DIR/ashfall-defective-v1.html" > "$PROMPT_TMP"

fmt_time() { echo "$(($1 / 60))m$(($1 % 60))s"; }
fmt_tok()  { awk -v n="$1" 'BEGIN { if (n >= 1000) printf "%.1fk", n/1000; else printf "%d", n }'; }

fails=0
for id in "$@"; do
  if [ "$FORCE" -ne 1 ] && [ -e "$RUNS_DIR/$id.txt" ]; then
    echo "[$id] SKIP: runs/$id.txt exists (use -f)" >&2; continue
  fi
  ok=0
  for attempt in $(seq 1 "$MAX_ATTEMPTS"); do
    job="$(mktemp -d)"
    started="$(date +"%Y-%m-%d_%H:%M:%S_%Z")"
    t0="$(date +%s)"
    echo "[$id] started $started ($MODEL, effort=$EFFORT, attempt $attempt/$MAX_ATTEMPTS)" >&2
    ( cd "$job" && claude -p --model "$MODEL" --effort "$EFFORT" --tools "" \
        --permission-mode dontAsk --no-session-persistence \
        --output-format json < "$PROMPT_TMP" ) > "$job/result.json" 2> "$job/stderr.log"
    rc=$?; wall=$(( $(date +%s) - t0 ))
    if [ "$rc" -eq 0 ] \
       && jq -e '.type == "result" and (.is_error | not)' "$job/result.json" >/dev/null 2>&1 \
       && [ -n "$(jq -r '.result // empty' "$job/result.json")" ]; then
      jq -r '.result' "$job/result.json" > "$RUNS_DIR/$id.txt"
      jq -n --arg run "$id" --arg model "$MODEL" --arg effort "$EFFORT" \
        --arg started "$started" --argjson wall "$wall" --argjson attempts "$attempt" \
        --slurpfile claude "$job/result.json" \
        '{run:$run, model:$model, effort:$effort, started:$started,
          wall_seconds:$wall, attempts:$attempts, claude:$claude[0]}' \
        > "$RUNS_DIR/$id.gen.json"
      rm -rf "$job"; ok=1; break
    fi
    echo "[$id] attempt $attempt FAIL after $(fmt_time "$wall") (rc=$rc)" >&2
    tail -n 3 "$job/stderr.log" >&2 2>/dev/null || true
    rm -rf "$job"
  done
  if [ "$ok" -ne 1 ]; then
    echo "[$id] giving up after $MAX_ATTEMPTS attempts" >&2
    fails=$((fails + 1)); continue
  fi

  uv run "$SCRIPT_DIR/eval_repair.py" "$RUNS_DIR/$id.txt"

  g="$RUNS_DIR/$id.gen.json"; e="$RUNS_DIR/$id.eval.json"
  read -r started wall inp crd cwr out cost <<EOF2
$(jq -r '[.started, .wall_seconds, .claude.usage.input_tokens,
          .claude.usage.cache_read_input_tokens, .claude.usage.cache_creation_input_tokens,
          .claude.usage.output_tokens, (.claude.total_cost_usd // 0)] | @tsv' "$g")
EOF2
  read -r ap dp gp mp tot touched <<EOF2
$(jq -r '[.apply_pts, .defect_pts, .guard_pts, .minimality_pts, .total, .touched_lines] | @tsv' "$e")
EOF2
  echo >&2
  echo "RESULTS.md row (eval03 section):" >&2
  printf '| %s | Claude Code (bare) | %s (%s) | %s | %s | $%.4f | %s + %s + %s + %s = %s | %s touched | %s in, %s out |\n' \
    "$started" "$MODEL" "$EFFORT" "$id" "$(fmt_time "$wall")" "$cost" \
    "$ap" "$dp" "$gp" "$mp" "$tot" "$touched" \
    "$(fmt_tok "$inp")" "$(fmt_tok "$out")"
done
[ "$fails" -eq 0 ]
