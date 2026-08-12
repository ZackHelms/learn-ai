#!/usr/bin/env bash
# grade.sh - run the ASHFALL OUTPOST AI grader over candidates using headless
# Claude Code ("claude -p") with ALL tools disabled. Args are grading-run stems
# in the listscore.py spelling (s11a = candidate runs/s11.html, output
# runs/s11a.ai.json) or plain candidate paths; see usage.
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
#   - the session gets an explicit --permission-mode, so a defaultMode in
#     ~/.claude/settings.json (e.g. "plan") cannot hijack the grader into
#     "writing the grading to the plan file" instead of answering
#   - every reply is vetted with eval_ashfall.load_ai - the same parser
#     listscore.py and --merge use. An unusable reply is retried (MAX_ATTEMPTS
#     at the top of the file), then parked at runs/<stem>.ai.json.rejected with
#     no .ai.json written, so re-running the same sweep re-grades only what is
#     missing (existing outputs SKIP, which is not counted as a failure)
#   - args whose candidate HTML does not exist are reported as ERROR and
#     skipped; the rest are still graded, and the exit code stays nonzero
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
JOBS=5
FORCE=0
MAX_ATTEMPTS="${MAX_ATTEMPTS:-2}"   # tries per grading run before parking the reply as .rejected

usage() {
  cat <<'EOF'
Usage: ./grade.sh [-m model] [-e effort] [-s suffix] [-j jobs] [-f] arg [...]

Each arg is a grading-run stem, or a candidate HTML path:
  s11a            grade runs/s11.html once            -> runs/s11a.ai.json
  s1{1..5}{a..e}  5 grading runs of each of s11..s15  -> runs/s11a.ai.json ...
  runs/s11.html   path form; the -s suffix names the output as before

The trailing letter of a stem is the grading-run suffix - unless a candidate
with that exact name exists (r21a -> runs/r21a.html), matching listscore.py.

  -m model   grader model (default: claude-sonnet-5)
  -e effort  low|medium|high|xhigh|max (default: high)
  -s suffix  default suffix for args that do not carry one (default: none)
  -j jobs    grade up to N in parallel (default: 5)
  -f         overwrite existing output files

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
if ! command -v python3 >/dev/null 2>&1; then echo "error: python3 not found (needed to vet grader replies)" >&2; exit 1; fi
case "$JOBS" in ''|*[!0-9]*|0) echo "error: -j must be a positive integer" >&2; exit 1 ;; esac

WORKDIR="$(mktemp -d)"
FAIL_DIR="$WORKDIR/failed"
SKIP_DIR="$WORKDIR/skipped"
mkdir -p "$FAIL_DIR" "$SKIP_DIR"
trap 'rm -rf "$WORKDIR"' EXIT

reply_has_scores() {
  # Acceptance check for a grader reply: the same parser listscore.py and
  # eval_ashfall.py --merge run later, PLUS completeness - all 13 F and 5 G
  # items must be present. load_ai tolerates skipped items (scored 0) so a
  # human doing a manual --merge is never blocked, but accepting such a reply
  # here silently drags the candidate's average down (set3 r32c: the grader
  # skipped all 13 F items, scoring 5/46 against siblings at 24-25). An
  # incomplete reply is a failed attempt: retry, then park as .rejected.
  PYTHONPATH="$SCRIPT_DIR" python3 -c '
import sys
from eval_ashfall import load_ai
missing = load_ai(sys.argv[1])[3]
if missing:
    raise SystemExit("incomplete grader reply: skipped %s" % ",".join(missing))
' "$1" >/dev/null 2>"$2"
}

echo "grader: model=$MODEL effort=$EFFORT suffix='$SUFFIX' jobs=$JOBS" >&2

