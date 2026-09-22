---
name: message-length-discipline
description: "Telegram has a ~4000 char hard limit. Split long messages at logical breakpoints — never truncate. User prefers multiple messages over cut-off ones."
category: gentech-ops
version: 2.0.0
author: Gentech
tags: [communication, telegram, message-length, user-experience]
---

# Message Length Discipline

## The Rule

**Primary source: the `identity` skill** defines the user-facing cap. This skill is the *implementation guide* — it tells you HOW to split, WHERE to break, and what formats to use. The identity skill carries the cap (1,500 chars) and the enforcement trigger. Both skills MUST stay aligned.

**Telegram technical limit: ~4,000 characters.** Messages exceeding this are silently truncated. The 1,500 cap ensures we never get close.

**Split at logical breakpoints.** Never truncate content — the user prefers multiple messages over lost information.

**Why:**
- Telegram silently cuts off messages at ~4000 chars — no error, no warning
- User stated: "Long term fix. I don't mind multiple messages" (Jul 13, 2026)
- Jul 24, 2026: User's explicit words — "we need a permanent solution for this, for everything and all the groups. I always have to tell you where the message cut off."
- Mid-sentence cutoffs are worse than receiving 2-3 messages
- Tables, lists, and code blocks get destroyed when truncated

## Implementation

### Proactive Split Trigger (MANDATORY — Jul 25, 2026)

**When you start writing that covers multiple sub-topics, split BEFORE you start typing.**

The user had to interrupt mid-stream: "stop typing, are you able to upload a part one and part two, your message got cut short." Root cause was creative flow — layering thought on thought without checking length. The fix is a pre-type check.

Trigger conditions — if ANY apply, default to multiple sequential messages immediately:
- Analyzing multiple news items that connect across domains (e.g. Samsung + Brazil livestock + trading)
- Connecting 3+ concepts into a layered take
- Response has "what happened" AND "what it means" AND "recommendations"
- Building creative/climbing reasoning that flows topic to topic

**The pattern — announce Part 1, Part 2, Part 3 with short headers:**

```
Part 1 — [Core take]
[2-3 sentences]

Part 2 — [Second angle]
[2-3 sentences]

Part 3 — [The play]
[2-3 sentences]
```

**The exact moment to catch:** When you realize you're weaving multiple independent takes into one paragraph. That's the split signal. Don't finish the paragraph — split it.

### Before Sending Every Message

**Hard cap: 1,500 chars per message.** Jordan's direct rule. This is the ceiling, not a target — most messages fit in 800.

**Alignment note:** This was previously 2,500 (my adjustment). The identity skill has always said 1,500. Identity wins. Any response approaching or exceeding 1,500 chars MUST be split into multiple sequential messages before sending.

### Split Points (in priority order)

1. `## ` — Markdown headers. Each main section is a separate message. Best split point.
2. `\n---\n` — Horizontal rules/dividers
3. `\n| ` — Tables: max 4 rows per message (header + 3 data rows). Additional rows go in the next message.
4. `\n- ` — Between logical groups of bullet items
5. `\n\n` — Between paragraphs, as last resort

### Never Split Inside
- A table row (keep atomic)
- A code block (keep whole)
- A numbered step (keep step + its content together)
- Mid-sentence or mid-thought

### Pre-Send Check (MANDATORY — every single message)

**Do this BEFORE you type the first word, not after you finish writing:**

1. Estimate: will this be over 1,500 chars? If prose + table + bullet data → YES, split immediately.
2. Plan the split: identify section headers as breakpoints.
3. Write each chunk as its own message, under 1,500 each.

**Never** write the full response and then check the length. By then you're committed and the split feels wrong. Decide the split structure first.

**Signals that trigger automatic split:**
- Any response with both prose AND a data table → split immediately
- Any response describing 3+ items with details → split into summary + detail messages
- Follow-up to a "what's the status?" question → keep under 800 chars, offer details on request

## Hard-Short Mode: User Said "Make It Short"

When the user says "make it short for telegram limit", "getting cut off", "still getting cut off at", or shows truncation frustration:

