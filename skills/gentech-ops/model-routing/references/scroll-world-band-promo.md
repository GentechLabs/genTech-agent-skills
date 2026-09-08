# scroll-world — Band Promo Pages with Higgsfield

**Source:** oso95/scroll-world (3.2k ⭐, MIT) — https://github.com/oso95/scroll-world
**Fork:** ProtoJay4789/scroll-world

## What it does

Builds immersive scroll-scrubbed "fly through the world" landing pages using Higgsfield AI for video generation (Seedance/Kling) and GPT Image for scene stills. The camera genuinely moves through 3D-like diorama scenes driven by scroll position — no cuts, one continuous flight.

## When to use

- Creating a branded scroll-through landing page for a band, game, or product
- Need the "Apple product page" scroll effect but generated via AI
- Have access to desktop GPU (Higgsfield CLI needs local auth)
- MIT license — free to fork and adapt

## Pipeline overview

1. **Interview** — Brand kit, palette, tone, scenes, mobile support, budget
2. **Generate stills** — One per scene (GPT Image 2 via Higgsfield or Codex)
3. **Generate video legs** — "Dive-in" clips per scene + connector clips between scenes (Seedance/Kling via Higgsfield)
4. **Frame extraction** — ffmpeg to get first/last frames for seam locking
5. **Encoding** — ffmpeg to stitch and compress
6. **Scrub engine** — Vanilla JS, portable, config-driven. Blob-seek, lazy load, seam crossfade.

## Key technique — Seamless connector clips

The skill's core innovation is the "connector clip" — a video generated with frame-locking (first frame = last frame of previous scene) so the camera flight appears to move continuously through the world without cuts.

## KAGEKŌ adaptation (Jul 17, 2026)

Scene templates at `/root/vaults/gentech/Gaming/kageko-scroll-world-prompts.md`:

1. Moon Rise — Gothic castle, full moon
2. Dive Into Stage — Smoky crimson stage
3. KAGE — Guitarist, red energy
4. HIKARI — Vocalist, blue energy
5. Together — Full band performance
6. CTA — Visual Kei Tap game promo

Style: Gothic neon-night, crimson #8B0000 + deep black #0A0A0A

## Requirements

- Higgsfield CLI: `npm install -g @higgsfield/cli && higgsfield auth login`
- ffmpeg/ffprobe
- Python 3 + Pillow
- Codex CLI (optional, for free stills via ChatGPT subscription)
- Desktop GPU recommended (runs on RTX 3070)

## Installation as skill

```bash
npx skills add oso95/scroll-world
# Or manually:
cp -R scroll-world/skills/scroll-world ~/.hermes/skills/
```

## Forge handoff

This is a Forge desktop item (desktop GPU needed). See Gentech handoff `2026-07-17-kageko-scroll-world-handoff.md` for full details.
