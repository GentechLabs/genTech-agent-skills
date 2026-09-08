# Competitive Analysis Framework

Template for proving GenTech AgentKit competitiveness against Arsenal AI, GOAT AgentKit, OKX.AI, and other agent platforms.

---

## Verification Checklist

Before claiming competitive status, verify each API is live:

```bash
# 1. Health check
curl -s https://<api-url>/health | jq .
# Expected: status: "ok"

# 2. x402 discovery
curl -s https://<api-url>/.well-known/x402 | jq .
# Expected: x402Version: 2, accepts array, bazaar object

# 3. Test 402 payment challenge
curl -s https://<api-url>/<paid-endpoint> -w "\nHTTP Status: %{http_code}\n"
# Expected: HTTP 402 with PAYMENT-REQUIRED header
```

---

## Competitive Comparison Table Template

| Feature | GenTech | Competitor A | Competitor B | Competitor C |
|---------|---------|--------------|--------------|--------------|
| Live Paid Endpoints | # | # | # | # |
| x402 v2 Support | ✅/❌ | ✅/❌ | ✅/❌ | ✅/❌ |
| Multichain | # chains | # chains | # chains | # chains |
| Unique Feature | ✅ | ❌ | ❌ | ❌ |
| Lowest Price | $X.XXX | $X.XXX | $X.XXX | $X.XXX |

**Fill in:**
- Exact endpoint counts
- Supported chains
- **Unique features** — what no one else has
- Actual prices from your pricing endpoints

---

## Revenue Modeling Framework

For each API, model three scenarios:

### Agent Registration API Example

| Scenario | Calls/Day | Avg Price | Yearly Revenue | Calculation |
|----------|-----------|-----------|----------------|-------------|
| Conservative | 50 | $0.0075 | $912 | 50 × $0.0075 × 365 |
| Realistic | 500 | $0.0075 | $9,125 | 500 × $0.0075 × 365 |
| Aggressive | 2,000 | $0.0075 | $36,500 | 2,000 × $0.0075 × 365 |

**Average price formula:**
```
Sum(endpoint_prices) / num_endpoints
```

**Yearly revenue formula:**
```
calls_per_day × avg_price × 365
```

---

## Amazon Exit Path Calculator

**Target:** $72,000/year (Phase 2 complete)

| API | Scenario | Revenue | % of Target | Cumulative |
|-----|----------|---------|-------------|------------|
| Agent Registration | Aggressive | $36,500 | 50% | 50% |
| + DeFi Intelligence | Realistic | $58,400 | 81% | 81% |
| + Agent Search | Realistic | $69,350 | 96% | 96% |
| + Fleet Monitor | Realistic | $85,775 | 119% | 119% |

**Formula:**
```
cumulative_percent = (cumulative_revenue / 72000) × 100
```

---

## Document Pattern

Create two documents for each competitive audit:

### 1. `competitive-portfolio.md` (Quick Status)

```markdown
# GenTech Labs — Competitive API Portfolio

> **Goal**: Prove GenTech AgentKit is competitive with live, working APIs

---

## 🚀 LIVE APIs

### API Name ✅
**URL**: https://api-url.com

| Feature | Status |
|---------|--------|
| Health | ✅ Healthy |
| x402 v2 | ✅ Compliant |
| Networks | ✅ X chains |
| Endpoints | ✅ X paid + Y free |

**Endpoints**:
| Path | Price | Description |
|------|-------|-------------|

**Revenue**: $X-$X/yr

---

## 📊 Competitive Analysis

[Quick comparison table]

---

## 💰 Revenue Projection

[Revenue table by API]

---

*Last Updated: DATE*
```

### 2. `competitive-audit-<date>.md` (Full Analysis)

```markdown
# 🏆 GenTech Competitive Audit — AgentKit API Portfolio

**Date**: YYYY-MM-DD
**Objective**: Prove GenTech AgentKit is competitive against [competitors]

---

## Executive Summary

[Comparison table with metrics]

**Key Finding**: [What makes us unique]

---

## 📦 Live APIs

[Detailed breakdown of each live API]

**Revenue Potential**: [Table with scenarios]

**Competitive Edge**: [What competitors don't have]

---

## 🔬 Competitive Deep Dives

[Section-by-section comparison vs each major competitor]

**Verdict**: [Why we win]

---

## 📊 Revenue Analysis

[Revenue breakdown by API]

### Path to Amazon Exit

[Exit path calculator]

---

## 🎯 Action Items

[Prioritized list of next steps]

---

## 🏅 Competitive Advantages

[Numbered list of unique strengths]

---

## 📝 Conclusion

[Summary of competitive position]
```

---

## Pitfalls

- **Never claim competitive without live verification** — Run health + x402 discovery checks first
- **Cloudflare deployments need CLOUDFLARE_API_TOKEN** — Without it, only temp URLs work (gentech-xxx.typical-erigeron.workers.dev)
- **Revenue models are projections, not guarantees** — Always show bands (conservative/realistic/aggressive)
- **Competitor counts change** — Arsenal may add APIs, new platforms emerge — re-audit quarterly
- **Unique features must be provably unique** — Verify competitors don't offer similar capabilities via docs/research

---

## Research Sources

- Arsenal AI: https://arsenal.ai
- GOAT AgentKit: https://goat-agentkit.dev
- OKX.AI: https://okx.ai/agents
- x402 Bazaar: https://bazaar.social
- Cloudflare Workers: https://developers.cloudflare.com/workers

---

*Created: July 4, 2026*
*Last Updated: July 4, 2026*