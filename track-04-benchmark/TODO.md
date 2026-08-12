# Track 04 - benchmark backlog

Track-specific action items. Repo-wide items live in the [root TODO](../TODO.md);
specs for the evals live in [ROADMAP](../docs/ROADMAP.md#track-04--benchmark).
Story of what happened lives in [CHANGELOG.md](CHANGELOG.md); scores live in
[RESULTS.md](RESULTS.md).

## Build items, in intended order

- [x] **Build eval04 (constraint stack) first** - DONE 2026-08-12. Both gates
      met: `reference-solution.txt` scores 100.0 (`--selftest`), spurious
      flags cost 4 pts each so "flag everything" loses. Shipped with a haiku
      shakedown run recorded in RESULTS.
- [ ] **Build eval02 (play Ashfall)** - Playwright driver + state/action
      contract v1 against `reference/ashfall-reference-v1.html`. The contract
      is versioned like a prompt; the artifact never changes. Gate: a scripted
      baseline agent produces an identical outcome on two runs of the same seed
      (proves environment-side determinism).
- [ ] **Build eval03 (repair)** - derive the defective file from the reference,
      seed N defects, write the hidden suite + a reference fix that passes 100%.
      Gate: the defective file fails exactly the expected tests; the reference
      fix passes all of them; a shotgun rewrite scores visibly worse than the
      minimal fix.
- [ ] **Build eval05 (poisoned context)** - bundle *generator* (event script ->
      spec/changelog/logs with injected contradictions) so the answer key is
      derived, not hand-written. Gate: key consistency check passes (every
      question's answer provably derives from the event script).
- [ ] **Track-level scorecard** - once two or more evals exist, a small script
      aggregating per-eval results into one table per model config.

## Waiting on Zack

Items that need your input. Answer inline, or delete when handled.

- (none yet)
