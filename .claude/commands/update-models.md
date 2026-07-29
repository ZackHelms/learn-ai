---
description: Check the model roster against upstream, propose updates, re-render docs
argument-hint: "[model-id]  (optional; default: whole roster)"
allowed-tools: Read, Edit, Grep, Glob, WebFetch, WebSearch, Bash(uv run scripts/render-roster.py*), Bash(ollama list*), Bash(ollama show*), Bash(git diff*), Bash(git status*)
---

Refresh `models/roster.yaml` against what is actually available upstream, then
regenerate every derived table.

Target: **$1** (empty means the whole roster).

## Why this command exists

Model tags rot. Vendors retag, deprecate, and rename constantly, and a stale
roster shows up as a confusing 404 on `ollama pull` — which reads to a learner
like *they* did something wrong. This command makes refreshing a bounded,
reviewable operation instead of a hunt through prose.

## What you may change

- `models/roster.yaml` — the only file where model facts live.
- Generated blocks, but only by running the renderer. Never by hand.

## What you must not change

- **Prose in any module.** If updating a model requires editing prose, that
  prose is violating the no-hardcoded-models rule — report it as a bug instead
  of working around it.
- **The roster's shape.** This is a pedagogical ladder, not a leaderboard. Do
  not swap a model for a better-benchmarking one just because it scores higher.
  Each rung exists for a reason recorded in its `why:` field. Rung 0 is
  *supposed* to be bad.
- **The non-Chinese constraint** ([ADR 0002](../../docs/decisions/0002-non-chinese-roster.md)).
  Excludes Qwen, DeepSeek, GLM, Yi, InternLM, Kimi, MiniMax, Baichuan. If a
  newly released model is excellent and Chinese, note it in your report and move
  on — do not add it.
- **The memory budget** ([ADR 0001](../../docs/decisions/0001-cpu-only-16gb.md)).
  Nothing that cannot run in ~10 GB usable RAM joins the core roster.

## Steps

1. **Read `models/roster.yaml`.** Note the current `roster_last_verified` date
   and which entries have `tag_verified: false`. Prioritize those — they have
   never been confirmed against the registry at all.

2. **Check what is installed locally**, if Ollama is running:
   ```bash
   ollama list
   ```
   A tag present locally is confirmed to exist. Set `tag_verified: true` for it.

3. **For each target model, verify against upstream.** Fetch the Ollama library
   page for the family (`https://ollama.com/library/<name>/tags`) and the
   vendor's model card. Confirm:
   - the tag string resolves,
   - the parameter count and quantization,
   - the license,
   - whether tool calling is native,
   - whether a newer point release of the *same family* exists.

   Prefer vendor announcements and Hugging Face model cards over blog roundups.
   A large amount of "best local models" content is SEO filler with invented
   version numbers — do not treat it as a source.

4. **If network access fails with HTTP 403**, stop and say so plainly. That is
   an environment network policy, not a missing model. Report which hosts were
   blocked and point at
   <https://code.claude.com/docs/en/claude-code-on-the-web>. Do not guess tags
   to fill the gap — guessing is what created
   [ADR 0005](../../docs/decisions/0005-unverified-tags.md).

5. **Propose edits before making them.** Show a table: model, field, current
   value, proposed value, source URL. Wait for confirmation on anything beyond
   a tag correction or a `tag_verified` flip.

6. **Apply confirmed edits** to `models/roster.yaml`. For each entry you
   actually verified, set `tag_verified: true`. Update the top-level
   `roster_last_verified` to today only if you checked the whole roster.

7. **Re-render:**
   ```bash
   uv run scripts/render-roster.py
   uv run scripts/render-roster.py --check
   ```
   The second must exit 0.

8. **Show the diff** and summarize: what changed, what stayed, what could not be
   verified and why. Explicitly list anything still `tag_verified: false`.

## Report format

End with:

- **Verified:** models confirmed unchanged.
- **Updated:** what changed, with source links.
- **Needs attention:** deprecated tags, models that no longer fit the budget,
  new releases worth considering (with the rung they would fill and what they
  would displace).
- **Could not verify:** which, and why.

Do not claim a model was verified unless you actually fetched a source for it.
