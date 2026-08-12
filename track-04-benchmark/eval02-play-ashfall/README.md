# eval02 - play Ashfall

The model is the *player*, not the builder. It manages the frozen Ashfall
Outpost reference build (`../reference/ashfall-reference-v1.html`,
sha256-pinned - the driver refuses a drifted file) for 60 turns through a
JSON state/action contract. No judge; the score is the game's own formula.

**What it measures:** long-horizon coherence - keeping a plan alive across
60 decisions - as a separate axis from single-step reasoning.
[Vending-Bench 2](https://andonlabs.com/evals/vending-bench-2) (Andon Labs;
original paper [arXiv:2502.15840](https://arxiv.org/abs/2502.15840)) showed
frontier agents fail long runs through looping, identity drift, and repeated
bad decisions rather than any single wrong step; this is the small, cheap,
fully deterministic-environment version.

**The memory design is the point.** The model never sees earlier turns. Its
only memory is a `note` field (up to 600 chars) it must write every turn,
which the driver hands back next turn. Keeping the plan coherent through that
bottleneck IS the long-horizon test - and it keeps every turn's prompt small
enough that a 4k-context local model can play the same protocol as a frontier
model.

## Contract v1

`PREAMBLE.md` (frozen) is the rules text every agent receives every turn,
followed by errors from its previous actions, its own note, and the state
JSON. Reply: `{"actions":[...], "note":"..."}`, max 16 actions, applied in
order through the game's own engine functions (`buildAt`, `assign`,
`tradeBuy`...). Failed actions are skipped and reported back next turn.
An unresolved choice event auto-resolves to its last option (and tells the
model it did). Changing PREAMBLE.md, the state encoding, or these rules is
contract v2 and a new results table.

## Run it

```bash
./run.sh -b naive n1                # free deterministic baseline
./run.sh -m sonnet5 -e medium s2    # one claude -p call per turn, costs summed
./run.sh -m haiku45 -e low r1b -s 4242   # non-default seed: record it
uv run driver.py --agent cmd:'ollama run <tag>' --seed 1337 --id local1   # untested here
```

Seed **1337 is the frozen comparison seed**. Runs on other seeds are fine
science (the map changes) but go in RESULTS with their seed called out.

## Scoring and what "good" looks like

Final score = the game's own end screen: pop x25 + research x40 + stockpile
value / 5 + turns survived x2 + 250 on a win (turn 60 with pop >= 12, needs
met). The driver adds nothing.

Measured anchors on seed 1337 (2026-08-12, all deterministic - reproduce
with `-b`):

| agent | outcome | score |
|---|---|---|
| builtin:idle | starves, pop 0 at turn 10 | 64 |
| builtin:naive (contract-level scripted) | pop 0 at turn 13 | 92 |
| builtin:greedy (the game's own benchmark policy) | pop 0 at turn 20 | 52 |

Yes: **the game's own greedy policy dies on seed 1337.** Six colonists
cannot man the full production chain; early famine is the designed crisis,
and the score formula pays corpses more for hoarded stock and research than
for a few extra turns of survival. Whether seed 1337 is winnable at all is
an open question - nothing has survived to turn 60 here yet. That makes the
eval unsaturated in both directions: beating greedy's 20 turns shows real
play; a checked win would be a headline. A weak model still produces a
number - it just starves faster (the idle floor is exactly that).

Determinism: the environment is fully deterministic (seeded PRNG lives in
game state; player actions consume no randomness) - verified by identical
state hashes on repeated naive and greedy runs. The *model* is still
sampled, so replicate before trusting small gaps.

## Files per run

`runs/<id>.eval.json` (outcome, config, API costs, state hash) and
`runs/<id>.turns.jsonl` (per-turn actions, errors, note - read this to see
*how* a run died: looping, forgetting the plan, ignoring errors).

## Verified

Built 2026-08-12 on Ubuntu 24.04 (WSL2): idle/naive/greedy baselines run;
naive and greedy repeated with identical hashes (`dc133b09`, `2a3ddb5b`);
claude path smoke-tested with haiku-4-5 low (see RESULTS). The ollama
command form has not been run on this machine.
