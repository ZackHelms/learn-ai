#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["playwright"]
# ///
"""
eval_repair.py - eval03 scorer (defect set v1).

Takes a model reply containing edits to ashfall-defective-v1.html (sha-pinned),
applies them, runs the hidden test suite in headless Chromium, and scores:

    apply       8   every edit block located and applied
    defects    60   6 defect-revealing tests x 10 (fail on the defective file)
    guards     12   6 regression tests x 2 (pass on the defective file too -
                    a shotgun rewrite that breaks them pays for it)
    minimal    20   x (defect tests passed / 6) x line factor:
                    <=16 touched lines 1.0, <=32 0.6, <=64 0.3, more 0
    total     100

Accepted edit formats (either, mixed): unified diff hunks, or SEARCH/REPLACE
blocks:

    <<<<<<< SEARCH
    exact current lines
    =======
    replacement lines
    >>>>>>> REPLACE

Both are applied by exact, unique content match - @@ line numbers are ignored,
context must match the file byte-for-byte. An edit whose search text is absent
or ambiguous is skipped (and costs the apply points).

Usage:
  ./eval_repair.py runs/x1.txt [...]     score replies; writes <stem>.eval.json
  ./eval_repair.py --selftest            reference-fix.txt must score 100 and
                                         the unpatched defective file must fail
                                         exactly the 6 defect tests
"""
import json
import hashlib
import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
DEFECTIVE = os.path.join(HERE, "ashfall-defective-v1.html")
DEFECTIVE_SHA = "62f5062537e5f6bf9423adfc39bbc98e31b76321c7a638473f3941809133c43e"
VERSION = "v1"

# ---------------------------------------------------------------- hidden suite
# kind "defect": passes on the reference, fails on the defective file.
# kind "guard":  passes on both; breaking it means collateral damage.
TESTS = [
    ("D1a neighbors: corner A1 has 3 neighbors, B2 has 8", "defect",
     "neighbors(0).length===3 && neighbors(9).length===8"),
    ("D1b adjacency: water east of a tile is counted", "defect",
     "(()=>{const S=newGame(1337);S.map[1].t='water';return adjCount(S,0,'water')===1;})()"),
    ("D2 worker multiplier is 0.7+0.15*skill", "defect",
     "(()=>{const S=newGame(1337);const gi=S.map.findIndex(t=>t.t==='ash');"
     "buildAt(S,gi,'sifter');const c=S.colonists.find(x=>x.job==='Farmer');"
     "c.skill=4;c.fatigue=0;c.morale=90;c.assign=gi;"
     "const exp=(0.7+0.15*4)*(1+0.10*adjCount(S,gi,'ash'));"
     "return Math.abs(prodInfo(S,gi).mult-exp)<1e-9;})()"),
    ("D3 same-turn production covers needs (no phantom shortage)", "defect",
     "(()=>{const S=newGame(1337);const gi=S.map.findIndex(t=>t.t==='ash');"
     "buildAt(S,gi,'greenhouse');const f=S.colonists.find(x=>x.job==='Farmer');"
     "f.skill=3;f.assign=gi;S.colonists=[f];"
     "S.res.food=0;S.res.soil=30;S.res.water=30;"
     "endTurn(S,true);return S.shortage.food===false;})()"),
    ("D4 export/import round-trips to an identical hash", "defect",
     "(()=>{const S=newGame(1337);for(let t=0;t<6;t++){policyStep(S);endTurn(S,true);"
     "if(S.pending)applyChoice(S,policyChoice(S));}"
     "const r=deserialize(serialize(S));if(r.err)return 'rejected: '+r.err;"
     "return hashState(r.S)===hashState(S);})()"),
    ("D5 zero-morale colonist leaves after 2 straight turns", "defect",
     "(()=>{const S=newGame(1337);for(const c of S.colonists)c.morale=0;"
     "S.res.food=0;S.res.water=0;const p0=popOf(S);"
     "endTurn(S,true);if(popOf(S)!==p0)return 'left after 1 turn';"
     "endTurn(S,true);return popOf(S)<p0;})()"),
    ("G1 sifter costs exactly 4 metal", "guard",
     "(()=>{const S=newGame(1337);const m0=S.res.metal;"
     "const err=buildAt(S,S.map.findIndex(t=>t.t==='ash'),'sifter');"
     "return err===null&&S.res.metal===m0-4;})()"),
    ("G2 research prerequisites enforced", "guard",
     "(()=>{const S=newGame(1337);S.res.scrip=999;S.res.parts=99;"
     "return buyResearch(S,'irrigation')!==null&&buyResearch(S,'agronomy')===null;})()"),
    ("G3 PRNG determinism", "guard",
     "(()=>{const a=mulberry32(42),b=mulberry32(42);"
     "for(let i=0;i<5;i++)if(a()!==b())return false;return true;})()"),
    ("G4 storage cap respected, overflow tallied", "guard",
     "(()=>{const S=newGame(1337);S._over={};S.res.water=capsOf(S).water;"
     "addRes(S,'water',10);return S.res.water<=capsOf(S).water&&(S._over.water||0)>9.9;})()"),
    ("G5 caravan buying moves scrip, goods, stock", "guard",
     "(()=>{const S=newGame(1337);S.turn=5;runCaravan(S);if(!S.caravan)return 'no caravan';"
     "S.res.scrip=500;const f0=S.res.food,s0=S.caravan.stock.food;"
     "const err=tradeBuy(S,'food',3);if(err)return err;"
     "return S.res.food===f0+3&&S.caravan.stock.food===s0-3;})()"),
    ("G6 map generation deterministic for a seed", "guard",
     "(()=>genMap(1337).map(t=>t.t).join('')===genMap(1337).map(t=>t.t).join(''))()"),
]

