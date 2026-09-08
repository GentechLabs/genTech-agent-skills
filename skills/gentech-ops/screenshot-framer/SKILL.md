---
name: screenshot-framer
description: "Capture screenshots of web pages and frame them in device mockups (phone/laptop/tablet/desktop) with branded overlays. Batch mode for asset libraries. Output ready for X posts, decks, and Academy materials."
version: 1.0.0
author: gentech
tags: [screenshot, mockup, device-frame, branding, asset-generation, social-media]
---

# Screenshot Framer — genTech-frame

## Purpose

Turn raw URLs or screenshots into polished device mockups with consistent branding. Used for Academy materials, social posts, hub screenshots, and deck assets.

## Tool Location

`/root/genTech-frame/` — GitHub: `ProtoJay4789/genTech-frame`

## Quick Start

```bash
cd /root/genTech-frame

# Single URL → laptop frame + gentech branding
python3 frame.py shot https://gentechlabs.net --device laptop --brand gentech

# Vanito's hub → laptop frame + vanito branding
python3 frame.py shot https://vanito.gentechlabs.net --device laptop --brand vanito

# Local screenshot (skip Playwright capture)
python3 frame.py shot path/to/image.png --device phone --brand academy --no-capture

# Batch all hubs from a URL list
python3 frame.py batch urls.txt --device laptop --brand gentech -o output/hubs/
```

## Devices

| Name | Aspect | Use Case |
|------|--------|----------|
| `laptop` | 16:10.5 | Hub screenshots, dashboards |
| `phone` | 9:19.5 | Mobile views, social media |
| `tablet` | 4:3 | App demos, portfolios |
| `desktop` | 16:9 | Full-page captures, decks |

## Brands

| Name | Accent | Tagline |
|------|--------|---------|
| `gentech` | #3b82f6 | Agent Economy Infrastructure |
| `vanito` | #cc0000 | Music · Games · Creation |
| `academy` | #8b5cf6 | GenTech Academy |

Add new brands by creating `brands/<name>.yaml` with `name`, `accent`, `tagline` fields.

## Output

Each framed image includes:
- Device bezel with proper screen cutout
- Screenshot centered inside the screen area
- Semi-transparent bottom bar with brand name + tagline + source URL
- Accent-colored border

## Batch Mode

```bash
# From URL list (one per line)
echo "https://gentechlabs.net
https://vanito.gentechlabs.net
https://gentechlabs.net/jordan.html" > urls.txt
python3 frame.py batch urls.txt --device laptop --brand gentech -o output/hubs/

# From image directory
python3 frame.py batch screenshots/ --device phone --brand academy -o output/batch/
```

## Architecture

```
frame.py (CLI entrypoint)
├── frame_lib/
│   ├── screenshot.py    — Playwright headless capture
│   ├── framer.py        — SVG device overlay engine
│   ├── brand.py         — Logo, accent, label bar
│   └── batch.py         — Batch processor
├── devices/*.svg        — Device frame SVGs
└── brands/*.yaml        — Brand configs
```

## Dependencies

```bash
pip install pillow pyyaml playwright cairosvg
playwright install chromium
```

## Upstream Contribution

The `frame_lib/framer.py` renderer is designed to be extracted as a standalone `pip install device-frame` package. Once stable, PR the frame rendering logic to [Tokokino](https://github.com/ShivaBhattacharjee/Tokokino) — giving their interactive editor a programmatic output path.

## Pitfalls

- **File permissions**: Output files inherit the running user's umask. If deploying to nginx, chmod 644 + chown www-data.
- **Playwright timeout**: Some pages take >30s to load. Increase `timeout` in `screenshot.py` for heavy SPAs.
- **SVG screen detection**: Device SVGs must have a `<rect id="screen">` or `data-role="screen"` element. The framer scans for it — if missing, falls back to the largest rect.
- **cairosvg required**: SVG rendering needs `cairosvg`. Without it, the framer uses a simple bezel fallback (works but less polished).