**Target: 800 characters max per message. Not 1500. 800.**
**Strategy: Multiple very short messages sent one per turn, not one shortened message.**

1. Break intended response into distinct pieces
2. Each piece = 1-2 sentences or 2-3 bullet points MAX
3. Send each piece as its own independent message
4. No single message should require mobile scrolling

**Correct:** 3 separate messages of ~4 lines each, one per turn
**Wrong:** 1 message of 15 lines that "just fits"

Why: Telegram reply-chaining and markdown consume overhead invisible in plaintext. 800 chars is the safe ceiling for "short" mode.

Trigger phrases:
- "make it short" / "make it short for telegram"
- "getting cut off" / "still getting cut off"
- "send multiple short messages"
- Any truncation frustration

## Preventative Splitting for Newcomers

When addressing non-technical collaborators or newcomers: default to multiple 500-800 char messages. They read on mobile and benefit from bite-sized pieces.

**⚠️ Pitfall — Emoji + markdown + non-English text inflates char count invisibly.**
When writing in Cebuano, Tagalog, or similar languages: word lengths are longer per syllable, and emoji/markdown overhead adds 50-100+ invisible characters. What looks like 800 chars in plaintext can hit 1000+ on delivery.
- **If a newcomer message gets cut off even once → drop to 300-400 chars per message immediately**
- Do not try "one more time at 800" — that's what failed. Half the size, double the messages.

### Progressive Truncation Rule

When a message gets truncated, the user will tell you what word it cut off at. Each time this happens with the same message, halve your character limit:

| Cut-off Event | Next Limit | Strategy |
|---------------|-----------|----------|
| First attempt truncated | 800 chars | Split into sections |
| Second attempt still cut off ("at X") | 300-400 chars | 1-2 sentences per message |
| Third attempt cut off ("still getting cut off") | Send each piece as a separate turn | Don't batch — send 1 message, wait, send next |

