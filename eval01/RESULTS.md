# Results

Scoreboard for the Ashfall Outpost eval. Protocol in [README.md](README.md), point
definitions in [RUBRIC.md](RUBRIC.md).

Column notes:

- **Datetime** - approximate start of generation, `date +"%Y-%m-%d_%H:%M:%S_%Z"`.
- **Reasoning effort** - the harness's reasoning/thinking setting, under whatever name the
  harness gives it, or `-` if it has none.
- **Run** - run number for this config (`r2`+ when repeating a surprising result).
  Record every run, never just the best one.
- **Cost** - whatever the harness exposes: tokens, credits, percent of quota.
- **Score** - `deterministic + model-graded = total`, out of 100 when the runtime pass ran
  (out of less otherwise; note it).
- **Grader** - judge model and reasoning effort for the model-graded half. Only compare
  totals that share a grader.

## Eval runs

|                Datetime |     Harness | LLM (Reasoning effort) | Run |  Time |    Cost | Score | Grader | Notes |
| ----------------------- | ----------- | ---------------------- | --- | ----- | ------- | ----- | ------ | ----- |
| 2026-08-09_17:11:22_EDT | Claude Code | claude-haiku-4-5 (low) |   1 | 1m57s | $0.1742 |       |        | 3.4k input, 19.7k output, 0 cache read, 36.1k cache write ($0.1742)



## Pipeline validation runs

Not eval rows - these validated that the pipeline works end to end. Candidates were generated
by Claude Code subagents (Agent tool, reasoning effort inherited from the session), not by
the harnesses this eval targets, so they are not comparable to real runs and live here only
as worked examples.

| Datetime | Harness | LLM | Reasoning effort | Run | Time(s) | Cost | Score | Grader | Notes |
| -------- | ------- | --- | ------ | --- | ------- | ---- | ----- | ------ | ----- |
| 2026-08-09_14:43:42_EDT | Claude Code subagent | Haiku 4.5 | inherited | r1 | 168 | 39k tok | 26 + 23 = 49 | Sonnet 5 subagent, prompt v1.2 | JS syntax error on load: A3=0, all C/D runtime 0. Agreement check: Haiku grader scored F+G 29 vs Sonnet 23 (12/18 items exact, all within 1; Haiku uniformly more lenient) |
| 2026-08-09_14:44:11_EDT | Claude Code subagent | Sonnet 5 | inherited | r1 | 1443 | 100k tok | 54 + 46 = 100 | Sonnet 5 subagent, prompt v1.2 | Saturates the eval: clean load, 21/21 assertions, identical benchmark hash across reload. Haiku grader agreed 46/46 (18/18 items exact) |
