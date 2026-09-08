# Multi-Provider Aggregator Pattern

Build a new paid API that aggregates results from multiple external providers and charges per call via x402 payments.

## When to Use

**Use when:**
- Multiple data sources need to be combined into one API
- Users want flexibility to choose providers or use all
- You want to monetize data aggregation (not just wrap existing tools)
- Each provider has different costs/quality trade-offs

**Contrast with `productize-as-paid-api.md`:**
- `productize-as-paid-api.md`: Wrap existing internal CLI/tool → paid API (mechanical wrapping)
- This pattern: Build NEW aggregation service → paid API (architectural design from scratch)

## Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ HTTP GET + X-PAYMENT header (on retry)
       ▼
┌──────────────────────────────────────┐
│         FastAPI Application          │
│  - x402 payment middleware          │
│  - Provider routing logic           │
│  - Error handling & CORS            │
└──────┬───────────────────────────────┘
       │
       ├─► Verify + settle via facilitator (/verify + /settle)
       │
       ├─► Provider A API (e.g., Exa)
       │
       ├─► Provider B API (e.g., Grok)
       │
       ├─► Provider C API (e.g., Surf)
       │
       └─► Combine results → Return JSON
```

> **Note:** Payment verification uses a facilitator's `/verify` + `/settle` endpoints, NOT "Bazaar" (which is discovery only). See `references/x402-facilitator-payment-flow.md` for the correct architecture.

## Endpoint Design

### Free Endpoint (No payment required)
- **GET /status** - API health, pricing, provider availability
- Use for health checks, monitoring, API discovery

### Paid Endpoints (x402 token required)

All paid endpoints share the same authentication pattern:

```python
@app.post("/search/provider-a", response_model=SearchResponse)
async def provider_a_search(
    request: ProviderARequest,
    x_402_token: str = Header(..., alias="x-402-token")
):
    # Verify payment first
    if not await verify_x402_payment(x_402_token, PRICING["provider_a"]):
        raise HTTPException(status_code=402, detail="Payment verification failed")
    
    # Execute search
    results = await search_provider_a(request.query, request.numResults)
    
    return SearchResponse(
        query=request.query,
        results=results,
        provider="provider_a",
        timestamp=datetime.utcnow().isoformat(),
        cost_usd=str(PRICING["provider_a"])
    )
```

### Aggregated Endpoint

```python
@app.post("/search", response_model=SearchResponse)
async def aggregated_search(
    request: SearchRequest,
    x_402_token: str = Header(..., alias="x-402-token")
):
    # Verify payment (highest cost)
    if not await verify_x402_payment(x_402_token, PRICING["aggregated"]):
        raise HTTPException(status_code=402, detail="Payment verification failed")
    
    all_results = []
    
    # Search across all requested providers
    for provider in request.providers:
        if provider == "provider_a":
            results = await search_provider_a(request.query, request.numResults)
            all_results.extend(results)
        elif provider == "provider_b":
            results = await search_provider_b(request.query, request.numResults)
            all_results.extend(results)
        elif provider == "provider_c":
            results = await search_provider_c(request.query, request.numResults)
            all_results.extend(results)
    
    return SearchResponse(
        query=request.query,
        results=all_results[:request.numResults * len(request.providers)],
        provider="aggregated",
        timestamp=datetime.utcnow().isoformat(),
        cost_usd=str(PRICING["aggregated"])
    )
```

## Tiered Pricing Model

| Endpoint | Cost | Use Case |
|----------|------|----------|
| POST /search | $0.025 | All providers (comprehensive) |
| POST /search/provider-a | $0.01 | Provider A only |
| POST /search/provider-b | $0.01 | Provider B only |
| POST /search/provider-c | $0.005 | Provider C only (budget) |

**Why tiered?**
- Different providers have different costs
- Users pay for what they use
- Aggregated search = convenience premium
- Cheapest provider attracts price-sensitive users

## Provider Integration Pattern

Each provider has its own async function:

```python
async def search_provider_a(query: str, num_results: int = 10) -> List[SearchResult]:
    """Search using Provider A API"""
    if not PROVIDER_A_API_KEY:
        return []
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.provider-a.com/search",
                headers={"Authorization": f"Bearer {PROVIDER_A_API_KEY}"},
                json={
                    "query": query,
                    "numResults": num_results,
                    "useAutoprompt": True
                },
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get("results", []):
                results.append(SearchResult(
                    title=item.get("title", "No title"),
                    url=item.get("url", ""),
                    snippet=item.get("text", ""),
                    score=item.get("score"),
                    source="provider_a"
                ))
            return results
    except Exception as e:
        print(f"Provider A search error: {e}")
        return []
