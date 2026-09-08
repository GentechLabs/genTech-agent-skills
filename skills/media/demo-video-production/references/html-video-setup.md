# html-video — VPS Setup & Reference

## Installation (VPS: root@100.73.143.15)

```bash
cd /root && git clone https://github.com/nexu-io/html-video.git
cd html-video && pnpm install && pnpm -r build
```

**Prerequisites:** Node.js 22+, ffmpeg, Chrome/Chromium (all pre-installed on VPS).

## Running

```bash
# CLI commands
cd /root/html-video
node packages/cli/dist/bin.js doctor                    # verify environment
node packages/cli/dist/bin.js search-templates --intent "..." --top 3
node packages/cli/dist/bin.js project-create --name "..." --intent "..."
node packages/cli/dist/bin.js project-set-template <id> --template <template-id>
node packages/cli/dist/bin.js project-render <id> --output /tmp/demo.mp4

# Studio (Browser UI)
node packages/cli/dist/bin.js studio --port 3071
# → http://127.0.0.1:3071 (or http://100.73.143.15:3071 via Tailscale)
```

**⚠️ Studio binds to 127.0.0.1 by default.** For remote access (Tailscale), patch the bind address:
```bash
sed -i "s/server.listen(port, '127.0.0.1'/server.listen(port, '0.0.0.0'/" \
  /root/html-video/packages/cli/dist/studio-server.js
```
This patch survives `pnpm -r build` but not a `git pull`. Re-apply after updating.

## Systemd Service (Persistent Studio)

```bash
cat > /etc/systemd/system/html-video-studio.service << 'EOF'
[Unit]
Description=html-video Studio
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/html-video
ExecStart=/usr/local/bin/node packages/cli/dist/bin.js studio --port 3071
Restart=always
RestartSec=5
Environment=HOME=/root
Environment=PATH=/usr/local/bin:/usr/bin:/bin

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable html-video-studio
systemctl start html-video-studio
```

## Template Categories

| Category | Templates | Best For |
|----------|-----------|----------|
| product-demo | frame-product-promo, frame-product-promo-30s | Hackathon demos, product showcases |
| presentation | frame-bold-signal | Title cards, chapter dividers |
| data-viz | frame-data-chart-nyt | "The number went up" stories |
| title-vfx | frame-glitch-title, vfx-text-cursor | Openers, system-online energy |
| hero | frame-liquid-bg-hero | Product reveals, bold statements |
| cinematic | frame-light-leak-cinema | Mood, brand films, storytelling |
| outro | frame-logo-outro | End cards, brand stamps |

## Key Differences from Remotion

| Aspect | html-video | Remotion |
|--------|-----------|----------|
| Authoring | HTML/CSS/JS (agent-driven) | React components (TSX) |
| Input | Natural language or URL | Config JSON + screen recording |
| Templates | 21 curated, license-clean | Custom per project |
| Voiceover | MiniMax (built-in) | ElevenLabs (cancelled) |
| Render | Hyperframes (Chromium + ffmpeg) | Remotion CLI |
| Cost | Free, local | Free for ≤3 devs |
| Agent integration | Built-in (Hermes, Claude, Codex) | Manual |

## VPS Disk Impact

- Clone + build: ~200MB
- Per project: varies (10-50MB depending on templates/assets)
- Rendered MP4s: 5-50MB each depending on duration/quality

## Source Fetching

html-video can fetch content server-side:
- **Web articles** → flattened to Markdown
- **GitHub repos** → README + structure via public API
- **WeChat articles** → server-rendered pages work out of the box

No copy-pasting article bodies — the agent reads the fetched content directly.
