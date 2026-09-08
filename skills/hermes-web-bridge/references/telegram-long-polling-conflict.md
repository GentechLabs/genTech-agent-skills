---
name: telegram-long-polling-conflict
description: "Why Telegram relay bridges fail and how to avoid the trap"
---

# Telegram Long Polling Conflict

## The Problem

The Telegram Bot API allows only ONE client to call `getUpdates` on a bot at a time. If the Hermes gateway is already using long polling for a bot, your bridge server CANNOT also poll for responses.

## Symptoms

- Bridge server sends message to Telegram channel successfully
- But `getUpdates` returns stale data or times out
- Gateway may stop receiving messages temporarily
- Bridge gets no response or wrong responses

## Why It Happens

1. Hermes gateway runs long polling on @ProtoJaybot: `getUpdates` with `offset=-1`
2. Bridge server also tries `getUpdates` on same bot
3. Telegram routes updates to whichever client polled last
4. Gateway loses updates, bridge gets updates meant for gateway
5. Both clients fight over the same update stream

## Verification

```bash
# Check if gateway is using webhooks or polling
curl -s "https://api.telegram.org/bot<TOKEN>/getWebhookInfo" | python3 -m json.tool
# If url is "" → using long polling → DO NOT also poll from bridge
# If url is set → using webhooks → bridge can use getUpdates (but shouldn't)
```

## Solution: Bypass Telegram Entirely

Use `hermes chat -q` as the backend instead of relaying through Telegram:

```
Browser → FastAPI → hermes chat -q → response → Browser
```

No Telegram involvement. No polling conflicts. Direct CLI communication.

## When Telegram Relay IS Appropriate

- Bot has NO existing gateway connection
- Using webhook mode (not long polling) and bridge handles all updates
- Creating a SECOND bot specifically for the bridge (separate token)
- Bot is dedicated to the bridge (no shared usage)
