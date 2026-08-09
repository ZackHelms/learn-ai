Build a complete, playable web game called ASHFALL OUTPOST.

OUTPUT FORMAT (strict)
- Exactly one self-contained HTML file. All CSS and JS inline.
- No external resources: no CDN, no fonts, no images, no network calls, no npm, no build step.
- Do NOT use localStorage, sessionStorage, IndexedDB, or cookies. Keep all state in memory.
- Must run by opening the file directly in a browser.
- Do not ask me clarifying questions. Make reasonable assumptions and list them in a comment block at the top of the file.
- Output the entire file in one code block. No commentary outside it.

PREMISE
A volcanic eruption has buried the region in ash. The player manages a survivor outpost
across turns, balancing production, people, research, trade, and periodic ashstorms.

IMPLEMENT IN THIS PRIORITY ORDER. If you run out of room, stop at a clean boundary and
mark unimplemented systems with // TODO comments. Do not silently skip.

1. CORE LOOP. Single game-state object. Seeded PRNG (mulberry32 or similar), default seed
   1337, seed editable by the player. "End Turn" advances one turn and resolves all systems
   in a fixed documented order. No use of Math.random anywhere.

2. MAP. 8x8 grid, terrain generated from the seed: ash flats, rock, water, vent, ruins.
   Click a tile to build. Buildings have terrain requirements and adjacency bonuses
   (e.g. condenser next to water, forge next to vent). Show the bonus in the tooltip.

3. ECONOMY. Resources: food, water, metal, power, parts, scrip. Production chains, not flat
   income: ore -> metal at the forge (consumes power), ash -> soil -> food at the greenhouse
   (consumes water). Storage caps; overflow is lost and logged.

4. POPULATION. Individual colonists with name, skill level (1-5) in one of 4 jobs, fatigue,
   and morale. Player assigns colonists to buildings. Output scales with skill; skill grows
   slowly with use. Fatigue rises when assigned, falls when resting.

5. NEEDS. Each turn colonists consume food and water. Shortages drive morale down.
   Low morale reduces output, and at zero a colonist leaves or refuses to work.
   Consequences must be visible and recoverable, not instant loss.

6. RESEARCH. At least 8 nodes in a tree with prerequisites and scrip/parts costs. Nodes
   unlock buildings, improve chain yields, or reduce storm damage. Show locked/available/done.

7. EVENTS. Weighted event deck fired on some turns. At least 10 events, at least 4 offering
   the player a choice of 2-3 responses with genuinely different tradeoffs. Recently fired
   events go on cooldown. Outcomes must alter state, not just print text.

8. TRADE. A caravan arrives periodically. Prices move with your stockpiles and with global
   supply/demand that drifts over time. Buy/sell for scrip. Caravan inventory is limited.

9. HAZARD. Ashstorms every N turns, severity scaling with turn count. Damages buildings
   (reduced or disabled output until repaired) and spikes water consumption. Mitigation
   buildings and research reduce damage. Repairs cost parts and labor.

10. SAVE/LOAD. Serialize full state to a JSON string into a textarea the player can copy out,
    and load from pasted text with validation and a clear error on bad input. No browser storage.

11. END CONDITIONS. Win at turn 60 with population >= 12 and all critical needs met.
    Lose if population hits 0. Final score from population, research completed, stockpiles,
    and turns survived. Show a scored summary screen.

12. UI. Tabbed panels (Map, People, Research, Trade, Log). Scrolling event log with turn
    numbers. Hover/tap tooltips explaining every number, including where a modifier came from.
    Keyboard: Space ends turn, 1-5 switch tabs. Must be usable at 360px wide and at desktop
    width. Do not rely on color alone to convey state.

13. VERIFICATION. Add a "Dev" panel with two buttons:
    - "Run Tests": at least 15 assertions over real invariants (no negative resources, storage
      caps respected, colonist count matches roster, research prereqs enforced, save/load
      round-trips to an identical state hash). Print pass/fail per assertion.
    - "Run Benchmark": headless simulation of 200 turns from the current seed using a fixed
      built-in greedy policy, then print a hash of final state plus summary stats. Running it
      twice from the same seed must print the identical hash.

QUALITY BARS
- Systems must interact. A research unlock must measurably change production, which must
  measurably change morale and labor output.
- No dead UI: every button does something.
- No placeholder or lorem text.
- The game must be winnable and losable. Difficulty should not be trivial.
