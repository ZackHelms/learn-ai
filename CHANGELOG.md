# Changelog

What has actually landed in this repo, newest first. Dates are commit dates.

This file is the **repo-wide** record: tracks and modules shipping, structural
decisions, tooling. Detail that only matters inside one track stays in that
track's own changelog — Track 04 keeps
[`track-04-benchmark/CHANGELOG.md`](track-04-benchmark/CHANGELOG.md), and its
scores live in [`RESULTS.md`](track-04-benchmark/RESULTS.md).

**How this file gets written.** Backlogs hold only open work. Finished items are
checked off (or marked `DONE`) in the backlog they lived in — root
[`TODO.md`](TODO.md) for repo-wide items, `track-NN-*/TODO.md` for track work —
and then folded into a dated entry here when a significant feature or a coherent
set of items is complete, at the next commit. One entry per coherent chunk, not
one per edit.

---

## 2026-08-12

- **Track 04 (benchmark) created and filled out.** New top-level track
  ([ADR 0007](docs/decisions/0007-benchmark-track.md)): a fixed collection of
  evals plus a protocol, so models get measured instead of vibed. `eval01/` moved
  from the repo root to `track-04-benchmark/eval01-build-ashfall/` with history
  preserved, and four more evals shipped and made runnable —
  [eval02 (play Ashfall)](track-04-benchmark/eval02-play-ashfall/),
  [eval03 (repair)](track-04-benchmark/eval03-repair/),
  [eval04 (constraint stack)](track-04-benchmark/eval04-constraint-stack/),
  [eval05 (poisoned context)](track-04-benchmark/eval05-poisoned-context/).
  All four are judge-free and deterministic where they can be. A track-level
  `scorecard.py` reads every `runs/*.eval.json` and prints headline numbers.
  Per-eval design notes, gates, and the reference-artifact freeze are in the
  [track changelog](track-04-benchmark/CHANGELOG.md).
- **Per-track TODO split.** The root `TODO.md` became repo-wide items plus a
  pointer index; Track 01 and Track 04 carry their own backlogs.

## 2026-08-09 — 2026-08-12

- **eval01 (build Ashfall) built, hardened, and swept.** An end-to-end
  build-from-a-brief eval with a scorer, a grading pipeline that keeps the grader
  from peeking at results, and recorded runs across four model families at five
  effort levels. Two rounds of scorer bug fixes and full re-scores followed.
  Scores in [`track-04-benchmark/RESULTS.md`](track-04-benchmark/RESULTS.md).

## 2026-08-08

- **Curriculum reorganized into tracks.** Top-level `track-NN-slug/` directories,
  each with its own premise, audience, and spend assumption
  ([ADR 0006](docs/decisions/0006-tracks-top-level.md)). Tracks 01–03 seeded;
  module numbering restarts per track.

## 2026-07-29

- **Curriculum foundation.** Track 01 modules 00 (overview) and 01 (local model
  lab), with exercises.
- **`models/roster.yaml` as single source of truth** for model names, tags, and
  sizes, rendered into prose through generated blocks.
- **`scripts/`**: `check-env.sh`, `pull-roster.sh`, `bench.py`,
  `render-roster.py`.
- **Agent instructions**: `AGENTS.md` as the source of truth, `CLAUDE.md`
  importing it, plus `.claude/` commands and subagents.
- **`docs/`**: `STYLE.md`, `ROADMAP.md`, and the first ADRs.
