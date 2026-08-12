#!/usr/bin/env bash
# run.sh - eval02 convenience wrapper around driver.py.
#
#   ./run.sh [-m model] [-e effort] [-s seed] [-f] id [id ...]   claude agent
#   ./run.sh -b idle|naive|greedy [-s seed] [-f] id              baseline agent
#
# Model aliases haiku45/sonnet5/opus5/fable5 accepted (default haiku45 low).
# Seed defaults to 1337 - the frozen comparison seed; record any other seed in
# RESULTS. Each run writes runs/<id>.eval.json + runs/<id>.turns.jsonl and
# prints a paste-ready RESULTS.md row.
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

MODEL="claude-haiku-4-5"; EFFORT="low"; SEED=1337; BASE=""; FORCE=0
while getopts 'm:e:s:b:fh' opt; do
  case "$opt" in
    m) MODEL="$OPTARG" ;;
    e) EFFORT="$OPTARG" ;;
    s) SEED="$OPTARG" ;;
    b) BASE="$OPTARG" ;;
    f) FORCE=1 ;;
    h) sed -n '2,11p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) exit 1 ;;
  esac
done
shift $((OPTIND - 1))
[ "$#" -ge 1 ] || { echo "usage: ./run.sh [-m model] [-e effort] [-s seed] [-b baseline] [-f] id..." >&2; exit 1; }
case "$MODEL" in
  haiku45|haiku) MODEL="claude-haiku-4-5" ;;
  sonnet5|sonnet) MODEL="claude-sonnet-5" ;;
  opus5|opus) MODEL="claude-opus-5" ;;
  fable5|fable) MODEL="claude-fable-5" ;;
esac
AGENT="claude:$MODEL:$EFFORT"
[ -n "$BASE" ] && AGENT="builtin:$BASE"

fails=0
for id in "$@"; do
  out="$SCRIPT_DIR/runs/$id.eval.json"
  if [ -e "$out" ] && [ "$FORCE" -ne 1 ]; then
    echo "[$id] SKIP: $out exists (use -f)" >&2; continue
  fi
  if ! uv run "$SCRIPT_DIR/driver.py" --agent "$AGENT" --seed "$SEED" --id "$id" >/dev/null; then
    echo "[$id] FAILED" >&2; fails=$((fails+1)); continue
  fi
  python3 - "$out" <<'EOF'
import json, sys
d = json.load(open(sys.argv[1]))
o = d["outcome"]; api = d.get("api", {})
mins = d["wall_seconds"] // 60
agent = d["agent"].replace("claude:", "").replace("builtin:", "")
print("RESULTS.md row (eval02 section):")
print("| %s | %s | %s | %d | %d | %dm%02ds | $%.4f | %s | %s | %s/%s/%s | %s |" % (
    d["started"], agent, d["run"], d["seed"], d["turns_played"], mins,
    d["wall_seconds"] % 60, api.get("cost_usd", 0), o["score"],
    "WIN" if o["win"] else "loss", o["pop"], o["research"], o["stock"],
    d["state_hash"]))
EOF
done
[ "$fails" -eq 0 ]
