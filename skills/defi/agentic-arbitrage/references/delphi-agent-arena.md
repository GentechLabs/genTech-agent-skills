# Delphi Agent Arena (Gensyn × Delphi) — Prediction-Market Trading Agent

**What it is:** A live competition where autonomous agents trade real prediction
markets for $10K (top-3 P&L split). Trading window Aug 10–24. **Zero real-money risk**
— runs on **Gensyn Testnet** (`TST` test tokens), no USDC/gas at stake. Pure skill
competition. Registered via DoraHacks (`dorahacks.io/hackathon/delphi-agent-competition`).
Aligned with the "Agency of Traders" + agent-sentiment-index vision.

## SDK setup (verified Aug 12, 2026)
```bash
npm init -y && npm install @gensyn-ai/gensyn-delphi-sdk viem dotenv
```
- **ESM-only** — must `import { DelphiClient } from "@gensyn-ai/gensyn-delphi-sdk"`, not `require()`.
- **Network:** `competition-testnet` (NOT the default sandbox/mainnet).
- **Client init** (keyless health check works — good smoke test before wiring a key):
  ```js
  const c = new DelphiClient({ network: "competition-testnet",
      signerType: "private_key", privateKey: process.env.DELPHI_SIGNER_KEY });
  const h = await c.health();  // {"status":"ok"} — proves network + client are correct
  ```
- **Market data reads need NO API key** — the competition subgraph is public:
  `https://api.goldsky.com/api/public/project_cmnoqdag1obop01z3efnu8ssq/subgraphs/delphi-agent-competition/1.0.0/gn`
  (probe with `{ "__typename": "Query" }`; it exposes gateway events, not titles/prices —
  full market titles/prices come from the REST API which IS keyed).

## 🔴 The ONE human gate (agent cannot self-serve)
Trading (reads via `listMarkets`, placing orders) needs a **testnet API key** generated at
`delphi-api-access.gensyn.ai` — **wallet sign-in required**. This is the split point: agent
stages everything (scaffold agent, verify SDK health, write strategy) and hands Jordan the
one-pass step: *open `delphi-api-access.gensyn.ai` → sign in → generate testnet key → paste*.
Also need a **throwaway signing key** holding TST (competition tokens from the dashboard/faucet).

## Strategy (scaffolded at /root/delphi-arena/trade.js)
Contrarian scoring on open LMSR markets:
- Pull live markets + implied probabilities; flag overpriced favorites (spot prob high)
  and buy the cheap opposite side when the gap exceeds a threshold.
- **Field is `m.spotImpliedProbabilities`** (array, e.g. `[0.48, 0.52]`) — present when
  `pricesAndImpliedProbabilities=true` on `listMarkets`. Use it; skip markets without it.
- Diversify across top-N candidates (don't over-concentrate).
- **Dry-run mode first** (no orders) so you can show Jordan its picks before arming.
- Leaders are beatable — most competitors sit near baseline; a disciplined signal agent
  can climb in the 12-day window.

## Why pursue it (strategic)
- Zero-risk (testnet) + real Gensyn/Delphi prestige if we place.
- Proving ground for the agent-sentiment index / "Agency of Traders" — whoever builds the
  best signal-driven trading agent wins.
- Reuses the trading/agent DNA (GTA, treasury, regime classifier).

## Current state (Aug 12)
Agent scaffolded + SDK verified (`health: ok` on competition-testnet). README + config
template committed to vault `10-Labs/delphi-arena/`. **Blocked only on Jordan's testnet API
key + TST signing key** to move from dry-run to live.
