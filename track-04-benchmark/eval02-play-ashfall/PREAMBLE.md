# You are playing ASHFALL OUTPOST (eval02 contract v1)

You manage a survivor outpost for 60 turns. Each turn you receive the current
game state as JSON and reply with a JSON object of actions. **You will not see
earlier turns.** Your only memory is the `note` field you write each turn: it
is stored verbatim (up to 600 characters) and handed back to you next turn.
Use it for your plan, your build order, and anything you must not forget.

## Goal and scoring

- **Win**: reach turn 60 with population >= 12 and no food or water shortage
  on the final turn.
- **Lose**: population hits 0 at any time (the run ends immediately).
- **Score** (what you are graded on): population x25 + research completed x40
  + stockpile value / 5 + turns survived x2 + 250 if you win.

## How a turn resolves (after your actions, in this order)

storm check -> production -> colonists eat 1 food + drink 1 water each
(x1.5 water during a storm) -> morale/fatigue -> possible settler arrival ->
caravan arrival/departure -> possible event. Shortages cost everyone 12
morale each; overcrowding costs 5. A colonist at 0 morale refuses to work,
and leaves if still at 0 the next turn. Ashstorms hit every 7 turns and
damage buildings (no output until repaired).

## Buildings

| type | terrain | cost | worker | effect |
|---|---|---|---|---|
| shelter | ash/rock/ruins | 6 metal | - | houses 4 (5 on ruins); base camp houses 6 |
| condenser | ash/rock/ruins | 5 metal 1 parts | Farmer | +4 water; +30%/adjacent water tile |
| sifter | ash | 4 metal | Farmer | +3 soil; +10%/adjacent ash |
| greenhouse | ash | 6 metal 1 parts | Farmer | 2 soil + 3 water -> 5 food; +20%/adj water |
| mine | rock | 6 metal | Miner | +3 ore |
| forge | ash/rock | 8 metal 2 parts | Miner | 3 ore + 2 power -> 2 metal; +25%/adj vent |
| geo | vent | 10 metal 2 parts | Miner | +6 power |
| workshop | ash/rock/ruins | 8 metal 1 parts | Tinker | 2 metal + 2 power -> 1 parts |
| scav | ruins | 4 metal | Scout | +4 scrip, 20% chance +1 parts |
| windbreak | ash/rock/ruins | 4 metal | - | halves storm damage odds here + adjacent |
| cistern | ash/rock/ruins | 5 metal | - | +40 water storage |
| depot | ash/rock/ruins | 5 metal | - | +25 food, +20 metal/ore/soil, +10 parts storage |
| clinic | ash/rock/ruins | 8 metal 3 parts | Tinker | needs research; faster rest, +2 morale/turn |
| bazaar | ash/rock/ruins | 8 metal 2 parts | Scout | needs research; +2 scrip, 10% better prices |

Base storage caps: food 60, water 60, metal 40, ore 40, soil 40, parts 24,
power 20, scrip unlimited. Overflow is lost. A worker whose job matches the
building produces x(0.7 + 0.15 x skill) and gains skill; a mismatched worker
produces x0.75 and learns nothing. Fatigue >= 80 halves output; morale < 40
reduces it. Sick or 0-morale colonists produce nothing.

## Research (scrip + parts, instant)

agronomy (40s 2p): greenhouse +30% | irrigation (50s 3p, needs agronomy):
greenhouses use half water | refining (45s 2p): forge +30% | turbines (55s
3p, needs refining): geo +40% | shutters (35s 2p): storm damage -30% |
frames (60s 4p, needs shutters): -30% more, repairs cost 1 part |
clinic (50s 3p): unlocks Clinic | bazaar (40s 2p): unlocks Bazaar |
deepstore (45s 2p): storage caps +50% | guild (70s 3p, needs bazaar):
caravans 50% bigger, sell +15%

## Trade and events

A caravan visits every ~6 turns for 2 turns. Prices move with world demand
and your stockpile (abundant = cheap). Some turns end with an event; if it
offers choices, the state's `pending_event` lists them, and your FIRST action
next turn should be a `choose`. If you do not choose, the last option is
applied automatically.

## The map

`terrain_rows` is 8 strings (rows 1-8), each 8 characters (columns A-H):
`a` ash flat, `r` rock, `w` water (unbuildable), `v` vent, `u` ruins.
Tiles are named like `C4` (column C, row 4). Adjacency = the 8 surrounding
tiles.

## Actions (apply in the order you list them, max 16 per turn)

```json
{"actions": [
  {"do":"choose",   "choice": 0},
  {"do":"build",    "at":"C4", "type":"condenser"},
  {"do":"assign",   "who":"c3", "at":"C4"},
  {"do":"unassign", "who":"c3"},
  {"do":"repair",   "at":"B2"},
  {"do":"demolish", "at":"B2"},
  {"do":"research", "id":"agronomy"},
  {"do":"buy",      "good":"food", "qty":5},
  {"do":"sell",     "good":"ore",  "qty":10}
 ],
 "note": "Plan: condenser C4 done. Next: sifter then greenhouse. Storm t7."}
```

An action that fails (bad tile, cannot afford, occupied...) is skipped and
its error is shown to you next turn under `errors`. An empty actions list is
legal: production, needs and events still run when the turn ends.

Reply with ONLY that JSON object. No prose, no code fences.
