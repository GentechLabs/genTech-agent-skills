---
name: gentech-family-hub-management
title: GenTech Family Hub Management — Multi-Person Data Isolation and Coordination
description: Managing multiple family members' hubs, dashboards, and intelligence systems with strict data isolation, cronjob coordination, and navigation patterns. Covers Jordan, Vanito, and other family members with separate Steam IDs, wishlists, game intelligence, and sync workflows.
tags: [gentech, family-hubs, data-isolation, cronjob-coordination, multi-person-systems]
version: 1.0
created: 2026-07-05
---

# GenTech Family Hub Management

Managing multiple family members' hubs, dashboards, and intelligence systems with strict data isolation and automatic synchronization.

## Core Principle

**Rule:** Each family member is a separate entity with isolated data, dashboards, and intelligence. Never mix data between family members in jobs, dashboards, or reports.

## Family Member Registry

### Jordan (ProtoJay4789)
- **Steam ID:** `76561197996487689`
- **Hub URL:** `https://gentechlabs.net/jordan.html`
- **Profile:** `https://gentechlabs.net/portfolio/`
- **Cronjobs:**
  - `[Jordan] GenTech Shop — Game Release Intelligence` (41f8e6d0e24b) — 2:00 PM
  - `[Jordan] GenTech Shop — Weekly Sales Sweep` (80fd54684d86) — Wed 12:00 PM
- **Group:** HQ, Treasury, Labs, Entertainment

### Vanito
- **Steam ID:** `76561198132811363`
- **Hub URL:** `https://gentechlabs.net/vanito.html`
- **Music Vault:** `https://gentechlabs.net/vanito.html#tab-music`
- **Cronjobs:**
  - `[Vanito] GenTech Shop — Game Release Intelligence` (e28c895e6a11) — 3:00 PM
  - `[Vanito] GenTech Shop — Weekly Sales Sweep` (1c25463fc281) — Wed 12:00 PM
  - `vanito-music-sync` (f3e90d867b9c) — Every 6 hours
- **Group:** Entertainment

## Hub Architecture Pattern

### VPS Deployment (Current) — Not GitHub Pages

**Change as of Jul 2026:** Personal hubs are served from the VPS (`/var/www/gentechlabs/`) as flat HTML files behind nginx. The old GitHub Pages approach is legacy.

**Hub URLs — `<name>` matches the flat HTML file:**
- Jordan: `https://gentechlabs.net/jordan.html`
- Vanito: `https://gentechlabs.net/vanito.html`
- Main landing: `https://gentechlabs.net/` (serves hub.html)

### Hub Tab Design — Lifestyle over Business

**Rule (user preference):** Personal hubs use **lifestyle/topic tabs**, not business/metric tabs. Vanito set the pattern first (Characters, Music, Deals). Jordan confirmed when he rejected Overview/Build/Portfolio/Links in favor of Travel, POE2, Gaming, Shop tabs.

**Correct tab categories per person:**

| Person | Tabs | Vibe |
|--------|------|------|
| **Jordan** | ✈️ Travel, ⚔️ POE2, 🎮 Gaming, 🛒 GenTech Shop | Lifestyle + gaming |
| **Vanito** | 🎭 Characters, 🎵 Music, 🕹️ Deals, 🛒 Shop | Creative + deals |

**Do NOT use:** Overview, Build, Portfolio, Links, Metrics, Dashboard — those belong on landing pages, not personal hubs.

### Deploying a Hub

```bash
# Build in the GitHub Pages repo (source of truth)
nano ~/repos/ProtoJay4789.github.io/jordan.html

# Deploy to VPS
sudo cp ~/repos/ProtoJay4789.github.io/jordan.html /var/www/gentechlabs/jordan.html
sudo chown www-data:www-data /var/www/gentechlabs/jordan.html

# Verify
curl -s https://gentechlabs.net/jordan.html | grep "<title>"
```
├── Games/
│   ├── Vanito-Travel/             # Vanito's Meta Ray-Ban app
│   ├── GenTech-Atlas/             # Jordan's commercial product
│   ├── Meta-Rayban-Fighter/       # Vanito's game
│   └── index.html                 # Projects index
├── Gaming/                        # Gaming dashboards
│   ├── index.html                 # Gaming Hub
│   ├── vanito-music-dashboard.html # Vanito's music dashboard
│   ├── vanito-music.json          # Synced music data
│   ├── wishlist-vanito.html       # Vanito's wishlist tracker
│   └── poe2-vanito.json           # Vanito's POE2 builds
├── music/
│   └── vanito/                    # Vanito's audio files
│       ├── index.html             # Music Vault with inline player
│       └── *.mp3                  # Track files
├── DeFi/
│   └── defi-dashboard.html        # DeFi dashboard (Jordan)
└── index.html                     # Portfolio (Jordan's professional face)
```

**Key rules:**
- Root `/index.html` = Jordan's professional portfolio. Not a hub. Stays static.
- `/Jordan/` = Jordan's personal hub with product links and dashboards.
- `/Vanito/` = Vanito's personal hub with his projects, music, gaming.
- **No generic `/Hub/`** — only personal hubs. If one exists, redirect to Jordan.
- Every glass-accessible page needs DPAD focus management (see below).

### Dashboard Navigation Pattern

**Rule:** Every specialized dashboard MUST have a back link to the person's main hub.

**Implementation:**
```html
<!-- In header section -->
<a href="/hub-vanito.html" class="back-link">← Back to Main Hub</a>

