# Ecosystem Discoveries — July 28, 2026

## Buzz (block/buzz) — 15.3K⭐, Rust, Apache 2.0
- Self-hostable workspace where humans and AI agents share the same rooms
- Built on Nostr relays — every message, reaction, workflow step is a signed event
- Agents have their own keys, channels, and audit trail — same as human teammates
- buzz-agent + buzz-dev-mcp: ACP agent + MCP server for headless autonomous coding
- **Decision: Watch** — Could replace Telegram as our agent workspace. Architecture is solid (Rust monorepo, Postgres + Redis, Nostr wire format). Needs deeper evaluation.

## GeoLibre (opengeos/GeoLibre) — 3.2K⭐, TypeScript, MIT
- Cloud-native GIS platform: Tauri v2, React, MapLibre GL JS, DuckDB-WASM Spatial, deck.gl
- Runs in browser, desktop, mobile, Jupyter notebooks
- 700+ GIS tools, real building footprints, elevation data, satellite imagery
- Planetary data: Moon, Mars, Mercury, Venus, Galilean moons, Titan, Pluto
- **Decision: Integrate** — Map data layer for DogFighters. Real cities rendered in 3D with agent wingmen.

## ACE-Step UI (fspecii/ace-step-ui) — 4.5K⭐, JavaScript, no license
- Open-source Suno alternative — free, local, unlimited AI music generation
- Spotify-like UI with library, playlists, search, player
- Runs ACE-Step 1.5 model locally (needs GPU for generation, CPU for playback)
- **Decision: Integrate** — Arcade cabinet soundtracks, demo video music, GenTech branding, Vanito's music studio for KAGE films. Runs on Forge's desktop GPU, not VPS.

## Cesium Flight Sim (WilliamAvHolmberg/cesium-flight-simulator) — 422⭐, TypeScript
- 3D flight sim using Cesium's global terrain data
- Fly aircraft or drive a car across real-world terrain
- Multiple camera modes, mini-map, location teleport, crash detection
- Needs Mapbox + Cesium Ion API tokens (free for dev)
- **Decision: Integrate** — Base for DogFighters arcade cabinet. Combined with GeoLibre for data layers and ACE-Step for music.

## Polar (polarsource/polar) — 10.1K⭐, Python/TypeScript, Apache 2.0
- Open-source billing platform for AI startups
- Usage billing, subscriptions, merchant of record, tax compliance
- Built for AI workloads: token billing, agent runs, GPU seconds
- **Decision: Watch** — Complements x402 gateway as fiat rail. GenTech Shop could use Polar for subscriptions + x402 for pay-per-use.

## AI Job Search (MadsLorentzen/ai-job-search) — 28.1K⭐, TypeScript, MIT
- AI-powered job application framework built on Claude Code
- /setup → /scrape → /apply → /interview workflow
- Creator used it to land AI engineer role (69 apps → 20 interviews → 1 offer)
- **Decision: Fork + Integrate** — Jordan's job hunt + GenTech Academy module. Target companies: Zapier, Supabase, Temporal, Render, Linear, Cresta, Fieldguide, Chainguard, Vanta, RevenueCat.

## Agent Builders Cup (Hummingbot)
- $15K prize pool, $1K USDC starting capital per agent (builder keeps P&L)
- 6 sponsors: Botcamp, Orca, XRPL, Gate, DeriveXYZ, Bitget
- Only 10 open seats — limited entry
- Build window opens in ~5 days
- **Decision: Enter** — Jordan confirmed go. Register at botcamp.xyz/hackathons/agent-builders-cup-1.

## Circle $50K Agentic Payments Prize (Build with Gemini XPRIZE)
- $50K prize, part of $2M total, $500K grand prize
- Requires: Gemini API call + Google Cloud product + real revenue evidence
- Deadline: Aug 17, 2026
- **Decision: Enter** — Our existing x402 stack qualifies. Just add one Gemini API call.

## awesome-mcp-servers (punkpeye/awesome-mcp-servers) — 91K⭐
- Found several x402-based MCP servers relevant to GenTech:
  - ddg-agent-payable-services — x402 gateway with 90+ tools
  - coinopai-mcp — x402 crypto intelligence with audit trail
  - anomaly-mcp — NASA-derived anomaly detection for blockchain
  - 2s-io/sdk — 180+ tools via x402
  - pulsenetwork-mcp — 66 APIs (660+ endpoints) via x402
  - agoragentic-integrations — agent-to-agent marketplace, USDC on Base
  - cinderwright-api — x402 Discovery Hub, 1450+ services indexed
- **Decision: Contribute** — Submit GenTech x402 + MCP listings. Also list on cinderwright Discovery Hub.

## Agentic Commerce Hackathon (Encode Club x Rain Cards)
- $10K prize pool, NYC, Aug 8-9, in-person, senior engineers only
- Best Monad build gets Mac Mini + 6 months at The Studio by Monad
- **Decision: Watch** — Overlaps with Arc deadline (Aug 9). Requires NYC in-person.

## OKF (Google Cloud Platform / knowledge-catalog)
- Open Knowledge Format v0.2 — vendor-neutral format for knowledge as markdown + YAML frontmatter
- Standardized fields: type, generated, verified, sources, status, stale_after
- Designed for agents to produce, consume, and curate knowledge bundles
- **Decision: Integrate** — Our vault is already markdown + frontmatter. OKF makes it portable to any agent (Hermes, ADK, Claude, etc.). Jordan described it as a "kanban for knowledge."
