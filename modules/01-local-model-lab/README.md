# Module 01 — Local model lab

> Get a set of small models running on your own hardware, and find out what that
> hardware can actually do.

## Why this module

Before anything agentic makes sense, you need models you can hit whenever you
like, for free, without thinking about it. Local models make experimentation
cheap, and cheap experimentation is what the rest of this course runs on.

This module also exists to give you a **feel** for the constraints. Not the
numbers — those are different on every machine — but the shape of the tradeoffs:
how much slower a bigger model is, how much memory it costs, how long a cold
load takes, where quality falls off. That intuition is hard to get from reading
and easy to get from twenty minutes of measuring.

One thing that surprised me: the interesting variable is not really "how smart
is this model." It is **how legibly does it fail.** That is what the roster is
built around.

## What you'll be able to do

- Run several local models and switch between them from the command line
- Call a model over an OpenAI-compatible HTTP API — the same shape you'll use
  for the rest of the course
- Measure real generation speed, prompt processing speed, and memory on *your*
  machine
- Explain what quantization costs you and what it buys
- Say which model on the roster to reach for and why

## Before you start

- Finished [Module 00](../00-overview/) — particularly the hardware and platform
  prerequisites
- ~45 minutes, plus download time
- **~20 GB of disk** and a decent connection

<!-- BEGIN GENERATED: roster-budget -->
- **Total RAM assumed:** 16 GB
- **Usable for a model:** ~10 GB (after OS, editor and a browser — this is the number that actually binds)
- **Disk for the core roster:** ~11.3 GB (5 models); budget 20 GB to be comfortable
- **Largest core model:** IBM Granite 4.1 8B at ~8.0 GB resident
<!-- END GENERATED: roster-budget -->

## Concepts

### The runtime and the API are separate things

Two pieces get conflated constantly, so let's separate them now.

The **runtime** is the program that loads model weights and does the math —
Ollama, llama.cpp, vLLM, LM Studio. The **API** is the HTTP interface it exposes.

This matters because the API has effectively standardized. Ollama, llama.cpp's
server, vLLM, and every hosted provider all speak some version of
`POST /v1/chat/completions` with the same JSON shape. So:

> Everything you learn against a local endpoint transfers to a hosted one, and
> the runtime becomes swappable.

That is why this course uses Ollama as the default and does not care much about
it. The runtime is an implementation detail. The API is the thing to learn.

### Quantization: the lever that makes this possible

Model weights are trained in 16-bit floats. An 8B model at 16 bits is ~16 GB —
already your whole budget.

**Quantization** stores those weights at lower precision. At roughly 4 bits, the
same model needs about a quarter of the memory. You lose some quality. In
practice the loss at 4-bit is small compared to the difference between a 3B
model and an 8B one, which makes the trade nearly always worth taking on
constrained hardware.

You will see names like `Q4_K_M`. Read it as: 4-bit, K-quant method, medium
variant. `Q8_0` is 8-bit and larger. `MXFP4` is a 4-bit float format some newer
models ship natively. The details matter less than the tradeoff, which you will
measure yourself in Exercise C.

### Memory is not just weights

Weights are the big number, but not the only one. There is also the **KV cache**
— the model's memory of the current conversation — which grows with context
length. A long conversation costs real RAM on top of the model.

This is why the budget above says ~10 GB usable rather than 16. Between the OS,
your editor, a browser, and KV cache, headroom disappears faster than you expect.

Practical consequence for this course: **one model resident at a time.** When
you compare models, you are loading and unloading them, not running them side by
side. You will see this in Exercise B as cold-load time.

### The roster

<!-- BEGIN GENERATED: roster -->
| Rung | Model | Params | Vendor | License | Tool calling | Disk (est.) |
|---|---|---|---|---|---|---|
| 0 | IBM Granite 4.0 Nano | 350M | IBM | Apache-2.0 | weak | ~0.3 GB |
| 1 | Google Gemma 4 E2B | ~2B effective | Google | Gemma Terms of Use | partial | ~1.6 GB |
| 2 | Microsoft Phi-4-mini | 3.8B | Microsoft | MIT | native | ~2.5 GB |
| 2 | IBM Granite 4.1 3B | 3B | IBM | Apache-2.0 | native | ~2.0 GB |
| 3 | IBM Granite 4.1 8B | 8B | IBM | Apache-2.0 | native, strong | ~4.9 GB |
| stretch | OpenAI gpt-oss-20b _(optional)_ | 21B total / 3.6B active (MoE) | OpenAI | Apache-2.0 | native, strong | ~12.0 GB |
<!-- END GENERATED: roster -->

Why each one is here:

