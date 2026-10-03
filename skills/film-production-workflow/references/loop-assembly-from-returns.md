# Loop Assembly from Returned Clips

Reference companion to the `Loop / Trailer Assembly from Returned Clips` section of `film-production-workflow/SKILL.md`.

Use this when a collaborator sends short clips back one at a time and says *"make this first / make this fifth / use the trimmed one / loop it"*.

## Decision tree

1. **Did they name the scene?**
   - Yes: still verify by frame match.
   - No: identify by frame match.

2. **Is the returned clip a different duration from the master?**
   - Same duration: use the master (likely they just confirmed it).
   - Shorter: they probably trimmed it. Ask explicitly: *"use the one you trimmed, or full length?"*
   - Longer: review manually; Telegram re-encode usually doesn't lengthen.

3. **Did they say "loop it"?**
   - Yes: build the sequence, then `stream_loop -1` to the master audio duration.
   - No: deliver the sequence standalone.

## Frame-matching script

```python
import os, subprocess, sys

FS = 64 * 36

def frames_of(path, fps):
    out = path + '.rgb'
    subprocess.run([
        'ffmpeg','-y','-v','error','-i',path,
        '-vf',f'fps={fps},scale=64:36','-f','rawvideo','-pix_fmt','gray',out
    ], check=True)
    data = open(out,'rb').read()
    return [data[i*FS:(i+1)*FS] for i in range(len(data)//FS)]

def avg_min_dist(unknown, candidate):
    # for each unknown frame, nearest candidate frame (downsampled)
    total = 0
    for A in unknown:
        best = 1e9
        for B in candidate:
            d = sum(abs(A[i]-B[i]) for i in range(0, FS, 11)) / (FS//11)
            if d < best:
                best = d
        total += best
    return total / len(unknown)

unknown = sys.argv[1]
candidates = sys.argv[2:]

u = frames_of(unknown, 6)
rows = []
for c in candidates:
    tag = os.path.basename(c)
    rows.append((tag, avg_min_dist(u, frames_of(c, 4))))

for tag, d in sorted(rows, key=lambda x: x[1])[:5]:
    print(f"{tag:40s} {d:.1f}")
```

## Normalising a returned trim

```bash
ffmpeg -y -v error -i "his_trim.mp4" -vf "fps=24,scale=1280:720" -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p -an his_trim_normalised.mp4
```

## Verifying the swap and the loop point

```python
import subprocess, os

FS = 64 * 36

def frame_at(path, t):
    p = f'/tmp/{os.path.basename(path)}_{t}.rgb'
    subprocess.run([
        'ffmpeg','-y','-v','error','-ss',str(t),'-i',path,
        '-frames:v','1','-vf','scale=64:36','-f','rawvideo','-pix_fmt','gray',p
    ], check=True)
    return open(p,'rb').read()

def diff(A, B):
    return sum(abs(A[i]-B[i]) for i in range(0, FS, 11)) / (FS//11)

loop = "NO-BRAKES-LOOP-v3.mp4"
trim = "his_trim.mp4"
seq_dur = 23.25  # fill in actual

print("open vs trim 1.0s:", diff(frame_at(loop, 1.0), frame_at(trim, 1.0)))
print("loop point vs trim 0.25s:", diff(frame_at(loop, seq_dur + 0.25), frame_at(trim, 0.25)))
```

A match shows a small diff (typically <15). The loop-point check proves the sequence cycles cleanly.

## Loop command

```bash
ffmpeg -y -v error -stream_loop -1 -i sequence.mp4 -i master.mp3 \
  -map 0:v:0 -map 1:a:0 -t <master_duration> \
  -c:v libx264 -preset slow -crf 29 -maxrate 1500k -bufsize 3000k \
  -g 48 -keyint_min 48 -pix_fmt yuv420p \
  -c:a aac -b:a 96k -movflags +faststart output.mp4
```

Then de-peak if the master runs hot:

```bash
ffmpeg -y -v error -i output.mp4 -i master.mp3 -map 0:v:0 -map 1:a:0 \
  -c:v copy -af "volume=-1.5dB" -c:a aac -b:a 96k -t <master_duration> output_web.mp4
```

Verify with `volumedetect`: peak ~−0.9 dB.

## Size fallback table

| Target | CRF | Maxrate | Typical 2:30 file |
|--------|-----|---------|-------------------|
| Full quality hosted | 23 | none | ~55–60 MB |
| Telegram-safe | 29 | 1500k | ~30–35 MB |
| Severe Telegram pinch | 31 | 1000k | ~20–25 MB |

Always state the trade-off when raising CRF.
