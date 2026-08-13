# Track 01 - local models backlog

Track-specific decisions and empirical gates. Repo-wide items live in the
[root TODO](../TODO.md); module specs live in
[ROADMAP](../docs/ROADMAP.md#track-01--local-models).

Open work only: check an item off when it lands, then fold it into a dated entry
in the [root CHANGELOG](../CHANGELOG.md) at the next commit and drop the line.

## Decisions pending

Mine to make, nobody else's. Each says what happens if left alone, so **silence
is a valid answer** - these are not blocking.

- [ ] **Ordering: evals at module 03, before the agent loop.**
      Reasoning in [ROADMAP](../docs/ROADMAP.md#two-decisions-about-ordering).
      *If unchanged:* evals land at 03, and everything downstream gets written
      to be measurable against the harness built there.

- [ ] **The spine example carried across modules.**
      Currently proposed: a changelog / release-notes drafter that reads
      `git log` and emits structured output. Chosen because ground truth is
      cheap, structured output is where small models fail legibly, and it needs
      real tools by module 04.
      *If unchanged:* module 02 onward is written around it. Changing it later
      means rewriting exercises, not editing a line.

## Gated on running module 01

Empirical. Not settleable from the armchair, and **module 02 gets written wrong
if these are guessed at.** Record answers in module 01's field notes.

- [ ] **Is the smallest model usefully bad, or uselessly bad?**
      The premise of the whole course is that weak models fail *legibly* - that
      the failure points at its cause. A model emitting pure noise teaches
      nothing. If rung 0 is noise rather than instructive failure, drop it and
      start the ladder a rung higher.

- [ ] **Can the top rung complete a multi-step tool loop?**
      **This is the largest design risk in the curriculum.** Module 04 assumes
      "a working agent" is reachable on this roster. Nothing in module 01 tests
      it directly, but Exercise A is the leading indicator: a model that cannot
      reliably emit a JSON object will not reliably emit a tool call - same
      capability, different hat.
      *If it fails:* module 04 needs constrained decoding (llama.cpp GBNF
      grammars) or heavier scaffolding - and should say so plainly rather than
      pretend the roster is fine.

## State to carry forward

### Library versions, verified from pypi/npm on 2026-07-29

Pulled live from the registries, so these are real rather than recalled. Useful
when writing modules 03, 07, and 08. Not pinned anywhere in the repo - treat as
a starting point to re-check, not as gospel.

| Package | Version | Notes |
|---|---|---|
| `pydantic-ai` | 2.20.0 | candidate for module 08 |
| `mcp` (Python) | **2.0.0** | major bump, released 2026-07-28 |
| `@modelcontextprotocol/sdk` (npm) | 1.30.0 | |
| `inspect-ai` | 0.3.251 | candidate for module 03 |
| `deepeval` | 4.1.4 | |
| `promptfoo` (npm) | 0.121.19 | pypi copy is stale - use npm |
| `langgraph` | 1.2.10 | |
| `openai` | 2.50.0 | |
| `smolagents` | 1.26.0 | |
| `llama-cpp-python` | 0.3.34 | |
| `ollama` (client) | 0.6.2 | |

**Module 07 must target MCP SDK 2.x.** The 2.0.0 release is recent enough
that most tutorials surfaced by search will be 1.x.
