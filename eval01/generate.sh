#!/usr/bin/env bash
# generate.sh - generate ASHFALL OUTPOST candidates across all effort levels of
# one model, in parallel, using headless Claude Code ("claude -p") in a bare
# environment. Companion to grade.sh (which judges what this script produces).
#
# Why this exists: generating candidates in a regular interactive session loads
# CLAUDE.md/AGENTS.md, user skills, plugins, and project memory - all of which
# bias what should be a bare-bones eval of model + effort level. Each run here:
#
#   - uses --safe-mode: no CLAUDE.md, no skills, no plugins, no hooks, no MCP
#     servers, no custom agents (auth, model selection, and built-in tools
#     work normally - unlike --bare, which would break subscription auth)
#   - runs from an empty temp dir: no project context, no auto-memory
#   - gets the prompt on stdin, byte-identical for every run (output is always
#     ./game.html, renamed to runs/<id>.html afterwards) so all runs share the
#     same server-side prompt-cache prefix
#   - uses --exclude-dynamic-system-prompt-sections so the per-run cwd moves
#     out of the system prompt, keeping the cached prefix identical across runs
#   - uses --permission-mode acceptEdits: file writes in the temp dir are
#     auto-approved; anything else (Bash, web) is auto-denied, identically for
#     every effort level. (Do NOT use "auto" here: headless, its classifier
#     can silently drop the write while the model claims success.)
#
# Because of the bare environment, these runs are NOT directly comparable to
# earlier candidates generated in interactive sessions with full context.
#
# Run IDs: <prefix><digit><suffix>, digit = low=1 medium=2 high=3 xhigh=4 max=5
#   ./generate.sh sonnet5 r1   ->  runs/r11.html (low) ... runs/r15.html (max)
# Launch order is max first, then xhigh/high/medium/low, GAP seconds apart:
# the first request writes the prompt cache (an entry is readable once the
# first response starts streaming), the rest read it.
#
# Per run this writes runs/<id>.html and runs/<id>.gen.json (started datetime,
# wall time, tokens, estimated API cost from Claude Code's total_cost_usd).
# When all runs finish it prints a summary table and paste-ready RESULTS.md
# rows. Failed runs keep their scratch dir under runs/.gen-work/<id>/.
#
# Auth: whatever "claude" is logged in as (subscription plan or API key).

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROMPT_FILE="${PROMPT_FILE:-$SCRIPT_DIR/make-game-ashfall-outpost.prompt.md}"
RUNS_DIR="$SCRIPT_DIR/runs"
WORK_ROOT="$RUNS_DIR/.gen-work"

GAP=20
EFFORTS="max xhigh high medium low"
SUFFIX=""
FORCE=0
DRY=0

usage() {
  cat <<'EOF'
Usage: ./generate.sh [-g gap] [-e "efforts"] [-s suffix] [-f] [-n] model prefix

  model      sonnet5 | opus5 | haiku45 | fable5 | any full model id
  prefix     run-id prefix, e.g. r1 (a trailing * is ignored, so r1* works)

  -g gap     seconds between staggered starts (default: 20)
  -e list    space-separated effort levels to run (default: all five;
             launch order = list order), e.g. -e "max low"
  -s suffix  appended after the digit: -s a -> runs/r11a.html ... r15a.html
  -f         overwrite existing runs/<id>.html / <id>.gen.json
  -n         dry run: print the plan and the claude command, start nothing

Run IDs map effort -> digit: low=1 medium=2 high=3 xhigh=4 max=5.
PROMPT_FILE=<path> overrides the prompt (default: make-game-ashfall-outpost.prompt.md).

Examples:
  ./generate.sh sonnet5 r1          # r11..r15, all five efforts in parallel
  ./generate.sh -s a opus5 r2       # r21a..r25a
  ./generate.sh -e "xhigh" -f sonnet5 r1   # redo just r14

Afterwards:
  ./eval_ashfall.py runs/r11.html --runtime     # deterministic half
  ./grade.sh -s a -j 5 runs/r1[1-5].html        # AI-judged half
EOF
}

while getopts 'g:e:s:fnh' opt; do
  case "$opt" in
    g) GAP="$OPTARG" ;;
    e) EFFORTS="$OPTARG" ;;
    s) SUFFIX="$OPTARG" ;;
    f) FORCE=1 ;;
    n) DRY=1 ;;
    h) usage; exit 0 ;;
    *) usage; exit 1 ;;
  esac
done
shift $((OPTIND - 1))
if [ "$#" -ne 2 ]; then usage; exit 1; fi

MODEL_ARG="$1"
PREFIX="${2%\*}"   # tolerate "r1*"

