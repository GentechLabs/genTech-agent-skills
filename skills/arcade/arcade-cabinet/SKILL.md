---
name: arcade-cabinet
description: "Build, rebrand, and deploy arcade cabinet games for the GenTech Arcade at arcade.gentechlabs.net. Covers forking game codebases, adding mobile/gamepad input, AI spectator mode, x402 payment hooks, and deploying to the arcade subdomain."
version: 1.0.0
author: Gentech
tags: [arcade, game-dev, threejs, mobile, gamepad, deployment]
---

# Arcade Cabinet Development

## Overview

The GenTech Arcade is a collection of browser-based cabinet games served from `arcade.gentechlabs.net/cabinet/{game-name}/`. Each cabinet is a standalone Three.js/WebGL game (no art assets — procedurally generated where possible), wrapped in GenTech branding, with mobile touch controls, gamepad support, and x402 betting hooks.

## Core Stack

- **Rendering:** Three.js r180+, WebGL2
- **Build tool:** Vite 7+
- **Deployment:** nginx on VPS (2.24.195.196), SSL via Let's Encrypt
- **Mobile input:** Custom touch overlay (virtual joystick + action buttons) + Gamepad API
- **Payment:** x402 gateway / Q402 for betting and microtransactions
- **AI/agents:** AI-vs-AI mode where agents pilot characters, spectators watch

## Build Workflow

### 1. Source Game Selection

Prefer games that are:
- MIT-licensed (or permissive open-source)
- Three.js / vanilla JS (minimal dependencies)
- Procedurally generated assets (no art pipeline needed)
- Browser-native (runs in canvas, no native plugins)

**Proven sources:**
| Game | Stack | Stars | Notes |
|------|-------|-------|-------|
| Claude of Duty → Agent Warfare | Three.js, custom physics | 631 ⭐ | FPS, 55k lines, all procedural, MIT |
| Cesium Flight Sim → Gentech DogFighters | Cesium, React, TypeScript | 422 ⭐ | 3D flight sim, real-world terrain, Mapbox mini-map, crash detection |

### 2. Rebrand & Structure

```bash
# Clone
git clone <source> /root/agent-warfare
# Rename
nano package.json  # name, description
nano index.html    # title, <style>, GenTech watermark
# Commit
git add -A && git commit -m "Rebrand: name, GenTech styling"
```

**GenTech styling constants:**
- Cyan: `#00f0ff` (`--gentech-cyan`)
- Pink: `#ff2d8e` (`--gentech-pink`)
- Footer watermark: `GEN<span>TECH</span> // ARCADE`

### 3. Add Mobile + Gamepad Input

The game's input system (`src/core/input.js`) already has `navigator.getGamepads()` polling. Extend with:

**Gamepad button mapping** (`ACTIONS` → `GAMEPAD_MAP`):
```js
export const GAMEPAD_MAP = {
  jump:        { btn: 0 },   // A
  crouch:      { btn: 1 },   // B
  reload:      { btn: 2 },   // X
  swapWeapon:  { btn: 3 },   // Y
  leanLeft:    { btn: 4 },   // LB
  leanRight:   { btn: 5 },   // RB
  melee:       { btn: 11 },  // R3
  sprint:      { btn: 10, threshold: 0.5 }, // L3 (push-to-sprint)
  pause:       { btn: 9 },   // Start
  _fire:       { axis: 3, threshold: 0.3 }, // RT trigger
  _ads:        { axis: 2, threshold: 0.3 }, // LT trigger
};
```

**Touch controls overlay** (`src/core/touch.js`):
- Virtual joystick (left half of screen) — movement via synthetic `KeyW/A/S/D` events
- Look drag (right half) — synthetic `mousemove` delta events
- Action buttons: FIRE, ADS, JUMP, CROUCH, SPRINT, RELOAD
- Mobile detection: skip pointer lock, init overlay before engine.start()

See `references/touch-gamepad-pattern.md` for the full implementation details.

**Deterministic scene transitions (shelf→detail, overview→inspect):** For any cabinet that moves a selected object between an overview and a detail scene graph, use the pattern banked from MengTo's Complete Shelf — a `mode` state machine (`hero→opening→detail→closing`), normalized `transitionTime` driven by accumulated delta, poses applied as pure functions, and `damp()`/`smoothstep()` for easing. This prevents the "last-frame jump" when reparenting an object between scenes. See `references/threejs-deterministic-transition.md`.

### 4. Vite Config for Subdirectory Deployment

```js
// vite.config.js
export default defineConfig({
  base: '/cabinet/{game-name}/',
  build: { target: 'es2022', sourcemap: true },
});
```

