---
name: demo-video-production
description: "Automated demo video pipeline: html-video (HTML→MP4 via agent + 21 templates) as primary, HyperFrames for custom GSAP compositions, Remotion as legacy fallback. Natural language or GitHub repo link → polished MP4. Covers hackathon demos, product promos, portfolio showcases, and social content."
version: 2.0.0
author: Gentech
tags: [demo, video, html-video, hyperframes, hackathon, automation, ffmpeg, templates]
trigger: "When building demo videos for hackathon submissions, product demos, portfolio pieces, or social content. Also triggers when the user mentions html-video, video rendering, screen recording editing, programmatic video generation, or 'make a demo video'."
related_skills:
  - hackathon  # submission materials pipeline
  - hyperframes  # custom GSAP compositions
  - voice-content-production  # voiceover generation
---

# Demo Video Production

## Overview

Automated pipeline for creating polished demo videos. **html-video** is the primary tool — describe what you want (or paste a GitHub repo link), the agent picks a template, fills in content, and renders MP4 locally. No cloud fees, no per-render costs.

## Pipeline Selection

| Need | Tool | When |
|------|------|------|
| **Quick demo from description/link** | html-video | Default. Natural language → template → MP4 |
| **Custom GSAP animation** | HyperFrames | When you need specific motion graphics, audio-reactive, or shader transitions |
| **React-based programmatic video** | Remotion | Legacy fallback only. Complex multi-component compositions |

**Default: always try html-video first.** Only drop to HyperFrames/Remotion if html-video's 21 templates don't cover the use case.

## Primary Pipeline: html-video

### Setup (one-time)

```bash
cd /root && git clone https://github.com/nexu-io/html-video.git
cd html-video && pnpm install && pnpm -r build
```

Verify: `node packages/cli/dist/bin.js doctor` — all checks should be OK.

### Quick Reference

```bash
# Search templates by intent
node packages/cli/dist/bin.js search-templates --intent "product demo dark theme" --top 3

# Create project + set template + render
node packages/cli/dist/bin.js project-create --name "My Demo" --intent "AI agent framework promo"
node packages/cli/dist/bin.js project-set-template <project-id> --template frame-product-promo
node packages/cli/dist/bin.js project-render <project-id> --output /tmp/demo.mp4

# Launch browser studio (interactive)
node packages/cli/dist/bin.js studio --port 3071
# → http://127.0.0.1:3071
```

### 21 Templates (Apache-2.0 / MIT, license-clean)

**Data Viz:** NYT-style charts, Swiss/Vignelli grids
**Titles & VFX:** Glitch, kinetic type, typewriter cursor
**Heroes:** Liquid gradients, light-leak, warm grain
**Product Promos:** 15s/30s multi-scene
**Explainers:** Decision trees, flow diagrams

### Workflow: Description → Video

1. **Pick template:** `search-templates --intent "your description"`
2. **Create project:** `project-create --name "..." --intent "..."`
3. **Set template:** `project-set-template <id> --template <template-id>`
4. **Render:** `project-render <id> --output demo.mp4`

Or use the **studio UI** at port 3071 — pick template, chat with agent, edit frames, add soundtrack, export.

### Workflow: GitHub Repo → Video

Paste a repo URL into the studio. The agent fetches README + structure via GitHub API, generates a multi-scene explainer video automatically. Great for:
- Hackathon project explainers
- Portfolio project promos
- Open source showcases

### Soundtrack (Optional)

MiniMax integration for AI-generated music + narration:
- **Background music:** Describe a mood → MiniMax generates instrumental
- **Narration:** Type a script → MiniMax TTS
- Both mixed into exported MP4 (music ducked under voice)

No API key configured? Rest of studio works unchanged.

### Render Specs

- **Resolution:** 1920x1080 default, supports 16:9
- **FPS:** 30 default, supports 60
- **Engine:** Hyperframes (headless Chromium + ffmpeg, libx264)
- **Local only:** No cloud render, no per-clip fee

## Fallback: HyperFrames (Custom GSAP)

When html-video templates don't cover the need (custom motion graphics, audio-reactive, shader transitions):

```bash
npx hyperframes init my-video --non-interactive
npx hyperframes preview           # live preview at port 3002
npx hyperframes render --quality high --output final.mp4
```