<!-- BEGIN GENERATED: roster-why -->
- **IBM Granite 4.0 Nano** (rung 0) — The control variable. Small enough to load instantly and dumb enough to fail on almost every non-trivial task, which is exactly what makes it useful: when your prompt or eval is wrong, this model shows you immediately and cheaply. Do not expect it to complete agent tasks.
- **Google Gemma 4 E2B** (rung 1) — Google's edge-targeted tier. Earns its slot twice over: it is a genuine step up from rung 0, and its bespoke license gives you something concrete to compare against the Apache-2.0 entries when licensing comes up.
- **Microsoft Phi-4-mini** (rung 2) — Function calling was an explicit design goal for this model rather than an afterthought, which makes it the cheapest place to watch tool calling start working. Punches above its size on instruction following.
- **IBM Granite 4.1 3B** (rung 2) — Same family and same post-training pipeline as the 8B, so comparing the two isolates the effect of SIZE with everything else held constant. That is a controlled experiment you cannot run across vendors.
- **IBM Granite 4.1 8B** (rung 3) — The "it actually works" baseline. When an exercise is supposed to succeed and you need to know whether the problem is your code or the model, this is the model you reach for. IBM specifically called out improved tool calling in the 4.1 post-training pipeline.
- **OpenAI gpt-oss-20b** (rung stretch) — OPTIONAL, AND IT MAY NOT FIT ON YOUR MACHINE. OpenAI states it runs in 16 GB, but that is your entire budget, so expect it to be marginal at best next to a desktop session. It is here for one lesson: a mixture-of-experts model has the MEMORY footprint of 21B and roughly the SPEED of 3.6B. Speed and memory are separate axes. Skip it without guilt.
<!-- END GENERATED: roster-why -->

<!-- BEGIN GENERATED: roster-provenance -->
> **Where these numbers come from.** disk_gb and min_ram_gb are ESTIMATES derived from vendor model cards and typical Q4_K_M quantization ratios. They have NOT been measured. Run scripts/bench.py on your own machine and record the real numbers in the module's FIELD-NOTES.md.
>
> ollama_tag values follow Ollama's documented naming convention but were NOT confirmed against the live registry when this file was written, because the authoring environment could not reach ollama.com. Run /update-models from a machine with network access to confirm and correct them. Entries carry `tag_verified: false` until someone does.
>
> Roster last verified against upstream: `2026-07-29`.
<!-- END GENERATED: roster-provenance -->

The roster lives in [`models/roster.yaml`](../../models/roster.yaml) and nowhere
else. Tables in these docs are generated from it. If you want different models,
edit that file and run `uv run scripts/render-roster.py` — nothing in the
curriculum hardcodes a model name.

## Exercises

### Setup 1 — Check your environment first

Before downloading several gigabytes, find out whether this machine can do the
work:

```bash
bash scripts/check-env.sh
```

It checks OS, cores, vector extensions, RAM, disk where Ollama stores models,
and required tools. It exits non-zero on anything blocking.

Two checks worth knowing about:

- **AVX2 / AVX-512.** These vector extensions matter a lot for CPU inference
  speed. If you are on x86 *without* AVX2, you are almost certainly running
  under emulation — see the Mac warning in Module 00.
- **Disk location.** Models go to `$OLLAMA_MODELS` (default `~/.ollama`), which
  may be on a different filesystem than this repo. The script checks the right
  one.

Fix anything it flags before continuing.

### Setup 2 — Install Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

On Ubuntu this installs a binary and sets up a systemd service. Verify:

```bash
ollama --version
curl -s http://localhost:11434/api/version
```

If the service is not running:

```bash
sudo systemctl start ollama    # or, in a container without systemd:
ollama serve                   # run in a separate terminal
```

