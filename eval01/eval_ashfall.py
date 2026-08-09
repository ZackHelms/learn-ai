#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["playwright"]
# ///
# The PEP 723 block above lets `uv run eval_ashfall.py` resolve playwright for the
# --runtime pass. Plain `python3 eval_ashfall.py` also works: the static pass is
# stdlib-only, and --runtime degrades gracefully when playwright is missing.
"""
eval_ashfall.py - deterministic scorer for the ASHFALL OUTPOST LLM eval.

WHAT THIS SCORES
----------------
This program scores only the parts of RUBRIC.md v1.1 that can be measured without a model in
the loop. That is 54 of the 100 rubric points:

    Category A - Executes ................ 10 pts   A1,A2 static / A3 runtime
    Category B - Instruction compliance .. 15 pts   all static
    Category C - Self-test harness ....... 15 pts   C1 static+runtime / C2,C3 runtime
    Category D - Determinism ............. 10 pts   all runtime
    Category E - UI mechanics ............  4 pts   all runtime

The remaining 46 points (Category F, systems implemented; Category G, interaction depth) are
judgment calls about whether code is real or a stub, and whether systems actually feed each
other. Those are graded by a strong LLM using GRADER_PROMPT.md, and merged back in here with
--merge so both halves land in one score out of 100.

HOW IT SCORES
-------------
Static checks are regex and structure checks over the raw HTML text. They never execute the
candidate. Static checks are cheap, dependency-free, and safe to run on untrusted output.

Runtime checks (--runtime) load the file in headless Chromium via Playwright, click controls
found by visible text, and diff the rendered page. They are more informative and more fragile;
see "Known weak spots" in RUBRIC.md. Without --runtime the script still runs, but reports a
lower scored_out_of so you do not accidentally compare a static-only run against a full one.

B1 and B2 are all-or-nothing on purpose: a single banned API call or a single remote resource
means the constraint was not followed.

USAGE
-----
    python3 eval_ashfall.py candidate.html
    python3 eval_ashfall.py candidate.html --runtime
    python3 eval_ashfall.py candidate.html --runtime --merge candidate.ai.json
    python3 eval_ashfall.py --report runs/

Writes <candidate>.eval.json next to the candidate unless --no-write is passed.
Exit code is 0 on a completed grade, 1 on a usage or IO error.
"""

import argparse
import glob
import json
import os
import re
import sys

STATIC_TOTAL = 26.0   # A1(3) A2(3) B(15) C1_static(2) D1(3)
RUNTIME_TOTAL = 28.0  # A3(4) C1_runtime(2) C2(5) C3(6) D2(3) D3(4) E1(2) E2(2)
DETERMINISTIC_TOTAL = STATIC_TOTAL + RUNTIME_TOTAL  # 54
AI_TOTAL = 46.0       # F(26) + G(20)


# --------------------------------------------------------------------------------------
# static checks
# --------------------------------------------------------------------------------------

BANNED_STORAGE = [
    r"\blocalStorage\b",
    r"\bsessionStorage\b",
    r"\bindexedDB\b",
    r"document\s*\.\s*cookie",
]

EXTERNAL_RES = [
    r"<script[^>]+src\s*=\s*[\"']https?://",
    r"<script[^>]+src\s*=\s*[\"'](?!data:)[^\"'>]+\.js",
    r"<link[^>]+href\s*=\s*[\"']https?://",
    r"@import\s+url\s*\(",
    r"\bfetch\s*\(",
    r"\bXMLHttpRequest\b",
    r"\bimportScripts\s*\(",
    r"cdn\.",
    r"googleapis\.com",
    r"unpkg\.com",
    r"jsdelivr",
]

PRNG_HINTS = [
    r"mulberry32",
    r"xorshift",
    r"splitmix",
    r"sfc32",
    r"1831565813",           # mulberry32 magic
    r"0x6D2B79F5",
    r"1664525",              # common LCG
    r"seed\s*[|>]{0,3}=?\s*0",
    r"function\s+\w*rng\w*\s*\(",
    r"\bseed\b[^\n]{0,40}\bfunction\b",
]


def strip_comments(text):
    """Crude comment stripper so banned-API mentions inside comments do not count."""
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.S)
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    text = re.sub(r"(?m)^\s*//.*$", " ", text)
    return text


