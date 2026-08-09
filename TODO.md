# TODO

The working backlog. Open this when you sit down.

This file is written to be **read cold** — assume no memory of the session that
produced the repo. [`docs/ROADMAP.md`](docs/ROADMAP.md) covers *what the modules
are*; this covers *what needs doing*. They deliberately do not overlap.

---

## Start here on a fresh machine

```bash
git clone https://github.com/ZackHelms/learn-ai.git
cd learn-ai

bash scripts/check-env.sh          # do this BEFORE downloading gigabytes
```

Fix anything it flags, then:

```bash
curl -fsSL https://ollama.com/install.sh | sh   # native app on macOS instead
bash scripts/pull-roster.sh --dry-run           # see what it will fetch
bash scripts/pull-roster.sh
```

> **Expect the first pull to fail.** The model tags in `models/roster.yaml` were
> never confirmed against the live registry — see *Unverified tags* below. A 404
> means the roster is stale, not that you did something wrong.
> `scripts/pull-roster.sh` prints the three-step fix.

Then work through [Track 01, Module 01](track-01-local-models/01-local-model-lab/)
and record what you get in its
[`FIELD-NOTES.md`](track-01-local-models/01-local-model-lab/FIELD-NOTES.md).

---

## Decisions pending

Mine to make, nobody else's. Each says what happens if left alone, so **silence
is a valid answer** — these are not blocking.

