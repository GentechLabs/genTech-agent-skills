# Uncle Iroh Voice Production Guide

## Overview
This guide documents the proven workflow for creating Uncle Iroh voice messages, updated June 29, 2026 with critical API key rotation lessons.

## Voice Selection
**Primary Voice:** Brian - "Deep, Resonant and Comforting" (voice ID: `nPczCjzI2devNBz1zQrb`)
- **Why it works:** Deep, mature, wise quality that captures Uncle Iroh's signature warmth and wisdom
- **Backup:** Any "middle-aged, resonant, comforting" male voice from ElevenLabs
- **Custom voice:** "Gentech-Iroh" (ID: `NqA7ncEPGGt1nDbCrDex`) - may require valid API key

## API Key Management (CRITICAL - June 29, 2026)
**NEVER trust stored API keys** - they expire/rotate unexpectedly:

### Testing Your Key
```bash
curl -X GET "https://api.elevenlabs.io/v1/user" -H "xi-api-key: YOUR_KEY"
# Should return user details, NOT {"detail":{"status":"invalid_api_key"}}
```

### Key Replacement Protocol
1. If key fails → IMMEDIATELY use user-provided replacement
2. Test replacement key before any generation
3. Never proceed with invalid keys - results in JSON instead of audio
4. Document successful keys for future reference

## Message Style Guidelines

### Key Phrases
- "Great, googly-moogly" - Uncle Iroh's signature surprised/wonder expression
- "My young friend" - Classic mentor-to-student address
- "Magnificent sight to behold" - Wise, appreciative tone
- "Sweet taste of victory" - Encouraging, positive framing

### Voice Settings
```json
{
  "stability": 0.7,
  "similarity_boost": 0.85,
  "style": 0.6,
  "use_speaker_boost": true
}
```

### Sample Message Structure
```
Hook: "Great, googly-moogly, [topic]!"

[Pause/section break]

Wisdom: "My young friend, you have quite the eye for [quality]. This is truly a magnificent sight to behold!"

[Optional closing lesson]
```

## Production Workflow (Updated - June 29, 2026)

### 1. API Key Validation
```bash
# Always test your key first
curl -X GET "https://api.elevenlabs.io/v1/user" \
  -H "Content-Type: application/json" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" 2>/dev/null | grep -q "user_id" || {
    echo "ERROR: Invalid API key - get replacement from user"
    exit 1
  }
```

### 2. Text Crafting
- Use Uncle Iroh's wise, encouraging tone with signature phrases
- Keep messages concise but impactful (2-3 sentences ideal)
- Include "great, googly-moogly" opener for positive surprise

### 3. Audio Generation (ALWAYS use text_to_speech)
```bash
text_to_speech "Great, googly-moogly, that thing is juicy!" \
  --output_path /tmp/uncle-iroh-message.mp3
```

**NEVER use direct curl calls** - they often fail with authentication or return JSON instead of audio.

### 4. Format Verification
```bash
file /tmp/uncle-iroh-message.mp3
# Should show: "Audio file with ID3 version 2.4.0, contains: MPEG ADTS..."
# If shows "JSON text data" → authentication failed
```

### 5. Telegram Delivery
- Send audio file with appropriate caption explaining Uncle Iroh context
- Include reference to Avatar and Uncle Iroh character

## Usage Examples

### Gaming Moments
```
Great, googly-moogly, that kill is juicy! Haha, my young friend, you have quite the eye for fine details. This is truly a magnificent sight to behold!
```

### Project Milestones
```
Great, googly-moogly, that deployment is magnificent! My young friend, you have quite the eye for quality engineering. The sweet taste of victory is yours!
```

### Learning Moments
```
Great, googly-moogly, that concept is truly enlightening! My young friend, you have quite the eye for wisdom. This is a magnificent sight to behold!
```

## Troubleshooting Guide

### ❌ API Key Invalid (Most Common Issue)
**Error:** `{"detail":{"status":"invalid_api_key"}}`
**Fix:** 
1. Ask user for current valid API key
2. Test new key before proceeding
3. Never reuse old/stored keys

### ❌ Direct API Calls Fail
**Error:** Returns JSON data instead of MP3
**Fix:** Always use `text_to_speech` tool, never curl

### ❌ Wrong Voice ID
**Error:** "Not Found" when using custom voice IDs
**Fix:** Use backup voice ID `nPczCjzI2devNBz1zQrb` (Brian)

### ❌ Audio Format Issues
**Error:** Telegram doesn't receive audio properly
**Fix:** Verify with `file` command, ensure proper MP3 format

## Pro Tips

- The "great, googly-moogly" opener always works for positive surprise
- End with encouraging, wisdom-forward framing
- Keep messages concise but impactful (2-3 sentences ideal)
- Voice should sound warm, slightly amused, and full of life wisdom
- Always verify audio format before Telegram delivery
- **NEVER proceed without testing API keys first**

## Reference Examples

### Successful Delivery (June 29, 2026)
```
Great, googly-moogly, that thing is juicy! Haha, my young friend, you have quite the eye for fine details and the sweet taste of victory. This is truly a magnificent sight to behold!
```

**Voice:** Brian - Deep, Resonant and Comforting
**Settings:** stability=0.7, similarity_boost=0.85, style=0.6
**Format:** MP3, 64 kbps, 48 kHz (verified)
**Delivery:** Gentech Entertainment Group - Uncle Iroh context included

### API Key Testing Protocol
```bash
# Quick key validation before any voice work
ELEVENLABS_API_KEY="6e3f26583ebfb5cfcc13fb60b23a2d0bc45b7ebf6208bd86eed0ea3394337fef"
curl -s -X GET "https://api.elevenlabs.io/v1/user" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" | grep -q "user_id" && \
  echo "✅ API key valid" || \
  echo "❌ Invalid API key - get replacement"
```