#!/usr/bin/env bash
# grade.sh - run the ASHFALL OUTPOST AI grader over candidate HTML files using
# headless Claude Code ("claude -p") with ALL tools disabled.
#
# Why this exists: interactive grading sessions kept exploring the repo
# (eval_ashfall.py, old results) before reading GRADER_PROMPT.md rule 11, then
# "fixed" the bias by delegating to a subagent - silently swapping the grader
# model. This wrapper makes peeking impossible instead of merely forbidden:
#
#   - the grader receives GRADER_PROMPT.md + the candidate HTML on stdin, nothing else
#   - --tools "" removes every tool: no file reads, no shell, no subagents
#   - each job runs from an empty temp dir: no CLAUDE.md, no repo settings, no memory
#   - the model never sees the candidate's filename (stronger blinding than agentic runs)
#
# Parallel jobs share nothing except the server-side prompt cache, which reuses
# identical prefix tokens for speed/cost and cannot carry content between requests.
#
# Auth: whatever "claude" is logged in as (subscription plan or API key).

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROMPT_FILE="$SCRIPT_DIR/GRADER_PROMPT.md"

MODEL="claude-sonnet-5"
EFFORT="high"
SUFFIX=""
JOBS=1
FORCE=0

usage() {
  cat <<'EOF'
Usage: ./grade.sh [-m model] [-e effort] [-s suffix] [-j jobs] [-f] candidate.html [...]

  -m model   grader model (default: claude-sonnet-5)
  -e effort  low|medium|high|xhigh|max (default: high)
  -s suffix  appended to the candidate stem for the output name:
             "-s b" grades runs/r01.html into runs/r01b.ai.json (default: none)
  -j jobs    grade up to N candidates in parallel (default: 1)
  -f         overwrite existing output files

Examples:
  ./grade.sh -s b runs/r01.html
  ./grade.sh -s c -j 5 runs/r01.html runs/r02.html runs/r03.html runs/r04.html runs/r05.html

Record model + effort + grader-prompt version in the RESULTS.md Grader column;
scores are only comparable when the grader is held fixed (see README.md).
EOF
}

while getopts 'm:e:s:j:fh' opt; do
  case "$opt" in
    m) MODEL="$OPTARG" ;;
    e) EFFORT="$OPTARG" ;;
    s) SUFFIX="$OPTARG" ;;
    j) JOBS="$OPTARG" ;;
    f) FORCE=1 ;;
    h) usage; exit 0 ;;
    *) usage; exit 1 ;;
  esac
done
shift $((OPTIND - 1))

if [ "$#" -lt 1 ]; then usage; exit 1; fi
if [ ! -f "$PROMPT_FILE" ]; then echo "error: missing $PROMPT_FILE" >&2; exit 1; fi
if ! command -v claude >/dev/null 2>&1; then echo "error: claude CLI not found" >&2; exit 1; fi
case "$JOBS" in ''|*[!0-9]*|0) echo "error: -j must be a positive integer" >&2; exit 1 ;; esac

WORKDIR="$(mktemp -d)"
FAIL_DIR="$WORKDIR/failed"
mkdir -p "$FAIL_DIR"
trap 'rm -rf "$WORKDIR"' EXIT

echo "grader: model=$MODEL effort=$EFFORT suffix='$SUFFIX' jobs=$JOBS" >&2

grade_one() {
  local candidate="$1"
  local tag stem out job_dir reply errlog rc t0 t1

  tag="$(basename "$candidate")"
  if [ ! -f "$candidate" ]; then
    echo "[$tag] FAIL: candidate not found" >&2
    : > "$FAIL_DIR/$(echo "$candidate" | tr '/' '_')"
    return 1
  fi
  stem="${candidate%.html}"
  out="${stem}${SUFFIX}.ai.json"
  if [ -e "$out" ] && [ "$FORCE" -ne 1 ]; then
    echo "[$tag] SKIP: $out exists (use -f to overwrite)" >&2
    : > "$FAIL_DIR/$(echo "$candidate" | tr '/' '_')"
    return 1
  fi

  job_dir="$WORKDIR/$(echo "$candidate" | tr '/' '_').d"
  mkdir -p "$job_dir"
  reply="$job_dir/reply.txt"
  errlog="$job_dir/stderr.log"

  # Assemble the full grading prompt: rules first, candidate underneath.
  {
    cat "$PROMPT_FILE"
    printf '\n\n===== CANDIDATE HTML - grade everything below this line =====\n\n'
    cat "$candidate"
  } > "$job_dir/prompt.txt"

  echo "[$tag] grading -> $out" >&2
  t0="$(date +%s)"
  # Empty cwd on purpose: no CLAUDE.md, no project settings, no repo memory.
  (
    cd "$job_dir" &&
    claude -p --model "$MODEL" --effort "$EFFORT" --tools "" \
      --no-session-persistence < prompt.txt
  ) > "$reply" 2> "$errlog"
  rc=$?
  t1="$(date +%s)"

  if [ "$rc" -ne 0 ] || [ ! -s "$reply" ]; then
    echo "[$tag] FAIL: claude exited $rc after $((t1 - t0))s; stderr tail:" >&2
    tail -n 5 "$errlog" >&2 || true
    : > "$FAIL_DIR/$(echo "$candidate" | tr '/' '_')"
    return 1
  fi

  mv "$reply" "$out"
  if grep -q '```json' "$out"; then
    echo "[$tag] OK -> $out ($((t1 - t0))s)" >&2
  else
    echo "[$tag] WARN -> $out ($((t1 - t0))s): no \`\`\`json block found; merge will likely fail - inspect and regrade with -f" >&2
    : > "$FAIL_DIR/$(echo "$candidate" | tr '/' '_')"
    return 1
  fi
}

for candidate in "$@"; do
  if [ "$JOBS" -gt 1 ]; then
    while [ "$(jobs -rp | wc -l)" -ge "$JOBS" ]; do
      wait -n
    done
    grade_one "$candidate" &
  else
    grade_one "$candidate"
  fi
done
wait

failures="$(find "$FAIL_DIR" -type f | wc -l)"
total="$#"
echo "done: $((total - failures))/$total ok" >&2
[ "$failures" -eq 0 ]
