You are grading one submission in a code eval. A different AI model was given a single prompt
asking it to build ASHFALL OUTPOST - a turn-based colony-survival game - as one self-contained
HTML file, in one shot, with no follow-up turns. The candidate's HTML file is provided after
this prompt: pasted below it, attached, or at a file path you can read.

You will score 18 items by reading the code:

- F1-F13: thirteen game systems, each scored 0, 1, or 2 (26 points)
- G1-G5: five cross-system interaction chains, each scored 0 to 4 (20 points)

## Rules

1. Do NOT run the code. Judge only by reading it.
2. Do NOT fix, improve, or rewrite anything. Do not comment on style.
3. Do NOT score anything except the 18 items below. A separate program already checks whether
   the file loads, whether banned APIs appear, and whether its self-tests pass. Ignore all that.
4. A defect that kills the WHOLE file at once - a JavaScript syntax error, an unclosed
   script tag - is already priced by that separate program. Do NOT let it cascade into your
   scores. Grade each system's source-level wiring as if the file parsed: everywhere these
   rules say "called" or "used", that means a call site or a read EXISTS IN THE SOURCE, not
   that it would execute in a browser. Mention the defect in `single_biggest_weakness`, then
   score past it.
5. Score what the code DOES, not what comments, variable names, or UI text claim. A function
   named `applyStormDamage` with no call site anywhere scores as if it did not exist.
6. A button or control that no code ever wires to a handler is worth nothing.
7. `// TODO` markers earn 0 for that item. List them in `todo_notes` instead.
8. When you are unsure, or you cannot find the wiring, give the LOWER score. A generous grader
   makes every model look the same, which destroys the eval.
9. Every score above 0 needs one line of evidence: a function or variable name plus where it
   is used. Under 15 words. Never paste long blocks of the candidate's code.
10. If the file is truncated, empty, or not really a game, score whatever is actually present
    by its wiring; items whose code is simply missing score 0.
11. Do NOT run `eval_ashfall.py` or any other scoring/test script, and do NOT open, read, or
    otherwise let yourself see any existing `.eval.json`, `.ai.json`, or `RESULTS.md` row for
    this candidate before or during grading. Those carry the deterministic score and prior
    grades; seeing them first anchors your judgment. Grade from the HTML source alone.
12. Do NOT infer, guess, or state which model, harness, or reasoning-effort level produced the
    candidate. Ignore what the filename or file path seems to imply about authorship - grade
    the code, not the label on it.

## Procedure

Work through the 18 items IN ORDER, one at a time. For each item:

1. SEARCH the code for the parts that would implement it.
2. VERIFY the parts are actually used: a call site for the function exists, another piece of
   code reads the value. Code with no call site anywhere in the source counts as absent.
   (Per rule 4: a call site that exists but would never execute because of a file-wide
   defect still counts - that defect is priced elsewhere.)
3. WRITE one worksheet line: the item id, what you found (identifier names, or "not found"),
   and the score.

Only after writing all 18 worksheet lines, output the final JSON (format at the bottom).

Evidence style - follow the good example:

- GOOD: "F3: smeltOre() consumes state.power, adds state.metal, called from endTurn()"
- BAD: "F3: the economy system looks complete and well implemented" (no identifier, no wiring)

## Part 1 of 2 - Category F: systems implemented (F1-F13, score each 0, 1, or 2)

Score meanings:

- 0 = absent, an empty stub, or present but never called or used.
- 1 = present and used, but shallow: missing required parts below, values hardcoded, or its
  output is not read by any other part of the game.
- 2 = ALL required parts below are present, working, and its outputs are consumed elsewhere.

