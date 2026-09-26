---
name: edu
description: "Use when Jordan says 'activate EDU' or needs a learning scenario."
version: 2.0.0
author: gentech
tags: [gentech-edu, agent-kit, learning, language, dialect, scenarios, travel, pack]
---

# EDU — the learning engine

**Jordan, 2026-09-23:** *"why don't we rename it to EDU? So I'll say, hey, Jintek, activate EDU and then
I'll describe what I want. I think that will work better than 'life lesson scenario' because they'll be
different, you know?"*

## ACTIVATION

**"Activate EDU"** (or "activate Jintek EDU") = start an EDU session. He then describes the subject, and
you build the scenario from **his** material. Do not ask him to choose from a menu — see the decides-alone
boundary below.

The name is deliberately general: **`life-based-language-lessons` described one pack; EDU is the engine
under all of them.** Language was the first pack, not the product.

## What EDU is (his spec, verbatim)

> *"the idea for the GenTech EDU was if you want to learn something you can just give us info and we'll
> create scenarios that help you learn and you get engaged because it's something that you care about."*

As a contract:

| Part | Meaning |
|---|---|
| **"if you want to learn something"** | ANY subject — Spanish, Thai, DeFi, how to talk to the Steward |
| **"just give us info"** | **he supplies the material** — itinerary, menu, portfolio, whatever he has |
| **"we'll create scenarios"** | practised situations, not summaries |
| **"that help you learn"** | sequenced, with the error log steering what comes next |
| **"engaged because it's something that you care about"** | **the corpus is his** — the whole moat |

## THE ENGINE / PACK BOUNDARY — the rule that keeps this from being rewritten

The engine is **subject-agnostic**. A subject is a **PACK**.

- **Engine (never subject-specific):** sequencing, mastery/error tracking, spaced repetition, rendering,
  delivery, the source loader, and **the honesty rules** — so every pack inherits them for free.
- **Pack (subject-specific):** the phrase/step bank, the dialect, the voice mapping, domain vocabulary.
  (`dialect`, `venue_type`, `menu section` are **travel-pack words**, not engine words.)
- **Adding a subject = adding a file, not editing the engine.** If it needs an engine edit, the boundary
  is wrong.

**This was a real defect:** `life-lesson-scenario.py` keys `SCENARIOS` by `(dialect, venue_type)` — Spanish
and travel in its bones. Thai or DeFi onboarding would have been a **rewrite, not an entry.** A working
feature was called an engine. Naming the boundary is the fix.

**Existing EDU work is also packs** — the Agentic Treasury onboarding docs and the DeFi milestone ladder
were hand-written before the engine existed. Retrofitting them is the obvious next cheap win.

## The layer model — how EDU combines with everything else

```
SURFACES   Travel suite · Agent Kit · gentechlabs.net · Hub boards
    ↑ surfacing
PACKS      language · travel-scenarios · treasury-onboarding · (next)
    ↑ runs on
ENGINE     EDU — generate scenarios from what you give it
    ↑ fed by
SOURCES    his itinerary · menus · APIs · the error log · whatever he hands over
              ↓
RAIL       x402 — per transaction
```

**A pack is owned by no single surface.** Language learning is a **pack on the EDU engine surfaced inside
the Travel suite**, because that is where the context is. Same engine, two doors.

**Jordan generalised this himself:** *"it's also the same way that the GenTech Hub is the engine to put the
visual data out there on a web page."* See `00-HQ/gentech-engine-architecture.md` — Hub, EDU, Treasury and
Travel are the **same machine**: `SOURCES → ENGINE → SURFACE → RAIL`. A new idea is a **pack**, not a new
product: no new funnel, no new pricing, no new payment story.

## PACKS BUILT

### LEVEL LAYER — "how good do I actually need to be?" (added 2026-09-24)

**Jordan:** *"I want to get my Spanish to a better speaking level before I go to somewhere like Santo
Domingo or Santiago or any of the other Dominican cities."*

