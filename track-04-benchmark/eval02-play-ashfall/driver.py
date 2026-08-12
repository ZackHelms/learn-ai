#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["playwright"]
# ///
# PEP 723: `uv run driver.py ...` resolves playwright; plain python3 works when
# playwright is already installed (eval01's runtime pass uses the same setup).
"""
driver.py - eval02 "Play Ashfall" environment driver (contract v1).

Loads the frozen reference build (reference/ashfall-reference-v1.html,
sha256-pinned - the driver refuses to run against a drifted file) in headless
Chromium, starts a game from --seed, and plays up to 60 turns. Each turn it
extracts a compact state JSON, hands it to the agent, applies the agent's
action list through the game's own engine functions, then ends the turn.
The final outcome is the game's own score formula; the driver adds nothing.

Agents (--agent):
  builtin:idle     no actions, ever. The floor.
  builtin:naive    deterministic scripted player using ONLY the v1 contract
                   (what the model sees is what it uses).
  builtin:greedy   the game's own built-in benchmark policy (policyStep),
                   driven at engine level - NOT through the contract. The
                   in-game reference policy as a ceiling-ish anchor.
  claude:MODEL:EFFORT   one bare `claude -p` call per turn (tools disabled,
                   empty cwd, --output-format json; costs summed).
  cmd:SHELL_CMD    any command: full prompt on stdin, reply text on stdout.

Determinism: the environment is deterministic (seeded PRNG in game state;
player actions consume no randomness), so identical action sequences give
identical outcomes - verified by running builtin agents twice. Model agents
are still sampled; replicate before trusting gaps.

Outputs: runs/<id>.eval.json (outcome, config, costs) and
runs/<id>.turns.jsonl (per-turn transcript: state, reply, errors).
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, "..", "reference", "ashfall-reference-v1.html")
REF_SHA = "2f7425cceb693f3389f5feaa15f835009df2798ee7780454ef8d46c59340f693"
CONTRACT = "v1"
MAX_ACTIONS = 16
NOTE_MAX = 600
TURNS = 60

STATE_JS = r"""
(() => {
  const tn = i => String.fromCharCode(65 + (i % 8)) + (Math.floor(i / 8) + 1);
  const cap = capsOf(G);
  const terr = [];
  const code = {ash:'a', rock:'r', water:'w', vent:'v', ruins:'u'};
  for (let y = 0; y < 8; y++) {
    let row = '';
    for (let x = 0; x < 8; x++) row += code[G.map[y*8+x].t];
    terr.push(row);
  }
  const blds = [];
  for (let i = 0; i < 64; i++) {
    const b = G.map[i].b; if (!b) continue;
    const w = G.colonists.find(c => c.assign === i);
    blds.push({at: tn(i), type: b.type, dmg: !!b.dmg, worker: w ? w.id : null});
  }
  const res = {};
  for (const k of RESKEYS)
    res[k] = [Math.round(G.res[k]*10)/10, cap[k] === Infinity ? null : Math.round(cap[k])];
  let pend = null;
  if (G.pending) {
    const ev = eventById(G.pending.id);
    let text = ev.text || '';
    if (ev.pickCol && G.pending.cid) {
      const c = colById(G, G.pending.cid);
      text = text.replace('@', c ? c.name : 'a colonist');
    }
    pend = {name: ev.name, text: text, about: G.pending.cid,
            choices: ev.choices.map((ch, i) => ({i: i, label: ch.label, ok: !ch.can || ch.can(G)}))};
  }
  const car = G.caravan
    ? (() => { const o = {leaves_after_turn: G.caravan.leaves - 1, stock: {}, buy: {}, sell: {}};
        for (const g of TRADEGOODS) { o.stock[g] = G.caravan.stock[g];
          const p = priceOf(G, g); o.buy[g] = p.buy; o.sell[g] = p.sell; } return o; })()
    : {next_arrival_turn: G.nextCaravan};
  return {
    turn: G.turn, res: res, pop: popOf(G), housing: housingOf(G),
    shortage: Object.keys(G.shortage).filter(k => G.shortage[k]),
    storm: {active: G.stormActive, next_at_turn: G.nextStorm},
    vent_surge: G.ventSurge, caravan: car,
    colonists: G.colonists.map(c => ({id: c.id, job: c.job, skill: c.skill,
      fatigue: Math.round(c.fatigue), morale: Math.round(c.morale),
      sick: c.sick, at: c.assign === null ? null : tn(c.assign)})),
    map: {terrain_rows: terr, buildings: blds},
    research_done: Object.keys(G.research),
    pending_event: pend,
    log_tail: G.log.slice(-8).map(e => 'T' + e.t + ' ' + e.m),
    over: G.over ? {win: G.over.win, score: G.over.score, reason: G.over.reason} : null
  };
})()
"""

FINAL_JS = r"""
(() => ({
  over: G.over, hash: hashState(G), turn: G.turn, pop: popOf(G),
  research: Object.keys(G.research).length,
  buildings: G.map.filter(t => t.b).length
}))()
"""


def tile_index(ref):
    m = re.fullmatch(r"([A-Ha-h])([1-8])", str(ref).strip())
    if not m:
        return None
    return (int(m.group(2)) - 1) * 8 + (ord(m.group(1).upper()) - 65)


def apply_action(page, a):
    """Apply one action dict via the game's engine; return error string or None."""
    if not isinstance(a, dict) or "do" not in a:
        return "malformed action %r" % (a,)
    do = a.get("do")
    if do == "choose":
        idx = a.get("choice")
        if not isinstance(idx, int):
            return "choose needs integer 'choice'"
        return page.evaluate(
            "(idx) => { if (!G.pending) return 'No event is pending.';"
            " const ev = eventById(G.pending.id); const ch = ev.choices[idx];"
            " const bad = !ch || (ch.can && !ch.can(G)); applyChoice(G, idx);"
            " return bad ? ('choice ' + idx + ' unavailable; first affordable option applied instead') : null; }",
            idx)
    if do in ("build", "repair", "demolish"):
        i = tile_index(a.get("at", ""))
        if i is None:
            return "%s: bad tile %r (use like C4)" % (do, a.get("at"))
        if do == "build":
            t = a.get("type")
            return page.evaluate("([i,t]) => buildAt(G, i, t)", [i, str(t)])
        fn = "repairAt" if do == "repair" else "demolishAt"
        return page.evaluate("(i) => %s(G, i)" % fn, i)
    if do == "assign":
        i = tile_index(a.get("at", ""))
        if i is None:
            return "assign: bad tile %r" % (a.get("at"),)
        return page.evaluate("([c,i]) => assign(G, c, i)", [str(a.get("who")), i])
    if do == "unassign":
        return page.evaluate("(c) => assign(G, c, null)", str(a.get("who")))
    if do == "research":
        return page.evaluate("(id) => buyResearch(G, id)", str(a.get("id")))
    if do in ("buy", "sell"):
        g, q = a.get("good"), a.get("qty")
        if not isinstance(q, (int, float)) or q <= 0:
            return "%s needs positive 'qty'" % do
        fn = "tradeBuy" if do == "buy" else "tradeSell"
        return page.evaluate("([g,q]) => %s(G, g, Math.floor(q))" % fn, [str(g), q])
    return "unknown action %r" % do


