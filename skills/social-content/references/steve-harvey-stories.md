# Steve Harvey Voice Content — Daily Story Reference

## Voice Profile
- **Character:** Steve Harvey — motivational, funny, uncle energy, real-talk
- **Voice ID (ElevenLabs):** `Rxk9LQxvNFEplpjjsjuN` (Steve Harvey clone)
- **Credit cost:** ~0.01 per 30-second story (negligible)

## Story Format
- **Length:** 100-120 words (30 seconds spoken)
- **Structure:** Hook → Observation → Punchline/Lesson
- **Ending:** Always end with a punchy one-liner or life lesson

## Topic Rotation
| Day | Topic Category | Example |
|-----|---------------|---------|
| Mon | Morning Motivation | "Rise and grind" energy |
| Tue | Hackathon/Building | What we shipped, lessons learned |
| Wed | Agent Economy | AI agents, DeFi, crypto insights |
| Thu | Real Talk | Life lessons, accountability |
| Fri | Gaming/Weekend | POE2, relaxation, balance |
| Sat | Community | Shoutouts, group wins |
| Sun | Reflection | Week in review, gratitude |

## Script Templates

### Motivation Template
"Let me tell you something. [Observation about what most people do]. But [contrast with what YOU do]. That's the difference between [A] and [B]. [Punchy one-liner]."

### Build Update Template
"[Hook about what just happened]. We [what you built/did]. [Why it matters in one sentence]. Now [what's next]. [Closing line]."

### Real Talk Template
"[Relatable situation]. Here's what I learned: [lesson]. [Expand in 1-2 sentences]. [Punchy closing]."

## Posting Workflow (Automated)
1. Cron fires daily at 7:15 AM ET (offset from morning digest)
2. Agent determines day of week → picks topic from rotation above
3. Agent writes script (100-120 words, Steve Harvey tone)
4. Agent runs `scripts/steve-harvey-tts.py` with script text → ElevenLabs REST API records audio
5. Agent delivers audio file + script text to Entertainment group
6. Jordan posts as IG/FB story

## TTS Automation
The built-in `text_to_speech` tool uses the profile's configured voice and doesn't support voice_id override. For voice-specific TTS (Steve Harvey clone), we use a helper script that calls ElevenLabs REST API directly.

**Script:** `scripts/steve-harvey-tts.py`
**Voice ID:** `Rxk9LQxvNFEplpjjsjuN` (Steve Harvey clone)
**API:** `POST https://api.elevenlabs.io/v1/text-to-speech/{voice_id}`
**Key source:** Script searches multiple `.env` locations (see Pitfalls below). Working key is in `~/.hermes/profiles/desmond/.env`.
**Output:** `/tmp/steve-harvey/steve_harvey_YYYYMMDD_HHMMSS.mp3`

Usage in cron prompt: `python3 /root/.hermes/profiles/gentech/scripts/steve-harvey-tts.py "script text here"`

## Pitfalls

### API Key Resolution Across .env Locations
The script's `get_api_key()` searches in order:
1. `~/.hermes/profiles/gentech/.env` (may be empty or stale)
2. `~/.hermes/.env`
3. `~/.env`
4. `~/vaults/gentech/.env` (had a truncated 32-char key that 401s — skip this)
5. `~/vaults/gentech/00-System/secrets/.env`
6. `~/.hermes/profiles/desmond/.env` ← **working key lives here (64 chars)**
7. `~/.hermes/profiles/dmob/.env`

If you get a 401 from ElevenLabs, check that the key being used is 64 characters, not 32. The vault `.env` key is truncated. The desmond/dmob profile keys are correct.

### ElevenLabs Key Characteristics
- Valid keys are 64 hex characters
- Invalid/truncated keys can be 32 chars (likely old or copy-paste error)
- Always verify key length before debugging API calls

## Privacy Rules
- ✅ Public-facing: building in public, hackathon updates, motivation, agent economy
- ❌ Never: collaborator personal info, internal group discussions, private vault content, financial specifics
