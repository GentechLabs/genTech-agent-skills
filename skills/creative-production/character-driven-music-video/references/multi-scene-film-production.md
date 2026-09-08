# Multi-Scene KAGE Film Production

Confirmed working 2026-07-24 across two scenes with full character consistency.

## Overview
Chain 15-second Seedance 2.0 clips into a multi-chapter film. Each scene uses:
- Character sheet as seed image
- Full character coating inline in every prompt
- Time-coded [0-3s][3-6s][6-9s][9-12s][12-15s] action blocks
- Style block at end (palette hex codes, lighting, camera)
- Sound design layered with ffmpeg at specific timestamps
- Title overlays with chapter numbering

## Scene Templates

### Scene Type 1: Intro / Standing (Scene 1 — CONFIRMED)
KAGE standing on rooftop, atmospheric establishment. No combat.

**Time blocks:**
| Time | Action |
|------|--------|
| 0-3s | Wide establishing shot — character small in frame, environment dominant |
| 3-6s | Slow crane push — camera glides toward character, tension builds |
| 6-9s | Reveal — character turns, first clear look at face/details |
| 9-12s | Walk — character moves forward, tracking shot |
| 12-15s | Climax chord — freeze frame, title card fades in |

**Sound design:** Rain ambience throughout (volume 0.5), impact SFX at 12s (adelay=12000, volume 1.8)

### Scene Type 2: Combat / Action (Scene 2 — CONFIRMED)
KAGE fights shadow creatures on the rooftop.

**Time blocks:**
| Time | Action |
|------|--------|
| 0-3s | Aftermath of previous scene. Characters arrive/enemies appear |
| 3-6s | First attack — character dodges, counterattacks with guitar |
| 6-9s | Multi-enemy fight — chained combat moves |
| 9-12s | Climax strike — final enemy defeated with a chord/impact |
| 12-15s | Victory stance — character stands in red mist, chest heaving, phoenix pulses |

**Combat prompt keywords:** "guitar swings", "strings connect", "red flash", "shadow dissolves into red mist", "coat spinning", "strums a short chord that sends a shockwave", "elbow connects"

**Sound design:** 
- Shadow emergence at 2s (adelay=2000, volume 0.9)
- Combat impact hits at 5s and 9s (adelay=5000 and adelay=9000, volume 1.2 each)

## Cost Reference
| Item | Cost |
|------|------|
| 10s Seedance 2.0 clip | ~$3.19 |
| 5s Seedance 2.0 clip | ~$1.60 |
| Sound effects (2-3 SFX) | ~$0.11 |
| **Per 15s scene** | **~$4.90** |
| **Full 60s film (4 scenes)** | **~$19.60** |

## Film Production Order (confirmed pattern)
1. Generate scene clips (10s + 5s per scene)
2. Generate SFX via blockrun_speech(action="sound_effect") — download immediately (URLs expire)
3. Concat 10s + 5s clips with ffmpeg demuxer
4. Mix audio: layering SFX at specific delays with adjusted volumes
5. Combine mixed audio with concatenated video
6. Add title overlays with drawtext (chapter title, "A GenTech Labs Production" watermark)
7. Check wallet. Deliver via MEDIA.

## ffmpeg Concat Command
```bash
echo "file 'clip1.mp4'" > concat.txt
echo "file 'clip2.mp4'" >> concat.txt
ffmpeg -f concat -safe 0 -i concat.txt -c copy raw-merge.mp4
```

## Audio Mix Command (combat scene example)
```bash
ffmpeg -i raw-merge.mp4 -i shadow-emerge.mp3 -i combat-hit1.mp3 -i combat-hit2.mp3 \
  -filter_complex \
  "[1:a]volume=0.9,adelay=2000|2000[A];\
   [2:a]volume=1.2,adelay=5000|5000[B];\
   [3:a]volume=1.2,adelay=9000|9000[C];\
   [A][B][C]amix=inputs=3:duration=first[audio]" \
  -map 0:v -map "[audio]" -c:v copy -c:a aac -b:a 192k -shortest scene-with-audio.mp4
```

## Chapter Title Overlay (15s scene)
```bash
ffmpeg -i scene-with-audio.mp4 \
  -vf "drawtext=text='CHAPTER [N]':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf:fontsize=24:fontcolor=white:alpha=0.6:x=(w-text_w)/2:y=(h-text_h)/2-50:enable='between(t,0.5,2.5)', \
  drawtext=text='[CHAPTER TITLE]':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf:fontsize=36:fontcolor=#CC0000:x=(w-text_w)/2:y=(h-text_h)/2:enable='between(t,1,3)', \
  drawtext=text='A GenTech Labs Production':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf:fontsize=18:fontcolor=white:alpha=0.5:x=(w-text_w)/2:y=h-60:enable='between(t,0,15)'" \
  -c:a copy -preset fast final.mp4
```
