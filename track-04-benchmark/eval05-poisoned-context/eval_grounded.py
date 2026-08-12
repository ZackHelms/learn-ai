#!/usr/bin/env python3
"""eval05 - grounded-answer scorer (bundle v1). Stdlib only.

20 questions x 5 pts = 100, exact-match after light normalization
(lowercase, backticks/quotes stripped, whitespace collapsed, trailing
period dropped). A VALUE question is right only with the right value;
ABSENT and CONFLICT questions are right only with that exact word -
"I don't know" earns nothing, which is the point: the eval pays for
calibrated abstention and conflict detection, not confidence.

Reply format expected from the model: one line per question, "N: ANSWER".
Lines that do not parse count as unanswered (0 for that question).

Usage:
  ./eval_grounded.py runs/x1.txt [...]   score replies -> <stem>.eval.json
  ./eval_grounded.py --selftest          the key replayed as a reply must
                                         score 100.0
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
VERSION = "v1"
PTS = 5.0


def norm(s):
    s = s.strip().strip("`\"'")
    s = re.sub(r"\s+", " ", s).rstrip(".").strip().lower()
    return s


def parse_reply(text):
    answers = {}
    for line in text.replace("\r\n", "\n").split("\n"):
        m = re.match(r"^\s*#?(\d{1,2})\s*[:.)-]\s+(.+?)\s*$", line)
        if m and 1 <= int(m.group(1)) <= 20:
            answers.setdefault(m.group(1), norm(m.group(2)))
    return answers


def score(text, key):
    answers = parse_reply(text)
    rows = []
    by_type = {}
    total = 0.0
    for n in sorted(key, key=int):
        want = norm(key[n]["answer"])
        typ = key[n]["type"]
        got = answers.get(n)
        ok = got == want
        if ok:
            total += PTS
        by_type.setdefault(typ, [0, 0])
        by_type[typ][1] += 1
        if ok:
            by_type[typ][0] += 1
        rows.append({"n": int(n), "type": typ, "want": want,
                     "got": got, "pass": ok})
    return {"version": VERSION, "total": total,
            "answered": len(answers),
            "by_type": {k: "%d/%d" % (v[0], v[1]) for k, v in by_type.items()},
            "questions": rows}


def report(path, res):
    print("%s  (bundle %s)" % (path, res["version"]))
    for r in res["questions"]:
        if not r["pass"]:
            print("  FAIL q%-2d %-8s want %-14r got %r"
                  % (r["n"], r["type"], r["want"], r["got"]))
    print("  by type: %s" % res["by_type"])
    print("  score: %.0f/100 (%d answered)" % (res["total"], res["answered"]))


def main(argv):
    key = json.load(open(os.path.join(HERE, "key.json")))
    if argv == ["--selftest"]:
        perfect = "\n".join("%s: %s" % (n, key[n]["answer"])
                            for n in sorted(key, key=int))
        res = score(perfect, key)
        report("<key replayed>", res)
        if res["total"] != 100.0:
            print("SELFTEST FAIL", file=sys.stderr)
            return 1
        print("selftest ok: key replay scores 100.0")
        return 0
    if not argv or any(a.startswith("-") for a in argv):
        print(__doc__.strip(), file=sys.stderr)
        return 2
    for path in argv:
        res = score(open(path).read(), key)
        res["candidate"] = os.path.basename(path)
        report(path, res)
        out = os.path.splitext(path)[0] + ".eval.json"
        json.dump(res, open(out, "w"), indent=1)
        print("  -> %s" % out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
