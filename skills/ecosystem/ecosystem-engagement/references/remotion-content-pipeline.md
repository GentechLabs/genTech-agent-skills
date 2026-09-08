# Remotion + ElevenLabs Content Pipeline

GenTech Labs' automated content production pipeline: vault data → Remotion video → ElevenLabs narration → ready to post.

## Pipeline Flow

```
Vault (build queue, PR portfolio)
  → content-pipeline.py (generates script)
    → Remotion Agent Skills (generates motion video)
      → elevenlabs-narrate.py (voiceover)
        → X/Twitter post
```

## Scripts

| Script | Location | What it does |
|--------|----------|-------------|
| `content-pipeline.py` | `scripts/content-pipeline.py` | Reads build queue + PR portfolio → generates video script |
| `elevenlabs-narrate.py` | `scripts/elevenlabs-narrate.py` | Takes script → ElevenLabs TTS → MP3 narration |

## Remotion Skills Installed

10 skills from `remotion-dev/skills` (4k⭐, 458 forks):
- `remotion-create` — scaffold new video projects
- `remotion-render` — render videos and stills
- `remotion-captions` — subtitle/caption handling
- `remotion-best-practices` — video design guidance
- `remotion-markup` — React markup for video
- `remotion-interactivity` — studio editing support
- `remotion-docs` — documentation reference
- `remotion-saas` — SaaS deployment patterns
- `remotion-upgrade` — version migration
- `mediabunny` — multimedia handling

## ElevenLabs Narration

Uses Jordan's ElevenLabs API key (Creator plan, $22/mo). Key stored at:
`/root/.hermes/profiles/gentech/config/elevenlabs.env`

**Default voice:** `YoYo` (cloned, ID: `xQbwtCgzouB5QdCSd0Z7`) — smooth, informal, for content pipeline narration.

**Other available cloned voices:**
- Steve Harvey (`Rxk9LQxvNFEplpjjsjuN`) — expressive, preacher cadence
- Vanito (`eMQtaKLvw87ksRqmQVpS`) — gaming content
- Gentech-Mako (`TkEJnN27nf5BsX1xwrLB`) — deep, wise
- IvanOnTech (`ToA54GQ3jBRB2zt0fBXj`)
- Christel (x2: `kb3G0tkYW7pEGVlHEdu5`, `R8Nmfj7gteuYpqJBPrMD`)
- D-Mob (`n2icbiwmCen7udwM65GS`)
- Gentech-Iroh (`NqA7ncEPGGt1nDbCrDex`)
- Alex (professional, `XaEUesE01wKIKaa0xI0h`)
- Alexei (professional, `NQJnREzQtnAHHZnia0tY`)

**IMPORTANT:** Use ElevenLabs API directly for cloned voices. BlockRun speech tool only works with premade voices — cloned voices return 502 from BlockRun gateway.

## Usage

```bash
# Step 1: Generate script from build data
python3 scripts/content-pipeline.py --preview

# Step 2: Create Remotion video
npx remotion studio --no-open

# Step 3: Narrate with ElevenLabs
ELEVENLABS_API_KEY=$(grep ELEVENLABS_API_KEY /root/.hermes/profiles/gentech/config/elevenlabs.env | cut -d= -f2) \
  python3 scripts/elevenlabs-narrate.py

# Step 4: Render final video
npx remotion render
```

## Content Ideas

- PR merged showcase (x402 Foundation #2905, Dexter-DAO Zod validation)
- Ecosystem contribution highlights
- Game updates (Visual Kei Tap)
- Build queue progress reports
- Hackathon submission demos

## Pitfalls

- ElevenLabs API key must be exported as env var (not in .env sourcing)
- Remotion requires Node.js ≥18 (we have v22.11.0)
- Video rendering is GPU-intensive — use Forge's desktop for final renders
- Script truncation: ElevenLabs has character limits (~5000 chars for TTS)
