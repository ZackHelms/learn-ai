# 0001 — Target CPU-only inference on 16 GB of RAM

**Status:** accepted · **Date:** 2026-07-29

## Context

This course needs a hardware target. The obvious choice is "whatever you have,"
but that makes every exercise unreproducible and every number meaningless.

## Decision

Target **16 GB of system RAM, CPU-only inference, no GPU**, with roughly 10 GB
actually usable for a model once an OS, an editor, and a browser are running.

## Why

- **It is what people have.** A 16 GB laptop is ordinary. A 24 GB GPU is not.
  Requiring a GPU would exclude most of the audience.
- **The constraint is pedagogically useful, not just tolerable.** It forces
  small models, and small models fail legibly. See
  [ADR 0003](0003-ollama-primary.md) and the roster rationale in
  `models/roster.yaml`.
- **One model resident at a time is a feature.** Cross-model comparison has to
  run sequentially, which means the reader sees load time, eviction, and cold
  starts as real phenomena rather than as footnotes.

## Consequences

- The roster caps out around 8B dense at Q4. Anything larger is optional and
  flagged as possibly not fitting.
- Generation will be slow — single-digit to low-double-digit tokens/sec is
  normal. Exercises must be sized so that slowness is tolerable, which mostly
  means short outputs.
- No exercise may depend on running two models concurrently.
- GPU users are not penalized; everything here works faster on a GPU. The
  target is a floor, not a ceiling.

## What would change this

If the audience turns out to be mostly on 32 GB machines, the roster could add a
larger rung. The CPU-only assumption should probably stay regardless, because
CPU is the lowest common denominator and GPU paths fragment instructions across
CUDA, ROCm, and Metal.
