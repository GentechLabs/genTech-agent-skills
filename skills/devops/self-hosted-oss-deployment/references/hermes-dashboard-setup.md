# Hermes Dashboard — VPS Deployment Pattern

**Date:** 2026-06-05
**Hermes version:** v0.15.2 (v0.16.0 pending)
**VPS:** root@100.73.143.15

## Setup

### Systemd Service

```bash
cat > /etc/systemd/system/hermes-dashboard.service << 'EOF'
[Unit]
Description=Hermes Web Dashboard
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root
ExecStart=${INSTALL_DIR}/venv/bin/hermes dashboard --host 0.0.0.0 --port 9119 --no-open --insecure
Restart=always
RestartSec=5
Environment=HOME=/root
Environment=PATH=${INSTALL_DIR}/venv/bin:/usr/local/bin:/usr/bin:/bin

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable hermes-dashboard
systemctl start hermes-dashboard
```

### Key Flags

- `--host 0.0.0.0` — bind to all interfaces (required for Tailscale access)
- `--port 9119` — default dashboard port
- `--no-open` — don't try to open browser (headless VPS)
- `--insecure` — **required** for non-loopback binds without Nous Portal OAuth

### Auth

v0.15.2 has a broken `dashboard_auth` module (referenced in web_server.py but not shipped in the pip package). Workaround:
- Create stub module at `hermes_cli/dashboard_auth/` with middleware, routes, audit, ws_tickets, prefix stubs
- Use `--insecure` flag to bypass OAuth gate
- v0.16.0 may ship the real module — check after update

### Theme

Dashboard themes go in `~/.hermes/profiles/gentech/dashboard-themes/*.yaml` (NOT `~/.hermes/dashboard-themes/` — the path is profile-specific via `get_hermes_home()`).

Theme format:
```yaml
name: my-theme
label: "My Theme"
palette:
  background: { hex: "#0a0a0f", alpha: 1.0 }
  midground: "#ff8c00"
  foreground: { hex: "#ffffff", alpha: 0 }
  warmGlow: "rgba(255, 140, 0, 0.15)"
  noiseOpacity: 0.5
typography:
  fontSans: '"Inter", system-ui, sans-serif'
  fontMono: '"JetBrains Mono", monospace'
customCSS: |
  /* custom styles */
```

Set active theme via config.yaml: `dashboard.theme: my-theme`

### Management

```bash
# Status
systemctl status hermes-dashboard

# Restart (after config changes)
systemctl restart hermes-dashboard

# Logs
journalctl -u hermes-dashboard -f

# Kill old background processes (conflict with systemd)
pkill -f "hermes_cli.main dashboard"
```

## Pitfalls

- **Theme path is profile-specific.** `get_hermes_home()` returns `${PROFILES_DIR}/gentech`, not `/root/.hermes`. Themes must be in `profiles/gentech/dashboard-themes/`.
- **`--insecure` required for 0.0.0.0 bind.** Without it, the OAuth gate refuses non-loopback binds when no auth providers are registered.
- **dashboard_auth module missing in v0.15.2.** web_server.py imports it at module load time — crashes without stubs.
- **Background processes conflict with systemd.** Kill any `hermes dashboard` background processes before starting the systemd service.