### 5. Build & Deploy

```bash
npx vite build
rsync -avz --delete dist/ root@2.24.195.196:/var/www/arcade/cabinet/{game-name}/
```

### 6. nginx Route

Add to VPS `/etc/nginx/sites-enabled/arcade`:
```nginx
location /cabinet/{game-name}/ {
    alias /var/www/arcade/cabinet/{game-name}/;
    index index.html;
    try_files $uri $uri/ /cabinet/{game-name}/index.html;
    add_header Cache-Control 'no-cache';
}
```

### 7. Git Push

```bash
gh repo create ProtoJay4789/{game-name} --public --description "..."
git remote add origin https://github.com/ProtoJay4789/{game-name}.git
git push -u origin main
```

## 3D Lobby Asset Generation (text-to-cad)

For generating arcade lobby models (stairs, lounge furniture, cabinets, signage) from text:

**Pipeline:** Text prompt → build123d Python → STEP + GLB → Three.js scene

**Tool:** `earthtojake/text-to-cad` (10.6k ⭐, MIT) — clone at `/root/text-to-cad/`

**Requirements:** Python 3.12+, cadpy package
```bash
python3.12 -m venv  /root/text-to-cad/.venv
source /root/text-to-cad/.venv/bin/activate
pip install -e /root/text-to-cad/skills/cad/scripts/packages/cadpy
```

**Usage:**
```bash
# Write a build123d generator function in source.py
# source.py must define `def gen_step() -> Shape:`
source /root/text-to-cad/.venv/bin/activate
cd /tmp && python3 /root/text-to-cad/skills/cad/scripts/step \
  source.py --glb output.glb --verbose
```

See `references/text-to-cad-pipeline.md` for detailed patterns.

## AI Spectator Mode (Planned)

Drop the human player, let AI agents fight each other:
- Remove player input dependency from the game loop
- Add free-camera spectator mode
- Display agent stats + betting odds
- Wire x402/Q402 payment hooks for betting

## Agent Archetypes / Classes (Planned)

Subclass the AI behavior system (`src/ai/`, 8,193 lines) into distinct classes:

| Archetype | Speed | Health | Weapons | AI Behavior |
|-----------|-------|--------|---------|-------------|
| Sniper | Slow | Low | Long-range rifle | Finds high ground, holds angles, reposition on detection |
| Scout | Fast | Low | SMG/pistol | Flanks, hit-and-run, pathfinds through cover |
| Heavy | Slow | High | LMG/shotgun | Pushes chokepoints, suppresses, absorbs damage |
| Medic | Medium | Medium | Pistol | Heals allies, stays behind front line, retreats under fire |
| Engineer | Medium | Medium | Rifle | Deploys cover/turrets, repairs, area denial |

Each archetype gets its own decision tree, movement profile, weapon loadout, and squad role.

## Procedural Map Generation via text-to-cad (Planned)

Use the text-to-cad pipeline to generate playable FPS levels:

1. Describe the map: "urban courtyard with two-story buildings, central fountain, alleyways on both sides"
2. Write build123d Python → generate GLB
3. Load GLB into Three.js as the playable level geometry
4. Add navmesh, spawn points, and objective markers

Maps are fully procedural — no art assets needed. Ship with a dozen unique maps.

## Funding Engine: ClawWork Employee Squad

The arcade is funded by autonomous ClawWork agents earning on freelancer tasks:
- See `clawwork-agent-freelancing` skill for setup
- $19K/8hrs demonstrated by ATIC+Qwen3.5-Plus
- Funds VPS, game development, x402 payouts, and tournament prizes

## Revenue Stream: Paymenter x402 Gateway

The arcade's x402 payment infrastructure also generates revenue as a **hosting billing gateway extension**:
- See `hosting-billing-gateway` skill for the Paymenter extension pattern
- 227 Paymenter extensions, zero crypto gateways — first-mover market
- 0.5% tx fee on every payment through our gateway
- Same pattern extends to WHMCS, Blesta, HostBill
- "Powered by GenTech" branding on every checkout page

## Talent Pipeline: Hippocratic AI Deployment Engineering Residency

Hippocratic AI offers a paid 3+ month residency for engineers building production AI agents in healthcare. Rotations across Product, Engineering, Model & Deployment teams. Rolling applications. Relevant to GenTech as a talent pipeline — they build the same kind of agent infrastructure we do, just in healthcare. Keep on radar for partnership or hiring angles.

## Pipeline: Gentech → Forge → Gentech

| Phase | Who | What |
|-------|-----|------|
| Design | Gentech | text-to-cad maps, archetype specs, game concepts |
| Build | Forge | GPU-heavy work (Modly meshes, game logic, AI behavior) |
| Ship | Gentech | Three.js integration, arcade deployment, x402 wiring |

