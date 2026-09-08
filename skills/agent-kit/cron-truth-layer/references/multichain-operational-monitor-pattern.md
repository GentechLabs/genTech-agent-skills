# Multichain Operational Monitor Pattern

## Overview

An operational monitor that verifies infrastructure health BEFORE touching financial data, then scans across multiple chains. Implemented in the revenue monitor v3 (`revenue-monitor.py` at `/root/.hermes/profiles/gentech/scripts/revenue-monitor.py`).

## Architecture

```
┌──────────────────────────┐
│ Service Health Check      │  ← 10 services, /health endpoints
│ (10/10 healthy)           │
└──────────┬───────────────┘
           ↓
┌──────────────────────────┐
│ Wallet per-chain scan     │  ← EVM RPC eth_getLogs + Solana RPC
│ Base / Avalanche /        │    getTokenAccountsByOwner + getTransaction
│ Solana (SPL USDC) / BNB   │
└──────────┬───────────────┘
           ↓
┌──────────────────────────┐
│ Self-transfer filter      │  ← Remove own-wallet internal moves
└──────────┬───────────────┘
           ↓
┌──────────────────────────┐
│ Label + Count             │  ← ALL external transfers = revenue
│ KNOWN_SENDERS enriches    │    (labels only, never filters)
└──────────┬───────────────┘
           ↓
┌──────────────────────────┐
│ Combined Report           │  ← Infra + portfolio + revenue + sources
└──────────────────────────┘
```

## Key Design Rules

### 1. Health-Check-First

Always ping services before scanning wallets. If the API gateway is down, x402 payments can't flow. Report infra readiness alongside financial metrics.

```python
health = check_service_health()
# ... report health ...
# THEN scan wallets
```

### 2. Label-Based Revenue (NEVER filter-based)

**🔴 WRONG — this silently discards all revenue when no senders are known:**
```python
KNOWN_SERVICES = {}  # empty = nothing matches
for tx in external:
    if tx["service"] != "unknown":  # never true
        count_revenue(tx)  # never called
```

**✅ CORRECT — count everything, label what you know:**
```python
KNOWN_SENDERS = {
    # "0xabc...def": "customer-name",  # optional labels
}
for tx in external:
    svc_name = KNOWN_SENDERS.get(tx["sender"].lower(), tx["chain"])
    total_revenue += tx["amount_usdc"]  # always count
```

Rule: ALL external USDC transfers to your wallet are revenue. The labeling dict is for enrichment only — it must never gate the counting.

### 3. Extensible Source Registry

When a new chain or payment type is added, the monitor should support it with minimal changes. Pattern:

```python
# ── Extensible Source Registry ──
# Add new sources here:
#   1. Add RPC URL + contract address
#   2. Add scan function or extend the chain loop
#   3. Add balance fetch to get_wallet_balances()
#   4. Add display row to format_report()
```

For Solana specifically (SPL USDC):
```python
def SCAN_SOL(wallet, since_sig, tracker):
    """Scan Solana for incoming SPL USDC transfers.
    
    Uses three RPC calls:
    1. getTokenAccountsByOwner → find USDC ATA + current balance
    2. getSignaturesForAddress → recent tx sigs for that ATA
    3. getTransaction → parse each sig for token balance changes
    
    Tracks: sol_usdc_balance (float), sol_usdc_ata (str), sol_tx_hashes (list)
    """
```

### 4. Multi-Source Balance Augmentation

The script covers on-chain balances directly via RPC. For wallet types that need MCP tools (Pay wallet, Q402 wallet), the cron job prompt tells the agent to call those tools and enrich the report:

```
## Step 2: Enrich with MCP Balance Checks
After the script runs, check:
- Pay wallet: mcp__pay__get_balance
- Q402 wallet: mcp__q402__q402_agentic_info
```

## Service Registration

Maintain a SERVICES dict with health endpoints:

```python
SERVICES = {
    "x402-gateway":     {"url": "https://api.gentechlabs.net", "health": "/health"},
    "landing-page":     {"url": "https://gentechlabs.net",    "health": "/health"},
    # ... all deployed services
}
```

## Multichain RPC Scanning

### EVM Chains (Base, Avalanche, BNB)

Track last scanned block per chain. Scan ERC-20 Transfer events for USDC:

```python
USDC_CONTRACTS = {
    "base":       "0x83358933e220DBD71d557b2c7c88c4b48eb88b43",
    "avalanche":  "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E",
    "bnb":        "0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d",
}
```

Use `eth_getLogs` with the Transfer event signature, filtering to `to` = our wallet address.

### Solana (SPL USDC)

Solana doesn't have event logs like EVM. Use:

1. `getTokenAccountsByOwner(wallet, {mint: USDC_MINT_SOL})` → find the Associated Token Account (ATA)
2. `getSignaturesForAddress(ATA, {limit: 15})` → recent transaction signatures
3. `getTransaction(sig)` with `jsonParsed` encoding → parse `preTokenBalances` vs `postTokenBalances`

Look for a positive balance change in the USDC token account belonging to our wallet. The `accountKeys[0]` is the fee payer (sender for simple transfers).

```python
USDC_MINT_SOL = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
SOL_RPC = "https://api.mainnet-beta.solana.com"
```

## Self-Transfer Filtering

Maintain a set of own wallet addresses (EVM + Solana):

```python
our_wallets = {WALLET_EVM.lower(), WALLET_SOL.lower()}
external = [t for t in new_transfers if t["sender"].lower() not in our_wallets]
```

This filters out LP deposits, internal rebalances, and other self-moves.

## Report Structure

```
💰 Revenue Monitor — GenTech Labs
📅 <timestamp>

🔌 Service Health
  🟢 x402-gateway — ok
  ...
  10/10 healthy

📊 Portfolio
  Total: $17.97
  SOL: 0.0729 ($5.54)
  SOL USDC: 5.00           ← new: Solana USDC balance
  AVAX: 0.0546
  ETH (Base): 0.000692
  BNB: 0.0081

💵 x402 Revenue
  Total earned: $0.0000 USDC
  By source:
    • base: $0.0000 (0 txs)   ← per-chain when no named senders

  ⏳ No payments yet — infrastructure ready

🔗 Balance Sources
  ✅ On-chain (Base/AVAX/BNB EVM) — scanned via RPC
  ✅ On-chain (Solana) — scanned via RPC
  ⏳ Pay wallet — checked by agent in cron prompt
  ⏳ Q402 wallet — checked by agent in cron prompt
  ⏳ Marketplace income — manual check per platform
📈 SOL: $75.96
```

## Infrastructure Readiness Signal

Even at $0 revenue, show readiness:

```
⏳ No payments yet — infrastructure ready, awaiting first x402 transaction
```

This signals that lack of revenue is a go-to-market gap, not an infrastructure gap.

## When to Use This Pattern

- Any cron job that reports financial metrics or operational health
- Multi-chain or multi-service deployments
- When you want a single cron report covering both "are we up?" and "are we making money?"
- When revenue sources may be added over time (extensible source registry)
