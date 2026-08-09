---
description: Scaffold a new curriculum module against the repo template
argument-hint: "<track> <number> <slug>   e.g. track-01-local-models 02 prompt-engineering"
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(ls*), Bash(uv run scripts/render-roster.py*)
---

Create a new module: **$ARGUMENTS**

## Steps

1. **Read [`docs/STYLE.md`](../../docs/STYLE.md) first.** It has the voice rules
   and the section template. Do not skip this — consistency across modules is
   the entire reason this command exists.

2. **Read [`docs/ROADMAP.md`](../../docs/ROADMAP.md)** for this module's spec.
   Most planned modules already have a thesis, a topic list, an exercise spine,
   and stated dependencies. Follow that spec; if you think it is wrong, say so
   and get agreement before diverging.

3. **Read the previous module** in the target track to match tone, depth, and
   pacing.

4. **Create `track-NN-slug/MM-slug/`** (module numbers restart per track) with:
   - `README.md` following the template exactly
   - `exercises/` if the module has hands-on work
   - `FIELD-NOTES.md` seeded with the standard header and left empty

5. **Update `docs/ROADMAP.md`** — flip the status to written and link it.

6. **Update the course maps** — for Track 01 that is the module list in
   `track-01-local-models/00-overview/README.md`; for every track, the track's
   `README.md` status section and the root `README.md` track listing must stay
   accurate.

7. **Re-render** if the module uses any generated block:
   ```bash
   uv run scripts/render-roster.py
   ```

## Requirements for the draft

- Every section of the template present, even if brief.
- The **"If you use a harness"** section is mandatory in Track 01 modules
  (Tracks 02 and 03 cover the commercial platforms directly). Map what the module
  teaches onto Claude Code / Codex / Copilot / Cursor. Describe mechanisms, link
  documentation, and never require the reader to own any of them.
- **No invented numbers.** No tokens/sec, no eval scores, no timings unless
  measured on a named machine or cited. Leave a blank and ship the script.
- **No hardcoded model names or tags.** Use a generated block.
- Exercises state their goal and how the reader knows it worked.
- Mark anything untested as untested.

## Then

Report what you created, what still needs the author's own input (field notes
and anything requiring a real run), and what you were unable to verify.

Do not fabricate field notes. `FIELD-NOTES.md` is for observations from a real
machine — leaving it empty is correct.
