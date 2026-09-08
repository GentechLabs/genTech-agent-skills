# Portfolio Site Structure Reference

**File:** `/root/vaults/gentech/github/ProtoJay4789.github.io/index.html`

## Current Sections (in order)

| ID | Title | Line Range |
|----|-------|------------|
| `sec-about` | About | ~900-1000 |
| `sec-journey` | Journey | ~1000-1100 |
| `sec-projects` | Projects | ~1100-1150 |
| `sec-stack` | AAE Stack | ~1150-1160 |
| `sec-apis` | API Services | ~1162-1232 |
| `sec-casestudies` | Case Studies | ~1234-1290 |

## CSS Color Variables (line ~10-22)

```css
--bg: #0a0a0f;
--panel: #101018;
--border: #1a1a2e;
--blue: #3b82f6;
--cyan: #06b6d4;
--purple: #8b5cf6;
--text: #e0e0e0;
--dim: #64748b;
--card: #111119;
--card-hover: #16161f;
--green: #22c55e;
--amber: #f59e0b;
```

## Card Classes

### Section Card
```html
<div class="card project-card">
  <div class="card-header">
    <span class="card-title">Title</span>
    <span class="status-badge status-live"><span class="status-dot"></span> Live</span>
  </div>
  <div class="project-tech">
    <span class="tag tag-blue|cyan|green|purple|amber">Label</span>
  </div>
  <div class="card-desc">Description text</div>
</div>
```

### Status Badges
- `status-live` - Green dot, "Live" text
- `status-building` - Blue dot, "Building" text
- `status-planned` - Gray dot, "Planned" text

### Tag Colors
- `tag-blue` - Primary technology
- `tag-cyan` - Secondary technology
- `tag-green` - Status or protocol
- `tag-purple` - Domain
- `tag-amber` - Warning or special

## Navigation Update Locations

### 1. Bottom Nav (line ~1328-1350)
```html
<button class="nav-item" onclick="scrollToSection('sec-NAME')">
  <span class="icon">🔥</span>
  <span>Title</span>
</button>
```

### 2. Settings Modal (line ~830-850)
```html
<button class="settings-option" onclick="scrollToSection('sec-NAME');closeSettings()">
  <span style="font-size:1.3em;">🔥</span>
  <div><strong>Title</strong><br><span style="font-size:0.8em; color:var(--dim);">Subtitle</span></div>
</button>
```

### 3. Section Mapping (line ~1364-1372)
```javascript
const map = {
  'sec-about': 0,
  'sec-journey': 1,
  'sec-projects': 2,
  'sec-stack': 3,
  'sec-apis': 4,
  'sec-casestudies': 5,
  'sec-NAME': 6  // Add incrementing number
};
```

### 4. Scroll Spy Array (line ~1378)
```javascript
const sections = ['sec-about', 'sec-journey', 'sec-projects', 'sec-stack', 'sec-apis', 'sec-casestudies', 'sec-NAME'];
```

## Insertion Pattern

Between sections, the pattern is:
```html
<a href="https://gentechlabs.net" target="_blank" class="link-btn">🧪 Browse All APIs →</a>
  </div>

  <!-- ═══ NEXT SECTION ═══ -->
  <div id="sec-next" style="margin-top: 18px;">
```

The closing `</div>` belongs to the previous section, then there's a blank line, then the next section starts.

## Methodology Card

```html
<div class="methodology">
  <em>"Quote text here"</em>
</div>
```

Used for summary or philosophical statements at the end of sections.

## Git Configuration

**User:** `Gentech`  
**Email:** `gentech@protojay4789.github.io`  
**Remote:** `https://github.com/ProtoJay4789/ProtoJay4789.github.io.git`

## Known Issues

- Push may fail if credentials not configured on VPS
- Use SSH key or OAuth token for automated pushes
- Manual push from user's machine is safe fallback