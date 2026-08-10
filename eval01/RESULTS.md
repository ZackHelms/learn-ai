# Results

Scoreboard for the Ashfall Outpost eval. Protocol in [README.md](README.md), point
definitions in [RUBRIC.md](RUBRIC.md).

Column notes:

- **Datetime** - approximate start of generation, `date +"%Y-%m-%d_%H:%M:%S_%Z"`.
- **Reasoning effort** - the harness's reasoning/thinking setting, under whatever name the harness gives it, or `-` if it has none.
- **Run** - run number for this config (`r2`+ when repeating a surprising result). Record every run, never just the best one.
- **Cost** - whatever the harness exposes: tokens, credits, percent of quota.
- **Score** - `deterministic + model-graded = total`, out of 100 when the runtime pass ran (out of less otherwise; note it).
- **Grader** - judge model and reasoning effort for the model-graded half. Only compare totals that share a grader.

## Pipeline validation runs

Not eval rows - these validated that the pipeline works end to end. Candidates were generated
by Claude Code subagents (Agent tool, reasoning effort inherited from the session), not by
the harnesses this eval targets, so they are not comparable to real runs and live here only
as worked examples.

|                Datetime |              Harness |       LLM | Reasoning effort | Run | Time(s) |     Cost |         Score |                         Grader | Notes |
|                -------- |              ------- |       --- |           ------ | --- | ------- |     ---- |         ----- |                         ------ | ----- |
| 2026-08-09_14:43:42_EDT | Claude Code subagent | Haiku 4.5 |        inherited |  r1 |     168 |  39k tok | 26 + 23 =  49 | Sonnet 5 subagent, prompt v1.2 | JS syntax error on load: A3=0, all C/D runtime 0. Agreement check: Haiku grader scored F+G 29 vs Sonnet 23 (12/18 items exact, all within 1; Haiku uniformly more lenient) |
| 2026-08-09_14:44:11_EDT | Claude Code subagent |  Sonnet 5 |        inherited |  r1 |    1443 | 100k tok | 54 + 46 = 100 | Sonnet 5 subagent, prompt v1.2 | Saturates the eval: clean load, 21/21 assertions, identical benchmark hash across reload. Haiku grader agreed 46/46 (18/18 items exact) |




## Eval runs

**Grader**: sonnet-5 (high), ai grader prompt v1.3 via grade.sh, each ai eval api cost equivalent is $0.95-$1.10 (110 input, 20.7k output, 622.0k cache read, 102.6k cache write).
**Scores**: from command like `./eval01/listscore.py r0{1..5}{a..e}` that (for each rNN) is AVG of the ai grader runs.
Each row is 1-shot to handle the prompt, 1 deterministic eval py, and 5 ai-grader runs average score.

|                Datetime |     Harness | LLM (Reasoning effort) | Run |  Time |    Cost |  det+ai=Score | Notes |
| ----------------------- | ----------- | ---------------------- | --- | ----- | ------- | ------------- | ----- |
| 2026-08-09_22:37:30_EDT | Claude Code | claude-opus-5 (xhigh)  |   0 | 50m9s | $21.2300 | xx + xxxx = xxxx | 731 input, 223.3k output, 25.0m cache read, 312.6k cache write ($21.23) |
| 2026-08-09_17:11:22_EDT | Claude Code | claude-haiku-4-5 (low) |   1 | 1m57s |  $0.1742 | 32 + 18.8 =  50.8 | ai grader prompt v1.2, 3.4k input, 19.7k output, 0 cache read, 36.1k cache write ($0.1742) |
| 2026-08-09_20:05:28_EDT | Claude Code | claude-haiku-4-5 (med) |   2 | 3m01s |  $0.2933 | 45 + 32.8 =  77.8 | ai grader prompt v1.2, 100 input, 21.9k output, 101.8k cache read, 86.8k cache write ($0.2933) |
| 2026-08-09_20:05:35_EDT | Claude Code | claude-haiku-4-5 ( hi) |   3 | 2m44s |  $0.2755 | 31 + 34.0 =  65.0 | ai grader prompt v1.2, 1.3k input, 20.6k output, 98.1k cache read, 80.7k cache write ($0.2755) |
| 2026-08-09_20:05:40_EDT | Claude Code | claude-haiku-4-5 (xhi) |   4 | 2m27s |  $0.2671 | 52 + 33.6 =  85.6 | ai grader prompt v1.2, 1.3k input, 20.1k output, 98.2k cache read, 77.7k cache write ($0.2671) |
| 2026-08-09_20:05:46_EDT | Claude Code | claude-haiku-4-5 (max) |   5 | 2m28s |  $0.2536 | 39 + 27.0 =  66.0 | ai grader prompt v1.2, 1.3k input, 17.3k output, 98.7k cache read, 78.0k cache write ($0.2536) |




