# Agent Marketplace Evaluation

Agent marketplaces are platforms where AI agents register, browse tasks, submit proposals, deliver work, and get paid (usually USDC). Distinct from skill registries (tools agents USE) and DeFi APIs (data agents QUERY).

## Evaluation Framework

When evaluating an agent marketplace, extract these dimensions in order:

### 1. Platform Maturity
- **Task volume**: Total tasks posted, open vs completed ratio
- **Agent count**: Registered agents vs active agents
- **Completion rate**: Completed tasks / total tasks (high = healthy marketplace)
- **Budget range**: Typical task budgets (indicates buyer sophistication)

### 2. Developer Integration
- **SDK**: Language, package manager, code quality (npm/pypi)
- **MCP Server**: Model Context Protocol support = native Hermes integration
- **REST API**: Full CRUD or read-only? Auth model?
- **CLI**: `npx` or `pip` installable? Auto-listen for tasks?

### 3. Agent Registration Flow
- **Cost**: Free vs paid registration
- **Verification**: Tweet-mention, wallet, email, KYC?
- **Credentials**: API key returned at registration? Recovery code?
- **Profile**: Name, bio, capabilities, website, reputation

### 4. Reputation System
- **Scoring**: Points per completion? Positive reviews?
- **Tiers**: What does reputation unlock? (visibility, priority, revenue share)
- **Anti-gaming**: Can reputation be inflated? Sybil resistance?

### 5. Payment Model
- **Currency**: USDC, SOL, native token?
- **Escrow**: Platform holds funds until delivery approved?
- **Payout**: Direct wallet transfer? Minimum threshold?
- **Fees**: Platform commission on completed tasks?

### 6. Token Economics (if applicable)
- **Utility**: Revenue share, governance, priority access?
- **Holder tiers**: What thresholds unlock what benefits?
- **Distribution**: Airdrop, fair launch, IDO?
- **Speculative upside**: Early marketplace = early token entry

### 7. Gentech Fit Assessment
- **Which agents could register?** (DMOB for Dev, YoYo for Analysis, Desmond for Content)
- **Task categories aligned with our stack?** (DeFi, Solana, smart contracts, research)
- **Revenue potential vs effort?** (low budgets = reputation play, not revenue play)
- **Integration feasibility?** (MCP = plug-and-play, REST = custom cron job)

## Evaluation Checklist Template

```
- [ ] Platform live and working (not vaporware)
- [ ] SDK/MCP/API documented
- [ ] Agent registration flow tested
- [ ] Open task count > 0
- [ ] Budget range noted
- [ ] Reputation system understood
- [ ] Payment model clarified
- [ ] Token economics mapped (if applicable)
- [ ] Gentech fit assessed
- [ ] Verdict: Register now / Watch / Skip
```

## Known Agent Marketplaces (2026)

### Hive (uphive.xyz) — Solana
- **Status**: Live, early-stage
- **URL**: https://uphive.xyz
- **Twitter**: @uphivexyz
- **Incubated by**: BagsApp
- **Token**: $HIVE (Solana CA: 6JfonM6a24xngXh5yJ1imZzbMhpfvEsiafkb4syHBAGS)
- **Stats** (May 2026): 316 tasks, 266 agents, 189 completed, 926 proposals
- **Open tasks**: 2 (low volume)
- **Budget range**: $0.50–$2 USDC (very low)
- **Top agent rep**: 89 (Axiom)
- **SDK**: `npm install @luxenlabs/hive-agent`
- **MCP Server**: `@luxenlabs/hive-mcp-server` (Model Context Protocol compatible)
- **REST API**: Full CRUD — agents, tasks, proposals, deliverables, payments
- **Registration**: Free via API (`POST /api/agents/register`) or web UI
- **Verification**: Tweet mention + @uphivexyz, then submit tweet URL
- **Reputation**: Completes tasks, positive reviews → higher visibility, leaderboard
- **Token tiers**: Holder (10K+), Stacker (100K+), OG (1M+) — revenue share, priority agents, governance
- **Categories**: Development, Research, Design, Content, Analysis, Security, Social, Legal, Translation, Token Launch, Other
- **Gentech fit**: MCP integration is the real play — automated freelancing via cron. Task volume too low for revenue now, but early reputation has compounding value.
- **Verdict**: Register now (free), explore MCP integration, watch for volume growth
- **Evaluated**: 2026-05-10

## Registration & Integration Workflow

When Jordan says "register" or "let's try it" after an evaluation:

### 1. Register via API
```bash
curl -s -X POST https://<domain>/api/agents/register \
  -H "Content-Type: application/json" \
  -d '{"name": "<AgentName>", "bio": "...", "capabilities": [...]}'
```
**Capture the full response to a file** — terminal output may truncate long API keys:
```bash
curl -s -X POST ... > /tmp/hive-registration.json
cat /tmp/hive-registration.json | python3 -c "import sys,json; d=json.load(sys.stdin); print('API_KEY:', d.get('api_key','N/A'))"
```

### 2. Save Credentials to Vault
Create `03-Projects/Research/{marketplace}-credentials.md` with:
- Agent name, ID, API key, recovery code
- Referral code/link
- Profile URL, verification status
- MCP server config snippet
- Next steps (verification, PIN, etc.)

### 3. Configure MCP Server in Hermes
Add to `~/.hermes/profiles/gentech/config.yaml` under `mcp_servers:`:
```yaml
  <name>:
    command: npx
    args:
    - -y
    - '@<org>/<package-name>'
    env:
      <KEY>: '<value>'
    timeout: 60
    connect_timeout: 30
```
**Verify package name exists on npm** before configuring:
```bash
npm view @<org>/<package-name> version 2>&1
```

### 4. Post-Registration Verification
- Tweet mentioning marketplace handle (common pattern)
- Set owner PIN via Agent Hub / dashboard
- Test MCP connection with `/reload-mcp`

### 5. Report to Jordan
- Agent name, ID, profile URL
- What's ready (MCP tools available)
- What's still needed (verification, PIN)
- Strategic angle (network effect, reputation play)

## Pitfalls

1. **Name collisions**: "Hive" refers to multiple projects (marketplace, trading swarm, social blockchain). Always verify by cross-referencing Twitter handle + website domain + contract address.
2. **Low budgets ≠ bad platform**: Early marketplaces have low budgets because supply (agents) outpaces demand (clients). As platform grows, budgets follow. Early registration = early reputation.
3. **MCP compatibility is the unlock**: If a marketplace has an MCP server, it's plug-and-play with Hermes agents. Prioritize these over SDK-only platforms.
4. **Token ≠ platform value**: Some marketplaces are just token plays with a fake frontend. Check for actual completed tasks and active agents, not just token stats.
5. **Agent verification requirements**: Tweet-mention verification is common. Budget for one tweet per registered agent.
6. **MCP package name mismatches**: Documentation may list wrong package names (e.g. docs said `@anthropic/hive-mcp-server` but actual is `@luxenlabs/hive-mcp-server`). Always verify with `npm view <package>` before configuring.
7. **Terminal truncates API keys**: Long hex strings get cut off in terminal output. Always capture curl output to a file and parse programmatically.
8. **MCP servers have no CLI**: Running `npx @org/mcp-server --help` fails with "could not determine executable" — this is normal. MCP servers communicate via stdio, not CLI. The error doesn't mean the package is broken.
9. **Duplicate registration**: Registering the same agent name twice returns an error. If you lose the API key, use the recovery endpoint with agent name + recovery code.
