---
name: telegram-publishing
description: Formatting and delivering content through Telegram within platform constraints.
triggers:
  - Crafting or splitting a message that will be delivered to Telegram
  - User reports messages being cut off, truncated, or too long
  - Formatting tables, lists, code blocks, or structured content for Telegram
---

# Telegram Publishing

Telegram enforces a **~4000 character limit** per message. Responses exceeding this are silently truncated. The fix is message splitting on the agent's end — there is no platform config that auto-splits.

## Rule

Split any response over ~3800 characters into multiple messages. Split at **logical breakpoints**:
- Between table rows (not inside a table)
- Between sections (after headers)
- Between list items (not mid-list)
- After code blocks (not inside them)

Never deliver a truncated message. If in doubt, split proactively — the user has stated they prefer multiple short messages to one cut-off one.

## Agent-Side Output Truncation — Close Strong or Get Cut (Aug 30, 2026)

A second truncation class exists besides the 4000-char cap: the **agent's own output length limit**. It hit twice in one night — each time on the *closing* section of a long reply (the action-items list and the wrap-up). The user then sees a system "truncated" notice with no closing at all.

**Rule:** for long replies, put the essential ask/CTA/summary **early** (right after the headline result), not in a trailing bullet list. If a closing list is necessary, keep it to 3 short lines max — or split it into its own follow-up message. Never let the "what I need from you / what happens next" live at the very bottom of a long message.

