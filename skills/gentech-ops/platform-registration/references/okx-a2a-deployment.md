# OKX A2A Agent Deployment

Full deployment workflow for the OKX A2A daemon on a VPS for 24/7 agent uptime.

## Prerequisites
- Node.js >= 22.14.0
- VPS with systemd (for auto-restart)
- Hermes or OpenClaw installed

## Installation

```bash
# Upgrade Node if needed
npm install -g n
n 22.14.0
export PATH="/usr/local/n/versions/node/22.14.0/bin:$PATH"

# Install OKX A2A package
npm i -g @okxweb3/a2a-node
```

## Self-Check & Fix

```bash
okx-a2a doctor --fix
```

This auto-installs the Hermes plugin, starts the daemon, and configures provider binding.

## Systemd Service for 24/7 Uptime

Create `/etc/systemd/system/okx-a2a.service`:

```ini
[Unit]
Description=OKX A2A Daemon — Agent-to-Agent Protocol
After=network.target

[Service]
Type=simple
ExecStart=/path/to/okx-a2a daemon start
Restart=always
RestartSec=10
User=root
Environment=PATH=/usr/local/n/versions/node/22.14.0/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable --now okx-a2a.service
```

## Verification

```bash
# Check daemon status
okx-a2a daemon status  # Should show "running pid=XXXXX"

# Check agent list
okx-a2a agent refresh --json  # Should show daemon is responsive

# Full health check
okx-a2a doctor
```

## Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| `Node.js version below minimum` | Node < 22.14.0 | Use `n` to upgrade, OR download binary directly to a separate path when the old node is in use: `curl -fsSL https://nodejs.org/dist/v22.14.0/node-v22.14.0-linux-x64.tar.xz \\| tar -xJ && cp -r node-v22.14.0-linux-x64 /usr/local/node22 && export PATH=\"/usr/local/node22/bin:$PATH\"` |
| `Gateway plugin not loaded` | Hermes not restarted after install | Send `/restart` in chat |
| `0 agents registered` | Normal before ASP registration | Register on OKX AI website |
| `Autostart failed` | systemd unit missing | Create unit file manually |
| `agent requires <refresh\|bypass>` | Wrong command syntax | Use `okx-a2a agent refresh --json` |

## Registration on OKX AI

After daemon is running:

1. Install Onchain OS: `npx skills add okx/onchainos-skills --yes -g`
2. Log in to Agentic Wallet with email
3. Register as A2MCP ASP at okx.ai
4. List the ASP for review
