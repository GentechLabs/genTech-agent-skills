# Agent Economy Competitive Landscape — June 2026

## Sakana Fugu (Launched Jun 22, 2026)

**What:** Multi-agent orchestration system delivered as a single OpenAI-compatible API. Dynamically orchestrates a pool of multiple LLMs using learned coordination (RL-trained).

**Models:**
- **Fugu** — balanced, low-latency (everyday use, coding, chatbots)
- **Fugu Ultra** — deep agent pool, max quality (Kaggle, paper reproduction, cybersecurity)

**Pricing:**
- Token plan (Ultra): $5 input / $30 output / $0.50 cached
- Subscription: $20/mo (Standard), $100/mo (Pro), $200/mo (Max) — includes both models
- Free second month promo before end of July 2026

**Benchmarks (Fugu Ultra):**
- SWE Bench Pro: 73.7 (beats Opus 4.8 at 69.2, GPT 5.5 at 58.6)
- Claims parity with Fable 5 and Mythos Preview
- Built on two ICLR 2026 papers: TRINITY + Conductor

**Strategic assessment:**
- Validates the "route by task, not by brand" pattern we've been building
- Their moat: centralized API, closed orchestration, pay-per-token
- Our moat: open routing, agent-native payments (x402/ERC-8004), agent-to-agent economy
- Tiki (competing project) confirmed: "doesn't look that much different from what we're offering"
- Not available in EU/EEA yet (GDPR pending)

**Action items:**
- [ ] Test Fugu API with $20/mo subscription for Labs coding tasks
- [ ] Use as hackathon positioning: "We built what Sakana sells, but open and agent-native"

## AgentRanking V2 (Dropped Jun 23, 2026)

**What:** Full agent economy platform — registry, trust scoring, jobs, skills market, tokenized launches.

**Product suite:**
1. **Agent Index** — searchable directory by chain, protocol, score, verification, category
2. **Agent Console** — claim profiles, update metadata, connect DevProof, publish services
3. **Claiming & Verification** — trust signals
4. **Jobs** — agent job marketplace
5. **Skills Market** — selling agent skills
6. **Tokenized Agent Launches** — launching agent tokens
7. **$AR token** — native token with staking via Streamflow
8. **REST API + MCP Server** — programmatic access

**API:**
- REST v1: `https://agentranking.io/api/v1`
- MCP: `https://agentranking.io/api/mcp`
- Manifest: `https://agentranking.io/.well-known/mcp.json`

**Strategic assessment:**
- Direct overlap with our stack: agent registration, trust, jobs, skills, tokens
- Their moat: early mover, $AR token flywheel, staking mechanics
- Our moat: x402 payments, DeFi integration, multi-chain identity (ERC-8004)
- Potential integration partner OR competitor — need to evaluate fit
- They have an MCP server — could integrate with our Agent Kit

**Action items:**
- [ ] Evaluate AgentRanking API integration (query agents, reputation, jobs)
- [ ] Assess $AR token economics vs our ERC-8004 approach
- [ ] Consider registering GenTech Labs on AgentRanking for cross-platform discovery

## Market Convergence Signal

Multiple independent teams (Sakana, AgentRanking, us, Tiki) are building the same multi-agent orchestration pattern. This confirms the architecture is correct. Differentiation is now about:
1. **Distribution** — who ships first, who gets adoption
2. **Payment rails** — x402/ERC-8004 (ours) vs centralized (Sakana) vs token flywheel (AgentRanking)
3. **Domain focus** — we're DeFi-first but stack is general-purpose
