# Language Learning — Pimsleur vs Build-Our-Own (Jordan's plan, 2026-09-23)

**Jordan's plan:** use **free Duolingo** as the entry-level way to get Spanish down; for a
subscription, use **Pimsleur — because it gives access to other languages besides Spanish, and
Pimsleur also has Thai.** Separately: *"the AI conversation and all that other stuff, we could
probably just build ourselves and put our own GenTech spin on it"* — the same way the agentic
treasury came from him already being a yield farmer.

## ✅ The plan is sound in principle — and one fact nearly breaks it

**Verified against Pimsleur's own site and language table, 2026-09-23:**

| Language | Levels | Lessons | Reality |
|---|---|---|---|
| **Spanish (Latin American)** | **5** | **150** (~75 hrs) | Full track. Speakers from Colombia/Argentina (I–III), Mexico (IV). |
| **Spanish (Castilian)** | 1 | 30 | Spain variant, one level only. |
| **Thai** | **1** | **30** (~15–16 hrs) | **Exists — but it is ONE level, Level 1 only.** |

**Pimsleur's Thai is not a course, it is an introduction.** Big languages get five levels; Thai
stops at one. Sources agree: *"For Thai, Pimsleur offers only 1 level with 30 lessons… This
single-level limitation is not a design choice for minimalism; it reflects the smaller market."*
30 lessons ≈ **one month of material.**

**So the "one subscription, two countries" idea is half right:**
- **Spanish: fully justified.** 150 lessons is a real course, and it's the language he actually
  needs for the DR.
- **Thai: it will not teach him Thai.** It will give him survival phrases for the January trip —
  which is genuinely useful for a two-week visit, but it is not a path to speaking Thai.

**And Thai is genuinely hard:** FSI puts Thai in **Category IV (~44 weeks / ~1,100 class hours)**
for an English speaker to reach professional working proficiency — versus **Category I
(~575–600 hours)** for Spanish. **Spanish is roughly twice as fast to learn**, and he already has
Spanish to reactivate. That is the real argument for leading with Spanish.

## Pricing (verified 2026-09-23)

| Plan | Price | Notes |
|---|---|---|
| **All Access Monthly** | **$20.95/mo** | all ~51 languages |
| **All Access Annual** | **$164.95/yr** (~$13.75/mo) | all languages — **the right tier for his plan** |
| Premium Monthly | ~$19.95–20/mo | **one language only** — do NOT buy this for a Spanish+Thai plan |
| Lifetime All Access | ~$798 one-time (sales to ~$627) | up to 4 users; breaks even ~2.5–4 yrs |
| Per level | ~$120–160 one level | never buy this way for a multi-language plan |

**Trap to avoid:** "Premium" is *one language*. The multi-language argument he's making only holds
on **All Access**. Confirm the plan name at checkout.

## The build-our-own idea — this is where it gets interesting

**He's right that this is buildable, and it's the same shape as the treasury play.** What already
exists in the fleet:

- **`ELEVENLABS_API_KEY` is present** — ElevenLabs voice generation, with a live skill
  (`voice-generation`, `tts-production`). That is the core of any speech-practice app.
- **Agent infrastructure** — the agents already hold conversations, so an AI conversation partner
  is not a research problem, it's an assembly problem.
- **The GenTech Travels pattern** — flights + FX + cost-of-living wired into a dashboard. A
  language product would reuse that shape (tracker → feed → dashboard).

**But the honest boundary — what a DIY build does NOT replace:**

The thing Pimsleur sells is **curriculum and sequencing**, not access. Anyone can get audio; the
value is *what to hear in which order*, 150 lessons deep, with graduated interval recall built in.
A home-grown AI conversation partner with no syllabus gives you a fluent-sounding partner and no
path. **That is the "eat the meat, spit out the bones" distinction:** copy the *mechanism*
(spaced repetition + spoken drills), not the illusion that generating audio equals teaching.

