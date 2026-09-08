# Sakura no Chikai — Production Notes (2026-07-27)

## Storyboard Structure
- **35 frames total** — 19 keyframes + 7 transitions + 2 production cards + 4 before/after + 3 character sheets
- **3-frame per scene pattern:** Before → Main → After
- **7 transition flow frames** between every scene section
- **Opening:** "GEN TECH LABS presents"
- **Closing:** "A film by Vanito" + "© 2026 GenTech Labs"

## Young HIKARI Consistency Rules (LOCKED after user corrections)
- Solid BLACK hair in TWO PIGTAILS — NO red tips ever
- White t-shirt with black kanji 光
- Memory silhouettes must stay FULLY INSIDE the door frame — no bleeding into dark room

## Cloudflare Cache-Busting Fix
- `?v=2` on URLs does NOT work — Cloudflare caches the 404 for the old filename
- **Fix:** Save new file with a COMPLETELY NEW filename (e.g. `s3-bridge-v2.png`)
- Then update the HTML to point to the new filename

## VPS Permissions
- `write_file` and `scp` as root default to `600` permissions
- Nginx needs `644` — always run `chmod 644` after every upload
- Storyboard-hikari.html was 600 on first write — caused 404

## Seedance 2.0 Pricing (Actual, 2026-07-27)
- 8s image-to-video: **$2.55** (actual charge)
- Previous estimate was ~$2.55-3.19 — actual was at the low end

## Wallet
- Started session at ~$8.02
- After ~35 image generations + 1 Seedance clip: **$3.43 remaining**
- Total burned: ~$4.60

## Storyboard Page
- Live at: https://vanito.gentechlabs.net/storyboard-hikari.html
- Separate from KAGE — HIKARI only
- All images cache-busted to `?v=5`
