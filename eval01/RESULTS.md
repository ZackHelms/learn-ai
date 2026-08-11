# Results

## Description
Scoreboard for the Ashfall Outpost eval. Protocol in [README.md](README.md), point definitions in [RUBRIC.md](RUBRIC.md).

Column notes:

- **Datetime** - approximate start of generation, `date +"%Y-%m-%d_%H:%M:%S_%Z"`.
- **Reasoning effort** - the harness's reasoning/thinking setting, under whatever name the harness gives it, or `-` if it has none.
- **Run** - run number for this config (`r2`+ when repeating a surprising result). Record every run, never just the best one.
- **Cost** - whatever the harness exposes: tokens, credits, percent of quota.
- **Score** - `deterministic + model-graded = total`, out of 100 when the runtime pass ran (out of less otherwise; note it).
- **Grader** - judge model and reasoning effort for the model-graded half. Only compare totals that share a grader.

## (9Aug2026) Pipeline validation runs

Not eval rows - these validated that the pipeline works end to end. Candidates were generated
by Claude Code subagents (Agent tool, reasoning effort inherited from the session), not by
the harnesses this eval targets, so they are not comparable to real runs and live here only
as worked examples.

|                Datetime |              Harness |       LLM | Reasoning effort | Run | Time(s) |     Cost |         Score |                         Grader | Notes |
|                -------- |              ------- |       --- |           ------ | --- | ------- |     ---- |         ----- |                         ------ | ----- |
| 2026-08-09_14:43:42_EDT | Claude Code subagent | Haiku 4.5 |        inherited |  r1 |     168 |  39k tok | 26 + 23 =  49 | Sonnet 5 subagent, prompt v1.2 | NOTE1 |
| 2026-08-09_14:44:11_EDT | Claude Code subagent |  Sonnet 5 |        inherited |  r1 |    1443 | 100k tok | 54 + 46 = 100 | Sonnet 5 subagent, prompt v1.2 | NOTE2 |

NOTE1: JS syntax error on load: A3=0, all C/D runtime 0. Agreement check: Haiku grader scored F+G 29 vs Sonnet 23 (12/18 items exact, all within 1; Haiku uniformly more lenient)
NOTE2: Saturates the eval: clean load, 21/21 assertions, identical benchmark hash across reload. Haiku grader agreed 46/46 (18/18 items exact)


