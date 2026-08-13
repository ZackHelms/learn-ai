# learn-ai

A hands-on lab notebook for learning practical AI skills, organized into
**tracks**. Each track has its own premise and its own audience — pick the one
that matches where you are. Working more than one is fine; the overlap
reinforces rather than repeats.

This is a lab notebook, not a textbook. I am working through this material and
writing it down as I go, which means it includes the wrong turns.

## Start here

There is no required order. Pick a track by what you have — hardware, spend,
and how much you already know:

| If this is you | Start with |
|---|---|
| All I have is a phone, a tablet, or a locked-down work laptop | [Track 02 — Free tier](track-02-free-tier/) |
| I want a breadth-first lap over the big four platforms, at zero spend | [Track 02 — Free tier](track-02-free-tier/) |
| I already pay for Claude Pro (or I am deciding whether to) | [Track 03 — Claude Pro](track-03-claude-pro/) |
| I have a machine that runs Ubuntu, and I want to see how the machinery works | [Track 01 — Local models](track-01-local-models/) |
| I use a coding harness at work and want to know what it is actually doing | [Track 01 — Local models](track-01-local-models/) |
| I want to compare models with numbers instead of impressions | [Track 04 — Benchmark](track-04-benchmark/) |

Spend is stated per track and never creeps: Tracks 01 and 02 are zero, Track 03
assumes a Claude Pro subscription and nothing beyond it, Track 04's scorers are
free but running hosted candidates costs metered API.

### Track 01 on a fresh machine

Track 01 is the only track that needs a local setup. On a clean box:

```bash
git clone https://github.com/ZackHelms/learn-ai.git
cd learn-ai

# do this BEFORE downloading gigabytes
bash scripts/check-env.sh

# fix anything it flags, then:
curl -fsSL https://ollama.com/install.sh | sh   # native app on macOS instead
bash scripts/pull-roster.sh --dry-run           # see what it will fetch
bash scripts/pull-roster.sh
```

> **Expect the first pull to fail.** The model tags in `models/roster.yaml` were
> never confirmed against the live registry — see *Unverified tags* in
> [`TODO.md`](TODO.md#unverified-tags). A 404 means the roster is stale, not that
> you did something wrong; `scripts/pull-roster.sh` prints the three-step fix.

Then work through [Module 00 — Overview](track-01-local-models/00-overview/) and
[Module 01 — Local model lab](track-01-local-models/01-local-model-lab/),
recording what you get in its
[`FIELD-NOTES.md`](track-01-local-models/01-local-model-lab/FIELD-NOTES.md).

Tracks 02 and 03 need no clone at all — read them in the browser. Track 04 needs
this repo plus API keys only for the runs you choose to fire.

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

### [Track 04 — Benchmark](track-04-benchmark/)

**Measure models instead of vibing them.** A benchmark — a fixed collection of
evals plus a protocol — for comparing models, effort levels, and harnesses with
recorded runs instead of impressions. One eval is shipped with four model
families scored across five effort levels; four more cover long-horizon
coherence, repair, instruction following, and grounding.

All five evals are shipped and runnable:
[eval01 — Build Ashfall](track-04-benchmark/eval01-build-ashfall/) (sets 0–3
scored), [eval02 — Play Ashfall](track-04-benchmark/eval02-play-ashfall/),
[eval03 — Repair](track-04-benchmark/eval03-repair/),
[eval04 — Constraint stack](track-04-benchmark/eval04-constraint-stack/),
and [eval05 — Poisoned context](track-04-benchmark/eval05-poisoned-context/).

Later tracks may cover the base paid tiers of OpenAI, Gemini, and GitHub
Copilot — deferred, see the [roadmap](docs/ROADMAP.md).

## Layout

| Path | What |
|---|---|
| [`track-01-local-models/`](track-01-local-models/) | Track 01 — local models, built by hand |
| [`track-02-free-tier/`](track-02-free-tier/) | Track 02 — the big four platforms at zero spend |
| [`track-03-claude-pro/`](track-03-claude-pro/) | Track 03 — what the $20/month Claude tier unlocks |
| [`track-04-benchmark/`](track-04-benchmark/) | Track 04 — the benchmark: evals, protocol, recorded results |
| [`models/roster.yaml`](models/roster.yaml) | Track 01's model list — single source of truth |
| [`scripts/`](scripts/) | Environment check, model pull, benchmarking (Track 01) |
| [`docs/ROADMAP.md`](docs/ROADMAP.md) | Track and module status, and specs for what's next |
| [`docs/STYLE.md`](docs/STYLE.md) | How this repo is written |
| [`docs/decisions/`](docs/decisions/) | Why things are the way they are |
| [`TODO.md`](TODO.md) | Repo-wide backlog and a pointer index to the per-track ones |
| [`CHANGELOG.md`](CHANGELOG.md) | What has already landed |
| [`AGENTS.md`](AGENTS.md) | Instructions for AI agents working on this repo |

## Contributing

Field notes especially welcome — different hardware produces different numbers,
and that spread is information. Read [`docs/STYLE.md`](docs/STYLE.md) first; the
rule that matters most is **never invent a number**.

## License

[MIT](LICENSE)
