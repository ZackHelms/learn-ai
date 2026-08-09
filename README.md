# learn-ai

A hands-on lab notebook for learning practical AI skills, organized into
**tracks**. Each track has its own premise and its own audience — pick the one
that matches where you are. Working more than one is fine; the overlap
reinforces rather than repeats.

This is a lab notebook, not a textbook. I am working through this material and
writing it down as I go, which means it includes the wrong turns.

## The tracks

### [Track 01 — Local models](track-01-local-models/)

**Deliberately weak, locally hosted models make the machinery of AI visible.**
Small models on ordinary hardware, zero paid tooling. You build prompts, evals,
tool loops, and context management by hand — and every module maps what you
built onto what Claude Code, Copilot, and Codex do internally. The deep-dive
track; needs a machine that can run Ubuntu (native or WSL2).

- [Module 00 — Overview](track-01-local-models/00-overview/) ✅ written
- [Module 01 — Local model lab](track-01-local-models/01-local-model-lab/) ✅ written
- Modules 02–09 — specced in [`docs/ROADMAP.md`](docs/ROADMAP.md)

### [Track 02 — Free tier](track-02-free-tier/)

**What can you actually do with the free tiers** of Google Gemini, Microsoft
Copilot, OpenAI ChatGPT/Codex, and Anthropic Claude — across web, desktop apps,
and VSCode? Strictly zero spend. No dev machine required; a phone or tablet is
enough to start.

- Module 01 — in progress (August 2026)

### [Track 03 — Claude Pro](track-03-claude-pro/)

**What does Claude Pro at $20/month actually unlock** compared to the free
tier? A natural follow-up to Track 02, for someone already paying — or deciding
whether to.

- Planned — candidate modules in [`docs/ROADMAP.md`](docs/ROADMAP.md)

Later tracks may cover the base paid tiers of OpenAI, Gemini, and GitHub
Copilot — deferred, see the [roadmap](docs/ROADMAP.md).

## Layout

| Path | What |
|---|---|
| [`track-01-local-models/`](track-01-local-models/) | Track 01 — local models, built by hand |
| [`track-02-free-tier/`](track-02-free-tier/) | Track 02 — the big four platforms at zero spend |
| [`track-03-claude-pro/`](track-03-claude-pro/) | Track 03 — what the $20/month Claude tier unlocks |
| [`models/roster.yaml`](models/roster.yaml) | Track 01's model list — single source of truth |
| [`scripts/`](scripts/) | Environment check, model pull, benchmarking (Track 01) |
| [`TODO.md`](TODO.md) | The working backlog — open questions and what's next to do |
| [`docs/ROADMAP.md`](docs/ROADMAP.md) | Track and module status, and specs for what's next |
| [`docs/STYLE.md`](docs/STYLE.md) | How this repo is written |
| [`docs/decisions/`](docs/decisions/) | Why things are the way they are |
| [`AGENTS.md`](AGENTS.md) | Instructions for AI agents working on this repo |

## Contributing

Field notes especially welcome — different hardware produces different numbers,
and that spread is information. Read [`docs/STYLE.md`](docs/STYLE.md) first; the
rule that matters most is **never invent a number**.

## License

[MIT](LICENSE)
