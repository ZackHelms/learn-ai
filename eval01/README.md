# eval01 - Ashfall Outpost, a one-prompt LLM eval

## Description
One task, one prompt, one shot: the model under test gets [`make-game-ashfall-outpost.prompt.md`]
(make-game-ashfall-outpost.prompt.md) and must produce a complete, playable, self-contained HTML 
game in a single reply. The output is scored out of 100: 
- **54 points, deterministic** - measured by [`eval_ashfall.py`](eval_ashfall.py) with no model
  in the loop (rubric categories A-E).
- **46 points, model-graded** - an LLM judge reads the code and scores it against
  [`GRADER_PROMPT.md`](GRADER_PROMPT.md) (rubric categories F-G).

[`RUBRIC.md`](RUBRIC.md) defines every point. [`RESULTS.md`](RESULTS.md) is the scoreboard. 
Candidate outputs and their score files live in `runs/`.

Hence the directory name: strictly speaking this is an **eval** (one task, graded against a rubric), 
not a benchmark (a standardized suite of many such tasks). See the glossary at the bottom.

**Why this task**:
A one-shot game build is a capacity probe: it forces long coherent code generation, strict
instruction following (banned APIs, seeded randomness), and cross-system design - and weak
models fail it in visibly different ways at every level. The deterministic half catches
"did not follow instructions" and "does not run"; the judged half catches "thirteen systems
that never talk to each other," which is where mid models separate from strong ones.

## Protocol - run one candidate

### 1. Generate

1. Pick a harness (claude.ai web, ChatGPT app, gemini CLI, Claude Code, ...), a model, and a
   reasoning-effort level if the harness exposes one.
2. Record the start datetime: `date +"%Y-%m-%d_%H:%M:%S_%Z"`.
3. Paste the prompt **verbatim** into a fresh session: make-game-ashfall-outpost.prompt.md
   One shot only: no follow-ups, no "continue", no fixing. If the reply truncates mid-file,
   that IS the result - truncation is a capability signal, score it as-is.
4. `mv ashfalloutpost.html runs/${model}-${runid}.html` (e.g. `runs/haiku-4-5-low-001.html`)
5. Record cost signal the harness exposes (tokens, credits, percent of quota) in [RESULTS.md](RESULTS.md)

### 2. Score - deterministic half

```bash
# static checks only: stdlib, no dependencies, safe on untrusted output
python3 eval_ashfall.py runs/<candidate>.html

# static + runtime checks (headless Chromium; needed for the full 54 points)
python3 eval_ashfall.py runs/<candidate>.html --runtime
```

The runtime pass needs Playwright. On Ubuntu 24.04 a bare `pip install` fails (PEP 668,
externally-managed Python), so use a venv:

```bash
python3 -m venv ~/.venvs/eval && ~/.venvs/eval/bin/pip install playwright
~/.venvs/eval/bin/playwright install chromium
~/.venvs/eval/bin/python3 eval_ashfall.py runs/<candidate>.html --runtime
```

(`uv run eval_ashfall.py ... --runtime` also resolves playwright via the script's inline
metadata, but you still need `playwright install chromium` once for the browser itself.)

A static-only run reports `scored_out_of` below 100. Never compare a static-only score
against a runtime-scored one without noting that.

### 3. Score - model-graded half

1. Open a **fresh** session with your grader model (see grader rules below).
2. Paste the entire contents of `GRADER_PROMPT.md`, then the candidate HTML underneath it.
   In an agentic harness you can instead say "the candidate is at <path>" and let it read
   the file.
3. Grade blind where possible: strip the filename and any header comment naming the authoring
   model before pasting.
4. Do NOT show the grader the deterministic results - they anchor its judgment.
5. Save the grader's **entire reply** to `runs/<candidate>.ai.json`. The merge step extracts
   the last JSON object and tolerates surrounding prose and markdown fences.

#### Scripted grading (recommended when the grader is Claude)

[`grade.sh`](grade.sh) runs the whole step with headless Claude Code (`claude -p`), using
whatever account `claude` is logged in as. The grader gets **no tools** and receives
GRADER_PROMPT.md plus the candidate HTML on stdin, so it *cannot* peek at scores (rule 11),
cannot delegate to a subagent (rule 13), and never sees the candidate's filename - stronger
blinding than an agentic session. Each job runs from an empty temp directory, so no
CLAUDE.md, project settings, or session memory leak into the grader's context.

```bash
./grade.sh -s b runs/r01.html      # one candidate -> runs/r01b.ai.json
./grade.sh -s c -j 5 runs/r0*.html # all candidates, 5 in parallel -> runs/r0Nc.ai.json
./grade.sh -m claude-opus-5 -e xhigh -s o runs/r01.html   # different judge, suffix "o"
```

