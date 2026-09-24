---
name: reasoning-model-harness
description: "Use when OpenCode Go reasoning models return empty content."
version: 1.0.0
author: gentech
category: gentech-ops
hermes:
  tags: [harness, reasoning, kimi-k3, glm-5.2, opencode-go, generation]
  trigger: "When generating large content (HTML, code, docs) via OpenCode Go reasoning models and getting empty content / finish:length"
---

# Reasoning-Model Harness — Don't Burn the Tank in Neutral

## The Problem (proven Aug 16, 2026)
Reasoning-first models (Kimi K3, GLM 5.2) on OpenCode Go spend their ENTIRE
`max_tokens` budget on `reasoning_content` before emitting any `content`.
Result: `finish_reason: "length"`, `content: ""`, 40-56K chars of reasoning,
zero output. This is a HARNESS mismatch, not a broken model.

## Symptoms
- HTTP 200, `cost: 0`, but `content` is empty
- `usage.completion_tokens` == your `max_tokens` (all burned)
- `message.reasoning_content` is huge (tens of thousands of chars)
- `finish_reason: "length"`

## Fixes (in order of reliability)

### 1. Use a code-specialized model for generation
`kimi-k2.7-code` is tuned to write code directly. But it can ALSO reason long
on big tasks — if it hangs >5 min, kill it and build manually.

### 2. Try `thinking: {type: "disabled"}`
Works reliably on SHORT queries (verified: instant reply, no reasoning burn).
On COMPLEX generation tasks the model may still reason anyway. Worth one try.

```json
{"model":"glm-5.2","messages":[...],"max_tokens":16000,"thinking":{"type":"disabled"}}
```

### 3. Build it yourself (most reliable)
For a full artifact (landing page, dashboard), don't fight the API. You have
the baseline + requirements — write the file directly. The model is for
reasoning/audit, not for one-shot large generation through this harness.

## Ollama Cloud AUDIT access (verified Sep 8 2026 — "models down" was a false alarm)
All audit models are LIVE on Ollama Cloud: `glm-5.2`, `glm-5.3-flash`, `kimi-k2.7-code`, `kimi-k3`, `gpt-oss:20b/120b` etc (19 total, verify via `/v1/models`). Two false "can't audit" symptoms:
1. **EmptyStreamError** (log: `provider=ollama-cloud ... Stream drop ... EmptyStreamError ... via=Google Frontend`, HTTP 200, empty body) is an upstream SSE hiccup, NOT a dead model — retry clears it.
2. **Reasoning models return `content:""` + `finish:"length"` on small budgets** (the harness trap below) — give AUDIT calls ≥500 tokens (1000-4000 real audits). Verified both glm-5.3-flash + kimi-k2.7-code return real content at max_tokens:500.
Workaround curl (shared OLLAMA_API_KEY, no new creds): `curl -s -X POST https://ollama.com/v1/chat/completions -H "Authorization: Bearer $KEY" -d '{"model":"glm-5.3-flash","messages":[...],"max_tokens":2000}'`.

## MEASURED: thinking vs acting (2026-09-22) — and the counter-intuitive rule

Jordan's read: *"Kimi K3 had the same issue Jev had where it did more thinking and reasoning than
acting."* Measured directly — same task, two framings, two budgets:

| Framing | Budget | reasoning | answer | thinking share |
|---|---|---|---|---|
| as a QUESTION | 300 | 1,022 ch | **0 ch** (`done=length`) | 100% |
| as a QUESTION | 4000 | 2,838 ch | 545 ch | 84% |
| as a JOB | 300 | 649 ch | 62 ch (correct) | 91% |
| as a JOB | 4000 | 1,250 ch | **14 ch** | 99% |

**Two rules, both opposite to intuition:**

1. **A BIGGER BUDGET MAKES THE ANSWER SHORTER.** 4000 tokens bought a 14-character answer; 300
   bought a usable one. More rope is just more rope to think with. Budget it tight.
2. **Frame the ask as a JOB, not a question.** Question framing at a tight budget produced
   literally nothing; job framing at the same budget produced a correct answer.

**Why K3 is still worth using — the role, not the model.** As a WORKER this disposition is pure
waste: it spends the budget getting to an answer it never writes down. As an AUDITOR the reasoning
IS the deliverable. The exact trait that makes it a bad builder makes it a good critic. **Same
engine, different gear** — so we give it a GENEROUS budget for audits (we want the deliberation)
and a TIGHT one if we ever need it to emit something.

⚠️ **Do not repeat Jordan's Jev analogy without checking it.** Our own Sep 19 deep dive recorded
TypeSafe AI's Jev as a **System One** decision model — deliberately fast, ~0.4 s typed decision,
calibrated confidence. Its whole design is about NOT over-thinking, so it is the wrong comparison
for a reasoning-burn failure. Correct the premise rather than agreeing with it.

## The Lesson (Jordan's insight)
> The model is the engine. The harness is the transmission. Same engine, wrong
> gear = burn the whole tank in neutral.

This is why harnesses are "the next big thing" — a reasoning model called wrong
is useless; the same model called right is a weapon. Match the model to the
task: reasoning models for hard problems, code models for generation, and
manual build when the harness fights you.

## 🚨 FIELD NAME TRAP — the right key DEPENDS ON THE ENDPOINT (corrected 2026-09-23)
**`reasoning_content` is never the right key on Ollama Cloud.** But the correct key is not one name
either — measured live on `kimi-k3`, same question, both endpoints:

| endpoint | message keys | deliberation in | `usage` |
|---|---|---|---|
| `/v1/chat/completions` | `['content','reasoning','role']` | **`reasoning`** | returned |
| `/api/chat` | `['content','role','thinking']` | **`thinking`** | `None` |

An extractor reading `reasoning_content` gets `""` for both, and a *successful* 44K-char audit
reports `reasoning: 0, content: 0, finish: length` — which reads exactly like "burned the budget in
neutral." It did not. Read `content` for the answer in both cases; pick the deliberation key by
endpoint. **DUMP `sorted(message.keys())` before concluding a model is broken or empty.** Costs one
call and prevents a false "the model can't do it" verdict.

## Pitfalls
- Don't retry the same reasoning model with a bigger budget — it just reasons longer, and (measured)
  it answers SHORTER. Tighten the budget, and frame the ask as a job rather than a question.
- A reasoning model that returns an empty `content` did not decline the task — it spent the budget
  reasoning and was cut off. Check `done_reason == "length"` before assuming anything else.
- `thinking: disabled` is not a guarantee on complex tasks.
- Check `reasoning_content` length before assuming the model is broken.
- OpenCode Go reports `cost: 0` — free, but don't waste time on it.
