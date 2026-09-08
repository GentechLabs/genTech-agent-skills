---
name: image-generation-workflow
description: "Reliable image generation and editing with the FAL image_generate tool — reference-image hosting rules, progressive JPEG conversion, verification, and delivery. Use whenever generating or editing images from user-sent photos."
tags: [image-generation, image-editing, fal, reference-images, vision-verify]
triggers:
  - "edit this picture"
  - "make a portrait from these photos"
  - "combine these two images"
  - "generate an image from a photo"
  - "reference image"
---

# Image Generation Workflow (FAL image_generate)

## When to Use
- User sends photo(s) and asks to edit, combine, or generate a new image from them
- Creating portraits, composites, or stylized versions of real people
- Any use of `image_generate` with `reference_image_urls`

## Core Rule: Reference Images MUST Be Publicly Fetchable URLs

`image_generate` (FAL backend) downloads `reference_image_urls` itself. If FAL can't fetch the URL, generation fails. Verified failures (2026-08-01):

- **The same rule applies to `image_url` (image-to-image edits / transformations)** — FAL fetches that image remotely too. Passing a local absolute path to `image_url` fails with the identical `file_download_error`. Host it the same way before editing.

- ❌ **Local absolute paths** (`/root/.hermes/.../image_cache/x.jpg`) → `file_download_error`. FAL is remote; it cannot read the VPS filesystem.
- ❌ **catbox.moe uploads** → `file_download_error` even though the URL returns 200 locally. FAL cannot reach that host.
- ❌ **tmpfiles.org direct URLs** → `image_load_error`. The direct URL serves an HTML viewer page (200 text/html), not raw bytes; the `/dl/` variant 302s back to the same HTML. FAL downloaded HTML and couldn't decode it.
- ✅ **VPS public nginx root** → `https://demo.gentechlabs.net/refs/<file>.jpg` (root `/var/www/gentechlabs`, site `demo.gentechlabs.net`). Verified working.
- ✅ **VPS nginx root under `vanito.gentechlabs.net/characters/`** → `https://vanito.gentechlabs.net/characters/<file>.png` (same `/var/www/gentechlabs/characters/` web root). Also verified working for both `image_url` edits and `reference_image_urls` (Aug 4, 2026). Any path under the `/var/www/gentechlabs` nginx root that returns `image/png` / `image/jpeg` content type works — the specific subdomain/hostname is not restrictive.
- ✅ **VPS python http.server fallback** → `http://<vps-public-ip>:<fresh-high-port>/<file>.jpg` served from `image_cache/`. Verified working 2026-08-02 when the nginx root wasn't used. Raw bytes with correct `image/jpeg` content type — FAL accepts it.
- ⚠️ **0x0.st** → uploads were disabled as of 2026-08-02 ("AI botnet spam" notice). Don't plan on it.

## Workflow (proven)

1. **Locate the user's photos** in `image_cache/` (verify with `file` to check format/size).
2. **Convert progressive JPEG → baseline JPEG** — some FAL models reject progressive JPEGs:
   ```python
   from PIL import Image
   img = Image.open('in.jpg')
   if img.mode != 'RGB': img = img.convert('RGB')
   img.save('out_baseline.jpg', 'JPEG', quality=95, progressive=False)
   ```
