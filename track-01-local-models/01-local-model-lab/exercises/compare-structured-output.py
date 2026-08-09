#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""Exercise A, automated: ask every roster model for structured JSON and check
mechanically whether it complied.

    uv run track-01-local-models/01-local-model-lab/exercises/compare-structured-output.py

Why this is worth automating
----------------------------
Running the prompt by hand once per model tells you very little, because small
models are inconsistent run to run. One good answer is not evidence. This runs
each model N times and reports a rate.

The moment you count passes instead of eyeballing output, you have written an
eval. That is all an eval is. Module 03 formalizes this; here it is in ~40 lines
of checking logic so the idea arrives before the vocabulary.

Note what is being measured: **format compliance, not correctness.** Whether the
population figure is right is a separate and much harder question. Structural
validity is cheap to check, and on small models it is the thing that breaks
first.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
ROSTER_PATH = REPO_ROOT / "models" / "roster.yaml"
HOST = "http://localhost:11434"

PROMPT = """Return ONLY valid JSON, no other text, matching this shape:
{"name": string, "population": number, "country": string}
for the city of Lyon."""

REQUIRED_KEYS = {"name", "population", "country"}

# A fenced code block is the most common near-miss: the JSON is fine, but it is
# wrapped. We record that separately from outright invalid output, because the
# two have completely different fixes -- one is a prompting problem, the other
# may need a bigger model or constrained decoding.
FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL)


def chat(model: str, prompt: str, timeout: int = 300) -> str:
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
        "stream": False,
    }
    req = urllib.request.Request(
        f"{HOST}/v1/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = json.loads(resp.read())
    return body["choices"][0]["message"]["content"]


def grade(raw: str) -> dict:
    """Grade one response. Returns the checks that make up a simple eval."""
    result = {
        "clean": False,      # parsed with no unwrapping needed
        "fenced": False,     # valid JSON, but wrapped in a code fence
        "valid": False,      # parsed at all, by any route
        "keys_ok": False,    # exactly the required keys
        "types_ok": False,   # population is actually a number
        "error": None,
    }

    text = raw.strip()

    parsed = None
    try:
        parsed = json.loads(text)
        result["clean"] = True
    except json.JSONDecodeError:
        m = FENCE_RE.search(text)
        if m:
            try:
                parsed = json.loads(m.group(1))
                result["fenced"] = True
            except json.JSONDecodeError as exc:
                result["error"] = f"fenced but unparseable: {exc.msg}"
        else:
            result["error"] = "not JSON"

    if parsed is None:
        return result

    result["valid"] = True

    if not isinstance(parsed, dict):
        result["error"] = f"JSON but not an object ({type(parsed).__name__})"
        return result

    keys = set(parsed)
    result["keys_ok"] = keys == REQUIRED_KEYS
    if not result["keys_ok"]:
        missing = REQUIRED_KEYS - keys
        extra = keys - REQUIRED_KEYS
        bits = []
        if missing:
            bits.append(f"missing {sorted(missing)}")
        if extra:
            bits.append(f"extra {sorted(extra)}")
        result["error"] = ", ".join(bits)

    result["types_ok"] = isinstance(parsed.get("population"), (int, float)) and not (
        isinstance(parsed.get("population"), bool)
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--runs", type=int, default=5, help="attempts per model")
    parser.add_argument("--include-optional", action="store_true")
    parser.add_argument("--show-output", action="store_true",
                        help="print the raw response from each first run")
    args = parser.parse_args()

    roster = yaml.safe_load(ROSTER_PATH.read_text())
    models = roster["models"]
    if not args.include_optional:
        models = [m for m in models if not m.get("optional")]

    try:
        urllib.request.urlopen(f"{HOST}/api/version", timeout=5)
    except Exception:
        sys.exit(f"error: no Ollama at {HOST}. Start it with:  ollama serve")

    print(f"Asking each model for structured JSON, {args.runs} runs each.\n")

    rows = []
    for m in models:
        tag = m["ollama_tag"]
        print(f"  {m['display_name']} ...", file=sys.stderr)

        grades = []
        first_raw = None
        for i in range(args.runs):
            try:
                raw = chat(tag, PROMPT)
            except Exception as exc:  # noqa: BLE001
                grades.append({"error": str(exc)[:80], "valid": False,
                               "clean": False, "fenced": False,
                               "keys_ok": False, "types_ok": False})
                continue
            if i == 0:
                first_raw = raw
            grades.append(grade(raw))

        n = len(grades) or 1
        rows.append({
            "name": m["display_name"],
            "rung": m["rung"],
            "clean": sum(g["clean"] for g in grades) / n,
            "valid": sum(g["valid"] for g in grades) / n,
            "keys": sum(g["keys_ok"] for g in grades) / n,
            "types": sum(g["types_ok"] for g in grades) / n,
            "errors": [g["error"] for g in grades if g.get("error")],
        })

        if args.show_output and first_raw is not None:
            print(f"\n--- {m['display_name']} first response ---")
            print(first_raw)
            print("--- end ---\n")

    print()
    print("| Rung | Model | Clean JSON | Parseable | Keys OK | Types OK |")
    print("|---|---|---|---|---|---|")
    for r in rows:
        print(
            f"| {r['rung']} | {r['name']} | {r['clean']:.0%} | {r['valid']:.0%} "
            f"| {r['keys']:.0%} | {r['types']:.0%} |"
        )

    print()
    print("Clean JSON = parsed with no unwrapping. Parseable = parsed after")
    print("stripping a code fence. The gap between those two columns is a")
    print("prompting problem. A low 'Parseable' number is a model problem.")
    print()

    distinct = {e for r in rows for e in r["errors"]}
    if distinct:
        print("Failure modes seen:")
        for e in sorted(distinct)[:12]:
            print(f"  - {e}")
        print()

    print("Paste this table into the module's FIELD-NOTES.md.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
