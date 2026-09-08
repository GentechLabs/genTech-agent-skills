# Sakura no Chikai — Production Notes (Jul 30-31, 2026)

Final film: `sakura-final-v14.mp4` live at https://vanito.gentechlabs.net/videos/sakura-final-v14.mp4
- Full song 269.3s applied, 135 keyframes, CRF 23, `-g 48 -keyint_min 48 -sc_threshold 0`
- Song outro: final frame held via `tpad=stop_mode=clone:stop_duration=X` so the complete track plays with no freeze
- Storyboard: https://vanito.gentechlabs.net/storyboard-hikari.html (32 scenes)

## FINAL 32-CLIP INVENTORY (order matters)
opening-title-v2 → outside-v2 → strum-v3-2s (Muffin LEFT) → hover-v2 → tilt-up-muffin-3s (TRIMMED from 8s) →
guitar-cu1 → guitar-cu2 → guitar-cu3 → evolved-guitar (桜誓い/SAKURA NO CHIKAI text + Muffin tail) →
strum-v5-2s (Muffin RIGHT) → muffin-petting → clip6-doorway → **t2-walking (ORIGINAL v1)** →
scene2-v4 → t3-v3 → t4-v3 → v2-v3 → c2-v4 → t5-v7 → **flashback-v3 (ORIGINAL v1)** →
t6-v3 → 3a-v4 → bridge-bangs → 3b-v4 → build-v3 → t7-v3 → 4a-v5 → scene4-v4 → outro-v4 →
ending-v3 (walk out with evolved guitar, Muffin follows, door shuts) → credit-v3 → closing-v3

## KEY DECISIONS THIS SESSION
1. Opening title: ORIGINAL `sakura-opening-title-v2.mp4` (桜の約束 + Muffin) — NOT the "GEN TECH LABS presents" card
2. V1 "singing at window" scene REMOVED; replaced with guitar close-ups (cu1/cu2/cu3 + evolved guitar)
3. Tilt-up scene trimmed 8s → 3s (cat staring up at her) — user: "make it move quickly to the next scene"
4. Silhouettes: ORIGINAL `sakura-t2-walking.mp4` (ramen shop, Papa 麺田中 apron + pigtail HIKARI)
5. Papa dancing: ORIGINAL `sakura-flashback-v3.mp4` (OLDER Papa, salt-and-pepper, stubble)
6. Evolved guitar scene NEW — 桜誓い text + SAKURA NO CHIKAI + Muffin tail in foreground
7. Ending: HIKARI walks out with fully evolved guitar, Muffin follows, door shuts

## OPERATIONAL PITFALLS
See SKILL.md "Operational Pitfalls (added Jul 31, 2026)" — full details there. Summary:
- BlockRun wallet swap between /root/.blockrun/ and profile .blockrun/ — copy funded .session key
- Active chain can flip to SOLANA → Base-only calls report "out of funds" even with balance
- Seedance 2.0 min duration = 4s → generate 4s, trim with `-c copy` for 2-3s scenes
- Scenery blend PIL recipe (50% cloudy overlay) passes when bangs-over-eye keyframe flags
- Vanito prefers ORIGINAL v1 silhouettes/dancing over regenerated versions — hunt earliest variant
- Rebuild discipline: find exact base file, verify clip membership via frame-0 md5, don't guess concat

## VERIFICATION TECHNIQUE (which clips are inside a merged video)
```bash
# frame 0 of a clip:
ffmpeg -y -ss 0 -i clip.mp4 -frames:v 1 /tmp/f0.png && md5sum /tmp/f0.png
# compare against merge's frame at the matching timestamp
ffmpeg -y -ss T -i merged.mp4 -frames:v 1 /tmp/merge_T.png && md5sum /tmp/merge_T.png
```
Matching md5 = that clip is in the merge at that position. Also use `ffprobe -select_streams v:0
-show_entries frame=pict_type` to check keyframe spacing (I-frames every 2s = healthy).

## COST NOTES
- GPT Image 2 keyframe: $0.065
- Seedance 2.0 4s: ~$1.28; 6s: ~$1.91
- This session total: ~$8-9; wallet ended at $11.85 on Base
