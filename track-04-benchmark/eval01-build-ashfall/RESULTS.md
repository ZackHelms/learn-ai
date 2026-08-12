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
NOTE (12Aug2026): re-scored again under the second fix batch (described in the set3 note):
r01 52->54, r02 45->47, r03 31->33, r04 52->54, r05 39->41 - all B5, the assumptions block
at the top of the JS instead of the file head. t04 unchanged.

| 2026-08-09_22:37:30_EDT | Claude Code (bare) | claude-opus-5 (max)      | t15 | xxxxxx | $xxxxx   | xx + xxxx = xxxxx | xxxx |
|                Datetime |            Harness |   LLM (Reasoning effort) | Run |   Time |     Cost | det + ai  = Score | Notes |
| ----------------------- | -------------------| -------------------------| --- | ------ | -------- | ----------------- | ----- |
| 2026-08-09_17:11:22_EDT | Claude Code        | claude-haiku-4-5 (low)   | r01 | 01m57s | $ 0.1742 | 54 + 18.8 =  72.8 | v1.2, 3.4k input, 19.7k output,      0 cache read, 36.1k cache write ($0.1742) |
| 2026-08-09_20:05:28_EDT | Claude Code        | claude-haiku-4-5 (medium)| r02 | 03m01s | $ 0.2933 | 47 + 32.8 =  79.8 | v1.2,  100 input, 21.9k output, 101.8k cache read, 86.8k cache write ($0.2933) |
| 2026-08-09_20:05:35_EDT | Claude Code        | claude-haiku-4-5 (high)  | r03 | 02m44s | $ 0.2755 | 33 + 34.0 =  67.0 | v1.2, 1.3k input, 20.6k output,  98.1k cache read, 80.7k cache write ($0.2755) |
| 2026-08-09_20:05:40_EDT | Claude Code        | claude-haiku-4-5 (xhigh) | r04 | 02m27s | $ 0.2671 | 54 + 33.6 =  87.6 | v1.2, 1.3k input, 20.1k output,  98.2k cache read, 77.7k cache write ($0.2671) |
| 2026-08-09_20:05:46_EDT | Claude Code        | claude-haiku-4-5 (max)   | r05 | 02m28s | $ 0.2536 | 41 + 27.0 =  68.0 | v1.2, 1.3k input, 17.3k output,  98.7k cache read, 78.0k cache write ($0.2536) |
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
NOTE (12Aug2026): det halves re-scored under the second fix batch (described in the set3
note). B5, assumptions comment now accepted from the top of the file through the head of
the first script block: r11 43->45, r12 49->51, r13 50->52, r14 52->54, r15 41->43,
t15 49->51. B3, banned-API grep now sees executable JS only: u13 29->32 (its one counted
"Math.random" sat in a help-text string saying it is never used). t15's B3 zero stands: it
assigns and restores Math.random in a self-test trap - executable code by the letter of
"no Math.random anywhere". AI halves untouched.

