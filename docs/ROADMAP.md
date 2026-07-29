# Roadmap

Status of the curriculum, and the plan for what comes next.

There are deliberately **no empty stub directories** in this repo. A module
appears on disk when it has content. Until then it lives here as a spec.

| # | Module | Status |
|---|---|---|
| 00 | [Overview](../modules/00-overview/) | ✅ written |
| 01 | [Local model lab](../modules/01-local-model-lab/) | ✅ written |
| 02 | Prompt engineering for weak models | 📋 specced below |
| 03 | Evals: unit tests for AI | 📋 specced below |
| 04 | Tool calling and the agent loop | 📋 specced below |
| 05 | Context engineering | 📋 specced below |
| 06 | Harness teardown | 📋 specced below |
| 07 | MCP: tools as a protocol | 📋 specced below |
| 08 | SDK agents | 📋 specced below |
| 09 | Hybrid and routing | 📋 specced below |

---

## Two decisions about ordering

I sketched this curriculum in a different order originally. Two things moved,
and it is worth writing down why.

### Evals come early (module 03), not late

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

### Tool calling gets its own module (04)

Originally this was folded into context engineering. Separating it matters
because **hand-writing the agent loop is what demystifies the word "agent"**.
It is about a hundred lines: send messages, get back a tool call, execute it,
append the result, repeat until done. Once you have typed that out, every
agent framework and every commercial harness becomes recognizable rather than
magical.

It is also the direct prerequisite for module 06 landing as *recognition*
instead of description.

---

## Module specs

### 02 — Prompt engineering for weak models

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

### 03 — Evals: unit tests for AI

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

### 04 — Tool calling and the agent loop

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

### 05 — Context engineering

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

### 06 — Harness teardown

**Thesis:** having built the loop and the context system by hand, the commercial
harnesses become legible.

Covers: what Claude Code, Codex, Copilot, and Cursor each do with the agent
loop, context assembly, tool permissions, and subagents; where the convergence
is real (`AGENTS.md` support across tools) and where it is not; what they add
that you would not build yourself; when a local model is genuinely the right
choice and when it is not.

Explicitly **not** a product review, and does not require owning any of them.

Depends on: 04, 05.

### 07 — MCP: tools as a protocol

**Thesis:** MCP is what happens when tool definitions stop being per-application
code and become an interface other people's programs can speak.

Covers: the protocol shape; writing a small server; connecting it to a local
model; whether small models can realistically drive MCP servers (open question —
this needs measuring, not asserting); tool-count budgets and context cost.

⚠️ **Target the current SDK.** The MCP Python SDK went to 2.0.0 on 2026-07-28.
Most tutorials found by search will be 1.x. Verify before writing.

Depends on: 04.

### 08 — SDK agents

**Thesis:** context-defined agents are cheap to build and hard to test. Code
agents are the opposite. Knowing when to convert is the actual skill.

Covers: the tradeoff honestly; converting the module 04/05 agent into an SDK
agent and diffing the experience; what you gain (typing, testing, control flow,
composition) and what you lose (edit-and-rerun immediacy); running the same
evals against both so the comparison is measured, not asserted.

Candidate library: Pydantic AI, which points at an OpenAI-compatible local
endpoint with little friction. Alternatives to weigh at writing time.

Depends on: 03, 04, 05.

### 09 — Hybrid and routing

**Thesis:** local versus frontier is not a binary. The interesting systems route.

Covers: routing by task difficulty; local models as a cheap first pass and
filter; privacy as a routing constraint rather than a policy document; latency
budgets; cost modeling; using a local model to draft and a frontier model to
verify, and the reverse.

Depends on: everything.

---

## Open items

Most of the work here surfaces on its own — the field notes ask for benchmark
numbers by name, the exercises force the model comparison, and a stale tag
announces itself as a failed pull. What follows is the residue: the things that
will *silently* not happen.

The first two groups are why this is a **gate list for module 02**, not a
backlog. Guess at them and module 02 gets written wrong.

### Decisions only the author can make

Each states its default, so leaving it alone is a valid answer rather than an
unresolved question.

- [ ] **Ordering: evals at 03, before the agent loop.** Reasoning is in
      [Two decisions about ordering](#two-decisions-about-ordering) above.
      *Default if unchanged:* evals land at 03 and everything downstream is
      written to be measurable against the harness built there.
- [ ] **The spine example.** Currently proposed: a changelog / release-notes
      drafter that reads `git log` and emits structured output — chosen because
      ground truth is cheap, structured output is where small models fail
      legibly, and it needs real tools by module 04. *Default if unchanged:*
      module 02 onward is written around it, and changing it later means
      rewriting exercises rather than editing a line.

### Answered by running module 01

These are empirical. Nobody can settle them from the armchair, and both were
flagged as risks when the curriculum was designed. Record answers in
[`modules/01-local-model-lab/FIELD-NOTES.md`](../modules/01-local-model-lab/FIELD-NOTES.md).

- [ ] **Is rung 0 usefully bad, or uselessly bad?** The premise needs it to fail
      in ways that *point at a cause*. A model that simply emits noise teaches
      nothing and should be swapped for the next rung up.
- [ ] **Is tool calling at rungs 2–3 reliable enough for module 04?**
      **This is the largest design risk in the curriculum.** Module 04 assumes
      "a working agent" is reachable on this roster. If the top rung cannot
      complete a multi-step tool loop, module 04 needs rethinking — either
      heavier scaffolding, constrained decoding, or an honest admission that
      this is where local models run out.

### Repo maintenance

- [ ] **Roster verification** — every `tag_verified: false` in
      `models/roster.yaml` needs confirming against the live registry. Run
      `/update-models` from a machine with network access. Note that fixing only
      the one tag that blocks you leaves the rest stale, which is the likely
      failure mode. See [ADR 0005](decisions/0005-unverified-tags.md).
- [ ] **Test the macOS paths** — native Ollama on macOS and Ubuntu-on-Apple-
      Silicon are both currently documented as untested. Honest, but untested.
- [ ] **CI** — run `render-roster.py --check` and a link check on PR. Waiting
      until `verify-docs` has proven itself locally.
- [ ] **Scheduled freshness check** — a monthly job that runs the freshness
      auditor and opens an issue when the roster drifts.