def static_checks(raw):
    code = strip_comments(raw)
    r = {}

    # A1 - well-formed enough to be a page with inline script
    has_html = bool(re.search(r"<html\b", raw, re.I)) or raw.lstrip().lower().startswith("<!doctype")
    has_script = bool(re.search(r"<script\b", raw, re.I)) and bool(re.search(r"</script>", raw, re.I))
    r["A1"] = {"pts": 3.0 if (has_html and has_script) else 0.0, "max": 3.0,
               "detail": "html=%s inline_script=%s" % (has_html, has_script)}

    # A2 - truncation detector
    tail = raw.rstrip()[-400:]
    closed = bool(re.search(r"</html>\s*$", raw.rstrip(), re.I))
    fence_leak = "```" in raw
    open_script = len(re.findall(r"<script\b", raw, re.I)) != len(re.findall(r"</script>", raw, re.I))
    truncated = (not closed) or open_script
    r["A2"] = {"pts": 3.0 if not truncated else 0.0, "max": 3.0,
               "detail": "closes_html=%s script_tags_balanced=%s code_fence_leak=%s"
                         % (closed, not open_script, fence_leak),
               "tail": tail[-120:]}

    # B1 - storage APIs
    hits = []
    for pat in BANNED_STORAGE:
        hits += [pat for _ in re.findall(pat, code)]
    r["B1"] = {"pts": 4.0 if not hits else 0.0, "max": 4.0,
               "detail": "violations=%d %s" % (len(hits), sorted(set(hits)))}

    # B2 - external resources
    ext = []
    for pat in EXTERNAL_RES:
        for m in re.findall(pat, code, re.I):
            ext.append(pat)
    r["B2"] = {"pts": 4.0 if not ext else 0.0, "max": 4.0,
               "detail": "violations=%d %s" % (len(ext), sorted(set(ext)))}

    # B3 - Math.random
    mr = re.findall(r"Math\s*\.\s*random", code)
    r["B3"] = {"pts": 3.0 if not mr else 0.0, "max": 3.0, "detail": "occurrences=%d" % len(mr)}

    # B4 - seeded PRNG evidence
    prng = sorted({p for p in PRNG_HINTS if re.search(p, code, re.I)})
    r["B4"] = {"pts": 2.0 if prng else 0.0, "max": 2.0, "detail": "hints=%s" % prng}

    # B5 - assumptions header
    head = raw[:4000]
    assumptions = bool(re.search(r"assumption", head, re.I)) and bool(
        re.search(r"<!--|/\*", head))
    r["B5"] = {"pts": 2.0 if assumptions else 0.0, "max": 2.0,
               "detail": "assumptions_comment_in_first_4kb=%s" % assumptions}

    # C1 static half - a control labelled like "run tests" exists in the markup
    tests_label = bool(re.search(r"run\s*tests?", raw, re.I))
    r["C1_static"] = {"pts": 2.0 if tests_label else 0.0, "max": 2.0,
                      "detail": "label_present=%s" % tests_label}

    # D1 - a control labelled like "run benchmark" exists (static is sufficient here)
    bench_label = bool(re.search(r"run\s*benchmark", raw, re.I))
    r["D1"] = {"pts": 3.0 if bench_label else 0.0, "max": 3.0,
               "detail": "label_present=%s" % bench_label}

    # informational only, not scored
    todos = len(re.findall(r"//\s*TODO", raw, re.I))
    r["_info"] = {"pts": 0.0, "max": 0.0,
                  "detail": "bytes=%d todo_markers=%d lines=%d"
                            % (len(raw), todos, raw.count("\n") + 1)}
    return r


# --------------------------------------------------------------------------------------
# runtime checks
# --------------------------------------------------------------------------------------

CONTROL_TIERS = [
    "button, input[type=button], input[type=submit], [role=button]",
    "a, label, summary",
    "div, span, li, td",
]


def find_button(page, pattern):
    """Return the best clickable element whose visible label matches pattern, or None.

    Real controls are preferred over generic containers, and within a tier the shortest
    matching label wins - otherwise a wrapping <div> that contains several buttons matches
    first and the click lands on empty space between them.
    """
    rx = re.compile(pattern, re.I)
    for tier in CONTROL_TIERS:
        best, best_len = None, 10 ** 9
        for el in page.query_selector_all(tier):
            try:
                if not el.is_visible():
                    continue
                txt = (el.inner_text() or el.get_attribute("value") or "").strip()
            except Exception:
                continue
            if txt and len(txt) < 60 and rx.search(txt) and len(txt) < best_len:
                best, best_len = el, len(txt)
        if best is not None:
            return best
    return None


HASH_RX = re.compile(r"hash\W{0,12}([0-9a-zA-Z_\-]{6,64})", re.I)


