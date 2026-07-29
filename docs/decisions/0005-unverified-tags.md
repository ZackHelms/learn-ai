# 0005 — Ship the roster with unverified tags, marked as such

**Status:** accepted · **Date:** 2026-07-29

## Context

`models/roster.yaml` was written in an environment whose network policy blocked
`ollama.com`, `registry.ollama.ai`, and `huggingface.co` (HTTP 403 at the
proxy). Model *facts* — families, sizes, licenses, release dates, tool-calling
support — were verified against vendor announcements and model cards. The exact
**Ollama tag strings** could not be, because that requires reaching the
registry.

Ollama tags do not always follow from the model name. A family released as
"Granite 4.1" might be `granite4.1:8b`, `granite4:8b`, or something else
entirely, and vendors retag over time.

## Decision

Ship the roster with tags following the documented naming convention, each
marked `tag_verified: false`, plus an explicit `provenance:` block stating what
was and was not checked.

## Why

The alternatives were worse:

- **Omit the tags.** Makes the roster unusable and hides the problem rather
  than surfacing it.
- **Guess silently.** Presents unverified strings as facts. This is the failure
  mode the repo's own style guide exists to prevent — a reader hitting a 404
  cannot tell whether they broke something or the repo was wrong.
- **Block on verification.** Would have stalled everything else for a network
  policy issue unrelated to the curriculum's design.

Marking uncertainty in the data means the machinery around it can react:
`pull-roster.sh` prints a specific recovery procedure on a failed pull, and
`/update-models` knows exactly which entries need confirming.

## Consequences

- A first-time reader may hit a 404 on `ollama pull`. `scripts/pull-roster.sh`
  handles this explicitly, naming the likely cause and the three-step fix.
- Clearing these flags is the top item in `docs/ROADMAP.md`.
- The estimated `disk_gb` / `min_ram_gb` figures are also unmeasured and labeled
  as estimates in `provenance:`. `scripts/bench.py` produces the real numbers.

## What would change this

Run `/update-models` from a machine with network access. When every entry reads
`tag_verified: true`, this ADR becomes history — leave it in place as the record
of why the flags exist.

To verify from a Claude Code web session instead, add `ollama.com` and
`registry.ollama.ai` to the environment's allowed hosts. See
<https://code.claude.com/docs/en/claude-code-on-the-web>.
