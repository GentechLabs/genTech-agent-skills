---
name: hermes-web-bridge
description: "Build lightweight web interfaces that communicate with Hermes via the CLI bridge pattern. Covers voice-powered UIs for constrained devices (Ray-Ban glasses, mobile browsers), FastAPI backend servers using `hermes chat -q`, systemd service deployment, and here.now publishing. Use when building any external interface — web, mobile, or voice — that needs to talk to Hermes without going through a messaging platform."
version: 1.0.0
author: GenTech Labs
license: MIT
tags: [web, bridge, voice, ray-ban, fastapi, hermes-cli, external-interface]
---

# Hermes Web Bridge

Build lightweight web interfaces that communicate with Hermes directly via the CLI, bypassing messaging platforms entirely.

## When to Use

- Building a web chat interface for Hermes
- Creating voice-powered UIs for constrained devices (smart glasses, mobile)
- Any external interface that needs Hermes responses without Telegram/Discord
- Rapid prototyping of Hermes-connected web apps

## Architecture

```
Browser (Ray-Ban / Mobile / Desktop)
    ↓ HTTP POST /api/chat
FastAPI Bridge Server (port 8765)
    ↓ subprocess: hermes -p <profile> chat -q "message" -Q
Hermes Agent (CLI mode)
    ↓ returns response text
Bridge Server → HTTP response → Browser
```

**Key insight:** `hermes chat -q` is a full Hermes session in a single command. It returns the response text directly. No gateway, no Telegram, no polling needed.

## The CLI Bridge Pattern

### Core Implementation

```python
import asyncio
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

async def ask_hermes(message: str, session_id: str = None) -> dict:
    """Send a message to Hermes and get the response."""
    cmd = ["hermes", "-p", PROFILE, "chat", "-q", message, "-Q"]
    if session_id:
        cmd.extend(["--resume", session_id])
    
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=120)
    
    output = stdout.decode().strip()
    new_session_id = session_id
    response_text = output
    
    # Parse session_id from first line
    if output.startswith("session_id:"):
        lines = output.split("\n", 1)
        new_session_id = lines[0].replace("session_id:", "").strip()
        response_text = lines[1].strip() if len(lines) > 1 else ""
    
    return {"response": response_text, "session_id": new_session_id}
```

### Session Continuity

Hermes maintains context across messages via `--resume <session_id>`:
1. First call: no session_id → Hermes creates new session, returns session_id in output
2. Subsequent calls: pass session_id → Hermes resumes that session with full context
3. Session IDs format: `YYYYMMDD_HHMMSS_XXXX`

### Timeout Handling

Set `asyncio.wait_for(proc.communicate(), timeout=120)` — Hermes can take 5-30s for complex queries. Cold starts are slower (~10s). Subsequent messages are faster (~5-8s).

## Web UI Constraints (Ray-Ban / Small Displays)

### Design Rules

