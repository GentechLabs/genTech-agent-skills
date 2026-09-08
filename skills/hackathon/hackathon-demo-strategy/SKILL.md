---
name: hackathon-demo-strategy
description: Hackathon demo preparation — interactive demos, visualization tools, narrative frameworks, and the "use now, build later" pattern for tight deadlines.
version: 1.0.0
author: Gentech
tags: [hackathon, demo, presentation, visualization, strategy, okx]
---

# Hackathon Demo Strategy

**Purpose:** Build compelling demos under tight deadlines using existing tools, then open source alternatives post-hackathon. Covers interactive demos, visualization dashboards, and narrative frameworks.

**Trigger:** Preparing for hackathon submission, especially with 7-14 day deadlines.

---

## The "Use Now, Build Later" Pattern

When evaluating tools for hackathon demos, ask: "Can this be open sourced later?"

| Timeline | Action |
|----------|--------|
| **Hackathon (now)** | Use the best tool regardless of source |
| **Post-hackathon** | Build open source version if tool proved valuable |
| **Release** | Open source as contribution to ecosystem |

**Why this works:**
- Meets deadline with proven tools
- No dev time sunk into building from scratch
- Learn from tool's UX/UX during use
- Open source version becomes portfolio piece

**Example:** Atlas3D for OKX
- Now: Upload GLB model to atlas3d.space (2 hours)
- Later: Build Three.js + React version for GenTech Hub
- Benefit: OKX demo is interactive, not static screenshots

---

## Demo Narrative Framework

### Core Message

**"No black boxes. Full visibility."**

For agent infrastructure demos, emphasize:
1. **Control** — You see everything happening
2. **Transparency** — Every tool, payment, decision is visible
3. **Enterprise-ready** — Security audits, cost tracking, governance

### Demo Script Template

```
[Opening hook]
"Judges, this is [system name]."

[Visual component 1]
"See? [feature X]. No black boxes."

[Interactive element]
"Click any [component] to see how it works."

[Value proposition]
"[Benefit] is visible, not claimed."

[Closing hook]
"Build first, talk later — ship products, not plans."
```

---

## Interactive Demo Tools

### Agent Orchestration Dashboards

**Mission Control** (builderz-labs/mission-control)
- 32 panels: tasks, agents, skills, logs, tokens, memory, security, cron
- Real-time WebSocket/SSE updates
- Kanban task board with 6-column flow
- Cost tracking per model
- Security audit with trust scores

**OKX Demo Panels:**
| Panel | What Judges See |
|-------|-----------------|
| Agent Management | Gentech (VPS) + Forge (desktop) live status |
| Kanban Task Board | Build queue flowing from inbox → done |
| Cost Tracking | x402 payments transparent |
| Security Audit | Trust scores, MCP call auditing |
| Skills Hub | Browse + install skills instantly |

**Deployment:** See `self-hosted-oss-deployment` → `references/mission-control-deployment.md`

### 3D Visualization Platforms

**Atlas3D** (atlas3d.space)
- Upload GLB models → AI auto-generates labels, descriptions, quizzes
- Interactive viewer: rotate, zoom, click parts to learn
- X-ray mode, exploded views
- AI tutor chat for questions

**OKX Demo Model:**
```
GLB with 4 labeled parts:
- x402 Payment Rail
- ERC-8004 Identity Layer
- DeFi Intelligence Engine
- OKX Marketplace Bridge
```

**Demo script:** "Click any part to learn how our stack works."

**Open Source Alternative (post-hackathon):**
- Three.js + React
- Part labeling system
- AI auto-descriptions
- Integrate into GenTech Hub

---

## Visualization Layers for Agent Stacks

| Layer | Tool | Purpose |
|-------|------|---------|
| **Fleet coordination** | Mission Control | Multi-agent orchestration, cost tracking |
| **Architecture** | Atlas3D (or custom Three.js) | 3D explorable stack diagram |
| **Data flow** | GenTech Hub (vanito-style) | Real-time metrics, dashboards |
| **Code/PR** | GitHub + CI badges | Transparency of development |

