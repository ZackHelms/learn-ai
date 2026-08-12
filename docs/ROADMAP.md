# Roadmap

Status of the curriculum, and the plan for what comes next.

The curriculum is organized into **tracks** — top-level `track-NN-slug/`
directories, each with its own premise, audience, and spend assumption
([ADR 0006](decisions/0006-tracks-top-level.md)). Module numbers restart per
track, so cross-track references name the track.

There are deliberately **no empty stub directories** in this repo. A module
appears on disk when it has content. Until then it lives here as a spec.

| Track | Premise | Status |
|---|---|---|
| [01 — Local models](../track-01-local-models/) | Weak local models make the machinery visible | 00–01 written; 02–09 specced below |
| [02 — Free tier](../track-02-free-tier/) | The big four platforms at zero spend | module 01 in progress (2026-08) |
| [03 — Claude Pro](../track-03-claude-pro/) | What $20/month unlocks over free | planned; candidates below |
| [04 — Benchmark](../track-04-benchmark/) | Measure models, don't vibe them | eval01 shipped; eval02–05 specced below |
| later | Base paid tiers of OpenAI, Gemini, GitHub Copilot | deferred, below |

---

## Track 01 — Local models

Premise: **local weak models + harness-agnostic** — deliberately weak models on
ordinary hardware make the machinery visible, and every module maps what was
built onto the commercial harnesses. The original curriculum; the full premise
is in [its README](../track-01-local-models/README.md).

| # | Module | Status |
|---|---|---|
| 00 | [Overview](../track-01-local-models/00-overview/) | ✅ written |
| 01 | [Local model lab](../track-01-local-models/01-local-model-lab/) | ✅ written |
| 02 | Prompt engineering for weak models | 📋 specced below |
| 03 | Evals: unit tests for AI | 📋 specced below |
| 04 | Tool calling and the agent loop | 📋 specced below |
| 05 | Context engineering | 📋 specced below |
| 06 | Harness teardown | 📋 specced below |
| 07 | MCP: tools as a protocol | 📋 specced below |
| 08 | SDK agents | 📋 specced below |
| 09 | Hybrid and routing | 📋 specced below |

---

### Two decisions about ordering

I sketched this curriculum in a different order originally. Two things moved,
and it is worth writing down why.

#### Evals come early (module 03), not late

My first instinct was to cover evals after context engineering, once there was
something substantial to evaluate. I think that is wrong, for the same reason
you do not teach unit testing in the last week of a programming course.

Putting evals at 03 means **every module after it can be measured**. The tool
loop in 04 gets scored. The context changes in 05 get scored — which is the only
honest way to claim a change to an instructions file actually helped. The SDK
rewrite in 08 gets scored against the context version it replaced.

There is a second reason, specific to this course. Evals need *spread* to teach
anything: if everything passes, the eval set has told you nothing. A roster of
deliberately weak models produces genuine spread. This is the single place where
the weak-model premise pays off hardest, and it should not be deferred.

#### Tool calling gets its own module (04)

Originally this was folded into context engineering. Separating it matters
because **hand-writing the agent loop is what demystifies the word "agent"**.
It is about a hundred lines: send messages, get back a tool call, execute it,
append the result, repeat until done. Once you have typed that out, every
agent framework and every commercial harness becomes recognizable rather than
magical.

It is also the direct prerequisite for module 06 landing as *recognition*
instead of description.

---

### Module specs

#### 02 — Prompt engineering for weak models

**Thesis:** most prompt engineering advice is written for frontier models, where
it is hard to tell whether a technique helped or the model just coped. On a 3B
model the difference is obvious and reproducible.

Covers: the system/user split and how much it actually matters; output-format
instructions and why "return JSON" is not enough; few-shot as the highest-ROI
technique at this size; task decomposition; where chain-of-thought helps and
where it just burns tokens; how the chat template can silently break things.

Exercise spine: take a task all roster models fail, and fix it with prompting
alone. Then find the task no amount of prompting fixes on rung 0 — the point
where the answer is a bigger model or a smaller problem.

Depends on: 01.

#### 03 — Evals: unit tests for AI

**Thesis:** evals are unit tests that tolerate non-determinism. Same idea —
pin behavior so a change that breaks it is visible — but the assertion is
statistical rather than exact.

Covers: the ladder from cheapest to most expensive assertion — exact match,
schema validation, property assertions, rubric scoring, LLM-as-judge; why you
climb that ladder only as far as you need; building a small eval set with real
ground truth; running the whole roster against it and producing a leaderboard;
pass rates and the variance you get from re-running the same eval; using a local
model as the judge, and how to tell when the judge is the problem.

