# Voice Cloning from Telegram — Jul 24, 2026

## Session Summary
Cloned Jocelyn's voice from Telegram voice messages. Key learnings below.

## Order of Operations for First-Time Voice Cloning

1. Collaborator sends voice message in Telegram → OGG file lands in `/root/.hermes/profiles/gentech/audio_cache/`
2. Find it: `ls -lt /root/.hermes/profiles/gentech/audio_cache/*.ogg | head -5`
3. Check duration: `ffprobe -v quiet -show_format /path/to/file.ogg` — should be 30-60s
4. Clone: POST to ElevenLabs `/v1/voices/add` with the OGG file
5. Save voice ID to `.env`
6. Test with TTS curl — verify file output with `file` command

## Pitfalls Encountered

### Wrong API Key Format
Jordan sent a 64-char hex string. That was NOT the ElevenLabs key — real keys start with `sk_`. Always test with `curl` before saving.

### Wrong Model ID
`elevenlabs/flash-v2.5` is wrong (the MCP-style path). The correct API model ID is `eleven_flash_v2_5`. The old `eleven_turbo_v2_5` still works but flash is the current recommended model.

### Telegram Voice Quality
Opus compression introduces noise. For clean clones:
- Ask for a quiet room recording
- 30-60 seconds minimum
- Natural voice, not reading
- Avoid background noise

### Deleting Poor Clones
After cloning a mixed-quality recording, the voice was muffled. Delete with:
```
curl -s -X DELETE -H "xi-api-key: $ELEVENLABS_API_KEY" "https://api.elevenlabs.io/v1/voices/VOICE_ID"
```

## English vs Native Language
When a collaborator speaks multiple languages, clone SEPARATE voices per language from clean recordings. A single clone from mixed-language audio produces muddy results.

## Jocelyn's Voices
- English: `dwPf6y3q42Kdh7xBSGKx` — clean, from a good 41s recording
- Original (deleted): `aWJOnPY23xAoAyL1eQwL` — noisy, from Telegram voice message
