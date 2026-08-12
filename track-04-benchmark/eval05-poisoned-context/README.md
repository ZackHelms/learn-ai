# eval05 - grounded answer, poisoned context

Three documents about a fictional telemetry daemon (spec, changelog,
operator log), 20 questions, exact-match key. Some questions are answerable,
some are contradicted between documents (the ops log asserts spec values
that the spec does not contain), and some are genuinely absent. Right
behavior is calibrated: give the value, or say `CONFLICT`, or say `ABSENT`.
No judge; 20 x 5 pts.

**What it measures:** grounding and hallucination resistance - believing the
context over plausibility, noticing when sources disagree, and abstaining
when the answer is not there. eval01-04 never touch this axis.

## Design: the key is derived, never hand-written

[`make_bundle.py`](make_bundle.py) generates the documents AND the answer
key from one ground-truth script (seed 1337), then asserts the gates before
writing: every value answer appears in a document, every conflict has two
irreconcilable claims, every absent key appears nowhere. Run it with
`--check` to prove the committed files match the generator byte-for-byte.
Hand-writing a key against 30k tokens of prose is where key errors live;
deriving it makes that class impossible.

Two committed variants share facts, questions, and key - only the haystack
differs:

| variant | size | audience |
|---|---|---|
| `bundle-small/` | ~24 KB, ~6k tokens | small local models |
| `bundle-full/` | ~118 KB, ~30k tokens | the real test |

A result is only comparable within its variant. The supersession rule is
part of the test: the changelog legitimately overrides the spec (not a
conflict); the ops log contradicting the spec's own claim is one.

## Run it

```bash
./run.sh -m haiku45 -e low r1s              # small bundle
./run.sh -m sonnet5 -e high s3f -z full     # full bundle
python3 eval_grounded.py runs/r1s.txt       # re-score
python3 eval_grounded.py --selftest         # key replay must score 100
```

## Anchors

Build-day smoke (2026-08-12): claude-haiku-4-5 low on the small bundle
scored 95/100 in 22s ($0.05) - perfect on values and absences, and believed
exactly one of the four poisoned claims. The small variant is close to
saturated for frontier models; the full variant is the discriminating one.
Bundle v1 (docs + questions + key + generator seed) is frozen; regenerating
with a new seed or sizes is v2 and a new results table.

## Verified

Built 2026-08-12 on Ubuntu 24.04 (WSL2): generator gates pass, `--check`
clean, scorer selftest 100.0, one haiku smoke run recorded in RESULTS. The
ollama pipe form in run.sh has not been run on this machine.
