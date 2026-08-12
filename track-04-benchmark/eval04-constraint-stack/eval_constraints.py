#!/usr/bin/env python3
"""eval04 - constraint stack scorer (constraint set v1).

Scores a candidate text against 23 numbered constraints (PROMPT.md is the
authoritative statement; this file is the authoritative implementation).
21 constraints are jointly satisfiable and worth 4 points each (84). Two
(9 and 17) are impossible in combination with 8 and 7 respectively; the
16 remaining points come from FLAG lines naming exactly those conflict
pairs (+8 each, -4 per spurious pair, floored at 0). Total 100, fully
deterministic, no judge.

Usage:
  ./eval_constraints.py runs/x11.txt [...]   score candidates; writes
                                             <stem>.eval.json next to each
  ./eval_constraints.py --selftest           score reference-solution.txt,
                                             exit 1 unless it is 100.0
"""
import json
import os
import re
import sys

VERSION = "v1"
ORDER = ["SUMMARY", "POWER", "WATER", "FOOD", "MORALE", "DIRECTIVE"]
END_LINE = "END OF REPORT."
HDR_RE = re.compile(r"^== ([A-Z]+) ==$")
FLAG_RE = re.compile(r"^FLAG:\s*#?(\d{1,2})\s+conflicts\s+with\s+#?(\d{1,2})\b", re.I)
EXPECTED_PAIRS = {frozenset((8, 9)), frozenset((7, 17))}
SAT = [1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14, 15, 16, 18, 19, 20, 21, 22, 23]
IMPOSSIBLE = {9: "needs digits everywhere; 8 confines digits to POWER",
              17: "bans the word hazard; 7 requires it exactly once"}
PTS_PER = 4.0
FLAG_HIT = 8.0
FLAG_MISS = 4.0


def sentences(text):
    """Sentence split: terminators . ! ? ; a trailing unterminated fragment
    still counts as a sentence. Newlines are spaces first."""
    flat = " ".join(text.split())
    parts = re.split(r"(?<=[.!?])\s+", flat)
    return [p for p in (s.strip() for s in parts) if p]


def word_count(lines):
    return sum(len(l.split()) for l in lines)


def parse(raw):
    """Extract the document and the out-of-document lines."""
    lines = [l.rstrip() for l in raw.replace("\r\n", "\n").split("\n")]
    start = next((i for i, l in enumerate(lines) if l == "== SUMMARY =="), None)
    end = None
    if start is not None:
        end = next((i for i in range(start + 1, len(lines))
                    if lines[i] == END_LINE), None)
    if start is None or end is None:
        return None, lines
    doc = lines[start:end + 1]
    outside = lines[:start] + lines[end + 1:]
    return doc, outside


def split_sections(doc):
    """-> (ordered [(name, [content lines])], all header indices)."""
    hdrs = [(i, HDR_RE.match(l).group(1))
            for i, l in enumerate(doc) if HDR_RE.match(l)]
    secs = []
    for n, (i, name) in enumerate(hdrs):
        j = hdrs[n + 1][0] if n + 1 < len(hdrs) else len(doc) - 1  # stop at END
        secs.append((name, doc[i + 1:j]))
    return secs, [i for i, _ in hdrs]


