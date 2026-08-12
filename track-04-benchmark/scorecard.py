#!/usr/bin/env python3
"""scorecard.py - one table per eval from whatever runs exist on disk.

Reads every runs/*.eval.json under eval02-05 (and eval01's, which have a
different schema) and prints the headline number for each run. Purely a
reader: it computes nothing and re-scores nothing.

Usage: ./scorecard.py            all evals
       ./scorecard.py eval03     just one
"""
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def rows_for(eval_dir):
    out = []
    for p in sorted(glob.glob(os.path.join(HERE, eval_dir, "runs", "*.eval.json"))):
        try:
            d = json.load(open(p))
        except ValueError:
            continue
        run = d.get("run") or d.get("candidate") or os.path.basename(p)[:-10]
        if run.endswith(".html"):
            run = run[:-5]
        if eval_dir.startswith("eval01"):
            out.append((run, "det %s/%s (judged half lives in its RESULTS.md)"
                        % (d.get("deterministic_points"), d.get("scored_out_of", 54))))
        elif eval_dir.startswith("eval02"):
            o = d.get("outcome", {})
            out.append((run, "score %s %s pop %s turns %s [%s]"
                        % (o.get("score"), "WIN" if o.get("win") else "loss",
                           o.get("pop"), d.get("turns_played"), d.get("agent"))))
        elif eval_dir.startswith("eval03"):
            out.append((run, "%.1f (defects %d/6, guards %d/6, touched %d)"
                        % (d.get("total", 0), d.get("defect_tests_passed", 0),
                           d.get("guard_tests_passed", 0), d.get("touched_lines", 0))))
        elif eval_dir.startswith("eval04"):
            out.append((run, "%.1f (sat %d/21, flags %.0f/16)"
                        % (d.get("total", 0), d.get("satisfied", 0),
                           d.get("flag_pts", 0))))
        elif eval_dir.startswith("eval05"):
            out.append((run, "%.0f (%s)" % (d.get("total", 0), d.get("by_type"))))
    return out


def main(argv):
    dirs = sorted(d for d in os.listdir(HERE)
                  if d.startswith("eval0") and os.path.isdir(os.path.join(HERE, d)))
    if argv:
        dirs = [d for d in dirs if d.startswith(argv[0])]
    for d in dirs:
        rows = rows_for(d)
        print("%s  (%d runs)" % (d, len(rows)))
        for run, desc in rows:
            print("  %-8s %s" % (run, desc))
        if not rows:
            print("  (none)")
        print()


if __name__ == "__main__":
    main(sys.argv[1:])
