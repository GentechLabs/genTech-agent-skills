# Smart Money Rotation — Buy Zones + Narrative Tracking

**Date:** 2026-06-05
**Status:** Feature concept (Green Room queued)
**Related:** AAE DeFi Milestone, CMC Watchlist, Circle Arc

---

## Overview

A cross-chain intelligent vault system that rotates idle stablecoins (dry powder) between chains and protocols based on yield opportunities, narrative strength, and macro market conditions. Combines zone-based entry strategies with autonomous agent execution.

**Core insight:** Most idle USDC products are single-chain. This system uses Arc as a base (USDC-native gas, near-zero fees) and rotates across ecosystems (Avalanche, Solana, Base) to chase yield.

---

## Buy Zone System

Four-tier zone system for each tracked asset. Zones are defined by price levels relative to recent highs/lows and historical support/resistance.

### Zone Definitions

| Zone | Emoji | Meaning | Action |
|------|-------|---------|--------|
| Deep Value | 🔥 | Asset is extremely oversold, near historical lows | Strong buy, heavy accumulation |
| Accumulate | 🟢 | Asset is at support, good entry point | Moderate buy, DCA |
| Watch | 🔵 | Asset is at fair value, wait for better entry | Monitor, no new positions |
| Extended | ⚪ | Asset is at resistance or all-time highs | Consider taking profit |

### Zone Definitions by Asset (June 2026)

```python
BUY_ZONES = {
    "BTC": [
        ("🔥 Deep Value", 0, 50000),
        ("🟢 Accumulate", 50000, 60000),
        ("🔵 Watch", 60000, 70000),
        ("⚪ Extended", 70000, 999999),
    ],
    "SOL": [
        ("🔥 Deep Value", 0, 40),
        ("🟢 Accumulate", 40, 60),
        ("🔵 Watch", 60, 80),
        ("⚪ Extended", 80, 999999),
    ],
    "LINK": [
        ("🔥 Deep Value", 0, 5),
        ("🟢 Accumulate", 5, 8),
        ("🔵 Watch", 8, 12),
        ("⚪ Extended", 12, 999999),
    ],
    "AVAX": [
        ("🔥 Deep Value", 0, 5),
        ("🟢 Accumulate", 5, 7),
        ("🔵 Watch", 7, 10),
        ("⚪ Extended", 10, 999999),
    ],
    "TAO": [
        ("🔥 Deep Value", 0, 150),
        ("🟢 Accumulate", 150, 250),
        ("🔵 Watch", 250, 400),
        ("⚪ Extended", 400, 999999),
    ],
    "ONDO": [
        ("🔥 Deep Value", 0, 0.50),
        ("🟢 Accumulate", 0.50, 0.80),
        ("🔵 Watch", 0.80, 1.20),
        ("⚪ Extended", 1.20, 999999),
    ],
}
```

**Pitfall:** Zone levels must be updated periodically as market structure changes. Hardcoded levels from June 2026 will be stale by Q4. Use a config file, not inline Python.

---

## Narrative Strength Tracking

Track which crypto narratives are outperforming vs underperforming. Agent uses this to prompt rotation decisions.

### Narrative Categories (June 2026)

| Narrative | Coins | Strength | Notes |
|-----------|-------|----------|-------|
| Real Assets (Gold/Silver) | XAUt, XAG | 🟢 STRONG | Flight to safety active during crypto selloff |
| AI / DePIN | TAO | 🟡 MIXED | Narrative strong but price correlated to BTC |
| RWA / DeFi | ONDO | 🟡 MIXED | Institutional interest solid, price follows macro |
| AVAX Ecosystem | AVAX, BEAM, COQ, ARENA | 🟢 STRONG (fundamentals) | FIFA ticketing 24x volume, C-Chain activity surging |
| Blue Chips | BTC, SOL, LINK | 🔴 WEAK (price) | Institutional selling at key support |

### Rotation Logic

