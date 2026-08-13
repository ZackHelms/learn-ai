# Track 04 - benchmark backlog

Track-specific action items. Repo-wide items live in the [root TODO](../TODO.md);
specs for the evals live in [ROADMAP](../docs/ROADMAP.md#track-04--benchmark).
Story of what happened lives in [CHANGELOG.md](CHANGELOG.md); scores live in
[RESULTS.md](RESULTS.md).

This file holds **open work only**. Check an item off when it lands, write the
detail into [CHANGELOG.md](CHANGELOG.md), and drop the checked line at the next
commit - the repo-level summary goes in the [root changelog](../CHANGELOG.md).

All five evals are built and runnable (2026-08-12, see the changelog). What is
left:

## Follow-ups (open)

- [ ] **eval02: winnability probe.** Nothing has survived seed 1337 to turn
      60. Worth one strong-model run (or a smarter scripted policy) to learn
      whether the win bonus is reachable at all; the answer changes how
      scores read.
- [ ] **eval03 v2: subtler defect set.** v1 discriminates below the frontier
      (haiku-low hit 86.7; expect strong models near 100). A v2 wants
      defects that look locally correct (boundary swaps in look-alike
      variables, coercion drops) and even vaguer reports.

## Waiting on Zack

Items that need your input. Answer inline, or delete when handled.

- **Which model x effort matrix do you want on evals 02-05?** Everything so
  far is deterministic baselines + one haiku-low smoke per eval (total spend
  today under $1). A full eval01-style sweep (4 models x 5 efforts) costs
  real money on eval02 especially (60 calls/run and slow wall time at high
  effort); eval04/05 are cheap enough to sweep freely. Runs are yours to
  fire one at a time - each run.sh prints the RESULTS row to paste.
- **Keep my `r1` smoke ids as the first official rows, or re-run fresh?**
  They are recorded in RESULTS either way; if you re-run, use a rep suffix
  (`r1b`) rather than `-f` so history stays.
- **eval03 v2 priority.** Is a harder defect set worth building soon, or is
  v1's local-model range enough for now?
