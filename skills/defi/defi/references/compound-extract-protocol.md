# Compound/Extract Protocol — Product Spec (Jun 17, 2026)

**Status:** SPEC COMPLETE → Building in Labs
**Priority:** HIGH — Flagship Agent Kit DeFi module
**Spec:** `09-Green Room/ideas/compound-extract-protocol.md`
**Architecture:** `02-Labs/compound-extract/ARCHITECTURE.md`
**Code:** `02-Labs/compound-extract/src/`
**Build timeline:** 2 weeks MVP, 6 weeks full product

## The Pain Point

LP providers on concentrated liquidity DEXs face a binary choice:
1. **Leave fees in** → fees sit idle, don't compound, lose buying power
2. **Close position to extract** → lose range, pay gas to re-enter, miss fee generation

Neither option is optimal.

## The Solution

Extract profits while keeping your position active:
- **Compound Mode**: Reinvest fees back into position → grows principal
- **Extract Mode**: Pull out accumulated fees → send to wallet
- **Auto Mode**: AI decides based on market conditions, gas prices, user preferences

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    USER INTERFACE                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │   Dashboard  │  │   Settings  │  │   History   │    │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘    │
│         └────────────────┴────────────────┘             │
│                        │                                │
│  ┌─────────────────────┴─────────────────────────┐    │
│  │              API Gateway / Router              │    │
│  └──────────────────────┬────────────────────────┘    │
└─────────────────────────┼───────────────────────────────┘
                          │
┌─────────────────────────┼───────────────────────────────┐
│                   CORE ENGINE                           │
│  ┌──────────────┐  ┌────┴─────┐  ┌──────────────┐    │
│  │ Fee Monitor  │  │ Decision │  │   Executor   │    │
│  │ (Tracking)   │  │ Engine   │  │ (Compound/   │    │
│  │              │  │ (AI)     │  │  Extract)    │    │
│  └──────────────┘  └──────────┘  └──────────────┘    │
└─────────────────────────────────────────────────────────┘
```

## Core Components (Built)

### 1. Fee Monitor (`src/fee_monitor.py`)
- Track real-time fee accumulation per LP position
- Calculate fee velocity (hourly/daily rate)
- Persist state to disk (JSON)

### 2. Decision Engine (`src/decision_engine.py`)
- AI-powered compound vs. extract decisions
- Rule-based in Phase 1, ML optimization in Phase 2
- Considers: market volatility, gas prices, user preferences
- Decision matrix: stable → compound, volatile → extract, high gas → wait

### 3. Executor (`src/executor.py`) — Built Jun 18, 2026

Pluggable adapter architecture for multi-chain DeFi execution. Abstract `SwapAdapter` base class with chain-specific implementations.

**Extract Flow:** claim fees → swap to target token → transfer to wallet
**Compound Flow:** claim fees → swap half to pair's other token → add_liquidity back

**Adapters:**

| Adapter | Chain | DEX | Status |
|---------|-------|-----|--------|
| `LFJAdapter` | Avalanche | Trader Joe V2.1 | ✅ Scaffold (simulated) |
| `ZeroXSwapRouter` | EVM (multi-chain) | 0x API | ✅ Scaffold (simulated) |
| `JupiterSwapRouter` | Solana | Jupiter | ✅ Stub |

**Key classes:**
- `SwapAdapter` (ABC) — `get_quote()`, `swap()`, `approve()`
- `LFJAdapter` — extends with `add_liquidity()`, `claim_fees()`
- `Executor` — orchestrates extract/compound with any adapter
- `create_executor(chain)` — factory for adapter selection

**Return types:** `ExtractResult`, `CompoundResult` — include transaction receipts, gas costs, amounts

**Testnet scaffold:** `testnet/` directory with config.json, deploy_fuji.py, 11 integration tests (5 extract + 6 compound)

**Pitfall — Python dataclass enum serialization:** When saving test results as JSON, `OperationResult` enums need `.value` before `json.dump()`. Pattern:
```python
d["status"] = d["status"].value if hasattr(d["status"], "value") else d["status"]
for tx in d.get("transactions", []):
    if "status" in tx and hasattr(tx["status"], "value"):
        tx["status"] = tx["status"].value