<!-- CSS for styling -->
.back-link {
  position: absolute;
  top: 20px;
  left: 20px;
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  font-size: 0.9em;
  display: flex;
  align-items: center;
  gap: 5px;
  transition: color 0.2s;
}
.back-link:hover {
  color: white;
}
```

**Navigation Flow:**
1. Main Hub (`hub-vanito.html`) → Music Dashboard (`Gaming/vanito-music-dashboard.html`)
2. Music Dashboard → Main Hub (back link)
3. Both display data from the same source (`hub-vanito-data.json`)

### DPAD Focus Management for Glass-Accessible Hub Pages

**Rule:** Any hub page served to Meta Ray-Ban glasses needs explicit DPAD (arrow key) focus management. The glasses webview only navigates via arrow keys + Enter — mouse clicks and standard tab order are not reliable.

**Pattern — Linear grid (hub launchpads):**
```javascript
let currentIdx = 0;
function getFocusables() {
  return [...document.querySelectorAll('.focusable')].filter(el => el.offsetParent !== null);
}
function setFocus(idx) {
  const items = getFocusables();
  if (idx < 0) idx = items.length - 1;
  if (idx >= items.length) idx = 0;
  currentIdx = idx;
  items.forEach((el, i) => el.classList.toggle('focused', i === idx));
  if (items[idx]) items[idx].focus({ preventScroll: true });
}
document.addEventListener('keydown', (e) => {
  const dir = { ArrowUp:'up', ArrowDown:'down', ArrowLeft:'left', ArrowRight:'right' }[e.key];
  if (dir === 'down' || dir === 'right') { e.preventDefault(); setFocus(currentIdx + 1); }
  else if (dir === 'up' || dir === 'left') { e.preventDefault(); setFocus(currentIdx - 1); }
  else if (e.key === 'Enter') {
    const items = getFocusables();
    if (items[currentIdx]) items[currentIdx].click();
  }
}, true);
window.addEventListener('load', () => setFocus(0));
```

**Key rules:**
- Use `capture` phase (`, true` as third arg to addEventListener) to intercept before the webview's default handler
- Add `.focusable` CSS class with `:focus` and `.focused` pseudo-selectors — use a bright accent color (`#00d4ff` or `#3b82f6`) for the outline ring
- Every navigable element gets `class="focusable"` — nav links, cards, buttons
- `element.focus({ preventScroll: true })` prevents the glasses from scrolling unexpectedly
- Native `<a href>` tags handle the Enter/click via JS calling `items[currentIdx].click()`
- Also add a click event listener for desktop/phone testing (the glasses ignore it, desktop needs it)

### Link Format for Telegram Sharing

**Rule:** When sharing hub links in Telegram, use plain text, clickable, own line, label then URL.

**Format:**
```
Label
https://the-url.com
```

**Example:**
```
Jordan's Hub
https://gentechlabs.net/jordan.html
```

**Explicitly do NOT use:**
- Markdown or HTML formatting around links
- Inline links like `[text](url)`
- Bullet points with links embedded
- Multiple links on one line
- Code blocks around URLs

## Data Loading Pattern

### Static HTML + Dynamic JSON

**Rule:** Hub HTML files are static templates. Data loads dynamically from JSON via JavaScript.

**Pattern:**
```html
<!-- In HTML body -->
<div id="music-list">
  <!-- Songs will be loaded here dynamically -->
</div>

<!-- JavaScript -->
<script>
  async function loadMusic() {
    try {
      const response = await fetch('hub-vanito-data.json');
      const data = await response.json();

      const musicList = document.getElementById('music-list');
      if (!data.music || !data.music.songs || data.music.songs.length === 0) {
        musicList.innerHTML = '<div class="placeholder">No songs yet!</div>';
        return;
      }

      const songsHtml = data.music.songs.map((song, index) => `
        <div class="song-card">
          <div class="song-icon">${index + 1}</div>
          <div class="song-info">
            <div class="song-title">${song.title}</div>
            <div class="song-style">${song.style}</div>
          </div>
        </div>
      `).join('');

      musicList.innerHTML = songsHtml;
    } catch (error) {
      console.error('Error loading music:', error);
    }
  }

  document.addEventListener('DOMContentLoaded', loadMusic);
</script>
```

**Pitfall:** Hardcoded placeholder data in HTML that never updates.
**Fix:** Use JavaScript to fetch from JSON and render dynamically.