## (9Aug2026) Eval runs
These were in claude code cli where CLAUDE.md and .claude/** context files would be used

NOTE (10Aug2026): det halves re-scored after the eval_ashfall.py discovery fixes (see
set1 note below). Changed: r01 32->52, t04 34->54. Original values in git history.

| 2026-08-09_22:37:30_EDT | Claude Code (bare) | claude-opus-5 (max)      | t15 | xxxxxx | $xxxxx   | xx + xxxx = xxxxx | xxxx |
|                Datetime |            Harness |   LLM (Reasoning effort) | Run |   Time |     Cost | det + ai  = Score | Notes |
| ----------------------- | -------------------| -------------------------| --- | ------ | -------- | ----------------- | ----- |
| 2026-08-09_17:11:22_EDT | Claude Code        | claude-haiku-4-5 (low)   | r01 | 01m57s | $ 0.1742 | 52 + 18.8 =  70.8 | v1.2, 3.4k input, 19.7k output,      0 cache read, 36.1k cache write ($0.1742) |
| 2026-08-09_20:05:28_EDT | Claude Code        | claude-haiku-4-5 (medium)| r02 | 03m01s | $ 0.2933 | 45 + 32.8 =  77.8 | v1.2,  100 input, 21.9k output, 101.8k cache read, 86.8k cache write ($0.2933) |
| 2026-08-09_20:05:35_EDT | Claude Code        | claude-haiku-4-5 (high)  | r03 | 02m44s | $ 0.2755 | 31 + 34.0 =  65.0 | v1.2, 1.3k input, 20.6k output,  98.1k cache read, 80.7k cache write ($0.2755) |
| 2026-08-09_20:05:40_EDT | Claude Code        | claude-haiku-4-5 (xhigh) | r04 | 02m27s | $ 0.2671 | 52 + 33.6 =  85.6 | v1.2, 1.3k input, 20.1k output,  98.2k cache read, 77.7k cache write ($0.2671) |
| 2026-08-09_20:05:46_EDT | Claude Code        | claude-haiku-4-5 (max)   | r05 | 02m28s | $ 0.2536 | 39 + 27.0 =  66.0 | v1.2, 1.3k input, 17.3k output,  98.7k cache read, 78.0k cache write ($0.2536) |
| 2026-08-09_22:37:30_EDT | Claude Code        | claude-opus-5 (xhigh)    | t04 | 50m09s | $21.23   | 54 + 46.0 = 100.0 | v1.3, 731 input, 223.3k output, 25.0m cache read, 312.6k cache write ($21.23) |


## (10Aug2026) eval01 set1

**Grader**: sonnet-5 (high)
**Scores**: from command like `./eval01/listscore.py r0{1..5}{a..e}` that (for each rNN) is AVG of the ai grader runs.
**Script**: `./eval01/zrunall.sh` provides a single script for running the entire generate+eval process for one model at a time.
NOTE: Looks like haiku doesnt actually use reasoning effort levels (based on similarity between r11-r15) even though the claude code interface lets you select an effort level. The Claude desktop app lets you select for haiku a deeper thinking mode.
NOTE (10Aug2026 review): det halves re-scored after fixing two eval_ashfall.py scorer bugs:
(1) dev-tab discovery used anchored `^dev\w*$`, missing panels labeled "6 Dev"/"Dev Panel"/
"6. Dev"/"Dev 6" - 9 of 20 candidates lost the whole C1_runtime/C2/C3/D2/D3 cluster to the
scorer even though their panels worked when opened by their real label; (2) "N passed, 0
failed" summaries counted the word "failed" as one failing test, zeroing C3 (6 pts).
Changed rows: r11 37->43, s11 48->54, s13 32->52, s14 34->48, s15 34->54, t12 34->54,
t14 34->54, t15 29->49, u11 34->54, u12 41->47, u14 34->54. AI halves untouched. Remaining
C3 zeros verified genuine by hand: s14 "FAIL - Building deducts its cost", t11 "FAIL The
game is winnable", t13 "FAIL The game is losable". u13 unchanged: real defect (hidden
#modal div intercepts all pointer events; no user could click anything). r15 prints test
results nowhere on the page. Original values in git history and runall logs.

|                Datetime |            Harness |   LLM (Reasoning effort) | Run |   Time |     Cost | det + ai  = Score | Notes |
| ----------------------- | -------------------| -------------------------| --- | ------ | -------- | ----------------- | ----- |
| 2026-08-09_17:11:22_EDT | Claude Code (bare) | claude-haiku-4-5 (low)   | r11 |  3m19s | $ 0.1771 | 43 + 38.6 =  81.6 |  14 input,  22.5k output,    37.7k cache read,  29.4k cache write ($ 0.1771) |
| 2026-08-09_20:05:28_EDT | Claude Code (bare) | claude-haiku-4-5 (medium)| r12 |  2m36s | $ 0.1431 | 49 + 29.4 =  78.4 |  14 input,  17.8k output,    37.7k cache read,  24.4k cache write ($ 0.1431) |
| 2026-08-09_20:05:35_EDT | Claude Code (bare) | claude-haiku-4-5 (high)  | r13 |  3m14s | $ 0.1739 | 50 + 30.6 =  80.6 |  14 input,  22.2k output,    37.7k cache read,  28.6k cache write ($ 0.1739) |
| 2026-08-09_20:05:40_EDT | Claude Code (bare) | claude-haiku-4-5 (xhigh) | r14 |  2m50s | $ 0.1507 | 52 + 27.4 =  79.4 |  14 input,  19.1k output,    37.7k cache read,  24.9k cache write ($ 0.1507) |
| 2026-08-09_20:05:46_EDT | Claude Code (bare) | claude-haiku-4-5 (max)   | r15 |  2m41s | $ 0.1500 | 41 + 32.2 =  73.2 |  14 input,  18.6k output,    36.9k cache read,  25.8k cache write ($ 0.1500) |

| 2026-08-10_09:22:17_EDT | Claude Code (bare) | claude-sonnet-5 (low)    | s11 | 04m31s | $ 1.0978 | 54 + 45.0 =  99.0 |  46 input,  30.7k output,  1278.2k cache read,  42.0k cache write ($ 1.0978) |
| 2026-08-10_09:21:57_EDT | Claude Code (bare) | claude-sonnet-5 (medium) | s12 | 10m11s | $ 2.2728 | 54 + 42.4 =  96.4 |  58 input,  60.5k output,  2461.2k cache read, 104.1k cache write ($ 2.2728) |
| 2026-08-10_09:21:35_EDT | Claude Code (bare) | claude-sonnet-5 (high)   | s13 | 17m04s | $ 3.9825 | 52 + 45.8 =  97.8 |  88 input, 102.8k output,  5455.7k cache read, 133.5k cache write ($ 3.9825) |
| 2026-08-10_09:21:14_EDT | Claude Code (bare) | claude-sonnet-5 (xhigh)  | s14 | 36m57s | $ 9.9160 | 48 + 42.4 =  90.4 | 228 input, 219.2k output, 17686.8k cache read, 219.9k cache write ($ 9.9160) |
| 2026-08-10_09:20:54_EDT | Claude Code (bare) | claude-sonnet-5 (max)    | s15 | 43m05s | $ 9.2433 | 54 + 46.0 = 100.0 | 148 input, 250.4k output, 13214.4k cache read, 253.5k cache write ($ 9.2433) |

| 2026-08-10_12:44:14_EDT | Claude Code (bare) | claude-opus-5 (low)      | t11 | 13m17s | $ 3.6710 | 48 + 46.0 =  94.0 |  53 input,  71.1k output,  2202.1k cache read,  79.1k cache write ($ 3.6710) |
| 2026-08-10_12:43:52_EDT | Claude Code (bare) | claude-opus-5 (medium)   | t12 | 15m25s | $ 4.6256 | 54 + 45.8 =  99.8 |  74 input,  78.0k output,  3408.8k cache read,  96.9k cache write ($ 4.6256) |
| 2026-08-10_12:43:32_EDT | Claude Code (bare) | claude-opus-5 (high)     | t13 | 31m19s | $ 8.3309 | 48 + 46.0 =  94.0 |  99 input, 168.3k output,  5626.6k cache read, 130.7k cache write ($ 8.3309) |
| 2026-08-10_12:43:10_EDT | Claude Code (bare) | claude-opus-5 (xhigh)    | t14 | 32m23s | $10.0894 | 54 + 46.0 = 100.0 | 114 input, 166.4k output,  8288.4k cache read, 178.3k cache write ($10.0894) |
| 2026-08-10_12:42:50_EDT | Claude Code (bare) | claude-opus-5 (max)      | t15 | 38m42s | $12.9251 | 49 + 45.8 =  94.8 | 152 input, 197.2k output, 12150.1k cache read, 191.8k cache write ($12.9251) |

| 2026-08-09_17:11:22_EDT | Claude Code (bare) | claude-fable-5 (low)     | u11 |  6m32s | $ 2.6521 | 54 + 46.0 = 100.0 | 10 input,   33.9k output,   198.2k cache read,  38.0k cache write ($ 2.6521) |
| 2026-08-09_20:05:28_EDT | Claude Code (bare) | claude-fable-5 (medium)  | u12 | 10m36s | $ 4.7398 | 47 + 46.0 =  93.0 | 25 input,   54.0k output,   812.9k cache read,  61.1k cache write ($ 4.7398) |
| 2026-08-09_20:05:35_EDT | Claude Code (bare) | claude-fable-5 (high)    | u13 | 26m07s | $13.2028 | 29 + 46.0 =  75.0 | 50 input,  133.7k output,  3098.1k cache read, 162.1k cache write ($13.2028) |
| 2026-08-09_20:05:40_EDT | Claude Code (bare) | claude-fable-5 (xhigh)   | u14 | 26m15s | $12.3045 | 54 + 46.0 = 100.0 | 53 input,  125.4k output,  2858.4k cache read, 147.7k cache write ($12.3045) |
| 2026-08-09_20:05:46_EDT | Claude Code (bare) | claude-fable-5 (max)     | u15 | 50m04s | $17.7021 | 54 + 46.0 = 100.0 | 89 input,  215.8k output,  3993.4k cache read, 145.9k cache write ($17.7021) |


## (11Aug2026) eval01 set2

|                Datetime |            Harness |   LLM (Reasoning effort) | Run |   Time |     Cost | det + ai  = Score | Notes |
| ----------------------- | -------------------| -------------------------| --- | ------ | -------- | ----------------- | ----- |
| 2026-08-10_23:04:41_EDT | Claude Code (bare) | claude-haiku-4-5 (low)   | r21 |  3m05s | $ 0.1571 | 23 + 30.6 =  53.6 |  17 input,  20.7k output,    42.0k cache read,  23.7k cache write ($ 0.1571) |
| 2026-08-10_23:04:21_EDT | Claude Code (bare) | claude-haiku-4-5 (medium)| r22 |  4m33s | $ 0.2301 | 45 + 26.6 =  71.6 |  17 input,  31.2k output,    42.0k cache read,  34.1k cache write ($ 0.2301) |
| 2026-08-10_23:04:01_EDT | Claude Code (bare) | claude-haiku-4-5 (high)  | r23 |  3m06s | $ 0.1586 | 34 + 33.8 =  67.8 |  17 input,  21.0k output,    42.0k cache read,  23.7k cache write ($ 0.1586) |
| 2026-08-10_23:03:41_EDT | Claude Code (bare) | claude-haiku-4-5 (xhigh) | r24 |  3m01s | $ 0.1538 | 39 + 28.8 =  67.8 |  17 input,  20.3k output,    42.0k cache read,  23.2k cache write ($ 0.1538) |
| 2026-08-10_23:03:21_EDT | Claude Code (bare) | claude-haiku-4-5 (max)   | r25 |  6m55s | $ 0.3175 | 33 + 28.2 =  61.2 |  27 input,  47.3k output,    80.1k cache read,  35.7k cache write ($ 0.3175) |

| 2026-08-10_23:24:23_EDT | Claude Code (bare) | claude-sonnet-5 (low)    | s21 |  5m13s | $ 1.5154 | 54 + 45.0 =  99.0 |  72 input,  34.4k output,  2229.0k cache read,  54.9k cache write ($ 1.5154) |
| 2026-08-10_23:24:03_EDT | Claude Code (bare) | claude-sonnet-5 (medium) | s22 |  9m18s | $ 2.5066 | 54 + 46.0 = 100.0 |  74 input,  58.2k output,  3413.1k cache read, 101.4k cache write ($ 2.5066) |
| 2026-08-10_23:23:43_EDT | Claude Code (bare) | claude-sonnet-5 (high)   | s23 | 14m06s | $ 3.4277 | 47 + 45.8 =  92.8 |  98 input,  84.5k output,  5092.7k cache read, 105.1k cache write ($ 3.4277) |
| 2026-08-10_23:23:23_EDT | Claude Code (bare) | claude-sonnet-5 (xhigh)  | s24 | 36m19s | $ 9.6881 | 48 + 45.8 =  93.8 | 216 input, 223.3k output, 16586.7k cache read, 226.7k cache write ($ 9.6881) |
| 2026-08-10_23:23:03_EDT | Claude Code (bare) | claude-sonnet-5 (max)    | s25 | 38m03s | $ 9.4786 | 45 + 45.8 =  90.8 | 198 input, 220.0k output, 16169.5k cache read, 220.8k cache write ($ 9.4786) |

| 2026-08-11_09:30:25_EDT | Claude Code (bare) | claude-opus-5 (low)      | t21 | 13m27s | $ 3.3940 | 45 + 46.0 =  91.0 |  36 input,  73.6k output,  1490.8k cache read,  80.6k cache write ($ 3.3940) |
| 2026-08-11_09:30:03_EDT | Claude Code (bare) | claude-opus-5 (medium)   | t22 | 16m36s | $ 5.3940 | 54 + 46.0 = 100.0 |  86 input,  77.9k output,  4452.1k cache read, 121.8k cache write ($ 5.3940) |
| 2026-08-11_09:29:43_EDT | Claude Code (bare) | claude-opus-5 (high)     | t23 | 29m02s | $ 7.2858 | 52 + 46.0 =  98.0 |  83 input, 153.1k output,  4406.5k cache read, 125.3k cache write ($ 7.2858) |
| 2026-08-11_09:29:21_EDT | Claude Code (bare) | claude-opus-5 (xhigh)    | t24 | 35m51s | $11.4945 | 54 + 46.0 = 100.0 | 133 input, 177.0k output, 10175.5k cache read, 197.9k cache write ($11.4945) |
| 2026-08-11_09:29:01_EDT | Claude Code (bare) | claude-opus-5 (max)      | t25 | 37m06s | $ 9.8742 | 54 + 46.0 = 100.0 | 123 input, 182.0k output,  7062.9k cache read, 178.9k cache write ($ 9.8742) |

| 2026-08-11_00:44:32_EDT | Claude Code (bare) | claude-fable-5 (low)     | u21 |  5m38s | $ 2.6566 | 54 + 46.0 = 100.0 |  18 input,  30.2k output,   399.9k cache read,  37.3k cache write ($ 2.6566) |
| 2026-08-11_00:44:12_EDT | Claude Code (bare) | claude-fable-5 (medium)  | u22 | 12m10s | $ 5.6697 | 54 + 46.0 = 100.0 |  38 input,  58.5k output,  1406.6k cache read,  66.7k cache write ($ 5.6697) |
| 2026-08-11_00:43:51_EDT | Claude Code (bare) | claude-fable-5 (high)    | u23 | 13m39s | $ 5.9850 | 32 + 46.0 =  78.0 |  29 input,  67.2k output,  1126.5k cache read,  74.8k cache write ($ 5.9850) |
| 2026-08-11_00:43:30_EDT | Claude Code (bare) | claude-fable-5 (xhigh)   | u24 | 43m46s | $15.3180 | 54 + 46.0 = 100.0 |  66 input, 203.8k output,  2543.6k cache read, 129.2k cache write ($15.3180) |
| 2026-08-11_00:43:10_EDT | Claude Code (bare) | claude-fable-5 (max)     | u25 | 38m38s | $13.6410 | 29 + 43.8 =  72.8 |  48 input, 170.3k output,  2509.1k cache read, 130.7k cache write ($13.6410) |

