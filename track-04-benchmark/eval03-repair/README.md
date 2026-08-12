# eval03 - repair, not build

The inverse of eval01: instead of emitting 3,000 lines cold, the model reads
a ~1,270-line working game, localizes five seeded defects from player bug
reports, and fixes them with a **minimal** patch. Input-comprehension-bound,
fully deterministic, no judge.

**What it measures:** fault localization and repair discipline.
[TRAIL](https://arxiv.org/abs/2505.08638) (Patronus AI, 2025) found the best
model localizes and categorizes errors in annotated agent traces at ~11% -
this axis is nowhere near saturated, and it separates models that eval01
lumps together at its ceiling.

## The artifact

`ashfall-defective-v1.html` = the frozen reference build with five one-edit
defects seeded by [`make_defective.py`](make_defective.py) (run it to
reproduce the file byte-for-byte; the scorer sha-pins it). One defect per
classic class: off-by-one, operator precedence, phase-ordering, broken save
round-trip, boundary condition.

"Hidden" tests means *protocol*-hidden: the suite lives in `eval_repair.py`
in a public repo, and the defect list is documented one file over. The
protocol is that the model receives PROMPT.md + the defective file and
nothing else (`run.sh` enforces it: bare `claude -p`, tools disabled, empty
cwd). Contamination is a real long-term risk and worth a dated note the day
this repo shows up in training data.

## Scoring (100, deterministic)

| component | pts | what |
|---|---|---|
| apply | 8 | every edit block located and applied (exact unique match) |
| defects | 60 | 6 defect-revealing tests x 10 |
| guards | 12 | 6 regression tests x 2 - shotgun rewrites pay here |
| minimality | 20 | x (defects fixed / 6) x line factor (<=16 lines 1.0, <=32 0.6, <=64 0.3, else 0) |

Anchors: an empty or unparseable reply scores 12 (guards pass on the
defective file); the committed [`reference-fix.txt`](reference-fix.txt) (10
touched lines) scores 100.0. `./eval_repair.py --selftest` verifies both
directions: the unpatched file must fail exactly the six defect tests, and
the reference fix must score 100.

Edits are accepted as SEARCH/REPLACE blocks or unified-diff hunks, applied
by exact unique content match (`@@` line numbers ignored) - format details
in PROMPT.md. Defect set v1 = PROMPT.md + the artifact + the suite, frozen
together; any edit to any of them is v2 and a new results table.

## Run it

```bash
./run.sh -m sonnet5 -e high s3     # generate + score
uv run eval_repair.py runs/s3.txt  # re-score an existing reply
uv run eval_repair.py --selftest   # verify the instrument
```

One call per run, ~21k input tokens (the whole file rides along every time).

## Verified

Built 2026-08-12 on Ubuntu 24.04 (WSL2): selftest passes both directions;
scorer applied mixed-format edits in adversarial checks; smoke-run end to
end with claude-haiku-4-5 low (see RESULTS). The ollama pipe form in run.sh
has not been run on this machine.
