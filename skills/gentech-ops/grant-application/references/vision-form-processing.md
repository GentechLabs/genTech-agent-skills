# Vision-Based Form Processing for Applications

A repeatable pattern for processing application/fellowship forms that the user shares as screenshots.

## When to Use

The user sends screenshots of an application form (fellowship, grant, accelerator, job) and asks you to:
- "Read the form"
- "Check the questions"
- "Brainstorm answers"
- "Help me fill this out"

## Workflow

### Step 1: Read the Form with Vision

Use `vision_analyze` on each screenshot the user sends. The form may span multiple images.

**Process each image:**
```python
vision_analyze(image_url="<path>", question="List every form field, question, and field type visible.")
```

**Wait for the user to send all images** — don't jump to drafting after the first screenshot. Say "Waiting on image 2 👀" or similar.

**What to extract:**
- Section headers and structure
- Every question (required vs optional)
- Field types (text input, dropdown, textarea, checkbox, radio)
- Character limits (e.g., "under 1000 characters")
- Help text / subtitles
- Pre-filled values the user already entered
- Any checkboxes already checked

### Step 2: Map Questions Against Vault Data

Before proposing answers, **check the vault for the user's real work:**

**Priority order:**
1. **`09-Green Room/`** — Current project docs, drafts, submissions
2. **`10-Labs/`** — Build queue, technical projects, active work
3. **`projects.json`** — Canonical project list with GitHub URLs and descriptions
4. **`06-Content/portfolio-canonical.html`** — Portfolio / bio info
5. **`03-Strategies/`** — DeFi positions, financial metrics
6. **Recent `build-queue.md`** — What's been shipped recently
7. **Grant/application drafts** — Previously saved drafts (e.g., `spc-fellowship-draft.md`, `circle-developer-grant-application.md`)

**Cross-reference:** For each form question, identify which vault source provides the best answer.

### Step 3: Present a Status Map

Before drafting full answers, show the user a **mapped table** of what you found:

```
| Form Field | Status | Source |
|-----------|--------|--------|
| Proudest achievement | ✅ [project] | [vault file] |
| Phone number | ❌ Need from user | — |
| Problem space | ✅ [elevator pitch] | [draft file] |
```

Mark what's filled vs what needs user input. Ask for blanks.

### Step 4: Draft Answers Grounded in Shipped Work

**Key rule:** Every answer must reference real, deployed, working infrastructure — not hypotheticals.

**Good sources of truth:**
- Live endpoints (api.gentechlabs.net/*)
- GitHub repos (github.com/ProtoJay4789/*)
- On-chain contracts with explorer links
- Specific numbers (16+ endpoints, 6 positions, 22/22 tests)
- Hackathon submissions with dates and results
- Grant approvals with amounts

**Avoid:**
- "We're building X" — say "We've shipped X" instead
- Vague timelines — use specific dates
- Generic descriptions — name the chains, protocols, and repos

### Step 5: Iterate

- Present drafts one field at a time or grouped by section
- Ask for missing data (phone, referral source, etc.)
- Offer to save the draft to vault when done

## Example: SPC Fellowship (Jul 30, 2026)

The SPC application had three screenshot groups:
1. **Image 1** — First 3 questions: progress on idea + artifact links, who would you recruit, anything else
2. **Image 2** — Full form: About You section (name/email/phone/LinkedIn/location/referral), Background (proudest work + link, 2-3 artifacts), Fundraising (team?, raised?, problem space, why you?)

**Vault sources used:**
- `09-Green Room/spc-fellowship-draft.md` — Previous draft
- `09-Green Room/circle-developer-grant-application.md` — Comprehensive project summary
- `projects.json` — Canonical project list
- `10-Labs/build-queue.md` — Recent progress

## Pitfalls

### Pitfall 1: Jumping to answer after first image

The form may span multiple screenshots. Wait for all images before drafting.

### Pitfall 2: Writing generic answers

Every answer must reference shipped work. If the vault doesn't have a match, search session history or ask the user.

### Pitfall 3: Forgetting to ask for personal info

Forms often ask for: phone number, email, referral source, location, LinkedIn — things the vault won't have. Flag these as blanks.

### Pitfall 4: Using outdated metrics

Always check the most recent vault files. Grant applications, build queue, and project status can change weekly.
