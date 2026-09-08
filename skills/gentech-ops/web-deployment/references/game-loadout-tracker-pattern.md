# Per-Game Loadout / Character Tracker Pattern

How GenTech tracks per-game builds on the live hub. Proven with POE2 (characters)
and Helldivers 2 (loadouts). Any new game tracker should follow this shape.

## The user problem this solves
Some games (Helldivers 2 notably) have NO in-game way to view or save a full
build — stratagems only appear mid-drop, separate from the weapons/armor screen.
The hub becomes the one screen the game refuses to give: **everything in a build
viewable + savable at a glance**, per faction/situation, updated by telling the
agent. This is a demo-able, subscription-flavored feature ("I can save and view
my build anytime").

## File layout (in canonical repo `/root/ProtoJay4789.github.io/`)
```
Gaming/
├── <game>.html          ← themed page, fetches the .json and renders cards
├── <game>-loadouts.json ← the saved builds (single source of truth)
└── (poe2-jordan.html, poe2-characters.json … existing examples)
```
Deploy copies BOTH files to `/var/www/gentechlabs/Gaming/` (nginx serves it at
`https://gentechlabs.net/Gaming/<game>.html`).

## JSON schema (Helldivers loadout — one card per named soldier)
```json
{
  "loadouts": [
    {
      "id": "destruction-diver",
      "player": "Jordan",
      "alias": "Destruction Diver",        ← the soldier's codename
      "warfront": "Automatons",            ← Bots / Bugs / Illuminate
      "role": "Anti-armor / Factory demolisher",
      "level": 74,
      "rank": "Exemplary Subject",
      "loadout": {
        "primary": "R-36 Eruptor",
        "secondary": "LAS-58 Talon",
        "throwable": "G-123 Thermite",
        "armor": "CE-81 Juggernaut (Medium)",
        "booster": ""
      },
      "stratagems": [
        "Bullet Storm (Orbital)",
        "Supply Pack",
        "Autocannon Sentry",
        "Laser Sentry"
      ],
      "strength": "Explosive anti-armor + thermite for heavy demolitions.",
      "weakness": "Eruptor is slow-firing with a long reload; vulnerable in close quarters.",
      "status": "Active",
      "lastUpdated": "2026-08-04",
      "notes": "First saved build. Factory destruction focus."
    }
  ]
}
```
The `stratagems[4]` array is the key value-add — it's the data the game hides.

## Themed page
Match the game's UI palette, not the generic dark theme:
- Helldivers 2: deep navy (`#05070f` bg, `#0a1628` cards, `#1e3a5f` borders),
  cyan accent (`#00d4ff` headers/borders), gold (`#c9a84c`) for stratagems/notes,
  red badge for Automatons.
- Warfront color-coded badges: bots=red, bugs=yellow/gold, illuminate=blue.
- Stratagem rows get emoji icons (🔥 strike, 📦 supply, 🛡️ sentry, ⚡ laser, 💥 mortar).
- Equipment grid (primary/secondary/throwable/armor) + a STRATAGEMS list + a
  strengths/weaknesses/notes box.
- `fetch('<game>-loadouts.json?t='+Date.now())` for cache-busting, with a
  hardcoded empty-state fallback and an error message on load failure.

## Hub wiring
Add a `link-card` to the relevant tab's `link-grid` in `/var/www/gentechlabs/hub.html`:
```html
<a href="https://gentechlabs.net/Gaming/helldivers2.html" class="link-card">
    <div class="icon">🪖</div>
    <span>Helldivers 2 Loadouts</span>
    <div class="desc">Saved builds — weapons, armor, stratagems</div>
</a>
```

## Growing it over time
Same discovery loop as POE2 builds: user tells you a new combo (warfront +
weapons + armor + 4 stratagems), you add a new card. One named soldier per
faction/situation (bots, bug-horde, illuminate), iterating as loadouts evolve.
Ask for the missing pieces explicitly (e.g. "what are the 4 stratagems?") rather
than guessing.

## Verify checklist
1. `curl -o /dev/null -w "%{http_code}"` on the live page → 200.
2. `curl -o /dev/null -w "%{http_code}"` on the live .json → 200 (page breaks if this 404s).
3. `curl https://gentechlabs.net/hub.html | grep -c "<Label>"` → ≥1.
4. Confirm the page renders via browser snapshot (check the card content appears).
