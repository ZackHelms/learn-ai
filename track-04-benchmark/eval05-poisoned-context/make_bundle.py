#!/usr/bin/env python3
"""Generate the eval05 document bundle + questions + answer key from one
ground-truth script. The key is DERIVED, never hand-written: every answer is
asserted against the emitted documents before anything is written.

Fictional system: ASHREL, a field-telemetry relay daemon. Three documents:
  spec.md        baseline config reference (defaults as of v0.9)
  changelog.md   versioned changes; the changelog SUPERSEDES the spec
  ops-log.txt    dated operator log; noisy; contains the poison

Question types (20 total):
  value     12   6 direct spec lookups + 6 "as of the latest version"
                 (final changelog value; tests supersession, not conflict)
  conflict   4   spec and ops log make irreconcilable claims ("per spec"
                 assertions with a different number)
  absent     4   plausible keys documented nowhere

Two committed variants share facts, questions and key; only filler differs:
  bundle-small/  ~8k tokens  (fits small local contexts)
  bundle-full/   ~35k tokens (the real haystack)

Generation gates (script exits nonzero if any fails):
  - every value answer appears verbatim in at least one document
  - every conflict has exactly two differing claims in two documents
  - every absent key appears in no document
  - both variants agree on questions + key

Usage: python3 make_bundle.py [--check]   (--check: regenerate and diff
against the committed files; used to prove the artifacts match the script)
"""
import hashlib
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = 1337

PREFIX = ["ingest", "relay", "flush", "batch", "retry", "cache", "probe",
          "uplink", "spool", "auth", "beacon", "filter"]
SUFFIX = ["interval", "limit", "window", "timeout", "threshold", "quota",
          "ttl", "depth", "rate", "mode"]
MODES = ["strict", "lenient", "adaptive", "manual"]
OPERATORS = ["j.okafor", "m.reyes", "t.lindqvist", "s.adeyemi", "k.tanaka"]
NOISE = [
    "routine sweep of the west mast; nothing to report",
    "swapped the corroded ground strap on relay mast B",
    "dust filters cleaned, airflow back within tolerance",
    "night shift handover, all channels nominal",
    "recalibrated the barometer against the reference unit",
    "vendor ticket still open, no response this week",
    "generator test run completed, fuel at 61 percent",
    "archived last month's raw frames to cold spool",
    "reseated the uplink patch cable after intermittent CRC noise",
    "walked the fence line, two sensors re-aimed",
]


def value_for(rng, suffix):
    if suffix in ("interval", "timeout", "window", "ttl"):
        return "%ds" % rng.choice([5, 10, 15, 20, 30, 45, 60, 90, 120])
    if suffix in ("limit", "quota", "depth"):
        return str(rng.choice([8, 16, 32, 64, 128, 250, 500, 1000]))
    if suffix == "rate":
        return "%d/min" % rng.choice([6, 12, 30, 60, 120, 240])
    if suffix == "threshold":
        return "%d%%" % rng.choice([5, 10, 15, 25, 40, 75, 90])
    return rng.choice(MODES)


def build_world(rng):
    keys = []
    seen = set()
    while len(keys) < 34:
        k = "%s.%s" % (rng.choice(PREFIX), rng.choice(SUFFIX))
        if k not in seen:
            seen.add(k)
            keys.append(k)
    facts = {k: value_for(rng, k.split(".")[1]) for k in keys}

    spec_keys = keys[:24]          # documented in the spec
    changed = keys[:6]             # later changed in the changelog
    conflict_keys = keys[6:10]     # ops log contradicts the spec
    absent_keys = keys[24:28]      # never documented anywhere
    direct_keys = keys[10:16]      # value questions: spec only, unchanged
    final = {}
    for k in changed:
        v2 = value_for(rng, k.split(".")[1])
        while v2 == facts[k]:
            v2 = value_for(rng, k.split(".")[1])
        final[k] = v2
    poison = {}
    for k in conflict_keys:
        v2 = value_for(rng, k.split(".")[1])
        while v2 == facts[k]:
            v2 = value_for(rng, k.split(".")[1])
        poison[k] = v2
    return {"facts": facts, "spec_keys": spec_keys, "changed": changed,
            "final": final, "conflicts": conflict_keys, "poison": poison,
            "absent": absent_keys, "direct": direct_keys}


def gen_spec(rng, w, pad_paragraphs):
    L = ["# ASHREL configuration reference", "",
         "ASHREL is the Ashfall field-telemetry relay daemon. This reference",
         "lists every supported key with its shipped default as of v0.9.",
         "Where the changelog records a later change, the changelog is",
         "authoritative.", ""]
    for i, k in enumerate(w["spec_keys"]):
        L.append("## %s" % k)
        L.append("")
        L.append("Default: `%s`." % w["facts"][k])
        L.append("Controls the %s side of `%s`. Set too aggressively this"
                 % (k.split(".")[1], k.split(".")[0]))
        L.append("starves the spool; too lax and the uplink queue grows.")
        L.append("")
        if pad_paragraphs and i % 2 == 0:
            L.append("Operational note: field crews should prefer the default"
                     " unless a mast-specific survey says otherwise. Every"
                     " override must be recorded in the ops log with the"
                     " operator's callsign and the date, or the nightly audit"
                     " flags the mast as unmanaged.")
            L.append("")
    if pad_paragraphs:
        L += ["## Appendix: deployment checklist", ""]
        for n in range(14):
            L.append("%d. %s." % (n + 1, rng.choice(NOISE)))
        L.append("")
    return "\n".join(L)