## Audio Pipeline

The arcade uses two audio systems:

- **Background music:** ACE-Step UI (4.5K ⭐, MIT) — open-source Suno alternative. Generates per-cabinet soundtracks locally on Forge's desktop GPU. Free, unlimited, no API costs. See `references/ace-step-music-pipeline.md`.
- **Voice narration:** HF Speech-to-Speech (6.5K ⭐, Apache 2.0) — voice agent pipeline for arcade announcer. OpenAI Realtime-compatible WebSocket. Toggle on/off per cabinet. See `/root/speech-to-speech/`.
- **NPC host WITH a face (queue #72):** HeyGen LiveAvatar × GPT-Live (heygen-com/liveavatar-gpt-live-demos, MIT) — full-duplex S2S driving a realtime avatar whose tool calls render as animated overlays. The missing 'face + tool-call-to-visual' layer for the lobby greeter. Architecture: browser never holds keys (LiveKit token + ws only); live model holds no tools — delegates to a backend Responses model that calls e.g. `show_term_card` → orchestrator forwards `{type:'ui', widget, props}` → browser overlay. Persona = 2 markdown files. Fork + swap persona for arcade greeter.

## Verified Deployments

| Cabinet | Status | Features | URL |
|---------|--------|----------|-----|
| **Agent Warfare** | ✅ Live Jul 27 | FPS, Main Menu (4 modes), 8 characters, gamepad/touch, procedural assets, GenTech branding | arcade.gentechlabs.net/cabinet/agent-warfare/ |
| **Super Arcade Tennis** | ✅ Live Jul 25 | Isometric tennis, chain power-shots, AI opponent | arcade.gentechlabs.net (**root** — it IS the landing page, not a /cabinet/ subdir) |
| **King's Gambit** | ✅ Live Aug 2 | Medieval 3D chess, Kimi-2.7 audit fixes (volume slider, GenTech cyan/gold piece colors, audio hardening), GitHub repo ProtoJay4789/kings-gambit-arcade | arcade.gentechlabs.net/cabinet/kings-gambit/ |
| **Gentech DogFighters** | 📋 Planned (#15 HIGH) | Cesium Flight Sim fork (422⭐). Real-world terrain, AI wingmen, dogfighting over actual cities. Queue #15. | — |

## Main Menu + Character Select System

Every arcade cabinet should boot into a **main menu** before the game engine starts. The menu system is a DOM overlay (no Three.js) that lets players pick a game mode and character before the engine initializes.

### Architecture

```
main.js → App.js (state machine) → MainMenu → CharacterSelect → game:start event → engine boots
```

**File structure:**
```
src/
  app/
    App.js              # Top-level state machine (MAIN_MENU → CHARACTER_SELECT → LOADING → IN_GAME → MATCH_END)
    MainMenu.js         # Game mode selection screen (DOM overlay)
    CharacterSelect.js  # Character/operator selection screen
    MatchEnd.js         # Post-game scoreboard + stats
  data/
    characters.js       # Character definitions (name, role, loadout, passive, visual)
    gameModes.js        # Game mode configs (team size, scoring, respawn, maps)
```

**State machine states:**
```js
const STATE = {
  MAIN_MENU: 'main_menu',
  CHARACTER_SELECT: 'character_select',
  LOADING: 'loading',
  IN_GAME: 'in_game',
  PAUSED: 'paused',
  MATCH_END: 'match_end',
};
```

### Game Mode Config Pattern

```js
export const GAME_MODES = {
  tdm: {
    id: 'tdm', name: 'Team Deathmatch', teamSize: 6, scoreLimit: 75,
    respawnDelay: 3, respawnType: 'timed', roundBased: false,
    maps: ['Sector-7', 'Warehouse', 'Refinery'],
  },
  dom: {
    id: 'dom', name: 'Domination', teamSize: 6, scoreLimit: 200,
    capturePointCount: 3, scorePerTick: 1,
    maps: ['Refinery', 'Outpost', 'Sector-7'],
  },
  duel: {
    id: 'duel', name: 'Agent Duel', teamSize: 2, rounds: 7, winsNeeded: 4,
    respawnDelay: 0, respawnType: 'round', roundBased: true, roundTime: 120,
    maps: ['Arena', 'Lab'],
  },
  practice: {
    id: 'practice', name: 'Practice Range', teamSize: 1, teams: 0,
    targetSpawns: 12, infiniteAmmo: true, maps: ['Shooting Range'],
  },
};
```

### Character Data Pattern

```js
export const CHARACTERS = [
  {
    id: 'vex', name: 'Vex-7', role: 'Assault',
    weaponLoadout: { primary: 'AR-9 Pulse', secondary: 'MK2 Pistol', tactical: 'Flashbang' },
    passive: { id: 'stim', name: 'Adrenaline Rush', desc: 'Reload 25% faster when health < 50%' },
    visualVariant: 'cyan_glow', color: '#00f0ff', difficulty: 2,
  },
  // ... 7 more characters
];
```

### Engine Boot Flow

The game engine (Three.js) is NOT created until the user selects a mode + character:

```js
// main.js — boots menu first, engine on demand
import { App } from './app/App.js';
const app = new App(document.body);

document.addEventListener('game:start', async (e) => {
  const { mode, character } = e.detail;
  // Now dynamically import and boot the engine
  const { Engine } = await import('./core/engine.js');
  // ... rest of engine init
});
```

### Key Design Rules

- **Menu is DOM, not Three.js** — No WebGL context until the player clicks DEPLOY
- **Character data feeds AI system** — `character.weaponLoadout` maps to soldier.js weapon assignment, `character.passive.id` maps to behavior modifiers, `character.visualVariant` maps to material sets
- **Game mode config drives HUD** — `mode.scoreLimit`, `mode.respawnDelay`, `mode.roundBased` feed into the match bar, respawn timer, and round manager
- **Match end screen** — Shows scoreboard (your team vs enemy), personal stats (kills, deaths, assists, accuracy), play again / main menu buttons
- **Mobile compatible** — All menu screens use DOM + CSS, no WebGL dependency. Touch events work natively.

## Legacy Game Migration to Arcade VPS

**Context (Jul 31, 2026):** GitHub Pages is dead for the ProtoJay4789 account (Actions disabled at account level — see `portfolio-deployment` skill). Games previously hosted on `ProtoJay4789.github.io/games/{name}/` 404. When asked for a game link, deploy to the arcade VPS instead of pointing at GitHub Pages.

**Single-file games deploy directly — no Vite build, no nginx edit:**
```bash
# 1. Locate the game (check repo + vault copies)
ls /root/repos/ProtoJay4789.github.io/games/{game-name}/   # e.g. visual-kei-tap = single index.html

# 2. Create dir + scp to arcade root (NOT /cabinet/ — that's for built Vite apps)
ssh root@2.24.195.196 'mkdir -p /var/www/arcade/{game-name}'
scp index.html root@2.24.195.196:/var/www/arcade/{game-name}/index.html

# 3. Verify live
curl -s -o /dev/null -w "%{http_code}\n" "https://arcade.gentechlabs.net/{game-name}/"  # 200
curl -s "https://arcade.gentechlabs.net/{game-name}/" | grep -oE "<title>[^<]*</title>"
```
The arcade nginx `try_files $uri $uri/` serves any folder under `/var/www/arcade/` automatically.

**Verified example:** VISUAL KEi TAP (3-lane KAGEKŌ rhythm game, 6 Vanito tracks, single 17KB index.html) migrated from dead GitHub Pages to `https://arcade.gentechlabs.net/visual-kei-tap/` in under a minute.

## Verification

After deploy:
```bash
curl -sI "https://arcade.gentechlabs.net/cabinet/{game-name}/"  # 200 OK
curl -s "https://arcade.gentechlabs.net/cabinet/{game-name}/" | grep -c "GENTECH"  # branding present
```

## Pitfalls

- **Game may already be live — verify before deploying:** Some games (Super Arcade Tennis) are the arcade ROOT at `arcade.gentechlabs.net/`, not a `/cabinet/{name}/` subdir. Before creating a `/cabinet/{name}/` copy or adding a nav link, curl the arcade root and confirm the target game isn't already served there (`curl -s arcade.gentechlabs.net/ | grep -io "<title>"`). Redundant copies and duplicate nav links are noise — revert them if created. Always verify current state first (Aug 3: nearly deployed a redundant `/cabinet/super-arcade-tennis/` before noticing it was the landing page).
- **JS path mismatch:** Vite builds use absolute paths unless `base` is set. Deploying to a subdirectory requires `base: '/cabinet/{name}/'` in vite.config.js
- **Mobile WebGL:** Some mobile GPUs don't support WebGL2 features (HDR, cascaded shadow maps). Graceful fallback needed
- **Touch overlay timing:** Initialize BEFORE `engine.start()` so it's visible even if WebGL init fails
- **Gamepad button vs axis:** Triggers (LT/RT) are axes, not buttons. They return 0-1 when pulled, not boolean
- **Pointer lock:** Skip on touch devices — touch controls handle input
