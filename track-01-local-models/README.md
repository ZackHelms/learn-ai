# Track 01 — Local models

> Agentic AI with locally hosted models — small models, ordinary hardware, no
> paid tooling required.

This is the deep-dive track. You run everything yourself, on your own machine,
and build the core machinery — prompts, evals, tool loops, context management —
by hand.

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

Nothing in this track requires Claude Code, GitHub Copilot, or OpenAI Codex.
Every module instead ends with an **"If you use a harness"** section mapping
what you just built by hand onto what those tools do internally — so the
material is useful *to* people who pay for them without being dependent *on*
them.

If you already use one of those tools at work, that mapping is this track's
selling point: it is how you find out what the tool is actually doing.

## Start here

**→ [Module 00 — Overview](00-overview/)**

Then [Module 01 — Local model lab](01-local-model-lab/).

## What you need

- **Ubuntu 24.04 LTS or later** — native, or via WSL2 on Windows. Mac users:
  read [the platform note](00-overview/#if-you-are-on-a-mac) first, it
  matters.
- **~16 GB RAM**, **~20 GB disk**
- **No GPU.** Everything runs on CPU.

```bash
git clone https://github.com/ZackHelms/learn-ai.git
cd learn-ai
bash scripts/check-env.sh
```

The model list lives in [`models/roster.yaml`](../models/roster.yaml) at the
repo root — it is this track's roster and the single source of truth for model
names, tags, and sizes.

## Status

Modules 00 and 01 are written. Modules 02–09 are specced in
[`docs/ROADMAP.md`](../docs/ROADMAP.md). There are no empty placeholder
folders — a module appears when it has content.

**This track ships no benchmark numbers.** Performance figures are meaningless
across machines, so instead of publishing numbers that would be wrong for you,
it ships [`scripts/bench.py`](../scripts/bench.py) and a `FIELD-NOTES.md` in
each module for recording your own.

**Model tags are not yet verified.** The roster's model families, sizes, and
licenses were checked against vendor sources, but the exact Ollama tag strings
were not — see [ADR 0005](../docs/decisions/0005-unverified-tags.md). If
`ollama pull` 404s, the roster is stale rather than you being wrong, and
[`scripts/pull-roster.sh`](../scripts/pull-roster.sh) tells you how to fix it.
