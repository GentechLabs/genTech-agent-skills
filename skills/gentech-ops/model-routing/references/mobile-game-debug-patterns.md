# Mobile HTML5 Game — Debug Patterns (Jul 17, 2026)

Captured during the Visual Kei Tap rhythm game build. These patterns recur across Canvas game projects on mobile.

## Symptom: Game Ends Immediately With All-Zero Score

Player presses PLAY, results screen shows immediately with Score=0, Max Combo=0, Perfect=Good=Miss=0.

### Root Cause Checklist (ordered by likelihood)

#### 1. HTML Audio autoplay failure (HIGHEST)
On mobile, `audio.play()` may silently fail even after a user gesture. `currentTime` stays at 0.

**Fix:** Use Web Audio API (`AudioContext`) instead:
```javascript
const actx = new AudioContext();
const resp = await fetch(url);
const buf = await resp.arrayBuffer();
const decoded = await actx.decodeAudioData(buf);
const source = actx.createBufferSource();
source.buffer = decoded;
source.connect(actx.destination);
source.start(0);
// Track time via: actx.currentTime - startTime
```

**Why AudioContext works where HTML Audio fails:**
- Created on user gesture (PLAY button click)
- `currentTime` always accurate — no mobile quirks
- No `loadedmetadata` race — `decodeAudioData` returns when ready

#### 2. Async race — beats not generated before game loop (HIGH)
```javascript
async function startGame() {
  state = S.PLAY;           // ← game loop starts processing immediately
  await loadAudio();        // ← waits here
  game.beats = genBeats();  // ← beats set AFTER the await
}
```
The game loop runs `checkMiss()` with an empty `beats` array during `loadAudio()`.

**Fix:** Explicitly clear beats AND guard end-game behind 10s minimum:
```javascript
game.beats = [];
await loadAudio();
game.beats = genBeats();
// In loop:
if (game.elapsed > 10 && game.elapsed >= getDur() - 0.5) endGame();
```

#### 3. Undefined variable in draw function (MEDIUM)
A `ReferenceError` in a draw function does NOT stop `requestAnimationFrame`. Game logic continues but visuals break silently.

**Common — lowercase `w` vs uppercase `W`:**
```javascript
// BUG:
function notes() {
  const h = H/dpr, lw = w/3;  // 'w' undefined!
}
```
**Fix:** Every draw function defines its own locals:
```javascript
function notes() {
  const w = W/dpr, h = H/dpr;
  // ...
}
```

**Prevention:** Run Node.js syntax check before deploying:
```bash
node -e "
const fs = require('fs');
const html = fs.readFileSync('game.html','utf8');
const m = html.match(/<script>([\s\S]*?)<\/script>/);
try { new Function(m[1]); console.log('OK'); }
catch(e) { console.log(e.message); }
"
```

#### 4. getDuration() returns near-zero (LOW)
On mobile, `audio.duration` can be NaN/Infinity before metadata loads. Fallback must always return a sensible value.

## GitHub Pages Caching Issue

### Symptom: Fixes deployed but browser still shows broken version.

**Root cause:** GitHub Pages CDN caches files for up to 10 minutes.

**Fix:** Deploy to a fresh URL path instead of overwriting the old one:
```bash
mkdir -p games/v2       # new path, zero cache risk
cp index.html games/v2/ 
git add games/v2/ && git push
```
Add a version stamp in the UI to verify:
```html
<span style="color:#333;font-size:8px">v2.1</span>
```

## Touch Events Not Registering

**Checklist:**
- `touch-action: none` in CSS
- `{ passive: false }` on `touchstart` listener
- `e.preventDefault()` in the handler
- Single handler on canvas, not on HTML overlay (which blocks touch events)
- `canvas.getBoundingClientRect()` for coordinate mapping
- Use `touchstart` not `click` for mobile — avoid the 300ms tap delay

## AudioContext Blocked by Brave Browser

**Symptom:** Game loads but never starts — audio doesn't play, elapsed stays at 0.

**Cause:** Brave blocks AudioContext by default as a fingerprinting vector.

**Fix:** Call `actx.resume()` before starting playback:
```javascript
if (actx && actx.state === 'suspended') await actx.resume();
```
Handle resume failure with a "Tap to play" overlay.

## Playability Patterns

### Hit Zone Position
- **Too low (80%+)** — Notes appear to fall too fast, less reaction time
- **Sweet spot: 60-65%** — Gives 35-40% more visible travel distance
- **Note speed:** 180-200 px/s for rhythm games; 280+ is too fast for most players

### Visual Feedback
- **Hit zone markers:** Glowing circles/beams at each lane's hit point show where to tap
- **Splash particles:** 12+ colored particles + white sparkles on perfect hit
- **Expanding ring:** Animated ring on each lane when hit
- **Note trails:** Fading gradient trail behind each falling note improves tracking

### Lane Separators
- Thin lines are invisible on mobile
- Use glowing beams (soft gradient with radial glow) instead
- Each lane needs a distinct target marker at the hit zone

## Testing Protocol

1. **Syntax check first:** `node -e "new Function(extractedJS)"`
2. **Headless logic test:** Node.js simulation of game loop (60 frames × duration)
3. **Fresh URL deploy:** Never overwrite — use new path to bypass CDN cache
4. **Verify live:** `curl -s -o /dev/null -w "%{http_code}" https://url`
5. **Test on actual mobile:** Brave, Chrome, Safari iOS — all have different quirks

## Model Audit Prompt Size Limits

When sending code to audit models:
| Model | Max useful prompt size | Notes |
|-------|----------------------|-------|
| Kimi K2.7 Code | ~6-7K chars | Empty response above threshold |
| GLM-5.2 (via OpenCode Go) | ~8K chars | Best for code review excerpts |
| DeepSeek V4 Flash | Full file OK for <30KB | Best for initial build |

### Mobile HTML5 Game Checklist

- [ ] Use `AudioContext`, not `HTML Audio`
- [ ] Loading overlay while audio/tracks load
- [ ] End-game guard: 10s+ minimum play time
- [ ] Every draw function: own `w = W`, `h = H`
- [ ] CSS `touch-action: none` + `{passive: false}` on touch handlers
- [ ] Explicit clear of beats/state before async operations
- [ ] Cache-busting on GitHub Pages: fresh URL per deploy
- [ ] Note speed 180-200, hit zone at 60-65%
- [ ] Glowing lane beams, not thin dividers
- [ ] Particle splash on hit (12+ particles)
- [ ] Note trails for visibility
