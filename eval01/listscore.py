#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""listscore.py - print a grading run's score as "deterministic + ai = total".

Usage:
    ./listscore.py r01a [r03b ...]

The argument is a grading-run stem: candidate stem plus grading suffix
(r01a = candidate r01, grading run a). For each argument this reads

    runs/<arg>.ai.json          the AI grader's saved reply (categories F-G)
    runs/<arg>.eval.json        the deterministic score; when that exact file
                                does not exist, falls back to the candidate's
                                (trailing letter stripped: r01a -> r01.eval.json)

and prints the RESULTS.md Score-column format, e.g.

    32 + 18 =  50

One labeled line per argument when more than one is given. Warnings go to
stderr when the deterministic file lacks the runtime pass (the total is then
out of less than 100) or the grader skipped items. F/G parsing and clamping
are imported from eval_ashfall.py, so the ai number always matches --merge.
"""

import json
import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from eval_ashfall import AI_TOTAL, DETERMINISTIC_TOTAL, load_ai  # noqa: E402


def num(x):
    """32.0 -> '32', 31.5 -> '31.5'."""
    return "%d" % round(x) if abs(x - round(x)) < 1e-9 else "%.1f" % x


def resolve(arg):
    """Return (label, ai_path, eval_path or None, eval_paths_tried)."""
    stem = re.sub(r"\.(ai\.json|eval\.json|html)$", "", arg)
    base = stem if "/" in stem else os.path.join(SCRIPT_DIR, "runs", stem)

    tried = [base + ".eval.json"]
    cand = re.sub(r"(?<=\d)[A-Za-z]$", "", base)  # r01a -> r01
    if cand != base:
        tried.append(cand + ".eval.json")
    eval_path = next((p for p in tried if os.path.exists(p)), None)
    return os.path.basename(stem), base + ".ai.json", eval_path, tried


def main(argv):
    if not argv:
        print("usage: listscore.py <run-stem> [...]   e.g. listscore.py r01a", file=sys.stderr)
        return 1

    multi = len(argv) > 1
    rc = 0
    for arg in argv:
        label, ai_path, eval_path, tried = resolve(arg)
        prefix = "%s: " % label if multi else ""

        if eval_path is None:
            print("%serror: no eval.json (tried %s)" % (prefix, ", ".join(tried)), file=sys.stderr)
            rc = 1
            continue
        try:
            with open(eval_path, encoding="utf-8") as fh:
                ev = json.load(fh)
            f_pts, g_pts, _data, missing = load_ai(ai_path)
        except FileNotFoundError as e:
            print("%serror: missing %s" % (prefix, e.filename), file=sys.stderr)
            rc = 1
            continue
        except (SystemExit, ValueError) as e:  # load_ai bad-JSON / corrupt eval.json
            print("%serror: %s" % (prefix, e), file=sys.stderr)
            rc = 1
            continue

        det = ev.get("deterministic_points", 0)
        det_max = ev.get("deterministic_max", 0)
        ai = f_pts + g_pts
        print("%s%s + %s = %s" % (prefix, num(det), num(ai), num(det + ai).rjust(3)))

        if det_max < DETERMINISTIC_TOTAL:
            print("%swarning: deterministic half scored out of %s (runtime pass missing); "
                  "total is out of %s, not 100"
                  % (prefix, num(det_max), num(det_max + AI_TOTAL)), file=sys.stderr)
        if missing:
            print("%swarning: grader skipped %d item(s), scored 0: %s"
                  % (prefix, len(missing), ", ".join(missing)), file=sys.stderr)
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