```
IF narrative_strength(Asset A) == 🟢 STRONG
AND narrative_strength(Asset B) == 🔴 WEAK
AND zone(Asset A) == 🔥 Deep Value OR 🟢 Accumulate
THEN prompt: "Rotate X% from Asset B to Asset A?"
```

**User override:** Jordan prefers to set personal preferences. Agent suggests, user approves.

**Pitfall — daily frequency masks rotation signals:** Running narrative rotation scans daily produces too much noise to spot actual sector rotations. Daily signals blend into general market volatility, making it impossible to distinguish "everything is down" from "money is rotating OUT of this narrative INTO that one." Use **weekly** cadence for narrative rotation scanning. Daily cadence is for price alerts and LP monitoring — not narrative strength assessment. Jordan missed an ONDO rotation specifically because daily signals masked the trend shift.

---

## Smart Money Rotation Agent (AAE Feature)

### Concept

Autonomous agent that monitors zone positions and narrative strength across all tracked assets, then prompts users to rotate between pools based on what's performing.

### User Flow

```
1. User deposits USDC into Dry Powder Vault
2. Agent monitors: zones + narratives + yield across chains
3. Morning digest: "AVAX in Deep Value zone. Gold holding strong."
4. Agent prompt: "Want to rotate 20% to Avalanche LP?"
5. User approves → agent executes swap + bridge + LP entry
6. Position updated in DeFi milestone tracker
```

### Free vs Paid Tiers

| Feature | Free | $15/mo Agent Pass |
|---------|------|-------------------|
| Zone tracker | ✅ | ✅ |
| Narrative dashboard | ✅ | ✅ |
| Basic alerts | ✅ | ✅ |
| Autonomous rotation prompts | ❌ | ✅ |
| Agent-executed rotations | ❌ | ✅ |
| Smart money tracking | ❌ | ✅ |
| Daily news digest | ❌ | ✅ |
| Priority alerts | ❌ | ✅ |

---

## Dry Powder Vault (Cross-Chain)

### Architecture

```
Base (dry powder holding — cheapest gas)
        ↓ CCTP bridge
Avalanche (LFJ LP — home chain)
        ↓ CCTP bridge
Solana (Meteora/Kamino — high yield)
```

### Arc Integration (v2 — when mainnet launches)

- USDC as native gas (near-zero fees)
- Built-in FX engine (swap stables without DEX)
- Institutional compliance layer
- 350ms finality for instant rotations

### Cross-Chain Infrastructure (Live Today)

| Protocol | Status | Best For |
|----------|--------|----------|
| Circle CCTP | ✅ Live | USDC cross-chain transfers |
| Across Protocol | ✅ Live | Fast, cheap bridging |
| Chainlink CCIP | ✅ Live | Cross-chain messaging |
| LayerZero | ✅ Live | Cross-chain messaging |
| Arc | ⏳ Testnet | Future primary chain |

### Pitfall

Arc mainnet is NOT live yet (June 2026). Do not commit architecture to Arc-only features. Build v1 on Base + Avalanche + Solana using CCTP. Migrate to Arc when mainnet launches.

---

## Integration with Existing Systems

### CMC Watchlist → Zone Monitor

The `cmc-watchlist.py` script already includes buy zones for all 11 tracked coins. Zone status appears in every watchlist report.

### DeFi Milestone Tracker → Rotation Prompts

When the Smart Money Rotation agent suggests a rotation, the DeFi milestone tracker updates to reflect the new position.

### Bear Market Positioning → Q4 Thesis

The vault's `bear-market-positioning.md` already documents the Q4 rotation thesis: "AI bubble is peaking, capital will rotate back to crypto." The Smart Money Rotation agent operationalizes this thesis.

---

## Implementation Priority

1. **v1 (build now):** Base + Avalanche + Solana rotation using CCTP + Arsenal API
2. **v2 (Arc mainnet):** Migrate vault to Arc as primary, add native FX
3. **v3 (full vision):** Autonomous rotation across 5+ chains with gas abstraction

---

*This reference captures the Smart Money Rotation concept from Jordan's brainstorm session (June 5, 2026). Update zone levels and narrative strength as market conditions change.*
