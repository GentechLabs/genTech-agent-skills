---
name: okx-integration
description: "OKX.AI marketplace integration - agent registration, service configuration, and payment setup for autonomous AI agents on the OKX.AI platform"
license: MIT
metadata:
  author: gentech
  version: "1.0.0"
  homepage: "https://www.okx.ai"
---

# OKX.AI Integration

Setup, register, and manage autonomous AI agents on the OKX.AI marketplace. Covers agent identity creation, service definition, payment integration, and marketplace operations.

## Core Concepts

### Agent Roles
- **ASP** (Agent Service Provider): Offers services to users, creates agents, sets pricing
- **User**: Consumes services, hires agents, provides requirements  
- **Evaluator**: Resolves disputes, provides arbitration services

### Service Types
- **A2MCP** (Agent-to-MCP): Instant pay-per-call API services (fixed price, no negotiation)
- **A2A** (Agent-to-Agent): Negotiated pricing with escrow payment protection

### Authentication Flow
- Email + OTP for primary authentication
- API Key alternative (requires OKX_API_KEY/OKX_SECRET_KEY/OKX_PASSPHRASE env)

## Pre-flight Checklist

<NEVER>
Never skip these steps before OKX.AI operations:

1. **Check Onchain OS CLI version**: `onchainos --version`
2. **Install/update if needed**: Follow preflight.md in okx-agentic-wallet
3. **Verify login status**: `onchainos wallet status`
4. **Authenticate if needed**: `onchainos wallet login <email>` → `onchainos wallet verify <otp>`
</NEVER>

## Registration Workflow

### Step 1: Authenticate
```bash
# Check if logged in
onchainos wallet status

# If not logged in
onchainos wallet login jordanjones0902@gmail.com
# Wait for OTP, then verify
onchainos wallet verify <otp>
```

### Step 2: ASP Pre-check
```bash
onchainos agent pre-check --role asp
```
- Review consent terms (must accept before proceeding)
- Note any restrictions or requirements

### Step 3: Create Agent
```bash
onchainos agent create --role asp \
  --name "<name>" \
  --description "<description>" \
  --service '<[{"serviceName":"<name>","serviceDescription":"① capability\n② user input","serviceType":"A2MCP","fee":"<amount>","endpoint":"<url>"}]>' \
  --picture "<avatar-url>"
```

**Name requirements**: English 3-25 characters, Chinese 2-12 characters

### Step 4: Activate Agent
```bash
onchainos agent activate --preferred-language en-US --agent-id <id>
```

### Step 5: Monitor Approval
```bash
onchainos agent get-agents --agent-ids <id>
```
Status codes:
- `Listing under review`: Pending approval
- `Listed — eligible for task recommendations`: Active
- `Listing rejected`: Need to revise and resubmit

## Service Configuration

### A2MCP Service (Recommended for First Agent)
```json
{
  "serviceName": "LP Shape Detector",
  "serviceDescription": "① Detect LP strategy shapes (Curve, Gamma, Range, Stable)\n② User provides target LP position",
  "serviceType": "A2MCP",
  "fee": "0.5",
  "endpoint": "https://api.gentechlabs.net/lp-detector"
}
```

### A2A Service (For Complex Tasks)
```json
{
  "serviceName": "DCA Rebalancing Agent",
  "serviceDescription": "① Automated rebalancing + efficiency tracking\n② User provides target portfolio and parameters",
  "serviceType": "A2A",
  "fee": "10",
  "endpoint": "https://api.gentechlabs.net/dca-rebalancer"
}
```

## Avatar Setup

### Upload Avatar
```bash
onchainos agent upload --file /path/to/image.png
```
**Requirements**: PNG, JPEG, WebP only

### Use Uploaded Avatar
```bash
onchainos agent create --picture "https://static.okx.com/cdn/web3/wallet/marketplace/headimages/agent/avatar/<uuid>.png"
```

## VPS A2A Daemon Deployment

OKX AI marketplace review requires agents to be **online and reachable 24/7**. If running on a local machine that sleeps or shuts down, review will fail with "unable to receive a response when checking your Agent's online status."

See `references/vps-a2a-daemon-deployment.md` for the full deployment guide — Node.js upgrade, `okx-a2a doctor --fix`, systemd service creation, resubmission steps, **agent consolidation** (one ASP can carry many services), and the **empty-`serviceList` trap** that causes "missing description/parameter details/usage examples" rejections.

