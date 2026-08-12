# Repair Ashfall Outpost (eval03, defect set v1)

Below this brief is the complete source of a single-file browser game that
shipped with several bugs. Five player bug reports are open. Your job: find
and fix all five with the **smallest possible change**. Do not restructure,
reformat, or rewrite working code - a hidden regression suite runs against
your patched file, and collateral damage costs you.

## Bug reports

1. **Adjacency feels wrong.** Players report tiles that are visibly next to
   water or a vent sometimes getting no adjacency bonus at all, while
   identical-looking placements elsewhere on the map work fine. Windbreak
   protection seems patchy in the same way.
2. **Experienced workers are overpowered.** Colonies snowball once workers
   skill up - late-game production is far beyond what the tooltips imply.
3. **Phantom shortages.** Some turns the log reports a food shortage even
   though that same turn's production visibly covered the need.
4. **Save/load is broken.** Exporting a game and immediately importing the
   very same text gets rejected.
5. **Departure timing is off.** Zero-morale colonists hang around longer
   than the warning message says they will.

## Output format

Reply with edit blocks ONLY - no commentary, no full file. Either format
works (you may mix them); edits are applied by exact, unique content match:

    <<<<<<< SEARCH
    exact lines as they appear in the file
    =======
    replacement lines
    >>>>>>> REPLACE

or unified-diff hunks (`@@`, `-`/`+`/context lines; line numbers in the `@@`
header are ignored, content must match exactly).

Scoring rewards fixes that pass the hidden tests, keeps regression guards
intact, and is proportional to how little you touch: the intended fix
changes about 10 lines. Submissions touching more than ~64 lines get no
minimality credit.

===== ashfall-defective-v1.html follows =====