def extract_json(text):
    """Pull the first balanced {...} out of a model reply; tolerate fences."""
    text = text.strip()
    fence = re.match(r"^```[a-zA-Z]*\n(.*)\n```$", text, re.S)
    if fence:
        text = fence.group(1).strip()
    start = text.find("{")
    if start < 0:
        raise ValueError("no JSON object in reply")
    depth, in_str, esc = 0, False, False
    for i in range(start, len(text)):
        ch = text[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
        elif ch == '"':
            in_str = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return json.loads(text[start:i+1])
    raise ValueError("unbalanced JSON object in reply")


def build_prompt(preamble, state, note, errors):
    lines = [preamble, "", "## Now planning turn %d of %d" % (state["turn"] + 1, TURNS), ""]
    lines.append("### Errors from your previous actions")
    lines.extend("- " + e for e in errors) if errors else lines.append("(none)")
    lines += ["", "### Your note from last turn",
              note if note else "(empty - this is your first turn)",
              "", "### Current state", "```json",
              json.dumps(state, separators=(",", ":")), "```", "",
              'Reply with ONLY the JSON object: {"actions":[...], "note":"..."}']
    return "\n".join(lines)


# ---------------------------------------------------------------- agents
class ClaudeAgent:
    def __init__(self, model, effort):
        self.model, self.effort = model, effort
        self.calls = 0
        self.cost = 0.0
        self.in_tok = self.out_tok = 0

    def __call__(self, prompt):
        last = None
        for attempt in range(2):
            job = tempfile.mkdtemp(prefix="eval02-")
            try:
                p = subprocess.run(
                    ["claude", "-p", "--model", self.model, "--effort", self.effort,
                     "--tools", "", "--permission-mode", "dontAsk",
                     "--no-session-persistence", "--output-format", "json"],
                    input=prompt, capture_output=True, text=True, cwd=job, timeout=900)
            finally:
                try:
                    os.rmdir(job)
                except OSError:
                    pass
            try:
                env = json.loads(p.stdout)
            except ValueError:
                env = None
            if p.returncode == 0 and env and env.get("type") == "result" \
                    and not env.get("is_error") and env.get("result"):
                self.calls += 1
                self.cost += env.get("total_cost_usd") or 0
                u = env.get("usage") or {}
                self.in_tok += (u.get("input_tokens") or 0) + \
                    (u.get("cache_read_input_tokens") or 0) + \
                    (u.get("cache_creation_input_tokens") or 0)
                self.out_tok += u.get("output_tokens") or 0
                return env["result"]
            last = "claude rc=%d stderr=%s" % (p.returncode, p.stderr.strip()[-200:])
            print("  [agent] attempt %d failed: %s" % (attempt + 1, last), file=sys.stderr)
            time.sleep(15)
        raise RuntimeError("claude agent failed twice: %s" % last)


class CmdAgent:
    def __init__(self, cmd):
        self.cmd = cmd
        self.calls = 0
        self.cost = 0.0
        self.in_tok = self.out_tok = 0

    def __call__(self, prompt):
        for attempt in range(2):
            p = subprocess.run(self.cmd, shell=True, input=prompt,
                               capture_output=True, text=True, timeout=900)
            if p.returncode == 0 and p.stdout.strip():
                self.calls += 1
                return p.stdout
            print("  [agent] cmd attempt %d failed rc=%d" % (attempt + 1, p.returncode),
                  file=sys.stderr)
        raise RuntimeError("cmd agent failed twice")


BLD_NEEDS = {"condenser": "Farmer", "sifter": "Farmer", "greenhouse": "Farmer",
             "mine": "Miner", "forge": "Miner", "geo": "Miner",
             "workshop": "Tinker", "clinic": "Tinker", "scav": "Scout", "bazaar": "Scout"}
BLD_COST = {"shelter": {"metal": 6}, "condenser": {"metal": 5, "parts": 1},
            "sifter": {"metal": 4}, "greenhouse": {"metal": 6, "parts": 1},
            "mine": {"metal": 6}, "geo": {"metal": 10, "parts": 2},
            "workshop": {"metal": 8, "parts": 1}, "scav": {"metal": 4},
            "windbreak": {"metal": 4}, "cistern": {"metal": 5}, "depot": {"metal": 5}}
BLD_TERR = {"shelter": "aru", "condenser": "aru", "sifter": "a", "greenhouse": "a",
            "mine": "r", "geo": "v", "workshop": "aru", "scav": "u",
            "windbreak": "aru", "cistern": "aru", "depot": "aru"}


def naive_agent(state, note):
    """Deterministic contract-level player: modest build order, matched
    assignments, two researches, basic caravan hygiene. No randomness."""
    acts = []
    res = {k: v[0] for k, v in state["res"].items()}
    pend = state["pending_event"]
    if pend:
        ok = [c["i"] for c in pend["choices"] if c["ok"]]
        acts.append({"do": "choose", "choice": ok[0] if ok else pend["choices"][-1]["i"]})

    blds = state["map"]["buildings"]
    occupied = {b["at"] for b in blds}
    have = {}
    for b in blds:
        have[b["type"]] = have.get(b["type"], 0) + 1

    def first_tile(terrs):
        rows = state["map"]["terrain_rows"]
        for r in range(8):
            for c in range(8):
                at = "%s%d" % (chr(65 + c), r + 1)
                if rows[r][c] in terrs and at not in occupied:
                    return at
        return None

    for b in blds:
        if b["dmg"] and res.get("parts", 0) >= 3:
            acts.append({"do": "repair", "at": b["at"]})
            res["parts"] -= 2
            break

    wish = []
    if have.get("condenser", 0) < 1: wish.append("condenser")
    if have.get("sifter", 0) < 1: wish.append("sifter")
    if have.get("greenhouse", 0) < 1: wish.append("greenhouse")
    if state["pop"] + 1 > state["housing"]: wish.append("shelter")
    if have.get("geo", 0) < 1: wish.append("geo")
    if have.get("mine", 0) < 1: wish.append("mine")
    if have.get("greenhouse", 0) < (state["pop"] + 4) // 5: wish.append("greenhouse")
    if have.get("condenser", 0) < (state["pop"] + 4) // 5: wish.append("condenser")
    if have.get("scav", 0) < 1: wish.append("scav")
    if state["turn"] > 10 and have.get("windbreak", 0) < 2: wish.append("windbreak")
    built = 0
    for t in wish:
        if built >= 2:
            break
        cost = BLD_COST[t]
        if any(res.get(k, 0) < v for k, v in cost.items()):
            continue
        at = first_tile(BLD_TERR[t])
        if at is None:
            continue
        acts.append({"do": "build", "at": at, "type": t})
        occupied.add(at)
        for k, v in cost.items():
            res[k] -= v
        if t in BLD_NEEDS:
            blds.append({"at": at, "type": t, "dmg": False, "worker": None})
        built += 1

    for rid, scost, pcost in (("agronomy", 40, 2), ("shutters", 35, 2)):
        if rid not in state["research_done"] and res.get("scrip", 0) >= scost + 25 \
                and res.get("parts", 0) >= pcost + 2:
            acts.append({"do": "research", "id": rid})
            res["scrip"] -= scost
            res["parts"] -= pcost
            break

    free = [c for c in state["colonists"]
            if c["at"] is None and c["sick"] == 0 and c["morale"] > 0 and c["fatigue"] < 70]
    for b in blds:
        need = BLD_NEEDS.get(b["type"])
        if not need or b["dmg"] or b.get("worker"):
            continue
        pickc = next((c for c in free if c["job"] == need), None) or (free[0] if free else None)
        if pickc:
            acts.append({"do": "assign", "who": pickc["id"], "at": b["at"]})
            free.remove(pickc)

    if "leaves_after_turn" in state["caravan"]:
        pop = state["pop"]
        if res.get("food", 0) < pop * 2:
            acts.append({"do": "buy", "good": "food", "qty": int(pop * 2 - res["food"]) + 1})
        if res.get("water", 0) < pop * 2:
            acts.append({"do": "buy", "good": "water", "qty": int(pop * 2 - res["water"]) + 1})
        if res.get("ore", 0) > 25:
            acts.append({"do": "sell", "good": "ore", "qty": int(res["ore"] - 20)})

    return {"actions": acts[:MAX_ACTIONS],
            "note": "naive scripted agent - no memory needed"}


# ---------------------------------------------------------------- main loop
def main():
    ap = argparse.ArgumentParser(description="eval02 driver (contract %s)" % CONTRACT)
    ap.add_argument("--agent", required=True,
                    help="builtin:idle|builtin:naive|builtin:greedy|claude:MODEL:EFFORT|cmd:SHELL")
    ap.add_argument("--seed", type=int, default=1337)
    ap.add_argument("--id", required=True, help="run id; outputs land in runs/<id>.*")
    ap.add_argument("--turns", type=int, default=TURNS)
    args = ap.parse_args()

    ref = os.path.realpath(REF)
    sha = hashlib.sha256(open(ref, "rb").read()).hexdigest()
    if sha != REF_SHA:
        sys.exit("reference artifact sha mismatch:\n  have %s\n  want %s\n"
                 "eval02 results are only comparable against the frozen v1 file." % (sha, REF_SHA))

    preamble = open(os.path.join(HERE, "PREAMBLE.md")).read()
    runs = os.path.join(HERE, "runs")
    os.makedirs(runs, exist_ok=True)

    agent_kind = args.agent
    model_agent = None
    if agent_kind.startswith("claude:"):
        _, model, effort = agent_kind.split(":", 2)
        model_agent = ClaudeAgent(model, effort)
    elif agent_kind.startswith("cmd:"):
        model_agent = CmdAgent(agent_kind[4:])
    elif agent_kind not in ("builtin:idle", "builtin:naive", "builtin:greedy"):
        sys.exit("unknown agent %r" % agent_kind)

    from playwright.sync_api import sync_playwright
    t0 = time.time()
    started = time.strftime("%Y-%m-%d_%H:%M:%S_%Z")
    transcript = open(os.path.join(runs, args.id + ".turns.jsonl"), "w")
    actions_total = errors_total = 0
    note = ""
    errors = []

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        page.goto("file://" + ref, timeout=30000)
        page.evaluate("(s) => { G = newGame(s >>> 0); }", args.seed)

        for _ in range(args.turns):
            state = page.evaluate(STATE_JS)
            if state["over"]:
                break

            if agent_kind == "builtin:greedy":
                # Engine-level anchor: resolve any pending event the way the
                # in-page benchmark does, then run its policy. Not contract play.
                page.evaluate("() => { if (G.pending) applyChoice(G, policyChoice(G)); policyStep(G); }")
                reply, errs = {"actions": ["<policyStep>"], "note": ""}, []
            else:
                if agent_kind == "builtin:idle":
                    reply = {"actions": [], "note": ""}
                elif agent_kind == "builtin:naive":
                    reply = naive_agent(state, note)
                else:
                    prompt = build_prompt(preamble, state, note, errors)
                    text = model_agent(prompt)
                    try:
                        reply = extract_json(text)
                    except ValueError as e1:
                        text = model_agent(prompt + "\n\nYour previous reply was not "
                                           "valid JSON (%s). Reply with ONLY the JSON object." % e1)
                        try:
                            reply = extract_json(text)
                        except ValueError as e2:
                            reply = {"actions": [], "note": note,
                                     "_parse_error": str(e2)}
                errs = []
                acts = reply.get("actions", [])
                if not isinstance(acts, list):
                    errs.append("'actions' was not a list")
                    acts = []
                if "_parse_error" in reply:
                    errs.append("reply was not valid JSON (%s); no actions applied"
                                % reply["_parse_error"])
                if len(acts) > MAX_ACTIONS:
                    errs.append("action list truncated to %d" % MAX_ACTIONS)
                    acts = acts[:MAX_ACTIONS]
                for a in acts:
                    err = apply_action(page, a)
                    if err:
                        errs.append("%r -> %s" % (a, err))
                dropped = page.evaluate(
                    "() => { if (!G.pending) return null;"
                    " const ev = eventById(G.pending.id);"
                    " applyChoice(G, ev.choices.length - 1); return ev.name; }")
                if dropped:
                    errs.append("pending event %r was not resolved by a choose action; "
                                "last option applied automatically" % dropped)
                note = str(reply.get("note", ""))[:NOTE_MAX]
                actions_total += len(acts)
                errors_total += len(errs)
                errors = errs

            page.evaluate("() => endTurn(G)")
            transcript.write(json.dumps({
                "turn": state["turn"] + 1, "pop": state["pop"],
                "actions": reply.get("actions"), "errors": errs, "note": note,
            }) + "\n")
            transcript.flush()
            print("[%s] turn %d done  pop=%d  errors=%d"
                  % (args.id, state["turn"] + 1, state["pop"], len(errs)), file=sys.stderr)

        final = page.evaluate(FINAL_JS)
        browser.close()
    transcript.close()

    over = final["over"] or {}
    result = {
        "run": args.id, "eval": "eval02", "contract": CONTRACT,
        "agent": agent_kind, "seed": args.seed, "started": started,
        "wall_seconds": int(time.time() - t0),
        "turns_played": final["turn"], "state_hash": final["hash"],
        "outcome": {"win": bool(over.get("win")), "score": over.get("score"),
                    "reason": over.get("reason"), "pop": over.get("pop"),
                    "research": over.get("research"), "stock": over.get("stock"),
                    "turns": over.get("turns")},
        "buildings": final["buildings"],
        "actions_total": actions_total, "errors_total": errors_total,
        "reference_sha256": REF_SHA,
    }
    if model_agent:
        result["api"] = {"calls": model_agent.calls,
                         "cost_usd": round(model_agent.cost, 4),
                         "input_tokens_total": model_agent.in_tok,
                         "output_tokens_total": model_agent.out_tok}
    out = os.path.join(runs, args.id + ".eval.json")
    json.dump(result, open(out, "w"), indent=1)
    print(json.dumps(result, indent=1))
    print("-> %s" % out, file=sys.stderr)


if __name__ == "__main__":
    main()
