# Cron Job TTS Integration

## Required Toolset

For cron jobs to use ElevenLabs TTS, the job must have `terminal` in `enabled_toolsets`:

```json
{
  "enabled_toolsets": ["web", "file", "terminal"]
}
```

The `text_to_speech()` tool is only available when `terminal` toolset is enabled.

## Critical Prompt Requirement

**The prompt MUST explicitly instruct the agent to call `text_to_speech()`.**

Writing about voice in the prompt is NOT enough — the agent must have an explicit instruction to use the tool.

### Correct Example (works):

```markdown
IMPORTANT: You MUST use the text_to_speech() tool to generate voice audio.

Voice script:
"Jordan, your game intelligence report is ready. [Summary]..."

Call text_to_speech() like this:
```
text_to_speech(
  text="Jordan, your game intelligence report is ready...",
  output_path="/root/.hermes/profiles/gentech/audio_cache/jordan-game-intel.mp3"
)
```
```

### Incorrect Example (fails silently):

```markdown
Voice script: "Jordan, your game intelligence report is ready. [Summary]..."

The voice will be delivered as audio.
```

This fails because the agent is never told to CALL the tool.

## Delivery Format

When `text_to_speech()` is called successfully, the agent's final response will include:

```
MEDIA:/root/.hermes/profiles/gentech/audio_cache/jordan-game-intel.mp3
```

Hermes automatically converts this to a native voice bubble in Telegram.

## Configuration

**System-level TTS config:**
```bash
hermes config set tts_provider elevenlabs
hermes config set tts_voice Vanito
```

**Profile-specific .env:**
```
ELEVENLABS_API_KEY=6e3f26583ebfb5cfcc13fb60b23a2d0bc45b7ebf6208bd86eed0ea3394337fef
```

## Common Failure Modes

| Symptom | Cause | Fix |
|---------|-------|-----|
| Text report, no voice | Prompt doesn't say "call text_to_speech()" | Add explicit tool call instruction to prompt |
| Wrong voice | Default TTS used instead of ElevenLabs | Verify `hermes config show | grep tts` and fix `tts_voice` |
| 401 errors | Expired API key | Rotate `ELEVENLABS_API_KEY` in all locations |
| Job runs, no output at all | Delivery target disconnected | Run cron-delivery-audit, change to `origin` |

## Checklist for Cron Job TTS

- [ ] `terminal` in `enabled_toolsets`
- [ ] Prompt explicitly says "call text_to_speech()" with code example
- [ ] System config: `tts_provider = elevenlabs`
- [ ] System config: `tts_voice = <correct_voice>`
- [ ] `.env` has valid `ELEVENLABS_API_KEY`
- [ ] Delivery target is `origin` or verified connected channel
- [ ] Test run produces both text AND `MEDIA:` audio file

## Reference: Game Intelligence Fix

**Before (no voice):**
```markdown
Generate a voice summary of the game intelligence report.
```

**After (voice works):**
```markdown
IMPORTANT: You MUST use the text_to_speech() tool to generate voice audio.

Call text_to_speech() like this:
```
text_to_speech(
  text="Jordan, your game intelligence report is ready...",
  output_path="/root/.hermes/profiles/gentech/audio_cache/jordan-game-intel.mp3"
)
```

The audio file will be delivered as MEDIA:/path/to/audio.mp3 in your response.
```