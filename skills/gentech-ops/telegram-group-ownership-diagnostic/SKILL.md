---
name: telegram-group-ownership-diagnostic
description: Diagnose "agent X isn't replying in group Y" across a multi-profile Hermes fleet. Determines which bot token actually owns a Telegram group before touching gateway recovery, and distinguishes bot-membership gaps from stuck-tool errors and flood-control throttling.
category: devops
tags: [telegram, gateway, multi-agent, diagnostic, group]
---

# Telegram Group Ownership Diagnostic

When a user reports "agent X isn't replying in group Y", the gateway is often **fine** — the bot wired to that profile may simply not be a member of that group, so it never receives the messages. This is the #1 false-alarm for "gateway down" in a multi-profile setup.

## Core insight

Multiple profiles can have routing context for the same group in their `config.yaml` (`channel_prompts`), but only **ONE bot token is actually a member** of that group. A profile can be configured to route to a group without its bot being in it — so messages there never reach it.

## Diagnostic order (do this BEFORE gateway recovery)

1. **Determine which bot owns the group.** For each profile, check membership:
   ```bash
   curl -s "https://api.telegram.org/bot<TOKEN>/getChat?chat_id=<group_id>"
   ```
   - `ok:true` → that bot owns the group (it can see + send)
   - `ok:false` → that bot is NOT a member; it can't see the messages
   - `"Forbidden: bot was kicked"` → banned, re-invite
   - `"Bad Request: chat not found"` → wrong chat ID or never added

2. **Cross-check the owning profile's home channel.** `grep TELEGRAM_HOME_CHANNEL <profile>/.env` — the profile whose home channel matches the group is the intended owner.

3. **Only then check the owning bot's gateway** — process (`ps aux | grep "gateway run"`), log freshness, and the group's inbound/response lines in `gateway.log`.

## Stuck reply ≠ dead gateway

A message received but never answered is usually one of:
- **Mid-turn tool error** — an MCP call failed mid-response (e.g. `get_execution_status not found`, `404 Execution not found`). The agent errored out before producing a reply. Check `gateway.log` for the tool error near the inbound timestamp.
- **Telegram flood control** — `Flood control exceeded. Retry in N seconds` in `gateway.log`. Sends are throttled; replies delay or drop. Restart the gateway to reset retry state if stuck >10 min.
- **Session compression** — a long session auto-compressing mid-turn can delay the reply.
- **Stale code after Hermes update** — the gateway process has been running since before an update and now crashes on every inbound message with an `ImportError` or `AttributeError` from a module that changed (e.g. `cannot import name 'slash_confirm' from 'tools'`, `No module named 'tools.send_message_tool'`, `No module named 'run_agent'`). The gateway receives the message and logs `Flushing text batch` followed immediately by the import error — no reply is ever sent. Fix: restart the gateway so it picks up the current installed code. Check gateway start time with `ps -o lstart= -p <pid>` — if it predates the last `hermes update`, this is the cause.

## Multiple bots per account — identify the LIVE one first

A fleet profile can have several Telegram bots (main agent bot, a "Treasury" desk bot, a gizmo bot, etc.), each with its own token. The token that actually owns a group is the one that answers `getChat` with `ok:true`. Before diagnosing a "kicked" bot:

1. **Find the live token** — `grep -E "^TELEGRAM_BOT_TOKEN=" ~/.hermes/profiles/<profile>/.env` (it lives in the profile `.env`, NOT always in `/root/.env` or `.bashrc`). Don't assume a token from a backup or a switch script is current.
2. **Identify each bot** — `curl getMe` returns `first_name` + `username`. Match that handle to the group's membership.
3. **Probe every group you care about with the live bot** in one pass, so you see the full blast radius (a kick is rarely isolated to one group).

## Confirmed case (Aug 10, 2026): live bot kicked from TWO groups

`@ProtoJaybot` (id 8710327768, the live Gentech bot) was kicked from **Labs** (`-1003872552815`) AND **Treasury** (`-1002916759037`) — which is why Gizmo couldn't run the Opportunity Scanner and those group-delivery crons kept failing with `Forbidden: bot was kicked from the supergroup chat`. HQ and Entertainment were still `ok:true`. Root cause: group admin removal / privacy-settings change. **The fix is human-gated** — a kicked bot cannot rejoin itself; a group admin must re-add `@ProtoJaybot` via the members list. After the user re-adds it, re-run the diagnostic to confirm `ok:true` before declaring it resolved. Note: the Treasury group had some crons "migrated to gentech-treasury profile" (a separate bot, `@GentechDeskbot` id 8981389550) — always check whether a group is intentionally served by a different bot before flagging a kick.

## Confirmed case (Aug 9, 2026)

Labs and Treasury groups "not replying" simultaneously — both gateways had been running since 00:36 and were crashing on every inbound message with `cannot import name 'slash_confirm' from 'tools'`. The underlying Hermes installation had been updated but the gateways were never restarted, so they held stale code in memory. The main Gentech gateway (started 54min later after the update completed) was fine. Restarting both gateways resolved it. Additionally, the Treasury group had a double-gateway (systemd Restart=on-failure spawned a second instance alongside a manual nohup restart), amplifying Telegram rate-limiting.

## Confirmed case (Aug 7, 2026)

Entertainment group "not replying" was a **combination**: the bot that owned the group was processing messages, but a Vanito message was stuck on a KeeperHub MCP tool error (`get_execution_status not found`), compounded by Telegram flood-control throttling. The gateway was healthy the whole time. Restarting the gateway (to clear the stuck session + flood state) was the fix — not a gateway outage.

## Pitfalls

- Don't restart gateways before confirming which bot owns the group — you may restart the wrong profile.
- A profile with `channel_prompts` for a group in config.yaml does NOT mean its bot is in that group.
- Bot username/handle is cosmetic; chat IDs + membership are what matter.

## Related
- **A member who was removed cannot rejoin, links "don't work", or a new collaborator's messages
  never arrive** → `agent-kit/telegram-member-recovery` (removal bans; `can_invite_users` mints links
  but only `can_restrict_members` lifts a ban; the allowlist is the other half of the fix).
