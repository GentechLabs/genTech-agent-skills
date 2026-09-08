# Collaborator Onboarding — Worked Example (Jul 24, 2026)

## Timeline

1. **Jordan introduces the student** — shares the student's Telegram ID and username
2. **Vault profile + mapping created** — standard onboarding. Profile at `00-HQ/collaborators/{name}.md`, mapping updated
3. **Student messages in group** — I don't see her messages
4. **Jordan asks "can you see @Celinealison92 message?"** — I cannot
5. **Root cause discovered:** Her ID was NOT in `TELEGRAM_ALLOWED_USERS` in the `.env` file. The Telegram gateway silently filtered her out.
6. **Fix applied:** Added `7504399137` to `TELEGRAM_ALLOWED_USERS`

## Root Cause

The vault mapping (used for collaborator identification + routing) and the Telegram gateway's `TELEGRAM_ALLOWED_USERS` (used for message delivery) are **two separate configs**. Both must be updated when onboarding a new collaborator.

**The vault mapping controls** who I know the collaborator is.
**The env ALLOWED_USERS controls** whose messages the gateway forwards to me.

## What the Onboarding Script Does Now

The `onboard.py` script handles both:
1. Creates vault profile + mapping
2. Adds Telegram ID to `TELEGRAM_ALLOWED_USERS` in `.env`

## Verification Steps After Onboarding

```bash
# 1. Verify the ID is in the env
grep TELEGRAM_ALLOWED_USERS ~/.hermes/profiles/gentech/.env

# 2. Verify mapping is correct
python3 -c "
import json
with open('/root/vaults/gentech/00-HQ/collaborators/mapping.json') as f:
    data = json.load(f)
for name, info in data['collaborators'].items():
    print(f'{name}: id={info.get(\"telegram_id\")}')
"

# 3. Tell Jordan it's done
```

## Prevention

Always run the onboarding script for new collaborators. Manual setup misses steps.
If you can't run the script, remember: **both vault AND env must be updated.**

## Companion Rule: MCP-First When Scraping Fails

This session also surfaced a broader pattern: when a web search or scrape gets blocked
(paywalls, browser automation detection, dynamic content), check MCP servers before
fighting the browser.

**Applied example:** Agoda blocked scraping for hotel prices → Tripadvisor MCP was
available through Pay catalog ($0.01/call). Could have returned results instantly
instead of 10+ minutes of browser wrestling.

**Rule:** Before deepening a scrape, call `mcp__pay__search_catalog(query="task")` to
check for a paid API that handles it cleanly. This is now a permanent memory entry.