## Cronjob Data Isolation

### Person-Level Cronjob Pattern

**Rule:** Every cronjob that deals with personal data MUST have explicit person identification in the prompt.

**Pattern:**
```python
# ✅ CORRECT - Explicit person identification
prompt = """
You are Gentech delivering Jordan's Game Release Intelligence.

Steam ID: 76561197996487689
Fetch wishlist from: https://steamcommunity.com/profiles/76561197996487689/wishlist
"""

# ❌ WRONG - No person identification
prompt = """
You are Gentech delivering Game Release Intelligence.
Fetch the Steam wishlist.
"""
```

### Cronjob Naming Convention

**Pattern:** `[Person] GenTech Shop — Function Name`

**Examples:**
- `[Jordan] GenTech Shop — Game Release Intelligence`
- `[Vanito] GenTech Shop — Game Release Intelligence`
- `[Jordan] GenTech Shop — Weekly Sales Sweep`
- `[Vanito] GenTech Shop — Weekly Sales Sweep`

### Cronjob Schedule Coordination

**Rule:** Multiple cronjobs serving different people should be staggered to avoid API rate limits and message congestion.

**Staggering Pattern:**
| Time | Person | Job |
|------|--------|-----|
| 2:00 PM | Jordan | Game Release Intelligence |
| 2:30 PM | Jordan | Voice Patch Notes |
| 3:00 PM | Vanito | Game Release Intelligence |
| 3:30 PM | Vanito | Voice Patch Notes |

**Benefits:**
- No API rate limit clashes
- Messages spaced out for readability
- Clear separation between family member intelligence

**Cronjob Update Pattern:**
```bash
# Update Vanito's game intel to 3:00 PM (from 2:00 PM)
cronjob action=update job_id=e28c895e6a11 schedule="0 15 * * *"

# Update Vanito's voice notes to 3:30 PM (from 2:00 PM)
cronjob action=update job_id=a564b3353770 schedule="30 15 * * *"
```

## Sync Workflows

### Music Sync Pattern

**Architecture:**
1. User edits JSON data file locally
2. Sync script runs every 6 hours
3. Script commits changes to git
4. GitHub Pages deploys automatically
5. All dashboards show updated data

**Implementation:**
```python
# Sync script: /root/my-music/vanito-music-sync.py
HUB_DATA_FILE = "/root/ProtoJay4789.github.io/hub-vanito-data.json"
GITHUB_MUSIC_JSON = "/root/ProtoJay4789.github.io/Gaming/vanito-music.json"

# Read from local hub JSON
with open(HUB_DATA_FILE, 'r') as f:
    hub_data = json.load(f)

# Update GitHub music JSON
github_data = {
    "player": "Vanito",
    "music": {
        "totalSongs": len(hub_data['music']['songs']),
        "lastUpdated": datetime.now().strftime('%Y-%m-%d')
    },
    "songs": hub_data['music']['songs']
}

# Write and commit
with open(GITHUB_MUSIC_JSON, 'w') as f:
    json.dump(github_data, f, indent=2)

subprocess.run(['git', 'add', 'Gaming/vanito-music.json', 'hub-vanito-data.json'], cwd='/root/ProtoJay4789.github.io')
subprocess.run(['git', 'commit', '-m', f"music(vanito): sync from hub - {len(github_data['songs'])} songs"], cwd='/root/ProtoJay4789.github.io')
subprocess.run(['git', 'push'], cwd='/root/ProtoJay4789.github.io')
```

**Cronjob:**
```python
cronjob action=create \
  name="vanito-music-sync" \
  schedule="every 360m" \
  prompt="Run Vanito music sync script to fetch songs from GenTech Hub and sync to GitHub.\n\nScript location: /root/my-music/vanito-music-sync.py" \
  no_agent=True \
  script="vanito-music-sync.py"
```

### GitHub Pages Deployment

**Pattern:**
1. Commit changes to GitHub
2. GitHub Pages automatically builds (30s delay)
3. Verify deployment
4. Share URL

**Verification Pattern:**
```bash
# Commit and push
cd /root/ProtoJay4789.github.io
git add Gaming/vanito-music-dashboard.html hub-vanito.html hub-vanito-data.json
git commit -m "feat: add music sync for Vanito's hub"
git push

# Wait for deployment
sleep 30

# Verify
curl -s "https://protojay4789.github.io/Gaming/vanito-music-dashboard.html" | grep "Vanito"
```

## Common Pitfalls

### Pitfall 1: Wrong Steam ID in Game Intelligence

**Problem:** User gets news for wrong family member's wishlist.

**Example:** Jordan received Vanito's game intelligence because cronjob used Vanito's Steam ID.