See the `hyperframes` skill for full GSAP animation, captioning, TTS, and audio-reactive capabilities.

## Fallback: Remotion (Legacy)

Only for React-based programmatic video with complex multi-component compositions. Project at `/root/repos/hackathon-demos/`.

## Title Screen Generation

Static title screens for videos/thumbnails — render HTML to PNG via Chrome headless:

```bash
google-chrome --headless --no-sandbox --disable-gpu \
  --screenshot=/path/to/output.png --window-size=1920,1080 \
  /path/to/title.html
```

**Pitfalls:**
- Chrome headless requires `--no-sandbox` when running as root.
- **Google Fonts do NOT load in headless Chrome.** Slides render blank text. Always use system fonts: `Liberation Sans, DejaVu Sans, Arial, sans-serif` for body text, `DejaVu Sans Mono, Courier New, monospace` for code. Verify with `fc-list` what's available.
- Emoji rendering may be inconsistent — prefer text labels or simple Unicode (→, ←) over emoji in headless renders.

## Quick Slide-to-Video Pipeline

For hackathon demos where you need polished slides fast:

1. Create one HTML file per slide (1920x1080, dark theme, system fonts)
2. Render each to PNG: `google-chrome --headless --no-sandbox --disable-gpu --window-size=1920,1080 --screenshot=slide.png slide.html`
3. Create ffmpeg concat file (list each PNG with `duration 4`)
4. Combine: `ffmpeg -y -f concat -safe 0 -i concat.txt -vf "fps=30,format=yuv420p" -c:v libx264 -pix_fmt yuv420p -movflags +faststart output.mp4`

This is faster than html-video templates when you need custom content per slide. Use html-video templates when you want GSAP animations.

## Source-Clip Meme Edits (Downloaded Clip + drawtext Overlays)

Transform a downloaded source video (X/Twitter clip, TikTok, etc.) into a captioned meme short with ffmpeg drawtext — terminal boot logs, staggered captions, title/punchline cards. **Free, no model costs.** Proven: "Gentech Boot Sequence" (rowers whirlpool clip → 9 agents powering on, Jul 2026).

### Workflow

1. **Get the source clip** — for X/Twitter, fxtwitter API returns the direct mp4 URL + thumbnail:
   `curl -s "https://api.fxtwitter.com/i/status/{ID}"` → parse `media.videos[].url`, then `curl -sL` download it. Check `ffprobe` for dimensions/duration (vertical 720x1280 = reel format).
2. **Build the edit in ONE ffmpeg call** — lavfi color title card → concat with processed source:
   - Title card: `-f lavfi -i "color=c=black:s={W}x{H}:d={D}:r=30"` + drawtext centered
   - Source overlays: persistent terminal prompt (boxed), staggered caption lines with `enable='between(t,start,end)'`
   - Punchline card: `enable='gte(t,N)'`
   - Concat + encode: `[title][vid]concat=n=2:v=1:a=0[vout]`, `-c:v libx264 -crf 23 -g 48 -keyint_min 48 -pix_fmt yuv420p -movflags +faststart`
