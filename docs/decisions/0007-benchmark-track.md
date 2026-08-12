# 0007 — The benchmark is a track

**Status:** accepted · **Date:** 2026-08-12

## Context

`eval01/` (the Ashfall Outpost one-prompt eval) was built at the repo root as a
deliberate working area, exempt from the track rules while it stabilized. It
has: four model families times five effort levels scored across four sets, a
deterministic scorer with a documented fix-and-re-score discipline, a pinned
LLM judge, and a results file with provenance for every number. That is no
longer a working area; it is an instrument.

TODO.md carried the open decision: formalize as a shared `evals/` asset, or
fold into a module (Track 01's evals module, or Track 02's comparison
exercise). Meanwhile the plan grew from one eval to a benchmark — a **fixed
collection of evals plus a protocol** — covering axes eval01 does not touch:
long-horizon coherence, repair/localization, instruction following under
constraint tension, grounding against poisoned context.

## Decision

Create **`track-04-benchmark/`** and move `eval01/` into it as its first
module, history preserved (`git mv`, 626 renames). The four planned evals are
specced in `docs/ROADMAP.md` and get directories only when they have content,
per the no-stubs rule.

- **Modules are named `evalNN-slug/`** (`eval01-build-ashfall/`,
  `eval02-play-ashfall/`, ...) instead of the curriculum tracks' `MM-slug/`.
  The eval ids are load-bearing — run ids (`u35`), results tables, logs, and
  notes all reference them — so the directory name keeps the id greppable.
- **Benchmark modules follow their own internal layout** (README, prompt,
  rubric, scorer, `runs/`, RESULTS.md), not the curriculum module template in
  `docs/STYLE.md`. The voice rules and *never invent a number* apply in full.
  Track 01's "If you use a harness" rule does not apply here.
- **`track-04-benchmark/reference/` holds frozen shared fixtures**, versioned
  and checksum-pinned, never edited in place. First entry:
  `ashfall-reference-v1.html`, a byte-identical copy of eval01 run u35
  (100.0/100), which becomes eval02's environment and eval03's seed material.
- **New evals are deterministic-first.** eval01's judged half is comparable
  only while judge model + effort + grader prompt stay fixed; eval02–05 are
  designed with no judge at all, so the benchmark's dependence on that
  discipline shrinks rather than compounds.

## Why a track, and not the alternatives

- **Not a shared `evals/` root directory:** it would be a second top-level
  concept competing with tracks, and ADR 0006 already establishes that
  top-level premises are tracks. The benchmark has exactly the track contract:
  a premise (measure, don't vibe), an audience (anyone choosing a
  model/effort/harness), and a spend assumption (deterministic halves free,
  hosted candidates and judges metered).
- **Not folded into Track 01 module 03:** that module *teaches* evals on the
  local roster, harness-agnostic and zero-spend. eval01 is a production
  instrument aimed mostly at hosted frontier models with real dollar costs in
  its results. Folding it in would break Track 01's spend premise and bury 600+
  result files inside a teaching module. The two link to each other instead.
- **Not left at the root:** the exemption was explicitly temporary, and every
  future eval would have widened it.

## Consequences

- Deep links to `eval01/...` paths break; repo-internal references were
  updated (root README, ROADMAP, AGENTS.md, TODO.md, the eval's own README).
  Historical mentions in dated notes, plans, and personal notes stay as
  written.
- Run ids, scores, RESULTS.md, and the scorer are untouched by the move —
  comparability is unaffected.
- The muscle-memory path changes: `cd track-04-benchmark/eval01-build-ashfall`
  instead of `cd eval01`. All pipeline scripts were already
  `SCRIPT_DIR`-anchored, so nothing inside them changed.
- TODO.md's "where does eval01 formally live" decision closes.

## What would change this

An eval that outgrows the artifact-in-repo model (e.g. result volume that
belongs in object storage, or a task whose fixture cannot be public without
contamination destroying it) — that would be a case for splitting run storage
from eval definition, not for leaving the track.
