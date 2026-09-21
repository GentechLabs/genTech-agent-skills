---
name: pre-change-impact-assessment
description: "Use BEFORE any big change to the system — installs, absorptions, provider repoints, config or doctrine changes. Snapshot what we do, predict what will differ, then diff after. Jordan's directive, 2026-09-20."
version: 1.0.0
author: gentech
tags: [doctrine, change-management, verification, absorption, regression]
---

# Pre-Change Impact Assessment

**Jordan's directive, 2026-09-20:**

> *"In the future, before we update to something like this, to where it'll be a big change for us in our
> system, I think what we might want to consider first is taking a snapshot of what we do and consider what
> will be changed as a result… I didn't realize how much Jev would kind of change the speed at which we
> move. Just let me know, like, hey, this has happened before when we tried to install the Jev Hermes skills
> and we had to undo a couple things… it's beneficial still, but I didn't catch how things were going to be
> different until the next day."*

---

## Why this exists

**A capability change shows up in a diff. A behavioural change does not.**

Jev added no visible capability — no new skill, no new tool, nothing you could point at. What it changed was
**how fast we move**: it introduced a layer that produced more questions and more deliberation. That is
invisible in any inventory, and it was only caught a day later, by feel.

**If you never captured "before", you cannot see the change at all.** You just notice that something feels
slower, with no evidence and no way to attribute it to the thing that caused it.

So the rule is three steps, not one: **snapshot → predict → diff.**

---

## When this applies

Any change that alters how the system behaves, not just what it contains:

- installing or absorbing an external tool, skill pack, or mechanism
- changing providers, models, routing, or fallback configuration
- changing standing doctrine, SOUL.md rules, or agent instructions
- enabling a new automated job that can act (not merely report)
- anything that touches more than one seat

**If you are unsure whether it qualifies: it qualifies.** The cost is one command and five minutes; the cost
of skipping it is a behavioural regression nobody can see.

---

## Step 1 — Snapshot BEFORE

```bash
python3 /root/.hermes/profiles/gentech/scripts/system-snapshot.py --label before-<change>
```

Captures, per seat: skill inventory with content hashes, SOUL.md rules, provider names, cron list, memory
usage. **No secrets** — keys are recorded as present/absent, never by value. Lands in
`00-System/snapshots/` so it is version-controlled and outlives the change it describes.

## Step 2 — PREDICT what will change, in writing, BEFORE applying

**This is the step that actually matters, and the one that was missing.** A snapshot alone is just a file.
Write down, in the impact note:

1. **What capability is added** — the easy part, visible in a diff.
2. **What BEHAVIOUR is expected to change** — the hard part. Be specific:
   - Will the agent stop more often, or less?
   - Will turns get longer? Will it ask questions it used to answer?
   - Will it deliberate where it used to decide?
   - What gets *slower* even if it gets *better*?
3. **What must this NOT be allowed to mean** — the boundary. (See `decides-alone-execution`.)
4. **What would make us undo it** — the kill criterion, decided *before* you are attached to the change.

**If you cannot state (2), you do not yet understand the change well enough to apply it.**

## Step 3 — Snapshot AFTER, then diff

```bash
python3 .../system-snapshot.py --label after-<change>
python3 .../system-snapshot.py --diff before-<change> after-<change>
```

The diff shows state. **It cannot show speed.** State changes are the floor, not the ceiling — the
behavioural prediction from step 2 has to be checked by hand, in words, on the day.

## Step 4 — Report the delta to Jordan, including precedent

Jordan's explicit ask: **tell him when it has happened before.** Check the register below and lead with it —
*"this has happened before, here's what it did last time"* is more useful than a fresh analysis.

---

## Precedent register

Prior big changes and what they actually changed. **Check this first.** Append every time.

### Jev `hermes-jev-skills` — absorbed 2026-09-19 23:33

- **Intended:** smarter per-turn decisions; the agent deciding better on its own.
- **Capability added:** none. No skill, no tool, no plugin. Nothing installed.
- **What actually changed — BEHAVIOURAL:** the mechanism was absorbed into `model-routing` as
  *"calibrated confidence — back off to the current model when unsure."* That is a **model-selection**
  instruction. With no boundary written, it read itself as *"unsure about the model"* → *"unsure about the
  task"* → *"ask Jordan."* **Result: ask-creep.** More questions, longer turns, work handed back mid-run.
- **Speed impact:** measurable in feel, not in any inventory. Caught by Jordan the next day, not by us.
- **Undone / corrected:** rule 7 of `develop-and-verify` lost its `"or ask"` clause; the routing section was
  pinned to *"calibrated confidence means pick a different model, it does not mean ask Jordan"*; the
  **Decides-Alone Test** was added as step 0 of absorption; **Run to the Stopping Point** became a rule.
- **Verdict:** net beneficial, but **the cost was invisible for a day and the fix took four changes.**

### Provider repoint `ollama-cloud → opencode-go` — 2026-09-20

- **Intended:** restore web reading, vision and background subsystems after an Ollama weekly quota exhaustion.
- **What changed:** 11 background subsystems + the fallback provider, across all four seats.
- **Behavioural prediction (recorded):** conversation, crons and handoffs unaffected; background roles take
  effect on next restart. Auxiliary-role coverage was flagged as **unproven** — the probe proves chat
  completions work, not that every auxiliary role is satisfied.
- **Verdict:** pending observation.

---

## The rule this earns

> **Before a big change: snapshot what we do, write down what you expect to be different, then measure the
> difference.** A change that only alters capability can be reviewed afterwards. A change that alters
> *behaviour* must be predicted beforehand, because afterwards there is nothing to compare it against.

Corollary, and the reason this is a standing rule rather than a one-off: **the changes that hurt are the ones
that feel like improvements.** Jev was beneficial. That is exactly why nobody was watching its speed cost.

---

## Related

- `decides-alone-execution` — the doctrine the Jev change violated; carries the Decides-Alone Test
- `00-HQ/absorption-doctrine.md` (vault) — the full absorption procedure and tested roster
- `00-HQ/propagation-broken-false-green-2026-09-20.md` (vault) — why the fleet didn't receive the corrections
- `system-snapshot.py` — the tool for steps 1 and 3
