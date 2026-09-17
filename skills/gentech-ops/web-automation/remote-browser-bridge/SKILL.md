---
name: remote-browser-bridge
description: "Use when agent-gated pages block automation (CDP attach)."
tags: [browser, cdp, tailscale, remote-attach, logged-in, agent-gated]
version: 1.0.0
author: gentech
category: web-automation
---

# Remote Browser Bridge — attach to the user's logged-in browser

When a page is login-gated (hackathon forms, faucet portals, submission dashboards), don't bounce screenshots — attach the browser harness to a browser the user has logged into. Proven end-to-end Sep 3, 2026: VPS agent attached to a Brave on the user's Windows PC over Tailscale and executed JS in his tabs.

## Architecture
- **User's PC**: Brave/Chrome with a **dedicated automation profile** + `--remote-debugging-port`, exposed to the tailnet via `tailscale serve --tcp` (never public internet).
- **Agent host (VPS)**: browser-harness daemon started OUTSIDE any code sandbox with `BU_CDP_URL` pointing at the tailnet IP; agent helpers (page_info/js/fill_input/cdp) ride the daemon's local socket.
- Sessions live in the dedicated profile — logins persist across restarts, one login per gated site ever needed.

## Why a dedicated profile (not the user's default)
- Chromium M136+ blocks CDP attach on the **default** profile (and M144 adds an "Allow remote debugging" popup). A dedicated `--user-data-dir` sidesteps both.
- Isolation: agent only sees what's in that profile — user keeps banking/email in their normal browser.

## User-side setup (Windows, one-time)
```powershell
# Kill Brave first — launch flags ONLY apply on a fresh process (relaunching while
# running just opens a flagless window in the old process; classic silent failure)
taskkill /IM brave.exe /F
Start-Process "<brave.exe path>" -ArgumentList '--remote-debugging-port=9222',"--user-data-dir=$env:USERPROFILE\gentech-brave-profile",'--no-first-run'

# Expose to tailnet only
tailscale serve --bg --tcp=9222 tcp://127.0.0.1:9222
```
- Brave's real path: query the registry Uninstall keys (DisplayName like '*Brave*' → InstallLocation) — install roots vary and hardcoding two guesses wastes round-trips.
- User logs into gated sites once in that window; cookies persist in the profile.

## Agent-side attach (VPS) — the critical ordering
1. **Sandboxed code execution CANNOT attach directly** — runners block private/internal IP URLs in code. The daemon must be launched from the terminal/shell instead.
2. Find the harness interpreter: the uv archive `bin/browser-use` is a **/bin/sh trampoline, not Python** — don't read its shebang. Use system python3.12 with `PYTHONPATH=<uv archive>/lib/python3.11/site-packages` (harness imports fine despite the 3.11 dir name).
3. Launch: `PYTHONPATH=<site-packages> BU_CDP_URL=http://<tailnet-ip>:9222 python3.12 -m browser_harness.daemon` via `terminal(background=True)` — it's a long-lived daemon, never exits.
4. Then in the sandboxed code executor, helpers connect to `bu-default.sock` and just work. Verify with `daemon_browser_kind()` → `cdp`.

## Pitfalls (all hit live this session)
- **pkill self-match**: `pkill -f browser_harness.daemon` kills the invoking shell (pattern matches own cmdline). Use `pkill -f 'browser_harness[.]daemon'`.
- **Host-header reset**: Chromium's debug endpoint resets connections whose Host header isn't localhost — a raw TCP forward must present the right Host; `tailscale serve --tcp` handles this, netsh portproxy also works (firewall scope 100.64.0.0/10).
- **Tabs vanishing**: user closes the automation window without realizing. Don't assume the bridge broke — re-enumerate tabs, reopen the URL in the surviving window, re-mark the tab title.
- **Signaling the right window**: `Browser.bringToFront` may be unsupported over remote CDP. `Target.activateTarget` (tab) + `Browser.setWindowBounds` (windowState: maximized) both work. Also set `document.title = "🟢 GENTECH — ..."` so the user can find the tab by name.
- **Fresh profile = logged out everywhere**: sessions do NOT cross between the user's normal browser and the automation profile. Expect one manual login per site in the automation window — hand the user precise modal steps, never enter credentials yourself.
- **Remote-assist pastes**: multi-line PowerShell blocks get mangled in paste — send ONE-LINE commands (`;`-joined) for anything the user runs, ending in a single diagnostic that prints exactly the layer that failed.
- **Diagnose by layer** when "it didn't work": procs count → netstat LISTENING → local curl /json/version → remote curl. Each result names the broken layer (launch / port / forward / tailnet).

## Security rules
- Tailnet-only exposure; revoke = `tailscale serve reset` or close the window.
- Never type passwords/2FA into the user's browser; credential entry is the user's move.
- Automation profile = build-task logins only.

Reference: `references/tailscale-cdp-attach.md` — full verified command matrix and session trail.
