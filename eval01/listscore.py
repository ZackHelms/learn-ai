#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""listscore.py - print grading-run scores as "deterministic + ai = total".

Usage:
    ./listscore.py r01a                # one run, bare line
    ./listscore.py r01{a..e}          # labeled lines + AVG line
    ./listscore.py r0{1..3}{a..e}     # grouped by candidate, AVG per group

Each argument is a grading-run stem: candidate stem plus grading suffix
(r01a = candidate r01, grading run a). For each argument this reads

    runs/<arg>.ai.json          the AI grader's saved reply (categories F-G)
    runs/<arg>.eval.json        the deterministic score; when that exact file
                                does not exist, falls back to the candidate's
                                (trailing letter stripped: r01a -> r01.eval.json)

and prints the RESULTS.md Score-column format. With multiple arguments, runs
are grouped by candidate and each group with 2+ parsed runs gets a column-wise
average line:

    r05a: 39 + 24 =  63
    r05b: 39 + 30 =  69
    AVG:  39 + 27.0 =  66.0

The AVG ai and total columns always carry one decimal place (".0" included)
so AVG lines column-align when pasted into RESULTS.md.

Warnings go to stderr when the deterministic file lacks the runtime pass (the
total is then out of less than 100) or the grader skipped items. F/G parsing
and clamping are imported from eval_ashfall.py, so the ai number always
matches --merge.
"""

import json
import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from eval_ashfall import AI_TOTAL, DETERMINISTIC_TOTAL, load_ai  # noqa: E402


def num(x):
    """32.0 -> '32', 18.8 -> '18.8'."""
    return "%d" % round(x) if abs(x - round(x)) < 1e-9 else "%.1f" % x


def resolve(arg):
    """Return (label, group_key, ai_path, eval_path or None, eval_paths_tried)."""
    stem = re.sub(r"\.(ai\.json|eval\.json|html)$", "", arg)
    base = stem if "/" in stem else os.path.join(SCRIPT_DIR, "runs", stem)

    tried = [base + ".eval.json"]
    cand = re.sub(r"(?<=\d)[A-Za-z]$", "", base)  # r01a -> r01
    if cand != base:
        tried.append(cand + ".eval.json")
    eval_path = next((p for p in tried if os.path.exists(p)), None)
    return os.path.basename(stem), os.path.basename(cand), base + ".ai.json", eval_path, tried


def main(argv):
    if not argv:
        print("usage: listscore.py <run-stem> [...]   e.g. listscore.py r01a  or  r01{a..e}",
              file=sys.stderr)
        return 1

    multi = len(argv) > 1
    rc = 0
    order = []   # group keys in first-seen order
    groups = {}  # group key -> [(label, det, ai)]

    for arg in argv:
        label, group, ai_path, eval_path, tried = resolve(arg)
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
        if group not in groups:
            groups[group] = []
            order.append(group)
        groups[group].append((label, det, f_pts + g_pts))

        if det_max < DETERMINISTIC_TOTAL:
            print("%swarning: deterministic half scored out of %s (runtime pass missing); "
                  "total is out of %s, not 100"
                  % (prefix, num(det_max), num(det_max + AI_TOTAL)), file=sys.stderr)
        if missing:
            print("%swarning: grader skipped %d item(s), scored 0: %s"
                  % (prefix, len(missing), ", ".join(missing)), file=sys.stderr)

    for i, group in enumerate(order):
        rows = groups[group]
        if i:
            print()
        for label, det, ai in rows:
            prefix = "%s: " % label if multi else ""
            print("%s%s + %s = %s" % (prefix, num(det), num(ai), num(det + ai).rjust(3)))
        if multi and len(rows) >= 2:
            n = len(rows)
            avg_det = sum(det for _, det, _ in rows) / n
            avg_ai = sum(ai for _, _, ai in rows) / n
            pad = max(len(label) for label, _, _ in rows) + 2
            print("%s%s + %4.1f = %5.1f" % ("AVG:".ljust(pad), num(avg_det),
                                            avg_ai, avg_det + avg_ai))
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
