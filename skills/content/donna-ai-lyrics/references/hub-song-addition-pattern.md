# Hub Song Addition Pattern (Vanito's Hub)

When adding a new song to Vanito's hub (hub-vanito.html), use this pattern.

## File Structure

All files go under `music/vanito/` on the gentechlabs.github.io repo:

```
music/vanito/
  shadow-and-light.mp3          # The audio file
  kimi-ga-hirotta-cover.jpg     # Album art
  kimi-scream-animated.gif      # Animated GIF (from Seedance)
  kimi-ga-hirotta.txt           # Donna-formatted lyrics
```

## Two Places to Update

### 1. Data JSON (`hub-vanito-data.json`)

Add a new song object to the `music.songs` array. This feeds the dynamic music tab:

```json
{
  "title": "Shadow and Light (Kimi ga Hirotta)",
  "style": "Dark J-Rock — KAGE's Story, English/Japanese, Screaming/Emotional",
  "added": "2026-07-14"
}
```

Update `lastUpdated` to the current date.

### 2. HTML Card (`hub-vanito.html`)

Add a featured release card with album art, GIF, audio player, and links. Place this after the discography/duets section:

```html
<!-- ═══ FEATURED RELEASE ═══ -->
<div class="card card-together" style="padding:20px; margin-bottom:16px; border:2px solid #cc2222; box-shadow: 0 0 25px rgba(200,30,30,0.15);">
  <div style="display:flex; gap:16px; flex-wrap:wrap;">
    <div style="flex:1; min-width:200px;">
      <div style="font-size:1.1rem; font-weight:700; color:#cc3333; letter-spacing:1px; margin-bottom:4px;">🎵 KIMI GA HIROTTA</div>
      <div style="font-size:0.85rem; color:#ff6644; font-style:italic; margin-bottom:8px;">Shadow and Light — Official Release</div>
      <div style="font-size:0.78rem; color:#999; line-height:1.6; margin-bottom:12px;">
        Description of the song and its story context.
        <br><br>
        <span style="color:#cc4444;">Genre tags · Style tags</span>
      </div>
      <audio id="kimi-player" controls preload="none" style="width:100%; height:36px; border-radius:4px;">
        <source src="music/vanito/shadow-and-light.mp3" type="audio/mpeg">
      </audio>
      <div style="margin-top:8px; display:flex; gap:6px; flex-wrap:wrap;">
        <a href="music/vanito/kimi-ga-hirotta.txt" target="_blank" style="font-size:0.75rem; color:#cc4444; text-decoration:none; padding:4px 10px; background:rgba(200,50,50,0.1); border-radius:4px;">📝 Lyrics</a>
        <a href="music/vanito/kimi-ga-hirotta-cover.jpg" target="_blank" style="font-size:0.75rem; color:#cc4444; text-decoration:none; padding:4px 10px; background:rgba(200,50,50,0.1); border-radius:4px;">🖼️ Artwork</a>
      </div>
    </div>
    <div style="flex:0 0 auto; width:220px; max-width:100%;">
      <img src="music/vanito/kimi-ga-hirotta-cover.jpg" style="width:100%; border-radius:8px; border:2px solid #cc2222; box-shadow: 0 0 20px rgba(200,30,30,0.2);">
      <div style="margin-top:8px;">
        <img src="music/vanito/kimi-scream-animated.gif" style="width:100%; border-radius:8px; border:1px solid #3d1a1a;">
      </div>
    </div>
  </div>
</div>
```

Also add a tag in the DUETS section if it's a KAGE × HIKARI collab:

```html
<span style="font-size:0.7rem; padding:4px 10px; background:rgba(200,50,50,0.1); border-radius:4px; color:#cc4444;">SHADOW AND LIGHT</span>
```

## Verification

After pushing, check:
- Audio player loads (right-click → open in new tab, verify raw URL returns 200)
- Album art displays
- Animated GIF plays
- Lyrics link resolves
- Password gate access works (PW: Vanzantk1!)