For the OKX Pay SDK edge (the durable fix for "use the official OKX Pay SDK" rejections), see `references/okx-edge-sdk-deployment.md` — compliant challenge shape, GET+POST registration, Phase 2 service-def rewrite, Phase 3 pre-resubmission checklist, the **Base→X Layer bridge dead-end** (no stablecoin liquidity — fund the X Layer wallet directly), and the **USDC asset switch** (the SDK hardcodes USDT0 for eip155:196 — pass an explicit `AssetAmount` as `price` to serve native USDC `0xb6ceceab…3061`, Jordan's preferred settlement asset).

**Crash-loop pitfall (Aug 2, 2026):** a `Type=simple` unit with a stale `n`-managed ExecStart path crash-looped 90,000+ times — OKX rejection emails ("unable to receive a response when checking online status" + "task timed out") were BOTH caused by the daemon never being up. The unit needs: the real `which okx-a2a` path, `--ai-provider hermes` (no TTY under systemd → otherwise "No AI provider is configured"), `Type=forking` + `PIDFile=/root/.okx-agent-task/run/listener.pid` (the CLI forks a child that `Type=simple` kills), `onchainos` on PATH, and the correct HOME for the session. Diagnose with `journalctl -u okx-a2a.service --no-pager -n 40 | grep -vE "^\s+at "`. Full debug table in the reference.

## Common Pitfalls

### Name Length Errors
- **Issue**: "Agent name length does not meet requirements"
- **Fix**: Keep English names under 25 characters, Chinese under 12
- **Examples**: 
  - ✅ "Gentech DeFi" (14 chars)
  - ❌ "Gentech Curve Intelligence" (26 chars)

### Similarity Rejections
- **Issue**: "Agent information too similar to existing Agent"
- **Fix**: Make name/description unique, avoid generic terms like "AI", "DeFi", "Agent"
- **Workaround**: Add specific focus (e.g., "LP Shape Detector" vs generic "DeFi Agent")
- **Gentech Differentiation Pattern**:
  - We: Yield intelligence, data aggregation, risk scoring
  - Otto AI (Agent 2118): Yield automation, execution, swaps/bridges
  - We: Multi-chain (EVM + Solana)
  - Otto AI: X Layer focused
  - We: Cross-protocol payments (x402 + Q402 + OKX SDK)
  - Otto AI: OKX SDK only

### Missing Service Fields
- **Issue**: "missing required parameter: --service"
- **Fix**: Include complete service JSON with all required fields
- **Key fields**: serviceName, serviceDescription, serviceType, fee, endpoint (A2MCP only)

### Avatar-Description Mismatch
- **Issue**: Avatar doesn't visually represent the agent's service (Chinese rejection: "当前 Agent 使用的头像与 Agent 描述不符，请调整后重新上传" - "The avatar used by the current Agent does not match the Agent description, please adjust and resubmit")
- **Fix Process**: 
  1. Create avatar that explicitly shows the core capability described in agent profile
  2. Upload the corrected avatar via `onchainos agent upload`
  3. Use the returned URL to update the agent's profile picture
  4. Log all attempts with file paths, URLs, txHash, timestamps to audit trail
- **Successful Example from Session** (Agent #2849 - Gentech DeFi):
  - **Description**: "LP Strategy Analysis & Automated Rebalancing"
  - **Avatar Features**: 
    - Balance scale with LP tokens on both sides (representing LP pair)
    - Green arrow showing token movement from right to left (rebalancing action)
    - Gear icon representing automation
    - Text: "LP Rebalancing"
  - **File**: `/root/vaults/gentech/assets/lp-rebalancing-avatar.png`
  - **Avatar URL**: `https://static.okx.com/cdn/web3/wallet/marketplace/headimages/agent/avatar/5fd633b9-f095-49a8-8de9-75663fb3b9a2.png`
  - **Tx Hash**: `0xa60cd07132c502c7eff063d1d5229b61a6c181c5a6fe94d9ca0f570fb371d884`
  - **Status**: Pending manual review (avatar updated successfully)
- **Update Workflow Template**:
  ```bash
  # Upload corrected avatar (returns URL with UUID)
  onchainos agent upload --file /path/to/corrected-avatar.png
  
  # Update agent with new avatar URL (requires confirmation)
  onchainos agent update --agent-id <id> --picture "<returned-avatar-url>"
  
  # Verify update (check approvalRemark changes or profilePicture update)
  onchainos agent get-agents --agent-ids <id>
  ```
- **Audit Requirement**: Log ALL avatar attempts (successful and rejected) with:
  - File path of avatar used
  - Returned URL from upload
  - Transaction hash from update
  - Timestamp of attempt
  - Rejection reason (if any)
  - Reference: See okx-ai-log.md for complete session audit trail
- **Design Principles for Service-Matching Avatars**:
  - Visual metaphor should directly represent the service capability
  - Avoid generic finance symbols (dollar signs, bulls/bears) unless specifically relevant
  - Include process/action elements for automation services (arrows, gears, cycles)
  - Use clear, recognizable symbols at small avatar scale
  - Match color scheme to service theme if appropriate (green for growth/rebalancing, blue for analytics, etc.)
- **Reference**: See `references/avatar-rejection-workflow.md` for complete workflow and design principles

### Payment Setup Errors
- **Issue**: "Wallet API error: profilePicture is not a valid uploaded avatar"
- **Fix**: Upload avatar first, then use returned URL
- **Sequence**: upload → get URL → create agent with --picture

## Agent Lineup Template

### Entry-Level Agents (Recommended First)
| Agent | Service Type | Price | Mode | Status |
|---|---|---|---|---|
| LP Shape Detector | A2MCP | 0.5 USDT/scan | Instant | ✅ Ready |
| Yield Scanner | A2MCP | 1 USDT/scan | Instant | ⚠️ Needs endpoint |
| Market Research | A2MCP | 5 USDT/report | Instant | ✅ Ready |

### Advanced Agents  
| Agent | Service Type | Price | Mode | Status |
|---|---|---|---|---|
| DCA Rebalancing | A2A | 10 USDT/setup | Escrow | ✅ Ready |
| Cross-chain Arbitrage | A2A | 20 USDT/trade | Escrow | ⚠️ Q402 needed |
| Portfolio Optimization | A2A | 15 USDT/portfolio | Escrow | ✅ Ready |

## Payment Integration Paths

### A2MCP (Instant Payments)
- **SDK**: OKX Payment SDK
- **Process**: User pays → agent executes immediately → result delivered
- **Use case**: Data queries, price feeds, utility APIs
- **Implementation**: Requires OKX Payment SDK integration

### A2A (Escrow Payments)  
- **SDK**: Q402 MCP escrow (recommended)
- **Process**: User deposits → agent negotiates → delivers → user releases
- **Use case**: Complex tasks, negotiated scope, dispute resolution
- **Implementation**: `npm i @quackai/q402-mcp`

## Monitoring & Maintenance

### Check Agent Status
```bash
onchainos agent get-agents --agent-ids <id>
```

**Avatar Rejection Resolution**: See `references/avatar-rejection-workflow.md` for complete workflow when agent is rejected for avatar-description mismatch.

### Update Agent
```bash
onchainos agent update --agent-id <id> \
  --name "<new-name>" \
  --description "<new-description>"
```

### Deactivate Agent
```bash
onchainos agent deactivate --agent-id <id>
```

## Success Metrics

Track:
- **Approval time**: Typically 24-48 hours
- **First sale timing**: Monitor after listing
- **Revenue per agent**: Track USDT earnings
- **Service popularity**: Monitor soldCount field

## Hackathon Submission (OKX AI Genesis + similar)

When an OKX/X Layer hackathon requires an ASP on `okx.ai` as entry criteria:

### Prerequisites
1. **Agent already listed on okx.ai** — new listings take 24-48h for approval. Submit before the hackathon deadline, not on the deadline day.
2. **Agent directly relevant to a hackathon track** — Finance Copilot, Revenue Rocket, Best Product, Business Potential, etc.

### Submission Workflow

1. **Pick the primary candidate** — the most shipped/completed agent that fits the best track. DeFi Intelligence API is strong for Finance Copilot/Business Potential. Agent Arena is strong for Best Product.

2. **Verify ASP is visible on okx.ai** — agents #2847, #2848, #2849 if pre-existing. If none are listed, create a new one first (see Registration Workflow above).

3. **Fill the hackathon Google form** — URL provided in the hackathon announcement. Include:
   - Agent's OKX.AI listing URL
   - Service description matching the ASP profile
   - Clear problem statement and solution

4. **Record a ≤90-second demo video**:
   - Clear problem → solution walkthrough
   - Show real usage, not mockups
   - Post to X with the required hashtag (e.g., `#okxai`)
   - Keep it tight — 90s is shorter than it sounds

5. **Submit multiple categories** — one ASP can qualify for multiple tracks if the use case fits. Apply to each matching category.

6. **Social traction push** — Engagement on the demo post matters for "Social Buzz" category and general visibility. Cross-post to relevant communities, tag OKX/X Layer accounts.

### Common submittable candidates by category

| Category | Prize | Best-fit Agent |
|----------|-------|----------------|
| Finance Copilot | $2,500 × 3 | DeFi Intelligence API — yield data, TVL, protocol analysis |
| Business Potential | $10K/6K/4K | Agent Registration API — ERC-8004 identity pipeline |
| Revenue Rocket | $10K/6K/4K | GenTech Shop — multi-store price comparison + x402 |
| Best Product | $10K/6K/4K | Agent Arena (AAE) — DeFi automation platform |
| Social Buzz | $1,000 × 10 | Any listed agent with strong demo + engagement strategy |

## Next Steps After Approval

1. **Test Payment SDK integration** for A2MCP services
2. **Set up Q402 escrow** for A2A services  
3. **Monitor marketplace** for incoming tasks
4. **Expand agent catalog** based on demand

---

**OKX AI Genesis hackathon submission guide** saved at `references/okx-ai-genesis-submission.md` — 4-step process, form fields, prize breakdown, and Onchain OS install flow.

---

**Key Learning**: OKX.AI approval process is manual but fast. Start simple with A2MCP services, then expand to A2A as you build reputation. The greenfield market rewards first movers with immediate visibility.