```

**Key patterns:**
- Always check for API key before calling
- Use httpx.AsyncClient for async HTTP
- Set reasonable timeout (30s for external APIs)
- Normalize results to common schema
- Handle API errors gracefully (return empty list, don't crash)

## Data Model Pattern

### Pydantic Models for Type Safety

```python
from pydantic import BaseModel, Field
from typing import List, Optional
from decimal import Decimal

class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str
    score: Optional[float] = None
    source: str

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    provider: str
    timestamp: str
    cost_usd: str

class StatusResponse(BaseModel):
    status: str
    version: str
    timestamp: str
    pricing: Dict[str, str]
    providers: Dict[str, Any]
```

### Request Models with Validation

```python
class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query")
    providers: Optional[List[str]] = Field(
        default=["provider_a", "provider_b", "provider_c"],
        description="Search providers to use"
    )
    numResults: Optional[int] = Field(
        default=10,
        description="Number of results",
        ge=1,  # Minimum 1
        le=20  # Maximum 20
    )
```

## Testing Pattern

### Mock-Based Testing (No external API calls)

```python
# Define mock results
MOCK_PROVIDER_A_RESULTS = [
    {
        "title": "Example Result 1",
        "url": "https://example.com/1",
        "snippet": "This is a sample result",
        "score": 0.95,
        "source": "provider_a"
    }
]

# Use pytest-asyncio with AsyncMock
@pytest.mark.asyncio
@patch('server.search_provider_a', new_callable=AsyncMock)
@patch('payment.verify_x402_payment', new_callable=AsyncMock)
async def test_provider_a_search_success(mock_payment, mock_search):
    mock_payment.return_value = True
    mock_search.return_value = MOCK_PROVIDER_A_RESULTS
    
    response = client.post(
        "/search/provider-a",
        json={"query": "test query"},
        headers={"x-402-token": "valid_token"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["provider"] == "provider_a"
    assert len(data["results"]) == 1
```

**Test coverage:**
- Success path (valid payment, results returned)
- Failure path (invalid payment → 402)
- Schema validation (wrong types, missing fields)
- Payment flow (verify payment called with correct amount)

## Common Pitfalls

### 1. Test Mock Field Mismatch
**Symptom:** Tests fail with validation errors
```
ValidationError: Field required, input_value={'title': '...', 'url': '...'}
```
**Cause:** Mock data missing required fields (e.g., `snippet`, `source`)
**Fix:** Ensure mock results match Pydantic model exactly

### 2. Aggregated Search Parameter Mapping
**Symptom:** `AttributeError: 'SearchRequest' object has no attribute 'maxResults'`
**Cause:** Different request models use different field names
**Fix:** Use consistent parameter names in aggregated loop

### 3. Silent Payment Verification Failures
**Symptom:** All requests return 402 but no error logs
**Cause:** Bazaar API unreachable or invalid API key, but error swallowed
**Fix:** Always log errors before returning False

## Shipped Instance

**Agent Search API** (Jul 2026)
- 5 endpoints (/status, /search, /search/exa, /search/grok, /search/surf)
- 3 providers (Exa, Grok, Surf)
- Pricing: $0.005-0.025/call
- 8/8 tests passing
- Deployed to https://search.gentechlabs.net
- Revenue target: $1,200-18,000/year

**Built in:** Single session, FastAPI + httpx + Pydantic, x402 payment integration, Cloudflare Workers deployment