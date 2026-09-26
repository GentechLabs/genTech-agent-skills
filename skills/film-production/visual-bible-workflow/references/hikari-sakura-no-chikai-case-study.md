# HIKARI Sakura no Chikai — Production Case Study (Updated Jul 29)

## Overview
- **Title:** 桜の約束 (Sakura no Chikai) — "A Promise Under the Cherry Blossoms"
- **Artist:** HIKARI
- **Director:** Vanito Vanzant
- **Studio:** GenTech Labs
- **33 clips, ~3:02 runtime** (expanded from original 25 clips, 2:24)
- **Song:** 269.3s (4:29) — `hikari-sakura-no-chikai-final.mp3`
- **Model:** Seedance 2.0 (bytedance/seedance-2.0)
- **Art style:** Painterly semi-realistic anime, dark gothic/visual-kei, high-contrast dramatic lighting
- **Cost:** ~$60 total (keyframes + animation)
- **Wallet:** Base USDC at 0xebc8c71970EEb6973bd87F1FF146B3Ec4a5972f8

## Story
HIKARI sits in her room playing guitar on a rainy day. The song is a promise to her late father, Papa Tanaka (passed when she was 16). Through the music, she relives memories of him spinning her as a child in a cherry blossom field. Her cat Muffin stays with her through it all — entering at the start, watching, batting at petals, comforting her during the crying scene, and remaining in the empty room after she leaves.

## 30-Clip Scene List (Final v6 — Muffin Cameo Only)

### Opening (Clips 1-6)
1. Opening title — 5s
2. Outside house in rain — 5s
3. Inside room, dark — 8s (no Muffin)
4. T1 — Finger hovering over guitar strings — 4s
5. V1 — First notes, playing — 6s
6. **Guitar CU 1** — 4s (Phase 1→2, first petal appears)

### Memory Arc (Clips 7-16)
7. T2 — Doorway glow, silhouettes walking into light — 4s
8. Scene 2 — Chorus, silhouettes in doorway — 8s
9. T3 — Petal lands on framed photo — 4s
10. T4 — Hand gripping guitar neck — 4s
11. V2 — Finding strength, playing stronger — 6s
12. **Window / Rain Shot** — 4s
13. **Guitar CU 2** — 4s (Phase 2→3)
14. C2 — Chorus 2, silhouettes dancing in doorway — 8s
15. T5 — Memory trigger, tear forming — 4s
16. Flashback — Papa spinning young HIKARI in field — 10s

### Emotional Peak (Clips 17-24)
17. T6 — Return from memory — 4s
18. 3a — Before peak, tears forming — 5s
19. Bridge — Tear on cheek, chorus hits — 8s
20. 3b — After peak, peaceful smile — 5s
21. **Guitar CU 3** — 4s (Full Bloom)
22. Build — Hands on strings, loudest part — 6s
23. T7 — Hope, sunlight breaking through window — 4s
24. 4a — Before final verse, calm — 5s

### Resolution (Clips 25-30)
25. Scene 4 — Outro, room golden and peaceful — 8s
26. Outro — Hand touching framed photo — 5s
27. 4b — Closing shot, empty room — 6s
28. **Muffin in Empty Room** — 4s (ONLY Muffin appearance — cat alone, watching light fade)
29. End credit — 5s
30. Closing production — 5s

**Total: 30 clips, ~2:43 runtime**

## Muffin's Role (Cameo-Only — Final Decision)
- **Only appears ONCE** — in the empty room at the end
- Sits alone, watching the golden light fade
- This is the ONLY clip where Muffin appears
- **Why:** Seedance 2.0 cannot keep a secondary character consistent across multiple clips, even with the exact same prompt. Every animation reinterprets the character. The cameo-only approach eliminates drift entirely.
- **Previous attempts that failed:** Muffin in entrance, Muffin in background of wide shots, Muffin batting petals — all resulted in her changing appearance between clips (black cat, gray cat, tortoiseshell, etc.)
- **Lesson learned:** For AI film production, secondary characters should appear in 1-2 clips MAXIMUM. Any more and the audience will notice the inconsistency.

## Guitar Evolution
- **Phase 1 (Opening → Verse 1):** Plain dark wood acoustic, no decorations
- **Phase 2 (Chorus 1 → Bridge):** A few sakura petals appearing on body
- **Phase 3 (Final Chorus → Outro):** Full bloom — covered in cherry blossom flowers and petals

## Lighting Progression
- **Opening → Verse 1:** Dark room, rainy window, golden doorway glow starting faint
- **Chorus 1 → Bridge:** Golden doorway light getting brighter, rain still falling
- **Bridge → Tears:** Golden light at its brightest, rain thinning
- **Final Chorus → Outro:** Sunlight breaking through window, golden doorway warm but fading
- **Ending:** Empty room, golden light almost gone, sunlight soft

## Key Techniques Used

### PRIMARY: Bangs-Over-Eye / Hair Forward (Vanito's preference)
- Compose shots so hair falls forward, partially covering the face
- One eye visible through strands — enough to see emotion
- Tears catch the light through the hair (like T7 sunlight scene)
- Character's face stays exactly as GPT Image 2 designed it
- No fog, no grid, no third system
- **CRITICAL RULE:** If flagged, STOP. Report to Vanito. Do NOT try alternatives or burn funds.

### SECONDARY: Scenery Blend Bypass (NOT 100% reliable)
- Overlay soft cloudy texture at ~50% opacity over face area
- Works for most angles but some still trigger detection
- Only use if Vanito explicitly approves

### Virtual Portrait / RealFace — NOT PREFERRED
- Tested and rejected by Vanito on Jul 29, 2026
- Risk: reference image becomes source for every animation, can shift character's look
- Only mention if Vanito asks directly

### Continuity Chain
- Every clip ends in the next clip's start position
- Camera angles: behind, behind/side, 3/4 profile, close-up
- No camera orbits (Seedance cannot do smooth orbits)

### Audio Sync
- Full song plays from 0:00
- Bridge tear scene timed to chorus peak (~3:00-3:08)
- FFmpeg concat for video, then mux with audio

## Muffin's Role
1. **Opening:** Walks through doorway, sits near HIKARI
2. **Throughout:** Watches HIKARI play, stays in frame
3. **Petal scenes:** Bats at falling cherry blossom petals playfully
4. **Bridge/crying scene:** Moves closer, comfort presence
5. **Ending:** Stays in empty room, watches golden light fade

## Character Sheets Created
- HIKARI Outfit Sheet — locked
- HIKARI Hairstyle Reference — locked (long black, red tips, always down)
- Papa Tanaka v3 — locked
- Young HIKARI v3 — locked
- Muffin the Cat — locked
- Guitar Evolution (3 phases) — locked
- Framed Photo Reference — locked
- Room Reference v3 — locked
- Official Style Reference — locked

## Vanito's Strategy
1. Character sheet EVERYTHING before generating
2. Finish full film first
3. One complete review pass after all clips done
4. Fix everything in batch