|                Datetime |            Harness |   LLM (Reasoning effort) | Run |   Time |     Cost | det + ai  = Score | Notes |
| ----------------------- | -------------------| -------------------------| --- | ------ | -------- | ----------------- | ----- |
| 2026-08-09_17:11:22_EDT | Claude Code (bare) | claude-haiku-4-5 (low)   | r11 |  3m19s | $ 0.1771 | 45 + 38.6 =  83.6 |  14 input,  22.5k output,    37.7k cache read,  29.4k cache write ($ 0.1771) |
| 2026-08-09_20:05:28_EDT | Claude Code (bare) | claude-haiku-4-5 (medium)| r12 |  2m36s | $ 0.1431 | 51 + 29.4 =  80.4 |  14 input,  17.8k output,    37.7k cache read,  24.4k cache write ($ 0.1431) |
| 2026-08-09_20:05:35_EDT | Claude Code (bare) | claude-haiku-4-5 (high)  | r13 |  3m14s | $ 0.1739 | 52 + 30.6 =  82.6 |  14 input,  22.2k output,    37.7k cache read,  28.6k cache write ($ 0.1739) |
| 2026-08-09_20:05:40_EDT | Claude Code (bare) | claude-haiku-4-5 (xhigh) | r14 |  2m50s | $ 0.1507 | 54 + 27.4 =  81.4 |  14 input,  19.1k output,    37.7k cache read,  24.9k cache write ($ 0.1507) |
| 2026-08-09_20:05:46_EDT | Claude Code (bare) | claude-haiku-4-5 (max)   | r15 |  2m41s | $ 0.1500 | 43 + 32.2 =  75.2 |  14 input,  18.6k output,    36.9k cache read,  25.8k cache write ($ 0.1500) |
| 2026-08-10_09:22:17_EDT | Claude Code (bare) | claude-sonnet-5 (low)    | s11 | 04m31s | $ 1.0978 | 54 + 45.0 =  99.0 |  46 input,  30.7k output,  1278.2k cache read,  42.0k cache write ($ 1.0978) |
| 2026-08-10_09:21:57_EDT | Claude Code (bare) | claude-sonnet-5 (medium) | s12 | 10m11s | $ 2.2728 | 54 + 42.4 =  96.4 |  58 input,  60.5k output,  2461.2k cache read, 104.1k cache write ($ 2.2728) |
| 2026-08-10_09:21:35_EDT | Claude Code (bare) | claude-sonnet-5 (high)   | s13 | 17m04s | $ 3.9825 | 52 + 45.8 =  97.8 |  88 input, 102.8k output,  5455.7k cache read, 133.5k cache write ($ 3.9825) |
| 2026-08-10_09:21:14_EDT | Claude Code (bare) | claude-sonnet-5 (xhigh)  | s14 | 36m57s | $ 9.9160 | 48 + 42.4 =  90.4 | 228 input, 219.2k output, 17686.8k cache read, 219.9k cache write ($ 9.9160) |
| 2026-08-10_09:20:54_EDT | Claude Code (bare) | claude-sonnet-5 (max)    | s15 | 43m05s | $ 9.2433 | 54 + 46.0 = 100.0 | 148 input, 250.4k output, 13214.4k cache read, 253.5k cache write ($ 9.2433) |
| 2026-08-10_12:44:14_EDT | Claude Code (bare) | claude-opus-5 (low)      | t11 | 13m17s | $ 3.6710 | 48 + 46.0 =  94.0 |  53 input,  71.1k output,  2202.1k cache read,  79.1k cache write ($ 3.6710) |
| 2026-08-10_12:43:52_EDT | Claude Code (bare) | claude-opus-5 (medium)   | t12 | 15m25s | $ 4.6256 | 54 + 45.8 =  99.8 |  74 input,  78.0k output,  3408.8k cache read,  96.9k cache write ($ 4.6256) |
| 2026-08-10_12:43:32_EDT | Claude Code (bare) | claude-opus-5 (high)     | t13 | 31m19s | $ 8.3309 | 48 + 46.0 =  94.0 |  99 input, 168.3k output,  5626.6k cache read, 130.7k cache write ($ 8.3309) |
| 2026-08-10_12:43:10_EDT | Claude Code (bare) | claude-opus-5 (xhigh)    | t14 | 32m23s | $10.0894 | 54 + 46.0 = 100.0 | 114 input, 166.4k output,  8288.4k cache read, 178.3k cache write ($10.0894) |
| 2026-08-10_12:42:50_EDT | Claude Code (bare) | claude-opus-5 (max)      | t15 | 38m42s | $12.9251 | 51 + 45.8 =  96.8 | 152 input, 197.2k output, 12150.1k cache read, 191.8k cache write ($12.9251) |
| 2026-08-09_17:11:22_EDT | Claude Code (bare) | claude-fable-5 (low)     | u11 |  6m32s | $ 2.6521 | 54 + 46.0 = 100.0 | 10 input,   33.9k output,   198.2k cache read,  38.0k cache write ($ 2.6521) |
| 2026-08-09_20:05:28_EDT | Claude Code (bare) | claude-fable-5 (medium)  | u12 | 10m36s | $ 4.7398 | 47 + 46.0 =  93.0 | 25 input,   54.0k output,   812.9k cache read,  61.1k cache write ($ 4.7398) |
| 2026-08-09_20:05:35_EDT | Claude Code (bare) | claude-fable-5 (high)    | u13 | 26m07s | $13.2028 | 32 + 46.0 =  78.0 | 50 input,  133.7k output,  3098.1k cache read, 162.1k cache write ($13.2028) |
| 2026-08-09_20:05:40_EDT | Claude Code (bare) | claude-fable-5 (xhigh)   | u14 | 26m15s | $12.3045 | 54 + 46.0 = 100.0 | 53 input,  125.4k output,  2858.4k cache read, 147.7k cache write ($12.3045) |
| 2026-08-09_20:05:46_EDT | Claude Code (bare) | claude-fable-5 (max)     | u15 | 50m04s | $17.7021 | 54 + 46.0 = 100.0 | 89 input,  215.8k output,  3993.4k cache read, 145.9k cache write ($17.7021) |


