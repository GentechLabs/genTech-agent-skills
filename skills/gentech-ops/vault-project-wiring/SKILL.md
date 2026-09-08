---
name: vault-project-wiring
description: "When Jordan greenlights a new project/idea ('go ahead and update X', 'add it to the list', 'make the spec'), wire it into the vault end-to-end: spec file, ideas.md flagship entry, canonical build queue JSON, and the human-readable mirror — then verify and sync. The proven flow for turning a vision into a queued, buildable item."
version: 1.0.0
author: gentech
category: gentech-ops
tags: [vault, build-queue, spec, workflow, ideas]
---

# Vault Project Wiring

Turns a greenlit vision into a queued, buildable item. Proven Aug 1, 2026
(Model Strength Score, triggered by the Bittensor/Covenant AI drama).

## Trigger

Jordan says any of:
- "go ahead and update X" / "go ahead and build the spec"
- "add it to the list" / "why not add to the queue"
- He describes a product vision and you've confirmed the direction

## Go/No-Go Decision Panel — the front door (Jordan's directive, Aug 7, 2026)

**`00-HQ/go-no-go.md`** is a checkbox control panel Jordan uses to greenlight or park work. It is the **decision layer that feeds this wiring flow**: a checked box = a green light, no further confirmation needed.

### How it works
- **`[x]` = GO** → run this wiring flow (spec → ideas.md → build queue → mirror → sync)
- **`[ ]` = NO-GO / not decided** → stays parked in the panel
- Jordan checks boxes in Obsidian → vault syncs → Gentech reads it to know what's greenlit

### Sections
- **🟢 GO — Greenlit, build it** — active decisions; check = start building
- **🔴 NO-GO / Hold** — decided against or parked; Gentech stops touching these
- **🎯 Learning Track** — recurring commitments (AWS + Cyfrin check-ins)

### Rules
1. **A checked box is a green light** — build it, don't re-ask
2. **Seed it from `considerations.md`** when creating/updating — the panel is the condensed decision view of the full open-decisions doc
3. **Keep it Jordan's** — he can add any new idea to the GO list anytime; Gentech picks it up
4. **Route by lane** — GO (cloud/VPS) → Gentech list; GO (desktop/PC) → Forge list; NO-GO → stays parked
5. **Sync after editing** — `ob sync` so all agents pick up the checked boxes

### Relationship to this skill
The go/no-go panel is the **front door**: Jordan decides there, and the decision flows into the build queue / Jordan handoff / Forge handoff. It does NOT replace those lists — it feeds them. When a box is checked, run the 6-step wiring flow below.

## Workflow (6 steps)

### 1. Check brain FIRST — 5-vertex sweep
Jordan's directive (Sep 3, 2026, BNB Build the Era): when he says "check the brain for our previous work on X", sweep ALL of these, not just one vault grep:

1. **Vault content search** — `search_files` the vault for the topic; verify with terminal grep (vault quirk: search_files can falsely return 0 hits mid-session).
2. **`/root/gentech/` kit dirs** — working code often lives OUTSIDE the vault (e.g. `bnb-hack-strategy-skill`, prior-round winner-pattern codebase). `ls` the dir, read the README.
3. **`00-HQ/council-minutes/`** — the decision trail; go/no-go items that never became builds still live here.
4. **`HQ/jordan-queue.md`** — current decision state (checked/unchecked boxes = greenlit/parked).
5. **`00-HQ/brain-snapshots/`** — latest snapshot status + deadlines.

- Topic exists → build on it, extend, reference it. Don't restart from zero.
- Related project exists (e.g. Agent Credit Score) → wire the new thing INTO it.
- Confirmed new → proceed.

### 2. Write the spec → `09-Green Room/specs/<kebab-case-name>.md`
Sections that make specs self-sufficient (Jordan reads these cold):
- **Status / Source / Vision** line at top (who, when, what triggered it)
- **TL;DR**
- **Why Now** — the trigger event and the lesson it teaches
- **Definition table** — score/factors/weights or equivalent structured core
- **Integration With Existing Stack** — table mapping to LIVE assets (x402 gateway, Agent Credit Score API, etc.). This is what makes the plan feel real vs vapor.
- **Revenue Model** — every project needs one
- **MVP Scope (Phase 1) / Phase 2 / Phase 3** — concrete, sequential
- **Open Questions**

### 3. Add flagship entry → `09-Green Room/ideas.md`
Insert at the TOP of the file (after header, before existing entries):
```
## 🏆 <Project Name> — <one-line descriptor>
**Source:** Jordan brainstorm (Mon DD) — <trigger> | **Status:** Spec complete, ready to prototype
- <factor/key bullets>
- <design principles>
- <first listing / proof-of-concept>
- Revenue: <model>
- Full spec: `09-Green Room/specs/<name>.md`
- **Needs you:** <what Jordan must do>
- [x] Add to build queue as #N
```

