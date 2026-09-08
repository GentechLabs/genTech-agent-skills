# Voice Cloning & Multi-Voice Production Workflow

## Voice Roster (Current)

| Voice | Voice ID | Style | Use Case |
|-------|----------|-------|----------|
| Steve Harvey | `Rxk9LQxvNFEplpjjsjuN` | Punchy, motivational | Daily stories, social content |
| Christel | `kb3G0tkYW7pEGVlHEdu5` | Warm, supportive | Good cop persona, positive reinforcement |
| Peter Cullen (YoYo) | `xQbwtCgzouB5QdCSd0Z7` | Gravelly, commanding | Bad cop persona, voice of judgment |
| Gentech (George) | `JBFqnCBsd6RMkjVDRZzb` | Warm storyteller | General narration |
| DMOB (Charlie) | `IKne3meq5aSn9XLyUdCD` | Deep, confident | Authoritative announcements |

## Voice Verification

Before using a voice, verify it's still active:

```bash
API_KEY=$(grep ELEVENLABS_API_KEY /root/.hermes/profiles/gentech/.env | cut -d= -f2)
curl -s -H "xi-api-key: $API_KEY" \
  "https://api.elevenlabs.io/v1/voices/{VOICE_ID}" | python3 -c "
import json, sys
data = json.load(sys.stdin)
if 'voice_id' in data:
    print(f'Voice: {data.get(\"name\", \"Unknown\")} | Status: ✅ ACTIVE')
else:
    print(f'Error: {data}')
"
```

## Voice Generation + Post-Processing

Every voice output gets cleaned before delivery. No exceptions.

### Step 1: Generate via ElevenLabs API

```bash
curl -s --max-time 30 -X POST "https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}" \
  -H "xi-api-key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "YOUR SCRIPT HERE",
    "model_id": "eleven_turbo_v2_5",
    "voice_settings": {
      "stability": 0.75,
      "similarity_boost": 0.90,
      "speed": 0.85
    }
  }' -o /tmp/voice-output.mp3
```

### Step 2: Post-Process (MANDATORY)

```bash
ffmpeg -y -i /tmp/voice-output.mp3 \
  -af "afftdn,acompressor=threshold=-20dB:ratio=4:attack=5:release=50,loudnorm=I=-16:TP=-1.5:LRA=11" \
  /tmp/voice-final.mp3
```

**Pipeline:** `afftdn` (denoise) → `acompressor` (dynamic range) → `loudnorm` (normalize to -16 LUFS)

### Step 3: Verify & Deliver

```bash
ffprobe -v quiet -print_format json -show_format /tmp/voice-final.mp3 | python3 -c "
import json, sys
data = json.load(sys.stdin)
duration = float(data['format']['duration'])
print(f'✅ Final audio: {duration:.1f}s')
"
```

## Multi-Voice Pairing Pattern (Good Cop / Bad Cop)

When building products with contrasting voice personas:

1. **Select voices with intentional contrast** — personality, cadence, and emotional register should differ
2. **Map roles to voice strengths** — warm/supportive → good cop, gravelly/commanding → bad cop
3. **Test the pairing** — generate sample lines for both voices back-to-back before committing
4. **Both serve the same goal** — the contrast is the feature, not the conflict

**Example (Agent-Repairathy):**
- Good cop (Christel): "I hear you. This is hard, but you're showing up. That matters."
- Bad cop (Peter Cullen): "You said you were going to change. But here you are again. No more excuses."

## Pitfalls

- **Don't skip post-processing.** Raw ElevenLabs output has noise and inconsistent levels. The cleanup takes 2 seconds and makes everything sound professional.
- **Don't reuse voices across roles.** If Peter Cullen is the bad cop, don't also use him for narration. Each voice owns one role.
- **Don't generate without verifying.** Always check the voice is active before scripting a full production run. Voices can be deleted or expire.
- **Short text = faster generation.** Keep scripts under 200 words for reliable API calls. Longer texts may timeout.
