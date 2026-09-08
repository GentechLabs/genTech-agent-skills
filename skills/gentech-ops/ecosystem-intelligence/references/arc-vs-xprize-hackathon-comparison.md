# Hackathon Comparison: Arc vs XPRIZE Agentic Payments

## Arc Programmable Money Hackathon (Encode Club)
- **Prize:** $10K + top 8 teams get 8-week accelerator
- **Platform:** Arc L1 (Circle's stablecoin chain) — must build on Arc
- **Tracks:** DeFi, Agentic Economy
- **Deadline:** Aug 9, 2026 (final submission) — 6 days from Jul 27
- **Requirements:** Working prototype on Arc, 3-min video, public repo, deck
- **Our fit:** Port x402 to Arc L1, use Circle's Agent Stack. Modular stack makes this config changes, not rewrites.
- **Status:** Jordan registered, 6 days remaining

## Circle $50K Agentic Payments Prize (Build with Gemini XPRIZE)
- **Prize:** $50K (part of $2M total, $500K grand prize)
- **Platform:** Any — not locked to a specific chain
- **Focus:** AI agents autonomously handling payments as core business
- **Deadline:** Aug 17, 2026 — 21 days from Jul 27
- **Requirements:**
  - Use **Gemini API for at least one LLM call**
  - Use at least one **Google Cloud product**
  - Show real users and real revenue with evidence
  - GitHub repo, ≤3-min demo video, 500-1000 word narrative
- **Our fit:** Already have everything — x402 gateway, ERC-8004, AgentEscrow, Agent Credit Score. Just need to add one Gemini API call + one Google Cloud product.
- **Status:** Not yet registered. Jordan needs to register at xprize.devpost.com

## Key Differences

| Dimension | Arc | XPRIZE |
|-----------|-----|--------|
| Prize | $10K + accelerator | $50K (Circle) / $2M total |
| Platform lock | Arc L1 only | Any platform |
| Build effort | Port to new L1 | Submit existing stack + Gemini call |
| Deadline | Aug 9 (6 days) | Aug 17 (21 days) |
| Revenue required | No | Yes — real users + revenue evidence |
| Gemini required | No | Yes — at least one API call |

## Strategy
- **Arc:** Submit our modular stack ported to Arc. The Agentic Economy track is exactly what we built. 6 days is tight but doable — x402 is multi-chain by design.
- **XPRIZE:** Stronger fit. We don't need to build anything new — our existing stack is exactly what they're looking for. Add one Gemini API call (route one agent decision through Gemini instead of DeepSeek) and one Google Cloud product. Submit what's already live.
