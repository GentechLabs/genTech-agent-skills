# FAL image_generate — Reference Image Hosting (Failure Transcript)

Session: 2026-08-01 — couple portrait from two user-sent photos.

## Goal
Pass two local photos as `reference_image_urls` to `image_generate` so the new image keeps authentic facial features.

## What failed (in order)

1. **Local absolute paths**
   - Input: `reference_image_urls: ["/root/.hermes/profiles/gentech/image_cache/img_x.jpg", ...]`
   - Error: `file_download_error` — "Failed to download the file... input: ['/root/...']"
   - Cause: FAL is a remote backend; it interprets the path as a URL and cannot reach the VPS filesystem. Local paths only work in the agent-side tool, not the remote generation backend.

2. **catbox.moe uploads**
   - Upload: `curl -F "reqtype=fileupload" -F "fileToUpload=@img.jpg" https://catbox.moe/user/api.php` → `https://files.catbox.moe/<id>.jpg`
   - Verified accessible locally (`curl -o /dev/null -w "%{http_code}"` → 200), but FAL still returned `file_download_error`.
   - Cause: FAL's downloader cannot reach files.catbox.moe (blocked/unreachable from its network).

3. **tmpfiles.org uploads**
   - Upload: `curl -F "file=@img.jpg" https://tmpfiles.org/api/v1/upload` → `https://tmpfiles.org/<id>/<name>.jpg`
   - Error: `image_load_error` — "Failed to load the image... not corrupted / supported format" (different error than download failure).
   - Cause: the direct URL returns an HTML viewer page (`200 text/html`), not raw bytes. The `/dl/` variant returns `302 text/html` that redirects back to the same HTML page. FAL downloaded HTML, then failed to decode it as an image.

## What worked

Serve the images from the VPS's own public nginx:

```bash
# 1. Convert progressive JPEG -> baseline JPEG (some FAL models reject progressive)
python3 -c "
from PIL import Image
for name in ['a', 'b']:
    img = Image.open(name + '.jpg')
    if img.mode != 'RGB': img = img.convert('RGB')
    img.save(name + '_baseline.jpg', 'JPEG', quality=95, progressive=False)
"

# 2. Copy into the public web root (nginx site: demo.gentechlabs.net, root /var/www/gentechlabs)
mkdir -p /var/www/gentechlabs/refs
cp a_baseline.jpg /var/www/gentechlabs/refs/man.jpg
cp b_baseline.jpg /var/www/gentechlabs/refs/woman.jpg
chmod 644 /var/www/gentechlabs/refs/*.jpg

# 3. Verify content type + size before generating
curl -s -o /dev/null -w "%{http_code} %{content_type} %{size_download}\n" https://demo.gentechlabs.net/refs/man.jpg
# expect: 200 image/jpeg <bytes>

# 4. Pass those URLs to image_generate reference_image_urls
```

## Verification pattern
After generation: download the result (`curl -s -L -o out.png <fal_url>`), check `file out.png`, then `vision_analyze` against the original references to confirm likeness, pose, and quality before showing the user.

## Rules of thumb
- Always verify the URL returns `image/jpeg` (or `image/png`) with `curl -o /dev/null -w "%{content_type}"` before handing it to FAL.
- `image_load_error` usually means FAL downloaded HTML or a corrupt file; `file_download_error` means FAL could not reach the host at all.
- The VPS nginx root is the most reliable public host for this use — it is already reachable and serves correct content types.

---

# Follow-up: 2026-08-02 — photo → graphic art, http.server fallback

Same task class: transform one user-sent photo into a stylized graphic art illustration via `image_generate` with `image_url` (single-image edit mode, same FAL downloader).

## Sequence
1. `image_url: /root/.hermes/profiles/gentech/image_cache/img_60e8e977fef8.jpg` → `file_download_error` (same as 2026-08-01; FAL can't read local paths).
2. tmpfiles.org upload → direct URL served `200 text/html` (viewer page), `/dl/` variant `302` → back to HTML. FAL: `image_load_error`. (Already documented — re-hit because the skill wasn't loaded first.)
3. 0x0.st → **uploads disabled**: "uploads disabled because it's been almost nothing but AI botnet spam for the past few months... no ETA." Transient host status; re-check before relying on it.
4. **Succeeded with python http.server on the VPS**:
   ```bash
   # Hermes terminal background=true (nohup/disown/setsid wrappers are rejected):
   cd /root/.hermes/profiles/gentech/image_cache && python3 -m http.server 8791 --bind 0.0.0.0
   ```
   - First attempt on port **8765 failed: `OSError: [Errno 98] Address already in use`** — an existing python3 service was already serving a web app there. Ports on this VPS are not free by default.
   - Port 8791 bound cleanly; verified:
     ```
     local:  200 image/jpeg
     public: 200 image/jpeg   (http://<vps-public-ip>:8791/img_60e8e977fef8.jpg)
     ```
   - FAL accepted the URL; generation succeeded.
5. Downloaded result, `file out.png` → 1024x1024 PNG, `vision_analyze` to confirm likeness, delivered via `MEDIA:`.

## Notes
- The `404 application/json` from python's SimpleHTTPServer class means the file isn't there (or wrong dir); if you get that on a port you intended to bind, first check `ss -tlnp | grep <port>` to see who owns it.
- Content-type check is the single best gate: FAL only needs raw bytes with a decodable image content type.
- Kill the one-off server after delivery (`process action=kill`) — these are throwaway hosts.