The `-s` suffix labels repeat gradings (`r01a`, `r01b`, ...): same grader twice measures
grader variance; two different graders measure inter-rater agreement (glossary below).
Parallel jobs share nothing except the server-side prompt cache, which reuses identical
prefix tokens for speed/cost and cannot carry content between jobs.

If you grade in an **interactive** agent session instead, use a fresh session that has not
explored the repo, and lead with read discipline:

> Read ONLY these two files, in this order: `eval01/GRADER_PROMPT.md` then
> `eval01/runs/r01.html`. No directory listings, no other files, no commands, no
> subagents - do the grading yourself in this session. Then follow GRADER_PROMPT.md and
> write your full reply verbatim to `eval01/runs/r01b.ai.json`.

Grader-prompt version: **v1.3** (2026-08-09: added rules 13-14 - never delegate, declare
contamination - and the `contamination` output field). Record the version in the RESULTS.md
Grader column; a prompt edit is a grader change (see rules below).

### 4. Merge and record

```bash
python3 eval_ashfall.py runs/<candidate>.html --runtime --merge runs/<candidate>.ai.json
python3 eval_ashfall.py --report runs/     # compare everything scored so far
```

Add a row to `RESULTS.md`. Every row records the candidate config AND the grader config.

## Rules that keep scores comparable

- **Hold the grader fixed.** LLM-as-judge scores are only comparable when the same judge
  model at the same reasoning effort graded both runs - with the same GRADER_PROMPT.md
  version. The
  grader prompt is part of the measuring apparatus: editing it invalidates prior F/G scores
  just like switching judge models does. Use the strongest model you have access to -
  grading does not need to happen in the harness being benchmarked, and even a free-tier-only
  setup has a best option; find it once and stick with it. The `Grader` column in RESULTS.md
  exists so a grader switch is visible instead of silent.
- **One sample is noisy.** A single run per config is the default here (free-tier quotas are
  real), but treat small gaps as ties. Rerun a config (`r2`, `r3`, ...) when a result looks
  surprising or two configs land close together, and record every run - never only the best
  one (that is cherry-picking).
- **The prompt is frozen.** Editing `make-game-ashfall-outpost.prompt.md` invalidates every
  prior row in RESULTS.md. If the prompt must change, that is a new eval version: bump the
  rubric version and start a new results table.
- **Truncated, broken, and weird outputs get scored anyway.** The eval measures what the
  model did, not what it meant.

## Glossary - the industry terms this exercise teaches

- **eval**: any measured test of model capability. This directory is one.
- **benchmark**: a standardized collection of tasks (evals) plus a fixed protocol for
  running them, so scores are comparable across models - e.g. SWE-bench, HumanEval. What we
  have here is a single-task eval used benchmark-style. (Usage overlaps: people also say
  "eval" for a whole suite; "benchmark" reliably implies the standardized collection.)
- **task / item**: one unit of work in an eval. This eval has one task; real benchmarks
  have hundreds, which is what makes their scores statistically stable.
- **reasoning effort**: the knob controlling how much hidden reasoning a model does before
  answering (OpenAI: "reasoning effort"; Anthropic: extended thinking / effort levels).
  Harnesses surface it under different names; record whatever the harness calls it.
- **harness / scaffold**: the software wrapping the model - chat UI, CLI agent, IDE plugin.
  The same model in different harnesses can score very differently.
- **LLM-as-judge**: using a model to grade output that is too open-ended for exact-match
  scoring. Categories F-G here. Known failure modes: leniency bias, verbosity bias,
  self-preference (a judge favoring output written by its own model family), anchoring.
- **rubric-anchored scoring**: giving the judge explicit per-score criteria ("2 requires
  ALL of...") instead of asking for a holistic number. Reduces judge variance.
- **pointwise vs pairwise**: scoring one output against a rubric vs asking which of two
  outputs is better. This eval is pointwise; pairwise is often more reliable but needs
  n^2 comparisons.
- **inter-rater agreement**: how closely two graders (human or model) agree on the same
  submission. Grading one candidate with two judge models and comparing is a cheap way to
  measure how trustworthy the judged half is.
- **pass@k / sampling variance**: models are stochastic; one sample per config is a noisy
  estimate. pass@k reports the chance at least one of k samples succeeds.
- **contamination**: the task or its solutions appearing in training data. This prompt is
  public in a personal repo - a minor risk today, a real one if a task goes viral.
- **saturation**: when strong models all hit the ceiling and an eval stops discriminating.
  The fix is usually a harder task, which is why this prompt asks for so much.

## Provenance

Initial files drafted by Opus 5 (xhigh) in the Claude desktop app, 2026-08-08. Reworked
2026-08-09 with Claude Code (Fable 5): grader prompt restructured for weak grader models,
merge parsing hardened, runtime checks taught to open the Dev tab, pipeline validated
end-to-end with subagent-generated candidates (see RESULTS.md). Renamed `benchmark01/` to
`eval01/` the same day, once the eval-vs-benchmark distinction sank in.