**Fix:** Explicit Steam ID in cronjob prompt:
```python
prompt = """
You are Gentech delivering Jordan's GenTech Game News — personalized game release intelligence for JORDAN (ProtoJay4789), not Vanito.

⚠️ IMPORTANT: This is for JORDAN's wishlist (Steam ID: 76561197996487689), NOT Vanito's (76561198132811363).

Fetch Jordan's Steam wishlist: https://steamcommunity.com/profiles/76561197996487689/wishlist
"""
```

### Pitfall 2: Cronjob Schedule Overlap

**Problem:** Multiple cronjobs hit APIs at same time, causing rate limits.

**Example:** 4 game intelligence jobs all at 2 PM daily.

**Fix:** Stagger jobs by 30 minutes:
```bash
# Jordan game intel: 2:00 PM (unchanged)
# Jordan voice notes: 2:30 PM
cronjob action=update job_id=90e51510349c schedule="30 14 * * *"

# Vanito game intel: 3:00 PM
cronjob action=update job_id=e28c895e6a11 schedule="0 15 * * *"

# Vanito voice notes: 3:30 PM
cronjob action=update job_id=a564b3353770 schedule="30 15 * * *"
```

### Pitfall 3: Static HTML with Hardcoded Data

**Problem:** Dashboard shows old data because HTML is hardcoded.

**Example:** Vanito's music hub showed "No songs yet!" even though JSON had 2 songs.

**Fix:** Use JavaScript to fetch JSON dynamically:
```javascript
async function loadMusic() {
  const response = await fetch('hub-vanito-data.json');
  const data = await response.json();
  // Render songs from data.music.songs
}
```

### Pitfall 4: Missing Back Navigation

**Problem:** User stuck in specialized dashboard, no way back to main hub.

**Fix:** Add back link in header with absolute positioning.

### Pitfall 5: Sync Script Not Committing Data File

**Problem:** Data file changes not pushed to GitHub, dashboards show old data.

**Fix:** Include data file in git add:
```python
subprocess.run(['git', 'add', 'Gaming/vanito-music.json', 'hub-vanito-data.json'], cwd='/root/ProtoJay4789.github.io')
```

### Pitfall 6: Hardcoded HTML Data Instead of Dynamic Loading (`Gaming/poe2-jordan.html`) showed Level 28 even though `poe2-jordan-monk.json` had Level 31 because HTML had hardcoded `const characters = { "monk-jordan": { level: 28, ... } }` instead of fetching from JSON.

**User Signal:** When user says "updates aren't being pushed" or "it looks like updates aren't working", check if HTML is hardcoded vs dynamic.

**Fix:** Use JavaScript to fetch JSON dynamically and render:
```javascript
// ✅ CORRECT - Dynamic loading
let characterData = null;

async function loadCharacterData() {
  try {
    const response = await fetch('poe2-jordan-monk.json');
    characterData = await response.json();
    renderCharacters();
  } catch (error) {
    console.error('Failed to load character data:', error);
    // Fallback to hardcoded data if JSON fails
    characterData = { /* fallback data */ };
    renderCharacters();
  }
}

function renderCharacters() {
  const grid = document.getElementById('character-grid');
  grid.innerHTML = '';

  const charInfo = characterData.character;
  const skills = characterData.skills;

  grid.innerHTML = `
    <h3>${charInfo.alias}</h3>
    <div class="class">${charInfo.class} — ${charInfo.ascendancy}</div>
    <div class="level">Level ${charInfo.level} • ${charInfo.act}</div>
    <!-- Render skills dynamically -->
  `;
}

// Initialize
loadCharacterData();

// ❌ WRONG - Hardcoded data (never updates)
const characters = {
  "monk-jordan": {
    alias: "Lightning Monk",
    level: 28,
    act: "Act 2"
    // This data is frozen at commit time
  }
};
renderCharacters();
```

**Diagnostic Pattern:** When user reports stale data:
1. Check if JSON file is updated (read file, check `lastUpdated` field)
2. Check if HTML has `fetch()` call for that JSON
3. If HTML has hardcoded data structure, rewrite to dynamic loading
4. Test by updating JSON and verifying dashboard reflects changes

### Audio Upload Workflow — User-Sung Songs

**Rule:** When a family member sends MP3 audio recordings of themselves singing original songs, the workflow is: transcribe → extract metadata → name files correctly → add to hub → push.

**Full Workflow:**

```
1. TRANSCRIBE — Whisper the audio to get lyrics
   whisper --model base --language en "<path>" 2>/dev/null

2. EXTRACT TITLE — Read ID3 metadata for the REAL song title
   ffprobe -v quiet -show_entries format_tags "<path>"
   → TAG:title=Fight Forever Never Quit  (this is the real title)

3. COPY TO HUB — Place in a dedicated directory
   mkdir -p /root/ProtoJay4789.github.io/music/<person>/
   cp <audio_path> /root/ProtoJay4789.github.io/music/<person>/<kebabed-title>.mp3

4. CHECK GITIGNORE — The repo likely blocks **/*.mp3
   Add an exception BEFORE the **/*.mp3 rule:
     **/*.mp3
     !music/<person>/*.mp3   ← add this

5. UPDATE DATA JSON — Add song entry with exact title from metadata
   hub-<person>-data.json → music.songs array

6. COMMIT & PUSH
   git add -A
   git commit -m "..."
   git push

7. SAVE LYRICS — Also save transcribed lyrics to vault
   /root/vaults/gentech/Travels/music/<person>-<kebabed-title>.txt
```

