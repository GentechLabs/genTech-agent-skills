# Mock → Real Data Upgrade Path for Revenue APIs

**Session:** July 5, 2026
**Use case:** Hackathon deadline pressure → ship with mock data first, upgrade later

## Pattern

**Problem:** You need to ship revenue APIs for a hackathon submission (deadline: Jul 17), but third-party data source integration is incomplete or blocked.

**Solution:** Ship APIs with mock data, document upgrade path, upgrade post-hackathon.

## Why This Works

| Aspect | Mock Data | Real Data |
|--------|-----------|-----------|
| **Payment flow** | ✅ Still works (x402 payments independent of data) | ✅ Same |
| **Revenue tracking** | ✅ Still works (PaymentLogger) | ✅ Same |
| **Endpoint structure** | ✅ Same | ✅ Same |
| **Data quality** | ⚠️ Sample data | ✅ Live data |

**Key insight:** x402 payments don't care about data source. Payment verification → settlement → delivery is identical whether data is mock or real.

## Upgrade Path Documentation Template

Create a dedicated document for each API that needs real data:

```markdown
# [API Name] Data Integration Upgrade Path

**Created:** [Date]
**Status:** Mock data shipped, real data pending

## Current State

- Endpoint: `http://localhost:PORT`
- Data source: Mock data (X sample items)
- Revenue: x402 payments functional
- Testing: All tests passing

## Blockers

- [ ] BlockRun API key not saved (see `00-HQ/data-integration-upgrade-path.md`)
- [ ] Provider website timing out

## Upgrade Plan

### Phase 1: Account Setup
1. Create fresh account with provider
2. Generate API key
3. Store securely in vault (not git)
4. Document in `11-Mess Hall/[provider]-api-key-rotation.md`

### Phase 2: Configure Integration
1. Add API key to `.env`
2. Update `README.md` with API key setup
3. Document key rotation in `skills/api-key-rotation.md`

### Phase 3: Wire Real Data
1. Replace mock data with real API calls
2. Add error handling for provider failures
3. Test with real data

### Phase 4: Deploy
1. Reload API processes
2. Verify endpoints return real data
3. Update documentation

## Backup Plans

**Option A: Alternative providers**
- [Provider A]: [Implementation notes]
- [Provider B]: [Implementation notes]

**Option B: Hybrid approach**
- Keep mock mode for demo purposes
- Add `real_data_available: bool` flag
- Allow users to toggle modes

## Reference

- Build queue item #[number]: [Hackathon name]
- Related skill: `api-monetization`
- Related doc: `00-HQ/data-integration-upgrade-path.md`
```

## Implementation Example

**Agent Search API (port 8003) — shipped Jul 5, 2026**

### Mock data in production:

```python
# main.py (current state)
MOCK_AGENTS = [
    AgentProfile(
        agent_id="gentech-marketplace-bot",
        name="GenTech Marketplace Bot",
        description="Automated market making and arbitrage for DeFi protocols",
        category="defi",
        capabilities=["arbitrage", "market-making", "liquidity-provision"],
        rating=4.8,
        total_jobs=1250,
        success_rate=97.5,
        pricing={"base_fee": "0.01 ETH", "success_fee": "5%"},
        blockchain="ethereum",
        owner_address="0x742d35Cc6634C0532925a3b844Bc9e7595f8bE21",
        verified=True
    ),
    # ... 4 more mock agents
]
```

### Real data integration (planned):

```python
# main.py (after upgrade)
import httpx
import os

BLOCKRUN_API_KEY = os.getenv("BLOCKRUN_API_KEY")
BLOCKRUN_BASE_URL = "https://api.blockrun.io"

async def fetch_agents_from_blockrun(
    category: str | None = None,
    blockchain: str | None = None
) -> List[AgentProfile]:
    """Fetch real agent profiles from BlockRun registry"""
    if not BLOCKRUN_API_KEY:
        return MOCK_AGENTS  # Fallback to mock
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BLOCKRUN_BASE_URL}/v1/agents",
                params={"category": category, "blockchain": blockchain},
                headers={"Authorization": f"Bearer {BLOCKRUN_API_KEY}"},
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            
            return [parse_blockrun_agent(agent) for agent in data["agents"]]
    except Exception as e:
        print(f"BlockRun API error: {e}")
        return MOCK_AGENTS  # Graceful fallback
```

## Benefits for Hackathons

| Benefit | Description |
|---------|-------------|
| **Faster shipping** | Don't wait for API key approvals or provider availability |
| **Demos work** | x402 payment flow demonstrates concept perfectly |
| **Full revenue path** | Monetization architecture is complete |
| **Upgrade is additive** | Adding real data doesn't break anything |
| **No risk** | Mock data serves as fallback if provider fails |

## When to Use

✅ **Use when:**
- Hackathon deadline < 2 weeks away
- External API key not yet available
- Provider website/API temporarily unavailable
- Want to demonstrate payment flow first, data quality second

❌ **Don't use when:**
- API is data-dependent (e.g., price tracking, real-time analytics)
- Mock data would mislead users
- You have plenty of time before deadline
- Real data source is easy to integrate (< 2 hours)

## Testing Strategy

Keep tests passing through upgrade:

```python
# test_api.py

# Mock-based tests (continue working with real data)
@pytest.mark.asyncio
@patch('main.fetch_agents_from_blockrun')
async def test_search_agents_success(mock_fetch):
    mock_fetch.return_value = MOCK_AGENTS
    
    response = client.get("/api/v1/agents/search?category=defi")
    
    assert response.status_code == 200
    assert response.json()["total"] > 0

# Real-data tests (add after upgrade)
@pytest.mark.skipif(
    not os.getenv("BLOCKRUN_API_KEY"),
    reason="BLOCKRUN_API_KEY not set"
)
@pytest.mark.asyncio
async def test_search_agents_real_data():
    # Actually call BlockRun
    response = client.get("/api/v1/agents/search?category=defi")
    
    assert response.status_code == 200
    # Verify data is from BlockRun (check agent IDs, verification status)
```

## Shipped Examples

| API | Status | Mock → Real Plan |
|-----|--------|------------------|
| Agent Search (8003) | ✅ Live with mock | Documented in `00-HQ/data-integration-upgrade-path.md` |
| DeFi Intelligence (8002) | ✅ Live with mock | Same upgrade path |
| Agent Registration (8001) | ✅ Live with real data | Direct blockchain calls, no mock needed |

## Related

- Skill: `api-monetization` — Full x402 payment integration patterns
- Skill: `gentech-ops` — Deploy-and-verify workflow
- Doc: `00-HQ/data-integration-upgrade-path.md` — BlockRun-specific plan
- Doc: `00-HQ/build-queue.md` — OKX hackathon status (Item #0)