3. **Verify before delivering (MANDATORY)** — extract frames at key moments, crop the text band (`-vf "crop=720:320:0:430"`), `vision_analyze` reading text verbatim. Never ship an unverified overlay.
4. **Deploy** — `cp` to `/var/www/gentechlabs/videos/` with a FRESH filename (Cloudflare cache — see pitfall #16 below), verify `curl -sI` returns HTTP 200, deliver via `MEDIA:` path + shareable link.

Full reproducible command: `references/ffmpeg-drawtext-meme-edit-command.md`

### Pitfalls (drawtext)

- **`alpha=` expressions do NOT evaluate per-frame in drawtext.** A fade-in like `alpha='if(lt(t,30.2),0,min(1,(t-30.2)*2))'` silently renders the text invisible for the ENTIRE clip (evaluated once, not per frame). Use `enable='gte(t,N)'` for time-gated appearance — it works, proven. No per-frame alpha fades in drawtext.
- **`enable` timestamps run on the SOURCE clock BEFORE concat.** With a 2.2s title card concat'd in front, all overlay windows shift +2.2s in the final output. Verify at `final_t = source_t + title_duration`, not the intended display time — checking too early makes correct text look missing (cost two verification rounds, Jul 2026).
- **Escape drawtext text** — colons, commas, apostrophes, `%` break the filter graph. Build a bash `esc()` helper (see reference) or escape `:` and `,` with backslashes.
- **Box behind text** — `box=1:boxcolor=black@0.55:boxborderw=8` keeps captions readable over busy video (splashing water, crowd motion).
- **Mono font for terminal aesthetics** — DejaVu Sans Mono at `/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf`; check `fc-list` for alternatives.

## Dashboard Screenshots (HTML→PNG)

For data visualization dashboards that render to PNG screenshots (milestone trackers, portfolio views, agent performance cards), use the same headless browser pipeline as video production.

### Theme System

| Theme | Colors | Best For |
|-------|--------|----------|
| **Gold** | Dark + gold accents | Milestone celebrations, DeFi |
| **Green** | Dark + green accents | Position tracking, yields |
| **Cyberpunk** | Dark + neon green/blue/purple | Agent performance, tech |
| **Minimalist** | White/light + clean | Professional, reports |
| **Retro Gaming** | 8-bit, pixel art | Fun, social, squads |

### Data Binding

Use `{{variable}}` syntax for template variables:

```html
<div class="stat-value">{{position.total_usd}}</div>
<div class="progress-bar-fill" style="width:{{milestone.progress}}%">
    {{milestone.progress}}%
</div>
```

### Screenshot Generation

```python
from playwright.sync_api import sync_playwright

def generate_screenshot(html_path, output_path, width=1400, height=900):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": width, "height": height})
        page.goto(f"file://{html_path}")
        page.screenshot(path=output_path, full_page=True)
        browser.close()
    return output_path
```

### Dashboard Types

1. **Milestone Tracker** — Progress toward financial goals (position, APR, milestones)
2. **Yield Farm Detail** — Deep-dive into position mechanics (token breakdown, fees, range)
3. **Agent Performance** — What the agent is doing (status, actions, metrics)
4. **Squad Dashboard** — Competitive view for teams (leaderboard, combined stats)
5. **Celebration Card** — Milestone achievement announcement
6. **Alert Card** — Urgent notification requiring action
7. **Weekly Summary** — Periodic performance review

### Design Principles

1. Dark mode by default — better contrast for screenshots
2. Mobile-first — Telegram screenshots at 1400x900 viewport
3. Consistent branding — GenTech colors (gold/green/blue)
4. Data is visual — progress bars, composition bars, color-coded stats
5. Context matches emotion — calm for daily, exciting for celebration, urgent for alert

### Pitfalls

- **Viewport size matters** — Telegram screenshots look best at 1400x900
- **Font loading** — Local fonts may not render in headless browser; use system fonts
- **Template variables** — Always provide defaults; missing data should show "N/A" not blank
- **Color contrast** — Ensure text is readable on dark backgrounds

### Integration

- **Cron jobs** — Generate dashboard on schedule, attach PNG to Telegram message
- **Agent layer** — Generate after each action for before/after comparison
- **Hackathon submissions** — Generate demo screenshots for submission materials

---

## Social Media Engine Integration

The Social Media Engine cron (`e7b632043e30`, Wed/Sat 10am ET) generates text drafts for Gentech + Forge. To produce short-form video from those drafts, extend the pipeline with Remotion rendering on Forge's desktop (RTX 3070).

### Pipeline Flow

```
Wed/Sat 10am → Social Media Engine drafts text → saved to vault
7pm (Forge desktop) → picks up draft → Remotion renders MP4 → Entertainment group
```

### Why Forge's Desktop

Remotion renders via headless Chrome + ffmpeg. Our VPS can do it, but Forge's RTX 3070 is significantly faster. The 7pm cron on Forge's desktop means:
- Rendering happens during Jordan's evening availability
- GPU acceleration for faster encodes
- No VPS resource contention

### Setup Requirements (Forge)

1. **Remotion project** — Set up a Remotion project on Forge's desktop with video templates (talking head, code walkthrough, product demo)
2. **Template components** — React components that take the text draft as props and render frames
3. **Cron job** — 7pm daily cron on Forge's desktop that:
   - Reads the latest draft from the vault (via GitHub sync)
   - Feeds it into the Remotion template
   - Renders MP4
   - Delivers to the Entertainment Telegram group

### Template Ideas

| Template | Use Case | Duration |
|----------|----------|----------|
| Talking head | Steve Harvey-style motivational clips | 30s |
| Code walkthrough | Build-in-public, hackathon demos | 60s |
| Product demo | New feature announcements | 30-45s |
| Text overlay | Quote cards, hot takes | 15s |

### Integration Points

- **Social Media Engine cron** generates the text draft (existing, no changes needed)
- **Vault** stores the draft as a JSON file with timestamp
- **Forge's cron** picks it up, renders, delivers
- **Entertainment group** receives the final MP4

### Pitfalls

- Remotion rendering is CPU/GPU intensive — don't run during gaming sessions
- Ensure the vault is synced to GitHub before Forge's cron runs (vault sync runs every 6 hours)
- First render on a new template is slow (Chrome cache warm-up). Subsequent renders are faster.
- Remotion license: free for individuals and teams ≤3. We qualify.

## Per-Hackathon Color Themes

| Hackathon | Background | Accent | Frame |
|-----------|-----------|--------|-------|
| Somnia | Deep purple/blue | `#00d4ff` (cyan) | macbook |
| Mantle | Dark violet | `#a855f7` (purple) | browser |
| Google Rapid | Navy blue | `#4285f4` (Google blue) | macbook |
| Sui Overflow | Teal/dark | `#6dd5ed` (Sui blue) | macbook |
| Agora | Warm dark | `#f59e0b` (amber) | macbook |

## Multi-Hackathon Pattern

The same project can be demo'd across multiple hackathons with:
1. Different template/config (colors, hackathon name, tagline angle)
2. Same screen recording (if the demo is similar)
3. Different voiceover (tailor the pitch to each track's judging criteria)

This maps to the `hackathon` skill's multi-hackathon submission pattern — build once, demo everywhere.

## Quality Gate (MANDATORY)

**Do NOT publish demo videos to YouTube without review.** Public videos represent GenTech Labs brand.

Before publishing:
1. Test-render a short clip to validate pipeline
2. Review full render for: audio sync, framing quality, text readability, voiceover clarity
3. Get Jordan's explicit approval before upload
4. Write proper title, description, tags for YouTube SEO

A half-baked demo hurts more than no demo. Quality over speed.

## Pitfalls

- **Chrome headless does NOT load Google Fonts.** When rendering slides via `google-chrome --headless --screenshot`, `@import url('https://fonts.googleapis.com/css2?family=...')` silently fails — text disappears or falls back to missing glyph boxes. **Fix:** Use system fonts in headless-only HTML: `font-family: Liberation Sans, DejaVu Sans, Arial, sans-serif`. Available on VPS: Liberation Sans, DejaVu Sans, DejaVu Sans Mono, FreeSans. Google Fonts work fine in html-video (Hyperframes/Puppeteer handles font loading), but NOT in raw `--headless --screenshot` renders.
- **html-video templates have empty input schemas.** The agent generates content by modifying the HTML directly. Don't try to pass `--inputs` with custom data — the templates are agent-driven, not data-driven.
- **Studio renders are local only.** No cloud render. Ensure Chrome + ffmpeg are installed (`doctor` command checks).
- **Recording quality matters more than effects.** A clean 1080p screen recording with good audio beats fancy effects on a blurry recording.
- **Duration sync:** For Remotion fallback, get voiceover duration first (`ffprobe`), then set `durationInSeconds` in config to match.
- **Remotion license:** Free for individuals and teams ≤3. Company license required for 3+ employee orgs. We qualify for free.
- **ElevenLabs cancelled (May 2026).** Use MiniMax (html-video built-in) or Edge TTS for voiceover. Don't reference ElevenLabs in new workflows.
- **Don't force screen recording when it won't work.** If the testnet agents aren't active or the product needs a backend that isn't running, an animated explainer (html-video template) is better than a broken demo. Judges understand constraints — honesty + clean architecture beats a broken live demo.
