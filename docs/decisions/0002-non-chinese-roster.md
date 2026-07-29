# 0002 — Restrict the model roster to non-Chinese vendors

**Status:** accepted · **Date:** 2026-07-29

## Context

Several of the strongest open-weight models at the sizes this course targets
come from Chinese labs — Qwen, DeepSeek, GLM, Yi, InternLM, Kimi, MiniMax. On
capability-per-parameter alone, some would be obvious roster picks.

## Decision

The roster includes **non-Chinese vendors only**. Current pool: IBM, Google,
Microsoft, OpenAI, Meta, Mistral AI, NVIDIA, AI2, Hugging Face.

## Why

This is a **stated preference of the repo owner**, recorded here so it is
explicit rather than implicit. It is not a technical judgement about model
quality, and this document should not be read as one.

Writing it down has a practical purpose: without it, every future roster
refresh re-opens the question, and eventually someone adds a Qwen model because
it benchmarks well and nobody remembers why it was left out.

## Consequences

- We give up some capability-per-parameter at the small end. Accepted.
- Coverage stays good regardless — IBM Granite in particular provides a full
  ladder from ~350M to 8B under Apache-2.0 with native tool calling, which is
  most of what this course needs.
- `models/roster.yaml` carries an `excluded:` section recording this so the
  reasoning travels with the data.
- Anyone who disagrees can edit one YAML file and re-render. The constraint is
  a default, not a lock — nothing in the curriculum depends on it.

## What would change this

A reader forking this for their own use can drop the constraint freely. For the
upstream repo it stands until the owner says otherwise.
