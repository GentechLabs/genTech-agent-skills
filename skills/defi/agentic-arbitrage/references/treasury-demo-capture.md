# Treasury Agent — Live Demo Capture Pattern (Aug 5, 2026)

When Jordan asks "can you capture a demo of the Treasury agent doing what it's doing?" (for a
video, employer proof, or hackathon submission), the answer is a **self-running capture script**
that shows the agent's real workflow with live on-chain data — not a narrated description.

## The pattern

`treasury_demo_capture.py` (in `~/.hermes/profiles/gentech-treasury/scripts/`) runs the agent's
actual layers and emits a timestamped transcript. It is **read-only — no trades fired** — so it's
safe to run anytime. Structure:

1. **Fused command-center report** — run `agentic-treasury.py` (the agent's brain: regime + LP
   farm + on-chain positions + arb + narrative → one decision call)
2. **Live on-chain positions** — the CDP account's real balances (read-only RPC, no key needed)
3. **Solana homebase quote** — `solana_homebase.py --action buy --symbol SOL --amount 5` (live
   Jupiter quote, DRY_RUN)
4. **Settlement proof** — the first real x402 payment (0.005 USDC, arb wallet, 402→200)

Each step is a `subprocess.run` of the real script; the transcript is saved to a file AND printed.

## Why it's strong for demos
- **100% real data** — live balances, live quotes, real settlement. Nothing simulated.
- **Shows the decision loop** — the agent reads 5 layers, fuses them, outputs a call (HOLD) + flags.
- **One command** — `python3 treasury_demo_capture.py` → full transcript file.
- Doubles as: video segment, employer artifact, hackathon live-proof (Arc, tranche-2, Colosseum).

## Deploying it as a demo page (2nd demo in the suite)
1. Build a `treasury-demo.html` page that renders the live report in a terminal-style card
   (JetBrains Mono, green/red/yellow/blue/purple color legend, "● LIVE · Real On-Chain Data" badge).
2. Add a card to `demo.html`'s DeFi Intelligence grid linking to it.
3. **Pitfall:** `write_file` into `/var/www/gentechlabs/` creates a 600-perm file nginx (www-data)
   can't read → **HTTP 403**. Fix: `chmod 644 /var/www/gentechlabs/{name}.html`, then verify
   `curl -s -o /dev/null -w "%{http_code}" https://gentechlabs.net/{name}.html` → 200.

## Key files
- `~/.hermes/profiles/gentech-treasury/scripts/treasury_demo_capture.py` — the capture script
- `/var/www/gentechlabs/treasury-demo.html` — the live demo page (2nd demo in the suite)
- `agentic-treasury.py` — the fused report the capture runs
