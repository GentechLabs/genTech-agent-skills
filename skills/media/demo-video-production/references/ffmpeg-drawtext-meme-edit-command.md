# ffmpeg drawtext Meme-Edit — Reproducible Command

Proven Jul 2026: "Gentech Boot Sequence" — rowers whirlpool X clip (720x1280, 33.4s)
transformed into an agent-boot meme short. Copy the shape, change the text/timing.

## 1. Source clip from X/Twitter (fxtwitter)

```bash
# Get video URL + thumbnail
curl -s "https://api.fxtwitter.com/i/status/{TWEET_ID}" | python3 -c "
import json,sys
d=json.load(sys.stdin)['tweet']
m=d.get('media',{})
for v in m.get('videos',[]): print(v.get('url'))
"
# Download
curl -sL "<video_url>" -o source.mp4
ffprobe -v error -show_entries format=duration:stream=width,height -of default=noprint_wrappers=1 source.mp4
```

## 2. Full edit command (one ffmpeg call)

```bash
#!/bin/bash
# Boot-sequence meme edit pattern
FONT=/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf
OUT=gentech-agents-booting.mp4

# Escape helper for drawtext (colons, commas, apostrophes break the filter graph)
esc() { printf '%s' "$1" | sed 's/\\/\\\\/g; s/:/\\:/g; s/,/\\,/g; s/'"'"'/\\'"'"'/g'; }

TITLE1=$(esc "GENTECH BOOT SEQUENCE")
TITLE2=$(esc "9 agents. 1 whirlpool. all systems nominal.")
STATUS=$(esc "gentech@core:~$ ./power_on.sh --agents 9")
PUNCH1=$(esc "THIS IS WHAT 2AM")
PUNCH2=$(esc "LOOKS LIKE AT GENTECH")
L1=$(esc "[OK] treasury-sync       ONLINE")
L2=$(esc "[OK] lp-monitor          ONLINE")
L3=$(esc "[OK] yield-router        ONLINE")
L4=$(esc "[OK] signal-watcher      ONLINE")
L5=$(esc "[OK] content-engine      ONLINE")
L6=$(esc "[OK] trading-desk        ONLINE")

ffmpeg -y \
 -f lavfi -i "color=c=black:s=720x1280:d=2.2:r=30" \
 -i rowers-source.mp4 \
 -filter_complex "\
[0:v]drawtext=fontfile=$FONT:text='$TITLE1':fontsize=48:fontcolor=white:x=(w-text_w)/2:y=h*0.40,drawtext=fontfile=$FONT:text='$TITLE2':fontsize=26:fontcolor=0x88ff88:x=(w-text_w)/2:y=h*0.40+70[title];\
[1:v]drawtext=fontfile=$FONT:text='$STATUS':fontsize=26:fontcolor=white:box=1:boxcolor=black@0.65:boxborderw=10:x=24:y=36,\
drawtext=fontfile=$FONT:text='$L1':fontsize=30:fontcolor=0x88ff88:box=1:boxcolor=black@0.55:boxborderw=8:x=36:y=h*0.76:enable='between(t,2.2,33.4)',\
drawtext=fontfile=$FONT:text='$L2':fontsize=30:fontcolor=0x88ff88:box=1:boxcolor=black@0.55:boxborderw=8:x=36:y=h*0.76+44:enable='between(t,6.5,33.4)',\
drawtext=fontfile=$FONT:text='$L3':fontsize=30:fontcolor=0x88ff88:box=1:boxcolor=black@0.55:boxborderw=8:x=36:y=h*0.76+88:enable='between(t,10.8,33.4)',\
drawtext=fontfile=$FONT:text='$L4':fontsize=30:fontcolor=0x88ff88:box=1:boxcolor=black@0.55:boxborderw=8:x=36:y=h*0.76+132:enable='between(t,15.1,33.4)',\
drawtext=fontfile=$FONT:text='$L5':fontsize=30:fontcolor=0x88ff88:box=1:boxcolor=black@0.55:boxborderw=8:x=36:y=h*0.76+176:enable='between(t,19.4,33.4)',\
drawtext=fontfile=$FONT:text='$L6':fontsize=30:fontcolor=0x88ff88:box=1:boxcolor=black@0.55:boxborderw=8:x=36:y=h*0.76+220:enable='between(t,23.7,33.4)',\
drawtext=fontfile=$FONT:text='$PUNCH1':fontsize=46:fontcolor=white:box=1:boxcolor=black@0.75:boxborderw=14:x=(w-text_w)/2:y=h*0.42:enable='gte(t,30.2)',\
drawtext=fontfile=$FONT:text='$PUNCH2':fontsize=46:fontcolor=white:box=1:boxcolor=black@0.75:boxborderw=14:x=(w-text_w)/2:y=h*0.42+70:enable='gte(t,30.2)'[vid];\
[title][vid]concat=n=2:v=1:a=0[vout]" \
 -map "[vout]" \
 -c:v libx264 -preset medium -crf 23 -g 48 -keyint_min 48 -pix_fmt yuv420p -movflags +faststart \
 "$OUT"
```

## 3. Frame verification (account for the concat offset!)

`enable` timestamps run on the source clock BEFORE concat. Title card is 2.2s, so:
`final_t = source_t + 2.2`. The punchline gated at source t=30.2 appears at final 32.4s.

```bash
# Check punchline at final 34.0s (source 31.8 > 30.2), cropped to the text band
ffmpeg -y -ss 34.0 -i "$OUT" -vf "crop=720:320:0:430" -frames:v 1 check-punch.png
# Then vision_analyze(check-punch.png, "What text appears here? Read it verbatim.")
```

DO NOT verify at `-ss 32.0` thinking the punchline starts at 30.2 — you'll see
"no text" and waste a rebuild cycle. Add the title duration.

## 4. Deploy

```bash
mkdir -p /var/www/gentechlabs/videos
cp "$OUT" /var/www/gentechlabs/videos/"$OUT"          # fresh filename — Cloudflare cache
curl -sI https://gentechlabs.net/videos/"$OUT" | head -6   # expect HTTP/2 200
```

## Debugging notes

- **Alpha fade invisible (whole clip):** `alpha='if(lt(t,N),0,min(1,(t-N)*2))'` parsed
  fine but rendered nothing — alpha is not evaluated per-frame in drawtext. Use `enable`.
- **Log lines visible but punchline missing:** check the concat offset first, then the
  enable expression. Both bites happened in the same session (Jul 2026).
- **`gentech@core:~$` in drawtext:** the `$` is fine inside single-quoted filter values;
  the danger chars are `:` `,` `'` `%`.
