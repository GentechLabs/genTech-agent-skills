# Character Action Sheets for Seedance 2.0

**Discovered: 2026-08-09 — Vanito church combat film production session**

## The Problem
When animating a character with Seedance 2.0, a static keyframe (single pose) doesn't give the model enough reference for complex action sequences. The character's appearance degrades — morphing into a shadow, losing facial features, or changing proportions.

## The Solution
Generate a **multi-pose action reference sheet** showing the character in 3-5 different action poses. The model uses this as visual reference for how the character should look in motion.

## Proven Recipe

Generate via GPT Image 2 using BlockRun MCP:

```javascript
// Action sheet generation template
import { ImageClient, getOrCreateWallet } from '@blockrun/llm/dist/index.js';
import { readFileSync } from 'node:fs';

const wallet = getOrCreateWallet();
const client = new ImageClient({ privateKey: wallet.privateKey });

const charSheet = readFileSync('/path/to/character-sheet.png');
const charUri = `data:image/png;base64,${charSheet.toString('base64')}`;

const prompt = `5-panel horizontal character action reference sheet of [CHARACTER NAME]
in [SETTING]. All 5 panels show the EXACT SAME character with ZERO variation.

[FULL CHARACTER APPEARANCE DESCRIPTION]

Panel 1: [pose 1 description]
Panel 2: [pose 2 description]
Panel 3: [pose 3 description]
Panel 4: [pose 4 description]
Panel 5: [pose 5 description]

Dark anime key art, cinematic lighting, no text, no borders.`;

const result = await client.generate(prompt, {
    model: 'openai/gpt-image-2',
    size: '1536x1024',
    images: [charUri]
});
console.log(JSON.stringify(result));
```

**Cost:** ~$0.13 per sheet  
**Size:** 1536×1024 (matches Seedance 16:9 output — no stretch)  
**Important:** `client.generate()` returns data URLs (base64), not CDN URLs. Save via decode.

## Sheet Types for Full Scenes

For a complete film scene with multiple character types:

| Sheet | Panels | Use |
|-------|--------|-----|
| **Hero action sheet** | 5 poses: shooting, swinging, rolling, reloading, standing | Main character combat |
| **Shadow creature sheet** | 3 poses: attack, reeling, death | Generic enemies |
| **Boss creature sheet** | 3 poses: waiting, roaring, death | Final boss |
| **Environment plate** | 1 wide shot: empty setting | Background consistency |

Total cost for all 4 sheets: ~$0.52

## KAGE Reference Sheet (proven example)

KAGE action sheet generated 2026-08-09:
- URL: `https://blockrun.ai/api/media/media/images/2026/08/09/cd8b9d03-3b18-4e9a-abf1-c7a4c3dcdfe3.png`
- Panels: shooting Desert Eagle, swinging candlestick, diving/rolling, racking slide, standing ready
- KAGE appearance description used:

```
KAGE: jet black spiky messy hair over one eye, very pale skin,
dark guyliner and smoky eye makeup, amber-gold eyes. Long black
leather trench coat, silver chain across chest, razor blade pendant,
black t-shirt with red winged cross, black scribble tattoos on forearms.
```

## Usage in Seedance

Use the action sheet URL as the `image_url` in Seedance payload:

```json
{
  "model": "bytedance/seedance-2.0",
  "duration": 10,
  "resolution": "720p",
  "image_url": "https://blockrun.ai/.../action-sheet.png",
  "prompt": "KAGE — [full appearance] — [specific action for this clip]...",
  "aspect_ratio": "16:9"
}
```

Always include the full character description in the prompt even when using an action sheet. The sheet provides visual reference; the prompt text is the primary lock.
