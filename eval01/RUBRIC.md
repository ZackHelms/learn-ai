# Ashfall Outpost - Eval Rubric v1.2

Scoring rubric for the ASHFALL OUTPOST single-prompt LLM eval. One prompt is pasted verbatim
into each model / reasoning-effort level; each run produces one self-contained HTML file,
which is then scored out of 100. This file defines what the points mean; the run protocol lives in
[README.md](README.md).

Changes in v1.2 (2026-08-09): no point values changed. The runtime checker now switches to a
Dev/Debug tab before hunting for the Run Tests / Run Benchmark buttons (a compliant candidate
used to lose all of C2-D3 for putting them in the Dev tab the prompt asked for). `--merge` now
accepts the grader's raw reply: it extracts the last JSON object, normalizes key spellings,
and scores skipped items as 0 with a warning. GRADER_PROMPT.md gained an explicit no-cascade
rule: a file-wide defect (e.g. one JS syntax error) is priced once by A3, and the AI grader
scores source-level wiring past it - without the rule, two graders legitimately read the same
broken-but-detailed candidate as 28/46 and 0/46. Protocol and reporting conventions moved to
README.md.

Grading is split by who can judge it reliably:

- **D** = deterministic. Scored by `eval_ashfall.py`. No model in the loop, no judgment calls.
- **AI** = model-graded. Scored by a strong LLM using `GRADER_PROMPT.md`.

Total: 100 points. Deterministic covers 54, AI covers 46.

---

## Category A - Executes (10 pts, D)

| ID | Check | Pts |
|----|-------|-----|
| A1 | File is well-formed HTML with at least one inline script | 3 |
| A2 | Output is not truncated (closes `</html>`, no cut-off code fence) | 3 |
| A3 | Loads in a headless browser with zero console errors and zero page errors | 4 |

A3 requires the runtime pass (on by default; `--noruntime` skips it).

---

## Category B - Instruction compliance (15 pts, D)

Measures whether the model followed explicit constraints in the prompt. This is where cheap
models and low reasoning-effort levels leak first.

| ID | Check | Pts |
|----|-------|-----|
| B1 | No `localStorage`, `sessionStorage`, `indexedDB`, or `document.cookie` | 4 |
| B2 | No external resources (remote `src`/`href`, CDN, `fetch`, `XMLHttpRequest`, `@import url`) | 4 |
| B3 | No `Math.random` anywhere | 3 |
| B4 | Evidence of a seeded PRNG (mulberry32 / LCG / xorshift pattern with a seed variable) | 2 |
| B5 | Assumptions comment block near the top of the file | 2 |

B1 and B2 are scored all-or-nothing per check: a single violation costs the full sub-score.
That is intentional. "Mostly followed the constraint" is not following the constraint.

---

## Category C - Self-test harness (15 pts, D)

The prompt asks for a Dev panel with a "Run Tests" button and at least 15 real assertions.
This category measures whether the model verifies its own work.

| ID | Check | Pts |
|----|-------|-----|
| C1 | A control whose label matches /run tests/i exists and is clickable | 4 |
| C2 | Clicking it reports 15 or more assertions | 5 |
| C3 | Zero reported failures | 6 |

C2 scales: `min(assertions, 15) / 15 * 5`, rounded to one decimal.

Assertion *quality* (whether the tests check real invariants or trivialities) is graded by the
AI grader as part of system 13 in Category F, not here.

---

## Category D - Determinism (10 pts, D)

| ID | Check | Pts |
|----|-------|-----|
| D1 | A control whose label matches /run benchmark/i exists | 3 |
| D2 | Clicking it emits a hash-like token | 3 |
| D3 | The hash is identical after a full page reload and a second run | 4 |

Note: hashes are only comparable to *themselves* within one candidate file. Do not compare
hashes across models - different implementations legitimately produce different state shapes.

---

## Category E - UI mechanics (4 pts, D)

| ID | Check | Pts |
|----|-------|-----|
| E1 | No horizontal overflow at a 360px viewport | 2 |
| E2 | Clicking "End Turn" measurably changes rendered page text | 2 |

Aesthetics, layout quality, and tooltip usefulness are AI-graded under system 12.

---

## Category F - Systems implemented (26 pts, AI)

The 13 numbered systems from the prompt, 2 points each.

| # | System |
|---|--------|
| 1 | Core loop, single state object, seeded PRNG, fixed resolution order |
| 2 | 8x8 map, seeded terrain, build placement, adjacency bonuses |
| 3 | Economy with real production chains and storage caps |
| 4 | Individual colonists with skill, fatigue, job assignment |
| 5 | Needs, consumption, morale consequences, recoverable |
| 6 | Research tree, 8+ nodes, prerequisites, unlocks |
| 7 | Weighted event deck, 10+ events, 4+ with meaningful choices, cooldowns |
| 8 | Trade caravan with responsive pricing and limited inventory |
| 9 | Ashstorms with scaling severity, damage, mitigation, repair |
| 10 | Save/load via export/import text with validation |
| 11 | Win/lose conditions and scored summary |
| 12 | Tabs, log, tooltips, keyboard shortcuts, responsive |
| 13 | Dev panel with real self-tests and headless benchmark |

Per system: **0** = absent or a non-functional stub. **1** = present but shallow, hardcoded,
or disconnected from the rest of the game. **2** = functional and wired into other systems.

A system marked `// TODO` and left unimplemented scores 0, but honest TODO marking is noted in
the grader output as a separate signal. It is not worth points; it is worth knowing.

---

## Category G - Interaction depth (20 pts, AI)

The differentiator. Weak runs produce parallel systems that never touch. Five traces, 0-4 each.

| ID | Trace | Pts |
|----|-------|-----|
| G1 | A research unlock measurably changes a production yield | 4 |
| G2 | Production shortfall -> unmet need -> morale drop -> reduced labor output | 4 |
| G3 | Ashstorm -> building damage -> output loss -> repair cost -> recovery | 4 |
| G4 | Trade prices respond to player stockpiles and/or drifting global supply | 4 |
| G5 | Event choices durably mutate state rather than printing flavor text | 4 |

Per trace: **0** = the link does not exist. **1** = cosmetic or logged but not applied to state.
**2** = applied but only via a single hardcoded constant. **3** = applied through the real
pipeline with a minor gap. **4** = fully wired, visible to the player, and traceable in code.

---

## How to run a full grade

See "Protocol - run one candidate" in [README.md](README.md). Short version: deterministic
pass with `eval_ashfall.py`, AI pass by handing `GRADER_PROMPT.md` plus the
candidate to a fixed grader model, then `--merge` for the total and `--report` to compare.

## Known weak spots (fix in a later iteration)

- C2/C3 parse assertion counts from rendered text by regex. A model that reports results in an
  unusual format will be undercounted. Cross-check with the AI grader's read of system 13.
- D2 hash detection looks for a hex-ish token near the word "hash". Same caveat.
- Button discovery is by visible text. A model that labels the button "Self Test" instead of
  "Run Tests" loses C1 despite complying in spirit. Either tighten the wording in the prompt or
  widen the matcher. (The narrower case - buttons hidden inside an inactive Dev tab - is fixed
  as of v1.2; the checker now tries Dev/Debug/Tests-labelled tabs before giving up.)
- The ceiling is reachable: a strong model has scored 100/100 (see the pipeline-validation
  table in RESULTS.md). The eval discriminates in the low and middle range; if every candidate
  you care about clusters at the top, the task needs to get harder (saturation).