3. **Copy into the public web root** (preferred — nginx serves correct content types):
   ```bash
   mkdir -p /var/www/gentechlabs/refs
   cp in_baseline.jpg /var/www/gentechlabs/refs/man.jpg
   chmod 644 /var/www/gentechlabs/refs/*.jpg
   ```
   **Fallback — quick one-off host from image_cache** (when nginx root isn't wired up):
   ```bash
   # Hermes-managed background process (NOT nohup — Hermes rejects shell-level wrappers):
   # terminal(background=true): cd /root/.hermes/profiles/gentech/image_cache && python3 -m http.server <fresh-high-port> --bind 0.0.0.0
   ```
   Pick a fresh high port (e.g. 879x) — don't assume a port is free. Verify BOTH locally and from the public IP before generating:
   ```bash
   curl -s -o /dev/null -w "local: %{http_code} %{content_type}\n" http://127.0.0.1:<port>/<file>.jpg
   curl -s -m 8 -o /dev/null -w "public: %{http_code} %{content_type}\n" http://<vps-public-ip>:<port>/<file>.jpg
   # both must show: 200 image/jpeg
   ```
4. **Verify the URL content type before generating**:
   ```bash
   curl -s -o /dev/null -w "%{http_code} %{content_type} %{size_download}\n" https://demo.gentechlabs.net/refs/man.jpg
   # expect: 200 image/jpeg <bytes>
   ```
5. **Generate** with `reference_image_urls` set to the public URLs. Include the reference subjects' EXACT appearance in the prompt text (hair, skin tone, facial hair, distinguishing marks) — the model reinterprets references, it does not copy them.
6. **Download the result** (`curl -s -L -o out.png <fal_url>`) and check `file out.png`.
7. **Pre-verify with `vision_analyze`** before showing the user — confirm likeness to references, pose, clothing, background, and that nothing is corrupted. Iterate if the model drifted.
8. **Deliver** via `MEDIA:/absolute/path` in the response.

## Character Sheet From a Photo (Olivia / Lightning pattern)

When the user sends a real photo and wants a multi-view character sheet from it (or a themed rework, e.g. "make him a Bloodborne hunter"), the proven recipe:

1. **vision_analyze the photo first** — extract every feature: hair style/length/fringe, eye shape/color, brows, nose, mouth, AND the facial structure (round/full-cheeked vs sharp/chiseled, soft vs defined jaw) and facial-hair type (connected goatee vs DISCONNECTED goatee with a shaved gap between mustache and chin tuft). Write these down — the prompt needs them.
2. **Host the source photo on the VPS first** (public URL rule above). Pass it as `image_url` so the face locks to the real person; optionally add `reference_image_urls=[official-style-reference.jpg]` for art-style consistency.
3. **Build a multi-view sheet prompt** — three orthographic views (front / profile / back) side by side + a weapon/prop detail inset. Repeat the exact features from step 1 in the prompt.
4. **vision_verify BEFORE showing** — compare the generated face against the source photo specifically for the drift below. Iterate silently until it matches.

## Established Characters (HIKARI / KAGE / Vanito cast) — use the character sheet FIRST

When the user asks to edit art to feature an established character (HIKARI, KAGE, Muffin, etc.), do NOT describe the character from memory — pull the canonical reference first. Vanito corrected this (Aug 6 2026): "Make sure to use our character sheet we have Hikari." The first pass came out as a generic rocker because I described her from memory instead of the sheet.

**Proven workflow:**
1. **Read the character sheet + visual bible** in the repo:
   - `/root/ProtoJay4789.github.io/09-Green Room/HIKARI Character Sheet.md`
   - `/root/ProtoJay4789.github.io/09-Green Room/HIKARI Complete Visual Bible.md`
   - (KAGE: `/root/vaults/gentech/music/vanito/kage-character-sheet.png`)
   The visual bible lists LOCKED reference image URLs hosted at `https://vanito.gentechlabs.net/characters/<file>.png` (e.g. `hikari-sakura-outfit-sheet.png`, `hikari-hairstyle-reference.png`).
2. **Pass the locked reference URLs as `reference_image_urls`** AND restate the exact canonical appearance in the prompt text (hair length/color/tips, bangs, outfit, accessories). The model reinterprets references — it does not copy them, so the prompt must carry the full detail.
3. **Confirm the outfit variant** — HIKARI has TWO canonical looks:
   - **Casual:** black cotton tee with white 桜 kanji, rolled sleeves, dark blue ripped skinny jeans, barefoot/sneakers.
   - **Concert/stage (gothic punk-rock):** strapless black corset with red crisscross lacing, tattered layered black skirt with red underlayer + high slits, fishnet arm sleeves + stockings, platform combat boots, black choker, chains, rings, long black nails.
   When the user says "use the concert outfit version" (or "stage version"), that's the corset look. Ask which variant if ambiguous.
4. **vision_verify BEFORE showing** — confirm the character matches the sheet (hair tips, bangs over eye, outfit elements) and the scene is preserved. Iterate silently until it matches.

**Pitfall — AI mangles kanji/lettering on character art.** The 桜 kanji on HIKARI's tee and any text on props (piano lids, signs) will be hallucinated or misspelled (e.g. "HIIKARI" on a piano lid). This is a known AI limitation — do not promise exact character rendering. If the text must be exact, hand it to Forge for a surgical compositing fix, or accept the AI's approximation.

## GPT Image 2 via BlockRun MCP (preferred when the Nous gateway doesn't proxy it)

When the Nous gateway returns **HTTP 402** for `fal-ai/gpt-image-2` (or the Nous portal is out of funds), do NOT fall back to FLUX/Klein 9B — use the **BlockRun MCP `blockrun_image` tool** instead. It provides GPT Image 2 (and other models) paid via USDC on Base/Solana, **no API keys needed**. Verified working 2026-08-07.

- **Tool:** `blockrun_image` (registered in the BlockRun MCP server at `/root/.hermes/blockrun-mcp/node_modules/@blockrun/mcp/dist/index.js`)
- **Default model:** `openai/gpt-image-2` ($0.06–0.12/image) — flagship, best on-image text + character consistency
- **Other models:** `google/nano-banana-pro` ($0.10, up to 4K photorealism), `zai/cogview-4` ($0.015, cheapest), `xai/grok-imagine-image` ($0.02), `openai/gpt-image-1` ($0.02–0.04)
- **Actions:** `generate` (text→image) and `edit` (img2img, up to 4 source images fused in one render)
- **Payment:** USDC on the active chain (Base default). Check balance with `blockrun_wallet action:"status"`.
- **Source images for edit** accept a base64 data URI, http(s) URL, or **local file path (auto-encoded)** — no public hosting needed, unlike FAL.

**Invoking when the tool isn't in the session toolset:** `blockrun_image` may not be loaded as a first-class tool in every session. Two reliable ways to reach GPT Image 2 directly:
1. **Standalone `.mjs` script — PREFERRED (verified working Aug 7 2026).** Import `ImageClient, getOrCreateWallet` from `/root/.hermes/blockrun-mcp/node_modules/@blockrun/llm/dist/index.js`, then `client.edit(prompt, sheetUri, { model:'openai/gpt-image-2', size:'1024x1024' })`. No MCP handshake, no toolset dependency — just `cd /root/.hermes/blockrun-mcp && node job.mjs`. Copy the ready-to-edit template from `templates/blockrun-gpt-image2-edit.mjs`.
2. Via the MCP protocol with a node spawn + JSON-RPC (see `references/blockrun-image-mcp.md`).

**User preference (Aug 7 2026): GPT Image 2 > FAL/FLUX Klein 9B for CHARACTER-CONSISTENT art.** When the user asks for character art (KAGE/HIKARI/Vanito cast) and wants GPT Image 2 quality, use the BlockRun path proactively — don't burn FAL generations on character work. GPT Image 2 edits the character sheet into the scene so hair/face/accessories stay locked, and it reliably honors **Dutch angle** and **low camera** phrasing that the FAL/FLUX Klein 9B backend misses (it defaults to straight-on).

**BlockRun quirks (Aug 7 2026):**
- `client.getBalance()` is broken (`not a function`) in the installed build. Read the on-chain USDC balance directly instead — see `scripts/blockrun-balance.mjs`.
- BlockRun CDN URLs can 502 transiently through the vision proxy. Download locally first (`curl -sL -o <name>.png <url>`), then vision-verify the local path.
- Wallet (Base): `0xebc8c71970EEb6973bd87F1FF146B3Ec4a5972f8`. GPT Image 2 img2img edit ≈ $0.128/image.

**Cost check:** a 1024×1024 gpt-image-2 generation costs ~$0.065. The BlockRun Base wallet typically holds enough for many generations.

## Verify the ACTIVE image model BEFORE image-to-image edits (user-corrected Aug 6 2026)

When the user asks to edit an existing image ("keep the picture the same, just change X"), the FIRST step is to confirm which model is actually active — not assume. The active model is `image_gen.model` in `config.yaml`. If that key is UNSET, Hermes silently defaults to **`fal-ai/flux-2/klein/9b`**, which is a fast text-to-image model that **reinterprets the entire scene on every edit** — it cannot do surgical "keep everything identical, change only the subject" edits. The room, lighting, and composition drift on every pass no matter how the prompt is phrased.

- **`fal-ai/flux-2/klein/9b`** (default when `image_gen.model` unset) — reinterprets the whole scene. Wrong tool for "keep the original, swap one element."
- **`fal-ai/gpt-image-2`** — SOTA text rendering + CJK, world-aware photorealism, far better at surgical edits and preserving the source scene. This is the model the user expects for character-swap edits.
- **`fal-ai/gpt-image-1.5`** — prompt adherence, also a better editor than Klein 9B.

**Check before editing:**
```bash
grep -A2 '^image_gen:' /root/.hermes/profiles/gentech/config.yaml
# if 'model:' is missing → it's running Klein 9B (reinterprets scenes)
```

**Set the model:**
```bash
hermes config set image_gen.model fal-ai/gpt-image-2
```
Note: `hermes config set` warns "'image_gen.model' is not a recognized config key" but still writes it — that warning is expected and harmless; verify the write landed in `config.yaml`.

**Pitfall — Nous gateway may not proxy gpt-image models yet.** On the Nous Subscription gateway (no direct `FAL_KEY`/`OPENAI_API_KEY` on the box), `fal-ai/gpt-image-2` and `fal-ai/gpt-image-1.5` can return **HTTP 402** ("model may not yet be enabled on the Nous Portal's FAL proxy"). If that happens, the gateway only proxies Klein 9B right now. Options, in order of preference: (a) **use BlockRun MCP `blockrun_image`** (see the section above — GPT Image 2 paid via USDC, no API keys, works even when the Nous portal is out of funds), (b) set a direct `FAL_KEY` to unlock gpt-image-2, (c) refresh the portal (`hermes model`), or (d) hand the surgical edit to Forge (Photoshop/GIMP compositing) for a pixel-identical result. Revert `image_gen.model` to `fal-ai/flux-2/klein/9b` if you need image gen to keep working while gpt-image is unreachable.

**Set expectations honestly:** if the active model is Klein 9B, tell the user up front that the scene WILL shift on every pass and a pixel-identical result is not achievable with that model — then offer gpt-image-2 (via FAL key) or Forge compositing as the path that actually delivers "keep the original, swap the subject."

## Pitfall: AI sharpens faces into "Hollywood" (user-corrected Aug 4 2026)
Reference-based generation defaults to a **chiseled, angular jaw** even when the subject has a soft, round, full-cheeked face. Vanito corrected this on Lightning: "make sure the face looks the same" — the first sheet came out too sharp-jawed. Fix by doing BOTH:
- In the prompt, state the structure to MATCH: "ROUND, FULL-CHEEKED, soft jawline blending into a thick neck. DO NOT make him chiseled, angular, or sharp-jawed." Name the build (burly/heavy-set).
- Always run a vision pass comparing the sheet's face to the source photo and regenerate if the jaw got sharpened.

## Pitfall: garbled AI pseudo-text headers
Character sheets often render view labels ("FRONT/PROFILE/BACK") as garbled pseudo-text ("FRUCT", "FEONNE"). Add "ABSOLUTELY NO TEXT, NO LABELS, NO HEADERS, NO WATERMARKS ANYWHERE" to the prompt and verify with vision before showing.

## Error Diagnosis
- `file_download_error` → FAL could not reach the host. Check the URL returns 200 with `image/jpeg` content type from a public network; switch to the VPS nginx root.
- `image_load_error` → FAL downloaded something that isn't a decodable image (HTML page, corrupted file) OR the JPEG is progressive. Convert to baseline + verify content type.
- Always check `file <image>` locally — progressive vs baseline is visible there.

## Pitfalls
- Don't retry the same failing host more than once — diagnose with curl first.
- Port conflicts are common on the VPS — a port can be silently serving another app (8765 was taken by an existing python service). If `curl` returns 404 `application/json` (not `text/html`), something else owns that port: switch to a fresh high port immediately.
- Kill the http.server when done (`process action=kill`) — no need to leave one-off file hosts running.
- User-sent photos in Telegram arrive as JPEGs in `image_cache/`; verify they exist before generating.
- The generated image reinterprets faces — set expectations ("looks similar but not identical") and iterate with stronger prompt language.
- Verify with vision_analyze BEFORE showing the user — never deliver unverified generations.

## References
- `references/fal-reference-image-hosting.md` — full failure transcript and debugging path
- `references/blockrun-image-mcp.md` — exact node probe scripts to invoke `blockrun_image` (and other blockrun_* tools) directly via MCP when they aren't in the session toolset, plus model pricing and img2img notes
- `templates/blockrun-gpt-image2-edit.mjs` — ready-to-edit GPT Image 2 img2img script (direct `ImageClient`, works without the MCP tool)
- `scripts/blockrun-balance.mjs` — on-chain USDC balance check (getBalance is broken)
