# 0006 — Tracks as the top-level curriculum unit

**Status:** accepted · **Date:** 2026-08-08

## Context

The repo began with a single premise: agentic AI with locally hosted weak
models, harness-agnostic. That premise is now one curriculum among several. The
next modules — what the free tiers of the major platforms can do, and what
Claude Pro unlocks — are not variations on the local-model premise, and forcing
them into the flat `modules/NN-slug/` layout would either dilute that premise
or misfile the content.

## Decision

Organize the curriculum into **tracks**: top-level directories named
`track-NN-slug/`, each with a README stating its premise, audience, and spend
assumption, containing its own zero-padded `MM-slug/` modules.

- `track-01-local-models/` — local weak models, harness-agnostic. The original
  premise and the original modules 00–01, moved with history preserved.
- `track-02-free-tier/` — what the free tiers of Gemini, Microsoft Copilot,
  ChatGPT/Codex, and Claude can do, at zero spend.
- `track-03-claude-pro/` — what Claude Pro at $20/month unlocks.

Module numbers restart per track. Tracks 02 and 03 exist as README-only
scaffolds until their first modules have content.

## Why this shape

- **Numbered top-level directories, no `tracks/` parent.** The numbers make
  the buckets visually obvious in a listing without adding nesting noise, and
  skipping the parent keeps module files at the same depth as before — every
  parent-relative link inside the moved modules kept working unchanged.
- **Numbers restart per track.** Adding a module to one track never renumbers
  another. The cost: a bare "module 04" is ambiguous repo-wide, so cross-track
  references must name the track.
- **Premises move down a level.** "No paid tooling, no API keys" and "every
  module ends with an If-you-use-a-harness section" were repo-wide rules; they
  are now Track 01 rules, stated in its README and scoped in `AGENTS.md` and
  `docs/STYLE.md`. Each track states its own spend assumption.

## Consequences

- Cross-track references must name the track.
- The root README, `docs/ROADMAP.md`, and `AGENTS.md` are track-aware; the
  roadmap gains per-track sections and a list of deferred tracks (base paid
  tiers of OpenAI, Gemini, GitHub Copilot) that get no scaffolding until there
  is a real need.
- `models/roster.yaml` and `scripts/` stay at the repo root. They serve Track
  01, but the documented commands (`uv run scripts/...`,
  `bash scripts/check-env.sh`) are root-anchored everywhere, and moving them
  would break more than it organizes.
- A new track requires a ROADMAP entry and an ADR before its directory
  appears.

## What would change this

A track accumulating enough modules that it needs internal structure of its
own, or enough tracks that the root listing gets noisy and a `tracks/` parent
becomes worth the link churn.
