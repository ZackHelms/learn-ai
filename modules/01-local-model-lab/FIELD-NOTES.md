# Module 01 — Field notes

Real results from real hardware. **Nothing in this file is copied from anywhere
else** — if a number is here, it came off a machine described here.

That is the whole point. Benchmark figures only mean something next to the
machine that produced them, so this repo ships no performance numbers of its
own. It ships `scripts/bench.py` and this file.

## How to add an entry

```bash
bash scripts/check-env.sh          # records your machine's specs
uv run scripts/bench.py --repeat 3 # the numbers
```

Then paste below using the template. Always include **date, hardware, and model
tags** — an entry without them is not useful to anyone, including you in six
months.

## Template

```markdown
### YYYY-MM-DD — <short machine name>

**Hardware:** <cores> cores, <RAM> GB, <CPU model>, <AVX2/AVX-512?>
**OS:** <Ubuntu 24.04 / macOS 15 native / WSL2 / VM>
**Ollama:** <version>

<paste the bench.py table here>

**Exercise A — structured output:**
| Model | Valid JSON? | Right keys? | Facts plausible? | Notes |
|---|---|---|---|---|
| | | | | |

**Surprises:**
-

**Questions this raised:**
-
```

---

## Entries

_None yet._

I could not run these myself when writing the module — the authoring environment
had no network access to the model registry, so no models could be pulled. Every
number in this file has to come from a real run.

If you work through this module, your entry is the first one.

---

## Things worth watching for

Collected as they come up, so later entries know what to look at.

> **Two of these gate module 02.** The curriculum's design rests on assumptions
> that can only be settled by running this module, and they are marked ⚠️ below.
> Answers belong here; they are tracked in
> [`TODO.md`](../../TODO.md#gated-on-running-module-01).

- **Does generation speed scale linearly with parameter count?** It should be
  roughly memory-bandwidth-bound on CPU, but the constant matters.
- **Cold load versus warm.** Run `bench.py` twice. The gap is what "keep the
  model loaded" is worth, and it informs how the eval harness in module 03
  should be ordered — reloading a model per test case would dominate runtime.
- **Does resident memory match the roster estimate?** The `disk_gb` and
  `min_ram_gb` fields in `models/roster.yaml` are *estimates*, explicitly
  flagged as unmeasured. If your numbers disagree, the roster is wrong — please
  correct it.
- ⚠️ **Where exactly does structured output break down?** The rung at which JSON
  becomes reliable is the single most useful thing to know about this roster,
  because everything agentic downstream depends on it.
- ⚠️ **Is the smallest model usefully bad, or uselessly bad?** The premise of
  this whole course is that weak models fail *legibly* — that the failure points
  at its cause. A model that emits pure noise teaches nothing. If rung 0 turns
  out to be noise rather than instructive failure, it should be dropped and the
  ladder should start a rung higher.
- ⚠️ **Can the top rung actually complete a multi-step tool loop?** Module 04 is
  built on the assumption that it can. Nothing in module 01 tests this directly,
  but the structured-output results are the leading indicator: a model that
  cannot reliably emit a JSON object is not going to reliably emit a tool call,
  because they are the same capability wearing different hats. If the top rung
  is shaky here, expect module 04 to need constrained decoding or heavier
  scaffolding — and say so rather than pretending otherwise.
- **Prompt processing versus generation speed.** If the ratio is large, long
  prompts are cheap and long outputs are expensive — which shapes how module 02
  and 05 should think about context.