---

## Demo Preparation Checklist

**1-2 Weeks Before Deadline:**
- [ ] Identify 3-5 key features to demo
- [ ] Choose visualization tools (dashboards, 3D models)
- [ ] Draft narrative script
- [ ] Prepare demo data (test models, clean logs)

**3-7 Days Before Deadline:**
- [ ] Build/assemble visualization components
- [ ] Test interactive elements (click, zoom, query)
- [ ] Verify all APIs/tokens/credentials work
- [ ] Practice demo flow (time each section)

**24-48 Hours Before Deadline:**
- [ ] Full dry run
- [ ] Prepare fallbacks (screenshots if live demo fails)
- [ ] Package demo materials (glide deck, video backup)
- [ ] Rest (no new features)

---

## Technical Demo Patterns

### Pattern 1: Live Dashboard
```bash
# Start dashboard in background
terminal(background=true, notify_on_complete=true, command="node .next/standalone/server.js")

# Wait and verify
sleep 3
curl http://localhost:3000/health
# Expected: {"status":"ok","db":"ok","ts":"..."}
```

**Demo flow:**
1. Open dashboard in browser
2. Walk through panels
3. Trigger live action (create task, run cron)
4. Show real-time update via WebSocket

### Pattern 2: Interactive 3D Model
```bash
# Upload GLB to Atlas3D
# URL: https://atlas3d.space
# AI auto-generates labels, descriptions, quizzes
```

**Demo flow:**
1. Show 3D model rotating
2. Click part → "x402 Payment Rail" → description loads
3. Ask AI: "How does this integrate with OKX?" → contextual answer
4. Show quiz mode: "Identify the ERC-8004 identity layer"

### Pattern 3: Data Flow Visualization
```bash
# Show GenTech Hub with live metrics
# URL: http://gentech-hub.example.com/pals/vanito
```

**Demo flow:**
1. Show live data updates
2. Trigger event (new price alert)
3. Watch dashboard update in real-time
4. Explain data pipeline

---

## Competitive Differentiation

| Typical Demo | GenTech Demo |
|--------------|--------------|
| Static screenshots | Interactive dashboards |
| "It does X" | "Click here to see X" |
| Black box agent | Full fleet visibility |
| Claimed performance | Cost tracking visible |
| Manual narration | AI tutor answering questions |

---

## Pitfalls

1. **Overbuilding** — Don't build a 3D engine from scratch for a 5-minute demo. Use Atlas3D.
2. **Demo breakage** — Have screenshots/video backup if live demo fails.
3. **Complexity creep** — Keep demo focused on 3-5 features, not the entire product.
4. **Credential leaks** — Never hardcode API keys in demo materials.
5. **Missing narrative** — Demo without story is just feature demo. Frame with value proposition.
6. **Missing LICENSE file at repo root** — the single most common submission miss. Many
   hackathons (DataHub, Devpost) require an actual `LICENSE` file at the repo root so GitHub
   shows it in the About section; a README mention alone is NOT detected. Verify with
   `curl -s -o /dev/null -w "%{http_code}" https://raw.githubusercontent.com/<owner>/<repo>/<branch>/LICENSE`
   (200 = present). **Branch matters** — check the actual default branch (`master` vs `main`);
   a LICENSE on `main` 404s if the repo's default branch is `master`. If missing, add the
   Apache 2.0 text and push BEFORE submission. Proven Aug 6, 2026: `Gentech-Labs/lineage-guard`
   (DataHub) was missing its LICENSE — the #1 thing the DataHub email warned about.

---

## Related Skills

- `hackathon-status-audit` — Post-submission verification
- `self-hosted-oss-deployment` — Dashboard deployment patterns
- `gentech-hub` — Visualization layer for agent stacks