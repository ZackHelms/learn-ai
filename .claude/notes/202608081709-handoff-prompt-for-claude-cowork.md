# Handoff: learn-ai Track 2, Module 01

Paste this as the first message of a new Cowork task running **on my computer**.

---

## Context you are inheriting

I am continuing work started in a cloud Cowork session. Read this whole brief before acting.

**Me:** Zack. Windows 11 host, VSCode with WSL2 / Ubuntu 24.04 open on the right side of my screen. My repo `learn-ai` lives inside WSL2 (not on the Windows filesystem - `C:\Users\zmhel\gitrepos` is empty). Remote: https://github.com/ZackHelms/learn-ai

**My preferences:** concise responses; plain ASCII only (straight quotes, plain hyphens - no curly quotes, no en/em dashes); label anything that is inference, assumption, or sourced ("inferred:", "assumed:", "source: X").

## The project

`learn-ai` is a personal learning repo built so others could use it later - my brother, my kids, my coworkers. Modules 00 (Overview) and 01 (Local model lab) are written; 02-09 are specced in `docs/ROADMAP.md`.

**Read these before writing anything:** `AGENTS.md`, `docs/STYLE.md`, `docs/ROADMAP.md`, `TODO.md`. The rules that matter most: never invent a number; never hardcode a model name/tag/size in prose (use `models/roster.yaml` + generated blocks); cite and date capability claims; every command shown must have been run or be explicitly marked untested.

## Decision made: restructure into tracks

The repo's current premise is "local weak models + harness-agnostic", which does not fit the module I want to build now. We agreed to reorganize repo-wide into tracks:

- **Track 1** - premise: *local weak models + harness-agnostic*. Contains existing modules 00 and 01. **I do not want to work on this track right now** - move it, do not rewrite it.
- **Track 2** - premise: *what can I do in the free tier?* This is what I am building today.
- **Track 3** - premise: *what can I do with Claude Pro at $20/month?* Would cover Claude desktop app, mobile app, VSCode, web app, Claude Design, and whatever else exists. Reinforces concepts from other tracks, or is a fresh starting point for someone. Not today.
- Later tracks may cover base paid tiers for OpenAI, Gemini, GitHub Copilot - deferred until I have a real need. (GitHub Copilot is what we use at work so it may come sooner; Gemini is interesting for its multimodal audio/video/image tooling.)

The track restructure needs to happen first, and needs a plan I approve before files move - README.md, docs/ROADMAP.md, AGENTS.md, and internal links all reference the current `modules/NN-slug/` layout.

## Today's goal: Track 2, Module 01

Walk me through using the **free versions** of the top four AI platforms:

1. Google Gemini
2. Microsoft Copilot
3. OpenAI ChatGPT / Codex
4. Anthropic Claude - **do this one last**, so we work the kinks out of the module format on the others first

For each platform, cover all three access modes:

- **VSCode with WSL2/Ubuntu** (my primary environment - this is the priority)
- **Rich client / desktop app**
- **Web**

With commentary on how the three modes differ in what the AI can actually do **for free**, and on whether running one, two, or all of them at once is useful - **only if that is actually true**, do not manufacture a benefit.

**Strictly free.** The module must work with zero spend. Anything paid is mentioned only as "here is what upgrading unlocks". This is written for people who will not pay.

**Mode: live walkthrough, doc written as we go.** Do not go away and write a finished module. We do each step together in real time, I try it, and the module records what actually happened - including the failures. This matches the repo's lab-notebook voice and means every command in it has been run. Use computer use if it is available in this session; otherwise tell me and I will drive and paste output.

## Findings already established - do not re-derive

**There is no free tier of Claude Code.** Anthropic's docs: "Claude Code requires a Pro, Max, Team, Enterprise, or Console account. The free Claude.ai plan does not include Claude Code access."
source: https://code.claude.com/docs/en/setup (checked 2026-08-08)

This kills my earlier plan of making a free-tier Claude Code account under a separate email. More usefully, it is the sharpest finding in the module: **Claude is the only one of the four platforms with no free path into VSCode/WSL2**, while Gemini, Copilot, and Codex each have some free CLI or extension story. That asymmetry deserves its own section. The free Claude story is web + desktop app + mobile only - verify what that actually includes before writing it.

**Still to verify at write time** (all of these rot fast, cite and date every one):
- Gemini CLI free tier - what it includes, what the limits are, install path on Ubuntu 24.04
- GitHub Copilot free tier - completion and chat limits, VSCode extension behavior under WSL2
- OpenAI Codex free access - whether the CLI/extension works without a paid ChatGPT plan at all
- What each vendor's desktop app does that the web version does not, on free

## What I want from you first

1. Confirm you can read the repo and run git in it.
2. Read `AGENTS.md` and `docs/STYLE.md`.
3. Propose the track restructure plan for my approval before moving any files.
4. Then start the live walkthrough with Gemini.
