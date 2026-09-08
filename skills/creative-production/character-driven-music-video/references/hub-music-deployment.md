# Vanito Hub — Music Deployment Workflow

> Last updated: 2026-07-15

## Overview

Songs Vanito sends need to be published on his hub page (hub-vanito.html) in the **Music tab**, with the cover art embedded in the MP3, and the metadata registered in `vanito-music.json`.

There are TWO locations that need updating:
1. **The song/cover files** → pushed to `music/vanito/` on the ProtoJay4789.github.io repo
2. **The hub page** → `hub-vanito.html` needs a music card added in the `#music-list` section
3. **The music JSON** → `vanito-music.json` needs a new song entry

## Step-by-Step

### Step 1: Prepare the files
```bash
# Cover art is the final approved image
cp <cover_image> music/vanito/kimi-no-koe-cover.png

# Song MP3 with cover art embedded (ffmpeg in-place is not allowed, use temp file)
ffmpeg -i <original_song.mp3> -i music/vanito/kimi-no-koe-cover.png \
  -map 0:a -map 1:v \
  -metadata title="I Heard Your Voice" \
  -metadata artist="KAGEKŌ" \
  -metadata album="Kimi no Koe" \
  -metadata track="1" \
  -c:a copy -c:v mjpeg -disposition:v attached_pic \
  -y /tmp/output.mp3
mv /tmp/output.mp3 music/vanito/Kimi_no_Koe_I_Heard_Your_Voice.mp3
```

### Step 2: Clone the hub repo (avoid vault nesting issues)
The hub repo is inside the vault at `/root/vaults/gentech/github/ProtoJay4789.github.io/` and the vault's working tree changes block clean git operations. **Always use a fresh clone for pushing.**

```bash
rm -rf /tmp/hub-push
git clone https://github.com/ProtoJay4789/ProtoJay4789.github.io.git /tmp/hub-push --depth 1
```

### Step 3: Copy files into the clone
```bash
cp <prepared_mp3> /tmp/hub-push/music/vanito/
cp <cover_image> /tmp/hub-push/music/vanito/kimi-no-koe-cover.png
```

### Step 4: Update hub-vanito.html
Edit `/tmp/hub-push/hub-vanito.html`. Find the `#music-list` div and add a music card:

```html
<!-- Song Title -->
<div class="card music-card" style="margin-bottom:12px;">
  <img src="music/vanito/kimi-no-koe-cover.png" style="width:56px; height:56px; object-fit:cover; border-radius:8px; border:2px solid #6a2a6a; flex-shrink:0;">
  <div class="music-info">
    <div class="music-title">I Heard Your Voice / Kimi no Koe</div>
    <div class="music-meta">4:47 · Dark J-Rock · 2026</div>
  </div>
  <audio controls preload="none" style="height:32px; width:140px; border-radius:4px;">
    <source src="music/vanito/Kimi_no_Koe_I_Heard_Your_Voice.mp3" type="audio/mpeg">
  </audio>
</div>
```

### Step 5: Update vanito-music.json
Add a new entry to the `songs` array at the TOP (most recent first):

```json
{
  "id": "kimi-no-koe",
  "title": "I Heard Your Voice / Kimi no Koe",
  "duration": "4:47",
  "genre": "Dark J-Rock",
  "mood": "Emotional, Melancholic, Hopeful",
  "dateCreated": "2026-07-15",
  "audioUrl": "https://raw.githubusercontent.com/ProtoJay4789/ProtoJay4789.github.io/main/music/vanito/Kimi_no_Koe_I_Heard_Your_Voice.mp3",
  "coverUrl": "music/vanito/kimi-no-koe-cover.png"
}
```

Also update the metadata at the top:
```json
"music": {
  "totalSongs": <increment>,
  "totalDuration": "<total>",
  "lastUpdated": "<YYYY-MM-DD>"
}
```

### Step 6: Commit and push
```bash
cd /tmp/hub-push
git add -f music/vanito/<files> vanito-music.json hub-vanito.html
git commit -m "🎵 Song title — description"
git push origin main
```

### Step 7: Verify
```bash
curl -s -o /dev/null -w "Song: %{http_code}\nCover: %{http_code}\n" \
  "https://raw.githubusercontent.com/ProtoJay4789/ProtoJay4789.github.io/main/music/vanito/<song_file.mp3>" \
  "https://raw.githubusercontent.com/ProtoJay4789/ProtoJay4789.github.io/main/music/vanito/<cover_file.png>"
# Both should return 200
```

## Cover Art Notes

- **Always use the original approved image** as the cover. Do NOT apply additional fixes/edits after Vanito approves it — each edit drifts character appearances.
- The cover image must be pushed to the same `music/vanito/` directory alongside the song.
- The hub-vanito.html music card references the cover via relative path: `music/vanito/<filename>`.

## Known Pitfalls

- **Repo inside vault causes git conflicts**: The local clone at `/root/vaults/gentech/github/ProtoJay4789.github.io/` always shows vault changes as modifications. **Do not attempt to push from this path.** Always use the fresh clone workflow above.
- **ffmpeg cannot edit MP3 in-place**: Write to a temp file first, then mv over the original.
- **Metadata matters**: Vanito's songs should be tagged with artist="KAGEKŌ" unless specified otherwise.
- **Verify, verify, verify**: Always curl the raw.githubusercontent.com URLs after pushing to confirm the files are live.
- **Characters tab edit requires HTML insertion at exact lines**: The discography and featured release sections are manually positioned. Use Python read/write or execute_code with careful line-number targeting rather than `patch` when the file has many similar patterns.
- **Python line-number insertion for hub HTML**: When `patch` fails due to duplicate strings (multiple identical `Coming soon` divs, repeated card patterns), use execute_code to read lines, search for a nearby unique marker, calculate the exact insertion index, insert new lines, and write back. This is safer than `patch` for hub-vanito.html because the file has many structurally identical elements. Always work from the fresh clone in /tmp/hub-push, NOT the vault-nested repo.

## Step 8: Update the Characters/Artist Tab

Vanito's hub has a **Characters tab** (`#tab-characters`) which serves as the artist tab. A new song release needs updates in THREE places there:

### A. Discography section
Add the song to the KAGE side (red accent `#cc2222`) AND the HIKARI side (slightly different red `#cc3333`). Each side has a track list with styled divs. Insert after the last listed track. Example entry:

```html
<div style="background:rgba(200,30,30,0.05); border-radius:6px; padding:6px 8px; border:1px solid rgba(200,30,30,0.08);">
  <div style="font-size:0.7rem; font-weight:600; color:#cc4444;">I HEARD YOUR VOICE</div>
  <div style="font-size:0.65rem; color:#664444; font-style:italic; margin-top:2px;">With HIKARI</div>
</div>
```

Increment the track counter when adding:
```html
<span style="font-size:0.6rem; color:#553333;">4 tracks · Post-Hardcore</span>
```

### B. Duets section
Find the DUETS div at the bottom of the discography card. Add a new badge:

```html
<span class="...">I HEARD YOUR VOICE</span>
```

### C. Featured Release + Story
Create a new featured release card after KIMI GA HIROTTA section. Use purple accents to distinguish it. Include story text, audio player, cover art, and links to lyrics/artwork.

### D. Story-writing pattern
1. KAGE's isolation before the connection
2. Hearing HIKARI's voice across the darkness
3. Finding her lyrics on crumpled paper
4. Writing a melody back
5. Shadow met light
6. Uplifting resolution

### E. Lyrics file
Create a `.txt` file in `music/vanito/` with full lyrics. Push alongside all other files.
