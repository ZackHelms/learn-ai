# 0003 — Ollama as the primary runtime, llama.cpp as an appendix

**Status:** accepted · **Date:** 2026-07-29

## Context

Running a model locally needs a runtime. The realistic options are Ollama,
llama.cpp directly (`llama-server`), LM Studio, and vLLM. They differ mostly in
how much they hide.

## Decision

**Ollama is the primary runtime.** `llama.cpp` appears as an appendix in module
01 and is available to anyone who wants it thereafter.

## Why

- **Ollama gets to a first token fastest.** One install, one `pull`, and an
  OpenAI-compatible endpoint on `:11434`. Module 01 is about understanding
  models, not about compiling one.
- **The OpenAI-compatible API is the actual teaching surface.** Every later
  module talks to `/v1/chat/completions`. Because that surface is a de-facto
  standard, everything the reader learns transfers to hosted providers and to
  other runtimes. The runtime becomes swappable, which is the point.
- **Model management is scriptable.** `pull`, `list`, `ps`, and `/api/ps` make
  `scripts/pull-roster.sh` and `scripts/bench.py` straightforward. Managing GGUF
  files by hand would put busywork in front of the lesson.
- **Native timing counters.** Ollama returns `eval_count`, `eval_duration`, and
  `load_duration` per request, so benchmarking separates load from prompt
  processing from generation without wall-clock guesswork.

**But llama.cpp still earns its appendix.** Ollama hides quantization choices,
context sizing, and grammar-constrained decoding. Those are real concepts the
reader should see at least once, and llama.cpp is where they are visible. LM
Studio was ruled out as GUI-first, which is hard to script and hard to put in a
repeatable exercise. vLLM is built for GPU serving and is a poor fit for CPU.

## Consequences

- A dependency on Ollama's naming and tagging. Mitigated by keeping tags in
  `models/roster.yaml` only, so a retag is a one-file fix.
- Module 01 must explicitly say what Ollama is abstracting, otherwise the reader
  builds a mental model with a hole in it. That is the appendix's job.
- Automated roster refresh needs network access to `ollama.com`. Noted in
  `.claude/commands/update-models.md`.

## What would change this

If Ollama's API drifted away from OpenAI compatibility, or if a runtime appeared
that was equally easy but more transparent, this would be worth revisiting. The
curriculum's dependency is on the *API shape*, not on Ollama itself.