**Recurrence warning (Aug 31, 2026):** even with this rule documented, a whole night of replies ran past the cap — every offender packed a status report + a checklist + TWO OR MORE paste-ready code blocks into one message. Hard rule: **one paste-ready code block per message.** If the reply needs two or more (e.g. a form's About text AND field values), the second block goes in the next message — and apply Jordan's one-task-at-a-time rule while splitting (see gentech-ops: next-task reminders do NOT ride along).

## Multi-Message Strategy

Split message 1 with the headline/overview, message 2+ with details. Use natural breakpoints:
- **Message 1:** Summary table, TL;DR, top-line results
- **Message 2+:** Deep dives, supporting data, next steps

Avoid splitting inside:
- A table row (keep rows atomic)
- A code block (keep code blocks whole)
- A numbered sequence step

If a section naturally exceeds the limit, restructure it into a table or bullet list first, then split the list.

## Link / Artifact Delivery — Build to Server First, Send ONLY the Link

When the deliverable is a built artifact (deploy page, deck, dashboard, HTML demo), **never inline the artifact content or a long build narrative into the message**. The user complained twice in one session (Aug 2, 2026) that messages "got cut off" / "chopped in half" — each time the root cause was inlining long content (HTML, multi-step build logs) alongside the link.

**The pattern:**
1. Build the artifact to the server FIRST (all tool calls, verification, 200-checks done before composing the message)
2. Send a message whose body is essentially **only the short URL** plus 2-3 terse status lines
3. If a link is the whole point of the message, make the URL the entire body — no surrounding prose to push it past the cap

**Correct (this is the entire message):**
```
Here's the link, boss:

https://gentechlabs.net/arc-deploy.html

Wallet has 20 USDC on Arc testnet. Connect MetaMask, sign, done.
```

**Wrong (what got truncated):** the link buried at the end of a paragraph that also described the build, the contract bytecode, the nginx config, and the wallet state.

**When the user replies "your message got cut off" / "last thing I saw was X"** — they are telling you the truncation point. Resend the REMAINDER only (from X onward), keep it under the cap this time, and prefer link-only if a link was involved.

## Inline Image Delivery — When Images Don't Render Until the User Types

When you send generated images via the `MEDIA:<path>` inline convention (or markdown `![](url)`), the user may see **nothing** — the image only appears after they send another message to "nudge" the gateway, or never appears inline at all. Vanito hit this repeatedly on a storyboard batch (Aug 10, 2026): "I don't see it," "I don't see it," every time after an inline image was sent.

**Diagnose before assuming the file is broken:** the file may be perfectly fine — `curl -o /dev/null -w "%{http_code}"` returning 200 and `file` confirming a valid PNG/JPEG proves the artifact is fine and the failure is on the chat image-delivery side, not the file.

**The reliable fix (use proactively for multi-image deliverables):**
1. **Deploy the images to the server first** (VPS `scp` + `chmod 644` + verify each returns 200).
2. **Build a single gallery HTML page** with all images as `<img>` tags, one per card, each labeled. Serve it at a stable URL, `chmod 644`, verify 200.
3. Send the user **ONE message with just the gallery URL** plus terse labels. They open the page once and scroll — no per-image inline rendering, no typing to trigger delivery.
4. Also provide **direct per-image links** as an alternative (`https://.../image.png`) in case they prefer clicking through individually.

**Avoid for multi-image batches:** sending several `MEDIA:` inline images in one message. The user will report each as "I don't see it" and the thread fills with the same complaint. The gallery page sidesteps the whole class of failure.

**When a user says "I don't see it" about a just-sent inline image:** don't regenerate or re-send the same way — confirm the file serves (200), then hand over the direct URL and/or the gallery page, and explain the file is confirmed live so they can verify it wasn't a rendering issue.

## Batch Image Delivery — When the Whole Set Arrives Empty (Aug 31, 2026)

Sending 5× `MEDIA:` blocks in one message (valid, verified JPGs) delivered NOTHING to the user — twice in a row (first PNGs from /tmp, then JPGs still from /tmp). Jordan: "I don't see any photos man." The delivery ladder for multi-image sets:

1. **Convert PNG → JPG** (~quality 88) — smaller, renders as a photo rather than a document.
2. **Write files OUTSIDE /tmp** before sending (e.g. `~/.hermes/profiles/<profile>/outbound/`) — /tmp paths failed to ride through twice on the gentech gateway; treat /tmp as untrusted for MEDIA delivery.
3. **Send one media block per message**, with a one-line numbered caption between blocks.
4. **Guaranteed fallback: the contact sheet** — one tall labeled image stitching all items in gallery order (PIL: scale all to content width, stack with cyan label strips, single JPEG). One attachment always lands, even when per-image delivery is flaky; user crops/saves sections from it.
5. Gallery-page-on-server (section above) remains the zero-risk option for sets larger than 3.

Verification still applies before ANY re-send: pass images through the media gate (see develop-and-verify) first — a re-send round-trip must never deliver the same broken artifact twice.

## Clickable Links — ALWAYS Use Markdown Hyperlinks

Bare URLs are NOT clickable in Telegram (Jordan flagged this Aug 3, 2026 on the Opportunity Scanner cron). Every URL must be a markdown hyperlink:

```
✅ [Devpost — Build with Gemini XPRIZE](https://xprize.devpost.com/)
✅ [Apply: DataHub Agent Hackathon](https://datahub.devpost.com/)
❌ https://datahub.devpost.com/   (bare URL — NOT clickable, do NOT emit)
```

This applies to **every** link: opportunity/hackathon/job listings, apply pages, artifact links, source URLs, dashboards. If a cron job or skill that posts to Telegram produces bare URLs, add an explicit "LINK FORMATTING — use `[text](url)`, never bare URLs" instruction to its prompt (as done for job `71d5c3e3b245`).

## Verified-Gallery Set Delivery to External Platforms (AKINDO, Devpost, DoraHacks) — Aug 31, 2026

Hackathon submission galleries are media-delivery tasks. The end-to-end pattern that worked:

1. **Assemble the set in the required order** — e.g. AKINDO gallery = hero (cover) → live-run proofs → spec-summary card last. Build any missing images (summary/spec card via PIL, ASCII-only with the media gate from develop-and-verify).
2. **Pass every image through the media gate BEFORE sending** — OCR (tesseract `--psm 6`) + vision readback + source-log grep for every rendered fact (amounts, versions, addresses, word spellings).
3. **Convert to JPG** (~q88), **write outside /tmp** (profile `outbound/` dir), send one image per message with a numbered caption.
4. **Fallback: single labeled contact sheet** (PIL stack, one JPEG) — one attachment always survives flaky per-image delivery.

## Fleet Notes
- Media-fleet sync pattern for shared skills: `gentech-ops` and `hackathon` are user-owned (not curator-managed), so autonomous sessions CANNOT update them — the Aug 31 lessons that belong there (one-task-per-reply discipline; AKINDO form field semantics) must be surfaced to a foreground session or adopted via `hermes curator adopt gentech-ops` / `hackathon` first. Don't silently assume a fleet-wide skill update landed.
- `shared-skill-floor` (skills do not auto-propagate between profiles; sync + grep-verify, content marker check) lives in the agent-kit/devops area — consult it before assuming other profiles got any update made here.

## Telegram-Specific Formatting

- **Bold:** `**text**`
- **Code:** `backticks` for inline, triple backticks for blocks
- **Tables:** render as pipe-separated markdown — Telegram renders them
- **Emoji:** use freely for visual scanning (✅ 🔲 🔥 💰 🟢 🟡 🔴)