Exercise spine: build an eval set for the module 02 task. Score every model.
Then deliberately regress a prompt and watch the eval catch it.

Depends on: 01, 02. **Everything after this uses the eval harness built here.**

#### 04 — Tool calling and the agent loop

**Thesis:** an agent is a while loop around a model that can call functions.
That is the whole idea. Write it yourself and it stops being mysterious.

Covers: tool/function schemas and how they reach the model; the loop itself,
written from scratch, no framework; parsing and validating tool calls from a
model that gets them wrong; error handling and retries; stopping conditions and
runaway loops; why small models fail at multi-step tool use specifically, and
what scaffolding recovers.

Exercise spine: implement the loop in ~100 lines against the local endpoint.
Run it across the roster and watch the capability cliff — rung 0 cannot do it,
rung 3 can. Score with the module 03 harness.

Depends on: 01, 03.

#### 05 — Context engineering

**Thesis:** context is a budget you spend, not a bucket you fill. And a
surprising amount of what people put in context should be a script instead.

Covers: instructions files (`AGENTS.md`, `CLAUDE.md`) and what belongs in them;
subagents and why isolating context beats one giant prompt; skills and
progressive disclosure; **pushing work out of the model** — anything
deterministic should be a script, because a script is free, exact, and
repeatable; context rot in long sessions; retrieval as context management.

The cost argument gets a section of its own: every repeated agent action that
could be a script is money and latency spent re-deriving something you already
know.

Exercise spine: take the module 04 agent, move its deterministic parts into
scripts, and show the eval score holds while token count drops.

Depends on: 03, 04.

#### 06 — Harness teardown

**Thesis:** having built the loop and the context system by hand, the commercial
harnesses become legible.

Covers: what Claude Code, Codex, Copilot, and Cursor each do with the agent
loop, context assembly, tool permissions, and subagents; where the convergence
is real (`AGENTS.md` support across tools) and where it is not; what they add
that you would not build yourself; when a local model is genuinely the right
choice and when it is not.

Explicitly **not** a product review, and does not require owning any of them.

Depends on: 04, 05.

#### 07 — MCP: tools as a protocol

**Thesis:** MCP is what happens when tool definitions stop being per-application
code and become an interface other people's programs can speak.

Covers: the protocol shape; writing a small server; connecting it to a local
model; whether small models can realistically drive MCP servers (open question —
this needs measuring, not asserting); tool-count budgets and context cost.

⚠️ **Target the current SDK.** The MCP Python SDK went to 2.0.0 on 2026-07-28.
Most tutorials found by search will be 1.x. Verify before writing.

Depends on: 04.

#### 08 — SDK agents

**Thesis:** context-defined agents are cheap to build and hard to test. Code
agents are the opposite. Knowing when to convert is the actual skill.

Covers: the tradeoff honestly; converting the module 04/05 agent into an SDK
agent and diffing the experience; what you gain (typing, testing, control flow,
composition) and what you lose (edit-and-rerun immediacy); running the same
evals against both so the comparison is measured, not asserted.

Candidate library: Pydantic AI, which points at an OpenAI-compatible local
endpoint with little friction. Alternatives to weigh at writing time.

Depends on: 03, 04, 05.

#### 09 — Hybrid and routing

**Thesis:** local versus frontier is not a binary. The interesting systems route.

Covers: routing by task difficulty; local models as a cheap first pass and
filter; privacy as a routing constraint rather than a policy document; latency
budgets; cost modeling; using a local model to draft and a frontier model to
verify, and the reverse.

Depends on: everything.

> **Restructure note (2026-08-08):** the frontier half of this module needs a
> hosted API key, which Track 01's spend rule forbids as a requirement. Plan of
> record: the frontier legs become clearly marked optional asides —
> `docs/STYLE.md` rule 5 has exactly that escape hatch. Revisit at write time.

---

## Track 02 — Free tier

Premise: **what can you actually do at zero spend** on Google Gemini, Microsoft
Copilot, OpenAI ChatGPT/Codex, and Anthropic Claude — across the web, the
desktop apps, and VSCode. No dev machine required; a phone or tablet is enough
to start. Paid features appear only as "what upgrading unlocks."

### 01 — Free tiers of the big four platforms

Status: **in progress (2026-08)**, being written live in a separate session —
every step performed for real before it is written down. Walks each platform
through the three access modes, with honest commentary on where the modes
differ in what the AI can actually do for free.

Later Track 02 modules get specced once module 01 has shaken out the format.

---

## Track 03 — Claude Pro

