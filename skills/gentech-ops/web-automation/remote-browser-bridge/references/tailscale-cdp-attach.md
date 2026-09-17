# Tailscale CDP attach — verified command matrix (Sep 3, 2026 session)

## Topology
- Agent: VPS, tailnet IP 100.126.236.51
- User PC: `gentechhq`, Windows, tailnet IP 100.102.61.86
- Brave 152.0.7977.76 with dedicated profile `C:\Users\jhitm\gentech-brave-profile`

## Verified sequence

### 1. PC-side (Jordan ran)
```powershell
taskkill /IM brave.exe /F
Start-Process "C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe" -ArgumentList '--remote-debugging-port=9222',"--user-data-dir=$env:USERPROFILE\gentech-brave-profile",'--no-first-run'
tailscale serve --bg --tcp=9222 tcp://127.0.0.1:9222
```
(First two path guesses — Program Files, LOCALAPPDATA — failed only because Brave was already running; registry lookup found `C:\Program Files\...` and taskkill-then-launch worked.)

### 2. VPS-side verification (raw HTTP first)
```bash
curl -s -m 10 http://100.102.61.86:9222/json/version   # → Browser: Chrome/152...
curl -s http://100.102.61.86:9222/json                 # → tab list
```

### 3. Daemon launch (VPS terminal, background=true)
```bash
pkill -f 'browser_harness[.]daemon'; sleep 1
PYTHONPATH=${PROFILES_DIR}/gentech/home/.cache/uv/archive-v0/eQ0C6m3fBESV2uLx/lib/python3.11/site-packages \
BU_CDP_URL=http://100.102.61.86:9222 \
/usr/bin/python3.12 -m browser_harness.daemon
```
Socket appears at `~/.hermes/profiles/gentech/home/.config/browser-harness/runtime/bu-default.sock`.

### 4. Sandbox helpers just work
```python
print(daemon_browser_kind())   # 'cdp'
print(list_tabs())
print(page_info())
js('document.title = "🟢 GENTECH — LOG IN HERE"')
cdp('Target.activateTarget', targetId=tid)
cdp('Browser.setWindowBounds', windowId=wid, bounds={'windowState':'maximized'})
```

## Verified outcomes
- Tab enumeration, live JS execution in user's tab, scroll, DOM reads: all confirmed.
- AKINDO login in automation profile persisted; account `gentech`, GentechLabs GitHub connected.

## Failure trail (for diagnosis, do not repeat)
1. First launch: flags ignored (Brave already running) → 31 procs, no LISTENING.
2. LOCALAPPDATA path wrong → registry lookup found Program Files.
3. `Browser.bringToFront` → -32601 method not found; use Target.activateTarget + setWindowBounds.
4. Sandboxed `ensure_daemon(env={'BU_CDP_URL':...})` → runner blocks private-IP URLs; launch daemon from terminal instead.
5. uv trampoline shebang is /bin/sh → use system python3.12 + PYTHONPATH.
6. Multi-line PowerShell pasted via Telegram arrived truncated — switched to one-liners.

## Resume state
- SoSoValue developer console (sosovalue.com/developer): Demo API key is free, self-serve. Login modal left open in automation tab. Pending: Jordan logs in → generate Demo key → submit full access form https://forms.gle/2nuJT2qNbUQsyyZy8.
- Ops doc: vault `00-HQ/brave-cdp-bridge-setup.md`. Hackathon state: `00-HQ/hackathon-tracker.md`.
