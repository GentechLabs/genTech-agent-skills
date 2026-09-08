---
name: collaborator-onboarding
description: One-command onboarding for new collaborators — adds Telegram access, vault profile, and mapping
category: gentech-ops
version: 1.0.0
author: Gentech
tags: [onboarding, telegram, discord, slack, collaborator, access]
trigger: "When Jordan says 'onboard', 'add', or 'invite' a new person. When a new collaborator's messages aren't being received."
---

# Collaborator Onboarding

## Purpose
Onboard a new collaborator across all connected platforms in one step. When someone new joins, run the script and they're fully set up — Telegram access, vault profile, mapping, and progress tracker.

## What it does
1. Adds Telegram ID to `TELEGRAM_ALLOWED_USERS` in `.env`
2. Creates vault profile at `00-HQ/collaborators/{name}.md`
3. Updates `00-HQ/collaborators/mapping.json`
4. Creates progress tracker at `00-HQ/collaborators/{name}-progress.md`

## Usage

```bash
cd /root/.hermes/profiles/gentech/scripts && python3 onboard.py \
  --name "{name}" \
  --username "@Celinealison92" \
  --telegram_id 7504399137 \
  --topics "voice,tts,orchestration" \
  --permissions "voice,content"
```

## Parameters

| Flag | Required | Description |
|------|----------|-------------|
| `--name` | ✅ | Display name (lowercased for filenames) |
| `--telegram_id` | ✅ | Telegram user ID (numeric) |
| `--username` | ❌ | Telegram @username |
| `--topics` | ❌ | Comma-separated topics |
| `--permissions` | ❌ | Comma-separated permissions |
| `--notes` | ❌ | Extra profile notes |

## If Telegram Messages Aren't Coming Through

The most common reason is the Telegram ID isn't in `TELEGRAM_ALLOWED_USERS` in the `.env` file. This script handles that automatically, but if you need to check manually:

```bash
grep TELEGRAM_ALLOWED_USERS ~/.hermes/profiles/gentech/.env
```

## Pitfalls
- `.env` is a protected file — use `sed` for edits, not direct write
- The `.env` change takes effect on next gateway connection (no restart needed if the gateway re-reads config)
- Remember to also tell the collaborator which groups they're in
- Mapping file uses lowercase names as keys
- **Both vault AND env must be updated** — missing either = messages silently dropped. See `references/collaborator-onboarding-worked-example.md` for the full root-cause investigation.

## Post-Onboarding Pipeline

After the initial setup, collaborators typically progress through voice capture:

### Stage 1: Voice Cloning
Create a voice capture script (see `elevenlabs-voice-generation` skill → `templates/voice-capture-script.md`):
1. Send the recording script to the collaborator
2. Receive audio files via Telegram
3. Create ElevenLabs voice model via API
4. Add voice_id to `elevenlabs-voice-generation/references/voice-catalog.md`
5. Update their progress tracker

### Stage 1.5: Personal Hub (New — After Voice Capture)
Give the collaborator their own personal hub page. This is their space to express themselves, share their story, and see their progress visually.

**Template:** `10-Labs/gentech-academy/{name}-hub-template.html` — copy from the student hub template.

**What to include:**
- **Header** — name, location, photo/avatar, role badge
- **About Me** — their story, in their words
- **Voice Card** — placeholder for their cloned voice (play button) — **OPTIONAL**, skip if collaborator doesn't want voice cloning
- **Personal Sections** — whatever they want (travel dreams, family, goals, hobbies)
- **Lessons** — their GenTech Academy progress tracker
- **Interests Tabs** — things they love (travel, shopping, cooking, etc.)

**Photo embedding pattern:** For standalone hubs that need to work without a server, embed photos as base64 data URIs directly in the HTML:
```html
<img src="data:image/jpeg;base64,{base64_string}" alt="description" style="...">
```
This keeps the hub self-contained — no server, no external hosting needed.

**VPS photo deployment pattern:** For hubs deployed on the VPS (gentechlabs.net), upload photos to `/var/www/gentechlabs/images/` and reference them as `/images/{name}.jpg`:
```bash
scp /path/to/photo.jpg root@2.24.195.196:/var/www/gentechlabs/images/
ssh root@2.24.195.196 "chown www-data:www-data /var/www/gentechlabs/images/*.jpg && chmod 644 /var/www/gentechlabs/images/*.jpg"
```
Then add photo cards to the hub HTML:
```html
<div class="card photo-card">
  <h3>🐋 Title</h3>
  <img src="/images/{name}.jpg" alt="description" class="hub-photo" loading="lazy">
  <p>Description text here.</p>
</div>
```
With CSS:
```css
.photo-card{padding:0;overflow:hidden}
.photo-card h3{padding:20px 24px 0}
.photo-card p{padding:0 24px 20px}
.hub-photo{width:100%;height:300px;object-fit:cover;display:block;margin:12px 0}
```

**Deploy:** Push to `ProtoJay4789.github.io` repo under a `collaborators/{name}/` directory, or keep in vault at `10-Labs/gentech-academy/` until Jordan decides to deploy. For VPS deployment, scp the HTML file and set ownership:
```bash
scp /var/www/gentechlabs/{name}.html root@2.24.195.196:/var/www/gentechlabs/
ssh root@2.24.195.196 "chown www-data:www-data /var/www/gentechlabs/{name}.html && chmod 644 /var/www/gentechlabs/{name}.html"
```

### Stage 1.6: Prompt Engineering Lesson (New — After Personal Hub)
Teach the collaborator how to request changes to their hub by **prompting Gentech** — no code, no file editing, just conversation.

**The 3-Step Pattern:**
1. **WHAT** — which section to change (Travel, Cooking, Shopping, etc.)
2. **WHERE** — top, bottom, after something, replace something
3. **WHAT** — the new words they want

**Lesson page template:** Deploy a styled HTML lesson page at `gentechlabs.net/{name}-lesson-1.html` using the first student's lesson as the pattern (original retired Aug 2026; rebuild from 10-Labs/academy-playbook/orchestrator-playbook-distilled.md).

**Key principle:** The collaborator never touches code. They tell Jordan what they want, Jordan relays to Gentech, Gentech makes it happen. The skill they're learning is **prompting** — clear instructions produce the right result.

**Voice cloning is OPTIONAL** — Jordan confirmed Jul 27, 2026 that voice cloning should be an elective module, not a required step. Students can choose to clone their voice or skip it entirely.

**Academy lessons are tailored per student** — Jordan confirmed Jul 27, 2026 that lessons should be based on what each student wants to learn, not a fixed curriculum. Ask the student what they're curious about and build the lesson around that. pilot student's path: voice cloned → personal hub → prompt engineering lesson (how to tell Gentech what to change). Next steps depend on what she wants to learn next.

**Pitfall:** The lesson page must be proper HTML with DOCTYPE, head, and body tags — NOT plain markdown. If written as markdown, the browser renders it as raw text. Always wrap in a styled HTML template matching the collaborator's hub aesthetic (dark theme, gradient accents, card layout).

### Stage 2: Voice Agent Deployment (follow-on)
- Pipecat or Omnivoice integration using the cloned voice
- Full pipeline documented in `elevenlabs-voice-generation/references/pipecat-integration.md`

### Stage 3: Orchestrator Training (long-term)
- Basic tool fluency → agent interactions → orchestrator delegation
- Track at `00-HQ/collaborators/{name}-progress.md`
