# Track 04 changelog

Working notes, newest first. What changed and why; [RESULTS.md](RESULTS.md)
carries the scores, per-eval READMEs carry the how-to.

## 2026-08-12

- **eval05 (poisoned context) shipped.** Generator-derived bundle + key
  (seed 1337): 3 documents, 20 questions (12 value / 4 conflict / 4
  absent), gates asserted at generation, `--check` proves the committed
  files match the generator. Two variants share the key: small ~6k tokens,
  full ~30k. Smoke: haiku-low 95/100 on small - believed exactly one
  poisoned claim; small is near-saturated, full is the real test.
- **eval03 (repair) shipped, hardened once pre-freeze.** Five one-edit
  defects seeded into the reference (`make_defective.py`, reproducible +
  sha-pinned); 12-test hidden suite (6 defect + 6 guard); dual-format patch
  applier (SEARCH/REPLACE or unified diff, content-matched). Selftest
  proves both directions: unpatched fails exactly the 6 defect tests,
  reference fix (10 touched lines) scores 100. The first draft's bug
  reports were too diagnostic - haiku-low scored a perfect 100 in 48s - so
  v1 froze with symptom-only reports (haiku drops to 86.7). A subtler v2
  defect set is the open follow-up.
- **eval02 (play Ashfall) shipped.** Playwright driver over the frozen
  reference (sha-pinned, refuses drift); contract v1 = compact state JSON
  in, action JSON out, with a 600-char self-written note as the model's
  ONLY memory between turns. Baselines: idle dies t10 (64), contract-level
  naive t13 (92), the game's own greedy policy t20 (52) - all reproduce to
  identical state hashes, and none survive seed 1337: winnability is
  genuinely open. haiku-low contract run started as the smoke (slow burn,
  ~6 min/turn - it plans hard); its row lands in RESULTS when it ends.
- **Track scorecard added** (`scorecard.py`): reads every
  `runs/*.eval.json` across evals and prints headline numbers; computes
  nothing.
- **eval04 (constraint stack) shipped.** 23 constraints (21 satisfiable + 2
  impossible), 100 pts fully deterministic, ~2k tokens/run. Reference
  solution proves satisfiability (`--selftest`); checker survived adversarial
  tests (near-miss, flag spam, structureless reply). One design change came
  out of the shakedown run: both conflict pairs are symmetric, so the prompt
  gained an explicit "satisfy the lower-numbered member" tie-break before
  freezing v1 - the pre-freeze haiku run had flagged both pairs correctly and
  then obeyed the *higher* member of each. First recorded run: haiku-4-5 low,
  72.0 ($0.14). Identical-config shakedown pair differed by 4 pts on sampling
  alone; noted in RESULTS.
- **Track created** ([ADR 0007](../docs/decisions/0007-benchmark-track.md)).
  `eval01/` moved from the repo root to `eval01-build-ashfall/` via `git mv`,
  history preserved; run ids, scores, and scorer untouched. One hiccup: an IDE
  editor holding the old `eval01/RESULTS.md` open re-saved it mid-move,
  resurrecting the file; removed after confirming byte-identity with the moved
  copy.
- **Reference artifact frozen**: `reference/ashfall-reference-v1.html` =
  byte-identical copy of eval01 run u35 (claude-fable-5 max, set 3, 100.0/100,
  73,579 bytes, sha256 `2f7425cc...`). 19 runs tied at 100.0; u35 chosen as the
  largest set-3 perfect build (newest pipeline, current scorer). Freeze policy
  in `reference/README.md`: defects found later ship as v2, never an in-place
  edit.
- **eval02-05 specced** in [ROADMAP](../docs/ROADMAP.md#track-04--benchmark)
  with dated citations (Vending-Bench 2 / Andon Labs; TRAIL arXiv:2505.08638;
  IFBench arXiv:2507.02833) and named design risks. Design rules for all four:
  judge-free, no output ceiling.
- **TODO restructure**: build backlog moved from the root TODO into
  [TODO.md](TODO.md) here; root TODO became a pointer index plus repo-wide
  items.
