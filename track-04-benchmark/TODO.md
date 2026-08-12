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
- [x] **Build eval02 (play Ashfall)** - DONE 2026-08-12. Gate met: naive and
      greedy baselines each reproduce to identical state hashes on seed 1337.
      Finding: nothing (including the game's own greedy policy) survives to
      turn 60 - winnability is open.
- [x] **Build eval03 (repair)** - DONE 2026-08-12. Gates met via
      `--selftest`: defective file fails exactly the 6 defect tests, the
      10-line reference fix scores 100, guards + minimality punish shotgun
      rewrites. Hardened pre-freeze after haiku-low aced the draft prompt.
- [x] **Build eval05 (poisoned context)** - DONE 2026-08-12. Key derived from
      the generator with gates asserted at generation; `--check` reproduces
      the committed bundles byte-for-byte.
- [x] **Track-level scorecard** - DONE 2026-08-12: `scorecard.py` (a pure
      reader over `runs/*.eval.json`).

## Follow-ups (open)

- [x] **eval02: record the in-flight haiku run** - DONE 2026-08-12: r1
      finished (pop 0 at turn 16, score 76, $1.35); row + note in RESULTS.
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