- **Pure black background** (#000000) — saves battery on OLED displays (Ray-Ban)
- **High-contrast text** (#e8e8f0) with accent (#00ff88) for interactive elements
- **HUGE tap targets** for pinch gestures — **120px minimum** for primary buttons on Ray-Ban (42px is too small for pinch)
- **Font size** 14-15px minimum for body text
- **Max-width 88vw** for message bubbles
- **touch-action: manipulation** and **-webkit-tap-highlight-color: transparent** on all buttons
- **Minimal CSS** — no frameworks, no heavy dependencies, no scrollbars
- **Single-purpose layout** — one big button beats a complex toolbar on tiny displays

### Voice Mode: Toggle, Not Auto-Send

Ray-Ban users expect tap-to-start, tap-to-stop — NOT auto-send after silence:

```javascript
rec.continuous = true;  // Keep listening until user taps again
// On tap: start recording
// On second tap: stop + send
// Show "🔴 Listening — tap to stop & send" while recording
```

Auto-send feels broken on constrained devices because the speech recognition
cuts off mid-sentence. Toggle mode gives the user control.

### Handwriting Canvas

For devices where typing is impractical, add a drawing canvas:

```javascript
// Full-width canvas with pen/eraser/clear tools
// Convert to PNG data URL: canvas.toDataURL('image/png')
// Send to server as base64
// Server saves temp file, asks Hermes to read it via vision
```

Server endpoint pattern:
```python
@app.post("/api/draw")
async def api_draw(request):
    # Save base64 image to /tmp/draw_*.png
    # Ask Hermes: "Read this handwriting: [path]"
    # Return the transcribed text
```

### Voice Input Pattern (Toggle Mode)

```javascript
const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
let listening = false, finalBuf = '';

if (SR) {
    const rec = new SR();
    rec.continuous = true;   // Keep listening until user taps again
    rec.interimResults = true;
    rec.lang = 'en-US';

    rec.onstart = () => {
        listening = true;
        finalBuf = '';
        // Show "🔴 Listening — tap to stop & send"
    };
    rec.onresult = (e) => {
        let interim = '';
        for (let i = e.resultIndex; i < e.results.length; i++) {
            if (e.results[i].isFinal) finalBuf += e.results[i][0].transcript + ' ';
            else interim += e.results[i][0].transcript;
        }
        // Show live transcript: finalBuf + interim
    };
    rec.onend = () => { listening = false; };
}

// Toggle: tap once = start, tap again = stop & send
micBtn.addEventListener('click', () => {
    if (listening) {
        rec.stop();
        const msg = finalBuf.trim();
        if (msg) sendMessage(msg);
    } else {
        try { rec.start(); } catch(e) {}
    }
});
```

### Auto-Send After Voice (DEPRECATED)

Do NOT use auto-send on constrained devices. Speech recognition cuts off
mid-sentence and users lose control. Use toggle mode instead.

## Deployment

## Deployment

### Systemd Service

```ini
[Unit]
Description=Gentech Bridge Server
After=network.target

[Service]
Type=simple
WorkingDirectory=/path/to/project
ExecStart=/usr/local/lib/hermes-agent/venv/bin/python3 server.py
Restart=always
RestartSec=5
Environment=BRIDGE_PORT=8765
Environment=HERMES_PROFILE=gentech

[Install]
WantedBy=multi-user.target
```

Deploy:
```bash
python3 -c "
content = '''[Unit]...
'''
with open('/etc/systemd/system/gentech-bridge.service', 'w') as f:
    f.write(content)
"
systemctl daemon-reload && systemctl enable gentech-bridge && systemctl start gentech-bridge
```

**Note:** Use `python3 -c` to write service files, not heredocs — heredocs can hang in terminal tool.

### Tailscale Deployment (HTTPS-Free Alternative)

When both devices are on the same **Tailscale tailnet**, no Cloudflare tunnel is needed:

```bash
# 1. Find VPS Tailscale IP
tailscale ip -4   # e.g. 100.x.x.x

# 2. Deploy bridge server on VPS (bound to 0.0.0.0)
cd /root/hermes-bridge && python3 server.py

# 3. Client accesses via Tailscale IP
# http://100.x.x.x:8765
```

**Why Tailscale instead of Cloudflare tunnel:**
- No random URLs that change on restart
- No Cloudflare account needed
- Lower latency (direct peer-to-peer)
- Tailscale encrypts the mesh — no separate HTTPS needed for internal use

**Requirements:**
- Tailscale on both VPS and client (`tailscale status` to verify)
- Bridge server bound to `0.0.0.0` (default)
- Systemd service with `After=tailscaled.target` for boot-order safety

**Proven Jul 15, 2026:** Bridge deployed on VPS at `100.73.143.15:8765`, accessed from Unihertz Titan (`titan-2`) on same tailnet. Full Hermes chat session via `hermes chat -q` bridge. Survives reboots via systemd `gentech-bridge.service`.

### Tailscale Deployment (HTTPS-Free Alternative)

When both devices are on the same **Tailscale tailnet**, no Cloudflare tunnel is needed:

```bash
# 1. Find VPS Tailscale IP
tailscale ip -4   # e.g. 100.x.x.x

# 2. Deploy bridge server on VPS (bound to 0.0.0.0)
cd /root/hermes-bridge && python3 server.py

# 3. Client accesses via Tailscale IP
# http://100.x.x.x:8765
```

**Why Tailscale instead of Cloudflare tunnel:**
- No random URLs that change on restart
- No Cloudflare account needed
- Lower latency (direct peer-to-peer)
- Tailscale encrypts the mesh — no separate HTTPS needed for internal use

**Requirements:**
- Tailscale on both VPS and client (`tailscale status` to verify)
- Bridge server bound to `0.0.0.0` (default)
- Systemd service with `After=tailscaled.target` for boot-order safety

**Proven Jul 15, 2026:** Bridge deployed on VPS at `100.73.143.15:8765`, accessed from Unihertz Titan (`titan-2`) on same tailnet. Full Hermes chat session via `hermes chat -q` bridge. Survives reboots via systemd `gentech-bridge.service`.

```bash
PUB="/root/.hermes/profiles/gentech/skills/productivity/here.now/scripts/publish.sh"
cd /path/to/project && /bin/bash "$PUB" index.html --client hermes --slug <slug>
```

**Pitfall:** The publish script sometimes fails with bare `bash` invocation. Use `/bin/bash` explicitly or run from the project directory.

### Hybrid Architecture

For external devices that can't reach the VPS directly:
- **Static UI** → here.now (CDN, accessible anywhere)
- **Backend** → VPS port (needs public IP or tunnel)
- **API_BASE** in HTML → hardcode VPS IP: `http://<PUBLIC_IP>:8765`

## Pitfalls

1. **Telegram long polling conflict:** Only ONE client can use `getUpdates` on a Telegram bot at a time. If the Hermes gateway is already polling, your bridge server CANNOT also poll for responses. **Solution:** Use `hermes chat -q` directly — no Telegram relay needed.

2. **Session ID parsing:** The `-Q` flag outputs `session_id: <id>\n<response>`. Parse the first line for the session ID, the rest is the response. If you forget `-Q`, you get verbose output mixed with response.

3. **Cold start latency:** First `hermes chat -q` call takes 5-10s (session initialization). Subsequent calls are faster (3-5s). Warn users about initial delay.

4. **Concurrent requests:** Multiple simultaneous `hermes chat -q` calls may conflict if they try to resume the same session. Use separate session IDs per user.

5. **Hermes profile env:** The bridge server must set `HERMES_PROFILE` env var or pass `-p <profile>` explicitly. Without it, Hermes uses the default profile.

6. **here.now anonymous expiry:** Sites without API keys expire in 24 hours. Claim with a here.now account for permanence.

7. **HTTPS required for constrained browsers:** Ray-Ban Meta glasses (and many mobile browsers) require HTTPS — they won't load HTTP pages at all. An HTTP URL like `http://2.24.195.196:8765` shows "URL must have HTTPS" error. **Fix:** Use a Cloudflare Tunnel for instant HTTPS:
   ```bash
   cloudflared tunnel --url http://localhost:8765
   # Outputs: https://random-name.trycloudflare.com
   ```
   For persistent tunnels, create a systemd service. Quick tunnels (no account) generate random URLs that change on restart. For permanent URLs, use a named tunnel with a Cloudflare account.
   **Verified:** Jun 15, 2026 — Ray-Ban Meta browser rejected HTTP, Cloudflare Tunnel fixed it.

8. **Mixed content blocking:** HTTPS pages cannot make API calls to HTTP backends. If you publish the UI on here.now (HTTPS) but the backend is HTTP, all fetch requests fail silently. **Fix:** Either (a) serve the page from the same origin as the API (direct VPS URL), (b) use Cloudflare Tunnel for the backend, or (c) detect in JS and auto-redirect:
   ```javascript
   const API_BASE = (location.port === '8765') ? '' : `http://${location.hostname}:8765`;
   ```
   When served from the bridge server directly, use same-origin (`''`). When served from here.now, the backend must be HTTPS.

10. **Button size for pinch gestures:** 42px buttons are too small for Ray-Ban pinch interaction. Users report they "can't tap" the button. **Fix:** Use 120px minimum for primary action buttons. The button should dominate the bottom of the screen. Secondary buttons (pen/eraser/send) can be smaller (40-50px) but still need generous padding.

11. **Voice auto-send feels broken:** Speech recognition with `continuous: false` cuts off mid-sentence on constrained devices. Users lose control and can't review before sending. **Fix:** Use `continuous: true` with toggle mode — tap to start, tap to stop and send. Show "🔴 Listening — tap to stop & send" while recording.

9. **systemd service files via heredoc:** Writing systemd service files via bash heredocs in the terminal tool can hang or get killed (SIGTERM). **Fix:** Use `python3 -c` to write the file instead:
   ```python
   python3 -c "
   with open('/etc/systemd/system/my-service.service', 'w') as f:
       f.write('''[Unit]\\n...\\n''')
   "
   ```

10. **Cloudflare Workers OAuth fails on VPS:** `wrangler login` uses browser-based OAuth that redirects to localhost. On a headless VPS, the OAuth callback cannot reach the browser, causing authentication to fail or timeout. **Fix:** Use API token authentication instead:
    ```bash
    # Create API token at https://dash.cloudflare.com/profile/api-tokens
    # Permissions: Account - Workers Scripts: Edit, Zone - Workers Routes: Edit
    export CLOUDFLARE_API_TOKEN=your_token_here
    wrangler deploy worker.js
    ```
    **Critical:** The API token must include zone permissions (`Zone - Workers Routes: Edit`) to configure custom domain routes. Without zone permissions, `wrangler deploy` will upload the worker but fail to attach routes, leaving custom domains unreachable (522 errors).

11. **Custom domain routes require dashboard configuration:** Even with correct API token permissions, custom domain routes (e.g., `deals.gentechlabs.net/*`) must be manually configured in the Cloudflare Workers Dashboard → Triggers tab. The CLI can upload worker code but cannot fully configure zone-level route bindings. **Fix:** After deploying worker, go to dashboard, add custom domains to worker triggers, then test endpoints.

12. **Bridge can time out after extended use:** The server's `hermes chat -q` subprocess has a 120-second timeout barrier. After many messages in a session, cold Hermes response times can drift past this. **Fix:** On the frontend, add a periodic keepalive/heartbeat ping (e.g., `GET /api/health` every 30s) and on the backend, raise the subprocess timeout or implement streaming response. Proven Jul 15, 2026 — Jordan's Unihertz Titan session timed out after ~15 minutes of active conversation.

13. **User preference: Web Bridge over Telegram for the "Gentech feeling":** Jordan explicitly prefers the branded web bridge UI over Telegram for direct agent conversation. The bridge provides a personalized, dark-themed experience that feels like talking to his own agent rather than a generic messaging platform. When both are available, treat the bridge as the primary conversation interface and Telegram as fallback.

14. **Full path to hermes binary required in subprocess:** When running `hermes chat -q` from a systemd service or non-interactive subprocess, the PATH may not include the Hermes venv. Always use the absolute path:
    ```python
    cmd = ["/usr/local/lib/hermes-agent/venv/bin/hermes", "-p", PROFILE, "chat", "-q", message, "-Q"]
    ```

12. **Bridge can time out after extended use:** The server's `hermes chat -q` subprocess has a 120-second timeout barrier. After many messages in a session, cold Hermes response times can drift past this. **Fix:** On the frontend, add a periodic keepalive/heartbeat ping (e.g., `GET /api/health` every 30s) and on the backend, raise the subprocess timeout or implement streaming response. Proven Jul 15, 2026 — Jordan's Unihertz Titan session timed out after ~15 minutes of active conversation.

13. **User preference: Web Bridge over Telegram for the "Gentech feeling":** Jordan explicitly prefers the branded web bridge UI over Telegram for direct agent conversation. The bridge provides a personalized, dark-themed experience that feels like talking to his own agent rather than a generic messaging platform. When both are available, treat the bridge as the primary conversation interface and Telegram as fallback.

14. **Full path to hermes binary required in subprocess:** When running `hermes chat -q` from a systemd service or non-interactive subprocess, the PATH may not include the Hermes venv. Always use the absolute path:
    ```python
    cmd = ["/usr/local/lib/hermes-agent/venv/bin/hermes", "-p", PROFILE, "chat", "-q", message, "-Q"]
    ```

## File Structure

```
project/
├── index.html          # Chat UI (single-file, no build step)
├── server.py           # FastAPI bridge server
└── .herenow/           # here.now state (auto-created)
    └── state.json
```

## References

- `references/https-cloudflare-tunnel.md` — HTTPS for constrained devices, Cloudflare Tunnel setup, mixed content fixes
- `references/hermes-chat-q-reference.md` — Full `hermes chat -q` API reference, session continuity, FastAPI integration
- `references/telegram-long-polling-conflict.md` — Why Telegram relay doesn't work for bridge servers
- `references/handwriting-canvas.md` — Drawing canvas implementation, vision AI reading, touch event handling
- `templates/bridge-server.py` — Complete FastAPI bridge server template

## Example: Ray-Ban Integration

Vanito's use case (Jun 2026): Voice + handwriting chat with Gentech from Meta Ray-Ban smart glasses.

- **UI:** Pure black, 120px mic button, toggle voice mode, drawing canvas
- **Backend:** FastAPI on port 8765, systemd service (`gentech-bridge`)
- **HTTPS:** Cloudflare quick tunnel (`gentech-tunnel` systemd service)
- **Deployment:** UI on here.now (HTTPS), backend via tunnel (HTTPS)
- **Flow:** Voice/Draw → text → `hermes chat -q` → response → display
- **Key URLs rotate** — quick tunnel gives random HTTPS URL each restart
- **Two input modes:** Voice (tap-toggle) + Handwriting (canvas → vision AI)

### Architecture: HTTPS All The Way

Ray-Ban Meta browser **rejects HTTP**. Both page and API must be HTTPS:
```
here.now (HTTPS) → Cloudflare Tunnel (HTTPS) → Bridge Server (localhost:8765)
```