Premise: **what does Claude Pro at $20/month unlock** compared to the free
tier. The natural follow-up to Track 02, for someone already paying or deciding
whether to. Planned; nothing specced in detail yet. Candidate directions:

- A tour of the paid surfaces — web, desktop app, mobile app, VSCode, Claude
  Design — and what each adds over the free tier.
- SDK-based agents on the small, fast end of the paid model lineup, with
  deliberately chosen effort levels and evals to measure the difference.
  Deliberately overlaps Track 01's evals and SDK material: the same concepts
  land differently on strong models, and the reinforcement is the point. What
  the Pro subscription itself covers versus what needs separate API billing is
  an open question — verify at write time.

---

## Track 04 — Benchmark

Premise: **a benchmark is a collection of evals plus a protocol.** One eval
measures one axis; the track's job is to cover several, so a model that aces
one axis and fails another is visible instead of averaged away. Full premise in
[its README](../track-04-benchmark/README.md); the move-in decision is
[ADR 0007](decisions/0007-benchmark-track.md).

| # | Eval | Status |
|---|---|---|
| eval01 | [Build Ashfall](../track-04-benchmark/eval01-build-ashfall/) — one-prompt build | ✅ shipped; sets 0–3 scored |
| eval02 | [Play Ashfall](../track-04-benchmark/eval02-play-ashfall/) — agent as player | ✅ shipped 2026-08-12 |
| eval03 | [Repair, not build](../track-04-benchmark/eval03-repair/) | ✅ shipped 2026-08-12 |
| eval04 | [Constraint stack](../track-04-benchmark/eval04-constraint-stack/) | ✅ shipped 2026-08-12 |
| eval05 | [Grounded answer, poisoned context](../track-04-benchmark/eval05-poisoned-context/) | ✅ shipped 2026-08-12 |

Design rules for the new four: **no judge** (eval01's judged half is comparable
only while judge model + effort + grader prompt stay fixed — a dependency not
worth repeating), and **no output ceiling** (eval01 is output-bound; each new
eval removes that so small-context local models get real numbers). Build order:
eval04 first (smallest, immediately useful as the cheap daily driver), then
eval02 (the frozen reference artifact already exists).

### eval02 — Play Ashfall

> **Shipped 2026-08-12.** As specced, plus the contract's key design call:
> the model's only memory is a 600-char note it re-writes each turn.
> Build-day finding: nothing — including the game's own greedy policy —
> survives seed 1337 to turn 60; winnability is an open question and the
> eval is unsaturated in both directions. Spec kept below.

**Thesis:** long-horizon coherence is a different axis from single-step
reasoning, and eval01 never touches it.