def find_button_in_tabs(page, pattern):
    """find_button, but if the control is hiding inside an inactive tab, switch tabs.

    The prompt asks for Run Tests / Run Benchmark inside a "Dev" panel, and visible-text
    discovery cannot see into a tab that is not active. Try the current view first, then
    click a Dev/Debug-looking tab, then walk every short-labelled control that looks like
    a tab header.
    """
    btn = find_button(page, pattern)
    if btn is not None:
        return btn
    for tab_pat in (r"^dev\w*$", r"^debug$", r"^tests?$"):
        tab = find_button(page, tab_pat)
        if tab is None:
            continue
        try:
            tab.click(timeout=2000)
            page.wait_for_timeout(400)
        except Exception:
            continue
        btn = find_button(page, pattern)
        if btn is not None:
            return btn
    return None


def runtime_checks(path, timeout_ms=15000):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return None, "playwright not installed (pip install playwright && playwright install chromium)"

    url = "file://" + os.path.abspath(path)
    r = {}
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            ctx = browser.new_context(viewport={"width": 1280, "height": 900})
            page = ctx.new_page()
            errors = []
            page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.goto(url, timeout=timeout_ms)
            page.wait_for_timeout(1200)

            # A3 - clean load
            r["A3"] = {"pts": 4.0 if not errors else 0.0, "max": 4.0,
                       "detail": "errors=%d %s" % (len(errors), errors[:3])}

            # C1 runtime half + C2 + C3 - self tests
            btn = find_button_in_tabs(page, r"run\s*tests?")
            r["C1_runtime"] = {"pts": 2.0 if btn else 0.0, "max": 2.0,
                               "detail": "clickable_control=%s" % bool(btn)}
            n_assert, n_fail = 0, None
            if btn:
                before = page.inner_text("body")
                try:
                    btn.click(timeout=4000)
                except Exception:
                    pass
                page.wait_for_timeout(1500)
                after = page.inner_text("body")
                delta = after.replace(before, "") if before in after else after
                n_pass = len(re.findall(r"\bPASS(?:ED)?\b|\bOK\b|(?<![a-z])\u2713", delta, re.I))
                n_fail = len(re.findall(r"\bFAIL(?:ED)?\b|(?<![a-z])\u2717", delta, re.I))
                m = re.search(r"(\d+)\s*/\s*(\d+)\s*(?:tests?|assertions?|passed)", delta, re.I)
                if m:
                    n_pass, n_assert = int(m.group(1)), int(m.group(2))
                    n_fail = n_assert - n_pass
                else:
                    n_assert = n_pass + n_fail
            r["C2"] = {"pts": round(min(n_assert, 15) / 15.0 * 5.0, 1), "max": 5.0,
                       "detail": "assertions_detected=%d" % n_assert}
            r["C3"] = {"pts": 6.0 if (n_assert > 0 and n_fail == 0) else 0.0, "max": 6.0,
                       "detail": "failures_detected=%s" % n_fail}

            # D2 + D3 - benchmark determinism across a full reload
            hashes = []
            for _ in range(2):
                page.goto(url, timeout=timeout_ms)
                page.wait_for_timeout(1000)
                b = find_button_in_tabs(page, r"run\s*benchmark")
                if not b:
                    break
                try:
                    b.click(timeout=4000)
                except Exception:
                    break
                page.wait_for_timeout(2500)
                body = page.inner_text("body")
                m = HASH_RX.search(body)
                hashes.append(m.group(1) if m else None)
            got = [h for h in hashes if h]
            r["D2"] = {"pts": 3.0 if got else 0.0, "max": 3.0, "detail": "hashes=%s" % hashes}
            same = len(got) == 2 and hashes[0] == hashes[1]
            r["D3"] = {"pts": 4.0 if same else 0.0, "max": 4.0, "detail": "identical=%s" % same}

            # E1 - 360px overflow
            page.goto(url, timeout=timeout_ms)
            page.set_viewport_size({"width": 360, "height": 740})
            page.wait_for_timeout(1200)
            sw = page.evaluate("() => document.documentElement.scrollWidth")
            r["E1"] = {"pts": 2.0 if sw <= 372 else 0.0, "max": 2.0, "detail": "scrollWidth=%s" % sw}

            # E2 - End Turn mutates rendered state
            page.set_viewport_size({"width": 1280, "height": 900})
            page.wait_for_timeout(500)
            eb = find_button(page, r"end\s*turn|next\s*turn")
            changed = False
            if eb:
                before = page.inner_text("body")
                try:
                    eb.click(timeout=4000)
                    page.wait_for_timeout(1200)
                    changed = page.inner_text("body") != before
                except Exception:
                    changed = False
            r["E2"] = {"pts": 2.0 if changed else 0.0, "max": 2.0,
                       "detail": "control=%s text_changed=%s" % (bool(eb), changed)}

            browser.close()
    except Exception as exc:  # a crash here is itself a signal, but do not lose the static score
        return r or None, "runtime pass aborted: %s" % exc
    return r, None


