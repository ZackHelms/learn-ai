#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""Render generated blocks from models/roster.yaml into the markdown docs.

Why this exists
---------------
Model names, tags and sizes go stale fast. If they are sprinkled through prose,
updating them means hunting version strings across a growing pile of markdown
and getting it wrong somewhere. So: prose never hardcodes them. `roster.yaml` is
the only place they live, and this script injects generated tables into markdown
between marker comments:

    <!-- BEGIN GENERATED: roster -->
    ...anything here is overwritten...
    <!-- END GENERATED: roster -->

Usage
-----
    uv run scripts/render-roster.py            # rewrite generated blocks in place
    uv run scripts/render-roster.py --check    # exit 1 if anything is stale (CI)
    uv run scripts/render-roster.py --list     # list known block names

If you do not have `uv`, `python3 scripts/render-roster.py` works too as long as
PyYAML is installed.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
ROSTER_PATH = REPO_ROOT / "models" / "roster.yaml"

# Matches a generated block and captures (name, body). DOTALL so the body can
# span lines; non-greedy so adjacent blocks do not get swallowed into one match.
#
# The end marker's leading newline is optional in the pattern but always
# re-emitted, so a block normalizes to:
#
#     <!-- BEGIN GENERATED: name -->
#     ...body...
#     <!-- END GENERATED: name -->
#
# regardless of whether the block started out empty.
BLOCK_RE = re.compile(
    r"(?P<begin><!-- BEGIN GENERATED: (?P<name>[a-z0-9-]+) -->\n)"
    r"(?P<body>.*?)"
    r"\n?(?P<end><!-- END GENERATED: (?P=name) -->)",
    re.DOTALL,
)

# A fence opens or closes on a line starting with ``` or ~~~ (optionally
# indented). Markers inside a fence are DOCUMENTATION of the syntax, not live
# blocks -- docs/STYLE.md and AGENTS.md both show an empty block as an example,
# and rendering into those would be wrong.
FENCE_RE = re.compile(r"^[ \t]*(?:```|~~~)", re.MULTILINE)


def fenced_spans(text: str) -> list[tuple[int, int]]:
    """Character ranges covered by fenced code blocks."""
    fences = [m.start() for m in FENCE_RE.finditer(text)]
    # Pair them up: 1st opens, 2nd closes, and so on. An unclosed final fence
    # is treated as running to end of file.
    spans = []
    for i in range(0, len(fences), 2):
        start = fences[i]
        end = fences[i + 1] if i + 1 < len(fences) else len(text)
        spans.append((start, end))
    return spans

TOOL_CALLING_LABEL = {
    "weak": "weak",
    "partial": "partial",
    "native": "native",
    "strong": "native, strong",
}


def load_roster() -> dict:
    with ROSTER_PATH.open() as fh:
        return yaml.safe_load(fh)


def core_models(roster: dict) -> list[dict]:
    """Everything the course actually depends on -- excludes optional stretch."""
    return [m for m in roster["models"] if not m.get("optional")]


def _rung(model: dict) -> str:
    return str(model["rung"])


# --------------------------------------------------------------------------
# Block renderers. Each takes the parsed roster and returns markdown WITHOUT
# a trailing newline. Register them in BLOCKS at the bottom.
# --------------------------------------------------------------------------


def render_roster_table(roster: dict) -> str:
    rows = [
        "| Rung | Model | Params | Vendor | License | Tool calling | Disk (est.) |",
        "|---|---|---|---|---|---|---|",
    ]
    for m in roster["models"]:
        name = m["display_name"]
        if m.get("optional"):
            name = f"{name} _(optional)_"
        rows.append(
            f"| {_rung(m)} | {name} | {m['params']} | {m['vendor']} "
            f"| {m['license']} | {TOOL_CALLING_LABEL[m['native_tool_calling']]} "
            f"| ~{m['disk_gb']} GB |"
        )
    return "\n".join(rows)


def render_roster_why(roster: dict) -> str:
    """The 'why is this model here' list. This is the pedagogically important
    one -- the table above says what, this says why."""
    parts = []
    for m in roster["models"]:
        label = f"**{m['display_name']}** (rung {_rung(m)})"
        why = " ".join(m["why"].split())
        parts.append(f"- {label} — {why}")
    return "\n".join(parts)


