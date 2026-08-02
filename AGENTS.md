# AGENTS.md

Instructions for any AI agent working in this repository — Claude Code, Codex,
Copilot, Cursor, or anything else.

**This file is the source of truth.** `CLAUDE.md` imports it and adds only
Claude-Code-specific notes. Put changes here, not there. See
[ADR 0004](docs/decisions/0004-agents-md-source-of-truth.md).

## What this repo is

A hands-on curriculum for learning **agentic AI with locally hosted models**.
Written as a lab notebook by someone learning the material while writing it, not
as a textbook by an expert.

Two premises drive nearly every decision:

1. **Deliberately weak models are better teaching tools.** Small CPU-bound
   models fail in legible, reproducible ways. A frontier model papers over a bad
   prompt, a sloppy tool schema, or a missing eval; a 1B model does not. Speed
   and small footprint outrank reasoning quality when choosing models.
2. **The curriculum is harness-agnostic.** No exercise may require Claude Code,
   GitHub Copilot, or OpenAI Codex. Those tools are *mapped to* instead, so the
   material is useful to people who pay for them without being dependent on
   them. (The `.claude/` directory is authoring tooling for this repo, not part
   of the curriculum.)

Audience: engineers who may already use a commercial coding harness and want to
understand what it is actually doing.

## Before you write anything

Read [`docs/STYLE.md`](docs/STYLE.md). It has the voice rules and the module
template. The most important rules are repeated here because they are the ones
most often broken:

### Never invent a number

Not tokens/sec, not memory, not latency, not eval scores. If a number is not
from a cited source or from a run on a named machine, it does not go in the
repo. Ship the script that measures it and leave the cell blank.

This is the single easiest way to make this repo worthless. A reader who catches
one fabricated benchmark correctly stops trusting every other number here.

### Never hardcode a model name, tag, or size in prose

`models/roster.yaml` is the single source of truth. Prose uses generated blocks:

```markdown
<!-- BEGIN GENERATED: roster -->
<!-- END GENERATED: roster -->
```

Regenerate after any roster change:

```bash
uv run scripts/render-roster.py
uv run scripts/render-roster.py --check   # exit 1 if stale
```

Content between markers is overwritten. Never hand-edit it.

### Cite claims about versions and capabilities

Link and date them. Model and tool facts rot within months. An uncited version
claim is a future bug.

### Every command shown must have been run

Or be explicitly marked untested. "I have not tested this on a Mac" is a fine
sentence; a command that silently does not work is not.

## Layout

```
models/roster.yaml     SINGLE SOURCE OF TRUTH for models
modules/NN-name/       curriculum; README.md + exercises/ + FIELD-NOTES.md
scripts/               check-env, pull-roster, bench, render-roster
TODO.md                the working backlog — actionable items live HERE
docs/STYLE.md          voice rules + module template  ← read before writing
docs/ROADMAP.md        curriculum design; module specs and ordering rationale
docs/decisions/        ADRs for load-bearing choices
.claude/               authoring tooling (commands, subagents)
```

## Conventions

- **Modules** are `modules/NN-slug/`, zero-padded, README.md as the entry point.
- **Field notes** live in each module's `FIELD-NOTES.md` — real measured output,
  always with date and hardware. The README stays stable; field notes carry the
  machine-specific observations.
- **No empty stub directories.** A module appears on disk when it has content.
  Until then it is a spec in `docs/ROADMAP.md`.
- **Every module ends with an "If you use a harness" section** mapping what was
  just built onto Claude Code / Codex / Copilot / Cursor. Describe mechanisms,
  link documentation, never require the reader to own the tool.
- **Python** uses `uv`. Scripts carry PEP 723 inline metadata so
  `uv run scripts/foo.py` resolves dependencies with no separate install step.
  Note that Ubuntu 24.04 marks system Python as externally managed (PEP 668), so
  a bare `pip install` fails — this is worth saying out loud in the docs rather
  than letting readers hit it.
- **Shell** is bash, `set -uo pipefail`, shellcheck-clean.
- **Commits** are conventional style, scoped: `docs(module-01): ...`,
  `feat(scripts): ...`, `fix(roster): ...`.

## Common tasks

| Task | How |
|---|---|
| Find what needs doing | Read `TODO.md`. Record new open items there, not in a new file |
| Refresh models against upstream | `/update-models`, or edit `models/roster.yaml` and re-render |
| Start a new module | `/new-module`, or copy the template from `docs/STYLE.md` |
| Check docs are consistent | `/verify-docs` |
| Regenerate tables | `uv run scripts/render-roster.py` |
| Verify a reader's environment | `bash scripts/check-env.sh` |
| Measure model performance | `uv run scripts/bench.py` |

## Known state worth carrying

- **Roster tags are unverified.** Every entry in `models/roster.yaml` carries
  `tag_verified: false` because the authoring environment could not reach
  `ollama.com`. Model families, sizes, and licenses *were* verified against
  vendor sources; the exact Ollama tag strings were not. See
  [ADR 0005](docs/decisions/0005-unverified-tags.md). Clearing these is the top
  roadmap item.
- **The MCP Python SDK went to 2.0.0 on 2026-07-28.** Module 07 must target 2.x.
  Most tutorials surfaced by search will be 1.x.
- **Sizes in the roster are estimates**, labeled as such in its `provenance:`
  block. Real numbers come from `scripts/bench.py`.

## Things that are not this repo's job

Fine-tuning, RAG pipelines, GPU/CUDA setup, multi-node serving, and model
training. Not because they do not matter, but because the curriculum has a
premise — small models, ordinary hardware, agentic patterns — and scope creep
would dilute it. Redirect rather than expand.
