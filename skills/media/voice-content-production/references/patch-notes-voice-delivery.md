# Patch Notes Voice Delivery (Jun 2026)

## Product Concept

**Voice-enabled patch notes using Optimus Prime voice.**

"Imagine him or maybe somebody else famous or another voice is reading to you the patch notes."

## Implementation

### Script: `optimus-patch-tts.py`

```bash
# Usage
python3 optimus-patch-tts.py "patch notes text"

# Example
python3 optimus-patch-tts.py "Autobots, listen up. Path of Exile 2 patch 0.5.2 has been deployed. Your Monk build remains combat-effective."
```

### Voice Settings (Optimus Prime)

| Setting | Value | Why |
|---------|-------|-----|
| Stability | 0.75 | Slightly lower for dramatic delivery |
| Similarity | 0.90 | High similarity for voice consistency |
| Style | 0.15 | Low style for controlled delivery |

### Post-Processing

```bash
ffmpeg -y -i input.mp3 \
  -af "highpass=f=80,silenceremove=start_periods=1:stop_periods=-1:stop_duration=0.3:stop_threshold=-35dB,acompressor=threshold=-20dB:ratio=3:attack=5:release=50,loudnorm=I=-16:TP=-1.5:LRA=11" \
  output-clean.mp3
```

## Credit Usage

| Content Type | Characters | Cost |
|--------------|------------|------|
| Patch notes (daily) | 300-500 chars | ~$0.01-0.02 |
| Deal alerts (weekly) | 200-400 chars | ~$0.01 |
| Monthly (2 users, daily) | ~45,000 chars | ~$0.60-1.20 |

## Product Design

**Hybrid approach (recommended):**
- Weekdays: Text patch notes (free)
- Sunday: Voice summary (Optimus Prime)
- Cost: ~$0.50/month

**Full voice (if budget allows):**
- Daily voice patch notes
- Cost: ~$1.00/month

## Example Output

```
📰 PATCH NOTES — Jordan's Game Intelligence
━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎮 Path of Exile 2 — NEW UPDATE
• Patch 0.5.3 released
• Balance changes, new content
• Link: store.steampowered.com/...

✅ No updates on other tracked games.

🎙️ Want this read by Optimus Prime? Upgrade to voice delivery!
```

## Integration with GenTech Shop

1. Deal tracker finds deals
2. Patch notes engine finds updates
3. Voice delivery system reads them aloud
4. User receives voice message in Telegram

**Jordan's vision:** "You can't ignore the man when he's talking and you're going to have a good time listening to him."