# --------------------------------------------------------------------------------------
# scoring / reporting
# --------------------------------------------------------------------------------------

CATEGORY_OF = {
    "A1": "A", "A2": "A", "A3": "A",
    "B1": "B", "B2": "B", "B3": "B", "B4": "B", "B5": "B",
    "C1_static": "C", "C1_runtime": "C", "C2": "C", "C3": "C",
    "D1": "D", "D2": "D", "D3": "D",
    "E1": "E", "E2": "E",
}


F_KEYS = [str(i) for i in range(1, 14)]
G_KEYS = ["G1", "G2", "G3", "G4", "G5"]


def _extract_json(text):
    """Return the last parseable JSON object in text.

    Graders - especially weak ones - wrap their JSON in prose or markdown fences no
    matter what the prompt says, so the whole grader reply can be saved verbatim and
    fed to --merge. Only the final JSON object is used.
    """
    try:
        obj = json.loads(text)
        if isinstance(obj, dict):
            return obj
    except ValueError:
        pass
    decoder = json.JSONDecoder()
    best, i = None, 0
    while True:
        j = text.find("{", i)
        if j < 0:
            break
        try:
            obj, end = decoder.raw_decode(text[j:])
            if isinstance(obj, dict):
                best, i = obj, j + end
                continue
        except ValueError:
            pass
        i = j + 1
    return best


def _as_int(v):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return 0


def _norm_scores(data):
    """Normalize grader key spellings: F may arrive as {"1":..} or {"F1":..}, nested
    under "F"/"G" or flat at the top level. Returns ({"1":..}, {"G1":..})."""
    f, g = {}, {}

    def put(dst, prefix, k, v):
        digits = re.sub(r"\D", "", str(k))
        if digits:
            dst[prefix + digits] = v

    for k, v in (data.get("F") or {}).items():
        put(f, "", k, v)
    for k, v in (data.get("G") or {}).items():
        put(g, "G", k, v)
    if not f:
        for k, v in data.items():
            if re.fullmatch(r"F\d{1,2}", str(k)):
                put(f, "", k, v)
    if not g:
        for k, v in data.items():
            if re.fullmatch(r"G[1-5]", str(k)):
                put(g, "G", k, v)
    return f, g


def load_ai(path):
    """Parse the grader reply. Returns (f_pts, g_pts, data, missing_keys).

    Missing keys score 0 rather than crashing: a grader that skipped an item has
    effectively scored it absent, but the gap is reported so you can regrade."""
    with open(path, encoding="utf-8", errors="replace") as fh:
        text = fh.read()
    data = _extract_json(text)
    if data is None:
        raise SystemExit(
            "error: no JSON object found in %s\n"
            "Save the grader's reply (the whole reply is fine) and pass that file to --merge."
            % path)
    f, g = _norm_scores(data)
    if not f and not g:
        raise SystemExit(
            "error: found JSON in %s but no F/G scores in it.\n"
            "Expected shape: {\"F\": {\"1\": 0-2, ... \"13\": 0-2}, \"G\": {\"G1\": 0-4, ... \"G5\": 0-4}}"
            % path)
    missing = [("F" + k) for k in F_KEYS if k not in f] + [k for k in G_KEYS if k not in g]
    f_pts = sum(min(2, max(0, _as_int(f.get(k)))) for k in F_KEYS)
    g_pts = sum(min(4, max(0, _as_int(g.get(k)))) for k in G_KEYS)
    return f_pts, g_pts, data, missing


