# AGENTS.md

Instructions for any AI agent working in this repository — Claude Code, Codex,
Copilot, Cursor, or anything else.

**This file is the source of truth.** `CLAUDE.md` imports it and adds only
Claude-Code-specific notes. Put changes here, not there. See
[ADR 0004](docs/decisions/0004-agents-md-source-of-truth.md).

## What this repo is

A hands-on AI curriculum organized into **tracks**, each with its own premise
and audience. Written as a lab notebook by someone learning the material while
writing it, not as a textbook by an expert.

## Tracks

Each track is a top-level `track-NN-slug/` directory with its own premise,
audience, and spend assumption, stated in its README. See
[ADR 0006](docs/decisions/0006-tracks-top-level.md).

| Track | Premise | Spend assumption |
|---|---|---|
| `track-01-local-models/` | Local weak models, harness-agnostic | Zero — no paid tooling, no API keys |
| `track-02-free-tier/` | What the free tiers of Gemini, Microsoft Copilot, ChatGPT/Codex, and Claude can do | Zero — free accounts only |
| `track-03-claude-pro/` | What Claude Pro at $20/month unlocks | A Claude Pro subscription, nothing beyond it |
| `track-04-benchmark/` | A benchmark — a fixed collection of evals plus a protocol — measuring models instead of vibing them | Deterministic scorers free; hosted candidates and eval01's judge cost metered API |

Deferred (roadmap mention only — never scaffold): base paid tiers of OpenAI,
Gemini, GitHub Copilot.

Rules that keep this structure from regressing:

- Modules live only inside a track: `track-NN-slug/MM-slug/`. Never create a
  bare `modules/` directory. (Track 04's benchmark modules are named
  `evalNN-slug/` because the eval ids are load-bearing in run ids and results —
  [ADR 0007](docs/decisions/0007-benchmark-track.md).)
- Module numbers are zero-padded and **restart per track**, so cross-track
  references must name the track ("Track 01, module 04").
- A track's premise governs its modules. Content that fits no existing premise
  is a new track: ROADMAP entry and ADR first, directory only when the first
  module has content.
- The "If you use a harness" module section is a **Track 01** rule, not a
  repo-wide one — see `docs/STYLE.md`.

Two premises drive nearly every decision **inside Track 01**:

1. **Deliberately weak models are better teaching tools.** Small CPU-bound
   models fail in legible, reproducible ways. A frontier model papers over a bad
   prompt, a sloppy tool schema, or a missing eval; a 1B model does not. Speed
   and small footprint outrank reasoning quality when choosing models.
2. **The track is harness-agnostic.** No exercise may require Claude Code,
   GitHub Copilot, or OpenAI Codex. Those tools are *mapped to* instead, so the
   material is useful to people who pay for them without being dependent on
   them. (The `.claude/` directory is authoring tooling for this repo, not part
   of the curriculum.)

Audience varies by track. Track 01: engineers who may already use a commercial
coding harness and want to understand what it is actually doing. Track 02: no
dev machine needed — a phone or tablet is enough. Track 03: someone already
paying for Claude Pro.

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
models/roster.yaml       SINGLE SOURCE OF TRUTH for models (Track 01's roster)
track-NN-slug/           one track per directory; README.md + MM-slug/ modules
  track-01-local-models/   local weak models, harness-agnostic (00–01 written)
  track-02-free-tier/      the big four platforms at zero spend
  track-03-claude-pro/     what Claude Pro unlocks
  track-04-benchmark/      the measuring instrument: evalNN-slug/ modules + frozen reference/ fixtures
scripts/                 check-env, pull-roster, bench, render-roster (Track 01)
TODO.md                  repo-wide backlog + pointer index; active tracks carry their own TODO.md
docs/STYLE.md            voice rules + module template  ← read before writing
docs/ROADMAP.md          curriculum design; track and module specs, ordering
docs/decisions/          ADRs for load-bearing choices
.claude/                 authoring tooling (commands, subagents)
```

## Conventions

- **Modules** are `track-NN-slug/MM-slug/`, zero-padded, numbering restarts per
  track, README.md as the entry point.
- **Field notes** live in each module's `FIELD-NOTES.md` — real measured output,
  always with date and hardware. The README stays stable; field notes carry the
  machine-specific observations.
- **No empty stub directories.** A module appears on disk when it has content.
  Until then it is a spec in `docs/ROADMAP.md`.
- **Every Track 01 module ends with an "If you use a harness" section** mapping
  what was just built onto Claude Code / Codex / Copilot / Cursor. Describe
  mechanisms, link documentation, never require the reader to own the tool.
  Tracks 02 and 03 cover the commercial platforms directly and skip it.
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
| Find what needs doing | Read `TODO.md`, then the relevant track's own `TODO.md` (linked from root). Record new items in the nearest backlog, never a new file |
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
training. Not because they do not matter, but because each track has a premise
and scope creep would dilute it. Content that fits no existing track's premise
is a ROADMAP proposal for a new track, not an expansion of an existing module.
Redirect rather than expand.