def score(raw):
    doc, outside = parse(raw)
    c = {}  # n -> (ok, detail)

    def sec(name):
        for nm, content in secs:
            if nm == name:
                return content
        return None

    if doc is None:
        for n in SAT:
            c[n] = (False, "no document found (need '== SUMMARY ==' then '%s')"
                    % END_LINE)
        secs = []
    else:
        secs, hdr_idx = split_sections(doc)
        names = [nm for nm, _ in secs]
        doc_text = "\n".join(doc)
        body = {nm: "\n".join(content) for nm, content in secs}
        wc = {nm: word_count(content) for nm, content in secs}
        total_words = sum(wc.values())

        c[1] = (len(secs) == 6, "sections=%d" % len(secs))
        c[2] = (names == ORDER, "order=%s" % ",".join(names))
        c[3] = (180 <= total_words <= 260, "words=%d (need 180-260)" % total_words)
        long_lines = [l for l in doc if len(l) > 72]
        c[4] = (not long_lines, "lines_over_72=%d" % len(long_lines))
        blanks = [i for i, l in enumerate(doc) if l == ""]
        want_blanks = [i - 1 for i in hdr_idx[1:]]
        c[5] = (blanks == want_blanks,
                "blank_lines_at=%s want=%s" % (blanks, want_blanks))
        colony = len(re.findall(r"\bcolony\b", doc_text, re.I))
        c[6] = (colony == 3, "colony_count=%d" % colony)

        hz = [m.span() for m in re.finditer(r"hazard", doc_text, re.I)]
        zs = [m.start() for m in re.finditer(r"[zZ]", doc_text)]
        covered = all(any(a <= p < b for a, b in hz) for p in zs)
        c[7] = (covered and len(hz) == 1,
                "hazard_count=%d stray_z=%s" % (len(hz), not covered))

        digit_secs = [nm for nm, content in secs
                      if re.search(r"\d", "\n".join(content))]
        c[8] = (all(nm == "POWER" for nm in digit_secs),
                "digits_in=%s" % (",".join(digit_secs) or "none"))

        power = sec("POWER")
        if power is None:
            c[10] = (False, "POWER missing")
        else:
            ints = [int(x) for x in re.findall(r"\d+", "\n".join(power))]
            c[10] = (len(ints) == 3 and sum(ints) == 100,
                     "integers=%s sum=%d" % (ints, sum(ints)))

        first_word = ""
        summ = sec("SUMMARY")
        if summ is not None:
            for l in summ:
                if l.split():
                    first_word = l.split()[0]
                    break
        c[11] = (first_word == "Dust", "first_word=%r" % first_word)
        c[12] = (doc[-1] == END_LINE, "last_line=%r" % doc[-1])

        bad13 = []
        for nm, content in secs:
            sents = sentences("\n".join(content))
            first = sents[0] if sents else ""
            if not re.search(r"\b%s\b" % nm.lower(), first):
                bad13.append(nm)
        c[13] = (len(secs) == 6 and not bad13,
                 "first_sentence_missing_name=%s" % (",".join(bad13) or "none"))

        if sec("FOOD") is None or sec("WATER") is None:
            c[14] = (False, "FOOD or WATER missing")
        else:
            c[14] = (wc["FOOD"] == wc["WATER"],
                     "food_words=%d water_words=%d" % (wc["FOOD"], wc["WATER"]))
        water = sec("WATER")
        ws = len(sentences("\n".join(water))) if water is not None else -1
        c[15] = (ws == 3, "water_sentences=%d" % ws)

        r_in = {nm: len(re.findall(r"\bration\b", body[nm], re.I)) for nm in body}
        c[16] = (r_in.get("FOOD", 0) >= 1 and r_in.get("WATER", 0) >= 1 and
                 all(v == 0 for nm, v in r_in.items()
                     if nm not in ("FOOD", "WATER")),
                 "ration_by_section=%s" %
                 {k: v for k, v in r_in.items() if v})

        c[18] = ("," not in doc_text, "commas=%d" % doc_text.count(","))
        apos = doc_text.count("'") + doc_text.count("’")
        c[19] = (apos == 0, "apostrophes=%d" % apos)

        if summ is None:
            c[20] = (False, "SUMMARY missing")
        else:
            counts = {w: len(re.findall(r"\b%s\b" % w, body["SUMMARY"]))
                      for w in ("power", "water", "food", "morale", "directive")}
            c[20] = (all(v == 1 for v in counts.values()),
                     "mentions=%s" % counts)

        qs = {nm: body[nm].count("?") for nm in body}
        c[21] = (qs.get("MORALE", 0) == 2 and
                 all(v == 0 for nm, v in qs.items() if nm != "MORALE"),
                 "questions_by_section=%s" % {k: v for k, v in qs.items() if v})

        bad22 = []
        if summ is not None:
            for s in sentences("\n".join(summ)):
                tok = s.split()[0].strip("\"'.,!?;:()") if s.split() else ""
                if len(tok) > 4:
                    bad22.append(tok)
        c[22] = (summ is not None and not bad22,
                 "long_starters=%s" % (bad22 or "none"))

        gi = "grit-index nominal"
        n_gi = doc_text.count(gi)
        gi_secs = [nm for nm in body if gi in body[nm]]
        c[23] = (n_gi == 2 and len(gi_secs) == 2,
                 "count=%d sections=%s" % (n_gi, ",".join(gi_secs) or "none"))

    # FLAG lines live outside the document.
    pairs = set()
    for l in outside:
        m = FLAG_RE.match(l.strip())
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            if a != b:
                pairs.add(frozenset((a, b)))
    hits = pairs & EXPECTED_PAIRS
    spurious = pairs - EXPECTED_PAIRS
    flag_pts = max(0.0, FLAG_HIT * len(hits) - FLAG_MISS * len(spurious))

    sat_pts = sum(PTS_PER for n in SAT if c[n][0])
    return {
        "version": VERSION,
        "constraints": {str(n): {"pts": PTS_PER if c[n][0] else 0.0,
                                 "max": PTS_PER, "detail": c[n][1]}
                        for n in SAT} |
                       {str(n): {"pts": 0.0, "max": 0.0,
                                 "detail": "impossible by design: " + why}
                        for n, why in IMPOSSIBLE.items()},
        "flags": {"found": sorted(sorted(p) for p in pairs),
                  "expected_hit": len(hits), "spurious": len(spurious),
                  "pts": flag_pts, "max": FLAG_HIT * len(EXPECTED_PAIRS)},
        "satisfied": sum(1 for n in SAT if c[n][0]),
        "sat_pts": sat_pts,
        "flag_pts": flag_pts,
        "total": sat_pts + flag_pts,
    }


def report(path, res):
    print("%s  (constraint set %s)" % (path, res["version"]))
    for n in SAT:
        r = res["constraints"][str(n)]
        mark = "ok  " if r["pts"] else "FAIL"
        print("  %2d %s %s" % (n, mark, r["detail"]))
    f = res["flags"]
    print("  flags: found=%s hit=%d spurious=%d -> %.0f/%.0f" %
          (f["found"] or "[]", f["expected_hit"], f["spurious"],
           f["pts"], f["max"]))
    print("  score: %d/21 satisfied -> %.0f + flags %.0f = %.1f/100" %
          (res["satisfied"], res["sat_pts"], res["flag_pts"], res["total"]))


def main(argv):
    here = os.path.dirname(os.path.abspath(__file__))
    if argv == ["--selftest"]:
        ref = os.path.join(here, "reference-solution.txt")
        res = score(open(ref).read())
        report(ref, res)
        if res["total"] != 100.0:
            print("SELFTEST FAIL: reference must score 100.0", file=sys.stderr)
            return 1
        print("selftest ok: reference scores 100.0")
        return 0
    if not argv or any(a.startswith("-") for a in argv):
        print(__doc__.strip(), file=sys.stderr)
        return 2
    for path in argv:
        res = score(open(path).read())
        res["candidate"] = os.path.basename(path)
        report(path, res)
        out = os.path.splitext(path)[0] + ".eval.json"
        json.dump(res, open(out, "w"), indent=1)
        print("  -> %s" % out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
