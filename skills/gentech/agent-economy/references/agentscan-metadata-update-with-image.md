# AgentScan Metadata Update with Image Integration

## Context

When updating AgentScan agent metadata to fix empty skills/domains display, we also added a profile picture for brand distinction.

## Problem

AgentScan was showing empty skills and domains for the Gentech agent because OASF metadata had skills/domains nested under `services` instead of at the top level.

## Solution Pattern

### 1. Prepare OASF Metadata with Top-Level Fields

OASF metadata must have `skills` and `domains` arrays at the **top level** (not just inside `services`).

**Correct structure:**
```json
{
  "name": "GenTech Labs",
  "description": "AI agent economy infrastructure...",
  "version": "1.0.0",
  "author": "ProtoJay4789",
  "skills": [/* 18 skills at top level */],
  "domains": [/* 14 domains at top level */],
  "image": "ipfs://<avatar-cid>",
  "services": [
    {
      "type": "x402",
      "name": "Rugcheck v2",
      "skills": [/* service-specific skills */],
      "domains": [/* service-specific domains */],
      "pricing": {...}
    }
  ]
}
```

**Key point:** AgentScan reads from top-level `skills` and `domains` fields, not from nested `services` entries.

### 2. Add Profile Picture via IPFS

**Step 1: Convert avatar to PNG (if SVG)**
```bash
# Using rsvg-convert
rsvg-convert /path/to/avatar.svg -o /tmp/avatar.png -w 400 -h 400

# Verify
file /tmp/avatar.png  # Should show: PNG image data, 400 x 400
```

**Step 2: Upload to Pinata via API**
```bash
curl -X POST "https://api.pinata.cloud/pinning/pinFileToIPFS" \
  -H "pinata_api_key: YOUR_API_KEY" \
  -H "pinata_secret_api_key: YOUR_SECRET" \
  -F "file=@/tmp/avatar.png"

# Response: {"IpfsHash": "QmVeoLNe7qK8UvFtiacsumCRfiaYjYnR9PEej3NAsFfg9M", "PinSize": 26174, "Name": "gentech-avatar.png"}
```

**Step 3: Add image field to metadata**
```json
{
  "image": "ipfs://QmVeoLNe7qK8UvFtiacsumCRfiaYjYnR9PEej3NAsFfg9M"
}
```

### 3. Upload Metadata to IPFS

**Using Pinata API:**
```bash
curl -X POST "https://api.pinata.cloud/pinning/pinJSONToIPFS" \
  -H "pinata_api_key: YOUR_API_KEY" \
  -H "pinata_secret_api_key: YOUR_SECRET" \
  -H "Content-Type: application/json" \
  -d "@/path/to/metadata.json"

# Response: {"IpfsHash": "QmTQiByteoJwjdWruhZFN4V4UkRb3Kfc8m4bwqeMDQ9SJy", "PinSize": 3601}
```

### 4. Update On-Chain via ERC-8004

**Using Python script (Avalanche):**
```python
# /root/vaults/gentech/scripts/update_erc8004_metadata.py
RPC_URL = "https://api.avax.network/ext/bc/C/rpc"
CONTRACT_ADDRESS = "0x8004A169FB4a3325136EB29fA0ceB6D2e539a432"
TOKEN_ID = 1770
NEW_URI = "ipfs://QmTQiByteoJwjdWruhZFN4V4UkRb3Kfc8m4bwqeMDQ9SJy"

python3 update_erc8004_metadata.py
# Prompts for private key securely (not saved to logs)
```

**Gas cost:** ~0.001 AVAX (~$0.01-0.02)

### 5. Verify Update

**Check AgentScan API:**
```bash
curl "https://agentscan.info/api/agents?search=Gentech"
```

**Expected within 24 hours:**
- ✅ Top-level skills populated (18 skills)
- ✅ Top-level domains populated (14 domains)
- ✅ Profile image displayed
- ✅ All services visible

## Completed Example (June 27, 2026)

**Metadata CID:** `QmTQiByteoJwjdWruhZFN4V4UkRb3Kfc8m4bwqeMDQ9SJy`
**Avatar CID:** `QmVeoLNe7qK8UvFtiacsumCRfiaYjYnR9PEej3NAsFfg9M`

**18 Skills:**
token-analysis, risk-scoring, rugpull-detection, security-audit, credit-scoring, reputation-analysis, agent-verification, travel-search, flight-research, hotel-search, destination-intelligence, social-scraping, content-analysis, trend-detection, media-intelligence, agent-identity, payment-processing, enforcement, audit-trails, erc-8004

**14 Domains:**
defi, security, blockchain, ai-agents, identity, finance, travel, data, tourism, social-media, content, analytics, infrastructure, payments

## Pitfalls

- **AgentScan is read-only:** No API endpoint to update metadata directly. All updates must go through on-chain `setTokenURI()`.
- **Top-level fields required:** Skills/domains at service level don't display. Always include top-level arrays.
- **Auto-sync delay:** AgentScan syncs within 24 hours, not instantly.
- **Private key security:** Never paste private keys in chat. Use local scripts with `getpass` for secure prompting.
- **Mobile UI limitations:** nft.storage upload paths may change. Use Pinata API from server for reliability.

## Tools Required

- `rsvg-convert` (librsvg) — SVG to PNG conversion
- `curl` — HTTP requests to Pinata API
- Python + `web3` — On-chain transaction signing
- Pinata API credentials (stored securely, not in code)