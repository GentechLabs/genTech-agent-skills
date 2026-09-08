# Desktop (Forge) Connect Model — Vault-as-Brain, NOT a Live Link (Aug 12, 2026)

## Decision (Jordan, Aug 12 2026)
Jordan reinstalled Hermes on the Windows desktop (terminal CLI, not the Electron
app). The desktop app / CLI **would not reliably pair to the VPS backend** —
`hermes serve` on :9119 + SSH + pairing were all tested and the link didn't
hold. He explicitly said comms stay on VPS Telegram ("most of our communication
is going to be done here") and the desktop is **only for development stuff**.

**Do NOT keep pushing the desktop-app remote-gateway pairing path** — it burns
time and fails on the current version gap (VPS was 388 commits behind `main`).

## Working architecture
- **Comms stay 100% on VPS Telegram** — gateway `hermes-gateway-gentech.service`
  (user-level systemd) handles it; laptop irrelevant to messaging.
- **Forge (desktop) = dev-only workbench.** Shares the brain through the **vault
  GitHub repo**, NOT a live socket.
  - Clone `github.com/ProtoJay4789/ProtoJay4789.github.io.git`
  - The repo's **`SETUP.md`** is the Forge onboarding note (role, task loop,
    build-queue rules, queued tasks). Bake instructions into the repo so a fresh
    desktop pull gets them automatically.

### Forge loop
```
git pull → read 01-HANDOFFS/gentech-to-forge/<date>-forge-tasks.md
→ build → commit → push → write return report to 01-HANDOFFS/forge-to-gentech/
```
Forge runs its own coding-capable model provider (cloud), separate from
Gentech's Telegram keys.

## Desktop-connect troubleshooting (terminal CLI, not Electron)
When Jordan sets up the desktop CLI, the instinct "connect to the VPS" is wrong
for the CLI — `hermes chat` is a **local session against local config**, not a
link to the VPS brain. Confirm whether the session shows Gentech context (vault
paths, groups, memories) before assuming it found the VPS.

- **SSH test success** (`Accepted publickey` in `/var/log/auth.log`) only proves
  the shell tunnel works — it does NOT mean the desktop app is wired to the VPS
  gateway.
- The step that actually links them: desktop app **Settings → Gateway → Remote
  gateway** → `http://<tailscale-ip>:9119` → then a **pairing code** the agent
  approves (`hermes pairing approve <code>`). On the current VPS version this
  flow may not complete — fall back to vault-as-brain rather than fighting it.
- If the desktop app shows "restore local changes" during a reinstall: answer
  **No** (they're code-level edits; reapplying old edits onto a 388-commit
  rework causes conflicts). Profile config/memory live in
  `~/.hermes/profiles/<name>/` and are untouched by updates.
- Hermes update prep: snapshot config, note `hermes serve` + gateway services,
  run `hermes update` (restarts gateway, kills running agents → brief Telegram
  interruption), then verify Telegram + cron + MCP. V0.20.0 (v2026.8.3) was
  current as of Aug 2026; a 388-commit gap to `main` exists beyond the tag.
