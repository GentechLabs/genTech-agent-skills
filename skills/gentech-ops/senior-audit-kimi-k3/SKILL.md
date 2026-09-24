---
name: senior-audit-kimi-k3
description: "Use when auditing money code — Kimi K3 on the real source."
version: 1.0.0
author: gentech
category: gentech-ops
hermes:
  tags: [audit, kimi-k3, ollama-cloud, sr-audit, reasoning, false-empty]
  trigger: "A treasury/DeFi/code system needs a second pair of eyes, or you have fixed several bugs of the same class in one session and need an independent read"
---

# Senior Audit — Kimi K3 as an Auditor

## When
A money-handling system needs an independent read, **especially after you have already fixed several
faults of the same class in one session** — that is the signal that your own eyes are the limiting
factor. Jr writes, Sr audits. Jr = DeepSeek V4 Flash. **Sr = Kimi K3.**

## The rail that works (verified 2026-09-23)
**Ollama Cloud**, not opencode-go (that returned `403 Forbidden` on `/zen/go/v1`):
```
POST https://ollama.com/v1/chat/completions
Authorization: Bearer $OLLAMA_API_KEY        # present in the profile .env
model: kimi-k3                               # also live: glm-5.3, kimi-k2.7-code
max_tokens: 16000                            # for an AUDIT — see budget below
```
Confirmed live model list via `GET https://ollama.com/v1/models` (20 models).

## 🚨 THE FALSE-EMPTY TRAP — the right key DEPENDS ON THE ENDPOINT
This is the whole reason the technique looked broken. **`reasoning_content` is never the right key
on Ollama Cloud**, but the correct key is not one name either — measured live on `kimi-k3`:

| endpoint | keys | deliberation in | `usage` |
|---|---|---|---|
| `/v1/chat/completions` (use this) | `['content','reasoning','role']` | **`reasoning`** | returned |
| `/api/chat` | `['content','role','thinking']` | **`thinking`** | `None` |

Read the wrong key and a call looks like `finish_reason: length, reasoning: 0, content: 0` — i.e.
"the budget burned in neutral." **It did not.** The answer was there under the other key.

```python
m = d["choices"][0]["message"]
answer    = m.get("content") or ""
reasoning = m.get("reasoning") or ""      # ← THIS key. Not reasoning_content.
```

**Rule: before declaring a reasoning model dead or empty, DUMP THE MESSAGE KEYS.** A probe that
prints `list(m.keys())` costs one call and would have saved a 67-second "failure".

## Budget — generous for an audit, and the answer still arrives
Measured on a real 13.5K-char code packet: `max_tokens: 16000` → **44,343 chars of reasoning +
6,548 chars of answer**, `finish_reason: stop`. The deliberation IS the deliverable for an auditor,
so unlike a generation task you do not starve it. (At `max_tokens: 6000` the same job hit
`length` — it reasoned past the ceiling and never wrote the answer.)

## Frame it as a JOB, not a question
Per `reasoning-model-harness`: question framing at a tight budget produced literally nothing; job
framing at the same budget produced a correct answer. Open with `JOB:` and state the deliverable.

## The prompt that worked
```
JOB: Audit <system> that moves real money on <chain>. Deliver a numbered list of concrete DEFECTS.

RULES
- Point every defect at a file + line from the code below. No architecture essays. No rewrites.
- Rank by how much real money each can lose.
- If you cannot point at a line, do not list it.
- For each: (a) file:line, (b) what actually breaks, (c) the minimal correct fix.
- End with one line: the single defect you would fix first.

MEASURED PRODUCTION FACTS (real, from today)
<the observed symptoms — the log lines, the wrong numbers, what the operator saw>

CODE UNDER AUDIT
<the REAL source, with line numbers>
```

The measured-facts block is what makes it an audit rather than a code review: it anchors the model to
symptoms that actually happened, so it hunts mechanisms instead of style.

## Route by BUDGET HEADROOM, not packet size — and K2.7 is fine when it has room (re-measured 2026-09-23)

An earlier version of this skill said "never route AUDIT work to `kimi-k2.7-code`". **That was too
broad.** HQ measured K2.7 and K3 tying on small packets (8/9 vs 7/8), and I re-measured the crossover
myself on a 1,810-char domain fixture (Chainlink staleness + a mint that never mints):

| model | packet | max_tokens | finish | answer |
|---|---|---|---|---|
| k2.7-code | 1,810 | **4,000** | `length` | **0 ch** (17,164 ch reasoning) |
| k2.7-code | 1,810 | **8,000** | `length` | **0 ch** (32,624 ch reasoning) |
| k2.7-code | 1,810 | **16,000** | `stop` | **2,200 ch — caught staleness** |
| k3 | 1,810 | 4,000 | `length` | 0 ch |
| k3 | 1,810 | 8,000 | `stop` | 3,538 ch |
| k3 | 1,810 | 16,000 | `stop` | 3,736 ch |

**The binding constraint is output budget, NOT packet size.** A 1.8K packet starves K2.7 at 4K and
8K identically; the same packet at 16K produces a real audit that catches the domain bug. So
`packet ≤ 8K` is the WRONG gate — it says "safe" for a case that returns nothing.

**The rule that actually holds:** budget the model for reasoning PLUS the answer
(`max_tokens ≥ ~16000` for a real audit, whatever the packet size). At equal ample budget both models
audit competently and both catch the domain bug. **K3's advantage is reliability under a tight
budget — its failure is loud, K2.7's is silent** — and K3 is not a superset on recall.

**Cost is not a reason to prefer K2.7.** Both are free at our tier, and on identical work K3 used
FEWER total tokens (measured 190 vs 36 on a trivial call, but 8,426 vs 13,863 on the real 2.2K
fixture) — K2.7 burns more by reasoning longer. There is no cost case for the silent-empty risk.

**Always check `finish_reason` before reading meaning into zero findings** — `length` + empty
`content` means the budget was burned, not that the code is clean.

## Pitfalls
- **Never paste a description of the code — paste the code with line numbers.** The model's value is
  pointing at lines you did not think to look at.
- **VERIFY every finding against the source before applying it** (`develop-and-verify`). Its #1 hit
  in the 2026-09-23 run was real and exact (`lfj_recenter.py:798`, an early `return` that skipped
  the cooldown write and turned one bad pass into a permanent 15-minute withdraw/re-deploy loop) —
  but read the line yourself first. An audit is a lead, not a verdict.
- **Budget the packet, not the model.** A huge packet does not need a huge `max_tokens`; it needs
  the budget for reasoning PLUS the answer.
- **A `403` is a rail problem, not a key problem** — try Ollama Cloud before concluding the key is dead.
- Apply fixes in the VAULT and sync; a profile-only edit is silently reverted.

## What this technique is FOR
The exact trait that makes a reasoning model a poor builder (it thinks far more than it writes)
makes it an excellent critic. Same engine, different gear.