PTS_APPLY, PTS_DEFECT, PTS_GUARD, PTS_MIN = 8.0, 10.0, 2.0, 20.0


# ---------------------------------------------------------------- edit parsing
def parse_edits(text):
    """-> list of (search_lines, replace_lines). Accepts SEARCH/REPLACE blocks
    and unified-diff hunks (content-matched; @@ offsets ignored)."""
    edits = []
    sr = re.compile(r"<{7} *SEARCH *\n(.*?)\n?={7} *\n(.*?)\n?>{7} *REPLACE",
                    re.S)
    for m in sr.finditer(text):
        edits.append((m.group(1).split("\n"), m.group(2).split("\n")))
    stripped = sr.sub("", text)
    lines = stripped.split("\n")
    i = 0
    while i < len(lines):
        if lines[i].startswith("@@"):
            search, replace = [], []
            i += 1
            while i < len(lines):
                l = lines[i]
                if l.startswith("@@") or l.startswith("--- ") or l.startswith("+++ ") \
                        or l.startswith("```") or l.startswith("<<<<<<<"):
                    break
                if l.startswith("-"):
                    search.append(l[1:])
                elif l.startswith("+"):
                    replace.append(l[1:])
                elif l.startswith(" ") or l == "":
                    search.append(l[1:] if l.startswith(" ") else "")
                    replace.append(l[1:] if l.startswith(" ") else "")
                else:
                    break
                i += 1
            if any(s for s in search):
                edits.append((search, replace))
        else:
            i += 1
    return edits


def apply_edits(text, edits):
    """Exact unique content match; returns (new_text, applied, failed_notes,
    touched_lines)."""
    applied, notes, touched = 0, [], 0
    for n, (search, replace) in enumerate(edits, 1):
        block = "\n".join(search)
        cnt = text.count(block)
        if cnt == 0:
            notes.append("edit %d: search text not found" % n)
            continue
        if cnt > 1:
            notes.append("edit %d: search text ambiguous (%d matches)" % (n, cnt))
            continue
        text = text.replace(block, "\n".join(replace), 1)
        applied += 1
        # touched = removed + added lines, with unchanged context free:
        # each positionally-changed pair counts 2, each inserted/deleted line 1.
        touched += 2 * sum(1 for a, b in zip(search, replace) if a != b) \
            + abs(len(search) - len(replace))
    return text, applied, notes, touched


def line_factor(touched):
    if touched <= 16:
        return 1.0
    if touched <= 32:
        return 0.6
    if touched <= 64:
        return 0.3
    return 0.0