resolve_arg() {
  # Map one CLI arg to a candidate + grading suffix (sets RES_CAND, RES_SFX).
  # An existing path or exact runs/<stem>.html keeps the -s default suffix;
  # otherwise a trailing digit-then-letter is split off as the suffix.
  local arg="$1" stem cand
  RES_CAND="" RES_SFX="$SUFFIX"
  if [ -f "$arg" ]; then RES_CAND="$arg"; return 0; fi
  stem="${arg%.html}"
  case "$stem" in */*) : ;; *) stem="$SCRIPT_DIR/runs/$stem" ;; esac
  if [ -f "$stem.html" ]; then RES_CAND="$stem.html"; return 0; fi
  case "$stem" in
    *[0-9][A-Za-z])
      cand="${stem%?}"
      if [ -f "$cand.html" ]; then
        RES_CAND="$cand.html"
        RES_SFX="${stem#"$cand"}"
        return 0
      fi
      echo "ERROR: $arg: no candidate found (tried $stem.html, $cand.html)" >&2 ;;
    *)
      echo "ERROR: $arg: no candidate found (tried $stem.html)" >&2 ;;
  esac
  return 1
}

grade_one() {
  local candidate="$1" sfx="$2"
  local tag mark stem out job_dir reply errlog rc t0 t1

  stem="${candidate%.html}"
  tag="$(basename "$stem")$sfx"
  mark="$(echo "$candidate" | tr '/' '_')$sfx"
  if [ ! -f "$candidate" ]; then
    echo "[$tag] FAIL: candidate not found" >&2
    : > "$FAIL_DIR/$mark"
    return 1
  fi
  out="${stem}${sfx}.ai.json"
  if [ -e "$out" ] && [ "$FORCE" -ne 1 ]; then
    echo "[$tag] SKIP: $out exists (use -f to overwrite)" >&2
    : > "$SKIP_DIR/$mark"
    return 0
  fi

  job_dir="$WORKDIR/$mark.d"
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
  local attempt note
  for attempt in $(seq 1 "$MAX_ATTEMPTS"); do
    t0="$(date +%s)"
    # Empty cwd on purpose: no CLAUDE.md, no project settings, no repo memory.
    # Explicit permission mode on purpose: without one, the user's settings
    # defaultMode applies - "plan" derails the grader into planning.
    (
      cd "$job_dir" &&
      claude -p --model "$MODEL" --effort "$EFFORT" --tools "" \
        --permission-mode dontAsk \
        --no-session-persistence < prompt.txt
    ) > "$reply" 2> "$errlog"
    rc=$?
    t1="$(date +%s)"

    if [ "$rc" -eq 0 ] && [ -s "$reply" ] && reply_has_scores "$reply" "$job_dir/validate.err"; then
      note=""
      if [ "$attempt" -gt 1 ]; then note=" (attempt $attempt)"; fi
      mv "$reply" "$out"
      echo "[$tag] OK -> $out ($((t1 - t0))s)$note" >&2
      return 0
    fi
    if [ "$attempt" -lt "$MAX_ATTEMPTS" ]; then
      echo "[$tag] RETRY: attempt $attempt unusable after $((t1 - t0))s (claude rc=$rc)" >&2
    fi
  done

  if [ -s "$reply" ]; then
    mv "$reply" "$out.rejected"
    echo "[$tag] FAIL: no usable F/G scores after $MAX_ATTEMPTS attempts; reply kept at $out.rejected" >&2
    tail -n 2 "$job_dir/validate.err" >&2 || true
  else
    echo "[$tag] FAIL: claude exited $rc with an empty reply; stderr tail:" >&2
    tail -n 5 "$errlog" >&2 || true
  fi
  : > "$FAIL_DIR/$mark"
  return 1
}

# Resolve every arg before starting anything. Args whose candidate is missing
# are reported as ERROR and skipped - the rest still get graded (a failed
# generation must not block grading its siblings). They count as failures in
# the summary and the exit code. Only when NOTHING resolves (e.g. a typoed
# sweep) does the script stop before spending any grading calls.
CANDS=()
SFXS=()
missing=0
for arg in "$@"; do
  if resolve_arg "$arg"; then
    CANDS+=("$RES_CAND")
    SFXS+=("$RES_SFX")
  else
    missing=$((missing + 1))
    : > "$FAIL_DIR/missing_$(echo "$arg" | tr '/' '_')"
  fi
done
if [ "${#CANDS[@]}" -eq 0 ]; then
  echo "ERROR: none of the $# argument(s) resolved to a candidate - nothing to grade" >&2
  exit 1
fi
if [ "$missing" -gt 0 ]; then
  echo "ERROR: $missing argument(s) have no candidate file (see above); grading the ${#CANDS[@]} that do" >&2
fi

i=0
while [ "$i" -lt "${#CANDS[@]}" ]; do
  if [ "$JOBS" -gt 1 ]; then
    while [ "$(jobs -rp | wc -l)" -ge "$JOBS" ]; do
      wait -n
    done
    grade_one "${CANDS[$i]}" "${SFXS[$i]}" &
  else
    grade_one "${CANDS[$i]}" "${SFXS[$i]}"
  fi
  i=$((i + 1))
done
wait

failures="$(find "$FAIL_DIR" -type f | wc -l)"   # includes missing-candidate args
skips="$(find "$SKIP_DIR" -type f | wc -l)"
total=$#
graded=$((total - failures - skips))
if [ "$missing" -gt 0 ]; then
  echo "done: $graded graded, $skips skipped (existing), $failures failed ($missing of them: candidate missing)" >&2
else
  echo "done: $graded graded, $skips skipped (existing), $failures failed" >&2
fi
[ "$failures" -eq 0 ]
