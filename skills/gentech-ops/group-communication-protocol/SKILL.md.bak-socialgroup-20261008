---
name: group-communication-protocol
description: "All collaborator communication stays in the group. Never DM collaborators — Jordan wants full team visibility. Covers posting rules, DM prevention, and the Aug 8 incident."
category: gentech-ops
version: 1.0.0
author: Gentech
tags: [communication, collaborators, groups, dms, protocol]
---

# Group Communication Protocol

**One rule, locked in:** All collaborator communication stays in the group. Never send private DMs to any collaborator (Vanito, Dadrian, etc.). If they're in the group, the group is where the message goes.

## The Rule

Jordan's explicit directive (Aug 8, 2026):

> "We don't want to DM anybody privately, we want to keep it here in the group."

This applies to ALL collaborators, ALL topics, ALL groups. No exceptions.

## How to Post

When you need to reach a collaborator who's in a group chat, send the message to the group they're in — NOT their private Telegram ID.

```
# ✅ CORRECT: Post in the group
hermes send --to telegram:-1003893562036 "Message for Vanito..."

# ❌ WRONG: Never DM a collaborator
curl -s "https://api.telegram.org/bot${TOKEN}/sendMessage" -d chat_id=8774981477
```

## What Happened

Aug 8, 2026 — Jordan asked Gentech to pitch DeepSeek V4 Pro to Vanito. Gentech sent a DM to Vanito's private Telegram ID (8774981477) instead of posting in the Entertainment group (-1003893562036). Jordan corrected it immediately:

> "No, Jintek, Veneto is here in the group, in the entertainment group. You can just send it here. We don't want to DM anybody privately, we want to keep it here in the group."

Root cause: instinct to "send a targeted message" overrode the standing convention of group visibility. The collaborator is IN the group — the group IS the right channel.

## Pitfalls

- **"It's a personal pitch."** Doesn't matter. Post in the group.
- **"They might not see it."** They will — they're in the group.
- **"I should DM for privacy."** Jordan wants team visibility. The group IS the channel.
- **"hermes send is available for DMs."** Available ≠ appropriate. Use it to post to groups, not private IDs.
