# Track 04 results

One row per run. eval01's results stay in
[`eval01-build-ashfall/RESULTS.md`](eval01-build-ashfall/RESULTS.md) - that
file predates the track and its history should not move; new eval01 runs keep
going there. This file collects runs of eval02-05.

A section per eval is added when the eval ships, with a column schema matching
what its scorer actually emits - no column exists here that a script does not
fill. The comparability rules are in the [track README](README.md): frozen
tasks, fixed scorers, every run recorded, small gaps are ties.

## eval02 - play Ashfall (contract v1, reference v1)

Score = the game's own end-screen formula; seed 1337 is the frozen
comparison seed. Baselines are deterministic - anyone can reproduce them
with `./run.sh -b <name> <id>`. See
[eval02-play-ashfall/](eval02-play-ashfall/).

| Started | Agent | Run | Seed | Turns | Time | Cost | Score | Win | pop/research/stock | hash |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-08-12_13:13:51_EDT | idle | idle1 | 1337 | 10 | 0s | $0 | 64 | loss | 0/0/223 | 4e7a29a2 |
| 2026-08-12_13:14:01_EDT | naive | naivea | 1337 | 13 | 0s | $0 | 92 | loss | 0/1/132 | dc133b09 |
| 2026-08-12_13:14:02_EDT | naive | naiveb | 1337 | 13 | 2s | $0 | 92 | loss | 0/1/132 | dc133b09 |
| 2026-08-12_13:14:05_EDT | greedy | greedya | 1337 | 20 | 0s | $0 | 52 | loss | 0/0/63 | 2a3ddb5b |
| 2026-08-12_13:14:06_EDT | greedy | greedyb | 1337 | 20 | 0s | $0 | 52 | loss | 0/0/63 | 2a3ddb5b |
| 2026-08-12_13:15:18_EDT | claude-haiku-4-5 (low) | r1 | 1337 | 16 | 35m47s | $1.3467 | 76 | loss | 0/1/22 | bd0fd65f |

NOTE (12Aug2026, r1): the first model run. haiku-low played genuinely - grew
the colony to pop 10 by turn 7 (refugees + settlers), survived the first
ashstorm behind a pre-built windbreak, then hit the mid-game food wall and
collapsed to zero by turn 16. Outlasted naive (13 turns) but not greedy
(20); scored between them (76). Its notes stayed coherent to the end; the
transcript (runs/r1.turns.jsonl) is worth reading. Cost flag: at effort
LOW, haiku averaged ~12.6k output tokens of thinking per turn - $1.35 and
36 minutes for one run. Budget eval02 sweeps accordingly; higher efforts
will cost multiples of that.

NOTE (12Aug2026): repeated baselines land on identical hashes - the
environment side is deterministic as designed. Even the game's own greedy
policy dies on seed 1337 (six colonists cannot man the full chain); nothing
has reached turn 60 yet, so the win bonus is unclaimed and the eval is
unsaturated in both directions. Among these corpses the score formula pays
hoarded stock and research more than extra turns - naive outscores greedy
while dying earlier.

## eval03 - repair, not build (defect set v1)

Score = apply 8 + defects 60 + guards 12 + minimality 20; empty reply
anchors at 12, the committed reference fix at 100. See
[eval03-repair/](eval03-repair/).

| Started | Harness | Model (effort) | Run | Time | Cost | apply + defects + guards + minimality = total | Touched | Tokens |
|---|---|---|---|---|---|---|---|---|
| 2026-08-12_13:25:24_EDT | Claude Code (bare) | claude-haiku-4-5 (low) | r1 | 1m25s | $0.1447 | 8.0 + 50.0 + 12.0 + 16.7 = 86.7 | 13 touched | 9 in, 8.4k out |

NOTE (12Aug2026): r1 is the build-day shakedown under the final (frozen)
prompt. An earlier run under a pre-freeze prompt draft whose bug reports
were too diagnostic (one quoted the intended formula, another the exact
error text) scored a perfect 100.0 - haiku-low found all five defects in
48s. The frozen v1 reports are symptom-only, which cost haiku one defect
(the adjacency off-by-one). Expect frontier models near the ceiling anyway;
v1's discrimination range is small/local models, and a subtler defect set
is the v2 direction (tracked in TODO).

## eval04 - constraint stack (set v1)

Score = satisfiable constraints (84) + conflict flags (16), fully
deterministic; see [eval04-constraint-stack/](eval04-constraint-stack/).
`run.sh` prints these rows ready to paste.

| Started | Harness | Model (effort) | Run | Time | Cost | sat + flags = total | Tokens |
|---|---|---|---|---|---|---|---|
| 2026-08-12_13:02:30_EDT | Claude Code (bare) | claude-haiku-4-5 (low) | r1 | 3m44s | $0.1425 | 56.0 + 16.0 = 72.0 | 9 input, 25.2k output, 0 cache read, 7.4k cache write |

NOTE (12Aug2026): r1 is the build-day shakedown run, kept as the first data
point. An earlier haiku-low run under a pre-freeze prompt draft (without the
lower-numbered tie-break sentence) scored 76.0 with a different miss mix -
recorded here as a variance hint, not a comparable row: identical-config
haiku runs moved 4 points on sampling alone. Both runs flagged both conflict
pairs correctly and failed only satisfiable constraints.

## eval05 - grounded answer, poisoned context (bundle v1)

Score = 20 questions x 5, exact match; a result is only comparable within
its bundle variant (small ~6k tokens / full ~30k). See
[eval05-poisoned-context/](eval05-poisoned-context/).

| Started | Harness | Model (effort) | Run | Bundle | Time | Cost | Score | By type | Tokens |
|---|---|---|---|---|---|---|---|---|---|
| 2026-08-12_13:28:05_EDT | Claude Code (bare) | claude-haiku-4-5 (low) | r1s | small | 0m22s | $0.0493 | 95.0 | value 12/12, conflict 3/4, absent 4/4 | 9 in, 2.2k out |

NOTE (12Aug2026): the one miss is the interesting one - haiku believed a
poisoned ops-log claim instead of flagging the conflict. Values and
absences were perfect. The small variant is near-saturated for capable
models; run the full variant for discrimination.