> **macOS:** download the native app from [ollama.com](https://ollama.com)
> instead of using the install script. Everything after this point is identical.
> I have not tested the macOS path myself.

### Setup 3 — Pull the roster

```bash
bash scripts/pull-roster.sh
```

This reads tags from `models/roster.yaml`, so it can't drift from the docs. It
skips the optional stretch model; add `--include-optional` if you want it, and
`--dry-run` to see what it would do first.

**If a pull 404s**, the roster is stale, not you. Vendors retag models
constantly, and the tags shipped here were never confirmed against the live
registry ([ADR 0005](../../docs/decisions/0005-unverified-tags.md)). The script
prints the fix; the short version is: find the real tag at
<https://ollama.com/library>, correct `models/roster.yaml`, set
`tag_verified: true`, and re-run `uv run scripts/render-roster.py`.

For reference, this is what it pulls:

<!-- BEGIN GENERATED: roster-pull -->
```bash
ollama pull granite4:350m
ollama pull gemma4:e2b
ollama pull phi4-mini
ollama pull granite4.1:3b
ollama pull granite4.1:8b
```

Optional, only if you have the headroom:

```bash
ollama pull gpt-oss:20b
```
<!-- END GENERATED: roster-pull -->

Then confirm:

```bash
ollama list
```

### Setup 4 — Python environment

The exercise scripts use [`uv`](https://docs.astral.sh/uv/):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Scripts in this repo carry [PEP 723](https://peps.python.org/pep-0723/) inline
metadata, so `uv run scripts/whatever.py` resolves dependencies automatically.
No virtualenv to create, no requirements file to install.

> Remember from Module 00: on Ubuntu 24.04 a bare `pip install` fails with an
> "externally managed environment" error. That is PEP 668, and it is intended
> behavior. `uv` avoids the whole question.

---

### Exercise A — One prompt, every model

**Goal:** see the capability ladder directly, and start building intuition for
how each rung fails.

Talk to a model the simplest possible way:

```bash
ollama run <tag> "Explain what a checksum is in two sentences."
```

Now do something more revealing. Ask for **structured output**, which is where
small models struggle in ways you can actually see:

```bash
ollama run <tag> 'Return ONLY valid JSON, no other text, matching:
{"name": string, "population": number, "country": string}
for the city of Lyon.'
```

Run that against every model in your roster, smallest to largest. Watch for:

- Does it return *only* JSON, or does it wrap it in prose or a code fence?
- Is the JSON actually valid?
- Are the field names right?
- Did it invent a field, or drop one?
- Is the data plausible?

**What to look for:** the failures should get *less* structural and *more*
factual as you go up the ladder. The smallest model tends to fail at the format
level — it does not reliably produce parseable JSON at all. Larger models
produce clean JSON and then get details wrong. Those are different problems with
different fixes, which is exactly the distinction this course is trying to teach
you to make.

Record what you see in [`FIELD-NOTES.md`](FIELD-NOTES.md).

> This is the seed of module 03. "Is the output valid JSON with the right keys?"
> is a *deterministic assertion* — a real eval, no judgment needed. Most useful
> evals start exactly here.

### Exercise B — Benchmark your machine

**Goal:** get real numbers for your hardware.

```bash
uv run scripts/bench.py
```

This walks the roster and reports, per model:

| Metric | Meaning |
|---|---|
| **Gen tok/s** | Generation speed — how fast it writes |
| **Prompt tok/s** | Prompt processing — how fast it reads |
| **Cold load** | Time to get weights into memory from disk |
| **Resident** | Actual memory occupied, per Ollama |

These are kept separate on purpose. They behave differently, and averaging them
into one "speed" number hides the interesting part. Prompt processing is usually
much faster than generation — which is why a long prompt costs less than you'd
think, and a long *output* costs more.

The script does not wall-clock anything; it reads the timing counters Ollama
returns with each response.

Useful variants:

```bash
uv run scripts/bench.py --repeat 3          # average out noise
uv run scripts/bench.py --model granite-8b  # one model, by roster id
uv run scripts/bench.py --json              # machine-readable
```

**Paste the output into [`FIELD-NOTES.md`](FIELD-NOTES.md).**

This repo deliberately ships **no benchmark numbers of its own.** Published
tokens/sec figures are close to meaningless across machines — core count, memory
bandwidth, vector extensions, and thermal headroom move the result by multiples.
Rather than print numbers that would be wrong for you, the repo ships the script.

Things worth noticing:

- How does generation speed scale with model size? Is it linear?
- How much of the total time is cold load? (Run it twice — the second is warm.)
- Does resident memory match the estimate in the roster? If not, the roster's
  estimate is wrong and worth correcting.

### Exercise C — What quantization costs

**Goal:** feel the size/quality tradeoff instead of taking it on faith.

Pull one model at two precisions. Most Ollama models offer several; check the
tags page for the family you're using:

```bash
ollama pull <model>:<tag>-q4_K_M
ollama pull <model>:<tag>-q8_0
```

Compare:

1. **Disk and memory** — `ollama list` and `ollama ps`
2. **Speed** — `uv run scripts/bench.py` against each
3. **Quality** — run the Exercise A JSON prompt against both, several times

The third one is the interesting one and the hardest to judge. That difficulty
is itself the lesson: **eyeballing quality does not scale.** You cannot tell
from three samples whether Q8 is meaningfully better than Q4, because the
variation between runs of the *same* model is comparable to the difference
between them.

This is precisely the problem evals exist to solve, and it is why module 03
comes early.

### Exercise D — Call the API directly

**Goal:** see the actual interface, before any library hides it.

```bash
curl -s http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "<tag>",
    "messages": [
      {"role": "system", "content": "You answer in exactly one sentence."},
      {"role": "user", "content": "What is a checksum?"}
    ],
    "temperature": 0
  }' | jq .
```

Look at the response shape: `choices[0].message.content`, plus a `usage` block
with token counts.

**This is the whole interface.** A list of messages with roles in, a message
out, token counts attached. Everything else in this course — tool calling,
agents, context engineering — is built on this one call. Frameworks wrap it.
Commercial harnesses wrap it. It does not get more complicated than this; it
just gets more elaborate around the edges.

Worth trying:

- Drop the system message. What changes?
- Set `"temperature": 0` versus `1.5` and run each a few times. Determinism is
  a dial, and even at 0 it is not perfectly deterministic.
- Add `"stream": true` and watch the response arrive in chunks.

## Check yourself

You are ready for module 02 when:

- [ ] `bash scripts/check-env.sh` exits 0
- [ ] `ollama list` shows the core roster
- [ ] `uv run scripts/bench.py` produces a table, and it is in your field notes
- [ ] You can state which roster model you'd pick for a task needing reliable
      structured output, and why
- [ ] You have seen the smallest model fail at *format* and a larger one fail at
      *facts*, and can describe the difference
- [ ] The `curl` call in Exercise D returns a completion

## Appendix — What Ollama is hiding

Ollama is a convenience layer over [llama.cpp](https://github.com/ggml-org/llama.cpp).
That convenience costs you visibility into things worth seeing once.

Running `llama-server` directly exposes:

- **The GGUF file itself.** One file, explicitly downloaded, explicitly chosen —
  including its quantization, rather than accepting a default.
- **`-c` / context size.** Ollama picks one for you. Set it yourself and watch
  memory move.
- **`-t` / thread count.** Defaults are not always right for your core count.
- **`-ngl` / GPU layers.** Irrelevant on CPU, but this is the knob everyone
  means when they say "offload to GPU."
- **GBNF grammars.** llama.cpp can *constrain decoding to a grammar*, making
  invalid JSON structurally impossible rather than merely requested. Given how
  Exercise A goes on small models, this is a genuinely big deal — you are
  changing what the model is able to emit, not asking it nicely.

llama.cpp also exposes an OpenAI-compatible server, so the Exercise D `curl` call
works against it with only a port change.

I have not written this appendix as a full walkthrough yet — I want to do it
properly with grammar-constrained decoding in module 03, where it will pay off
against a real eval. For now, treat this as a list of what to be curious about.

## If you use a harness

What you just did by hand maps onto commercial tooling like this:

**Model selection.** Claude Code, Codex, and Copilot pick models for you, mostly
by tier. Exercise B is you doing that selection explicitly, with measurements.
The tradeoff those tools navigate silently — capability against latency and cost
— is the same one you just measured as capability against latency and *memory*.

**The API surface.** Exercise D's request shape is essentially what every one of
these tools sends. Anthropic's Messages API and OpenAI's Chat Completions API
differ in details, but the structure — messages with roles in, message out,
token usage attached — is common to all of them. When you later see a harness
"managing context," it is managing what goes in that `messages` array.

**Context windows.** The KV-cache growth described above is why long sessions
degrade and why harnesses compact or summarize. You will feel this directly on a
16 GB machine, where a long context is a memory problem rather than a billing
one. Same mechanism, more visible consequence.

**Cost.** Locally, cost is time and RAM. With a harness, it is tokens and money.
The optimization pressure is identical, which is why module 05's argument —
push deterministic work into scripts — applies to both.

You do not need any of these tools for this course. If you do use one, the thing
to take from this module is that its model calls look like Exercise D.

## Field notes

_Real results from real hardware. Include date, machine, and model tags._

**Template:**

```markdown
### YYYY-MM-DD — <machine: cores, RAM, CPU>

<paste `uv run scripts/bench.py` output>

Exercise A observations:
- <model>: <what it did with the JSON prompt>

Surprises:
- <what you did not expect>
```

See [`FIELD-NOTES.md`](FIELD-NOTES.md).

## Further reading

- [Ollama docs](https://github.com/ollama/ollama/tree/main/docs) — API reference
- [llama.cpp](https://github.com/ggml-org/llama.cpp) — what's underneath
- [GGUF format](https://github.com/ggml-org/ggml/blob/master/docs/gguf.md)
- [uv](https://docs.astral.sh/uv/) and [PEP 723](https://peps.python.org/pep-0723/)
- [`models/roster.yaml`](../../models/roster.yaml) — the roster and why each model is on it
- [ADR 0003](../../docs/decisions/0003-ollama-primary.md) — why Ollama over the alternatives

---

Previous: [Module 00 — Overview](../00-overview/) ·
Next: Module 02 — Prompt engineering ([spec](../../docs/ROADMAP.md))
