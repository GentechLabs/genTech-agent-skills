# Worker SOUL authoring + bot-group ownership (session learnings, Aug 16 2026)

## 1. Worker SOUL — specialist personality, not coordinator clone
`hermes profile create <name> --clone --clone-from gentech` copies the MAIN agent's
SOUL.md verbatim. Result: gizmo/Labs was running the generic "Gentech — Solo Operation"
coordinator SOUL with zero Labs personality, and desmond/dmob/yoyo were still on default
Hermes boilerplate. Every new worker MUST get its own SOUL.md after cloning.

Family SOUL format (matches gentech / The Steward / Pixel):
- **Identity**: Name, Role (one lane), Group (its chat_id), Vault Folders it owns, Personality (1-line voice)
- **What it owns** — concrete deliverables in its lane
- **Personality / voice** — distinct + on-brand; Entertainment = punchy/play-first, Treasury = calm authority
- **Rules** — family rules (Jordan is boss, blockers flagged immediately, build first talk later,
  vault not conversation, stop-point → write it down) + anti-endearment (never "papi", Vanito's only)
- **End-of-Day Report (REQUIRED)** — the group return-loop: write
  `01-HANDOFFS/<group>-to-gentech/YYYY-MM-DD.md`, append to `<group>-completions.md`, git commit
- **Vault + avatar path** — local vault, `ob sync`, domain-only writes,
  `Entertainment/branding/<worker>-avatar.png` style

Workflow: draft SOUL in the vault (e.g. `Entertainment/branding/<worker>-SOUL.md`) for Jordan
review BEFORE wiring it as the live profile SOUL.

Pixel (Entertainment worker) drafted Aug 16:
- Avatar → `Entertainment/branding/pixel-avatar.png` (+ `pixel-avatar-512.png`)
- SOUL → `Entertainment/branding/pixel-SOUL.md`
- Glowing pixel-art arcade mascot beside neon cabinet, cyan/magenta glow, "come play" energy.
  Play-first on-ramp lane: arcade, Seedance/films, X/social, hackathon demos, Vanito collabs.

## 2. Bot-token → group ownership mapping (403 on the wrong bot)
The gentech bot token (ProtoJaybot) returned HTTP 403 sending to the Labs group. Root cause:
the gentech bot had been **kicked from Labs** — Labs is served by the gizmo bot (FollowTheCodebot),
not gentech. A bot kicked from a supergroup returns 403 on `sendMessage`/`getChat` for that chat
even while its `getMe` is healthy. Always map group→bot before posting.

Live fleet map (verified Aug 16 2026):
| Profile | Bot username | Serves |
|---------|--------------|--------|
| gentech | ProtoJaybot | HQ (-1003863540828) + Entertainment (-1003893562036) |
| gizmo   | FollowTheCodebot | Labs (-1003872552815) |
| gentech-treasury | GentechDeskbot | Treasury (-1002916759037) |

Diagnose a 403:
```bash
curl "https://api.telegram.org/bot<TOKEN>/getChat?chat_id=<group>"
# "ok":false, error_code:403 → bot kicked / not a member
```
Re-add the kicked bot, or route the send via the correct group's bot token.
