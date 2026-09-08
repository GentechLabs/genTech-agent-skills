# ACE-Step Music Generation Pipeline

## Overview

ACE-Step UI (4.5K stars, MIT) is an open-source Suno alternative for local AI music generation. Runs the ACE-Step 1.5 model on your own GPU — free, unlimited, no API costs. Cloned at `/root/ace-step-ui/`.

## Cost Model (for explaining to Vanito / Entertainment group)

| Question | Answer |
|----------|--------|
| Does it cost per track? | **No.** Zero per-track fees. No subscriptions. |
| Does it need a cloud GPU (BlockRun)? | **No.** Runs on Forge's local desktop GPU only. |
| What's the actual cost? | **Electricity only** — same as running a game. |
| Can you use it on your phone? | **Not directly.** Forge generates on desktop, uploads the finished track. |
| How fast? | Forge picks up the prompt, generates (~1-5 min), delivers within the hour. |

**Why it's free:** ACE-Step runs the AI model **locally** on your own GPU. You download the model once (~several GB), and from then on every song costs exactly $0 in API fees. No per-track billing, no monthly subscription, no BlockRun charges.

This is different from cloud AI tools (BlockRun, ElevenLabs, OpenAI) where each API call costs money. ACE-Step is more like installing a game — you pay for the hardware once, then play unlimited.

## GenTech Use Cases

| Use Case | Description | Status |
|----------|-------------|--------|
| **Arcade cabinet soundtracks** | Per-cabinet background music (combat tracks for Agent Warfare, upbeat for Tennis, high-energy for DogFighters) | 🏗️ Planned |
| **Menu themes** | Arcade entrance music, cabinet select screen, settings menu | 🏗️ Planned |
| **Demo video soundtracks** | Custom music for hackathon submissions — no copyright risk | 🏗️ Planned |
| **GenTech branding** | Jingle, intro/outro music for demos and social content | 🏗️ Planned |
| **Vanito / Entertainment group** | Custom tracks for KAGE films, social media content | 🏗️ Planned |

## Architecture

```
Vanito/Entertainment → prompt in Telegram → Forge (desktop GPU) → ACE-Step 1.5 → WAV/MP3 → vault/arcade server
```

- **Generation:** Requires GPU (Forge's desktop). Not available on VPS.
- **Playback:** CPU-only. Generated tracks play on any device.
- **Cost:** $0 per track. Electricity only.
- **Trade-off:** Not instant like cloud APIs. Forge processes prompts in batch.

## Related

- `arcade-cabinet` skill — wiring generated tracks into arcade cabinets
- HF Speech-to-Speech at `/root/speech-to-speech/` — pairs with ACE-Step for voice + music audio pipeline