- [ ] **Ordering: evals at module 03, before the agent loop.**
      Reasoning in [ROADMAP](docs/ROADMAP.md#two-decisions-about-ordering).
      *If unchanged:* evals land at 03, and everything downstream gets written
      to be measurable against the harness built there.

- [ ] **Where `eval01/` formally lives.** The Ashfall Outpost one-prompt eval
      sits at the repo root as a deliberate working area while it stabilizes —
      outside the track structure, which normally forbids new top-level
      directories. Once proven, either formalize as a shared `evals/` asset
      (short ADR) or fold into a module (Track 01's evals module, or Track 02 as
      the free-tier comparison exercise).
      *If unchanged:* stays at root, exempt from the track rules.

- [ ] **The spine example carried across modules.**
      Currently proposed: a changelog / release-notes drafter that reads
      `git log` and emits structured output. Chosen because ground truth is
      cheap, structured output is where small models fail legibly, and it needs
      real tools by module 04.
      *If unchanged:* module 02 onward is written around it. Changing it later
      means rewriting exercises, not editing a line.

---

## Gated on running module 01

Empirical. Not settleable from the armchair, and **module 02 gets written wrong
if these are guessed at.** Record answers in module 01's field notes.

- [ ] **Is the smallest model usefully bad, or uselessly bad?**
      The premise of the whole course is that weak models fail *legibly* — that
      the failure points at its cause. A model emitting pure noise teaches
      nothing. If rung 0 is noise rather than instructive failure, drop it and
      start the ladder a rung higher.

- [ ] **Can the top rung complete a multi-step tool loop?**
      **This is the largest design risk in the curriculum.** Module 04 assumes
      "a working agent" is reachable on this roster. Nothing in module 01 tests
      it directly, but Exercise A is the leading indicator: a model that cannot
      reliably emit a JSON object will not reliably emit a tool call — same
      capability, different hat.
      *If it fails:* module 04 needs constrained decoding (llama.cpp GBNF
      grammars) or heavier scaffolding — and should say so plainly rather than
      pretend the roster is fine.

---

## Repo maintenance

- [ ] **Clear the `tag_verified: false` flags.** Run `/update-models` from a
      machine with network access. Note the likely failure mode: fixing only the
      one tag that blocked you and leaving the other five stale.
- [ ] **Test the macOS paths.** Native Ollama on macOS, and Ubuntu-on-Apple-
      Silicon. Both are currently documented as untested — honest, but untested.
- [ ] **CI** — `render-roster.py --check` plus a link check on PR. Waiting until
      `/verify-docs` has proven itself locally.
- [ ] **Scheduled freshness check** — monthly job running the `freshness-auditor`
      subagent, opening an issue when the roster drifts.

---

## State to carry forward

Context that would otherwise be lost. Nothing here is urgent; all of it is the
kind of thing that wastes an hour if forgotten.

### Unverified tags

`models/roster.yaml` entries all carry `tag_verified: false`. Model **families,
sizes, licenses, and tool-calling support were verified** against vendor
announcements and model cards. The **exact Ollama tag strings were not**, because
the authoring environment could not reach `ollama.com`.

Rationale in [ADR 0005](docs/decisions/0005-unverified-tags.md). Short version:
guessing silently would have been worse, since a reader hitting a 404 could not
tell whether they broke something or the repo was wrong.

`disk_gb` and `min_ram_gb` are likewise **estimates**, labeled as such in the
roster's `provenance:` block. `scripts/bench.py` produces real numbers.

### Network policy in Claude Code web sessions

Web sessions apply an environment network policy that **403s `ollama.com`,
`registry.ollama.ai`, and `huggingface.co`** at the proxy. pypi and npm are
reachable.

So `/update-models` and the `freshness-auditor` subagent must run from a local
session, or those hosts need adding to the environment's allowed list — see
<https://code.claude.com/docs/en/claude-code-on-the-web>. The symptom is HTTP
403, not a DNS failure; don't mistake it for a dead link.

### Library versions, verified from pypi/npm on 2026-07-29

Pulled live from the registries, so these are real rather than recalled. Useful
when writing modules 03, 07, and 08. Not pinned anywhere in the repo — treat as
a starting point to re-check, not as gospel.

| Package | Version | Notes |
|---|---|---|
| `pydantic-ai` | 2.20.0 | candidate for module 08 |
| `mcp` (Python) | **2.0.0** | major bump, released 2026-07-28 |
| `@modelcontextprotocol/sdk` (npm) | 1.30.0 | |
| `inspect-ai` | 0.3.251 | candidate for module 03 |
| `deepeval` | 4.1.4 | |
| `promptfoo` (npm) | 0.121.19 | pypi copy is stale — use npm |
| `langgraph` | 1.2.10 | |
| `openai` | 2.50.0 | |
| `smolagents` | 1.26.0 | |
| `llama-cpp-python` | 0.3.34 | |
| `ollama` (client) | 0.6.2 | |

⚠️ **Module 07 must target MCP SDK 2.x.** The 2.0.0 release is recent enough
that most tutorials surfaced by search will be 1.x.

### What is actually verified in this repo

Worth being precise about, since the repo's central rule is *never invent a
number*.

**Run and confirmed working:** `check-env.sh` (on Ubuntu 24.04, 15 GB, 4 cores,
AVX-512), `render-roster.py` including `--check` idempotency, `bench.py` argument
and error paths, `pull-roster.sh` roster parsing, the structured-output
exercise's grading logic against handcrafted cases, all relative links and
anchors.

**Never run:** anything requiring a model. No model was pulled, loaded, or
benchmarked. That is why the repo ships **zero performance figures** — it ships
`scripts/bench.py` and an empty `FIELD-NOTES.md` instead.

The macOS instructions and the llama.cpp appendix are likewise unverified and
marked as such in the text.

---

## Done

- Track restructure: top-level `track-NN-slug/` layout, tracks 01–03
  ([ADR 0006](docs/decisions/0006-tracks-top-level.md)), 2026-08-08
- Modules 00 (overview) and 01 (local model lab), with exercises
- `models/roster.yaml` as single source of truth, with generated-block rendering
- `scripts/`: `check-env.sh`, `pull-roster.sh`, `bench.py`, `render-roster.py`
- `AGENTS.md` + `CLAUDE.md`, `.claude/` commands and subagents
- `docs/`: `STYLE.md`, `ROADMAP.md`, five ADRs