def render_pull_commands(roster: dict) -> str:
    lines = ["```bash"]
    for m in core_models(roster):
        lines.append(f"ollama pull {m['ollama_tag']}")
    lines.append("```")

    optional = [m for m in roster["models"] if m.get("optional")]
    if optional:
        lines.append("")
        lines.append("Optional, only if you have the headroom:")
        lines.append("")
        lines.append("```bash")
        for m in optional:
            lines.append(f"ollama pull {m['ollama_tag']}")
        lines.append("```")
    return "\n".join(lines)


def render_budget(roster: dict) -> str:
    b = roster["budget"]
    core = core_models(roster)
    core_disk = sum(m["disk_gb"] for m in core)
    biggest = max(core, key=lambda m: m["min_ram_gb"])
    return "\n".join(
        [
            f"- **Total RAM assumed:** {b['total_ram_gb']} GB",
            f"- **Usable for a model:** ~{b['usable_ram_gb']} GB "
            "(after OS, editor and a browser — this is the number that actually binds)",
            f"- **Disk for the core roster:** ~{core_disk:.1f} GB "
            f"({len(core)} models); budget {b['disk_gb']} GB to be comfortable",
            f"- **Largest core model:** {biggest['display_name']} at "
            f"~{biggest['min_ram_gb']} GB resident",
        ]
    )


def render_provenance(roster: dict) -> str:
    p = roster["provenance"]
    return "\n".join(
        [
            f"> **Where these numbers come from.** {' '.join(p['sizes'].split())}",
            ">",
            f"> {' '.join(p['tags'].split())}",
            ">",
            f"> Roster last verified against upstream: `{roster['roster_last_verified']}`.",
        ]
    )


BLOCKS = {
    "roster": render_roster_table,
    "roster-why": render_roster_why,
    "roster-pull": render_pull_commands,
    "roster-budget": render_budget,
    "roster-provenance": render_provenance,
}


def markdown_files() -> list[Path]:
    return sorted(
        p
        for p in REPO_ROOT.rglob("*.md")
        if ".git" not in p.parts and "node_modules" not in p.parts
    )


def process(check_only: bool) -> int:
    roster = load_roster()
    stale: list[str] = []
    written: list[str] = []
    unknown: list[str] = []

    for path in markdown_files():
        original = path.read_text()
        spans = fenced_spans(original)

        def replace(match: re.Match) -> str:
            # Leave example markers inside fenced code blocks alone.
            if any(lo <= match.start() < hi for lo, hi in spans):
                return match.group(0)
            name = match.group("name")
            if name not in BLOCKS:
                unknown.append(f"{path.relative_to(REPO_ROOT)}: {name}")
                return match.group(0)
            new_body = BLOCKS[name](roster)
            return match.group("begin") + new_body + "\n" + match.group("end")

        updated = BLOCK_RE.sub(replace, original)
        if updated == original:
            continue

        rel = str(path.relative_to(REPO_ROOT))
        if check_only:
            stale.append(rel)
        else:
            path.write_text(updated)
            written.append(rel)

    for u in unknown:
        print(f"warning: unknown generated block -> {u}", file=sys.stderr)

    if check_only:
        if stale:
            print("Generated blocks are stale in:", file=sys.stderr)
            for s in stale:
                print(f"  {s}", file=sys.stderr)
            print(
                "\nRun: uv run scripts/render-roster.py",
                file=sys.stderr,
            )
            return 1
        print("All generated blocks are up to date.")
        return 0

    if written:
        for w in written:
            print(f"updated {w}")
    else:
        print("No changes; everything already up to date.")
    return 1 if unknown else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--check",
        action="store_true",
        help="do not write; exit non-zero if any generated block is stale",
    )
    parser.add_argument(
        "--list", action="store_true", help="list known generated block names"
    )
    args = parser.parse_args()

    if args.list:
        for name in BLOCKS:
            print(name)
        return 0

    if not ROSTER_PATH.exists():
        print(f"error: {ROSTER_PATH} not found", file=sys.stderr)
        return 2

    return process(check_only=args.check)


if __name__ == "__main__":
    raise SystemExit(main())
