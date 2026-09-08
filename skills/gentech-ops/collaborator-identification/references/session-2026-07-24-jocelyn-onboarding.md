# Collaborator Onboarding — Jul 24, 2026 (first student)

## Summary
Jordan introduced the student (Telegram ID on file) as a new collaborator. Non-technical Filipina, voice talent track, aspiring orchestrator-in-training.

## Key Details
- **Name:** student (departed Aug 2026)
- **Background:** Filipina, non-technical
- **Role:** Jordan's first student
- **Track:** Voice cloning (ElevenLabs/Pipecat/Omnivoice) → orchestrator
- **Language:** Cebuano/Bisaya (primary communication language)
- **Telegram ID:** 7504399137
- **Telegram Username:** @Celinealison92

## What Was Set Up
- Profile: archived (file removed Aug 31, 2026)
- Progress tracker: archived (file removed Aug 31, 2026)
- mapping.json entry with topics (voice, tts, orchestration) and permissions (voice, tts-production, content)
- Green Room ideas added: GenTech Onboarding Playbook, Voice Pipeline
- Memory updated
- `TELEGRAM_ALLOWED_USERS` updated in `.env` to include 7504399137

## Lessons Learned

### 1. Vault Mapping ≠ Telegram Delivery
The student's profile was set up perfectly in the vault. But her messages never reached me. Root cause: `TELEGRAM_ALLOWED_USERS` in `.env` didn't include her ID. The vault mapping only tells the agent who the person is — the env var tells the Telegram gateway to let their messages through. Both are required.

### 2. Message Length Discipline with Newcomers
Wrote a welcome in Cebuano that kept getting cut off at ~1400 chars. Final working approach: 2-3 very short messages (~300-400 chars each). Emoji, markdown, and non-English text inflate char count invisibly.

### 3. Don't Overthink Collaborator Interactions
Jordan corrected me THREE times about how to handle the student's messages:
1. "Why didn't you reply to her?"
2. "Sorry I meant here in the group"
3. "No the same way you reply to me or Vanito"

Lesson: A known collaborator in the group = a person in the conversation. Reply immediately and naturally. Zero special processing. If Jordan corrects you twice on the same thing, stop and adjust — don't wait for a third.

### 4. Multi-Language Communication
Don't assume English for non-technical collaborators. Write in their native language with simple analogies:
- "AI agents are like robots that help with work"
- "Orchestrator = like a conductor, you tell the agents what to do"

### 5. Voice Cloning Pipeline
First step is voice sample recording (1-2 min, quiet room, normal tone). Provide a sample script in their native language.

## Voice Sample Script (Cebuano)
```
"[Cebuano self-introduction — warm, grateful for the opportunity, offers voice talent] Hello, ako si (name). Taga Pilipinas ko. Ganahan ko makat-on ug bag-ong mga butang bahin sa AI ug technology. Nindot kaayo ni nga oportunidad para nako. Mapasalamaton ko ni Jordan ug Gentech nga gihatagan ko ug tsansa. Sa umaabot, gusto ko makatabang sa team pinaagi sa akong tingog. Mag-amping mo ug daghang salamat!"
```