That is a **different requirement** from the trip already priced, and the engine did not cover it. The
engine teaches the **dialect**; it had no notion of a **level**. And the level is a property of the
**place**, not of the language — `es-DO` is the same dialect in Sosúa and Santiago, but a tourist town
runs on English and a real city does not.

- **`life-lesson-level.py`** + **`data/level-targets.json`** (the level targets are
  **PACK data** — a new subject adds this file, it never edits the engine).
- **Sosúa/Cabarete/Punta Cana → A1** (tourist zone, survival is enough). **Santo Domingo/Santiago/
  La Vega/Moca → B1** (real city, conversational floor). **Thailand → A1** (Cat IV, ~1,100 hrs —
  polite survival does not fit in months).
- **Unmatched place → NO target.** It refuses to guess a default.
- Ladder = **cumulative CEFR guided hours as RANGES** (A1 90–100 · A2 180–200 · B1 350–400 ·
  B2 500–600 · C1 700–900 · C2 1000–1200), quoted as ranges — averaging them into one number is
  false precision.

### ⛔ THE LEVEL LAYER'S HARD RULES (it is the easiest place in the fleet to lie)

1. **NEVER print a CEFR level as a fact about the learner.** Phrase-bank practice cannot certify a
   level. Everything derived from it is labelled **ESTIMATE** with the basis printed.
2. **No observed practice → `UNMEASURED`.** Never a fabricated 0%, and never a default "you're A1".
3. **BANK COVERAGE IS NOT THE LEVEL** — the highest-value rule here. A learner can master **100%** of
   a 28-phrase bank and still not be A1. Report coverage and level **separately**, and say the cap out
   loud. **Conflating progress with proficiency is how a language app lies to you** — and it is the
   exact failure this product exists to beat.
4. **An unattempted phrase is NOT a miss.** Exclude it from numerator *and* denominator; counting it
   as a miss manufactures a low score out of nothing.
5. **Read the phrase bank out of the engine (`import life-lesson-engine`), never copy it.** A copied
   list drifts the moment a phrase is added, and the level check then measures a bank that no longer
   exists. Selftest check 8 guards this.

8/8 RED, synced to all 4 seats, each seat's selftest verified passing on its own machine.

| Pack | Script | What it draws on |
|---|---|---|
| **Language** (dialect-first) | `life-lesson-engine.py`, `life-lesson-audio.py` | real trips, nearest-trip-first |
| **Travel scenarios** | `life-lesson-scenario.py` | real venues, real menus, our FX rate |
| **App equivalence** | `edu_apps.py` | the need → the local app, across countries |

## APP EQUIVALENCE — the need is the unit, not the app

> *"you've got your like Kluk, for example — I know in Southeast Asia they use Kluk the same way we use
> Grubhub. So now I know food equivalence — so if I don't want to grab a moto or take an Uber somewhere, I
> could just have it delivered."*

**He is not learning app names. He is mapping a NEED he already understands onto whatever that country
calls it.** `FOOD DELIVERY → {US: Grubhub, DR: Komida, TH: Grab/LINE MAN}`. That is what makes it usable in
a country he has never visited.

**The unit is the need.** One need — *"I don't want to go out for it"* — resolves either by **riding there**
or by **having it delivered**, and knowing the equivalence is what reveals the choice.

Rules:
- **A country with no known app returns `unknown — do not assume it carries over`** — never a blank, never a
  borrowed US name. Assuming the home app works abroad is the exact error this prevents.
- **A withdrawn app stays marked dead.** foodpanda pulled out of Thailand in **May 2025** — recommending it
  would send him to a dead end.
- **Every mapping carries a status**, or it reads as an endorsement.

## The insight this is built on

Duolingo's own monetisation admits the mechanism: **AI conversation is paywalled because conversation is the
only place the app learns what you actually need.** The generated sentences are **telemetry**. They harvest
that signal and still drill everyone the same generic corpus (*"the bear drinks beer"*).

**We take the mechanism and close the loop:** collect what the learner gets wrong → drill THAT next, in
sentences drawn from his own itinerary.

