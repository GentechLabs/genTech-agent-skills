---
name: curriculum-development
description: "Create, structure, and ship GenTech Academy curriculum modules. Covers module architecture, template packaging, README writing, and GitHub publishing workflow."
version: 1.0.0
author: gentech
tags: [academy, curriculum, documentation, module, templates, publishing]
---

# Curriculum Development — GenTech Academy

## Purpose

Ship production-grade curriculum modules for the GenTech Academy. Each module is a self-contained directory under `modules/NN-name/` in the `ProtoJay4789/gentech-academy` repo.

## Module Structure

```
modules/NN-name/
├── README.md              # Full module guide (the curriculum)
└── templates/
    ├── config.yaml        # Working template — fill in keys, deploy
    ├── script.sh          # Runnable automation
    └── example.py         # Code examples
```

## Naming Convention

- Two-digit number: `01`, `02`, `03`...
- Hyphenated slug: `put-your-ai-on-the-grid`, `consistent-visual-pipeline`
- Full path: `modules/01-put-your-ai-on-the-grid/`

## README Template

Every module README should include:

1. **Title + tagline** — What the student builds
2. **Architecture diagram** — ASCII or Mermaid showing the system
3. **Prerequisites** — What they need before starting
4. **Templates section** — Each template with a code block and explanation
5. **Quickstart** — 30-minute setup path
6. **Real-world example** — How we use this at GenTech (KAGE case study, etc.)
7. **Pitfalls** — What goes wrong and how to avoid it
8. **Next steps** — Where to go in the next module

## Publishing Workflow

```bash
cd /root/gentech-academy

# 1. Create module directory
mkdir -p modules/NN-name/templates

# 2. Write README.md
# 3. Create template files
# 4. Update root README.md with module listing
# 5. Commit and push
git add -A
git commit -m "feat: Module NN — Module Title"
git push origin main
```

## Module Inventory

| # | Module | Status |
|---|--------|--------|
| 01 | Put Your AI on the Grid | ✅ Shipped |
| 02 | Consistent Visual Pipeline | ✅ Shipped |
| 03 | Multi-Agent Architecture | ⏳ Next |
| 04 | Production-Grade x402 | 📄 Draft exists |

## What Makes a Good Module

- **Templates are the differentiator** — not just concepts, but working configs they fill in and deploy
- **Real examples** — reference actual GenTech projects (KAGE film, Vanito hub, GTA)
- **30-minute quickstart** — first success fast, depth later
- **Pitfalls section** — saves students the debugging we already did
- **Voice cloning is optional** — make it an elective module, not a required step. Students can choose to clone their voice or skip it. The core curriculum stays focused on building and shipping.
- **Lesson 1 is prompting** — the first lesson teaches students how to talk to their AI (3-step pattern: What → Where → What to say). No code, no file editing, just conversation. This is the foundational skill.
- **Tailor lessons to each student's goals** — ask what they want to learn, don't prescribe a fixed curriculum. the student builds their hub, someone else might want coding, another might want AI agents. One-size-fits-all is dead. When a student finishes Lesson 1, ask them directly: "What do YOU want to learn next?" and build the lesson around their answer.
- **Lesson 1 is always "How to Talk to Your AI"** — the 3-step pattern (What → Where → What to say). Published as a standalone HTML page at `gentechlabs.net/{name}-lesson-1.html`. Students practice by telling the AI what to change on their site, the AI makes it happen. No code, no files, just conversation.

## Conversation-Driven Development (Non-Technical Students)

For students who cannot code or edit files, the entire curriculum is **conversation-driven**:

### The Pattern
1. **Student describes what they want** in natural language (e.g., "Add a travel wishlist with Oslob, Kawasan, Simala and their costs")
2. **Agent builds it** — edits the HTML/JSON directly, no student involvement
3. **Student reviews and refines** — "Change the title to My Travel Wishlist" or "Add budget breakdown"
4. **Repeat** — each iteration adds a new section or feature

### Key Rules
- **No code, no file editing, no config changes** from the student. Zero.
- **Student provides content only** — their words, their prices, their descriptions. Agent handles all technical implementation.
- **One section at a time** — don't batch multiple sections. Let the student see each one, approve it, then move to the next.
- **Acknowledge every contribution** — when the student shares a photo, a price list, or a personal story, acknowledge it warmly before building.
- **Use their native language** — the student's native language. English for technical concepts, native language for warmth and encouragement.
- **Keep messages under 800 chars** — mobile readers, non-technical. Split long explanations into multiple short messages.
- **Price research is part of the conversation** — when a student asks "how much is X?", search, structure as a table, recommend the cheapest option, and offer to add to their wishlist. See `references/conversation-driven-hub-building.md` for the full price research pattern.
- **Emotional revelations get acknowledged, not ignored** — when a student shares something personal ("I never received flowers"), validate, affirm, and offer to capture it in their hub. See the Emotional Support Pattern in the reference file.

### Section Template (What the Student Provides)
When a student wants to add a section, they tell me:
- **What** — the content (destinations, meals, items, prices)
- **Where** — section title and placement
- **What to say** — their own words for the description

I turn that into a styled card grid with prices, icons, and descriptions — no questions asked about implementation.

### Hub Sections Built This Way (first student, Jul 27 2026)
- About Me — her personal story in her own words
- 🧳 My Travel Wishlist — 3 destinations with ₱ budgets
- 🍲 My Daily Meals — 2 recipes with ingredient tags and costs
- 🛍️ My Smart Finds — 3 household items with prices
- All photos embedded from images she shared in chat

## Multi-Language Onboarding

### When the Student's First Language Isn't English
1. **Check native language** — Jordan tells you, or the student reveals it
2. **Write in their mother tongue first** — e.g. Cebuano/Bisaya
3. **Use simple analogies** — "AI agents are like robots that help with work"
4. **Define roles concretely** — "Orchestrator = like a conductor, you tell the agents what to do"
5. **Give a concrete first step** — voice recording script, hub template, etc.
6. **End with "no pressure" and open invitation** to ask questions
7. **Code-switch naturally** — technical terms in English, warmth/encouragement in native language

## Pitfalls

- **Don't write theory without templates** — the value is in the working configs
- **Don't skip the quickstart** — students need a win in the first 30 minutes
- **Don't use product names as module names** — "Put Your AI on the Grid" not "Telegram Gateway Setup"
- **Don't forget to update root README.md** — the module listing is the table of contents
