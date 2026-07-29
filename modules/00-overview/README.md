# Module 00 — Overview

> What this course is, why it uses deliberately weak models, and what you need
> before starting.

## Why this module

I kept using agentic coding tools and not really knowing what they were doing.
Not in a vague way — in a specific way. When an agent got something wrong, I
could not tell whether the problem was my prompt, the tool description, the
context it had been given, or the model itself. Every one of those has a
different fix, and I could not distinguish them.

That is the gap this course tries to close. The method is to build the pieces by
hand, on models small enough to run on an ordinary laptop, and watch what breaks.

## The premise: small, dumb models are better teaching tools

This is the one idea that shapes everything else, so it goes first.

The models in this course are deliberately weak. Not "small but surprisingly
capable" — genuinely limited. The smallest one on the roster will fail most
tasks you give it.

That is the point.

A frontier model is *forgiving*. Give it a vague prompt, a badly described tool,
or no examples, and it will often succeed anyway by inferring what you meant.
That is excellent when you are trying to get work done and useless when you are
trying to learn, because **you cannot tell which parts of your setup were
load-bearing.** Everything works, so nothing taught you anything.

A 3B model is not forgiving. Vague prompt, and it does the wrong thing. Sloppy
tool schema, and it calls the tool with garbage arguments. No examples, and the
output format drifts every run. Each failure points directly at its cause.

There is a second reason, which shows up in module 03. Evals are only
informative when there is *spread*. If every model passes everything, your eval
set has told you nothing. A ladder of weak models produces real spread and
therefore real signal.

So: **speed and small footprint outrank intelligence** in the model roster. And
the roster is a ladder rather than a leaderboard — the bottom rung is there to
fail, and the top rung is there so that "working agent" stays reachable.

## What you'll be able to do

By the end of the course:

- Run several local models on ordinary hardware and know which one to reach for
- Write prompts that work on a model that cannot cover for you
- Build eval sets that catch regressions — unit tests that tolerate
  non-determinism
- Write an agent loop from scratch and explain what every line does
- Decide what belongs in context, what belongs in a script, and what belongs in
  code
- Recognize what Claude Code, Codex, and Copilot are doing under the hood, and
  make an informed call about when a local model is the right tool

## The modules

| # | Module | What it's for |
|---|---|---|
| **00** | **Overview** ← you are here | The premise, prerequisites, and the map |
| **01** | [Local model lab](../01-local-model-lab/) | Get models running and learn what your hardware can actually do |
| 02 | Prompt engineering | What actually moves the needle when the model can't cover for you |
| 03 | Evals | Unit tests for AI: same idea, but the assertion is statistical |
| 04 | Tool calling & the agent loop | An agent is a while-loop around a model that can call functions — write one |
| 05 | Context engineering | Context is a budget, not a bucket; and most of it should be a script |
| 06 | Harness teardown | What the commercial tools do, now that you've built the pieces yourself |
| 07 | MCP | Tools as a protocol rather than per-app code |
| 08 | SDK agents | When code beats context, and how to convert |
| 09 | Hybrid & routing | Local and frontier together: cost, latency, privacy |

Modules 00 and 01 are written. The rest are specced in
[`docs/ROADMAP.md`](../../docs/ROADMAP.md), which also explains two ordering
decisions worth knowing about: **evals come early**, and **the agent loop gets
its own module**.

There are no empty placeholder folders. A module shows up on disk when it has
something in it.

### On evals being "unit tests for AI"

Since this framing recurs: an eval is a test that pins behavior so a change
which breaks it becomes visible. Same purpose as a unit test. The difference is
that the assertion has to tolerate non-determinism — you are usually asserting
that a property holds, or that a score clears a threshold across several runs,
rather than that output equals a fixed string. Everything else about how you
think about tests carries over, including that they are worth writing early and
that a test suite which always passes is not doing its job.

## Prerequisites

### Hardware

<!-- BEGIN GENERATED: roster-budget -->
- **Total RAM assumed:** 16 GB
- **Usable for a model:** ~10 GB (after OS, editor and a browser — this is the number that actually binds)
- **Disk for the core roster:** ~11.3 GB (5 models); budget 20 GB to be comfortable
- **Largest core model:** IBM Granite 4.1 8B at ~8.0 GB resident
<!-- END GENERATED: roster-budget -->

No GPU required. Everything in this course runs on CPU. If you have a GPU,
things will simply be faster; nothing depends on it.

### Software

**Ubuntu 24.04 LTS or later** is the reference platform. Every command here is
written and tested against it.

You can get there three ways:

| Path | Notes |
|---|---|
| **Native Linux** | The straightforward case. |
| **Windows + WSL2** | Works well. `wsl --install -d Ubuntu-24.04`. See the note below about the memory cap. |
| **macOS** | Read the next section before you do anything. |

