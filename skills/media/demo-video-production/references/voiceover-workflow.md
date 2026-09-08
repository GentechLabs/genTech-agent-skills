# Demo Video Voiceover Workflow

For hackathon demo videos — generate segmented voiceover, clean, concatenate with natural pauses.

## Pattern (proven on AdaptiveFolio, May 26, 2026)

### Step 1: Break script into timed segments
Write each segment as a separate text block (2-4 sentences, ~15-20 sec each). Name them sequentially: `segment-1-hook.mp3`, `segment-2-problem.mp3`, etc.

### Step 2: Generate each segment
Use `text_to_speech` tool with the target voice. Generate into a dedicated folder:
```bash
mkdir -p /root/{project-name}-demo
```

### Step 3: Clean all segments with ffmpeg
```bash
mkdir -p clean
for f in segment-*.mp3; do
  name=$(basename "$f")
  ffmpeg -y -i "$f" -af "afftdn=nf=-25,highpass=f=80,lowpass=f=12000,acompressor=threshold=-20dB:ratio=4:attack=5:release=50,loudnorm=I=-16:TP=-1.5:LRA=11" "clean/$name"
done
```

### Step 4: Create silence gap + concatenate
```bash
# 0.8s silence for natural pause between segments
ffmpeg -y -f lavfi -i anullsrc=r=44100:cl=mono -t 0.8 -q:a 9 -acodec libmp3lame clean/silence.mp3

# Build concat file
for f in clean/segment-*.mp3; do echo "file '$f'"; echo "file 'clean/silence.mp3'"; done | sed '$ d' > clean/concat.txt

# Concatenate
ffmpeg -y -f concat -safe 0 -i clean/concat.txt -c copy {project-name}-voiceover.mp3
```

### Step 5: Get duration
```bash
ffprobe -v quiet -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 output.mp3
```

**Target:** 1:50-2:10 for a 2-3 minute demo video.

## Title Screen
Create an HTML file matching the project's design aesthetic, then screenshot with Chrome headless:
```bash
google-chrome --headless --disable-gpu --screenshot=title-screen.png --window-size=1920,1080 --no-sandbox file:///path/to/title-screen.html
```

## Steve Harvey Voice Direction

**Pacing: SLOW and DELIBERATE.** Like Steve Harvey leaning in to talk to a guest on his show — not reading a news report. He pauses. He lets words land. He looks at the audience before delivering the punchline.

- Pauses between sections (use periods and line breaks for pacing in the script)
- Warm, motivational, punchy — but never rushed
- No AI self-reference. Just Steve being Steve.
- Opening hook: "Let me tell you something..." or "Good morning..."
- Closing motivator: "You built it. Now ship it."

**Script format for demo voiceover:**
```
[Hook line]

[Pause — new paragraph]

[Content section — short sentences, room to breathe]

[Pause — new paragraph]

[Closer — direct, punchy, Steve energy]
```
