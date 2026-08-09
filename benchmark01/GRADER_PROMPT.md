# AI grader prompt - Ashfall Outpost eval, categories F and G

Use this with your strongest available model at its highest effort/reasoning setting. It grades
only the 46 points that cannot be measured mechanically. Categories A-E are already scored by
`eval_ashfall.py`; the grader must not re-score them.

**How to use:** paste everything between the two `=====` lines below, then paste the candidate
HTML file underneath it. Optionally paste the `<candidate>.eval.json` produced by the
deterministic pass as context. Save the model's JSON reply as `<candidate>.ai.json`, then run:

```bash
python3 eval_ashfall.py <candidate>.html --runtime --merge <candidate>.ai.json
```

Grade every candidate with the *same* grader model and effort level. Switching graders mid-eval
invalidates cross-run comparison. Grade blind where you can: strip the filename and any header
comment naming the authoring model before pasting.

=====================================================================

You are grading one submission in a code eval. A different LLM was given a single prompt asking
it to build ASHFALL OUTPOST, a turn-based colony sim, as one self-contained HTML file in one
shot with no follow-up turns.

Your job is to score two categories by reading the code. Do not run it. Do not fix it. Do not
comment on style. Do not score whether it loads, whether it uses banned APIs, or whether its
self-tests pass - those are already measured by a separate deterministic scorer.

## Grading stance

- Score what the code DOES, not what its comments, variable names, or UI labels claim.
- A button that exists but is not wired to a handler is worth nothing.
- A system whose values are hardcoded and never read by another system is shallow, not complete.
- `// TODO` markers earn no points. Note them separately in `todo_notes`.
- When evidence is ambiguous or you cannot find the wiring, score the LOWER value. Do not give
  benefit of the doubt. A generous grader makes every model look the same, which destroys the
  eval.
- For every non-zero score, cite concrete evidence: a function name, an identifier, or a short
  code fragment (under 15 words). Do not paste large blocks of the candidate back at me.

## Category F - Systems implemented (26 pts, 2 per system)

Score each of the 13 systems 0, 1, or 2.

- **0** - absent, or a non-functional stub.
- **1** - present but shallow: hardcoded, incomplete against the spec below, or not read by any
  other system.
- **2** - functional, meets the spec below, and its outputs are consumed elsewhere in the game.

| # | System | What "2" requires |
|---|--------|-------------------|
| 1 | Core loop | One state object, a seeded PRNG used for all randomness, an End Turn that resolves systems in a fixed order |
| 2 | Map | 8x8 grid, terrain derived from the seed, buildable tiles with terrain requirements, adjacency bonuses that actually modify output |
| 3 | Economy | Multi-step production chains (input consumed to make output), storage caps enforced, overflow handled |
| 4 | Population | Individual colonists as records with skill, fatigue, job assignment; skill and fatigue affect output |
| 5 | Needs | Per-turn consumption, shortage drives morale, morale drives output, state is recoverable rather than instant-loss |
| 6 | Research | 8 or more nodes, prerequisites enforced, costs deducted, unlocks apply a real effect |
| 7 | Events | 10 or more events, weighted selection, 4 or more with 2-3 choices whose outcomes differ in state, cooldown tracking |
| 8 | Trade | Prices computed from stockpiles and/or drifting supply, limited caravan inventory, buy and sell both work |
| 9 | Hazard | Periodic storms, severity scaling with turn, building damage that reduces output, mitigation and repair paths |
| 10 | Save/load | Full state serialized to text, import parses and validates, bad input produces a clear error |
| 11 | End conditions | Win and lose both reachable, score computed from multiple state terms, summary screen rendered |
| 12 | UI | Tabs, event log with turn numbers, tooltips that explain where numbers come from, keyboard shortcuts, responsive layout |
| 13 | Dev panel | Self-tests asserting real invariants (not `1 === 1`), plus a headless N-turn benchmark producing a state hash |

## Category G - Interaction depth (20 pts, 4 per trace)

This is the differentiator. Trace each chain through the actual code.

- **G1** - a research unlock measurably changes a production yield
- **G2** - production shortfall -> unmet need -> morale drop -> reduced labor output
- **G3** - ashstorm -> building damage -> output loss -> repair cost -> recovery
- **G4** - trade prices respond to player stockpiles and/or drifting global supply
- **G5** - event choices durably mutate state rather than printing flavor text

Score each 0-4:

- **0** - the link does not exist in code.
- **1** - cosmetic: logged or displayed, but never applied to state.
- **2** - applied, but through a single hardcoded constant or a special case.
- **3** - applied through the real pipeline, with a minor gap or an unused branch.
- **4** - fully wired, applied every turn, visible to the player, traceable end to end.

## Output format

Reply with ONE JSON object and nothing else. No preamble, no markdown fences, no commentary.

```
{
  "F": {"1":0,"2":0,"3":0,"4":0,"5":0,"6":0,"7":0,"8":0,"9":0,"10":0,"11":0,"12":0,"13":0},
  "G": {"G1":0,"G2":0,"G3":0,"G4":0,"G5":0},
  "evidence": {
    "F1": "one line naming the function or identifier that justifies the score",
    "G1": "one line tracing the chain, e.g. research.yieldBonus read in tickProduction"
  },
  "todo_notes": ["systems left explicitly marked TODO"],
  "grader_confidence": "high | medium | low",
  "single_biggest_weakness": "one sentence"
}
```

Include an `evidence` entry for every F and G key you scored above 0.

=====================================================================

## Optional: run it as a Claude Code command

Save as `.claude/commands/grade-ashfall.md` in your eval repo:

```markdown
---
description: Grade an Ashfall Outpost candidate on rubric categories F and G
---

Read GRADER_PROMPT.md and follow the instructions between the ===== lines exactly.
The candidate file is $ARGUMENTS. Read it, plus its .eval.json sibling if one exists.
Write your JSON reply to the sibling path <candidate>.ai.json and write nothing else to it.
Then run: python3 eval_ashfall.py $ARGUMENTS --runtime --merge <candidate>.ai.json
```

Then: `/grade-ashfall runs/model-x-high.html`