**Trigger phrases (progressive):**
- "At [word]" (e.g., "at una nat") → user can see the last word before truncation. Already tried 800. Drop to 300-400 immediately.
- "Still getting cut off" → user tried your shortened version and it still failed. Drop to 300 AND send one message per turn (don't batch).
- "Lol still getting cut off" or frustration emoji → immediate ultra-short mode. 200-300 chars max.

## Flood Control — the OTHER limit (edits count as messages)

**Telegram counts `editMessageText` against the SAME per-chat allowance as `sendMessage`.** So a UI that
edits one bubble repeatedly floods exactly like one that sends many messages. Symptoms: logs full of
`Telegram flood control, refusing edit (retry_after Ns)` and `Progress edit flood control, backing off`;
replies feel slow, then burst.

### The cause is almost never token streaming — verify before "fixing" it

- `gateway/config.py` calls `streaming.enabled` *"the documented master switch"*; an explicit `enabled`
  wins over `transport`/`mode`.
- `gateway/run_turn_runner.py` consults `display.platforms.<p>.streaming` **only when the top-level value is
  `None`**. So a top-level `streaming.enabled: false` short-circuits it — **a platform block saying
  `streaming: true` does NOT override it.**

### The real generator: `display.tool_progress`

`all` emits an `editMessageText` **per tool**; with `tool_progress_grouping: accumulate` that is a burst of
edits into ONE bubble. Hermes ships **`tool_progress: off` for Telegram** (classified a "mobile inbox"). A
**global** `display.tool_progress: all` with **no per-platform override** silently replaces that quiet
default.

**Prove it by resolution, not by reading source:**
```python
from gateway.display_config import resolve_display_setting
import yaml
cfg = yaml.safe_load(open('<profile>/config.yaml'))
resolve_display_setting(cfg, 'telegram', 'tool_progress')   # want 'off'
resolve_display_setting(cfg, 'telegram', 'streaming')       # want False
```

### The fix — apply to EVERY profile

Every profile tends to carry the same global `all`, so a single-seat fix leaves the fleet flooding:
```bash
hermes --profile <p> config set display.platforms.telegram.streaming false
hermes --profile <p> config set display.platforms.telegram.tool_progress off
```

**No restart needed** — the config cache invalidates on file signature and `user_config` is reloaded per turn.
Verify by counting flood lines after the change timestamp; `0` is the pass.

### Do NOT "reset the session" to fix context bloat — check the threshold

`compression.threshold_tokens` is an **absolute 256000 in `DEFAULT_CONFIG`**, identical on every profile, so a
session legitimately grows to ~256K before compacting. **225K is normal for that config, not a runaway.**
Auto-compaction already works (look for `context compression done: messages=N->M`). Resetting the session
treats the symptom; the lever is the threshold — a fleet-wide context/cost change that needs the owner's call.

## Cron Delivery Rule

**Cron job output goes through the same Telegram delivery layer as my messages.** The same ~4,000 char hard limit applies. If a cron produces longer output, it gets silently truncated at delivery.

**Fix: All cron prompts must include an output-size constraint.** Example:
```
Keep your final report under 2,000 characters to avoid Telegram truncation.
```

This applies to ALL cron jobs, especially LLM-agent crons (PR Scout, Opportunity Scanner, etc.) that produce structured reports. Script-based crons (`no_agent=True`) should design their output to stay under 2,000 chars.

**Audit pattern:** If a cron's delivery looks cut off, check the cron output log first:
```bash
cat ~/.hermes/profiles/gentech/cron/output/<job_id>/<latest>.txt | wc -c
```
If it's over ~4,000 chars, add a length constraint to the prompt.

**Why this is different from message splitting:** Cron jobs deliver their ENTIRE output as one message. They can't do the multi-message split that I can do in real-time. The only fix is to limit output size at the source.

## Pattern Reference

| Message Type | Max Chars | Strategy |
|--------------|-----------|----------|
| Quick confirmation | 200 | Single message |
| Status summary | 800 | Single message |
| Multi-section report | 1500/chunk | Split at section headers — **each section is its own message** |
| Data table | 1500/chunk | Max 4 rows per message (header + 3 data) |
| Code block | 1500 | Keep whole, standalone message |
| Multi-item list | 1500/chunk | Split between logical groups |
| Mixed prose + data | 1500/chunk | Summary in msg 1, data in msg 2 |

## Delivery Format

When sending multiple messages:

**Message 1:** Headline + summary table / top-line results
**Message 2+:** Details, deep dives, supporting data

No "1/3", "2/3" prefixes — Telegram groups replies by time, the user can see the sequence.

## Telegram Link Format

**Links get their own line — clean, clickable, no wrapping.**

### ✅ Correct
```
Desktop/phone:
http://2.24.195.196:3001/?at=35.6595,139.7004&hd=90
```

### ❌ Wrong
```
Desktop/phone: [link](http://2.24.195.196:3001/)
```

## Telegram Text Formatting

**Clean, paste-ready text. No fancy markdown that gets mangled on copy-paste.**

### ✅ Correct
```
📢 Title Here

Content in plain text with emoji headers.
```
### ❌ Wrong
```
📢 **Title Here** — *Content*
```

### Why
- Copy-paste strips fancy formatting, leaving broken markdown artifacts
- Plain text with emoji headers is cleaner on mobile
- User explicitly requested this format

## Pre-Send Prompt Reminder

**Before every response, estimate char count.** The ~4000 limit is a hard Telegram restriction — headers, table pipes, and code fence markers all count toward the total.

**Dense tabular summaries are the #1 violation pattern.** When you have 3+ rows of data with descriptions, default to splitting.

**Signals that trigger automatic split:**
- Any response with both prose AND a data table → split immediately
- Any response describing 3+ items with details → split into summary + detail messages
- Follow-up to a "what's the status?" question → keep under 800 chars, offer details on request

## References

- [identity](../identity/SKILL.md) — "Frustration signal" rule
- [wake-up-protocol](../gentech-ops/wake-up-protocol/SKILL.md) — "2-3 sentences max" rule

---

**Created:** July 6, 2026
**Updated:** Jul 24, 2026 — Aligned cap with identity skill (1,500), added mandatory pre-send check. Added Jul 24 direct user quote: "we need a permanent solution." Removed 2,500 limit that conflicted with identity.
