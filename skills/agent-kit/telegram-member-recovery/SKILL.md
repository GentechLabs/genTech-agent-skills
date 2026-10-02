---
name: telegram-member-recovery
description: "Use when a Telegram member was removed and cannot rejoin. Removal = BAN: they land on the removed-users list and an invite link cannot work until they are unbanned. Covers the Bot API calls that prove it, the two permissions that fix it, and the allowlist step that keeps their messages from being dropped."
version: 1.0.0
author: Gentech
tags: [telegram, members, ban, recovery, bot-api, collaborators, permissions]
trigger: "A collaborator cannot rejoin a Telegram group after being removed; an invite link 'does not work'; a member is missing from the contact picker; a new collaborator's messages never arrive."
---

# Telegram Member Recovery

**The one fact that saves an afternoon: removing a member from a Telegram supergroup BANS them.**
They are not "removed and free to return" — their status becomes `kicked`, they land on the
**Removed users / Banned members** list, and they stay there. An invite link cannot work for a
kicked user, and an admin re-adding them fails silently. The ban must be lifted first.

## Ask the API, do not theorise

Never guess at the cause from the client UI. The Bot API answers in one call:

```bash
# is this person banned?  -> status: "kicked" = banned. until_date 0 = forever.
curl -s "https://api.telegram.org/bot$TOKEN/getChatMember?chat_id=$GROUP&user_id=$USER_ID"

# how many members/agents are actually in the group?
curl -s "https://api.telegram.org/bot$TOKEN/getChatMemberCount?chat_id=$GROUP"

# what may the BOT itself do? (pass the bot's own id from getMe)
curl -s "https://api.telegram.org/bot$TOKEN/getChatMember?chat_id=$GROUP&user_id=$BOT_ID"
```

Status values that matter: `creator` / `administrator` / `member` / `restricted` / `left` /
**`kicked`** (banned). `left` can rejoin with a link; **`kicked` cannot rejoin at all.**

## The two permissions do different jobs

| permission | what it buys you |
|---|---|
| `can_invite_users` | mint invite links (`createChatInviteLink`) |
| `can_restrict_members` | **lift a ban** (`unbanChatMember`) |

A bot with only `can_invite_users` holding a banned user is a dead end: **the link is the door, the
ban is the lock.** Granting invite rights and then sending a link produces a link that fails and
looks like the link's fault.

```bash
# the fix, once the bot has can_restrict_members
curl -s -X POST "https://api.telegram.org/bot$TOKEN/unbanChatMember" \
  -d "chat_id=$GROUP&user_id=$USER_ID&only_if_banned=true"
# then, and only then, a link (single-use for one person)
curl -s -X POST "https://api.telegram.org/bot$TOKEN/createChatInviteLink" \
  -d "chat_id=$GROUP&name=rejoin&member_limit=1"
```

A human can do the same from the client: group → Manage → **Banned members** →
find the person → **Unban**. That list is where a removed member is sitting.

## Rules

- **Act on the numeric ID, never a username.** The vault
  (`00-HQ/collaborators/mapping.json`) holds ids and they do not change; usernames go stale — one
  collaborator's recorded `@handle` was gone while the id still resolved perfectly.
- **Removing someone you may want back is a two-step operation.** Remove bans them; unban right
  after, or restrict instead. Say which one you did.
- **A bot is never in the contact list and does not need to be.** "Not in my contacts" is a
  plausible-sounding theory that sends people to the wrong fix — the ban list is the answer.
- **Restoring the membership is only half the job — the allowlist is the other half.** Every agent
  profile that serves that group must carry their id in `TELEGRAM_ALLOWED_USERS` (that profile's
  `.env`), or their messages are dropped **silently** while every surface looks green. Check every
  seat, not just the one in front of you.
- **Do not migrate the group to work around one member.** A migration moves every delivery target
  (in this fleet: ~137 references across ~77 cron jobs) and Telegram **cannot merge groups** —
  history and message ids stay behind. Lift the ban instead.

## Proven by the case that produced this skill

2026-10-01: a collaborator was removed, then could not rejoin, and the working theory was "he is not
in the admin's contacts". `getChatMember` returned **`status: "kicked"`, `until_date: 0`** — a
permanent ban. The bot held `can_invite_users` but not `can_restrict_members`, so no link could have
helped. After the unban, `getChatMember` returned `status: "member"` and the member count went
`3 → 4`. A group migration had already been scoped and was correctly abandoned.
