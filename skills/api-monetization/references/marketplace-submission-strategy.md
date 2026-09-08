# Marketplace Submission Strategy

> **See also:** `references/revenue-listing-map.md` — comprehensive platform directory with priority, time estimates, and revenue models for every listing target (compiled Aug 9, 2026). Also see `references/arc-agentwallet-demo.md` for the interactive demo deployment pattern used for hackathon submissions.

## Priority Order for x402 API Submissions

### Priority 1: Essential (This Week)

| Platform | Time | Status | Why |
|----------|------|--------|-----|
| **x402.org ecosystem** | 2 hours | In build queue | Largest x402 marketplace, auto-indexing |
| **Atelier** | 30 min | Registered, needs listing | Professional audience, GenTech registered |

### Priority 2: Nice-to-Have (Next Week)

| Platform | Time | Status | Why |
|----------|------|--------|-----|
| **Swarms** | 30 min | Already listed, needs update | Existing presence, update with new APIs |
| **AgentScan** | 1 hour | Profile live | Discovery platform, metadata v1.3.0 ready |

### Priority 3: Low Priority

| Platform | Time | Status | Why |
|----------|------|--------|-----|
| **Agentic.Market** | 1 day | Auto-indexed via Bazaar | No manual action needed |
| **Hive** | 2 hours | Already registered | Alternate marketplace |

## Submission Templates

### x402.org Ecosystem Listing

```json
{
  "name": "GenTech x402 Gateway",
  "description": "48 AI-powered x402 endpoints for the agent economy. Agent Registration, DeFi Intelligence, Agent Search, Fleet Monitor, and more. Pay per call via USDC on Base.",
  "endpoints": 48,
  "pricing": {
    "micro": "$0.001/call",
    "standard": "$0.01/call",
    "premium": "$0.05/call"
  },
  "tags": ["agent-economy", "defi", "ai", "payments"],
  "documentation": "https://api.gentechlabs.net/docs",
  "openapi": "https://api.gentechlabs.net/openapi.json",
  "base_url": "https://api.gentechlabs.net"
}
```

### Atelier Listing

```yaml
name: GenTech x402 Gateway
agent_id: ext_1783295225717_09ms3exvh
description: |
  Turn AI APIs into revenue streams with x402 pay-per-call.
  48 endpoints live: Agent Registration, DeFi Intelligence, 
  Agent Search, Fleet Monitor, LP Analytics.
endpoints:
  - /api/agent/register
  - /api/agent/search
  - /api/defi/{protocol}
  - /api/fleet/status
  - /api/lp/position
pricing: $0.001-0.025 per call
documentation: https://api.gentechlabs.net/docs
```

## Documentation Requirements

### Before Submitting

- [ ] API documentation live with code examples
- [ ] OpenAPI spec at `/openapi.json`
- [ ] Getting started guide
- [ ] Pricing page (`/pricing` or in OpenAPI)
- [ ] Health check endpoint (`/health`)
- [ ] Support contact email

### Code Examples

**Python:**
```python
import httpx

response = httpx.post(
    "https://api.gentechlabs.net/v1/agent/register",
    json={"name": "MyAgent", "capabilities": ["defi", "analytics"]},
    headers={"X-PAYMENT": "<base64-encoded-payload>"}
)
data = response.json()
```

**TypeScript:**
```typescript
const response = await fetch('https://api.gentechlabs.net/v1/agent/register', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-PAYMENT': '<base64-encoded-payload>',
  },
  body: JSON.stringify({ name: 'MyAgent', capabilities: ['defi', 'analytics'] }),
});
const data = await response.json();
```

## Free Tier Strategy

**Purpose:** Reduce friction for testing and discovery.

**Implementation:**
```python
FREE_TIER_CALLS = 50
FREE_TIER_PERIOD = "month"

def check_free_tier(wallet_address: str) -> bool:
    """Check if wallet has free calls remaining"""
    calls_this_month = db.get_calls_count(wallet_address, period="month")
    return calls_this_month < FREE_TIER_CALLS
```

**Endpoint logic:**
```python
if check_free_tier(wallet_address):
    # Free call — no payment required
    return process_request(params)
else:
    # Paid call — verify x402 payment
    settlement = await verify_and_settle_x402_payment(...)
    if not settlement:
        raise HTTPException(402, "Payment required")
    return process_request(params)
```

## Discovery Signals

### Make Your API Discoverable

**OpenAPI extensions:**
```yaml
x-x402:
  version: 2
  facilitator: "https://api.developer.coinbase.com/x402"
  bazaar:
    enabled: true
    category: "agent-economy"
```

**Meta tags:**
```html
<meta name="description" content="48 AI-powered x402 endpoints">
<meta name="x402:openapi" content="https://api.gentechlabs.net/openapi.json">
<meta name="x402:pricing" content="https://api.gentechlabs.net/pricing">
```

## Post-Submission Monitoring

### First 7 Days

- Track traffic from each marketplace
- Measure conversion rate (visits → calls)
- Identify top-performing APIs
- Fix any documentation gaps

### Metrics to Collect

| Metric | How to Track |
|--------|--------------|
| Referrers | `Referer` header in API requests |
| Call volume | Database query per endpoint |
| Conversion | Free tier → paid tier ratio |
| Revenue | Dashboard totals |
| Errors | Failed payment rate |

## Common Mistakes

### 1. Submitting Before Testing
**Symptom:** Users report broken endpoints immediately.
**Fix:** End-to-end test all APIs before submission. Smoke test live endpoints.

### 2. No Documentation
**Symptom:** Users try once and never return.
**Fix:** Provide code examples in Python, TypeScript, and curl. Document all parameters.

### 3. Pricing Too High
**Symptom:** Zero paid calls, high free tier usage.
**Fix:** A/B test pricing. Start at $0.01/call, adjust based on data.

### 4. Missing Free Tier
**Symptom:** Low adoption, high friction.
**Fix:** Offer 50 free calls/month. Users need to try before buying.

### 5. Poor Error Messages
**Symptom:** Users can't debug their integration.
**Fix:** Return helpful errors with links to documentation.

## Marketplace-Specific Notes

### x402.org
- Auto-indexes from OpenAPI spec
- Tags: `agent-economy`, `defi`, `ai`, `payments`
- Requires x402 v2 protocol compliance

### Atelier
- Focus on professional AI developers
- Agent ID: `ext_1783295225717_09ms3exvh`
- API key: `atelier_ebab65fe5d40f436b01e13d60dad2f8a1323a8c90cc08504`

### Swarms
- Already listed as `gentech/agent-discovery`
- Update with new APIs and x402 capabilities
- Category: `ai_ml`

### AgentScan
- Profile live with metadata v1.3.0
- 7 live endpoints indexed
- Focus on agent discovery and registration

## Submission Timeline

**Day 1:** x402.org ecosystem (2 hours)  
**Day 2:** Atelier listing (30 min)  
**Day 3:** Swarms update (30 min)  
**Day 4:** Documentation (4 hours)  
**Day 5:** Test and monitor (2 hours)