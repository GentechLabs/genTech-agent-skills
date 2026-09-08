// Capture a GSAP animation HTML to PNG frames via Chrome CDP, then encode with ffmpeg.
// Usage: node capture-gsap-frames.mjs
//   - Requires: Chrome running with --remote-debugging-port=9223, `ws` installed in this dir
//   - Edit OUT, PORT, FPS, DURATION, and the HTML URL below.
// Encode after: ffmpeg -framerate 30 -i frame_%05d.png -vf "scale=1920:1080" -c:v libx264 -pix_fmt yuv420p -crf 20 -movflags +faststart out.mp4
import { writeFileSync } from 'fs';

const PORT = 9223;
const FPS = 30;
const DURATION = 30;
const TOTAL = FPS * DURATION;
const OUT = '/tmp/explainer-frames';

const ws = await fetch(`http://localhost:${PORT}/json`).then(r => r.json());
const page = ws.find(t => t.type === 'page');
const WebSocket = (await import('ws')).default;
const sock = new WebSocket(page.webSocketDebuggerUrl);

let id = 0;
const pending = new Map();
function send(method, params = {}) {
  return new Promise((resolve) => {
    const msgId = ++id;
    pending.set(msgId, resolve);
    sock.send(JSON.stringify({ id: msgId, method, params }));
  });
}
sock.on('message', (data) => {
  const msg = JSON.parse(data.toString());
  if (msg.id && pending.has(msg.id)) { pending.get(msg.id)(msg.result); pending.delete(msg.id); }
});
await new Promise(r => sock.on('open', r));
await send('Page.enable');
await send('Runtime.enable');

// CRITICAL: wait until the GSAP timeline is registered before capturing,
// else the first beat renders as a blank/loading frame.
let ready = false;
for (let i = 0; i < 50 && !ready; i++) {
  const res = await send('Runtime.evaluate', {
    expression: `(typeof window.__timelines !== 'undefined' && Object.keys(window.__timelines).length > 0)`
  });
  ready = res.result && res.result.value === true;
  if (!ready) await new Promise(r => setTimeout(r, 200));
}
console.log('timeline ready:', ready);
await new Promise(r => setTimeout(r, 500));

for (let i = 0; i < TOTAL; i++) {
  const t = i / FPS;
  await send('Runtime.evaluate', {
    expression: `Object.values(window.__timelines)[0].seek(${t})`
  });
  await new Promise(r => setTimeout(r, 15));
  const shot = await send('Page.captureScreenshot', { format: 'png' });
  writeFileSync(`${OUT}/frame_${String(i).padStart(5,'0')}.png`, Buffer.from(shot.data, 'base64'));
  if (i % 30 === 0) console.log(`captured ${i}/${TOTAL}`);
}
console.log('DONE');
process.exit(0);