| # | System | Score 2 requires ALL of |
|---|--------|-------------------------|
| F1 | Core loop | one game-state object; a seeded PRNG used for all randomness; an end-turn function that resolves systems in a fixed order |
| F2 | Map | 8x8 grid; terrain derived from the seed; building placement checks terrain type; adjacency bonuses that actually change production numbers |
| F3 | Economy | multi-step production chains (an input is consumed to make an output, e.g. ore -> metal, ash -> soil -> food); storage caps enforced; overflow handled |
| F4 | Population | colonists are individual records with skill, fatigue, morale, job assignment; skill and fatigue values are read by the production code |
| F5 | Needs | per-turn food/water consumption; shortage lowers morale; morale changes output; recovery is possible (not instant loss) |
| F6 | Research | 8 or more nodes; prerequisites enforced before purchase; costs deducted; each unlock applies a real effect somewhere |
| F7 | Events | 10 or more events; weighted random selection; 4 or more events offer 2-3 choices whose outcomes change state differently; recently fired events go on cooldown |
| F8 | Trade | prices computed from player stockpiles and/or a drifting supply variable; caravan inventory is limited; both buy and sell work |
| F9 | Hazard | storms fire periodically; severity grows with turn count; damaged buildings produce less until repaired; some research or building reduces damage; repair costs resources |
| F10 | Save/load | full state serialized to text the player can copy; import parses pasted text, validates it, and shows a clear error on bad input |
| F11 | End conditions | win check and lose check both exist and both are reachable; final score computed from several state values; a summary screen is rendered |
| F12 | UI | tab switching works; event log lines carry turn numbers; tooltips explain where numbers come from; keyboard shortcuts exist; layout adapts to narrow screens |
| F13 | Dev panel | self-tests assert real game invariants (not trivialities like `1 === 1`); a headless multi-turn benchmark runs the game loop without the UI and prints a state hash |

How to check "outputs are consumed elsewhere": find the value the system writes (a state
field, a modifier, a flag), then search for a DIFFERENT function that reads it. If nothing
else reads it, the system is disconnected: score at most 1.

## Part 2 of 2 - Category G: interaction depth (G1-G5, score each 0 to 4)

This is the differentiator. Weak submissions build 13 parallel systems that never touch each
other. Trace each chain link by link through the actual code.

Score meanings:

- 0 = the link does not exist in code.
- 1 = cosmetic: the effect is logged or displayed, but game state is never changed.
- 2 = applied, but through a single hardcoded constant or special case.
- 3 = applied through the real production/consumption pipeline, with a minor gap or an
  unused branch.
- 4 = fully wired: applied every turn it is relevant, visible to the player, and every link
  in the chain is traceable in code.

| # | Chain to trace | How to trace it |
|---|----------------|-----------------|
| G1 | research unlock -> production yield changes | find where a completed research node stores its effect; find the production formula; confirm the formula reads that effect |
| G2 | production shortfall -> unmet need -> morale drop -> reduced labor output | find the consumption step; confirm shortage writes to morale; confirm morale is a factor in the output formula |
| G3 | ashstorm -> building damage -> output loss -> repair cost -> recovery | find the storm function; confirm it flags/damages buildings; confirm damaged buildings produce less; confirm repair spends resources and restores output |
| G4 | trade prices respond to stockpiles and/or drifting global supply | find the price formula; confirm it reads the player's resource amounts or a supply variable that changes over turns |
| G5 | event choices durably mutate state | pick 2 events that offer choices; confirm each choice branch writes different changes into game state, not just into the log |

A chain is only as strong as its weakest link. If storms damage buildings but damaged
buildings produce at full rate, G3 is at most 1.

## Output format

First your 18 worksheet lines. Then, as the LAST thing in your reply, one JSON object inside
a fenced code block. Fill in every value; integers only.

```json
{
  "F": {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0, "7": 0,
        "8": 0, "9": 0, "10": 0, "11": 0, "12": 0, "13": 0},
  "G": {"G1": 0, "G2": 0, "G3": 0, "G4": 0, "G5": 0},
  "evidence": {
    "F1": "one line: identifier that justifies the score, and where it is used",
    "G1": "one line tracing the chain, e.g. research.yieldBonus read in tickProduction()"
  },
  "todo_notes": ["systems the candidate explicitly marked TODO"],
  "grader_confidence": "high | medium | low",
  "single_biggest_weakness": "one sentence"
}
```

Before sending, check:

- All 13 F keys ("1" through "13") and all 5 G keys ("G1" through "G5") are present.
- F values are only 0, 1, or 2. G values are only 0, 1, 2, 3, or 4.
- There is an `evidence` entry for every item scored above 0.
- The JSON code block is the last thing in your reply.

## If you are grading agentically (file access, not paste-in-chat)

Name output files generically from the candidate's own filename - never from a guessed model
name, harness, or run id. Take the candidate's filename, strip its extension, and use that stem:

- candidate `ashfalloutpost.html` -> reply saved as `ashfalloutpost.ai.json`
- candidate `runs/haiku-4-5-low-001.html` -> reply saved as `runs/haiku-4-5-low-001.ai.json`

Save your full reply (worksheet + trailing JSON block, verbatim) next to the candidate file
using that name. Do not invent a different stem, do not rename or move the candidate, and do
not create `<stem>.eval.json` yourself - that merged deterministic+model-graded file is
produced by `eval_ashfall.py --merge`, run by the human after your reply, not by you (see rule
11 - you do not run that script).