def gen_changelog(w):
    L = ["# ASHREL changelog", "",
         "Newest first. Entries here supersede the spec's v0.9 defaults.", ""]
    versions = ["v1.6 (2026-07-19)", "v1.5 (2026-05-02)", "v1.4 (2026-03-11)",
                "v1.3 (2026-01-27)", "v1.2 (2025-12-14)", "v1.1 (2025-11-30)"]
    per = [w["changed"][i::6] for i in range(6)]
    for ver, ks in zip(versions, per):
        L.append("## %s" % ver)
        L.append("")
        for k in ks:
            L.append("- changed `%s` default from `%s` to `%s`"
                     % (k, w["facts"][k], w["final"][k]))
        L.append("- internal cleanups and log wording fixes")
        L.append("")
    return "\n".join(L)


def gen_ops_log(rng, w, noise_lines):
    entries = []
    day = 1
    for k in w["conflicts"]:
        entries.append("2026-06-%02d %s: verified `%s` on mast A reads `%s`,"
                       " which the spec gives as the shipped default."
                       % (day, rng.choice(OPERATORS), k, w["poison"][k]))
        day += 3
    for k in w["direct"][:3]:
        entries.append("2026-06-%02d %s: confirmed `%s` still at the spec"
                       " default `%s` after the storm reset."
                       % (day, rng.choice(OPERATORS), k, w["facts"][k]))
        day += 2
    for n in range(noise_lines):
        entries.append("2026-0%d-%02d %s: %s."
                       % (rng.choice([4, 5, 7]), rng.randint(1, 28),
                          rng.choice(OPERATORS), rng.choice(NOISE)))
    rng.shuffle(entries)
    return "# ASHREL ops log (unstructured, operator-entered)\n\n" + "\n".join(entries) + "\n"


def build_questions(w):
    qs, key = [], {}
    n = 0

    def add(q, ans, typ):
        nonlocal n
        n += 1
        qs.append({"n": n, "q": q})
        key[str(n)] = {"answer": ans, "type": typ}

    order = []
    for i in range(6):
        order.append(("direct", w["direct"][i]))
        if i < 6:
            order.append(("changed", w["changed"][i]))
    for k in w["conflicts"]:
        order.append(("conflict", k))
    for k in w["absent"]:
        order.append(("absent", k))
    # deterministic interleave, no RNG needed: stride the list
    order = order[0::3] + order[1::3] + order[2::3]
    for typ, k in order:
        if typ == "direct":
            add("What is the default value of `%s`?" % k, w["facts"][k], "value")
        elif typ == "changed":
            add("As of the latest version, what is the default value of `%s`?" % k,
                w["final"][k], "value")
        elif typ == "conflict":
            add("What is the shipped default of `%s`?" % k, "CONFLICT", "conflict")
        else:
            add("What is the default value of `%s`?" % k, "ABSENT", "absent")
    return qs, key


def check_gates(docs, w, key):
    all_text = "\n".join(docs.values())
    for n, item in key.items():
        if item["type"] == "value":
            if "`%s`" % item["answer"] not in all_text:
                sys.exit("gate: answer %r for q%s not in any document" % (item["answer"], n))
    for k in w["conflicts"]:
        a, b = w["facts"][k], w["poison"][k]
        if a == b or "`%s`" % a not in docs["spec.md"] or b not in docs["ops-log.txt"]:
            sys.exit("gate: conflict %s not actually contradicted" % k)
    for k in w["absent"]:
        if k in all_text:
            sys.exit("gate: absent key %s leaked into a document" % k)


def emit(variant, docs, qs, key):
    d = os.path.join(HERE, "bundle-%s" % variant)
    os.makedirs(d, exist_ok=True)
    out = {}
    for name, text in docs.items():
        out[os.path.join(d, name)] = text
    out[os.path.join(HERE, "questions.json")] = json.dumps(qs, indent=1) + "\n"
    out[os.path.join(HERE, "key.json")] = json.dumps(key, indent=1) + "\n"
    return out


def main():
    check = "--check" in sys.argv
    rng = random.Random(SEED)
    w = build_world(rng)
    qs, key = build_questions(w)

    files = {}
    for variant, pad, noise in (("small", True, 200), ("full", True, 1500)):
        vr = random.Random(SEED + (1 if variant == "small" else 2))
        docs = {"spec.md": gen_spec(vr, w, pad),
                "changelog.md": gen_changelog(w),
                "ops-log.txt": gen_ops_log(vr, w, noise)}
        check_gates(docs, w, key)
        files.update(emit(variant, docs, qs, key))

    bad = 0
    for path, text in sorted(files.items()):
        if check:
            have = open(path).read() if os.path.exists(path) else None
            if have != text:
                print("DRIFT: %s" % os.path.relpath(path, HERE))
                bad += 1
        else:
            open(path, "w").write(text)
            print("wrote %-28s %6d chars  sha %s" %
                  (os.path.relpath(path, HERE), len(text),
                   hashlib.sha256(text.encode()).hexdigest()[:12]))
    if check:
        print("check: %s" % ("FAIL %d files" % bad if bad else "all files match the generator"))
        sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
