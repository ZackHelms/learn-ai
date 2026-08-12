# Track 04 changelog

Working notes, newest first. What changed and why; [RESULTS.md](RESULTS.md)
carries the scores, per-eval READMEs carry the how-to.

## 2026-08-12

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