```

**Pitfall — Missing source files:** The executor.py was referenced but didn't exist. Created it from ARCHITECTURE.md spec. Always check if referenced files exist before assuming they're built.

## Testnet Deployment (Avalanche Fuji)

**Config:** Chain ID 43113, RPC `https://api.avax-test.network/ext/bc/C/rpc`

**Scaffold structure:**
```
testnet/
├── config.json          — Fuji RPC, chain ID, mock contract addresses
├── deploy_fuji.py       — Deployment scaffold (FujiConnection, ContractDeployer)
├── test_extract.py      — 5 extract integration tests
├── test_compound.py     — 6 compound integration tests
└── README.md            — Deployment guide with flow diagrams
```

**Deploy flow:** `deploy_fuji.py --dry-run` → verify → `deploy_fuji.py` (real)

**Next:** Write `CompoundExtract.sol` → compile → deploy to Fuji → replace mocks with real contract calls

## Supported DEXs

| DEX | Chain | Status |
|-----|-------|--------|
| LFJ (Trader Joe) | Avalanche | ✅ Phase 1 |
| Uniswap V3 | Ethereum/Base | 🔲 Phase 2 |
| Aerodrome | Base | 🔲 Phase 2 |
| Meteora | Solana | 🔲 Phase 2 |

## Revenue Model

| Stream | Fee | Notes |
|--------|-----|-------|
| Extraction fee | 0.1-0.5% | On extracted amount |
| Compound fee | 0.05-0.1% | On compounded amount |
| Premium auto-mode | $5/mo | AI decision engine |
| API access | $20/mo | For other protocols |

## Competitive Advantage

| Feature | Bankr | GOAT SDK | AAE (Us) |
|---------|-------|----------|----------|
| Fee extraction | Basic | Basic | **Optimized** |
| Auto-compound | ❌ | ❌ | **✅** |
| AI decision engine | ❌ | ❌ | **✅** |
| Gas optimization | ❌ | ❌ | **✅** |

## Build Timeline

| Phase | Duration | Deliverable | Status |
|-------|----------|-------------|--------|
| Phase 1: Fee Monitoring | ✅ Complete | Real-time tracking, dashboard display | ✅ Done |
| Phase 2: Executor + Testnet | ✅ Complete | Pluggable adapters, 11 integration tests | ✅ Done (Jun 18) |
| Phase 3: Solidity Contract | TBD | CompoundExtract.sol on Fuji | 🔲 Next |
| Phase 4: Auto Mode | 1 week | AI decision engine integration | 🔲 |
| Phase 5: Multi-DEX | 2 weeks | Uniswap V3, Aerodrome, Meteora | 🔲 |

## Key Insight

The hard part isn't "can we extract fees" — on most concentrated liquidity DEXs, fees accumulate separately from the position and can be claimed via `collect()`. The hard part is **automating the decision** and making it seamless. That's where the AI adds value.

## Connection to Existing Work

- **LFJ Integration**: Our existing reader.mjs pipeline can be extended
- **Agent Kit**: DeFi module includes compound/extract as standard feature
- **AAE**: Autonomous agents compound/extract without user intervention
- **Dashboard**: New "Compound/Extract" tab with position overview

## Next Steps

1. ✅ Product spec complete
2. ✅ Architecture doc in Labs
3. ✅ Phase 1: Fee monitoring code (tests passing)
4. ✅ Phase 2: Executor module + testnet scaffold (11 tests passing, Jun 18)
5. 🔲 Phase 3: Write CompoundExtract.sol → compile → deploy to Fuji
6. 🔲 Phase 4: Replace mocks with real contract calls
7. 🔲 Phase 5: Auto mode (AI decision engine integration)
8. 🔲 Phase 6: Multi-DEX expansion (Uniswap V3, Aerodrome, Meteora)
