# TODO

The repo-wide backlog, written to be **read cold** - assume no memory of the
session that produced it. Only two things live here: items that cut across every
track, and pointers to the per-track backlogs where the detailed work lives.

- *What the modules are* → [`docs/ROADMAP.md`](docs/ROADMAP.md)
- *What needs doing, per track* → the track's own `TODO.md`, linked below
- *What already landed* → [`CHANGELOG.md`](CHANGELOG.md)
- *How to get started as a reader* → [`README.md`](README.md#start-here)

**This file holds open work only.** When an item finishes, check it off here,
then fold it into a dated entry in [`CHANGELOG.md`](CHANGELOG.md) at the next
commit - one entry per significant feature or coherent set of items, not one per
edit. Same rule in the per-track backlogs, except a track with its own changelog
(Track 04) records the detail there and only the repo-level summary comes here.

---

## Where the backlog lives

| Track | Backlog | Status |
|---|---|---|
| 01 - Local models | [`track-01-local-models/TODO.md`](track-01-local-models/TODO.md) | decisions pending + empirical gates on module 01 |
| 02 - Free tier | none - status in [ROADMAP](docs/ROADMAP.md#track-02--free-tier) | module 01 being written live in a separate session (2026-08) |
| 03 - Claude Pro | none - candidates in [ROADMAP](docs/ROADMAP.md#track-03--claude-pro) | planned, nothing actionable yet |
| 04 - Benchmark | [`track-04-benchmark/TODO.md`](track-04-benchmark/TODO.md) | all five evals shipped; open follow-ups and a run matrix waiting on Zack |

---

## Repo-wide maintenance

- [ ] **Clear the `tag_verified: false` flags.** Run `/update-models` from a
      machine with network access. Note the likely failure mode: fixing only the
      one tag that blocked you and leaving the other five stale.
- [ ] **Test the macOS paths.** Native Ollama on macOS, and Ubuntu-on-Apple-
      Silicon. Both are currently documented as untested - honest, but untested.
- [ ] **CI** - `render-roster.py --check` plus a link check on PR. Waiting until
      `/verify-docs` has proven itself locally.
- [ ] **Scheduled freshness check** - monthly job running the `freshness-auditor`
      subagent, opening an issue when the roster drifts.

---

## State to carry forward

Context that would otherwise be lost. Nothing here is urgent; all of it is the
kind of thing that wastes an hour if forgotten.

### Unverified tags

`models/roster.yaml` entries all carry `tag_verified: false`. Model **families,
sizes, licenses, and tool-calling support were verified** against vendor
announcements and model cards. The **exact Ollama tag strings were not**, because
the authoring environment could not reach `ollama.com`.

Rationale in [ADR 0005](docs/decisions/0005-unverified-tags.md). Short version:
guessing silently would have been worse, since a reader hitting a 404 could not
tell whether they broke something or the repo was wrong.

`disk_gb` and `min_ram_gb` are likewise **estimates**, labeled as such in the
roster's `provenance:` block. `scripts/bench.py` produces real numbers.

### Network policy in Claude Code web sessions

Web sessions apply an environment network policy that **403s `ollama.com`,
`registry.ollama.ai`, and `huggingface.co`** at the proxy. pypi and npm are
reachable.

So `/update-models` and the `freshness-auditor` subagent must run from a local
session, or those hosts need adding to the environment's allowed list - see
<https://code.claude.com/docs/en/claude-code-on-the-web>. The symptom is HTTP
403, not a DNS failure; don't mistake it for a dead link.

### What is actually verified in this repo

Worth being precise about, since the repo's central rule is *never invent a
number*.

**Run and confirmed working:** `check-env.sh` (on Ubuntu 24.04, 15 GB, 4 cores,
AVX-512), `render-roster.py` including `--check` idempotency, `bench.py` argument
and error paths, `pull-roster.sh` roster parsing, the structured-output
exercise's grading logic against handcrafted cases, all relative links and
anchors.

**Never run:** anything requiring a model. No model was pulled, loaded, or
benchmarked. That is why Track 01 ships **zero performance figures** - it ships
`scripts/bench.py` and an empty `FIELD-NOTES.md` instead.

The macOS instructions and the llama.cpp appendix are likewise unverified and
marked as such in the text. (Track 04 is the exception on model runs: its
RESULTS files record real model runs with real costs.)