### 4. Add to canonical queue → `scripts/build_queue.json`
- Next sequential ID (`max(existing ids) + 1`)
- Item field schema (see `references/build-queue-json-schema.md`)
- **Reality check (verified Aug 29, 2026):** the live file is a **BARE TOP-LEVEL JSON ARRAY** — no `{items, version, summary}` envelope exists in practice. `json.load()` returns a list; code calling `.get("items")` crashes with `AttributeError: 'list' object has no attribute 'get'`. Don't "fix" the file to match the schema doc — it is canonical as-is.
- **Shipped history is RETAINED** (60 of 71 items shipped as of Aug 29) — never prune shipped items or renumber survivors; the invariant is `ids == 1..N sequential`, so after an append `max(ids) == len(items)`.
- Gate types are an open set in live use: `greenlight`, `modal_funding` — set whatever the actual human gate is.

### 5. Mirror in human-readable file → `10-Labs/build-queue.md`
The JSON is canonical; this table is what Jordan reads. Drift is the default failure
mode: the mirror once carried a duplicate #32 (Aug 2026) and once lagged the JSON by
23 rows (ended #48 vs #71, discovered Aug 29). For any drift >1 row, do NOT
hand-insert — **regenerate the whole mirror from JSON with a python table builder**
(one row per item: id, name, 🔒 gate flag, priority, emoji+status, trimmed detail
~320 chars + last `note` ~180 chars), then verify the two new rows are present and
row count == JSON item count.

### 6. Verify + sync
```bash
# file is a BARE ARRAY — iterate it directly (Aug 29 verified)
python3 -c "import json; ids=[i['id'] for i in json.load(open('/root/vaults/gentech/scripts/build_queue.json'))]; assert ids==list(range(1,len(ids)+1)), 'IDs not sequential'; print(len(ids), 'items, sequential OK')"
cd /root/vaults/gentech && ob sync
```

## Pitfalls

- **Canonical queue is JSON, not markdown.** `scripts/build_queue.json` is source
  of truth. Older skills may reference `00-HQ/build-queue.md` — that path is stale.
- **Mirror numbering drifts — and drift compounds.** `10-Labs/build-queue.md` lags
  the JSON silently because nothing writes it except wiring sessions (observed gaps:
  duplicate #32 in Aug 2026; 23-row lag ending at #48 while JSON was at #71 on Aug 29).
  After every insert, diff mirror row count vs JSON count; regenerate wholesale when
  the gap exceeds one row.
- **Human-gated items.** If Jordan must greenlight/fund/register, set
  `needs_jordan: true` + `human_gated: true` + `gate_type: "greenlight"`. The
  spec's "Needs you" line must state exactly what he does next.
- **Flip to GO the moment Jordan registers.** When Jordan says "signed up for X"
  (hackathon/Devpost/DoraHacks) or confirms a build, flip that queue item in place:
  set `needs_jordan: false`, `human_gated: false`, and append a `[Jordan REGISTERED <date> — build GO, deadline <date>]` note to the item's `note`. Then commit + push. Do NOT add a new item — the item already exists in gated state. Proven Aug 3, 2026: DataHub #30 and Keeperhub #21 were un-gated this exact way when Jordan registered.
- **Infra/debug items go on the queue with the diagnosis, not just the symptom.** When a build is blocked by an infrastructure root-cause (e.g. Paperclip embedded-Postgres root EACCES), add a queue item whose `detail` records the full root-cause chain + candidate fixes, so a later session can pick it up without re-diagnosing. `assigned_to: gentech`, `needs_jordan: false` if the fix is buildable autonomously. Proven Aug 3, 2026: Paperclip #33.
- **Don't over-analyze pre-greenlight.** A product announcement without shipped
  code is a signal, not a spec — but once HE greenlights, go deep: spec + queue
  in one pass, no second round of "should we?"
- **Hackathon green-lights don't route through this flow.** Product ideas →
  this 6-step wiring (ideas.md + build_queue.json + mirror). Hackathon GOs →
  the hackathon skill's green-light lifecycle (tracker flip → spec in
  09-Green Room/specs → 01-HANDOFFS/gentech-to-labs handoff → jordan-queue
  checkbox → registration link). Don't force a hackathon into ideas.md/build_queue.

## Support Files

- `references/build-queue-json-schema.md` — exact JSON item shape + verification snippet
- `references/decentralized-ai-marketplace-lens.md` — Bittensor/Covenant case study: failure modes to design out of any decentralized AI marketplace (kill switch, key-man risk, exit rugs, provenance)
