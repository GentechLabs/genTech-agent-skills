# Measuring a paginated x402 catalog index

Use this recipe when you need to know whether GenTech resources are actually present
in a catalog like CDP Bazaar or PayAI, not just whether the endpoint is valid.

## The honest measurement loop

A catalog index is paginated. Do not trust a single request, a large `limit`, or a
`next` pointer that may be absent.

```python
import json
import urllib.request

BASE = "https://api.cdp.coinbase.com/platform/v2/x402/discovery/resources"


def get(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "gentech-labs-index-check/1.0",
        "Accept": "application/json",
    })
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode())


def walk():
    doc = get(f"{BASE}?limit=1000&offset=0")
    declared = doc.get("pagination", {}).get("total")
    rows, prev_first = [], None
    off = 0
    while off < (declared or 0):
        d = get(f"{BASE}?limit=1000&offset={off}")
        batch = d.get("items") or d.get("resources") or []
        if not batch:
            break
        marker = json.dumps(batch[0], sort_keys=True)
        if marker == prev_first:
            raise RuntimeError("pagination not advancing")
        prev_first = marker
        rows += batch
        off += len(batch)
    return rows, declared
```

## Match your catalog to the index

The index stores URLs. Your catalog stores service metadata. Match on literal path
segments after stripping placeholders.

```python
import re


def literal_segments(u):
    u = re.sub(r"https?://[^/]+", "", str(u))
    u = re.sub(r"[?].*$", "", u)
    segs = []
    for s in u.split("/"):
        s = s.strip()
        if not s or s.startswith(":") or (s.startswith("{") and s.endswith("}")):
            continue
        segs.append(s.lower())
    return segs


def is_indexed(service_endpoint, indexed_urls):
    service_segs = literal_segments(service_endpoint)
    for u in indexed_urls:
        if service_segs and service_segs == literal_segments(u)[:len(service_segs)]:
            return True
    return False
```

## Three wrong instruments that report a working route as missing

1. **Trusting a large `limit`.** The server may cap `limit` to 1,000. A 1,000-row
   sample from a 22,000-row index is 4.5% of the data. Always reconcile against
   `pagination.total`.
2. **Matching service names to URLs.** A service named `market_intelligence` may be
   indexed under `/v1/market/price/ETH/`. Names are labels; URLs are ground truth.
3. **Matching paths literally with placeholders.** The catalog may write
   `/v1/defi/lp/{address}` while the index stores `/v1/defi/lp/:address`. Strip
   placeholders before comparing.

## Per-resource status checks

PayAI exposes a listing-status endpoint:

```bash
curl -s "https://facilitator.payai.network/discovery/listing-status?resource=<url>"
```

CDP does not expose an equivalent per-resource status endpoint; the full index walk
is required.

## When to settle vs. when to verify

| Platform | Trigger | Cost |
|---|---|---|
| CDP Bazaar | Settled payment per resource | ~$0.02/resource |
| PayAI GET resources | Verified payload, no settle | $0 |
| Dexter | Real settlement (pending verification for tiny amounts) | Real USDC |

Never spend autonomously. Money movement is Jordan-owned regardless of amount.
