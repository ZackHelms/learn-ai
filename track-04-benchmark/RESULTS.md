# Track 04 results

One row per run. eval01's results stay in
[`eval01-build-ashfall/RESULTS.md`](eval01-build-ashfall/RESULTS.md) - that
file predates the track and its history should not move; new eval01 runs keep
going there. This file collects runs of eval02-05.

A section per eval is added when the eval ships, with a column schema matching
what its scorer actually emits - no column exists here that a script does not
fill. The comparability rules are in the [track README](README.md): frozen
tasks, fixed scorers, every run recorded, small gaps are ties.

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
