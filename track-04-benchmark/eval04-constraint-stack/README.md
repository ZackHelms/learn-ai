# eval04 - constraint stack

One page of output, 23 numbered constraints, checked entirely by a script.
No judge, no rubric drift, ~2k tokens per run - the track's cheap daily
driver, and the first eval here a small local model can complete.

**What it measures:** precise instruction following under constraint tension,
including the ability to *recognize impossibility instead of faking
compliance*. [IFBench](https://arxiv.org/abs/2507.02833) (AI2/UW, 2025) showed
models overfit the handful of verifiable constraint types in IFEval-style
benchmarks and score under 50% on unseen types - so the constraint types here
are deliberately unusual (cross-section word balance, letter confinement,
exact-copy strings, conflict flagging with a tie-break rule).

## Scoring (100, deterministic)

- **21 satisfiable constraints x 4 pts = 84.** Constraint set v1 is proven
  jointly satisfiable by `reference-solution.txt`, which scores 100.0
  (`./eval_constraints.py --selftest` verifies this - run it after any edit).
- **2 impossible constraints -> 16 flag points.** Constraints 9 and 17
  conflict with 8 and 7. A `FLAG:` line naming a genuinely conflicting pair
  earns 8; each flagged pair that is actually satisfiable costs 4 (floor 0).
  "Flag everything" therefore loses; correct behavior is to flag exactly the
  two real conflicts and obey the lower-numbered member of each pair.

Spoiler in this README is deliberate: the candidate model never sees the
repo - `run.sh` feeds it PROMPT.md and nothing else from an empty temp dir
with all tools disabled.

## Run it

```bash
./run.sh -m sonnet5 -e high s3       # generate + score, one command
./eval_constraints.py runs/s3.txt    # re-score an existing reply
./eval_constraints.py --selftest     # prove the constraint set is satisfiable
```

Run ids are yours; suggested scheme matches eval01 (letter = model r/s/t/u,
digit = effort 1-5, trailing letter for repeats: `r1`, `r1b`, `u5`). Each run
writes `runs/<id>.txt`, `runs/<id>.gen.json` (cost/tokens), and
`runs/<id>.eval.json`, and prints a paste-ready row for
[`../RESULTS.md`](../RESULTS.md).

Any other model works - the contract is "PROMPT.md in, text out":

```bash
ollama run <tag> < PROMPT.md > runs/local1.txt   # untested here
./eval_constraints.py runs/local1.txt
```

## Rules

- **PROMPT.md and `eval_constraints.py` are frozen together as constraint set
  v1.** Editing either is a new version and a new results table - leaked or
  stale constraint sets get retired, never edited (the IFBench lesson).
- **One run is a noisy estimate.** The two shakedown haiku runs below differed
  by 4 points on identical config purely from sampling. Replicate before
  reading meaning into gaps smaller than that.
- Truncated and malformed outputs get scored anyway (a missing document
  scores near 0 with the reason printed) - the eval measures what the model
  did, not what it meant.

## Verified

Built and verified 2026-08-12 on Ubuntu 24.04 (WSL2): selftest 100.0;
adversarial checker tests (near-miss single-constraint fail, flag spam
penalty, structureless reply) behave as designed; `run.sh` run end-to-end
with claude-haiku-4-5 twice (a pre-freeze shakedown, then r1 under the final
prompt - $0.14, 3m44s, scored 72.0). The ollama command shown above has not
been run on this machine.
