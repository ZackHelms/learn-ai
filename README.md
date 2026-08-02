# learn-ai

Learning **agentic AI with locally hosted models** — small models, ordinary
hardware, no paid tooling required.

This is a lab notebook, not a textbook. I am working through this material and
writing it down as I go, which means it includes the wrong turns.

## The premise

The models used here are **deliberately weak**. Small, fast, CPU-bound, and not
very smart.

That is on purpose. A frontier model is forgiving — give it a vague prompt, a
sloppy tool schema, or no examples and it often succeeds anyway. Great for
getting work done, useless for learning, because you cannot tell which parts of
your setup mattered. A 3B model is not forgiving. It fails, and the failure
points at its cause.

Small models make the machinery visible.

## Harness-agnostic

Nothing here requires Claude Code, GitHub Copilot, or OpenAI Codex. Every module
instead ends with a section mapping what you just built by hand onto what those
tools do internally — so the material is useful *to* people who pay for them
without being dependent *on* them.

## Start here

**→ [Module 00 — Overview](modules/00-overview/)**

Then [Module 01 — Local model lab](modules/01-local-model-lab/).

## What you need

- **Ubuntu 24.04 LTS or later** — native, or via WSL2 on Windows. Mac users:
  read [the platform note](modules/00-overview/#if-you-are-on-a-mac) first, it
  matters.
- **~16 GB RAM**, **~20 GB disk**
- **No GPU.** Everything runs on CPU.

```bash
git clone https://github.com/ZackHelms/learn-ai.git
cd learn-ai
bash scripts/check-env.sh
```

## Layout

| Path | What |
|---|---|
| [`modules/`](modules/) | The curriculum |
| [`models/roster.yaml`](models/roster.yaml) | The model list — single source of truth |
| [`scripts/`](scripts/) | Environment check, model pull, benchmarking |
| [`TODO.md`](TODO.md) | The working backlog — open questions and what's next to do |
| [`docs/ROADMAP.md`](docs/ROADMAP.md) | Module status and specs for what's next |
| [`docs/STYLE.md`](docs/STYLE.md) | How this repo is written |
| [`docs/decisions/`](docs/decisions/) | Why things are the way they are |
| [`AGENTS.md`](AGENTS.md) | Instructions for AI agents working on this repo |

## Status

Modules 00 and 01 are written. Modules 02–09 are specced in
[`docs/ROADMAP.md`](docs/ROADMAP.md). There are no empty placeholder folders —
a module appears when it has content.

Open questions and what's next to do are in [`TODO.md`](TODO.md), which is
written to be read cold.

**This repo ships no benchmark numbers.** Performance figures are meaningless
across machines, so instead of publishing numbers that would be wrong for you,
it ships [`scripts/bench.py`](scripts/bench.py) and a `FIELD-NOTES.md` in each
module for recording your own.

**Model tags are not yet verified.** The roster's model families, sizes, and
licenses were checked against vendor sources, but the exact Ollama tag strings
were not — see [ADR 0005](docs/decisions/0005-unverified-tags.md). If
`ollama pull` 404s, the roster is stale rather than you being wrong, and
`scripts/pull-roster.sh` tells you how to fix it.

## Contributing

Field notes especially welcome — different hardware produces different numbers,
and that spread is information. Read [`docs/STYLE.md`](docs/STYLE.md) first; the
rule that matters most is **never invent a number**.

## License

[MIT](LICENSE)
