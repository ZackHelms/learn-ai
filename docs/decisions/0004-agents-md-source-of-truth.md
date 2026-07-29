# 0004 — AGENTS.md is the source of truth; CLAUDE.md imports it

**Status:** accepted · **Date:** 2026-07-29

## Context

This repo is harness-agnostic by design: no exercise may require Claude Code,
Codex, or Copilot. But the repo *itself* is authored with agent assistance and
benefits from an instructions file. Those files are harness-specific —
`CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for Copilot,
`AGENTS.md` for a growing set of tools.

Creating a `CLAUDE.md` looks like it contradicts the harness-agnostic premise.

## Decision

**`AGENTS.md` holds all the substance.** `CLAUDE.md` is a thin file that imports
it via `@AGENTS.md` and adds only genuinely Claude-Code-specific notes.

## Why

- **One source of truth.** Two full instruction files drift, and the drift is
  silent — you only find out when an agent follows the stale one.
- **The repo should practice what it teaches.** Module 05 covers instructions
  files and module 06 covers cross-harness convergence. A repo that maintains
  four divergent copies of its own instructions would be poor evidence for its
  own advice.
- **It resolves the tension honestly.** The *curriculum* is harness-agnostic.
  The *authoring workflow* uses whatever tool is at hand. Those are different
  things, and pretending the repo has no tooling would be a lie of omission.
- **Additive, not exclusive.** A Copilot or Cursor user can add their own
  pointer file importing the same content. Nobody is locked out.

## Consequences

- Edits go in `AGENTS.md`. `CLAUDE.md` stays short enough that reviewing it is
  trivial.
- The `.claude/` directory (commands, subagents) is genuinely Claude-Code
  specific. It is *authoring* tooling, not curriculum, and the README says so.
- Users of other harnesses get the substance from `AGENTS.md` and lose only the
  slash commands, which are conveniences rather than requirements. Every one of
  them documents the equivalent manual steps.

## What would change this

If cross-harness command formats converge, the `.claude/` commands should move
to the shared format. Worth re-checking when module 06 is written.
