#!/usr/bin/env bash
# run.sh - generate and score eval04 candidates using headless Claude Code
# ("claude -p") with all tools disabled, from an empty temp dir, so the model
# sees PROMPT.md and nothing else (same blinding as eval01's grade.sh).
#
# Usage: ./run.sh [-m model] [-e effort] [-f] id [id ...]
#
#   id       run id, yours to choose. Suggested scheme (matches eval01):
#            letter = model (r=haiku45 s=sonnet5 t=opus5 u=fable5),
#            digit = effort (low=1 medium=2 high=3 xhigh=4 max=5),
#            optional trailing letter for repeats: r1, r1b, u5 ...
#   -m       model (default: claude-haiku-4-5); aliases haiku45/sonnet5/
#            opus5/fable5 accepted
#   -e       effort: low|medium|high|xhigh|max (default: low)
#   -f       overwrite existing runs/<id>.*
#
# Per id this writes runs/<id>.txt (the reply), runs/<id>.gen.json (claude
# result envelope + config), runs/<id>.eval.json (the score), and prints a
# paste-ready row for ../RESULTS.md. Harness failures (nonzero exit, error
# envelope, empty reply) are retried once; model output that merely scores
# badly is NOT a failure - it is a result.
#
# Any other model works too - the contract is just "PROMPT.md in, text out":
#   ollama run <tag> < PROMPT.md > runs/local1.txt   # untested here
#   ./eval_constraints.py runs/local1.txt
#
# Auth: whatever "claude" is logged in as (subscription plan or API key).

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROMPT_FILE="$SCRIPT_DIR/PROMPT.md"
RUNS_DIR="$SCRIPT_DIR/runs"

MODEL="claude-haiku-4-5"
EFFORT="low"
FORCE=0
MAX_ATTEMPTS="${MAX_ATTEMPTS:-2}"

usage() { sed -n '2,20p' "$0" | sed 's/^# \{0,1\}//'; }

while getopts 'm:e:fh' opt; do
  case "$opt" in
    m) MODEL="$OPTARG" ;;
    e) EFFORT="$OPTARG" ;;
    f) FORCE=1 ;;
    h) usage; exit 0 ;;
    *) usage; exit 1 ;;
  esac
done
shift $((OPTIND - 1))
[ "$#" -ge 1 ] || { usage; exit 1; }

case "$MODEL" in
  haiku45|haiku)  MODEL="claude-haiku-4-5" ;;
  sonnet5|sonnet) MODEL="claude-sonnet-5" ;;
  opus5|opus)     MODEL="claude-opus-5" ;;
  fable5|fable)   MODEL="claude-fable-5" ;;
esac
case "$EFFORT" in low|medium|high|xhigh|max) ;;
  *) echo "error: bad effort '$EFFORT'" >&2; exit 1 ;;
esac

command -v claude >/dev/null || { echo "error: claude CLI not found" >&2; exit 1; }
command -v jq >/dev/null || { echo "error: jq not found" >&2; exit 1; }
[ -f "$PROMPT_FILE" ] || { echo "error: missing $PROMPT_FILE" >&2; exit 1; }
mkdir -p "$RUNS_DIR"

fmt_time() { echo "$(($1 / 60))m$(($1 % 60))s"; }
fmt_tok()  { awk -v n="$1" 'BEGIN { if (n >= 1000) printf "%.1fk", n/1000; else printf "%d", n }'; }

fail_total=0
for id in "$@"; do
  if [ "$FORCE" -ne 1 ] && [ -e "$RUNS_DIR/$id.txt" ]; then
    echo "[$id] SKIP: runs/$id.txt exists (use -f to overwrite)" >&2
    continue
  fi
  ok=0
  for attempt in $(seq 1 "$MAX_ATTEMPTS"); do
    job="$(mktemp -d)"
    started="$(date +"%Y-%m-%d_%H:%M:%S_%Z")"
    t0="$(date +%s)"
    echo "[$id] started $started ($MODEL, effort=$EFFORT, attempt $attempt/$MAX_ATTEMPTS)" >&2
    (
      cd "$job" &&
      claude -p --model "$MODEL" --effort "$EFFORT" --tools "" \
        --permission-mode dontAsk --no-session-persistence \
        --output-format json < "$PROMPT_FILE"
    ) > "$job/result.json" 2> "$job/stderr.log"
    rc=$?
    wall=$(( $(date +%s) - t0 ))
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
      rm -rf "$job"
      ok=1
      break
    fi
    echo "[$id] attempt $attempt FAIL after $(fmt_time "$wall") (rc=$rc)" >&2
    tail -n 3 "$job/stderr.log" >&2 2>/dev/null || true
    rm -rf "$job"
  done
  if [ "$ok" -ne 1 ]; then
    echo "[$id] giving up after $MAX_ATTEMPTS attempts" >&2
    fail_total=$((fail_total + 1))
    continue
  fi

  python3 "$SCRIPT_DIR/eval_constraints.py" "$RUNS_DIR/$id.txt"

  g="$RUNS_DIR/$id.gen.json"
  e="$RUNS_DIR/$id.eval.json"
  read -r started wall inp crd cwr out cost <<EOF2
$(jq -r '[.started, .wall_seconds, .claude.usage.input_tokens,
          .claude.usage.cache_read_input_tokens, .claude.usage.cache_creation_input_tokens,
          .claude.usage.output_tokens, (.claude.total_cost_usd // 0)] | @tsv' "$g")
EOF2
  read -r satp flagp total <<EOF2
$(jq -r '[.sat_pts, .flag_pts, .total] | @tsv' "$e")
EOF2
  echo >&2
  echo "RESULTS.md row (eval04 section):" >&2
  printf '| %s | Claude Code (bare) | %s (%s) | %s | %s | $%.4f | %s + %s = %s | %s input, %s output, %s cache read, %s cache write |\n' \
    "$started" "$MODEL" "$EFFORT" "$id" "$(fmt_time "$wall")" "$cost" \
    "$satp" "$flagp" "$total" \
    "$(fmt_tok "$inp")" "$(fmt_tok "$out")" "$(fmt_tok "$crd")" "$(fmt_tok "$cwr")"
done
[ "$fail_total" -eq 0 ]
