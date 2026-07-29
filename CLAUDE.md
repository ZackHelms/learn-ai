# CLAUDE.md

@AGENTS.md

---

The instructions above are the source of truth and are shared with every other
harness. Only Claude-Code-specific notes belong below. If you are about to add
something here that would apply to any agent, put it in `AGENTS.md` instead —
see [ADR 0004](docs/decisions/0004-agents-md-source-of-truth.md).

## Slash commands

| Command | Purpose |
|---|---|
| `/update-models` | Check `models/roster.yaml` against upstream, propose edits, re-render tables |
| `/new-module` | Scaffold a module against the template in `docs/STYLE.md` |
| `/verify-docs` | Lint fenced commands, check links, detect generated-block drift |

## Subagents

| Agent | Use it for |
|---|---|
| `freshness-auditor` | Read-only sweep for stale version claims across the repo |
| `module-author` | Drafting a module in-voice against the template |

## Network access

`/update-models` and `freshness-auditor` need to reach `ollama.com`,
`registry.ollama.ai`, and `huggingface.co`. Claude Code **web** sessions apply
an environment network policy that may block these — the symptom is HTTP 403 at
the proxy, not a DNS failure.

If they are blocked, either run the command from a local Claude Code session, or
add those hosts to the environment's allowed list. See
<https://code.claude.com/docs/en/claude-code-on-the-web>.

## Working here

- After editing `models/roster.yaml`, always run
  `uv run scripts/render-roster.py`. Leaving generated blocks stale is the most
  likely way to make this repo internally inconsistent.
- Prefer editing `docs/ROADMAP.md` over creating placeholder module
  directories. This repo deliberately has no empty stubs.
- When a task would add fine-tuning, RAG, or GPU setup, say it is out of scope
  and point at `AGENTS.md` rather than quietly expanding the curriculum.