case "$MODEL_ARG" in
  sonnet5|sonnet)  MODEL_ID="claude-sonnet-5" ;;
  opus5|opus)      MODEL_ID="claude-opus-5" ;;
  haiku45|haiku)   MODEL_ID="claude-haiku-4-5" ;;
  fable5|fable)    MODEL_ID="claude-fable-5" ;;
  *)               MODEL_ID="$MODEL_ARG" ;;   # full ids pass through
esac

effort_digit() {
  case "$1" in
    low) echo 1 ;; medium) echo 2 ;; high) echo 3 ;; xhigh) echo 4 ;; max) echo 5 ;;
    *) echo "error: unknown effort '$1' (low|medium|high|xhigh|max)" >&2; return 1 ;;
  esac
}

fmt_time() { echo "$(($1 / 60))m$(($1 % 60))s"; }
fmt_tok()  { awk -v n="$1" 'BEGIN { if (n >= 1000) printf "%.1fk", n/1000; else printf "%d", n }'; }

if ! command -v claude >/dev/null 2>&1; then echo "error: claude CLI not found" >&2; exit 1; fi
if ! command -v jq >/dev/null 2>&1; then echo "error: jq not found" >&2; exit 1; fi
if [ ! -f "$PROMPT_FILE" ]; then echo "error: missing prompt $PROMPT_FILE" >&2; exit 1; fi
case "$GAP" in ''|*[!0-9]*) echo "error: -g must be a non-negative integer" >&2; exit 1 ;; esac

# Resolve run ids up front; refuse to clobber existing candidates unless -f.
IDS=""
for effort in $EFFORTS; do
  digit="$(effort_digit "$effort")" || exit 1
  id="${PREFIX}${digit}${SUFFIX}"
  IDS="$IDS $id"
  if [ "$FORCE" -ne 1 ] && { [ -e "$RUNS_DIR/$id.html" ] || [ -e "$RUNS_DIR/$id.gen.json" ]; }; then
    echo "error: runs/$id.html or runs/$id.gen.json exists (use -f, or a -s suffix)" >&2
    exit 1
  fi
done

CLAUDE_FLAGS="--safe-mode --permission-mode acceptEdits --no-session-persistence --exclude-dynamic-system-prompt-sections --output-format json"

echo "generate: model=$MODEL_ID efforts=[$EFFORTS] ids=[${IDS# }] gap=${GAP}s prompt=$(basename "$PROMPT_FILE")" >&2

if [ "$DRY" -eq 1 ]; then
  for effort in $EFFORTS; do
    id="${PREFIX}$(effort_digit "$effort")${SUFFIX}"
    echo "would run: [$id] claude -p --model $MODEL_ID --effort $effort $CLAUDE_FLAGS < <prompt>  ->  runs/$id.html" >&2
  done
  exit 0
fi

mkdir -p "$WORK_ROOT"

# Assemble the prompt once: the eval prompt, then a fixed output-location
# instruction. Identical bytes for every run keeps the cache prefix shared;
# the digit-specific filename is applied by the rename below, not the model.
PROMPT_TMP="$(mktemp)"
trap 'rm -f "$PROMPT_TMP"' EXIT
trap 'echo "[generate] interrupted - killing runs" >&2; kill 0' INT TERM
{
  cat "$PROMPT_FILE"
  printf '\n\nInstead of replying with a code block, save the complete single-file HTML output to `./game.html` in the current working directory. Create no other files.\n'
} > "$PROMPT_TMP"

