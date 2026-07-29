---
description: Check docs for stale generated blocks, broken links, and untested commands
allowed-tools: Read, Grep, Glob, Bash(uv run scripts/render-roster.py*), Bash(shellcheck*), Bash(bash -n*), Bash(ls*), Bash(git status*)
---

Audit the repo's documentation for the failure modes that actually bite here.

## Checks

### 1. Generated-block drift

```bash
uv run scripts/render-roster.py --check
```

Must exit 0. If it fails, the docs disagree with `models/roster.yaml` — the fix
is to run the renderer without `--check`, never to hand-edit the block.

### 2. Hardcoded model references in prose

Grep the modules for model names, tags, and sizes appearing **outside**
generated blocks. Look for family names (`granite`, `gemma`, `phi`, `llama`,
`gpt-oss`), tag-shaped strings (`something:3b`), and parameter counts (`8B`,
`350M`).

Findings inside `<!-- BEGIN GENERATED -->` markers are fine. Findings outside
them violate the rule in [`AGENTS.md`](../../AGENTS.md) — report file and line.

Some prose legitimately names a model when discussing it conceptually. Use
judgement: a *tag* or a *size* in prose is a bug; "IBM's Granite family" in a
sentence about vendors is not.

### 3. Shell blocks

Extract every ```bash block from the modules and syntax-check it:

```bash
bash -n <<< "$block"
```

Also run `shellcheck` over `scripts/*.sh` if available. Report syntax errors and
anything referencing a path that does not exist in the repo.

### 4. Links

Check every relative markdown link resolves to a real file. Relative links are
used throughout so they work both on GitHub and locally — a broken one is
usually a moved file.

List external links with their context so they can be spot-checked, but do not
fetch them; that is the `freshness-auditor`'s job.

### 5. Module template conformance

For each `modules/*/README.md`, confirm the sections from
[`docs/STYLE.md`](../../docs/STYLE.md) are present, especially:

- **If you use a harness** — mandatory in every module
- **Field notes**
- **Check yourself**

Report missing sections.

### 6. Unsourced numbers

Grep for number-shaped claims — `tok/s`, `tokens/sec`, `GB`, `ms`, `%` — and
check each is either inside a generated block, attributed to a named machine, or
carries a citation. **Flag anything that reads like a benchmark result with no
provenance.** This is the repo's most important rule and the easiest to break by
accident.

## Report

Group findings by severity:

- **Broken** — stale generated blocks, failing shell syntax, dead relative links
- **Rule violations** — hardcoded models in prose, unsourced numbers, missing
  mandatory sections
- **Worth a look** — external links to spot-check, prose that names a model in a
  way that may or may not be intentional

Give file and line for everything. Do not fix anything without saying what you
are about to change first.
