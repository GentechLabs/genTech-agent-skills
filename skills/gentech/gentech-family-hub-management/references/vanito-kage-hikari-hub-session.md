# Vanito's KAGE × HIKARI Hub Session — 2026-07-09

## What was built

- **Artists tab** on `hub-vanito.html` — dedicated 🎭 tab with KAGE and HIKARI character bios
- **Dynamic header** — switches from normal gradient header to KAGEKŌ album cover when on Artists tab
- **Tab theming** — dark `#0d0d0d` background, red/gold card styling matching album art aesthetic
- **Native audio players** — `<audio controls>` on each character card (works in Telegram browser)

## Characters

| Character | Voice | Color | Song |
|-----------|-------|-------|------|
| KAGE (影) | Screaming male, post-hardcore | Red (#cc2222) | Fight Forever Never Quit |
| HIKARI (光) | Melodic female, J-rock | Red (#cc3333, updated from gold) | Mirai e Hashire |
| KAGE × HIKARI | Duet | Crimson/elemental | In the Darkness We Rise |

## Album: KAGEKŌ (影光)
Shadow-Light. Split composition album cover — KAGE dark/crimson left, HIKARI golden light right, jagged divide.

## Key Technical Details

### Image editing
- blockrun_image(action="edit") with local file path in `image` param (not `image_url`)
- Removing text from artwork: exhaustive prompt listing every text element, then verify with vision_analyze
- Adding text to artwork: same tool, but prompt describes new text placement, style, color
- Cost: ~$0.06-0.12 per edit

### Dynamic header gotchas
- .header CSS class MUST be on the header div for normal state styling
- innerHTML swap removes addEventListener-bound handlers — use inline onclick for critical buttons
- Setting `header.className = 'normal-header'` WITHOUT 'header' broke ALL tab headers visually

### Audio playback
- `<audio controls>` native element works on all devices including Telegram browser
- `onclick="document.getElementById('id').play()"` on images — works on some browsers, fails silently on Telegram in-app browser
- `new Audio(url).play()` — least reliable, avoid

### Character bio format
- Compact prose bio (not wall-of-text) → audio player → style tags
- Together card: origin story in 2-3 sentences → duet audio player → DUET/ALBUM/COLLAB badges
- Gold/yellow color was replaced with red throughout to match the dark album theme

## GitHub state
- Repo: ProtoJay4789.github.io
- Hub file: hub-vanito.html
- Music JSON: hub-vanito-data.json
- Audio dir: music/vanito/
- Cache: pushed with cache-control meta tags for fresh content