You will also need `curl`, `git`, and [`uv`](https://docs.astral.sh/uv/) for the
Python exercises. Module 01 covers installing what is missing.

> **A note on Ubuntu 24.04 and `pip`.** Ubuntu 24.04 marks its system Python as
> externally managed ([PEP 668](https://peps.python.org/pep-0668/)), so a bare
> `pip install` outside a virtualenv will refuse to run. This surprises people.
> The course uses `uv`, which sidesteps it entirely.

### On WSL2 and memory

WSL2 does not give the guest all of your host's RAM by default. If the memory
check in module 01 reports less than you expect, that is why. Create or edit
`%USERPROFILE%\.wslconfig`:

```ini
[wsl2]
memory=12GB
```

Then run `wsl --shutdown` from PowerShell to apply it.

### If you are on a Mac

Be careful here. This is the one prerequisite I would push back on if someone
told me it was fine, so I want to be direct about it.

**Running Ubuntu in a VM or container on a Mac is not equivalent to running it
on a PC.** Two things go wrong:

1. **You lose GPU acceleration entirely.** A Linux guest on macOS has no access
   to Metal. On Apple Silicon especially, native inference benefits from unified
   memory and the GPU; inside a Linux VM you get neither. The same Mac will be
   meaningfully slower running a model in a VM than running it natively.

2. **The emulation trap.** If you pull an `amd64` Linux image onto an Apple
   Silicon Mac, it runs under emulation. Inference then becomes *catastrophically*
   slow — not "a bit disappointing," but slow enough that you would reasonably
   conclude local models are useless. The symptom looks like a verdict on the
   technology rather than a misconfiguration, which is what makes it dangerous.

   `scripts/check-env.sh` in module 01 detects this specific case and tells you.

**My recommendation for Mac users:** install Ollama natively on macOS rather
than running Linux. Ollama has a native macOS build. The exercises are almost
entirely `curl` and Python, both of which work fine on macOS. The differences
are in module 01's install step, and only there.

If you would rather stay on Ubuntu for consistency with the text, that works —
just use an **arm64** image on Apple Silicon, allocate as much RAM as you can,
and expect lower throughput than the same machine running natively.

I have not personally tested the macOS paths. That is exactly the kind of thing
that goes in field notes, and if you try it, I would like to know how it went.

## How to use this repo

```
modules/NN-name/README.md      the teaching
modules/NN-name/exercises/     hands-on work
modules/NN-name/FIELD-NOTES.md real measured results — yours go here
models/roster.yaml             the model list (single source of truth)
scripts/                       environment check, model pull, benchmark
docs/                          style guide, roadmap, decision records
```

Work through modules in order; each builds on the last. Do the exercises — this
material does not transfer by reading.

**Fill in the field notes.** Every module has a `FIELD-NOTES.md`. Benchmark
numbers only mean something next to the machine that produced them, so the repo
ships no performance figures of its own — it ships the scripts that measure them
on your hardware. The gap between what you get and what someone else gets is
information, not noise.

## A note on what is and isn't verified here

The models in the roster were checked against vendor announcements and model
cards. The **exact Ollama tag strings were not** — the environment this was
written in could not reach `ollama.com`. Those entries are flagged
`tag_verified: false`, and there is a
[decision record](../../docs/decisions/0005-unverified-tags.md) explaining why
they shipped that way rather than being guessed at silently.

Practically: if `ollama pull` 404s on something, the roster is stale rather than
you being wrong. `scripts/pull-roster.sh` tells you how to fix it.

I would rather flag uncertainty than have you debug my confident mistake.

## If you use a harness

If you already use Claude Code, GitHub Copilot, OpenAI Codex, or Cursor, none of
this course requires them — but essentially all of it applies to them.

Those tools are an agent loop, a context assembly strategy, a tool set, and a
model, wrapped in a good interface. This course builds each of those pieces by
hand at small scale. The goal is that by module 06 you are recognizing things
rather than learning them.

Every module ends with a section like this one, mapping what you just built onto
the equivalent mechanism in the commercial tools. You do not need to own any of
them to follow along.

The one place this repo *does* use a harness is its own authoring tooling —
`.claude/` holds commands for maintaining the curriculum. That is not part of
the course, and the curriculum has no dependency on it. See
[ADR 0004](../../docs/decisions/0004-agents-md-source-of-truth.md) for how that
tension gets resolved.

## Field notes

_Observations go here as the course gets written and re-run. Include the date
and hardware._

**2026-07-29 — Starting out.** Wrote this module before running any of the
later ones, which means the module list will move as reality intervenes. That
is expected; the roadmap is a plan, not a promise.

The two things I am least sure about right now: whether the smallest models are
*too* weak to be interesting rather than usefully bad, and whether tool calling
at these sizes is reliable enough for module 04 to work as designed. Both are
empirical questions I cannot answer from the armchair.

## Further reading

- [`docs/ROADMAP.md`](../../docs/ROADMAP.md) — module specs and ordering decisions
- [`docs/STYLE.md`](../../docs/STYLE.md) — how this repo is written
- [`docs/decisions/`](../../docs/decisions/) — why things are the way they are
- [PEP 668](https://peps.python.org/pep-0668/) — the Ubuntu `pip` behavior
- [uv documentation](https://docs.astral.sh/uv/)

---

Next: [Module 01 — Local model lab](../01-local-model-lab/)
