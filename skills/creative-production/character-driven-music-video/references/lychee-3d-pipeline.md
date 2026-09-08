# Lychee Studio → Unreal Engine 5.8 Pipeline

## Overview
3D character pipeline for upgrading Vanito's Seedance 2.0 characters (KAGE, HIKARI) to full 3D models with Chaos Clothing physics in Unreal Engine 5.8. Forge handles the actual 3D work — this doc is the reference handoff.

## Pipeline Steps

| Step | Tool | What It Does | Cost |
|------|------|-------------|------|
| 1 | **Lychee Studio** | Generate 3D characters, clothing, props from text/images. Props Extraction breaks a character into separate game-ready pieces. | 20€/seat/mo (20K credits) |
| 2 | **Blender** | Fit, align, adjust AI-generated meshes. Sculpt mode for quick shape fixes. | Free |
| 3 | **AccuRig** | Auto-rig character, export to Unreal skeleton. | Free |
| 4 | **Unreal Engine 5.8** | Import, retarget animations, Chaos Clothing physics, build the game. | Free (5% royalty) |

## Lychee Studio Details

- **Website:** lychee-studio.ai
- **Pricing:** Starter 20€/seat/month (20,000 credits), Pro 100€/seat/month (100,000 credits)
- **Free credits:** 5,000 on signup (no credit card)
- **3D model cost:** ~500 credits each (Turbo: 200, P1+Texture: 500)
- **Key features:** Props Extraction (break character into parts), Image-to-3D, Multiview, Game Export (FBX/glTF)
- **Node types:** 19 total (2D, 3D, Video)

## Character References

Source images for KAGE and HIKARI are in the vault at:
- `/root/repos/ProtoJay4789.github.io/music/vanito/kage-hikari-reference.jpg`
- `/root/repos/ProtoJay4789.github.io/music/vanito/kage-seedance-source.jpg`
- `/root/repos/ProtoJay4789.github.io/music/vanito/hikari-kizuna-no-chikara.png`
- `/root/repos/ProtoJay4789.github.io/music/vanito/4am-crops/01-kage-closeup.png`
- `/root/repos/ProtoJay4789.github.io/music/vanito/4am-crops/02-hikari-closeup.png`

## Character Design Specs

### KAGE (current — Look 3)
- Plain black t-shirt, no jacket
- Rectangular pendant
- Full blackwork sleeve tattoos both arms
- Stratocaster with "KAGE" text
- Wet messy hair, bloody hands
- Grungier/rawer aesthetic
- Role: Screamer (anguish, raw power)

### HIKARI
- Long black hair with vibrant RED HIGHLIGHTS/STREAKS throughout (not just tips)
- Black lace choker with pendant
- Off-shoulder black corset with criss-cross lacing
- Detached black lace fingerless sleeves
- Asymmetrical black skirt with red underskirt, high slit left thigh
- Fishnets with garter strap
- Black platform boots with silver buckles
- Multiple silver rings, black arm bands
- Role: Melodic vocalist

## Target: VISUAL KEi TAP Remake

The existing rhythm game (`games/visual-kei-tap/index.html`) is a 3-lane canvas game with 6 KAGEKŌ tracks. The remake in Unreal would feature:
- 3D KAGE and HIKARI models with Chaos Clothing physics
- 3D stage with lighting, particle effects
- 3D falling notes instead of canvas rectangles
- Character idle/hit/miss/combo animations
- Capes, coats, accessories that move with physics

## Reference Video
https://youtu.be/gSHON893CCI — Full AI clothing workflow tutorial by Stefan 3D AI
