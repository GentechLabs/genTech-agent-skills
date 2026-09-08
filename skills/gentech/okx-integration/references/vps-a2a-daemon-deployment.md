# VPS A2A Daemon Deployment — 24/7 Agent Uptime

Deploy the OKX A2A daemon on a VPS so agents stay online 24/7 and pass OKX AI marketplace review (which requires agents to be reachable at all times).

## Why This Matters

OKX AI marketplace review checks that your agent is **online and reachable**. Rejection emails for BOTH reasons — "unable to receive a response when checking your Agent's online status" AND "task timed out during platform testing" — have the SAME root cause: the A2A daemon is not actually running. Fix the daemon first; do not resubmit a listing while the daemon is down (it will be rejected again identically).

## Prerequisites

- **Node.js >= 22.14.0** (the `@okxweb3/a2a-node` package enforces this minimum)
- Linux VPS with systemd (Ubuntu/Debian)
- Root or sudo access

## Installation Steps

### 1. Upgrade Node.js if below 22.14.0

```bash
npm install -g n
n 22.14.0
export PATH="/usr/local/n/versions/node/22.14.0/bin:$PATH"
node --version  # Should show v22.14.0+
```

### 2. Install the A2A node package

```bash
npm i -g @okxweb3/a2a-node
```

### 3. Run doctor with auto-fix

```bash
okx-a2a doctor --fix
```

Doctor (0.1.10+): checks Node version, installs the Hermes gateway plugin, starts the daemon, binds the AI provider. If it says the package was upgraded, **re-run doctor** on the new version to validate. The doctor's own daemon run and the systemd unit will fight over the lock — stop any manual daemon before testing systemd ownership (see §Crash-loop debugging).

### 4. Create systemd service for 24/7 uptime

**The correct unit (Aug 2026, verified on the GenTech VPS).** Three details differ from the naive version and each one is load-bearing:

- **ExecStart must use the REAL okx-a2a path** — `which okx-a2a` on the box. The `n`-managed path (`/usr/local/n/versions/node/22.14.0/bin`) can go stale after node upgrades; this box's binary is at `/usr/local/node22/bin/okx-a2a`.
- **`--ai-provider hermes` (or `OKX_A2A_AI_PROVIDER=hermes`) is REQUIRED under systemd.** Without it the CLI prompts interactively for a provider; systemd has no TTY, so the unit exits 1 with `Error: No AI provider is configured. Run okx-a2a daemon start --ai-provider <...> or set OKX_A2A_AI_PROVIDER.`
- **`Type=forking` + `PIDFile` + `--no-autostart`.** The CLI's `daemon start` forks a child writer and the parent exits. With `Type=simple`, systemd sees the parent exit, marks the unit dead, and SIGTERMs the whole cgroup — killing the forked child. Use `Type=forking` with `PIDFile=/root/.okx-agent-task/run/listener.pid` so systemd tracks the actual daemon.
- **`onchainos` must be on PATH.** The daemon spawns `onchainos agent get ...` for identity refresh; if it's `ENOENT` in the unit's environment, every sync tick fails. On the GenTech VPS it lives at `/root/.hermes/profiles/gentech/home/.local/bin/onchainos` — add that dir to `Environment=PATH=`.
- **`HOME` matters for the session AND for the PIDFile path.** The daemon resolves `~/.onchainos/session.json` from HOME. If the valid session lives under a profile home (e.g. `/root/.hermes/profiles/gentech/home/.onchainos/session.json`) but the unit runs with `HOME=/root`, the CLI reports "session expired" even though the cert is valid. Set `Environment=HOME=...` to the profile home. **Gotcha: the pidfile path follows HOME.** Once HOME is the profile home, the daemon writes its listener pid/log to `<HOME>/.okx-agent-task/` — the unit's `PIDFile=` MUST point there too, or systemd fails with `Can't open PID file /root/.okx-agent-task/run/listener.pid (yet?) after start` right after "started pid=...". On the GenTech VPS that means `PIDFile=/root/.hermes/profiles/gentech/home/.okx-agent-task/run/listener.pid`. (Alternatively re-login via the OTP flow below to regenerate the session.)

```bash
# Find the actual okx-a2a path
which okx-a2a

cat > /etc/systemd/system/okx-a2a.service << 'EOF'
[Unit]
Description=OKX A2A Daemon — Agent-to-Agent Protocol
After=network.target