# ---------------------------------------------------------------- suite runner
def run_suite(html_text):
    from playwright.sync_api import sync_playwright
    results = []
    with tempfile.TemporaryDirectory(prefix="eval03-") as td:
        p = os.path.join(td, "candidate.html")
        open(p, "w", encoding="utf-8").write(html_text)
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            page = browser.new_page()
            page.goto("file://" + p, timeout=30000)
            for name, kind, js in TESTS:
                try:
                    r = page.evaluate("() => { try { return (%s); } catch(e) "
                                      "{ return 'threw: ' + e.message; } }" % js)
                except Exception as e:  # page crashed etc.
                    r = "evaluate failed: %s" % e
                results.append((name, kind, r is True,
                                "" if r is True else str(r)))
            browser.close()
    return results


def score_reply(reply_text):
    base = open(DEFECTIVE, encoding="utf-8").read()
    edits = parse_edits(reply_text)
    patched, applied, notes, touched = apply_edits(base, edits)
    results = run_suite(patched)
    d_pass = sum(1 for _, k, ok, _ in results if k == "defect" and ok)
    g_pass = sum(1 for _, k, ok, _ in results if k == "guard" and ok)
    apply_pts = PTS_APPLY if edits and applied == len(edits) else \
        (PTS_APPLY * applied / len(edits) if edits else 0.0)
    min_pts = PTS_MIN * (d_pass / 6.0) * line_factor(touched)
    total = apply_pts + d_pass * PTS_DEFECT + g_pass * PTS_GUARD + min_pts
    return {
        "version": VERSION, "edits": len(edits), "applied": applied,
        "apply_notes": notes, "touched_lines": touched,
        "tests": [{"name": n, "kind": k, "pass": ok, "detail": d}
                  for n, k, ok, d in results],
        "defect_tests_passed": d_pass, "guard_tests_passed": g_pass,
        "apply_pts": round(apply_pts, 1), "defect_pts": d_pass * PTS_DEFECT,
        "guard_pts": g_pass * PTS_GUARD, "minimality_pts": round(min_pts, 1),
        "total": round(apply_pts + d_pass * PTS_DEFECT + g_pass * PTS_GUARD + min_pts, 1),
    }


def report(path, res):
    print("%s  (defect set %s)" % (path, res["version"]))
    print("  edits=%d applied=%d touched=%d %s" %
          (res["edits"], res["applied"], res["touched_lines"],
           "; ".join(res["apply_notes"]) or ""))
    for t in res["tests"]:
        print("  %s %-6s %s%s" % ("ok  " if t["pass"] else "FAIL",
                                  t["kind"], t["name"],
                                  "" if t["pass"] else "  [" + t["detail"][:80] + "]"))
    print("  score: apply %.1f + defects %d + guards %d + minimality %.1f = %.1f/100"
          % (res["apply_pts"], res["defect_pts"], res["guard_pts"],
             res["minimality_pts"], res["total"]))


def main(argv):
    sha = hashlib.sha256(open(DEFECTIVE, "rb").read()).hexdigest()
    if sha != DEFECTIVE_SHA:
        sys.exit("defective artifact sha mismatch (have %s) - regenerate with "
                 "make_defective.py or restore from git" % sha)
    if argv == ["--selftest"]:
        base = open(DEFECTIVE, encoding="utf-8").read()
        results = run_suite(base)
        bad = [n for n, k, ok, _ in results if (k == "defect") == ok]
        for n, k, ok, d in results:
            print("  %s %-6s %s" % ("ok  " if ok else "FAIL", k, n))
        if bad:
            print("SELFTEST FAIL: unpatched defective file - these tests are "
                  "on the wrong side: %s" % bad, file=sys.stderr)
            return 1
        print("unpatched defective file fails exactly the 6 defect tests - ok\n")
        res = score_reply(open(os.path.join(HERE, "reference-fix.txt")).read())
        report("reference-fix.txt", res)
        if res["total"] != 100.0:
            print("SELFTEST FAIL: reference fix must score 100.0", file=sys.stderr)
            return 1
        print("selftest ok: reference fix scores 100.0")
        return 0
    if not argv or any(a.startswith("-") for a in argv):
        print(__doc__.strip(), file=sys.stderr)
        return 2
    for path in argv:
        res = score_reply(open(path, encoding="utf-8").read())
        res["candidate"] = os.path.basename(path)
        report(path, res)
        out = os.path.splitext(path)[0] + ".eval.json"
        json.dump(res, open(out, "w"), indent=1)
        print("  -> %s" % out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