**The bone to refuse:** a conversation partner with no syllabus — fluent-sounding, teaches nothing.

## DIALECT, NOT LANGUAGE — the non-negotiable

> *"when it comes to different languages, you also got to look at different dialects… I'm going to the
> Dominican Republic, right? Well now I need to learn the Dominican dialect and how they speak Spanish very
> fast. Also, there's slang words, like K-L-K for what's up."*

**"Spanish" is not a lesson. `es-DO` is.** Resolve to a **variant** (`es-DO`, `th-TH`), never a bare
language code. A generic-language lesson is the same defect as a generic corpus: content the learner cannot
use.

### Every lesson must carry three things
1. **The variant** (`es-DO`) — resolved from the destination, nearest trip first.
2. **The matching regional voice** — a language name is NOT a voice (see below).
3. **The regional form beside the textbook form** — the contrast *is* the teaching.

## THE TWO TECHNICAL TRAPS (both cost real time)

### Trap 1 — a language name is not a voice
Our ElevenLabs account's own voices are **all `lang=en`** (`Roger`, `Sarah`, `Brian`…). Using one for Spanish
produces **an American accent reading Spanish** — the opposite of useful, because the learner rehearses
phonetics that do not exist where he is going.

**Pick the voice by DIALECT**, and store that mapping alongside the dialect so a new dialect can never
silently inherit the wrong accent.

### Trap 2 — shared-library voices 404 until ADDED to the account
Regional voices live in the **shared library**, but a direct synthesis call by id returns
**`404 voice_not_found`**. Two-step path:

```bash
# 1. find them (returns the public_owner_id the add call needs)
curl -s "https://api.elevenlabs.io/v1/shared-voices?accent=dominican&page_size=10" \
  -H "xi-api-key: $ELEVENLABS_API_KEY"
# 2. ADD to the account — this is the step that is easy to miss
curl -X POST "https://api.elevenlabs.io/v1/voices/add/{public_owner_id}/{voice_id}" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" -H "Content-Type: application/json" \
  -d '{"new_name":"Anderson (DR)"}'
```

A plain voice listing does **not** include `public_owner_id` — use `shared-voices` or the add fails.

## Scenario intelligence — language learning + trip planning

> *"if I wanted to give you a scenario… I know when I go to the POP airport and I get off I'm gonna want to
> know what to say to the taxi guy… or one of the first restaurants I plan on going to is Flip Flops… that's
> what would make this next level — adding intelligence so we get language learning and trip planning
> together."*

**A scenario is not a generic dialogue.** It is built against the **actual venue, its actual menu, and the
actual price in the local currency** — which is what makes the phrase usable the moment he lands.

Rules:
- **Read the venue's real data** (own site, menu boards via `vision_analyze` on the menu images).
- **Convert prices with OUR FX tracker's latest row**, never a remembered rate — and **print the provenance**.
- **A price with no published figure is `varies`** — never `$0`, never a guess. Same for a missing FX rate:
  declare the gap, do not fall back to a stale number.
- **Record the friction, not just the phrase.** ("Agree the price before the bags go in the trunk." /
  "Staff speak English here — low-stakes practice.") That is the intelligence layer.

## The engine owns the sequence (decides-alone boundary)

- ❌ A **picker** that waits for the learner to choose a lesson — hands the decision back. The
  "calibrated confidence became *ask Jordan*" failure in a new costume. **A toy.**
- ❌ A **chatbot in a lesson frame** — adding turns to a conversation is not teaching.
- ✅ An engine that reads the itinerary, knows which trip is next, and **serves what he needs next**,
  prioritising what he keeps getting wrong. **An agent.**

## Where EDU lives

**GenTech EDU is a SECTION OF THE AGENT KIT** — the thing we offer so people learn to use the skills and the
Agentic Treasury we built. The language layer sits alongside the existing sections (Tutors / Milestones /
Activity-Hobby). **Not** a Travels feature, **not** a standalone product.

**Why it matters commercially:** the Agent Kit is the distribution surface — a language section inherits its
audience, packaging and payment rail instead of needing a new funnel. Same move as the personal-assistant
skills: *a new capability inside a stack people already buy into.*