def grade(path, use_runtime, merge_path):
    with open(path, encoding="utf-8", errors="replace") as fh:
        raw = fh.read()

    checks = static_checks(raw)
    runtime_note = None
    if use_runtime:
        rt, runtime_note = runtime_checks(path)
        if rt:
            checks.update(rt)

    det_pts = sum(v["pts"] for k, v in checks.items() if k in CATEGORY_OF)
    det_max = sum(v["max"] for k, v in checks.items() if k in CATEGORY_OF)

    cats = {}
    for k, v in checks.items():
        c = CATEGORY_OF.get(k)
        if not c:
            continue
        cats.setdefault(c, [0.0, 0.0])
        cats[c][0] += v["pts"]
        cats[c][1] += v["max"]

    out = {
        "candidate": os.path.basename(path),
        "deterministic_points": round(det_pts, 1),
        "deterministic_max": round(det_max, 1),
        "runtime_pass": bool(use_runtime and runtime_note is None),
        "runtime_note": runtime_note,
        "categories": {c: {"pts": round(v[0], 1), "max": round(v[1], 1)} for c, v in sorted(cats.items())},
        "checks": checks,
    }

    if merge_path:
        f_pts, g_pts, ai_raw, ai_missing = load_ai(merge_path)
        out["ai_points"] = f_pts + g_pts
        out["ai_max"] = AI_TOTAL
        out["ai_detail"] = ai_raw
        out["ai_missing_keys"] = ai_missing
        out["total"] = round(det_pts + f_pts + g_pts, 1)
        out["scored_out_of"] = round(det_max + AI_TOTAL, 1)
    else:
        out["total"] = round(det_pts, 1)
        out["scored_out_of"] = round(det_max, 1)
    return out


def print_grade(g):
    print("=" * 68)
    print("ASHFALL EVAL  |  %s" % g["candidate"])
    print("=" * 68)
    for cid, v in g["categories"].items():
        bar = "#" * int(round(v["pts"] / max(v["max"], 0.001) * 20))
        print("  %-2s  %5.1f / %-5.1f  %s" % (cid, v["pts"], v["max"], bar))
    if "ai_points" in g:
        print("  F+G %5.1f / %-5.1f  (model-graded)" % (g["ai_points"], g["ai_max"]))
        if g.get("ai_missing_keys"):
            print("  warning: grader skipped %s - scored as 0, consider regrading"
                  % ",".join(g["ai_missing_keys"]))
    print("-" * 68)
    print("  TOTAL %.1f / %.1f" % (g["total"], g["scored_out_of"]))
    if g["runtime_note"]:
        print("  note: %s" % g["runtime_note"])
    if not g["runtime_pass"]:
        print("  note: runtime checks not scored - do not compare against runtime-scored runs")
    print("-" * 68)
    for k, v in g["checks"].items():
        if k == "_info":
            print("  info  %s" % v["detail"])
            continue
        print("  %-11s %4.1f/%-4.1f  %s" % (k, v["pts"], v["max"], v["detail"][:90]))
    print()


def report(dirpath):
    rows = []
    for p in sorted(glob.glob(os.path.join(dirpath, "*.eval.json"))):
        with open(p) as fh:
            g = json.load(fh)
        rows.append(g)
    if not rows:
        print("no *.eval.json files in %s" % dirpath)
        return
    rows.sort(key=lambda r: -r["total"])
    print("%-34s %8s %8s %8s" % ("candidate", "det", "ai", "total"))
    print("-" * 62)
    for g in rows:
        print("%-34s %8s %8s %7s/%s" % (
            g["candidate"][:34],
            "%.1f" % g["deterministic_points"],
            ("%.1f" % g["ai_points"]) if "ai_points" in g else "-",
            "%.1f" % g["total"], "%.0f" % g["scored_out_of"]))


def main():
    ap = argparse.ArgumentParser(description="Deterministic scorer for the Ashfall Outpost eval.")
    ap.add_argument("candidate", nargs="?", help="path to the model's HTML output")
    ap.add_argument("--runtime", action="store_true", help="run headless browser checks (needs playwright)")
    ap.add_argument("--merge", help="path to the AI grader's JSON reply, to produce a score out of 100")
    ap.add_argument("--report", help="print a comparison table of *.eval.json in this directory")
    ap.add_argument("--no-write", action="store_true", help="do not write <candidate>.eval.json")
    a = ap.parse_args()

    if a.report:
        report(a.report)
        return 0
    if not a.candidate:
        ap.print_help()
        return 1
    if not os.path.isfile(a.candidate):
        print("no such file: %s" % a.candidate, file=sys.stderr)
        return 1
    if a.merge and not os.path.isfile(a.merge):
        print("no such file: %s (expected the saved grader reply)" % a.merge, file=sys.stderr)
        return 1

    g = grade(a.candidate, a.runtime, a.merge)
    out = None
    if not a.no_write:
        # written before printing so a truncated or piped stdout cannot lose the result
        out = re.sub(r"\.html?$", "", a.candidate) + ".eval.json"
        with open(out, "w") as fh:
            json.dump(g, fh, indent=2)
    print_grade(g)
    if out:
        print("wrote %s" % out)
    return 0


if __name__ == "__main__":
    sys.exit(main())


