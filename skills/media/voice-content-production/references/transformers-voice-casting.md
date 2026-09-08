# Transformers Voice Casting Guide

## Character-to-Voice Mapping

When casting characters for multi-voice skits, map personality traits to ElevenLabs voice characteristics.

### Autobots (Heroes)

| Character | Voice ID | Voice Name | Why It Works |
|-----------|----------|------------|--------------|
| Optimus Prime | `xQbwtCgzouB5QdCSd0Z7` | YoYo (Peter Cullen style) | Gravelly baritone, authoritative, natural leader |
| Bumblebee | `IKne3meq5aSn9XLyUdCD` | Charlie | Deep, Confident, Energetic — young hero energy |
| Ironhide | `nPczCjzI2devNBz1zQrb` | Brian | Deep, Resonant — tough, reliable veteran |

### Decepticons (Villains)

| Character | Voice ID | Voice Name | Why It Works |
|-----------|----------|------------|--------------|
| Megatron | `pNInz6obpgDQGcFmaJgB` | Adam | Dominant, Firm — villain leader, commanding |
| Starscream | `SOYHLrjzK2X1ezoPC6cr` | Harry | Fierce Warrior — sniveling second-in-command |
| Soundwave | `CwhRBWXzGAHq8TQ4Fs17` | Roger | Laid-Back, Mysterious — intelligence officer |

## Casting Principles

1. **Match personality to voice trait** — dominant characters get firm voices, heroes get confident voices
2. **All male voices for Transformers** — maintains the franchise theme
3. **Contrast heroes vs villains** — heroes sound warm/resonant, villains sound firm/fierce
4. **Use existing clones first** — we already have Optimus Prime (YoYo), use premade for the rest
5. **Test before committing** — generate a short sample from each voice to verify fit

## Conversation Flow Pattern

For a 6-character skit:
1. **Optimus** opens (sets the scene)
2. **Starscream** responds (creates conflict)
3. **Megatron** interrupts (escalates)
4. **Bumblebee** adds intel (turns the tide)
5. **Soundwave** reports (provides data)
6. **Ironhide** closes (action call)

Each character speaks 1-2 lines. Total: 25-35 seconds per skit.

## Technical Implementation

```bash
# Generate each character's clip separately
for character in optimus starscream megatron bumblebee soundwave ironhide; do
  curl -s --max-time 30 -X POST "https://api.elevenlabs.io/v1/text-to-speech/${VOICE_ID}" \
    -H "xi-api-key: $ELEVENLABS_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"text\": \"${TEXT}\", \"model_id\": \"eleven_turbo_v2_5\", \"voice_settings\": {\"stability\": 0.65, \"similarity_boost\": 0.85}}" \
    -o /tmp/${character}.mp3
done

# Post-process each clip
for f in /tmp/*.mp3; do
  ffmpeg -y -i "$f" -af "afftdn,acompressor=threshold=-20dB:ratio=4:attack=5:release=50,loudnorm=I=-16:TP=-1.5:LRA=11" "${f%.mp3}-clean.mp3"
done

# Combine in conversation order
cat > /tmp/concat.txt << EOF
file '/tmp/optimus-clean.mp3'
file '/tmp/starscream-clean.mp3'
file '/tmp/megatron-clean.mp3'
file '/tmp/bumblebee-clean.mp3'
file '/tmp/soundwave-clean.mp3'
file '/tmp/ironhide-clean.mp3'
EOF

ffmpeg -y -f concat -safe 0 -i /tmp/concat.txt -c copy /tmp/transformers-skit.mp3
```

## Use Cases

- **Hackathon demos** — show real-time voice agent conversation
- **Social content** — Transformers characters discussing current events
- **Educational content** — characters explaining concepts in-character
- **Agent Arena narration** — Optimus narrating matches, Megatron trash-talking
