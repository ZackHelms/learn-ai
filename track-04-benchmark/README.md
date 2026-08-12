# Track 04 - Benchmark

**Premise:** you cannot compare models, harnesses, or effort levels on vibes.
This track is the repo's measuring instrument: a benchmark, run the same way
every time, against whatever model you care about.

A **benchmark is a collection of evals plus a protocol**. One eval measures one
axis; a benchmark covers several on purpose, so a model that aces one axis and
falls over on another is visible instead of averaged away. The protocol - frozen
prompts, frozen scorers, pinned judges, every run recorded - is what makes a
number from March comparable to a number from August.

**Audience:** anyone who wants "which model/effort/harness should I use" to be
answered by a table of real runs instead of a hunch. It is also where the other
tracks point when they claim something helped: Track 01 module 03 *teaches*
evals on the local roster; this track is the production instrument.

**Spend assumption:** running the deterministic scorers is free, and local
models can be candidates for free. Generating candidates from hosted models,
and eval01's judged half, cost metered API (or ride a subscription). Every cost
figure in a RESULTS.md here is real spend from a real run - this track invents
no numbers, including dollar ones.

## The evals

| # | Eval | Axis it isolates | Judge | Status |
|---|---|---|---|---|
| eval01 | [Build Ashfall](eval01-build-ashfall/) - one prompt, one huge artifact | one-shot breadth under an output ceiling | 46/100 LLM-judged | shipped; 4 model families x 5 effort levels, sets 0-3 scored |
| eval02 | Play Ashfall - agent as player, 60 turns | long-horizon coherence | none | specced in [ROADMAP](../docs/ROADMAP.md#track-04--benchmark) |
| eval03 | Repair, not build - seeded defects, minimal diff | comprehension + fault localization | none | specced |
| eval04 | Constraint stack - 20-25 checked constraints, 2 impossible | precise instruction following, abstention | none | specced |
| eval05 | Grounded answer, poisoned context | grounding, conflict detection, abstention | none | specced |

eval01 measures generation breadth and is output-bound: a model that cannot
emit ~60k+ bytes cannot compete regardless of quality. eval02-05 are designed
to remove that ceiling one axis at a time - eval02 needs only a small action
per turn, eval03 is input-bound, eval04 is one page, eval05 is short answers
against a long context. A 4k-context local model gets a real number on most of
them. They are also deliberately judge-free: eval01's judged half is only
comparable while the judge model, effort, and grader prompt stay fixed, and
that is a dependency worth not repeating four more times.

## Shared fixtures

[`reference/`](reference/) holds frozen artifacts consumed by more than one
eval - currently `ashfall-reference-v1.html`, a 100/100 eval01 build that
becomes eval02's game environment and eval03's defect-seeding base. Frozen
means frozen: new version, new file, never an in-place edit.

## Rules (the protocol half of the benchmark)

These generalize eval01's rules to the track:

- **Frozen tasks.** A prompt, constraint set, or bundle edit is a new eval
  version and a new results table, not a revision.
- **Fixed scorers.** Deterministic scorer fixes are allowed (they correct the
  instrument) but require re-scoring every prior run in the same batch and a
  dated note - see eval01's RESULTS.md for the pattern.
- **Pinned judges.** Where a judge exists, model + effort + grader-prompt
  version are recorded per row; changing any of them invalidates comparisons.
- **Every run recorded.** Never only the best one.
- **Small gaps are ties.** One run per config is a noisy estimate; replicate
  before believing a surprise. eval01's ten identical-config haiku runs spread
  about +/-9 points of pure sampling noise - assume similar until measured.

## Module naming

Modules here are `evalNN-slug/` rather than the `MM-slug/` used by the
curriculum tracks - the eval ids (eval01, eval02, ...) are load-bearing in run
ids, results tables, and notes. Rationale in
[ADR 0007](../docs/decisions/0007-benchmark-track.md).