**Key gotchas:**
- Always check ID3 tags (`ffprobe -v quiet -show_entries format_tags`) — Telegram renames files to `audio_xxx.mp3`, the REAL title is inside the metadata
- The `.gitignore` almost certainly blocks `**/*.mp3` — add a `!music/<person>/*.mp3` exception before the wildcard rule
- Some people use Japanese Romaji titles (e.g. "Mirai e Hashire") — preserve the exact form from metadata
- After pushing, wait ~30s for GitHub Pages deployment

### Music Vault Page Pattern

When building a music vault index page with inline audio players:

```html
<!-- music/<person>/index.html -->
<h1>🎧 Person's Music Vault</h1>
<div class="track-list">
  <div class="track">
    <div class="num">01</div>
    <div class="info">
      <div class="title">Fight Forever Never Quit</div>
      <div class="ext">.mp3</div>
    </div>
    <audio controls src="fight-forever-never-quit.mp3"></audio>
  </div>
</div>
```

**Workflow:**
1. Hardcode each track's filename and title (music vaults are small — usually 3-10 tracks)
2. Use `<audio controls>` element for native browser playback (works in glasses webview if audio is supported)
3. Link back to the person's hub: `<a href="../Vanito/">← Vanito's Hub</a>`
4. Place MP3 files in the same directory as index.html
5. `.gitignore` must have a `!music/<person>/*.mp3` exception before the catch-all `**/*.mp3` rule

### Character Bio Page Pattern

**Rule:** When a family member creates named characters/artists, add a dedicated tab section with their bios, images, and backstories.

**Bottom Nav button:**
```html
<button class="nav-item" data-tab="characters" onclick="switchTab('characters')">
  <span class="icon">🎭</span>
  <span>Artists</span>
</button>
```

**Tab content structure:**
```html
<div id="tab-characters" class="tab-content">
  <!-- Hero banner image (editable version without text overlay) -->
  <!-- Section title -->
  <!-- Individual character cards with portrait image + bio + tags -->
  <!-- Together/"how they met" card for duo characters -->
</div>
```

**Character card layout (compact bio + native audio player):**
```html
<div class="card card-kage" style="padding:16px; margin-bottom:16px;">
  <div style="display:flex; gap:12px;">
    <img src="..." style="width:100px; height:100px; object-fit:cover; border-radius:8px; border:2px solid #cc2222; flex-shrink:0; cursor:pointer;" onclick="document.getElementById('kage-player').play()">
    <div style="flex:1; min-width:0;">
      <div class="char-name-kage">KAGE</div>
      <div class="char-subtitle">影 — Shadow</div>
      <div class="char-bio" style="margin-top:4px; font-size:0.78rem; line-height:1.4;">
        Short bio text here...
      </div>
      <div style="margin-top:6px;">
        <audio id="kage-player" controls preload="none" style="width:100%; height:36px; border-radius:4px;">
          <source src="music/path/to/song.mp3" type="audio/mpeg">
        </audio>
      </div>
      <div style="margin-top:4px; display:flex; gap:4px; flex-wrap:wrap;">
        <span class="char-tag red">Tag1</span>
        <span class="char-tag dark">Tag2</span>
      </div>
    </div>
  </div>
</div>
```

**Together / "How They Met" card for duos:**
```html
<div class="card card-together" style="padding:16px; text-align:center;">
  <div style="font-size:1rem; font-weight:700; color:#cc3333; letter-spacing:1px;">KAGE × HIKARI</div>
  <div style="font-size:0.8rem; color:#777; margin-top:4px; font-style:italic;">Tagline here</div>
  <div class="char-bio" style="margin-top:8px; font-size:0.8rem; text-align:left;">
    Short origin story: how they met, first collab, current album.
  </div>
  <div style="margin-top:8px;">
    <audio controls preload="none" style="width:100%; height:36px; border-radius:4px;">
      <source src="music/vanito/their-duet-song.mp3" type="audio/mpeg">
    </audio>
  </div>
  <div style="margin-top:8px; display:flex; gap:4px; justify-content:center; flex-wrap:wrap;">
    <span class="char-badge" style="background:#5d1a0a; color:#ff8844; border:1px solid #8d2a0a;">DUET</span>
    <span class="char-badge" style="background:#1a0a2d; color:#bb88ff; border:1px solid #3d1a5d;">ALBUM NAME</span>
    <span class="char-badge" style="background:#1a1a1a; color:#aaa; border:1px solid #333;">COLLAB</span>
  </div>