**And applying the DECIDES-ALONE test:** a language app that waits for him to choose a lesson is a
toy. One that watches what he keeps getting wrong and *drills that* is an agent. Build the second.

## The recommendation

1. **Free Duolingo now** — as he planned. It's the entry-level habit and costs nothing.
2. **Do NOT buy Duolingo Max ($168/yr).** Its headline is AI conversation — the exact thing he
   intends to build. Paying for it and then rebuilding it is paying twice.
3. **If he subscribes to anything, Pimsleur All Access Annual ($164.95)** — it is the only option
   that covers Spanish *and* Thai, and All Access Monthly is only ~$6/mo less so annual wins.
   **But buy it for Spanish. Treat Thai as a survival-phrase bonus, not a course.**
4. **italki tutor (from $4/lesson)** remains the cheapest way to get *real speaking reps* while
   any DIY build is still a project.
5. **Build the GenTech version as the actual play** — because that's where his instinct was right,
   and the assets (ElevenLabs, agents, the Travels pipeline) are already in hand.

## Sequencing against his own trip calendar

- **DR trip (~Nov, 4 days):** Spanish. Duolingo free + Dreaming Spanish free now; a few italki
  sessions before he flies. Tourist Spanish is enough — the trip is the deadline.
- **Thailand (Jan/Feb, 2 weeks):** Thai survival phrases only. Do not set a fluency goal for Thai
  in four months — FSI says ~1,100 hours. Set a "get around politely" goal and hit it.


---

## ⚠️ DIALECT, NOT LANGUAGE — the correction that changed the product (Jordan, 2026-09-23)

> *"when it comes to different languages, you also got to look at different dialects. I'm going to the
> Dominican Republic, right? Well now I need to learn the Dominican dialect and how they speak Spanish very
> fast. Also, there's slang words, like K-L-K for what's up."*

**"Spanish" is not a lesson. `es-DO` is.** A learner who studies textbook Spanish and lands in Santo Domingo
hears a different language — so a generic-language lesson is the same defect as a generic corpus.

**The Dominican features that decide whether he understands anyone:**
- **S dropped** — `¿Cómo estás?` → `¿Cómo etá'?`; `los amigos` → `lo' amigo'`
- **D dropped between vowels** — any `-ado` → `-a'o`: `cansado` → `cansa'o`
- **R→L in coda** (esp. Cibao) — `amor` → `amol`, `favor` → `favol`
- **`tú` + inversion** — `¿Qué tú haces?`, not `¿Qué haces?`
- **Compression** — `voy a ir` → `voi' a ir`, `estoy` → `'toy`
- **Speed** — the fastest Spanish; mostly **missing consonants**, not tempo

**Slang worth knowing (verified):** **KLK / `¿Qué lo qué?`** (what's up), **`vaina`** (thing — the single most
useful word), `dime a ver`, `nítido` (cool), `pana`, `ya tú sabe'`, `¿cómo e' que e'?`.
*Caution: `¿Qué lo qué?` is a friends-and-peers greeting — not the first thing you say to an official.*

### Two hard-won technical rules

1. **A language name is not a voice.** Every voice on our ElevenLabs account is `lang=en`
   (`Roger`, `Sarah`, `Brian`…), so the first lesson had an **American accent reading Spanish** — the opposite
   of useful for a learner. **Pick the voice by DIALECT**, and store that mapping with the dialect.
2. **Shared-library voices are not synthesis-capable by id alone.** A direct
   `POST /v1/text-to-speech/{voice_id}` on a shared voice returns **`404 voice_not_found`**. You must first
   **add it to the account**: `POST /v1/voices/add/{public_owner_id}/{voice_id}`. The lookup that finds
   regional voices is `GET /v1/shared-voices?accent=dominican` (9 results) — and it returns a **`public_owner_id`
   that the add call requires**; a plain voice listing does not.

**Rule for the stack:** every language entry names a dialect, carries the dialect's voice, and shows the
**regional form beside the textbook form** — the contrast is the teaching.
