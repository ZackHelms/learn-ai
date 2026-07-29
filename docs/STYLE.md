# Style guide

This exists so that module 8, written a year from now, still reads like module 1.
It is aimed at both me and at any agent drafting content here.

## Voice

This repo is a **lab notebook**, not a textbook. I am learning this material as I
write it. That has consequences for how things get written:

- **First person, singular.** "I expected X, I got Y." Not "one might observe."
- **Say what actually happened**, including when it was dumb. The wrong turn is
  usually the most useful part of the page — it is the part the reader is about
  to take.
- **No false authority.** If I have not run it, the text says so. "I have not
  tested this on a Mac" is a perfectly good sentence.
- **No hype.** Not "revolutionary", "unlock", "supercharge", "game-changing".
  Describe what the thing does.
- **Short sentences beat clever ones.** The subject matter supplies the
  difficulty; the prose should not add more.
- **Second person for instructions.** "Run this", "you should see". The reader
  is doing the work, not watching me do it.

## Hard rules

These are not style preferences. Breaking them makes the repo wrong.

1. **Never invent a benchmark number.** Not tokens/sec, not memory, not latency,
   not an eval score. If a number is not from a cited source or from a run on a
   named machine, it does not go in. When in doubt, ship the script that
   measures it and leave the cell blank.
2. **Never hardcode a model name, tag, or size in prose.** `models/roster.yaml`
   is the single source of truth. Use a generated block (see below).
3. **Every command shown must have been run**, or be explicitly marked as
   untested. A command that does not work destroys trust in every other command
   on the page.
4. **Cite sources with a link and a date.** Model and tool facts rot within
   months. An uncited claim about a version is a future bug.
5. **No exercise depends on a paid harness or a hosted API key.** That is the
   whole premise. If something genuinely requires one, it is an optional aside
   clearly marked as such.

## Generated blocks

Anything derived from `models/roster.yaml` is injected between markers:

```markdown
<!-- BEGIN GENERATED: roster -->
<!-- END GENERATED: roster -->
```

Content between markers is **overwritten** — never hand-edit it. Regenerate with:

```bash
uv run scripts/render-roster.py          # write
uv run scripts/render-roster.py --check  # verify (exit 1 if stale)
uv run scripts/render-roster.py --list   # available block names
```

Available blocks: `roster`, `roster-why`, `roster-pull`, `roster-budget`,
`roster-provenance`.

## Module template

Every module README follows this order. Sections may be short; they should not
be missing, because a reader learns where to look once and then relies on it.

```markdown
# Module NN — Title

> One sentence on what this module is for.

## Why this module
The problem this solves, in my words. What was confusing before.

## What you'll be able to do
3–5 bullets, each a concrete capability, not a topic.

## Before you start
Prerequisites, prior modules, rough time, what will be downloaded.

## Concepts
The actual teaching. Prose and diagrams. No exercises here.

## Exercises
Numbered, hands-on. Each states its goal and how to know it worked.

## Check yourself
Concrete pass criteria. Ideally a command whose output the reader can compare.

## If you use a harness
How this maps to Claude Code / Codex / Copilot / Cursor. See below.

## Field notes
What surprised me. Honest, dated, first person.

## Further reading
Links with dates.
```

### The "If you use a harness" section

This section appears in **every** module, and it is load-bearing rather than
decorative.

The curriculum is harness-agnostic: nothing requires Claude Code, Codex, or
Copilot. But most readers arriving here already use one, and the material is far
more valuable if it explains what those tools are doing under the hood rather
than pretending they do not exist.

So each module ends by mapping what was just built by hand onto the equivalent
mechanism in the commercial harnesses. Built a tool loop? That is what the
harness's agent loop is. Wrote an instructions file? That is `CLAUDE.md` /
`AGENTS.md` / `.github/copilot-instructions.md`.

Rules for this section:

- Describe the **mechanism**, not the marketing.
- Do not claim a harness does something specific unless it is documented and
  linked. These products change monthly; an uncited claim will be wrong soon.
- Never require the reader to have the harness in order to follow along.

## Field notes

Each module has a `FIELD-NOTES.md` alongside it. That is where real measured
output goes — benchmark tables, eval scores, things that broke.

This separation is deliberate. The README is the teaching, which should stay
stable. Field notes are observations from a specific machine on a specific date,
which are only meaningful with that context attached. Keeping them apart means
the README does not slowly fill up with stale numbers.

Always record: the date, the hardware, and the model tags used.

## Formatting

- Wrap prose at roughly 88 characters.
- Fenced code blocks always carry a language (` ```bash `, ` ```python `).
- Show commands without a `$` prefix so they can be copied directly.
- When output matters, show it in its own block, labelled.
- Use relative links between repo files so they work on GitHub and locally.
- American spelling, Oxford comma.

## Commits

Conventional-commit style, present tense, scoped by area:

```
docs(module-01): add quantization exercise
feat(scripts): add --check mode to render-roster
fix(roster): correct granite tag after upstream retag
chore(deps): note MCP SDK 2.0 in roadmap
```
