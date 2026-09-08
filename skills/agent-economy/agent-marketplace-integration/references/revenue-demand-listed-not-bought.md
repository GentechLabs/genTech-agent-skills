# Demand-Side Truth: "Listed ≠ Bought" (Aug 24, 2026)

## The core lesson

Having services live + listed on many marketplaces does NOT produce revenue. We had **10 live
services** (token security, wallet analysis, market intel, DeFi LP analytics, agent discovery,
NFT search, treasury defender, lineage guard, deal tracker, agent research) priced at
**$0.01–$0.10/call**, live on **6 chains**, listed on Syra, awesome-mcp-servers, OpenDexter,
x402scan, EvoMap, Hive — **and months of zero revenue.**

Why: x402 pay-per-call at $0.01 with **no sticky buyer** = no income. A niche analytics
endpoint (e.g. token_security) is only valuable if an agent discovers it AND invokes it
thousands of times a day. Nobody is. **Presence on a marketplace is not the same as being
bought.**

## What actually earns in the x402 space (verified demand)

- **LLM inference resale is the proven volume earner.** blockrun's model: accept USDC via
  x402, forward requests to GPT/Claude/Gemini/DeepSeek, charge **provider cost + 5%** →
  ~$820/day (~$25K/mo) from agents paying per request. Inference is the most-pinged service
  on earth; niche analytics at $0.02 is not.
- **4,400 buyers vs only 477 sellers** on x402 (Mar 2026) — the sell-side is starved, but
  that's an *opportunity* only if you're selling what agents actually consume at volume.
- **Agent-to-agent specialist services** (MCP endpoints doing 18,670 tx/day at $0.01) =
  an orchestrator keeps invoking one capability repeatedly. That's the repeat-buyer pattern
  to chase, not one-off analytics.
- **Agent.market (Coinbase)** is the single largest x402-native agent marketplace (69K+
  active agents). If not listed there, that's the biggest real demand pool gap.

## The decision framework when revenue is the goal

1. **Diagnose demand, not presence.** Ask: "who repeatedly buys this service?" A $0.02
   analytics endpoint nobody pings is dead weight regardless of how many marketplaces list it.
2. **Reposition toward high-frequency, high-volume services** agents actually buy repeatedly —
   inference resale (cost + margin) beats niche per-call analytics for near-term income.
3. **Prioritize venues with real buyer traffic.** Coinbase Agent.market / high-volume x402
   pools over another empty directory listing. Verify the venue's buyer count before adding
   it as another "listed" row.
4. **When a marketplace never pays, that's a different problem** (see payout-rail-probe) —
   distinguish "no buyers here" from "never pays anyone."

## Rule of thumb

More listings is not the fix for zero revenue. The fix is (a) the right service (high
invocation frequency), (b) the right venue (real buyer traffic), and (c) at least one real
paid call to prove the rail and get settlement-gated marketplaces to index you.