</div>
```

**Dynamic Header Swapping Pattern:**
When switching to the characters/artists tab, swap the main page header to show the album/character art instead of the default branded header.

```css
/* CSS classes needed */
#page-header.normal-header {
  background: linear-gradient(135deg, var(--gold) 0%, var(--fire) 50%, var(--magma) 100%);
  padding: 32px 20px 28px;
  text-align: center;
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
}

#page-header.characters-header {
  padding: 0;
  background: none;
  overflow: hidden;
  position: relative;
  border-radius: 0 0 12px 12px;
}

#page-header.characters-header img {
  width: 100%;
  display: block;
  border-radius: 0 0 12px 12px;
}

#page-header.characters-header .settings-btn {
  z-index: 3;
}
```

```javascript
// JS in switchTab function
function switchTab(tab) {
  document.querySelectorAll('.tab-content').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(b => b.classList.remove('active'));
  const section = document.getElementById('tab-' + tab);
  const btn = document.querySelector('.nav-item[data-tab="' + tab + '"]');
  if (section) section.classList.add('active');
  if (btn) btn.classList.add('active');
  window.scrollTo(0, 0);

  // Dynamic header swap
  const header = document.getElementById('page-header');
  if (tab === 'characters') {
    header.className = 'characters-header';
    header.innerHTML = `
      <img src="music/vanito/kage-hikari-album-cover.png" alt="KAGEKŌ">
      <button class="settings-btn" onclick="openSettings()" title="Settings">⚙️</button>
    `;
  } else {
    header.className = 'header normal-header';  // ⚠️ MUST keep .header class
    header.innerHTML = `
      <h1>⚔️ Person's Hub</h1>
      <div class="subtitle">Tagline here</div>
      <button class="settings-btn" onclick="openSettings()" title="Settings">⚙️</button>
    `;
  }
}
```

**PITFALL — CSS class stripping on header swap:**
When using `header.innerHTML` to swap content, the old .header CSS class is lost if you don't include it in the new className. The original header HTML had `class="header"` which applied gradient background, padding, and ::before shimmer via CSS. If you switch to `header.className = 'normal-header'` without including 'header', all those styles vanish and the header becomes invisible on all tabs. Always set `className = 'header normal-header'` for the normal state.

**PITFALL — inline event handlers on innerHTML:**
When using `header.innerHTML = \`...\``, ALL inline event handlers (`onclick=...`) need to be re-assigned in the HTML string. Any event listeners attached via `addEventListener` on child elements of the old innerHTML are lost. Settings button, modal toggles, etc. must have their onclick inline.

**Tab-level theming to match album artwork:**
The entire characters tab can be independently styled to match the album's aesthetic:

```css
#tab-characters {
  background: #0d0d0d;
  border-radius: 12px;
  padding: 16px;
  margin-top: -8px;
}

#tab-characters .card {
  background: linear-gradient(145deg, #1a0a0a 0%, #0d0d0d 100%);
  border: 1px solid #3d1a1a;
  border-radius: 12px;
}

#tab-characters .card-kage {
  border-left: 3px solid #cc2222;
  box-shadow: 0 0 15px rgba(200, 30, 30, 0.1);
}

#tab-characters .card-hikari {
  border-left: 3px solid #cc3333;
  box-shadow: 0 0 15px rgba(200, 50, 50, 0.1);
}

#tab-characters .card-together {
  border: 1px solid #5d2a0a;
  background: linear-gradient(180deg, #1a0a0a 0%, #0d0805 100%);
  box-shadow: 0 0 20px rgba(200, 80, 20, 0.08);
}

#tab-characters .section-title {
  color: #cc3333;
}

.char-name-kage {
  font-size: 1.3rem;
  font-weight: 800;
  color: #e83030;
  text-shadow: 0 0 10px rgba(232, 48, 48, 0.3);
  letter-spacing: 2px;
}

.char-name-hikari {
  font-size: 1.3rem;
  font-weight: 800;
  color: #e03030;
  letter-spacing: 2px;
}

.char-subtitle {
  font-size: 0.8rem;
  color: #666;
  font-style: italic;
}

.char-bio {
  margin-top: 8px;
  font-size: 0.85rem;
  line-height: 1.6;
  color: #ccc;
}

.char-tag {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.char-tag.red { background: #cc2222; color: #fff; }
.char-tag.gold { background: #cc3333; color: #fff; }
.char-tag.dark { background: #1a1a1a; color: #aaa; border: 1px solid #333; }
.char-tag.fire { background: #cc4400; color: #fff; }

.char-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
}
```

**Image editing for character art (blockrun_image):**
When a user provides character images that contain text (titles, labels, lyrics), edit them to remove text:

```javascript
blockrun_image({
  action: "edit",
  image: "<local_filepath>",  // use 'image' param (NOT 'image_url')
  model: "openai/gpt-image-2",
  prompt: "Remove ALL text from this image. Remove 'X', 'Y', 'Z'... Keep ONLY the character and background.",
  size: "1024x1024"
})
```