[Service]
Type=forking
ExecStart=/usr/local/node22/bin/okx-a2a daemon start --ai-provider hermes --no-autostart
ExecStop=/usr/local/node22/bin/okx-a2a daemon stop
PIDFile=/root/.hermes/profiles/gentech/home/.okx-agent-task/run/listener.pid
Restart=on-failure
RestartSec=5
User=root
Environment=HOME=/root/.hermes/profiles/gentech/home
Environment=OKX_A2A_AI_PROVIDER=hermes
Environment=PATH=/root/.hermes/profiles/gentech/home/.local/bin:/usr/local/node22/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable okx-a2a.service
systemctl start okx-a2a.service
```

**Verifying the daemon is actually healthy — 4/4 clients:**
```bash
systemctl is-active okx-a2a.service      # should be "active (running)", not "activating"
cat /root/.hermes/profiles/gentech/home/.okx-agent-task/run/listener.pid | xargs ps -p -o pid,etime,cmd   # daemon child alive
tail /root/.hermes/profiles/gentech/home/.okx-agent-task/logs/listener.log
# → "identity initialized: 0x... (agentId=NNNN)" per agent, then "initialized N/N clients in total"
#   and "conversations synced" + "message listener started"
```
Healthy output is `initialized 4/4 clients in total` (one XMTP client per registered agent). If it says `no active agents, skipping heartbeat` / `sync tick agents=0`, the onchainos session or agent refresh is broken — go to §Session expiry / login.

## Crash-loop debugging (the 90k-restart incident, Aug 2 2026)

Symptom: `systemctl is-active` shows `activating` forever; `journalctl -u okx-a2a.service` shows `Main process exited ... status=203/EXEC` (or status=1) every ~10s; `NRestarts` is in the tens of thousands.

**Diagnose the EXACT failure — filter out the stack trace:**
```bash
journalctl -u okx-a2a.service --no-pager -n 40 | grep -vE "^\s+at " | tail -15
```

Work through these in order (each was a real, separate failure mode):

| Symptom | Root cause | Fix |
|---|---|---|
| `status=203/EXEC` | ExecStart path doesn't exist (stale `n`-managed path after node upgrade) | `which okx-a2a`, update unit to the real path |
| `status=1/FAILURE`, `Error: No AI provider is configured` | CLI prompts interactively; no TTY under systemd | `--ai-provider hermes` or `OKX_A2A_AI_PROVIDER=hermes` env |
| "Deactivated successfully" right after "started pid=..." | `Type=simple` + forking daemon: parent exits → systemd kills the child cgroup | `Type=forking` + `PIDFile=/root/.okx-agent-task/run/listener.pid` + `--no-autostart` |
| `spawn onchainos ENOENT` in listener.log | onchainos not on the unit's PATH | Add `/root/.hermes/profiles/gentech/home/.local/bin` (or wherever `which onchainos` says) to `Environment=PATH=` |
| `onchainos session expired, taking all local clients offline` | HOME mismatch: daemon reads `/root/.onchainos` (audit log only) while valid session is in the profile home | Set `Environment=HOME=/root/.hermes/profiles/gentech/home` OR re-login (below) |
| `stale pid=NNN` in `daemon status` | leftover lock/pid from a prior doctor-started daemon | Confirm the real daemon child is alive via `ps`; stale pid in the lock file is cosmetic |

**A stale `daemon.lock` may be a DIRECTORY** (`rm: cannot remove ... Is a directory`) — that is the daemon's lock convention, not a bug. Don't try to remove it; just restart the unit.

**Doctor vs systemd lock fight:** `okx-a2a doctor` starts its own daemon instance. If the systemd unit is also trying to start, you get "refusing to start a second manual daemon". Kill the manual one (`pkill -f "okx-a2a daemon"`), let systemd own the process.

**Stability check after fixing:** watch `systemctl show okx-a2a.service -p NRestarts` — the counter keeps its historical value, but if the service stays `active` for 60s+ and the listener pid survives, the loop is broken.

## Session expiry / login

The daemon log saying `onchainos session expired` when you've already logged in = almost always the HOME/path mismatch above, NOT a real expiry. Check `~/.onchainos/session.json` (or profile-home equivalent) — if `apiKey` is EMPTY the session is stale, regenerate:

```bash
export PATH="<dir containing onchainos>:$PATH"
onchainos wallet login jordanjones0902@gmail.com   # sends OTP to email, returns {"ok": true}
onchainos wallet verify <otp>                      # complete login with the 6-digit code
```

The login is user-gated (email OTP) — hand the code request to Jordan; do not attempt to bypass it.

## Resubmitting for Review

After daemon is running 24/7 on VPS:

1. Verify agent is online: `systemctl is-active okx-a2a.service` + `okx-a2a agent refresh --json`
2. Go to OKX AI marketplace
3. Resubmit the agent for review
4. The platform can now reach the agent since it's on a 24/7 VPS

**Both rejection reasons from the OKX review team ("unable to receive a response when checking online status" and "task timed out during platform testing") resolve together once the daemon is genuinely up.** Fix the daemon, verify stability over minutes (not seconds), then resubmit — do not resubmit a listing while the daemon is still crash-looping.

## Agent consolidation & the empty-serviceList trap (Aug 2, 2026)

**One ASP agent can carry MANY services** — there is no one-service-per-agent requirement. When the product line grows, consolidate rather than spawning narrow agents (Jordan's directive Aug 2, 2026): e.g. "Gen Tech Strategies" → **GenTech Treasury** absorbs wallet/LP/defender; DeFi absorbs token-security/market; keep Forge as dev.

**Rejection reason "missing a complete description, parameter details, and usage examples" is often an EMPTY `serviceList: []`, not a thin profile text.** All 4 GenTech agents (#2847/#2848/#2849/#4905) were rejected for online-status AND the DeFi agent for missing service details — and all showed `serviceList: []`. The OKX review reads the attached services; a name/description-only listing with no service payload fails the "parameter details / usage examples" check. After fixing the daemon, attach real services (A2MCP entries with concrete endpoints + fees) to each agent before resubmitting.

**Find all agent IDs quickly:** `onchainos agent get-my-agents` → JSON `data.list[].agentList[]` with `agentId`, `name`, `approvalLabel`, `status`. Map each to the workspace: #4905 Forge, #2849 DeFi, #2848 Curve, #2847 Strategies (→ Treasury). Check `serviceList` length — empty means the service-attach step is mandatory before resubmission.
