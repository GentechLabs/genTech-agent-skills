# Portfolio Design Strategy — Job-Seeking vs Founder Showcase

## Core Principle

The portfolio has **two modes** with completely different priorities. Know which one is active before touching the design.

| Dimension | Job-Seeking Mode | Founder Showcase Mode |
|-----------|-----------------|----------------------|
| **Primary audience** | Recruiters, hiring managers | Investors, partners, ecosystem |
| **Hero content** | Name + recognizable job title | Brand/company name + vision |
| **First section** | Skills (maps to job descriptions) | Timeline / origin story |
| **Project framing** | "I built this" (individual ownership) | "We built this" (team/ecosystem) |
| **CTA** | "Open to work" / Email / LinkedIn | "Try the demo" / GitHub |
| **Narrative** | Engineer who ships | Founder building the future |
| **Vanity metrics** | Frame with context (cost, impact) | Frame as proof of traction |

## Founder Showcase Mode (Current — Jordan's Portfolio)

### Hero Section
- **Name first** — "Jordan Jones" not "Jordan the ProtoJay"
- **Title reflects mission** — "Founder · Agent Economy Builder · GenTech Labs" (NOT "Senior Full-Stack Engineer" — Jordan has never had a dev job and that title doesn't represent him)
- **Skills in subtitle** — Solidity · TypeScript · Python · Rust · Go · Solana · EVM
- **Status banner** — "⚡ Building the Agent Economy"

### Section Order (Investor/Partner Skim Priority)
1. **About** — who you are, what you build, the mission
2. **Skills** — grouped by category (Languages, Blockchain & DeFi, Infrastructure & AI)
3. **Experience** — current role: Founder & Solo Engineer at GenTech Labs
4. **Featured Projects** — 6 projects with impact metrics, not just existence
5. **Open Source** — contributions with PR numbers
6. **Hackathons** — shows active builder
7. **Agent Infrastructure** — brief, shows depth
8. **Connect** — Email, LinkedIn, GitHub

### What NOT to Lead With
- Two-agent team as the hero (confuses people)
- Timeline as first content section (too narrative, not skimmable)
- "AAE Builder" or "V4" without explanation (doesn't map to anything recognizable)
- Vanity metrics without context ("32 cron jobs" → "32 cron jobs, $0.30/day operating cost")
- **"Senior Full-Stack Engineer"** — Jordan explicitly rejected this. He's never had a dev job. The title is dishonest and won't be respected. Use "Founder · Agent Economy Builder · GenTech Labs" instead.

### Project Card Anatomy (Consistent)
```
Card Title | Status Badge (Live/Building)
Tech Tags (3-4 max)
One-line description with impact
Impact metric (✅ 19/19 validator checks · First of its kind)
GitHub link
```

### CTA Placement
- **Hero section**: Email (primary), LinkedIn, GitHub — all visible without scrolling
- **Footer**: Repeat "Building the Agent Economy"

## Design Rules

### Color & Typography
- Dark theme (Inter font) — works for both modes
- Gradient header (blue→accent→purple) — distinctive but not distracting
- **No shimmer animations** on hero — decorative motion reads as garnish, not craft
- Body text: solid color, never gradient (WCAG contrast)
- Status dots: only if live/real — fake liveness erodes trust

### Information Architecture
- **One clear CTA per page** — what do you want the visitor to do?
- **No more than 8 sections** — 14+ sections = scroll fatigue
- **Sticky nav** if sections exceed 5
- **Merge overlapping metrics** — stats row + ops grid that overlap = confusion

### Content Rules
- "I built this" not "we built this" (job-seeking mode)
- Every project needs: what it does, what it's built with, what it proves
- Every stat needs context — "32 cron jobs" alone is noise
- No fake status indicators — if status dots aren't live, remove them

## When to Switch Modes

- **Job-seeking mode**: Default. Portfolio is for getting hired.
- **Founder mode**: Only when specifically targeting investors, grant applications, or ecosystem partnerships. Requires full redesign of hero, section order, and framing.

## Related

- Technical deployment: `portfolio-deployment` skill
- VPS deployment path: `/var/www/portfolio/` on `2.24.195.196`
- Live URL: `gentechlabs.net/portfolio/` (subdomain `portfolio.gentechlabs.net` needs DNS record)