**Prompt strategy — be exhaustive:**
- List EVERY text element to remove explicitly (titles, subtitles, Japanese characters, labels, Parental Advisory, lyrics)
- List what to KEEP: character appearance (hair style, clothing, pose, colors), background (moon, buildings, landmarks, atmosphere)
- Close with: "The image should look like the original artwork but with all text completely removed"
- Size should match source image aspect ratio

**After generation, verify:**
```bash
curl -s -o <target-path> <result-url>
vision_analyze(image="<path>", question="Is there any text remaining on this image?")
```
If residual text from background elements (neon signs, graffiti) remains, assess if it's ambient scene detail vs legible title text. Only re-run if main titles survive.

**PITFALL — .gitignore blocks new formats:** The repo likely blocks `**/*.png` or `**/*.jpg`. After saving edited images as PNG, verify with `git add` and add `!music/vanito/*.png` exceptions as needed.

**Album Cover Generation — Iterative Show-Before-Save (Vanito preference):**

1. **GENERATE** — Create image with detailed prompt referencing character designs
2. **SHOW** — Present URL in chat: "Just a look, not saved unless you say so 👀"
3. **GET FEEDBACK** — Let Vanito react ("slice it", "not anime", "make them look the same")
4. **REGENERATE** — Apply feedback (split composition, change art style)
5. **SHOW AGAIN** — Wait for explicit approval ("YESSSSSS")
6. **SAVE** — Only after explicit instruction ("put it on the hub")

**CRITICAL: Do NOT save to hub/repo until Vanito explicitly says to.** Premature saving breaks the iterative workflow. Keep generated images as references in chat only.

**Split composition technique** (when user asks for "slice" or "split" look):
- Left half: Character A with dark/crimson tones
- Right half: Character B with warm/golden tones
- Divide: Jagged crack of fire, shattered mirror, or diagonal split
- Background shared: red sun, skyline, banners, floating embers

**Native Audio Player on Character Cards:**
```html
<audio id="kage-player" controls preload="none" style="width:100%; height:36px; border-radius:4px;">
  <source src="music/vanito/song.mp3" type="audio/mpeg">
</audio>
<img src="..." onclick="document.getElementById('kage-player').play()">
```
**Telegram in-app browser restriction:** `audio.play()` via onclick often fails silently even from direct user gestures. The native `<audio controls>` play button reliably works. Do NOT use `new Audio(url).play()`. Verify MP3 content-type via `curl -sI`.

**Cache prevention for frequently updated content:**
```html
<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
<meta http-equiv="Pragma" content="no-cache">
<meta http-equiv="Expires" content="0">
```
GitHub Pages has its own CDN caching — hard refresh (Ctrl+Shift+R) or private tab is most reliable.

### Animated Character Profile Pictures

**Rule:** Vanito wants character images animated as looping videos, not static PNGs.

**Workflow:**
1. Generate looping 5s video from character PNG via xAI Grok video (cheaper, less restrictive)
2. Save as `<name>-animated.mp4` in `music/vanito/`
3. Replace `<img>` with `<video autoplay loop muted playsinline poster="original.png">`
4. Increase size (Vanito found 100×100 too small — use 140×140)
5. Always include `poster` fallback for mobile browsers that don't autoplay

**Cost:** ~$0.26 per character via xAI Grok. Seedance 2.0 Fast (~$1.27) rejected for "real person detection".

**Prompt pattern:**
```
Portrait of [character description], slow subtle motion, 
[hair/feature] sways gently, [light color] light pulses softly. 
Same character designs, same composition.
```

### Canvas Rain Effect

For realistic rain that drips over content, use JavaScript canvas (not CSS):

- `<canvas id="rain-canvas">` hidden by default
- 150 drops with random speed/thickness/wind
- Splash particles on bottom impact
- `requestAnimationFrame` loop
- CSS water sheen overlay on cards via `::after`
- Always use `pointer-events: none` on canvas

**File locations:** Canvas element before `</body>`, JS engine before `</script>`, CSS in `<style>`.

### Scene Animation Pipeline

When generating story scenes to animate:

1. **Generate scene image** → show preview (don't save yet)
2. **Vanito approves** → animate via xAI Grok video (5s, $0.26)
3. **Show animated preview** → wait for approval
4. **Save MP4** to `music/vanito/` and embed in hub
5. **GitHub Pages delay** — use `https://raw.githubusercontent.com/ProtoJay4789/ProtoJay4789.github.io/main/...` URLs instead of relative paths

### GitHub Pages Video Delivery

**Rule:** Videos pushed to GitHub Pages have a 30-60s deployment delay. Use raw GitHub CDN for instant delivery:

```html
<video src="https://raw.githubusercontent.com/ProtoJay4789/ProtoJay4789.github.io/main/music/vanito/file.mp4"
  autoplay loop muted playsinline>
</video>
```

### Gitignore Exception Ordering

**Rule:** gitignore rules are order-dependent — later rules override earlier ones. Always put blanket **deny first**, then `!` exceptions after:

```gitignore
# ✅ CORRECT
**/*.mp4
!music/vanito/*.mp4   # This exception works

# ❌ WRONG
!music/vanito/*.mp4   # This gets overridden
**/*.mp4               # by this
```

### MEDIA: Prefix for Telegram

When showing images/videos inline on Telegram, use the MEDIA: prefix:

```
MEDIA:/absolute/path/to/file.png
```

This renders the media directly in the chat instead of a blue hyperlink.

### Pitfall 9: Building Business Tabs Instead of Lifestyle Tabs

**Problem:** Creating a personal hub with business/metric tabs (Overview, Build, Portfolio, Links) when the user wants lifestyle/topic tabs.

**User Signal:** Jordan rejected an Overview/Build/Portfolio/Links layout and asked for Travel, POE2, Gaming, Shop instead. Vanito's hub had Characters, Music, Deals from the start.

**Fix:** Before building a personal hub, ask what the person is into — hobbies, games, travel, creative work. Map those to tabs. Business tabs belong on landing pages, not personal hubs.

**Tab archetypes by person type:**
- **Builder (Jordan):** Travel, POE2, Gaming, Shop
- **Artist (Vanito):** Characters, Music, Deals, Shop
- **Learner archetype:** Travel, Shopping, Cooking

### Pitfall 10: Deploying to Wrong Location

**Problem:** Building hub files in the GitHub Pages repo but not deploying them to the VPS.

**Fix:** Always run the deploy step after building:
```bash
cp ~/repos/ProtoJay4789.github.io/<name>.html /var/www/gentechlabs/<name>.html
chown www-data:www-data /var/www/gentechlabs/<name>.html
curl -s https://gentechlabs.net/<name>.html | grep "<title>"
```

**Problem:** Sync script times out or hangs when GitHub repository has divergent branches or conflicts. GitRepoLock doesn't handle all edge cases, causing script to hang indefinitely.

**Example:** Vanito music sync cronjob timed out after 60s. Investigation showed repo had divergent branches (local ahead by 2 commits, remote also moved forward). GitRepoLock's `push_with_retry()` couldn't reconcile automatically.

**User Signal:** Cronjob shows "Command timed out" or hangs without output. Terminal shows script running but never completes.

**Fix Pattern:** Add divergent branch detection and force reset before sync operations:
```python
# Add to sync script before git operations
def ensure_clean_repo_state():
    """Ensure repo is in clean state before sync"""
    import subprocess

    # Check if repo has divergent branches
    result = subprocess.run(
        ['git', 'fetch', 'origin'],
        cwd='/root/ProtoJay4789.github.io',
        capture_output=True
    )

    # Check if local is behind or divergent
    status = subprocess.run(
        ['git', 'status', '--short', '--branch'],
        cwd='/root/ProtoJay4789.github.io',
        capture_output=True,
        text=True
    )

    if 'diverged' in status.stdout.lower() or 'behind' in status.stdout.lower():
        print("Divergent branches detected, resetting to origin/main")
        subprocess.run(
            ['git', 'reset', '--hard', 'origin/main'],
            cwd='/root/ProtoJay4789.github.io',
            capture_output=True
        )
        return True

    return False

# Call before git operations in main()
ensure_clean_repo_state()
```

**Fallback Pattern for Manual Recovery:**
```bash
# When sync script hangs, manually recover
cd /root/ProtoJay4789.github.io

# Stash any local changes
git stash push -m "Temporary stash for sync"

# Force reset to match remote
git fetch origin
git reset --hard origin/main

# Clean up untracked files
rm -f audio_*.json audio_*.srt audio_*.tsv audio_*.txt audio_*.vtt

# Run sync again
python /root/my-music/vanito-music-sync.py
```

**Timeout Configuration:**
```python
# In sync script, set appropriate timeout for git operations
# Git operations can hang, especially with network issues
GIT_TIMEOUT = 120  # 2 minutes for git fetch/push

subprocess.run(
    ['git', 'push'],
    cwd='/root/ProtoJay4789.github.io',
    timeout=GIT_TIMEOUT,
    capture_output=True
)
```

## Reference Files

- `references/family-member-registry.md` — Full Steam IDs, cronjob IDs, file paths for Jordan, Vanito, Christel
- `references/cronjob-coordination-strategies.md` — Schedule optimization, staggering patterns, person-level data isolation
- `scripts/verify-family-hub-deployment.sh` — Automated verification script for family hub deployment

## Related Skills

- `gentech-daily-sync` — Daily vault synchronization
- `gentech-hub` — Hub architecture and data structures
- `enhanced-gentech-shop` — Shopping dashboards and price tracking
- `portfolio-deployment` — GitHub Pages deployment patterns
- `ar-vr-wearable-web-apps` — Glasses web app deployment patterns (tunnels, HTTPS, DPAD apps)