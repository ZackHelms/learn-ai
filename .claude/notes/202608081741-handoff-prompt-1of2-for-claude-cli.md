# Handoff: learn-ai track restructure

## Who and where

I am Zack. This repo is `learn-ai`, remote https://github.com/ZackHelms/learn-ai. You are running in WSL2/Ubuntu 24.04 with native git and full filesystem access.

**My preferences:** concise responses; plain ASCII only (straight quotes, plain hyphens, no curly quotes, no en/em dashes); label anything that is inference, assumption, or sourced ("inferred:", "assumed:", "source: X").

## Scope of this session

**Track restructure only.** Do not write module content. A separate session is handling Track 2 Module 01.

## Read before proposing anything

- `AGENTS.md`
- `docs/STYLE.md`
- `docs/ROADMAP.md`
- `TODO.md`
- `README.md`
- `models/roster.yaml`

The rules that matter most: never invent a number; never hardcode a model name, tag, or size in prose (use `models/roster.yaml` plus generated blocks); cite and date capability claims; every command shown must have been run or be explicitly marked untested.

## The decision already made

The repo's current premise is "local weak models + harness-agnostic." That does not fit the modules I want to build next. Reorganize repo-wide into tracks:

- **Track 1** - premise: *local weak models + harness-agnostic*. Contains the existing modules 00 (Overview) and 01 (Local model lab). **Move it, do not rewrite it.** No content changes to these modules beyond what is mechanically required by the move (path references, relative links).
- **Track 2** - premise: *what can I do in the free tier?* Scaffolding only this session. Module 01 will walk through free-tier Gemini, Microsoft Copilot, OpenAI ChatGPT/Codex, and Anthropic Claude, across VSCode/WSL2, desktop app, and web.
- **Track 3** - premise: *what can I do with Claude Pro at $20/month?* Scaffolding only. Would cover Claude desktop app, mobile app, VSCode, web app, Claude Design.
- Later tracks may cover base paid tiers for OpenAI, Gemini, GitHub Copilot. Deferred. Do not create scaffolding for these; mention them in the roadmap as deferred only.

Modules 02-09 are currently specced in `docs/ROADMAP.md` under the old flat layout. Part of your job is proposing where each lands.

## What I want you to produce, in order

**1. A restructure plan for my explicit approval. Move no files until I approve it.**

The plan must cover:

- Proposed directory layout. Current is `modules/NN-slug/`. Propose the track-aware replacement and justify the naming. Consider whether module numbers restart per track and what that costs in link stability.
- A complete inventory of every file that references the current layout. Grep for `modules/`, relative links between modules, and any path references in `README.md`, `docs/ROADMAP.md`, `AGENTS.md`, `TODO.md`, scripts, CI config, and generated-block tooling.
- The exact `git mv` sequence, so history is preserved. Do not delete-and-recreate.
- Where each of the specced modules 02-09 lands, per track. Flag any that do not fit cleanly, rather than forcing them.
- What `AGENTS.md` needs to say about tracks so future sessions do not regress the structure.
- Anything in the plan you are uncertain about, called out explicitly rather than decided silently.

**2. After I approve: execute on a branch.** Not on main. Show me the diff before any commit.

## Constraints

- Preserve git history on every move.
- Every internal link must still resolve after the move. Verify, do not assume.
- Do not rewrite Track 1 prose.
- If the repo has link-checking or generated-block tooling, run it and paste real output. If it does not, say so rather than claiming links were verified.

## Start by

Confirming you can read the repo and run git in it, then reading the files listed above. Then give me the plan.
