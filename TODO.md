# TODO

The working backlog, written to be **read cold** - assume no memory of the
session that produced the repo. This root file is a quick read: repo-wide items
plus pointers to the per-track backlogs. Each active track keeps its own
`TODO.md` with the details. [`docs/ROADMAP.md`](docs/ROADMAP.md) covers *what
the modules are*; the TODO files cover *what needs doing*.

---

## Start here on a fresh machine

```bash
git clone https://github.com/ZackHelms/learn-ai.git
cd learn-ai

bash scripts/check-env.sh          # do this BEFORE downloading gigabytes
```

Fix anything it flags, then:

```bash
curl -fsSL https://ollama.com/install.sh | sh   # native app on macOS instead
bash scripts/pull-roster.sh --dry-run           # see what it will fetch
bash scripts/pull-roster.sh
```

> **Expect the first pull to fail.** The model tags in `models/roster.yaml` were
> never confirmed against the live registry - see *Unverified tags* below. A 404
> means the roster is stale, not that you did something wrong.
> `scripts/pull-roster.sh` prints the three-step fix.

Then work through [Track 01, Module 01](track-01-local-models/01-local-model-lab/)
and record what you get in its
[`FIELD-NOTES.md`](track-01-local-models/01-local-model-lab/FIELD-NOTES.md).

---

## Where the backlog lives

| Track | Backlog | Status |
|---|---|---|
| 01 - Local models | [`track-01-local-models/TODO.md`](track-01-local-models/TODO.md) | decisions pending + empirical gates on module 01 |
| 02 - Free tier | none - status in [ROADMAP](docs/ROADMAP.md#track-02--free-tier) | module 01 being written live in a separate session (2026-08) |
| 03 - Claude Pro | none - candidates in [ROADMAP](docs/ROADMAP.md#track-03--claude-pro) | planned, nothing actionable yet |
| 04 - Benchmark | [`track-04-benchmark/TODO.md`](track-04-benchmark/TODO.md) | **in progress** - eval02-05 being built; details and open questions there |

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
benchmarked. That is why the repo ships **zero performance figures** - it ships
`scripts/bench.py` and an empty `FIELD-NOTES.md` instead.

The macOS instructions and the llama.cpp appendix are likewise unverified and
marked as such in the text. (Track 04 is the exception on model runs: its
RESULTS files record real model runs with real costs.)

---

## Done

- Per-track TODO split: root TODO became repo-wide items + pointers;
  Track 01 and Track 04 carry their own backlogs, 2026-08-12
- Track 04 (benchmark): `eval01/` moved to
  `track-04-benchmark/eval01-build-ashfall/` with history
  ([ADR 0007](docs/decisions/0007-benchmark-track.md)), eval02-05 specced in
  ROADMAP, reference artifact frozen from run u35, 2026-08-12
- Track restructure: top-level `track-NN-slug/` layout, tracks 01-03
  ([ADR 0006](docs/decisions/0006-tracks-top-level.md)), 2026-08-08
- Modules 00 (overview) and 01 (local model lab), with exercises
- `models/roster.yaml` as single source of truth, with generated-block rendering
- `scripts/`: `check-env.sh`, `pull-roster.sh`, `bench.py`, `render-roster.py`
- `AGENTS.md` + `CLAUDE.md`, `.claude/` commands and subagents
- `docs/`: `STYLE.md`, `ROADMAP.md`, five ADRs
