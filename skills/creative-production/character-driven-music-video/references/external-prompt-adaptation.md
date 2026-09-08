# External Character Sheet Prompt Adaptation Pattern

> **Source session:** 2026-08-08 — Vanito shared @TechieBySA's NOVA inline skater character bible prompt and asked to adapt it for KAGE on a skateboard.

## The Pattern

When a character sheet prompt template is shared from an external source, adapt it systematically by substituting these categories — keep the **layout structure** (LEFT/CENTER/RIGHT sections) intact:

### Substitution Table

| Template Element | KAGE Substitute |
|-----------------|-----------------|
| Character name | KAGE |
| Role/archetype text | SKATEBOARDER / SHADOW ON WHEELS (or appropriate tagline) |
| Equipment (skates, etc.) | Skateboard — black deck with phoenix graphic, silver trucks, black wheels |
| Action/dynamic pose | Mid-kickflip in air, board flipping under combat boots, coat billowing |
| Color palette | CRIMSON #CC0000, DEEP BLACK #0A0A0A, NEON RED #FF2200, COLD RAIN #4488CC, SILVER |
| Art style keywords | Gothic visual kei digital painting, semi-realistic CGI, hand-painted textures, hard-edge brushwork |
| Style negations | NOT cartoon, NOT Disney, NOT Pixar, NOT photorealistic |
| Environment | Blood red moon, Tokyo skyline, dark watercolor splash in black and crimson |
| Tagline | "THE SHADOW SKATES ALONE" (or KAGE-appropriate phrase) |

### Step-by-Step Adaptation

1. **Load the definitive reference** — KAGE's Blood Moon Rising headshot + full-body images from `09-Green Room/KAGE Reference Images.md`
2. **Substitute identity** — name, role text, tagline
3. **Swap equipment** — inline skates → skateboard (or whatever equipment the concept needs)
4. **Replace color palette** — template's palette → KAGE's gothic palette (crimson, deep black, neon red)
5. **Rewrite style block** — template's art style → "gothic visual kei digital painting, semi-realistic CGI, hand-painted textures"
6. **Keep layout structure** — LEFT (hero shot), CENTER (turnaround), RIGHT (details + palette) — this is the value of the template, don't redesign
7. **Keep the prompt structure** — the multi-section format (LEFT/CENTER/RIGHT/OVERALL) produces cleaner results than a monolithic prompt
8. **Apply Rule 0.5** — always enumerate EVERY KAGE detail from the definitive reference; never guess

### Key Principles

- The template's **value is the layout structure** — it forces the model to organize a complex sheet cleanly
- **Don't copy the template's art style** — substitute KAGE's gothic visual kei style
- **The text labels** (TURNAROUND, DETAILS, COLOR PALETTE, etc.) help the model structure output
- This pattern works for ANY character sheet adaptation, not just KAGE

### Proven Example (2026-08-08)

**Source:** @TechieBySA's NOVA inline skater prompt
**Adaptation:** KAGE skateboarder (Guitarist-turned-skateboarder)
**Model:** openai/gpt-image-2 via clawrouter_image_generate
**Size:** 1536x1024
**Cost:** ~$0.13/image
**Result:** Clean character bible sheet with text labels, turnaround views, detail panels — KAGE's gothic style preserved