## Scripts

| Script | Job |
|---|---|
| `edu_apps.py` | **app equivalence** — need → local app, per country; unknown never borrows |
| `life-lesson-engine.py` | lesson from real trip data; `--selftest` plants 8 failures |
| `life-lesson-audio.py` | renders the lesson in the **dialect's** voice; verifies the response is real MPEG |
| `life-lesson-scenario.py` | scenario from a **real venue** + its menu + our FX rate |
| `life-lesson-level.py` | the LEVEL layer — place → CEFR target and the honest gap; `--selftest` plants 8 failures |
| `data/travel-venues.json` | real venues, real menus, real prices (source + verified date on each) |
| `data/travel-apps.json` | which apps actually work where — source + checked date on each |
| `data/level-targets.json` | required CEFR level per zone (**PACK data** — a new subject adds this file) |

Every script has `--selftest` that **plants failures and proves each goes RED**. Run it before trusting a
change.

## Where these files live — and why it is a rule, not a preference

**One skill, one tree: `skills/edu/` — `scripts/` beside `data/`. Nothing resolves a profile path by
name.**

- **Every script derives its own SEAT from `__file__`** (`profiles/<seat>/…`), the same idiom as
  `handoff-watcher.py` — cron has no script-args field, so path-derived identity is the only
  fleet-wide mechanism. Read and write paths (`state/`, `cache/life-lessons/`, `data/`) are built from
  that, so each seat uses **its own** files.
- **The vault is the one shared exception** and says so inline (`VAULT = /root/vaults/gentech`) — trip
  data and the FX tracker are fleet-wide by design.
- **The canonical copy is the shared core: `10-Labs/skills-distribution/edu/`.** Edit the CORE, never a
  seat copy — a seat edit is a build artifact and the next `fleet_skills_sync.py` reverts it.
- **The core copy is not a seat.** Run from `10-Labs/skills-distribution/edu/` it falls back to HQ, which
  owns the core; it is there to be *synced*, not to run lessons.

**History — the three measured faults this layout closes (2026-09-25):** (1) the skill had **no core
copy**, so nothing synced it and `data/travel-apps.json` drifted on HQ alone until the drift gate went
red; (2) `edu_apps.py` and then `life-lesson-scenario.py` each read **a different file than this doc
names** — the doc/reader disagreement that hid the drift; (3) `life-lesson-{engine,audio,level}.py`
carried **`/root/.hermes/profiles/gentech` hardcoded into all four seats**, so every seat read HQ's state
and cache, and this doc's LEVEL LAYER section existed on HQ alone while the level *script* was on all
four seats. One canonical tree + a path-derived seat closes all three.

## Pitfalls

- **Renaming a language key orphans stored mastery.** Splitting `es` → `es-DO` silently reset every learner
  record to "new", so the drill loop forgot what he got wrong. **A rename is not a reason to lose data** —
  keep a legacy-key fallback when you re-key. (Selftest caught this, not review.)
- **Filename vs place-name mismatch.** Vault dirs use hyphens (`puerto-plata/`), place keys use spaces
  (`puerto plata`) — a plain `in` test **never matched**, so a country silently dropped out of the ranking.
  Normalise both sides.
- **Iteration order is not priority.** Returning the first match meant the alphabet decided the language
  (`bangkok/` beat `puerto-plata/`), serving **Thai two months early**. Rank by **nearest trip**, and prove
  order-independence with a reversed-input check.
- **Never trust a grep over a file's behaviour.** A class sweep flagged a guard as missing that was present
  under a different name. Confirm by **running it**, and check the run was not suspiciously fast.
- **A shared voice that 404s is not a missing voice** — it just has not been added to the account.

## References

- `travel-planning/references/language-learning-plan.md` — dialect phonology, verified slang, pricing tiers.
- `09-Green Room/gentech-edu/life-based-lessons.md` (vault) — the mechanism, the corrected framing, the
  Dominican feature table, and the Agent-Kit placement.
