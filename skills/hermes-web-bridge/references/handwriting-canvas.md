# Handwriting Canvas for Constrained Devices

## Problem
Devices like Ray-Ban smart glasses have tiny or no keyboards. Users need an alternative input method — drawing their message by hand.

## Solution: Canvas + Vision AI

### Frontend: Drawing Canvas

```html
<div class="canvas-wrap">
    <canvas id="canvas" width="600" height="280"></canvas>
</div>
<div class="draw-tools">
    <button onclick="setPen()">✏️ Pen</button>
    <button onclick="setEraser()">◻️ Erase</button>
    <button onclick="clearCanvas()">🗑️ Clear</button>
    <button onclick="sendDrawing()">📨 Send</button>
</div>
```

```javascript
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
let drawing = false, lastX = 0, lastY = 0;

// High-DPI scaling
const rect = canvas.parentElement.getBoundingClientRect();
canvas.width = rect.width * 2;
canvas.height = 280 * 2;
canvas.style.height = '280px';
ctx.scale(2, 2);
ctx.lineCap = 'round';
ctx.strokeStyle = '#00ff88';
ctx.lineWidth = 3;

// Touch/mouse events
canvas.addEventListener('touchstart', e => {
    e.preventDefault();
    drawing = true;
    const t = e.touches[0];
    const r = canvas.getBoundingClientRect();
    lastX = t.clientX - r.left;
    lastY = t.clientY - r.top;
});
canvas.addEventListener('touchmove', e => {
    e.preventDefault();
    if (!drawing) return;
    const t = e.touches[0];
    const r = canvas.getBoundingClientRect();
    const x = t.clientX - r.left;
    const y = t.clientY - r.top;
    ctx.beginPath();
    ctx.moveTo(lastX, lastY);
    ctx.lineTo(x, y);
    ctx.stroke();
    lastX = x; lastY = y;
});
canvas.addEventListener('touchend', e => { e.preventDefault(); drawing = false; });

// Send to server
async function sendDrawing() {
    const dataUrl = canvas.toDataURL('image/png');
    const res = await fetch('/api/draw', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token },
        body: JSON.stringify({ image: dataUrl }),
    });
    const data = await res.json();
    // data.response = transcribed text
    clearCanvas();
}
```

### Server: Vision AI Reading

```python
import base64, os, time

@app.post("/api/draw")
async def api_draw(request: Request):
    body = await request.json()
    image_data = body.get("image", "")
    
    # Save base64 image to temp file
    header, encoded = image_data.split(",", 1)
    img_bytes = base64.b64decode(encoded)
    tmp_path = f"/tmp/rayban_draw_{int(time.time())}.png"
    with open(tmp_path, "wb") as f:
        f.write(img_bytes)
    
    # Ask Hermes to read the handwriting
    prompt = (
        f"A user wrote this by hand on their Ray-Ban smart glasses. "
        f"Read the handwriting in this image and type out exactly what it says. "
        f"Image saved at: {tmp_path}"
    )
    result = await ask_hermes(prompt, sess.get("hermes_session"))
    
    # Clean up
    try: os.unlink(tmp_path)
    except: pass
    
    return {"response": result.get("response", "Could not read")}
```

## Design Notes

- Canvas should be **full-width** with rounded corners
- Use **green (#00ff88)** pen on **dark (#0a0a12)** background for contrast
- Eraser is just drawing with background color at wider stroke
- **touch-action: none** on canvas element to prevent browser scroll/zoom
- Canvas tools should be **40-50px** buttons with clear labels
- "Send" button should be visually distinct (filled accent color)

## Pitfalls

1. **High-DPI displays:** Scale canvas by devicePixelRatio for crisp lines
2. **Touch events need passive:false:** `{ passive: false }` to prevent scroll
3. **Base64 size:** Canvas drawings can be 100KB+ as PNG. Compress or warn about slow connections
4. **Hermes vision:** The `hermes chat -q` command needs to see the image file path. Make sure temp files are accessible to the Hermes process
5. **Clean up temp files:** Always delete /tmp/draw_*.png after reading to prevent disk fill
