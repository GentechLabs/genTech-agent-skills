# Weekly API Marketplace Scanner

## Purpose
Recurring cron job (weekly) that audits our marketplace visibility across all x402 API directories and applies the three-way routing decision to findings.

## Scan Workflow

### 1. Check Pay-Skills Catalog
The canonical catalog is at `mcp__pay__list_catalog`. Search for "gentech" — if not found, our APIs aren't listed.

**Current status (Jul 29):** Only `rugcheck-v2-api` has a complete PAY.md + openapi.json. PR #190 to solana-foundation/pay-skills is mergeable but awaiting human review. 0 GenTech providers in the live catalog.

### 2. Check AgentScan
Registered as agent #1770. Profile is incomplete. Platform still shows "Launching Soon."

### 3. Check Virtuals ACP
Not registered. 2K+ agents, ACP v2.0 since Apr 2026. BNB Chain lists it as a core tool.

### 4. Check Other Marketplaces
Reference the canonical audit at `10-Labs/marketplace-audit.md` for full status of:
- OKX AI (registered, rejected — needs A2A node resubmission)
- Swarms (listed, stale — needs manual update by Jordan)
- Atelier (registered, needs profile update)
- x402 Bazaar (auto-indexed, no action needed)
- Awesome lists (3 merged, 9 open PRs)
- Agentic.Market / Coinbase Bazaar (not listed)

### 5. Discover New Marketplaces
Search for emerging x402 directories and agent marketplaces:
```bash
web_search(query="x402 API marketplace directory 2026 agent monetization")
web_search(query="new AI agent marketplace 2026 registration open")
```

### 6. Apply Three-Way Routing

Every finding gets classified:

| Finding Type | Action | Destination |
|-------------|--------|-------------|
| **Small fix** (stale vault data, config, documentation) | Fix immediately | Vault file update |
| **Big task** (new marketplace listing, API registration, PR updates) | Add to Build Queue | `scripts/build_queue.json` + `10-Labs/build-queue.md` |
| **Human-only** (wallet login, account creation, DNS changes) | Add to Orchestrator List | `HQ/jordan-queue.md` |

### 7. Update Vault

Files to create/update each scan:
- **Canonical audit**: `10-Labs/marketplace-audit.md` — update date, add new findings
- **Build queue**: `scripts/build_queue.json` (canonical) + `10-Labs/build-queue.md` (human-readable summary)
- **Orchestrator list**: `HQ/jordan-queue.md` — add new Jordan action items

### 8. Generate Report

Follow the canonical output format:
```
📡 API Marketplace Scout — [Date]

### ✅ Fixed Automatically
- [Small fixes made]

### 📋 Added to Build Queue
- [Big tasks for Labs]

### 🎯 Added to Orchestrator List
- [Jordan's action items]

### 🔍 Key Findings
- [Notable status changes, gaps, discoveries]
```

## API Inventory — PAY.md Coverage

Out of 60+ API directories in `10-Labs/`, only **1** has PAY.md + openapi.json:

| API Directory | PAY.md | openapi.json | Listed on Pay-Skills? |
|---------------|--------|-------------|----------------------|
| rugcheck-v2-api | ✅ | ✅ | ❌ (PR #190 pending) |
| crypto-price-api | ❌ | ❌ | ❌ |
| gas-price-api | ❌ | ❌ | ❌ |
| token-security-api | ❌ | ❌ | ❌ |
| deal-tracker-api | ❌ | ❌ | ❌ |
| defi-dashboard-api | ❌ | ❌ | ❌ |
| wallet-analytics | ❌ | ❌ | ❌ |
| code-audit-api | ❌ | ❌ | ❌ |
| agent-invoicing | ❌ | ❌ | ❌ |
| stablecoin-portal | ❌ | ❌ | ❌ |
| x402-gateway | ❌ | ❌ | ❌ |
| +50 more | ❌ | ❌ | ❌ |

## Pitfalls

1. **Canonical build queue is JSON, not Markdown** — `scripts/build_queue.json` is the source of truth (v50, 28 items). `10-Labs/build-queue.md` is a human-readable summary that may not exist until created. Always read the JSON first.
2. **Orchestrator list may not exist** — `HQ/jordan-queue.md` is created on first scan. If missing, create it.
3. **Pay-Skills catalog is large (70 providers)** — The `list_catalog` response is compact by default. Don't ask for full details unless filtering for a specific provider.
4. **New marketplaces appear frequently** — The x402 ecosystem is evolving fast. Always check for new directories.
5. **Don't reroute existing marketplace registrations** — Each marketplace has ONE entry point. Adding a second registration duplicates work.
6. **Swarms listing is stale** — Jordan must log in and manually edit. Cannot be automated.
7. **OKX AI needs A2A node running 24/7** — Without a daemon, the listing stays rejected.
