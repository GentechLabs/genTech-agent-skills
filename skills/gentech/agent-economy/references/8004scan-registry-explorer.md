# 8004scan.io — ERC-8004 Registry Explorer (Verified Aug 2026)

## What It Is

8004scan.io is a block-explorer-style UI over the **same on-chain ERC-8004 Identity
Registry** (`0x8004A169FB4a3325136EB29fA0ceB6D2e539a432`) that Agentscan.info reads.
It auto-indexes every agent registered on any supported chain — **no separate
registration or submission needed**. If you registered on-chain, you are on 8004scan.

- Platform stats (Aug 2026): 384K+ registered agents, 522K+ feedback, 357K+ active users
- GenTech Labs #1770 (Avalanche) confirmed live there — auto-synced from on-chain registration
- Per-agent pages: `https://8004scan.io/agents/<chain-slug>/<tokenId>` (e.g. `avalanche/1770`)

## Chain IDs

| URL param | Chain | Notes |
|-----------|-------|-------|
| `1776` | **Injective** (EVM chain ID) | Small early ecosystem (~931 agents vs BNB's 247K+) |
| `8453` | Base | Our primary deployment chain |
| `196` | X Layer (OKX) | |
| avalanche / bsc / ethereum / celo | various | Slug-per-chain pages exist |

## API Reality Check

- **No public REST API.** `/api/*` returns the Next.js HTML shell (not JSON).
  The old `8004scan.io/api/v1/agents` endpoint pattern is what our monitor script uses
  — it works today but is NOT a documented public API. Do not assume stability.
- Data is served via Next.js internal endpoints; page content is extractable via
  web_extract/browser if you need on-demand reads.

## Lead Triage Pattern (built into a2a/discovery)

The raw registry feed is ~60% noise (Ave.ai Trading Agent dupes, `smoke-*` staging
agents, `Agent #xxxxx`, testnet chains). The kit's `a2a/discovery/discovery.py` encodes:

1. **Drop** testnet/staging chains: 84532, 11155111, 1187947933, 97, 5
2. **Drop** known spam families (Ave.ai Trading Agent)
3. **Drop** `smoke-*` and `Agent #xxxxx` entries
4. **Score**: x402 (+3), real description (+2), Base chain (+1), reputation ≥10 (+2)
5. **Sort** by score → top of list = best outreach target

Live run example (Aug 1, 2026): 50 new agents → 8 triaged leads after the filter.

## Relationship to Agent Kit

The full agent-to-agent module lives in `ProtoJay4789/genTech-agent-kit` under `a2a/`:
- `a2a/discovery/` — the registry monitor above
- `a2a/workspace/` — Buzz bridge (Hermes profile as native Buzz agent)
- `a2a/self-audit/` — 4-role harness (Evolution/Critic/Verifier/Gardener) + constitution
- `a2a/identity/` — ERC-8004 on-chain registration across 7+ chains

Theme: **discover → talk → self-audit**.
