#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""Benchmark the roster on YOUR machine and print a table you can paste into
a module's FIELD-NOTES.md.

Why measure it yourself
-----------------------
Published tokens/sec numbers are close to meaningless across machines: core
count, memory bandwidth, vector extensions, thermal headroom and what else is
running all move the result by multiples. This repo therefore ships no
benchmark numbers of its own. It ships this script instead.

We do not wall-clock the request. Ollama reports its own timing counters
(`eval_count`, `eval_duration`, `load_duration`, ...), which separate model
LOAD time from PROMPT PROCESSING time from GENERATION time. Those three behave
very differently and averaging them into one number hides the interesting part.

Usage
-----
    uv run scripts/bench.py                    # whole core roster
    uv run scripts/bench.py --model granite-8b # one model, by roster id
    uv run scripts/bench.py --include-optional # include stretch models
    uv run scripts/bench.py --repeat 3         # average over N runs
    uv run scripts/bench.py --json             # machine-readable output
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
ROSTER_PATH = REPO_ROOT / "models" / "roster.yaml"
DEFAULT_HOST = "http://localhost:11434"

# Deliberately boring and deterministic-ish: we are measuring throughput, not
# quality. Long enough to get past warmup, short enough to not take all day on
# a slow CPU.
PROMPT = (
    "Write a short paragraph explaining what a checksum is, "
    "in plain language, for someone who has never heard the term."
)
NUM_PREDICT = 120

NS_PER_S = 1_000_000_000


@dataclass
class Run:
    load_s: float
    prompt_tokens: int
    prompt_s: float
    gen_tokens: int
    gen_s: float

    @property
    def gen_tps(self) -> float:
        return self.gen_tokens / self.gen_s if self.gen_s > 0 else 0.0

    @property
    def prompt_tps(self) -> float:
        return self.prompt_tokens / self.prompt_s if self.prompt_s > 0 else 0.0


@dataclass
class Result:
    model_id: str
    display_name: str
    tag: str
    runs: list[Run] = field(default_factory=list)
    resident_bytes: int | None = None
    error: str | None = None

    @property
    def gen_tps(self) -> float:
        return statistics.mean(r.gen_tps for r in self.runs) if self.runs else 0.0

    @property
    def prompt_tps(self) -> float:
        return statistics.mean(r.prompt_tps for r in self.runs) if self.runs else 0.0

    @property
    def load_s(self) -> float:
        # First run only: later runs hit a warm model, so averaging load time
        # across runs would report a meaningless near-zero.
        return self.runs[0].load_s if self.runs else 0.0


def api(host: str, path: str, payload: dict | None = None, timeout: int = 600) -> dict:
    url = f"{host}{path}"
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST" if data else "GET",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())


def check_service(host: str) -> None:
    try:
        version = api(host, "/api/version", timeout=5).get("version", "?")
    except Exception:
        sys.exit(
            f"error: no Ollama at {host}\n"
            "  Start it with:  ollama serve\n"
            "  Or check the service:  systemctl status ollama"
        )
    print(f"Ollama {version} at {host}", file=sys.stderr)


def installed_tags(host: str) -> set[str]:
    try:
        models = api(host, "/api/tags", timeout=10).get("models", [])
    except Exception:
        return set()
    tags = set()
    for m in models:
        name = m.get("name", "")
        tags.add(name)
        # Ollama reports "foo:latest"; a bare "foo" in the roster should match.
        if name.endswith(":latest"):
            tags.add(name.rsplit(":", 1)[0])
    return tags


def resident_size(host: str, tag: str) -> int | None:
    """How much memory the model actually occupies right now, per Ollama."""
    try:
        for m in api(host, "/api/ps", timeout=10).get("models", []):
            name = m.get("name", "")
            if name == tag or name.rsplit(":", 1)[0] == tag.rsplit(":", 1)[0]:
                return m.get("size")
    except Exception:
        pass
    return None


