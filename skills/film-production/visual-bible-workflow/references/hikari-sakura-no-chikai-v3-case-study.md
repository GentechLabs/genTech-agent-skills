# HIKARI Sakura no Chikai — v3 Case Study (Jul 30, 2026)

## Overview
Third version of the film. 33 clips, ~2:49 runtime. Full redo with bangs-over-eye method, then partial rollback to old clips after Vanito flagged consistency drift.

## What Went Wrong

### Mass-Regeneration Drift
The biggest mistake: regenerating ALL 33 keyframes instead of only the flagged ones. GPT Image 2 introduced drift across every batch:
- **Muffin changed** — tortoiseshell pattern shifted, sometimes looked like a different cat entirely
- **Room layout drifted** — posters, furniture, lighting changed between clips
- **Props hallucinated** — a pen appeared in HIKARI's hair in one shot
- **Flashback changed** — the Papa/young HIKARI dancing scene lost its original composition
- **Doorway silhouettes changed** — the walking-through-portal and dancing silhouettes lost their original beauty

### Vanito's Feedback (verbatim)
- "Muffin kept changing — different cats. He was supposed to stay consistent."
- "The flashback changed completely. I like the old way we had it."
- "The room looked like it changed."
- "She ended up having a pen thing in her hair."
- "Everything started randomizing."
- "We're supposed to be going based on the sheet that we have."

### The Fix
Swapped the old clips back in for the scenes Vanito loved:
- **T2 Doorway Walk** → `sakura-t2-walking.mp4` (original portal walk)
- **C2 Dancing Silhouettes** → `sakura-c2-v3.mp4` (original spinning dance)
- **Flashback** → `sakura-flashback-v3.mp4` (original field spinning)
- **Bridge Crying** → `sakura-bridge-tears-v2.mp4` (original tears scene)
- **Scene 2 Chorus** → `sakura-scene2-chorus.mp4` (original chorus)

**Cost: $0** — all old clips were still on the VPS.

## What Went Right

### Bangs-Over-Eye Method (LOCKED)
- 100% pass rate on all 3 face-visible tests
- Inside room wide shot — passed
- Crying scene (hair forward, tear visible) — passed
- Muffin Bats Petals (regenerated with bangs) — passed
- No fog, no grid, no Virtual Portrait needed

### Muffin as Cameo (LOCKED)
Vanito's words: "The cat could be a cameo, it walks away."
- Muffin walks in at the start
- Bats a petal during final chorus
- Sits in empty room at the end
- NOT in every shot — this prevents drift

### Old Clips Are Gold
Every old clip is still on the VPS. Never delete them. They're the fallback when new generations drift.

## Key Lessons for Future Films

1. **Never mass-regenerate.** Only regenerate flagged clips. Keep everything else.
2. **Old clips are the source of truth.** If Vanito approved a clip once, it stays unless he asks to change it.
3. **Muffin = cameo only.** Not a background character in every shot.
4. **Bangs-over-eye is the only face bypass.** No scenery blend, no grid, no Virtual Portrait.
5. **Swap, don't redo.** Edit the concat file to swap old clips back in. Zero cost, instant fix.
6. **Vanito notices everything.** If something drifts, he'll see it. Don't try to sneak changes past him.

## Final Film
- URL: `https://vanito.gentechlabs.net/videos/sakura-final-v3.mp4`
- 33 clips, 2:49 runtime, 960x960, 24fps
- Full audio synced
- Wallet: $7.46 remaining
