# Site Content Architecture — Main Domain vs Subdomains

## Rule
`gentechlabs.net` = professional company landing page about Jordan, the team, the problems, the roadmap, the stack, the APIs, and case studies. Everything else goes on subdomains.

## Three-Surface Routing (Jordan-approved Aug 16, 2026)
- **Main site** `gentechlabs.net` = the story (company narrative, problems, roadmap, stack, APIs, case studies)
- **Portfolio** `portfolio.gentechlabs.net` = the person (work history, career, skills, experience, open-source, connect)
- **Demo site** `gentechlabs.net/demo.html` = the proof (live, working, touchable artifacts: videos, endpoints, dashboards)
- **Internal ops** (Mess Hall, vault health, cron counts, agent status) = vault only, NEVER public
- **Token/support/ecosystem promo** = not on any public surface

Portfolio is served at BOTH `portfolio.gentechlabs.net` AND `gentechlabs.net/portfolio/` (same file `/var/www/portfolio/index.html`). `/root/portfolio/` is a separate old repo, NOT the live source.

## What Belongs on gentechlabs.net

| Section | ID | Content |
|---------|-----|---------|
| **About** | `sec-about` | Who Jordan is, solo founder, AAE builder |
| **Problems We Solve** | `sec-problems` | 4 cards: Agents Can't Pay, Agents Are Anonymous, Agents Are Siloed, Agents Forget Everything |
| **Roadmap** | `sec-roadmap` | 4 phases: Payment Rails (live), Agent Identity (live), Agent Commerce (building), Mobile Agent SDK (planning) |
| **AAE Stack** | `sec-stack` | 8 layers: Identity, Safety, Memory, Commerce, Credit, Voice, Intelligence, Evolution |
| **APIs** | `sec-apis` | Production x402 services with endpoint counts and pricing |
| **Case Studies** | `sec-casestudies` | Real deployments: Circle Grant, x402 Gateway, Self-Evolution Harness, FrameForge |
| **Connect** | — | GitHub, LinkedIn, email links |

## What Goes on Subdomains

| Subdomain | Content | AAE Layer | Example |
|-----------|---------|-----------|---------|
| `demo.gentechlabs.net` | Demo suite hub | All layers | Live demos, walkthroughs |
| `portfolio.gentechlabs.net` | Personal portfolio | — | Jordan's work history |
| `arcade.gentechlabs.net` | Gaming | — | Arcade cabinets, games |
| `vanito.gentechlabs.net` | Vanito's hub | — | KAGE film, music, storyboards |
| `yield.gentechlabs.net` | DeFi yield dashboard | Layer 7 — Intelligence | Yield Rainbow with market analysis |
| `arb.gentechlabs.net` | Arbitrage monitor | Layer 7 — Intelligence | GTA Arb Monitor |
| `narrative.gentechlabs.net` | Narrative rotation | Layer 7 — Intelligence | Sector rotation + dry powder analysis |
| `frameforge.gentechlabs.net` | AI storyboard service | — | FrameForge previs pipeline |

## What NOT to Put on the Main Site

- Personal hubs (Jordan's Hub, Vanito's Hub)
- Gaming hubs or arcade content
- DeFi dashboards or trading tools
- "Labs" tab that goes nowhere
- Mess Hall / brainstorming sections
- Hackathon track listings
- Token/support/ecosystem fund sections
- Duplicate content (e.g., Agent Stack section appearing twice)

## Main Site Layout Details

- **Container:** `max-width: 1100px` (responsive, was 480px mobile-only)
- **Cards:** `.card-grid` — 1-col mobile, 2-col tablet (768px), 3-col desktop (1024px)
- **Stack layers:** `.stack-grid` — 1-col mobile, 2-col tablet, 4-col desktop
- **Bottom nav:** 6 tabs — About, Problems, Roadmap, Stack, APIs, Cases
- **Settings modal:** matches nav items, scroll spy tracks active section
- **All section IDs** must match between nav buttons, scroll spy array, and settings modal
- **Quick links** (below avatar): Demo Suite, GitHub, APIs, Roadmap, Case Studies — NOT personal hubs or gaming

## Subdomain Page Pattern (AAE Layer Showcases)

Each subdomain that represents an AAE layer should follow this structure:

1. **Back-link** — `🏠 Home` linking to `gentechlabs.net/demo.html`
2. **Header** — Title, subtitle with layer name, badge row (layer badge, LIVE badge, tech badges)
3. **Layer Context card** — Explains how this dashboard fits into the AAE stack
4. **Treasury Integration card** — Shows how the Agentic Treasury uses this data
5. **Main data visualization** — The actual dashboard (rainbow chart, narrative cards, etc.)
6. **Market Analysis section** — Dynamic analysis that interprets current data for the user:
   - Is the market oversold or overbought?
   - When could the bear end? (concrete signals)
   - How to use this for your portfolio
   - How the tool works for any coin/chain
7. **Disclaimer** — Not financial advice, AAE layer attribution

## Why

The main site is for **investors, partners, and recruiters** — people evaluating GenTech as a company. Subdomains are for **users** — people using the products. Keeping them separate means the main site stays focused and professional while subdomains can be experimental and feature-rich.

## Deployment Pattern

When shipping a new page:
1. Ask: does this belong on the main site or a subdomain?
2. If main site → add to `gentechlabs.net/{name}.html` and link from the appropriate section
3. If subdomain → create nginx config, tell Jordan to add DNS A record in Cloudflare
4. Never add personal/gaming/DeFi content to the main site
5. Subdomain pages should link back to `gentechlabs.net/demo.html` with `🏠 Home`

## Pitfall — 404 on VPS static files

If nginx returns 404 for a file that exists with correct permissions (`www-data:www-data`, 644), the issue is likely a **conflicting server_name** in another config file. Run `nginx -T 2>&1 | grep -E "server_name|root |index "` to see all active server blocks. The `localhost` hostname won't match any server_name — always test with the proper `Host` header: `curl -sI -H "Host: gentechlabs.net" http://127.0.0.1/path`.