## (11Aug2026) eval01 set2

**Grader**: sonnet-5 (high), prompt v1.3
NOTE (11Aug2026 review): the first opus5 sweep (00:10, log runall.20260811_001010) lost
t25 to a harness failure - claude exited 1 after 10m6s; root cause unrecoverable because
the later re-run clobbered the scratch dir (generate.sh now retries harness failures and
preserves every failed attempt under runs/.gen-work/failed/). eval_ashfall.py and grade.sh
then refused to run because one of five candidates was missing (both now continue and
print ERROR per missing file). The whole opus5 sweep was re-run 09:29 (that is the t2x
data below); the unscored first-attempt t21-t24 are stashed in runs/zHOLD-t2-fail/.
u23/u25 det collapse verified genuine by hand, same defect as set1 u13: the intro modal
(#overlay/#modal) is styled `display:flex`, which overrides the HTML `hidden` attribute,
so a full-viewport backdrop intercepts every click - no user could play either. The ai
half is blind to it (code reads fine): 46.0/43.8. u25's B3 -3 is a scorer false positive
(visible help text "Math.random is never used" matches the grep); fix tracked in TODO.md,
not applied mid-set - u25 det reads 29, would be 32 under the fixed scorer.
NOTE (12Aug2026): det halves re-scored under the second fix batch (described in the set3
note); u25 reads 32 now, as predicted above. B5 top-of-JS assumptions blocks: r21 23->25,
r22 45->47, r23 34->36, r24 39->41, r25 33->35. B3 on executable JS only: s25 45->48,
t21 45->48, u25 29->32 - each counted occurrence was a string or visible text asserting
compliance (t21's self-test scans its own source for the call). AI halves untouched.

|                Datetime |            Harness |   LLM (Reasoning effort) | Run |   Time |     Cost | det + ai  = Score | Notes |
| ----------------------- | -------------------| -------------------------| --- | ------ | -------- | ----------------- | ----- |
| 2026-08-10_23:04:41_EDT | Claude Code (bare) | claude-haiku-4-5 (low)   | r21 |  3m05s | $ 0.1571 | 25 + 30.6 =  55.6 |  17 input,  20.7k output,    42.0k cache read,  23.7k cache write ($ 0.1571) |
| 2026-08-10_23:04:21_EDT | Claude Code (bare) | claude-haiku-4-5 (medium)| r22 |  4m33s | $ 0.2301 | 47 + 26.6 =  73.6 |  17 input,  31.2k output,    42.0k cache read,  34.1k cache write ($ 0.2301) |
| 2026-08-10_23:04:01_EDT | Claude Code (bare) | claude-haiku-4-5 (high)  | r23 |  3m06s | $ 0.1586 | 36 + 33.8 =  69.8 |  17 input,  21.0k output,    42.0k cache read,  23.7k cache write ($ 0.1586) |
| 2026-08-10_23:03:41_EDT | Claude Code (bare) | claude-haiku-4-5 (xhigh) | r24 |  3m01s | $ 0.1538 | 41 + 28.8 =  69.8 |  17 input,  20.3k output,    42.0k cache read,  23.2k cache write ($ 0.1538) |
| 2026-08-10_23:03:21_EDT | Claude Code (bare) | claude-haiku-4-5 (max)   | r25 |  6m55s | $ 0.3175 | 35 + 28.2 =  63.2 |  27 input,  47.3k output,    80.1k cache read,  35.7k cache write ($ 0.3175) |
| 2026-08-10_23:24:23_EDT | Claude Code (bare) | claude-sonnet-5 (low)    | s21 |  5m13s | $ 1.5154 | 54 + 45.0 =  99.0 |  72 input,  34.4k output,  2229.0k cache read,  54.9k cache write ($ 1.5154) |
| 2026-08-10_23:24:03_EDT | Claude Code (bare) | claude-sonnet-5 (medium) | s22 |  9m18s | $ 2.5066 | 54 + 46.0 = 100.0 |  74 input,  58.2k output,  3413.1k cache read, 101.4k cache write ($ 2.5066) |
| 2026-08-10_23:23:43_EDT | Claude Code (bare) | claude-sonnet-5 (high)   | s23 | 14m06s | $ 3.4277 | 47 + 45.8 =  92.8 |  98 input,  84.5k output,  5092.7k cache read, 105.1k cache write ($ 3.4277) |
| 2026-08-10_23:23:23_EDT | Claude Code (bare) | claude-sonnet-5 (xhigh)  | s24 | 36m19s | $ 9.6881 | 48 + 45.8 =  93.8 | 216 input, 223.3k output, 16586.7k cache read, 226.7k cache write ($ 9.6881) |
| 2026-08-10_23:23:03_EDT | Claude Code (bare) | claude-sonnet-5 (max)    | s25 | 38m03s | $ 9.4786 | 48 + 45.8 =  93.8 | 198 input, 220.0k output, 16169.5k cache read, 220.8k cache write ($ 9.4786) |
| 2026-08-11_09:30:25_EDT | Claude Code (bare) | claude-opus-5 (low)      | t21 | 13m27s | $ 3.3940 | 48 + 46.0 =  94.0 |  36 input,  73.6k output,  1490.8k cache read,  80.6k cache write ($ 3.3940) |
| 2026-08-11_09:30:03_EDT | Claude Code (bare) | claude-opus-5 (medium)   | t22 | 16m36s | $ 5.3940 | 54 + 46.0 = 100.0 |  86 input,  77.9k output,  4452.1k cache read, 121.8k cache write ($ 5.3940) |
| 2026-08-11_09:29:43_EDT | Claude Code (bare) | claude-opus-5 (high)     | t23 | 29m02s | $ 7.2858 | 52 + 46.0 =  98.0 |  83 input, 153.1k output,  4406.5k cache read, 125.3k cache write ($ 7.2858) |
| 2026-08-11_09:29:21_EDT | Claude Code (bare) | claude-opus-5 (xhigh)    | t24 | 35m51s | $11.4945 | 54 + 46.0 = 100.0 | 133 input, 177.0k output, 10175.5k cache read, 197.9k cache write ($11.4945) |
| 2026-08-11_09:29:01_EDT | Claude Code (bare) | claude-opus-5 (max)      | t25 | 37m06s | $ 9.8742 | 54 + 46.0 = 100.0 | 123 input, 182.0k output,  7062.9k cache read, 178.9k cache write ($ 9.8742) |
| 2026-08-11_00:44:32_EDT | Claude Code (bare) | claude-fable-5 (low)     | u21 |  5m38s | $ 2.6566 | 54 + 46.0 = 100.0 |  18 input,  30.2k output,   399.9k cache read,  37.3k cache write ($ 2.6566) |
| 2026-08-11_00:44:12_EDT | Claude Code (bare) | claude-fable-5 (medium)  | u22 | 12m10s | $ 5.6697 | 54 + 46.0 = 100.0 |  38 input,  58.5k output,  1406.6k cache read,  66.7k cache write ($ 5.6697) |
| 2026-08-11_00:43:51_EDT | Claude Code (bare) | claude-fable-5 (high)    | u23 | 13m39s | $ 5.9850 | 32 + 46.0 =  78.0 |  29 input,  67.2k output,  1126.5k cache read,  74.8k cache write ($ 5.9850) |
| 2026-08-11_00:43:30_EDT | Claude Code (bare) | claude-fable-5 (xhigh)   | u24 | 43m46s | $15.3180 | 54 + 46.0 = 100.0 |  66 input, 203.8k output,  2543.6k cache read, 129.2k cache write ($15.3180) |
| 2026-08-11_00:43:10_EDT | Claude Code (bare) | claude-fable-5 (max)     | u25 | 38m38s | $13.6410 | 32 + 43.8 =  75.8 |  48 input, 170.3k output,  2509.1k cache read, 130.7k cache write ($13.6410) |



## (11Aug2026) eval01 set3

**Grader**: sonnet-5 (high), prompt v1.3
**Validation**: first run of the hardened pipeline (generate.sh harness-failure retries, eval/grade
continue-on-missing). 20/20 generations succeeded on attempt 1 and all 100 gradings landed, so the
new retry/continue paths stayed idle in production; they were exercised beforehand against a stubbed
claude CLI.
NOTE (11Aug2026): scorer artifacts found in this set, queued as one fix + re-score batch in TODO.md:
(1) t33 det 34 is depressed ~20 pts by a discovery blind spot - its compact tab label "6Dev" defeats
the \bdev\b tab walk, and its tab bar re-renders on every click, detaching the fallback walker's
stale element handles. Verified by hand: 6Dev -> Run Tests opens and clicks fine for a human.
(2) B3 "Math.random" false positives on t31 and t34 (-3 each): the string appears only in self-test
names asserting it is NOT used - same class as set2 u25. (3) All five haiku runs plus t35 lost B5
(-2) with a real assumptions comment sitting past the scorer's 4KB window (r31: line 227) - six
correlated hits after 0/20 in sets 1-2; runs within a set evidently share time-local behavior.
Genuine defects, verified by hand: t34 (opus xhigh) det 25 - one mismatched quote at line 2391
closes a double-quoted string with a single quote, killing its only script block; page renders,
nothing is interactive; not truncation (A2 clean). u33 (fable high) det 46: one failing self-test
plus 439px overflow at 360px viewport; no recurrence of the set1/set2 fable modal bug.
Grader integrity: r32c's reply skipped all 13 F items and the lenient vetting accepted it
(listscore warned; r32 ai avg is 20.6 with it, 24.5 without) - grade.sh now rejects incomplete
replies, effective for future sets.
NOTE (12Aug2026): the fix batch queued above is applied, and every scored run in this file
was re-scored locally (det halves only, no API cost). The three fixes, with their set3
effects: (1) tab discovery matches dev/debug/tests/tools at a letter boundary so "6Dev"
resolves, and the last-resort walk re-queries controls after every click instead of holding
a stale snapshot: t33 34->48, recovering C1/C2/D2/D3 (+14, not the ~20 estimated - the
remaining C3 zero is genuine: t33's own test 31 "Total deprivation empties the outpost"
reports FAIL on its page). (2) B1-B3 violation greps now see executable script code with
comments and string literals stripped: t31 43->46, t34 25->28 (self-test names and strings
about Math.random, same class as set2 u25). (3) the B5 4KB-window decision: position kept
but the window redefined - an assumptions comment counts if it STARTS anywhere from the top
of the file through the first 4KB of the first script block, and the word must now sit
inside an actual comment: r31 46->48, r33 52->54, r34 39->41, t35 46->48.
Corrections to the 11Aug note above, found while widening: r32 and r35 have no assumptions
comment at all - genuine B5 zeros, not window artifacts - and the artifact was never
set3-local: the same top-of-JS placement cost every haiku run in sets 0-2 and set1 t15 the
same 2 points ("0/20 in sets 1-2" was wrong). In total 27 runs changed det score across the
four tables above; an audit of every per-check delta confirmed nothing else moved. One
flake caught while auditing: r05's benchmark hash is genuinely unstable (three distinct
values across five hand-run samples), so its D3 zero stands and its delta is B5-only.
Original values in git history.

|                Datetime |            Harness |   LLM (Reasoning effort) | Run |   Time |     Cost | det + ai  = Score | Notes |
| ----------------------- | -------------------| -------------------------| --- | ------ | -------- | ----------------- | ----- |
| 2026-08-11_13:14:38_EDT | Claude Code (bare) | claude-haiku-4-5 (low)   | r31 |  2m41s | $ 0.1378 | 48 + 29.0 =  77.0 |   17 input,  17.9k output,    42.1k cache read,  21.1k cache write ($ 0.1378) |
| 2026-08-11_13:14:16_EDT | Claude Code (bare) | claude-haiku-4-5 (medium)| r32 |  2m38s | $ 0.1372 | 52 + 20.6 =  72.6 |   17 input,  17.8k output,    42.0k cache read,  21.0k cache write ($ 0.1372) |
| 2026-08-11_13:13:56_EDT | Claude Code (bare) | claude-haiku-4-5 (high)  | r33 |  3m03s | $ 0.1595 | 54 + 33.4 =  87.4 |   17 input,  21.0k output,    42.0k cache read,  24.2k cache write ($ 0.1595) |
| 2026-08-11_13:13:34_EDT | Claude Code (bare) | claude-haiku-4-5 (xhigh) | r34 |  2m42s | $ 0.1418 | 41 + 30.8 =  71.8 |   17 input,  18.4k output,    42.0k cache read,  22.0k cache write ($ 0.1418) |
| 2026-08-11_13:13:14_EDT | Claude Code (bare) | claude-haiku-4-5 (max)   | r35 |  7m04s | $ 0.3366 | 44.7 + 28.6 =73.3 |   27 input,  49.0k output,    83.6k cache read,  40.6k cache write ($ 0.3366) |
| 2026-08-11_13:34:48_EDT | Claude Code (bare) | claude-sonnet-5 (low)    | s31 |  4m52s | $ 1.4649 | 54 + 45.0 =  99.0 |   54 input,  34.1k output,  1653.5k cache read,  75.9k cache write ($ 1.4649) |
| 2026-08-11_13:34:28_EDT | Claude Code (bare) | claude-sonnet-5 (medium) | s32 |  8m38s | $ 2.0885 | 48 + 43.8 =  91.8 |   56 input,  54.4k output,  2326.3k cache read,  95.4k cache write ($ 2.0885) |
| 2026-08-11_13:34:06_EDT | Claude Code (bare) | claude-sonnet-5 (high)   | s33 | 19m04s | $ 5.7147 | 46 + 45.0 =  91.0 |  170 input, 108.8k output, 10638.1k cache read, 148.2k cache write ($ 5.7147) |
| 2026-08-11_13:33:44_EDT | Claude Code (bare) | claude-sonnet-5 (xhigh)  | s34 | 29m22s | $ 6.4430 | 48 + 46.0 =  94.0 |  144 input, 176.7k output,  9196.5k cache read, 171.8k cache write ($ 6.4430) |
| 2026-08-11_13:33:24_EDT | Claude Code (bare) | claude-sonnet-5 (max)    | s35 | 38m43s | $ 9.4695 | 54 + 45.8 =  99.8 |  206 input, 226.5k output, 15448.1k cache read, 239.3k cache write ($ 9.4695) |
| 2026-08-11_14:21:53_EDT | Claude Code (bare) | claude-opus-5 (low)      | t31 |  8m21s | $ 1.9172 | 46 + 46.0 =  92.0 |   17 input,  46.0k output,   462.8k cache read,  53.4k cache write ($ 1.9172) |
| 2026-08-11_14:21:33_EDT | Claude Code (bare) | claude-opus-5 (medium)   | t32 | 14m37s | $ 4.1269 | 54 + 45.8 =  99.8 |   57 input,  77.9k output,  2580.2k cache read,  88.6k cache write ($ 4.1269) |
| 2026-08-11_14:21:11_EDT | Claude Code (bare) | claude-opus-5 (high)     | t33 | 22m53s | $ 7.6160 | 48 + 46.0 =  94.0 |   93 input, 110.5k output,  6355.0k cache read, 167.4k cache write ($ 7.6160) |
| 2026-08-11_14:20:48_EDT | Claude Code (bare) | claude-opus-5 (xhigh)    | t34 | 30m38s | $10.0097 | 28 + 46.0 =  74.0 |  106 input, 153.0k output,  8631.6k cache read, 186.6k cache write ($10.0097) |
| 2026-08-11_14:20:28_EDT | Claude Code (bare) | claude-opus-5 (max)      | t35 | 37m47s | $11.0930 | 48 + 46.0 =  94.0 |  116 input, 199.9k output,  8556.2k cache read, 181.6k cache write ($11.0930) |
| 2026-08-11_15:08:46_EDT | Claude Code (bare) | claude-fable-5 (low)     | u31 |  5m51s | $ 2.6765 | 54 + 46.0 = 100.0 |   16 input,  31.0k output,   359.9k cache read,  38.2k cache write ($ 2.6765) |
| 2026-08-11_15:08:26_EDT | Claude Code (bare) | claude-fable-5 (medium)  | u32 |  9m17s | $ 4.1393 | 54 + 46.0 = 100.0 |   23 input,  46.8k output,   715.3k cache read,  54.1k cache write ($ 4.1393) |
| 2026-08-11_15:08:04_EDT | Claude Code (bare) | claude-fable-5 (high)    | u33 | 24m37s | $11.7846 | 46 + 46.0 =  92.0 |   49 input, 121.6k output,  2701.8k cache read, 149.9k cache write ($11.7846) |
| 2026-08-11_15:07:44_EDT | Claude Code (bare) | claude-fable-5 (xhigh)   | u34 | 24m09s | $11.2745 | 54 + 46.0 = 100.0 |   40 input, 119.8k output,  2295.8k cache read, 149.3k cache write ($11.2745) |
| 2026-08-11_15:07:22_EDT | Claude Code (bare) | claude-fable-5 (max)     | u35 | 39m26s | $16.8636 | 54 + 46.0 = 100.0 |   70 input, 185.2k output,  4076.3k cache read, 176.3k cache write ($16.8636) |