run_one() {
  local effort="$1" id="$2"
  local job="$WORK_ROOT/$id"
  rm -rf "$job"
  mkdir -p "$job"

  local started ts0 ts1 rc wall
  started="$(date +"%Y-%m-%d_%H:%M:%S_%Z")"
  ts0="$(date +%s)"
  echo "[$id] started $started ($MODEL_ID, effort=$effort)" >&2

  # shellcheck disable=SC2086  # CLAUDE_FLAGS is a fixed flag list
  (
    cd "$job" &&
    claude -p --model "$MODEL_ID" --effort "$effort" $CLAUDE_FLAGS < "$PROMPT_TMP"
  ) > "$job/result.json" 2> "$job/stderr.log"
  rc=$?
  ts1="$(date +%s)"
  wall=$((ts1 - ts0))

  if [ "$rc" -ne 0 ] || ! jq -e '.type == "result" and (.is_error | not)' "$job/result.json" >/dev/null 2>&1; then
    echo "[$id] FAIL after $(fmt_time "$wall"): claude exited $rc; kept $job/ - stderr tail:" >&2
    tail -n 5 "$job/stderr.log" >&2 || true
    : > "$WORK_ROOT/$id.fail"
    return 1
  fi

  local html="$job/game.html"
  if [ ! -f "$html" ]; then
    local candidates=( "$job"/*.html )
    if [ "${#candidates[@]}" -eq 1 ] && [ -f "${candidates[0]}" ]; then
      html="${candidates[0]}"
      echo "[$id] WARN: model wrote $(basename "$html") instead of game.html; using it" >&2
    else
      echo "[$id] FAIL after $(fmt_time "$wall"): no game.html produced; kept $job/" >&2
      : > "$WORK_ROOT/$id.fail"
      return 1
    fi
  fi

  mv "$html" "$RUNS_DIR/$id.html"
  jq -n \
    --arg run "$id" --arg model "$MODEL_ID" --arg model_arg "$MODEL_ARG" \
    --arg effort "$effort" --arg started "$started" --argjson wall "$wall" \
    --slurpfile claude "$job/result.json" \
    '{run: $run, model: $model, model_arg: $model_arg, effort: $effort,
      started: $started, wall_seconds: $wall, claude: $claude[0]}' \
    > "$RUNS_DIR/$id.gen.json"

  local cost
  cost="$(jq -r '.total_cost_usd // empty' "$job/result.json")"
  echo "[$id] OK -> runs/$id.html ($(fmt_time "$wall"), \$${cost:-n/a})" >&2
  rm -rf "$job"
  : > "$WORK_ROOT/$id.ok"
}

# Launch in EFFORTS order (max first by default), staggered so later runs can
# read the prompt cache the first run writes.
first=1
for effort in $EFFORTS; do
  if [ "$first" -eq 1 ]; then first=0; else sleep "$GAP"; fi
  id="${PREFIX}$(effort_digit "$effort")${SUFFIX}"
  rm -f "$WORK_ROOT/$id.ok" "$WORK_ROOT/$id.fail"
  run_one "$effort" "$id" &
done
wait

# Summarize in digit order (low -> max), only the efforts that ran.
echo >&2
printf '%-8s %-8s %-8s %-8s %6s %9s %10s %10s %9s %10s\n' \
  run effort status time api_min turns input cache_rd cache_wr output >&2
total_cost=0
ok=0; failed=0
for effort in low medium high xhigh max; do
  case " $EFFORTS " in *" $effort "*) ;; *) continue ;; esac
  id="${PREFIX}$(effort_digit "$effort")${SUFFIX}"
  if [ ! -e "$WORK_ROOT/$id.ok" ]; then
    printf '%-8s %-8s %-8s\n' "$id" "$effort" FAILED >&2
    failed=$((failed + 1))
    continue
  fi
  ok=$((ok + 1))
  g="$RUNS_DIR/$id.gen.json"
  read -r wall api_ms turns inp crd cwr out cost <<EOF2
$(jq -r '[.wall_seconds, .claude.duration_api_ms, .claude.num_turns,
          .claude.usage.input_tokens, .claude.usage.cache_read_input_tokens,
          .claude.usage.cache_creation_input_tokens, .claude.usage.output_tokens,
          (.claude.total_cost_usd // 0)] | @tsv' "$g")
EOF2
  total_cost="$(awk -v a="$total_cost" -v b="$cost" 'BEGIN { printf "%.4f", a + b }')"
  printf '%-8s %-8s %-8s %-8s %6s %9s %10s %10s %9s %10s\n' \
    "$id" "$effort" ok "$(fmt_time "$wall")" \
    "$(awk -v m="$api_ms" 'BEGIN { printf "%.1f", m/60000 }')" "$turns" \
    "$(fmt_tok "$inp")" "$(fmt_tok "$crd")" "$(fmt_tok "$cwr")" "$(fmt_tok "$out")" >&2
done
echo >&2
echo "done: $ok ok, $failed failed; total estimated API cost \$$total_cost" >&2

if [ "$ok" -gt 0 ]; then
  echo >&2
  echo "RESULTS.md rows (fill in scores after eval_ashfall.py + grade.sh):" >&2
  for effort in low medium high xhigh max; do
    case " $EFFORTS " in *" $effort "*) ;; *) continue ;; esac
    id="${PREFIX}$(effort_digit "$effort")${SUFFIX}"
    [ -e "$WORK_ROOT/$id.ok" ] || continue
    g="$RUNS_DIR/$id.gen.json"
    read -r started wall inp crd cwr out cost <<EOF2
$(jq -r '[.started, .wall_seconds, .claude.usage.input_tokens,
          .claude.usage.cache_read_input_tokens, .claude.usage.cache_creation_input_tokens,
          .claude.usage.output_tokens, (.claude.total_cost_usd // 0)] | @tsv' "$g")
EOF2
    printf '| %s | Claude Code (bare) | %s (%s) | %s | %s | $%.4f | __ + __ = __ | %s input, %s output, %s cache read, %s cache write ($%.4f) |\n' \
      "$started" "$MODEL_ID" "$effort" "$id" "$(fmt_time "$wall")" "$cost" \
      "$(fmt_tok "$inp")" "$(fmt_tok "$out")" "$(fmt_tok "$crd")" "$(fmt_tok "$cwr")" "$cost"
  done
fi

[ "$failed" -eq 0 ]
