# GSAP Timeline → MP4 via Chrome Headless + CDP Frame Capture

Proven 2026-08-16 (GenTech "website → paid API" explainer). Renders a custom
GSAP animation to MP4 by driving Chrome headless over CDP, seeking the timeline
to each frame time, screenshotting, then encoding with ffmpeg. No html-video /
HyperFrames / Remotion dependency — works for any single-file GSAP animation.

## Why this exists

html-video templates are agent-driven but generic; when you need a *specific*
3-beat product story with exact copy, a hand-built GSAP HTML + CDP capture is
faster and fully controlled. This is the "custom GSAP" path without pulling in
the full HyperFrames toolchain.

## The animation HTML contract

The GSAP timeline must be registered on `window.__timelines` so the capture
script can seek it:

```html
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<script>
  window.__timelines = window.__timelines || {};
  const tl = gsap.timeline({ paused: true });
  tl.to({}, { duration: 57 }, 0);   // total duration in seconds
  tl.fromTo("#beat1 .title", {opacity:0, y:40}, {opacity:1, y:0, duration:0.8}, 0.6);
  // ... all beats ...
  window.__timelines["my-anim"] = tl;
</script>
```

- Use **system fonts** (`Liberation Sans`, `DejaVu Sans`, `DejaVu Sans Mono`) —
  Google Fonts do NOT load in headless Chrome (blank text).
- Use `data-start`/`data-duration` on beat layers only if you're using the
  html-video orchestrator; for raw CDP capture the GSAP timeline alone drives it.

## Capture script (Node, `ws` required)

```bash
cd <project-dir> && npm init -y && npm install ws
```

```js
// capture-frames.mjs — run from the dir that has node_modules/ws
import { writeFileSync } from 'fs';
const FPS = 30, DURATION = 57, TOTAL = FPS * DURATION;
const OUT = '/tmp/explainer-frames';
const ws = await fetch('http://localhost:9225/json').then(r => r.json());
const page = ws.find(t => t.type === 'page');
const WebSocket = (await import('ws')).default;
const sock = new WebSocket(page.webSocketDebuggerUrl);
let id = 0; const pending = new Map();
function send(method, params = {}) {
  return new Promise(res => { const m = ++id; pending.set(m, res); sock.send(JSON.stringify({id:m, method, params})); });
}
sock.on('message', d => { const m = JSON.parse(d.toString()); if (m.id && pending.has(m.id)) { pending.get(m.id)(m.result); pending.delete(m.id); } });
await new Promise(r => sock.on('open', r));
await send('Page.enable'); await send('Runtime.enable');
// WAIT for the timeline to register before capturing (critical — see pitfalls)
let ready = false;
for (let i = 0; i < 50 && !ready; i++) {
  const r = await send('Runtime.evaluate', { expression: `(typeof window.__timelines !== 'undefined' && Object.keys(window.__timelines).length > 0)` });
  ready = r.result && r.result.value === true;
  if (!ready) await new Promise(r => setTimeout(r, 200));
}
await new Promise(r => setTimeout(r, 500));
for (let i = 0; i < TOTAL; i++) {
  const t = i / FPS;
  await send('Runtime.evaluate', { expression: `Object.values(window.__timelines)[0].seek(${t})` });
  await new Promise(r => setTimeout(r, 15));
  const shot = await send('Page.captureScreenshot', { format: 'png' });
  writeFileSync(`${OUT}/frame_${String(i).padStart(5,'0')}.png`, Buffer.from(shot.data, 'base64'));
  if (i % 30 === 0) console.log(`captured ${i}/${TOTAL}`);
}
console.log('DONE'); process.exit(0);
```

## Launch Chrome + capture + encode

```bash
# Launch headless Chrome with a debug port (use a FRESH port per run)
google-chrome --headless=new --no-sandbox --disable-gpu \
  --remote-debugging-port=9225 --user-data-dir=/tmp/chrome-explainer \
  --window-size=1920,1080 "file:///path/to/anim.html" &
sleep 4
rm -rf /tmp/explainer-frames && mkdir -p /tmp/explainer-frames
node capture-frames.mjs

# Encode frames → video (scale to even dims; headless may give 1920x941 not 1080)
ffmpeg -y -framerate 30 -i "/tmp/explainer-frames/frame_%05d.png" \
  -vf "scale=1920:1080" -c:v libx264 -pix_fmt yuv420p -crf 20 \
  video-only.mp4
```

## Muxing a voiceover (any ElevenLabs clone)

Generate narration segments (one per beat, ≤35s each for cloned voices), concat,
then mux with the video:

```bash
ffmpeg -y -f concat -safe 0 -i concat-audio.txt -c copy narration.mp3
ffmpeg -y -i video-only.mp4 -i narration.mp3 \
  -c:v copy -c:a aac -b:a 192k \
  -af "afade=t=in:st=0:d=0.5,afade=t=out:st=<dur-0.5>:d=0.5" \
  -shortest -movflags +faststart narrated.mp4
```

**Sync rule:** get the narration total duration first (`ffprobe`), then set the
GSAP timeline `duration` to match. The beats should be timed to the narration
segments (e.g. seg1 0-8s, seg2 8-17s, ...). Verify audio is present at each beat
boundary with `ffmpeg -ss <t> -t 1 -i out.mp4 -af volumedetect -f null -`.

## Verification (MANDATORY before delivery)

- **OCR beats, don't trust vision_analyze alone.** `tesseract frame.png -` reads
  text reliably; vision_analyze was inconsistent this session (misread a correct
  frame as a "loading spinner"). Extract frames at each beat time and OCR them.
- Check frame dimensions: headless Chrome with `--window-size=1920,1080` may
  capture 1920x941 (missing the browser chrome height). Always `-vf scale=1920:1080`
  on encode, and confirm with `python3 -c "from PIL import Image; print(Image.open('f.png').size)"`.

## Pitfalls

- **Timeline not ready → first beat renders as a blank/loading frame.** The
  capture script MUST poll for `window.__timelines` to be registered before
  seeking. Without the wait, beat 1 (the hook) is a black frame while later beats
  work — because GSAP loaded after capture started.
- **`ws` module not found in ESM.** The capture script must live in a dir with
  `node_modules/ws` (run `npm install ws` there). A script in `/tmp` can't resolve
  it even if `ws` is installed globally.
- **Chrome as root needs `--no-sandbox`.** Without it Chrome exits immediately
  with a zygote error.
- **`--window-size` doesn't guarantee 1080 height.** Scale on encode to force
  even dimensions (libx264 rejects odd heights like 941).
- **Fresh debug port per run.** Reusing a port with a stale Chrome process causes
  "Cannot read properties of undefined (reading 'webSocketDebuggerUrl')" — the
  page target isn't listed. Create a page via `curl -X PUT "http://localhost:PORT/json/new?about:blank"` if no page target exists.