def one_run(host: str, tag: str) -> Run:
    resp = api(
        host,
        "/api/generate",
        {
            "model": tag,
            "prompt": PROMPT,
            "stream": False,
            "options": {"num_predict": NUM_PREDICT, "temperature": 0},
        },
    )
    return Run(
        load_s=resp.get("load_duration", 0) / NS_PER_S,
        prompt_tokens=resp.get("prompt_eval_count", 0),
        prompt_s=resp.get("prompt_eval_duration", 0) / NS_PER_S,
        gen_tokens=resp.get("eval_count", 0),
        gen_s=resp.get("eval_duration", 0) / NS_PER_S,
    )


def bench_model(host: str, model: dict, repeat: int, present: set[str]) -> Result:
    tag = model["ollama_tag"]
    result = Result(model["id"], model["display_name"], tag)

    if present and tag not in present:
        result.error = "not pulled"
        return result

    for i in range(repeat):
        try:
            result.runs.append(one_run(host, tag))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode(errors="replace")[:200]
            result.error = f"HTTP {exc.code}: {body}"
            return result
        except Exception as exc:  # noqa: BLE001 - surface whatever went wrong
            result.error = str(exc)[:200]
            return result
        if i == 0:
            result.resident_bytes = resident_size(host, tag)

    return result


def human_gb(n: int | None) -> str:
    return f"{n / 1024**3:.1f} GB" if n else "—"


def render_table(results: list[Result]) -> str:
    lines = [
        "| Model | Gen tok/s | Prompt tok/s | Cold load | Resident |",
        "|---|---|---|---|---|",
    ]
    for r in results:
        if r.error:
            lines.append(f"| {r.display_name} | _{r.error}_ | — | — | — |")
        else:
            lines.append(
                f"| {r.display_name} | {r.gen_tps:.1f} | {r.prompt_tps:.1f} "
                f"| {r.load_s:.1f}s | {human_gb(r.resident_bytes)} |"
            )
    return "\n".join(lines)


def machine_note() -> str:
    cores = "?"
    try:
        import os

        cores = str(os.cpu_count() or "?")
    except Exception:
        pass
    mem = "?"
    try:
        with open("/proc/meminfo") as fh:
            for line in fh:
                if line.startswith("MemTotal:"):
                    mem = f"{int(line.split()[1]) / 1024 / 1024:.0f} GB"
                    break
    except Exception:
        pass
    return f"{cores} cores, {mem} RAM, measured {time.strftime('%Y-%m-%d')}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--model", help="roster id to benchmark (default: all core)")
    parser.add_argument("--repeat", type=int, default=1, help="runs per model")
    parser.add_argument("--include-optional", action="store_true")
    parser.add_argument("--json", action="store_true", help="emit JSON not markdown")
    args = parser.parse_args()

    roster = yaml.safe_load(ROSTER_PATH.read_text())
    models = roster["models"]

    if args.model:
        models = [m for m in models if m["id"] == args.model]
        if not models:
            ids = ", ".join(m["id"] for m in roster["models"])
            sys.exit(f"error: no model with id '{args.model}'. Known ids: {ids}")
    elif not args.include_optional:
        models = [m for m in models if not m.get("optional")]

    check_service(args.host)
    present = installed_tags(args.host)

    results = []
    for m in models:
        print(f"  benchmarking {m['display_name']} ...", file=sys.stderr)
        results.append(bench_model(args.host, m, args.repeat, present))

    if args.json:
        print(
            json.dumps(
                {
                    "machine": machine_note(),
                    "results": [
                        {
                            "id": r.model_id,
                            "tag": r.tag,
                            "gen_tps": round(r.gen_tps, 2),
                            "prompt_tps": round(r.prompt_tps, 2),
                            "cold_load_s": round(r.load_s, 2),
                            "resident_bytes": r.resident_bytes,
                            "error": r.error,
                        }
                        for r in results
                    ],
                },
                indent=2,
            )
        )
        return 0

    print()
    print(render_table(results))
    print()
    print(f"_Measured on: {machine_note()}_")
    print()
    print(
        "Paste the table above into the FIELD-NOTES.md for the module you are on.\n"
        "Numbers only mean something next to the machine that produced them."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