Mechanism: the frozen reference build
(`track-04-benchmark/reference/ashfall-reference-v1.html`, a 100/100 eval01
run) is the environment. A Python driver runs it in headless Chromium from a
fixed seed; each turn the model receives compact state JSON and returns action
JSON; the driver applies it and advances. Final outcome at turn 60 is scored
deterministically (survival, resources, milestones — exact weights set at
write time from the reference's actual mechanics).

Why this axis: [Vending-Bench 2](https://andonlabs.com/evals/vending-bench-2)
(Andon Labs; accessed 2026-08-12; original paper
[arXiv:2502.15840](https://arxiv.org/abs/2502.15840)) shows frontier-model
failures over thousands of steps are looping, identity drift, and repeated bad
decisions — coherence failures, not reasoning failures at any single step.
This is the 60-turn small-scale version.

Properties worth having: no judge; no output ceiling, so a 4k-context local
model competes (small state in, small action out — Track 01's roster can play,
it just plays badly, which is a number rather than a DNF); per-turn cost is
tiny.

Design risks, named now so they get solved rather than discovered: the
determinism claim is environment-side — the game's own seeded PRNG (eval01
bans `Math.random`, so every compliant build ships one) plus a fixed seed
makes environment and scoring reproducible, but the *model* is still sampled,
so replicates are still required. The reference exposes a UI, not an API; the
driver's state-export/action contract is part of eval02 and must be versioned
like a prompt — the artifact itself stays frozen. And the state JSON must stay
small enough that turn history fits small contexts, or the protocol defines
what the model is told each turn (last-K turns only) — that memory design is
itself part of what gets measured.

Depends on: the frozen reference (exists), Playwright driver (exists in spirit
in eval01's runtime checks).

### eval03 — Repair, not build

> **Shipped 2026-08-12.** Five defects across the four planned classes,
> hardened once pre-freeze: the draft bug reports were diagnostic enough
> that haiku-low scored 100, so v1 froze with symptom-only reports. Still
> expected to saturate for frontier models — a subtler v2 defect set is in
> the track TODO. Spec kept below.

**Thesis:** eval01 is output-bound; repair is input-bound. Reading 2k lines
and touching 10 is the inverse skill of emitting 3k lines cold, and it
separates models eval01 lumps together.

Mechanism: a working ~2k-line file derived from the reference build, with N
seeded defects (off-by-one, operator-precedence, a turn-ordering race, a
broken save/load round-trip). The model gets the defective file and the
symptom list only, and must output a minimal unified diff. Scored
deterministically: hidden tests passed, defects fixed, lines touched
(penalizing shotgun rewrites), diff-applies-cleanly as its own reported line
(a malformed diff is signal, but legible signal).

Why this axis: [TRAIL](https://arxiv.org/abs/2505.08638) (Patronus AI, 2025)
found the best model localizes and categorizes errors in annotated agent
traces at ~11% — fault localization is nowhere near saturated, unlike
build-from-scratch.

Design risks: every seeded defect must be provably detectable by the hidden
suite (ship a reference fix that passes 100% — the never-invent-a-number rule
applied to solvability). The suite lives in the public repo, so "hidden" means
excluded from the run protocol, not secret — contamination risk is real and
worth a dated note. The lines-touched penalty needs calibrating against the
reference fix so minimal-correct scores maximum. The reference build's own
self-test pattern (it ships 30+ in-page tests) seeds the suite.

Depends on: the frozen reference (exists).

### eval04 — Constraint stack

> **Shipped 2026-08-12.** Built as specced: 23 constraints (21 satisfiable +
> 2 impossible), plus a lower-numbered tie-break rule the shakedown run
> showed was needed. Spec kept below for the record.

**Thesis:** instruction following measured with *unseen* constraint types,
cheap enough to run daily on anything.

Mechanism: one page of output, 20–25 programmatically checked constraints,
several in deliberate tension, and exactly two impossible to satisfy. Correct
behavior on the impossible pair is to flag it, not silently fake it. Scoring
is a checker script, fully deterministic, ~2k tokens per run — the daily
driver for local models and free-tier quota days.

Why this axis: [IFBench](https://arxiv.org/abs/2507.02833) (AI2/UW, 2025)
found models overfit the small set of verifiable constraint types in
IFEval-style benchmarks — leading models score under 50% on unseen constraint
types. So the constraints here are deliberately unusual, and the set is
versioned like a prompt: leaked-and-stale constraint sets get retired to a new
version with a new results table, never edited.

Design risks: the flag mechanic must be scored as classification — credit for
flagging the two impossible constraints AND for *not* flagging the satisfiable
ones — or "flag everything" games it. Every satisfiable-in-tension pair needs
a reference output proving satisfiability before the eval ships.

Depends on: nothing. Smallest eval in the track; build first.

### eval05 — Grounded answer, poisoned context

> **Shipped 2026-08-12.** Generator-derived bundle and key exactly as
> specced (the gates run at generation time; `--check` reproduces the
> committed files). Two variants, ~6k and ~30k tokens, same key. Spec kept
> below.

**Thesis:** eval01–04 never ask "did the model believe its context or invent
one." This does, with abstention and conflict-detection as first-class scored
outcomes.

Mechanism: a 30–50k-token bundle (spec + changelog + logs) and 20 questions —
some answerable, some contradicted between documents, some genuinely absent.
Answers use a constrained format (`VALUE` / `ABSENT` / `CONFLICT` with doc
references) so the key is exact-match and judge-free. Difficulty scales with
bundle size: an 8k variant and a full variant from the same generator serve a
small local model and a frontier model, reported separately.

Design risks: hand-writing an answer key against 50k tokens of prose is where
key errors live — the bundle should be *generated* from a ground-truth event
script with contradictions injected deliberately, so the key derives from the
script instead of from a human re-reading the prose. Freeze the v1 bundle for
comparability; the generator plus a new seed is the long-term contamination
answer.

Depends on: nothing shared; the bundle generator is the work.

---

## Deferred tracks

Base paid tiers of **OpenAI**, **Gemini**, and **GitHub Copilot**. Deferred
until there is a real need — no scaffolding, no directories, just this mention.
Copilot may come sooner (it is the tool at my day job); Gemini is interesting
for its multimodal audio/video/image tooling.

---

## Open items

Actionable work — decisions pending, the empirical questions that gate module
02, and repo maintenance — lives in [`TODO.md`](../TODO.md) at the repo root.

This file stays curriculum design: what each module is for, and why they are
ordered the way they are. Keeping the backlog out of it means the two cannot
drift into disagreeing with each other.
