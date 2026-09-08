---
name: agentic-arbitrage
description: >-
  Build and manage the GenTech Treasury Agent (GTA) — a cross-venue arbitrage
  system with macro intelligence, yield farming, narrative rotation, and
  decision-partner UX. Covers Hyperliquid perp vs Coinbase spot basis
  detection, Across/CCTP bridging for funding, VPS geo-bypass, Robinhood
  Chain integration, and the three-phase product roadmap (Cockpit → MCP
  Distribution → Web Product).
triggers:
  - build an arb monitor
  - set up arbitrage trading
  - connect to hyperliquid from US
  - cross-venue basis trading
  - GTA arb
  - agentic treasury arbitrage
  - bridge to hyperliquid
  - across protocol deposit
  - robinhood chain trading
  - GTA decision partner
  - virtuals competition
  - agentic treasury architecture
---

# Agentic Arbitrage

## Concept

An agent running on a non-US VPS has unrestricted access to perp DEXes
that geo-block US IPs at the **frontend only**. The protocol layer
(chain/RPC) has no such restriction. This means a US-based user can deploy
an agent on cloud infra and trade these venues as if they were offshore.

## Core Pipeline

```
User funds wallet (Base USDC) ──▶ Across Bridge ──▶ Hyperliquid L1
                                                      │
Agent scans perp vs spot basis every hour ──────────▶ Spread detected
Agent reports opportunity (contango/backwardation) ──▶ User decides
Agent executes both legs ────────────────────────────▶ Position open
Agent monitors hourly ───────────────────────────────▶ P&L + spread tracking
Agent closes when spread normalizes ─────────────────▶ Profit auto-sweeps
```

## 0. US-Compliance Pivot (Aug 3, 2026) — READ BEFORE BUILDING EXECUTION

**Hyperliquid execution is a US gray zone.** HL excludes US persons in its ToS; the
key technically works but trading HL perps as a US resident is a ToS violation + CFTC
gray zone. **Do not steer a US-based user to a Hyperliquid execution key.** Keep HL as
**detection/price-signal only** (read-only is fine — the monitor uses it).

- **Execution is US-venue-native:** Coinbase spot (✅ verified live) → Robinhood perps
  (KYC/OAuth pending) → Polymarket → Ondo.
- **Strategic edge:** CLARITY Act deepens US venues, moving the arb opportunity ONTO
  compliant rails. We arbitrage *between* platforms (Coinbase vs Robinhood), not by
  fighting to get into HL.
- **GTA = open execution + authorized-proxy layer** (not just arb): the agent does
  everything for you across every venue you're legally entitled to use, with granular
  permissions (read/trade/move/withdraw — withdrawals always human-confirmed). Full
  thesis: `09-Green Room/specs/gta-product-thesis.md`.

### GTA Buy List vs. acquisition rails (Jordan, Aug 4 2026)
The CMC watchlist (`cmc-watchlist.py`) is really the **GTA buy list** — the assets
the agent should be positioned to acquire. But **"tracking a price" ≠ "being able
to buy it."** Before claiming the buy list is actionable, map every asset to a
*actually wired* execution rail — otherwise you over-promise execution that isn't
there. Rails today:
- **BTC/cbBTC** → Coinbase spot leg (SUPPORTED map). The only wired rail today.
- **SOL/TAO** → needs a Solana swap path (Jupiter via BlockRun).
- **AVAX/COQ** → needs an Avalanche rail (our wallet) — CDP server account is Base-only.

### AVAX rail — Almanak (installed) + custody decision (Aug 6, 2026)
The Avalanche rail is **Almanak** (almanak.co, `pip install almanak`, open-source Python
SDK). Installed + verified in the isolated 3.12 venv `/root/.hermes/profiles/gentech/venvs/almanak-venv`
(version 2.24.0; CLI works: `almanak --version`, `almanak ax --help`, `almanak ax swap USDC AVAX 1 --chain avalanche --dry-run`).
Almanak is the Avalanche-native rail that can manage the LFJ AVAX/USDC V2 pool (Trader Joe —
Jordan's favorite venue; the AAD-5/DeFi Milestone was originally built on it).

**⚠️ Custody blocker (NOT a coding step — a Jordan decision):** CDP does NOT cover
Avalanche (swap API + server account are Base/Ethereum-only; `list_token_balances(network='avalanche')`
is rejected). So the AVAX rail CANNOT reuse the CDP server wallet. It needs EITHER:
- **(a) Almanak full** — deploy a Safe smart account + Zodiac signer service. Institutional-grade
  (backtest, copy-trading), heavier setup. Also the shared engine for the Agent Arena.
- **(b) A separate AVAX keypair** the agent holds directly (raw signing — different security
  posture than CDP's TEE). Fast to execution.

**✅ DECISION MADE (Aug 6, 2026) — Jordan chose (a) Almanak FULL.** His rationale: "using the
Almanak stack the full is probably going to be better because most of everything is already
there instead of us trying to build it like ourselves." Compose Almanak's institutional
infrastructure (Safe custody, gateway, backtest, TraderJoe LP connector) rather than build our
own custody/signing from scratch. Next step: deploy Safe + Zodiac signer service, configure
`ALMANAK_PLATFORM_WALLETS` + `ALMANAK_SIGNER_SERVICE_ENDPOINT_ROOT` + `ALMANAK_SIGNER_SERVICE_JWT`,
then scaffold the `traderjoe_lp` strategy for the AVAX/USDC V2 pool. Owner: The Steward.
- **LINK/ONDO** → Base, but real contract addresses must be verified LIVE against
  `get_swap_price` before enabling (never fabricate; a CoinGecko `platforms.base`
  address is a *candidate*, not verified).
- **XAUt** → commodity-backed token, needs real address + venue.
Q402 moves stablecoins (USDC/USDT) — it can *pay*, but it does NOT swap into these
tokens, so it is not a buy rail for them. Jordan's goal: the Agentic Treasury
executes from **ANY home base** — dry powder (onchain/DEX) OR the Arc blockchain OR
Base. Design acquisitions as rail-per-chain, not one venue.

### Coinbase spot leg (the working execution path)
The verified US-compliant execution leg. See `references/coinbase-cdp-spot-leg.md`.
Key gotchas: CDP swap API needs **contract addresses + raw integer amounts** (not
tickers/decimals); `get_swap_price` = unfunded read-only basis oracle;
`create_swap_quote` needs a funded account (gasFee validation fails on empty wallet).
**NEVER fabricate contract addresses** — only list tokens verified against the live
API; mark unverified ones "unsupported" until you look up + test the real address.
- **⚠️ Upstream SDK bug — FIXED Aug 3 (re-apply on SDK reinstall):** real swap
  execution on a **fully funded** account (USDC + native gas both present) previously
  failed with `CommonSwapResponseFees.gasFee — Input should be a dictionary, input_value=None`.
  The CDP API returns `gasFee: null` and `cdp-sdk` v1.47.1's Pydantic parser rejected it.
  **Resolved with 3 in-place SDK patches** (Optional-ize `CommonSwapResponseFees.gas_fee/`
  `protocol_fee`, `CommonSwapResponseIssues.allowance/balance`, and fix the
  `liquidity_available` bool-vs-string validator). After patching, quote works and
  execution reaches the signing step. **Next gate is the `CDP_WALLET_SECRET` signing
  credential** (user-only, trade-capable — never fabricate it). The in-place patches are
  lost on `pip` reinstall — see `references/coinbase-cdp-swap-execution-blocker.md` for
  the exact patches + the `chainId`-in-tx and account-fetch method traps.
- **Method-signature trap:** `get_account(address=...)` fetches an existing funded
  account; `get_or_create_account(address=...)` does NOT accept `address` (raises
  `TypeError`). Use `get_account(address=)` when executing on a specific funded account.
- **⚠️ Spot-leg token gating (Aug 4):** `gta_coinbase_leg.py` only executes symbols in
  its `SUPPORTED` dict — and it currently holds ONLY cbBTC (verified). PAXG, AVAX, etc.
  return `{"skipped":"unsupported-token-<SYM>"}`, NOT an auth error. This is the #1
  reason the GTA spot leg "won't trade": the executor keeps flagging PAXG ENTER, but the
  leg returns unsupported until real contract addresses are looked up + added to
  `SUPPORTED`. Diagnose an unexecuting spot leg by checking `SUPPORTED` FIRST before
  blaming auth. **Credential split:** `CDP_API_KEY_ID`/`CDP_API_KEY_SECRET` = read-only
  (balances/quotes/auth to the API); `CDP_WALLET_SECRET` = the server-account signing
  secret that actually authorizes a real swap (user-only, trade-capable, never fabricate).
  Both are required for real execution — API key alone returns 401 on account/list if
  the project scope is wrong, and is read-only even when valid.
- **⚠️ CDP 401 = credential rejection, NOT a code bug (Aug 4):** a `401` on
  `list_evm_accounts` means Coinbase rejects the API key itself, even when the key
  format is correct (36-char `CDP_API_KEY_ID` + 88-char Ed25519 `CDP_API_KEY_SECRET`)
  and the JWT signs fine. Prove it by running the SDK's own
  `CdpClient().evm.list_accounts()` — `200` = key good, `401` = key was rotated/revoked,
  belongs to a different project, or lost its EVM read scope. Fix = regenerate the key in
  the Coinbase portal, NOT more code. Also note the SDK base is
  `https://api.cdp.coinbase.com/platform` + `/v2/evm/accounts` (NOT `/v1/`). Full
  diagnostic: `references/cdp-401-diagnosis.md`.
- **`CDP_WALLET_SECRET` is NOT auto-wired:** the trade-capable signing secret is stored
  at `/root/.blockrun/cdp-wallet-secret` (chmod 600, Jordan-provided) but `gta_coinbase_leg.py`
  does NOT load it. The SDK only reads it from the `CDP_WALLET_SECRET` env var or the
  `CdpClient(wallet_secret=...)` arg. Storing the file is not enough — wire it into
  execution before a real swap can sign.
- **Funding routing (multi-wallet gotcha):** the CDP server accounts start EMPTY — the
  user funds the GTA **EOA** (`gentech-arb-wallet.json`), and USDC must be MOVED EOA→CDP
  account (with `chainId:8453` in the tx dict) before a real swap. The CDP account also
  needs native ETH for gas. Full recipe: `references/gta-executor-and-cdp-sdk.md`.

## 0b. GTA-as-Platform — The Agency of Traders + Layer 3 Agent Intelligence (Aug 3, 2026)

Jordan's strategic reframe (Aug 3): **GTA is not just a trader — it's a gateway/
platform.** Full vision: `09-Green Room/specs/gta-product-thesis.md` (three-layer
model) + `09-Green Room/specs/agent-arena-vision.md`.

**The Agency of Traders** (Jordan's name) — an open, social, BYO-agent prediction-
market competition:
- **Free + bring-your-own-agent** (differentiates from Minara's pay-to-play walled garden)
- Agents plug into the **GTA treasury via MCP**, get a **scoped bankroll + trust score**
  (trust-layer governance — see `a2a-trust-layer-deep-dive.md`), and compete visibly
- Social: watch which agents outperform based on what you pick; live PnL decides winner
- Arena mechanics borrowed from **Xona World** (`xona-labs/xona-world`, MIT): per-cycle,
  stateless single-shot decision per agent; same bankroll/markets, only the model differs

**Layer 3: Agent Intelligence (the new data layer).** Layers 1 & 2 were built with
*people* as users. Layer 3 treats *agents as participants* whose behavior is measurable,
first-class data:
- **Log every GTA/connected-agent trade with agent attribution from day one** — an
  agent-flow dataset, cheap to start, expensive to retrofit. Build-order item #6.
- **Agent sentiment / flow index** — net long/short agent positioning, confidence,
  and **agent-vs-human divergence** (the spread between agent flow and human fear/greed
  is itself a signal). A proprietary first-mover indicator nobody owns yet.
- We can identify agents (a2a / ERC-8004 / trust-layer) → agent trades are attributable.
- This is the differentiator: the platform generates its OWN indicator data.

**Working reframe to remember:** GTA reads the market *including what other agents are
doing*, not just human flow. The data from Layers 1 & 2 feeds Layer 3's signal.

## 0c. AAE = Autonomous Agent Economy + Agentic Treasury (Aug 4, 2026)

**⚠️ IDENTITY (Jordan-corrected):** "AAE" = **Autonomous Agent Economy**, slogan
"Join the AAE — the autonomous agent economy." NOT "Asian", NOT "Aided-Execution",
NOT "DeFi strategy fusion." The **prime product is the Agentic Treasury** — a user
deposits USDC and the treasury manages itself (trade / rotate / rebalance
autonomously). The fusion layer below IS the seed of that product.

**Naming hierarchy (locked Aug 6, 2026):**
- **AAE** = the slogan — "Join the autonomous agent economy."
- **Agentic Treasury** = the product (the umbrella — grows + moves capital across rails).
- **The Steward** = the agent that runs it (permanent name, chosen by Jordan Aug 6).
  The treasury profile's SOUL.md identity is "The Steward" — grow it / move it / guard it.
  In the Gentech Treasury group the agent is simply called **Treasury** (the Treasury agent);
  "The Steward" is the persona that manages it. Jordan: "everyone that gets an agent gets
  Treasury; The Steward is the one who manages it."
- **DeFi Milestones** = a FEATURE inside the Agentic Treasury (the tiered fee-progression
  system: Scout → Raider → Warlord → Sovereign). It is NOT the product name anymore.
  Keep the `defi-milestones` project id; the product umbrella is the Agentic Treasury.
- The repo can stay technical (`deploy-agentic-treasury`); the agent identity is The Steward.

**⚠️ Don't over-rename:** when Jordan says a name, confirm the exact scope before
rewriting. He corrected an over-eager rename of `defi-milestones` → `agentic-treasury`
in projects.json — the project id stays `defi-milestones`; the Agentic Treasury is the
umbrella product, not a replacement project entry. Ask which level (slogan/product/agent/
feature) a name applies to before propagating it across the vault.

**⚠️ Rename code carefully — separate identity labels from functional names.** When
cleaning up old naming (GTA/consigliere → The Steward/Agentic Treasury), update the
*identity labels* (doc titles, `💼 GTA Pos` → `💼 Steward Pos` in `agentic-treasury.py`,
the demo-capture matcher) but DO NOT rename functional script names (`gta_coinbase_leg.py`,
`gta-arb-monitor.py`, `gta_executor.py`) — those are referenced by crons and would break.
When changing an emitted label, update the consumer that matches on it in the SAME pass
(e.g. `treasury_demo_capture.py` greps for `"GTA Pos"` — change both emitter and matcher
together or the demo silently stops capturing).

Jordan wants the whole DeFi cron fleet consolidated around the **AAE fusion layer**,
not run as parallel pings. Pattern:
- **Fusion core:** `Treasury/scripts/aae-hybrid-signal.py` chains `regime_classifier` +
  `strategy_returns` + `allocation_engine` into ONE unified signal
  (`run_hybrid_signal()` → `.aae-hybrid-signal.json`) + human-readable
  `format_hybrid_report()`. Runs clean standalone: `python3 aae-hybrid-signal.py`.
- **Feeds (write JSON, don't spam chat):** `narrative-rotation.py` (✅ FIXED Aug 4 —
  was 401'ing on a hardcoded stale CMC key; now `_load_cmc_key()` reads
  /root/.hermes/scripts/cmc_config.json first, then env CMC_API_KEY; both 200),
  `yield-rainbow.py` → `yield-rainbow-data.json`, `coin-rainbow.py` → per-coin
  (BTC/AVAX) value zones → `coin-rainbow-data.json`, `gta-arb-monitor.py` →
  `.gta-arb-state.json`.
- **MVP BUILT (Aug 4, greenlit):** `agentic-treasury.py` is the fused report — reads
  all feeds, emits ONE Telegram-safe table (<1000 chars) with emoji status per layer
  + fused call + flags. Wrapper `agentic-treasury.sh` (refreshes coin rainbow, runs
  report, appends dashboard link). Cron `1cbde1d52242` "Agentic Treasury", no_agent,
  `0 8,14,20 * * *` → HQ. Dashboard: `/var/www/gentechlabs/coin-rainbow.html` at
  demo.gentechlabs.net/coin-rainbow.html. All in ~/.hermes/profiles/gentech/scripts/.
- **Value it unlocks:** surfaces broken inputs (dead narrative feed, LP idled out of
  range at 0% efficiency) that parallel pings bury.
- **Pitfalls:** (1) nginx 403 on agent-written HTML/JSON — root scripts write 0600
  files, nginx (www-data) 403s; fix: chown www-data + chmod 644 the file AND
  `os.chmod(OUTPUT_FILE, 0o644)` in the generator so future runs don't regress.
  (2) Brand-new subdomain has no DNS — serve from an existing demo root
  (demo.gentechlabs.net/<file>) until the A record is added. (3) Never hardcode API
  keys in scripts — they go stale (the narrative 401).
- **Multi-channel delivery:** cron delivery is channel-agnostic
  (`platform:chat_id:thread_id`). The same Agentic Treasury can push to
  Discord/Slack/WhatsApp via gateway + `deliver` target. Free = reading the glance;
  paid lane ($10-20) = executing the fused call, alert webhooks, per-coin rainbows.
- **Not to conflate:** `aa-service-prompts` skill uses "AAE" for a separate per-user
  detect→offer→opt-in loop — that is a different feature name, not the Autonomous
  Agent Economy product.

## 1. VPS Geo-Bypass

- The geo-block is at the website (app.hyperliquid.xyz), not the API/chain.
- The agent's Python SDK talks directly to the L1 chain — no frontend,
  no IP check.
- Verify: `curl -s "https://api.hyperliquid.xyz/info" -X POST ...`
- The VPS IP is not a US IP by default on most cloud providers.

## 2. Hyperliquid Connection

**Read-only (verify access):**
```python
python3 -c "
import json, urllib.request
data = json.dumps({'type': 'allMids'}).encode()
req = urllib.request.Request('https://api.hyperliquid.xyz/info', data=data,
    headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req, timeout=10) as resp:
    mids = json.loads(resp.read())
    print(f'{len(mids)} assets, BTC: \${float(mids[\"BTC\"]):,.2f}')
"
```

**Full Exchange (requires private key):**
```python
from hyperliquid.exchange import Exchange
from hyperliquid.info import Info
import eth_account

account = eth_account.Account.from_key(PRIVATE_KEY)
info = Info('https://api.hyperliquid.xyz')
exchange = Exchange(account, 'https://api.hyperliquid.xyz')
```

**IMPORTANT:** SDK's `requests.post()` has no default timeout. Always use
curl with `--max-time 8` or provide a `timeout` to the Exchange constructor.
The Hyperliquid API requires `Content-Type: application/json` header.

## 3. Spot Price Fetching

**Coinbase public API** (no key needed for prices):
```
curl -s "https://api.coinbase.com/v2/prices/BTC-USD/spot"
```

**CoinGecko** (free, wider coverage):
```
https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd
```

**CoinGecko ID mapping** for the arb watchlist:
```
BTC → bitcoin, ETH → ethereum, SOL → solana, AVAX → avalanche-2,
LINK → chainlink, ONDO → ondo-finance, PAXG → pax-gold
```

## Polymarket (Alternative Execution Venue)

When arb execution is blocked (no HL bridge, no Coinbase key), **Polymarket
prediction markets** are the fastest path to a working agent loop. Proven by
0xJeff (80K followers, ex-TradFi) in Jul 2026 — his Hermes agent trades oil
UP/DOWN markets with 4W/2L (66.7% WR), paying its own inference costs.

**How it works (0xJeff's pattern):**
1. **Signal source:** Synth API — 24/7 competition where miners predict
   price paths of assets (commodities, equities, crypto). More accurate
   miners earn more rewards.
2. **Execution:** Polymarket Daily UP/DOWN markets via BlockRun's Polymarket
   MCP tools (x402 pay-per-use, bypasses geoblocking).
3. **Decision rule:** If Synth signal confidence > Polymarket consensus by
   ≥2% (positive delta), execute the trade. If Synth signal diverges from
   consensus by >8% (negative delta), trade against consensus.
4. **Gap-event filter (4-tier Kelly sizing):**
   - <1.5% gap from prior close → Proceed (full Kelly)
   - 1.5-2.5% gap → Scale half Kelly
   - 2.5-4.0% gap → Scale quarter Kelly
   - >4.0% gap → Skip entirely
5. **Stack:** DeepSeek V4 Flash + Synth API + BlockRun x402 + Polymarket CLOB
6. **Schedule:** Daily cron job — if opportunity exists, trade; if not, wait

**Why this matters for GTA:**
- No bridge needed — trade directly from Base wallet USDC
- No KYC — Polymarket is permissionless
- No API keys — BlockRun's Polymarket tools are wired
- Proven model — 0xJeff's agent is live and profitable
- CLARITY Act market is the obvious first trade (35.9¢ YES as of Jul 28)

**GTA Polymarket integration (planned):**
- Trade CLARITY Act YES/NO based on macro analysis
- Oil UP/DOWN markets (same pattern as 0xJeff)
- Use Synth API or our own signal generation
- Gap-event filter adapted for crypto prediction markets

## Kraken Spot (Third Venue)

**Status:** ✅ Free public API, no key required. Ready to add to arb scanner.

**API:** `https://api.kraken.com/0/public/Ticker?pair=XBTUSD,ETHUSD,SOLUSD`
**Type:** Spot (not perp)
**Rate limits:** Generous for public endpoints

**Why Kraken matters:**
- Third leg for triangulation — HL perp vs Coinbase spot vs Kraken spot
- More venues = more spread patterns to catch
- No KYC, no API key for read-only data
- Kraken Futures also available (separate API) for perp data

## Ondo Network (Future Venue)

**Status:** Announced Jul 28, 2026 — no developer tools released yet.

**What it is:** Ondo Finance (largest RWA tokenization player — OUSG, ONDO
token) announced their own execution layer. Think Hyperliquid but
non-custodial and RWA-native.

**Key features:**
- Enclaves for private, high-speed execution (CEX-like matching in TEE)
- Decentralized attestors for verifiability
- Blockchains for asset transfer settlement
- First app: Ondo Perps (perpetual futures)

**Why Ondo matters for GTA:**
- Another venue for arb — Ondo Perps + HL + Coinbase + Robinhood
- RWA-native perps — long/short tokenized Treasuries with leverage
- Non-custodial — aligns with GTA's self-custody model
- When API drops, wire into arb scanner as venue #4+

## Robinhood Chain (Future Venue)

**Status:** Pending OAuth token acquisition (user has account, needs to
complete KYC + authorization).

**MCP Server:** `https://agent.robinhood.com/mcp/trading`
**Auth:** OAuth 2.0 Bearer token (PKCE flow)
**Chain:** Robinhood Chain (US-compliant, RWA #1 by holders as of Jul 26, 2026)

**Why Robinhood matters for GTA:**
- US-compliant — no VPS geo-bypass needed
- RWA #1: 328K holders (flipped Solana at 312K)
- Virtuals.io competition live (60K USDG, Jul 22–Aug 5)
- BNY Mellon moving to 24/7 tokenized Treasury settlement — infrastructure
  aligns with agent treasury management

**Integration:** See `mcp-integration-strategy` skill for the OAuth PKCE
flow setup steps and `references/robinhood-mcp-oauth-flow.md` for the
full worked example.

**OAuth flow details (discovered Jul 27, 2026):**
- The correct authorization path is `/oauth/authorize` (NOT `/oauth`)
- Registration endpoint: `POST https://agent.robinhood.com/oauth/trading/register`
  with `{"redirect_uris":["https://api.gentechlabs.net/robinhood-callback"],"client_name":"GTA Trading","token_endpoint_auth_method":"none"}`
- Token exchange: `POST https://api.robinhood.com/oauth2/token/` with
  `grant_type=authorization_code` + `code_verifier` (PKCE)
- The MCP server requires a JWT Bearer token in the `Authorization` header
- Password grant (`grant_type=password`) is deprecated — returns
  "This version of Robinhood is no longer supported"
- User must complete KYC in the Robinhood app before the OAuth authorize
  screen will appear

**MCP tools (once authenticated):** Use `tools/list` to discover what's
available — spot prices, trading, account info.

## 4. Basis Detection

Basis = perp price - spot price, expressed in basis points (bps).
- **CONTANGO** (perp > spot, +bps): Short perp, Long spot
- **BACKWARDATION** (perp < spot, -bps): Long perp, Short spot

**Typical thresholds:**
- Report at > 5 bps (notable)
- Execute at > 10 bps (tradeable after fees)
- Close at < 3 bps (spread normalized)

**Funding rate:** Fetch from Hyperliquid's `meta` endpoint. Used to
calculate carry cost.

## 5. Across Protocol Bridge (Base → Hyperliquid)

Hyperliquid uses **Across Protocol** (not a native bridge) for deposits
on Base chain. Chain ID **999** = Hyperliquid on Across.

**Bridge contract (SpokePool) on Base:**
`0x09aea4b2242abC8bb4BB78D537A67a245A7bEC64`

**Quote API** (free, no key):
```
GET https://app.across.to/api/suggested-fees
  ?originChainId=8453
  &destinationChainId=999
  &inputToken=0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913  (USDC on Base)
  &outputToken=0xb88339CB7199b77E23DB6E890353E22632Ba630f  (USDC on HL)
  &amount=<raw_usdc_amount>
  &recipient=<user_address>
```

**Deposit-addresses API** (requires Across API key — embedded in
Hyperliquid frontend, not publicly available):
```
POST https://app.across.to/api/deposit-addresses
Authorization: Bearer <api_key>
Body: { destination: { token: { chainId, address }, recipient },
        refundAddresses: [{ namespace: "evm", address }] }
```

**Deposit flow:**
1. Approve USDC for the spoke pool contract
2. Call `depositV3(depositor, recipient, inputToken, outputToken, inputAmount,
 outputAmount, destinationChainId, exclusiveRelayer, quoteTimestamp,
 fillDeadline, exclusivityDeadline, message)` on the spoke pool.
      **IMPORTANT:** The function is `depositV3` (selector `0x7b939232`),
      NOT `deposit` (selector `0xd2645d20`). The old `deposit()` does NOT
      exist on this contract. Using `deposit()` will revert silently with
      no error message — you must use `depositV3()`.

      Always use the web3.py Contract object with a minimal ABI for ABI
      encoding rather than manually constructing calldata. The built-in
      `build_transaction()` method handles the encoding correctly.
3. Wait ~3 seconds for the bridge to complete
4. Funds appear on Hyperliquid L1

**Treasury address (EOA, validators-controlled):**
`0x8d68eFBf06fb8cf932518bcB53705E674C4852DC` — can receive USDC but
requires the Across mechanism to credit the correct user.

**Pitfalls:**
- The `deposit-addresses` endpoint requires an Across API key (403 w/o it)
- **exclusiveRelayer changes between quote requests.** The Across API may
  return a different `exclusiveRelayer` address each call. If you cache a
  quote and reuse it, the contract reverts with no error data. Always
  use the freshest quote.
- **depositV3Now() with empty exclusiveRelayer:** Setting
  `exclusiveRelayer = 0x0` allows any relayer to fill after the 5-second
  exclusivity window. Useful when the quote API is rate-limited, but you
  still need a fresh `outputAmount`.
- The deposit function selector must match the exact Across V3 deploy.
  **Use `depositV3()` (selector `0x7b939232`), NEVER `deposit()` (selector
  `0xd2645d20`) which does NOT exist on this contract.**
- Gas on Base is ~$0.0002/tx — very cheap (~4,000 txns per $1 ETH)
- USDC allowance must be >= deposit amount. If you approved $20 but
  try to deposit $20.99, `estimate_gas` will revert with
  `"ERC20: transfer amount exceeds allowance"`
- **Bridge relay may NOT complete even though the Base tx confirmed.**
  The Across relay for Hyperliquid (chain 999) may not be consistently
  serviced by relayers. In testing (Jul 26, 2026), the deposit succeeded
  on Base but funds never arrived on Hyperliquid even after the 3-hour
  fill deadline passed. The $20.99 is stuck in the spoke pool contract.
  - Refund/withdraw functions weren't findable from bytecode selectors
  - The `deposit-addresses` API (which would give a proper deposit
    address) requires an Across API key (403)
  - If this happens, use the Hyperliquid UI (app.hyperliquid.xyz via VPN)
    for deposits instead — it generates a valid deposit address with
    proper relay coverage
  - **Update Jul 26:** Direct send to HL treasury EOA on Base
    (0x8d68eFBf06fb8cf932518bcB53705E674C4852DC) does NOT credit sender's
    account. The Across deposit-addresses mechanism is the only verified
    path for Base → Hyperliquid deposits.
- When checking if funds arrived, check both `clearinghouseState` (perp)
  AND `spotClearinghouseState` (spot). Funds arrive in spot first.

- To check if a previous bridge deposit was relayed:
  1. Compute the relay hash: `getV3RelayHash(V3RelayData)` on the proxy
  2. Check `fillStatuses(bytes32 relayHash)` — returns 0 (unfilled),
     1 (filled), or 2 (requested slow fill)
  3. Status 0 after the fill deadline means the relay never completed —
     funds are stuck in the spoke pool with no depositor-initiated refund

### CCTP Alternative (when Across relayers fail)

Circle's Cross-Chain Transfer Protocol (CCTP) is an alternative bridge path
that bypasses the Across relayer network. CCTP burns USDC on the source chain
and mints it on the destination — no third-party relayers needed.

**Current status (Jul 2026):** Untested — blocked by lack of ETH for gas on
Arbitrum. If this path is pursued, bridge a small amount of ETH alongside
USDC for gas, or use Q402 gasless sends on Arbitrum for the final leg.

**Direct Base send to treasury (tested, FAILED):**
Sending USDC directly to `0x8d68eFBf06fb8cf932518bcB53705E674C4852DC` on
Base (Hyperliquid's treasury EOA) did NOT credit the sender's HL account
in testing. The Across deposit-addresses mechanism is required.

### Alternative: `depositV3Now()`

When the Across quote API is rate-limited/unavailable, `depositV3Now()` can
be used instead of `depositV3()`. It replaces `quoteTimestamp` with a
`fillDeadlineOffset` (seconds from current block time), so no external quote
is needed for timestamps. Selector: `0x7aef642c`.

**Pitfalls:**
- Still needs the `outputAmount` from a quote (otherwise contract reverts)
- `exclusiveRelayer = 0x0` (empty) means any relayer can fill after the
  5-second exclusivity window
- Requires working RPC for gas estimation (RPCs may be rate-limited)
- **`depositV3Now()` also reverts with no error data** when the quote
  parameters are stale or the exclusiveRelayer has changed. The revert
  is silent — no error string, no custom error — making it hard to
  distinguish "bad quote" from "contract paused" from "wrong selector."
  Always simulate with `eth_call` before sending.

### Across API Rate-Limiting

The Across quote API (`app.across.to/api/suggested-fees`) rate-limits
aggressively from VPS IPs. Observed behavior (Jul 26, 2026):
- First call from a fresh IP: works
- Second call within ~30s: HTTP 403
- After ~60s cooldown: works again
- `urllib.request` gets 403 faster than `curl` (different User-Agent)

**Workaround:** Use `curl` for the quote, then hardcode the values into
the Python script. The quote values are valid for ~60s (the
`exclusivityDeadline` is typically 5s, but the `fillDeadline` is 3600s).

### Direct Treasury Send (FAILED)

Sending USDC directly to the Hyperliquid treasury EOA on Base
(`0x8d68eFBf06fb8cf932518bcB53705E674C4852DC`) does NOT credit the
sender's Hyperliquid account. The transaction confirms on-chain but
the funds are not reflected in `clearinghouseState` or
`spotClearinghouseState`. The Across deposit-addresses mechanism is the
only verified path for Base → Hyperliquid deposits.

**Tested Jul 26, 2026:** $14.64 USDC sent to treasury address. TX
confirmed. HL account remained at $0.00. Funds are in the treasury's
wallet but not attributed to any user.

### Deposit Status via Across Indexer

Check if a deposit was detected by the Across indexer:
`GET https://indexer.api.across.to/hyperliquid-transfers?direction=in&user={ADDR}`
Returns `[]` if no transfers detected. The read indexer is less rate-limited
than `app.across.to`.

### RPC Fallback Chain

Free Base RPCs (in order of reliability):
- `https://base.drpc.org` — most reliable, least rate-limiting
- `https://base-mainnet.public.blastapi.io` — rate-limits after ~3 calls
- `https://1rpc.io/base` — rate-limits quickly
- `https://base-pokt.nodies.app` — alternative option

Rotate RPCs to avoid rate limits. Use `eth_chainId` as a quick health check.

### Proxy Architecture

The Across V3 SpokePool at `0x09aea4b2242abC8bb4BB78D537A67a245A7bEC64` is
an **EIP-1967 transparent proxy**. The implementation is at
`0x77aa19d49484cc88c2ca1c8527226e891c5c72d8`. To find it:
```python
storage_slot = "0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc"
impl = w3.eth.get_storage_at(proxy_address, storage_slot)
```

### Relay Status Debugging

To check if a depositV3 was relayed (after the deposit was made):
1. Encode the V3RelayData struct and call `getV3RelayHash()`
2. Call `fillStatuses(relayHash)` — 0 = unfilled, 1 = filled

```python
fill_sel = Web3.keccak(text="fillStatuses(bytes32)")[:4].hex()
fill_data = fill_sel + relay_hash[2:]
status = int(w3.eth.call({'to': PROXY, 'data': fill_data}), 16)
```

### Refund Limitations

Across V3 does **NOT** have a depositor-initiated refund function on the
SpokePool. The bytecode was analyzed against 4byte.directory and none of
the ~70 function selectors match `withdrawDeposit` or `refundDeposit`
variants. Refunds only happen through the relayer merkle-leaf system,
which requires coordination with Across relayers.

If a bridge relay fails:
- The funds remain in the spoke pool contract (safe, held with many others)
- Fill deadline passes → deposit expires → no auto-refund
- To recover: use the Across UI (across.to/bridge) on a personal device,
  or deposit again via the Hyperliquid app (app.hyperliquid.xyz via VPN)
- The deposit-addresses API at `app.across.to/api/deposit-addresses`
  requires an API key embedded in the Hyperliquid frontend (returns 403
  without it)

### Function Selector Discovery

When the ABI is not available, extract function selectors from the
implementation bytecode and look them up on 4byte.directory:

```python
from web3 import Web3
import requests

# Get bytecode
bytecode = w3.eth.get_code(implementation_address).hex()

# Search bytecode for known selectors
for sig in ['depositV3(...)', 'fillStatuses(bytes32)', 'getV3RelayHash(...)']:
    selector = Web3.keccak(text=sig)[:4].hex()
    if selector in bytecode:
        print(f'Found {selector} = {sig}')

# Or look up unknown selectors on 4byte
unknown_selectors = ['0x1b3d5559', '0x97943aa9']
for sel in unknown_selectors:
    resp = requests.get(f'https://www.4byte.directory/api/v1/signatures/?hex_signature={sel[2:]}')
    for r in resp.json().get('results', []):
        print(f'{sel}: {r["text_signature"]}')
```

Key Across V3 selectors (confirmed in implementation):
- `0x7b939232` = depositV3(address,address,address,address,uint256,uint256,uint256,address,uint32,uint32,uint32,bytes)
- `0xc35c83fc` = fillStatuses(bytes32)
- `0xd7e1583a` = getV3RelayHash((bytes32,bytes32,bytes32,bytes32,bytes32,uint256,uint256,uint256,uint256,uint32,uint32,bytes))

## 6. Execution (signal → trade)

GTA Signal generates direction + leverage at 7AM/7PM ET.
GTA Watcher monitors open positions every 30 min.
GTA Arb Monitor scans basis hourly.

**Agent wallet mode:** trade-only key that can place/cancel orders but
CANNOT withdraw funds. User retains full custody.

**For automated execution (future):**
- Hyperliquid Python SDK `exchange.order(name, is_buy, sz, px, ...)`
- Coinbase spot via CDP API (requires CDP API key + wallet delegation)
- Basis trade: short perp on HL + buy spot on Coinbase (contango)
- Basis trade: long perp on HL + sell spot on Coinbase (backwardation)

**Execution engine (built Aug 3, 2026):** `scripts/gta_executor.py` + `scripts/test_gta_executor.py` — reads `.gta-arb-state.json`, applies the rule set (execute ≥10bps, report ≥5bps, close <3bps, stop-loss +50bps widen, 7-day max hold), emits a decision (ENTER/HOLD/CLOSE/SKIP) and an order plan. **Dry-run by default — safe, no funds move.** Real mode activates only with `GTA_HL_KEY` env var set; otherwise it raises `NoExecutionKeyError` and refuses to fake a successful order. Cron `a11f9e0205f3` runs it every 3h, reports decisions to HQ. Build plan: `09-Green Room/specs/gta-execution-engine-build-plan.md`.

**Layer 3 seed — agent-flow ledger (DONE Aug 3, greenlit by Jordan):** `gta_executor.py` now appends every decision (ENTER/CLOSE/HOLD/REPORT/SKIP) to `agent-flow.jsonl` (append-only, never mutated), each tagged with `agent_id` (default `gentech-gta`, overridable via `GTA_AGENT_ID` so Forge/ClawWork/arena competitors log under their own id), timestamp, action, symbol, reasons, mode, executed. It logs HOLD/SKIP too (flow includes "stayed out") and never fails the trade on a logging error. Verified: executor runs, appends attributed record, 9/9 tests pass. This is the attributable dataset the agent-sentiment aggregator reads later (see section 0b + `09-Green Room/specs/agent-sentiment-stack-assessment.md`). Next when ready: aggregator over `agent-flow.jsonl` → per-agent net positioning / confidence → cross against `narrative-rotation.py` → expose as MCP tool.
- **Current hard blockers (must surface, not hide):** (1) no Hyperliquid execution private key on the box → real order placement is a stub until `GTA_HL_KEY` exists (use a trade-only key that can't withdraw — user keeps custody); (2) Base→HL bridge historically broken (Across relayers stuck funds Jul 26), `deposit_v3_fixed.py` referenced in skill is missing; (3) KeeperHub `kh_` key not provided (blocked queue #1).
- **Test** with: `cd /root/.hermes/profiles/gentech/scripts && python3 test_gta_executor.py -v` (9 tests, no key needed) and `python3 gta_executor.py` against real state.

## 7. Position Tracking & Risk

**Per-trade parameters:**
- Entry spread (bps)
- Position size
- Stop-loss: spread widens > 50 bps from entry
- Take-profit: spread normalizes < 3 bps
- Max hold time: 7 days (funding cost erodes profit)

**Self-refueling:** Monitor ETH balance on Base. If < $0.50, swap
$1 USDC → ETH. Gas on Base costs ~$0.0002/tx.

## 8. Temporary Fund Monitoring

When waiting for a bridge deposit to arrive, create a short-lived cron with
a repeat count so it auto-expires:

```bash
cronjob action=create name="Fund Monitor" script="hl_fund_monitor.py" \
  schedule="5m" repeat=6 deliver="telegram:-1003863540828" \
  prompt="Run the script and report result."
```

> **⚠️ Delivery routing (up-to-date):** The Telegram group **Strategies `-1002916759037` was RENAMED → "Treasury"** (Jordan, Sep 7 2026 — same chat ID now = Treasury). Finance/DeFi/portfolio/yield/market routing targets Treasury `-1002916759037`. No active cron delivers to a retired Strategies chat (verified: the old GTA jobs Arb Monitor `81f57cc36b11`, Watcher `ab75cb79f6ec`, Signal `ac3040c8bf15`, CLARITY tracker `8d40bf2cbe43` are deleted from live jobs.json). Also note GTA is currently **detection-only** — the monitor reports opportunities but execution (bridge → trade both legs → auto-close) is not yet wired; it's a decision partner, not an autonomous trader.

Key design:
- `repeat=N` — auto-cancels after N runs (won't run forever)
- `script` — no_agent mode for silent checks, or LLM-driven for formatted reports
- Each run checks the Hyperliquid spot state for new balances
- When funds land, the cron reports and can be killed manually

## 9. Quiet Hours

All GTA crons should be silent between 11pm-6:30am ET (3:00-10:30 UTC).
Add this check at the top of each script:

```python
from datetime import datetime, timezone
_hr = datetime.now(timezone.utc).hour
if 3 <= _hr < 10 or (_hr == 10 and datetime.now(timezone.utc).minute < 30):
    sys.exit(0)
```

## Output Format

All reports to the user should follow this format:

```
🔁 GTA ARB SCAN — <TIME> UTC
<asset> — <CONTANGO/BACKWARDATION> <X.X> bps
  Perp: $X.XX | Spot: $X.XX
  Trade: <direction>
```

Split long messages into **Part 1/Part 2** by default (Telegram ~4000 char
limit). Always split before sending.

## 10. Decision-Partner UX Pattern

GTA is not an autonomous trading bot — it's a **decision partner**. The core interaction:

Same market data, different lenses depending on what the user wants to do:

| Mode | What GTA Sees | Action |
|------|-------------|--------|
| **Arb** | Spread +10bps | Short perp / long spot |
| **Yield Farm** | ETH lending 8% vs 12% | Supply highest yield |
| **Narrative** | Fear & Greed 27, BTC dom rising | Rotate to PAXG/stable |
| **Macro Hedge** | FOMC Wednesday, oil meeting | Shrink size, move to cash |
| **Rainbow** | SOL perp funding +40% APR | Stake SOL / farm funding |

### Macro Event Tracking

GTA tracks the following macro events and adjusts recommendations:

**CLARITY Act (H.R. 3633):**
- Status: Merged draft published Jul 28 (Senate Banking + House Agriculture)
- Ethics provision added for first time (banning federal officials from issuing digital assets)
- **Jul 28 update:** Senate put CLARITY Act on hold to prioritize Russia sanctions bill
- Motion to proceed: Expected Mon/Tue Jul 28-29 (may slip)
- Floor vote: Pushed to final days before August 8 recess
- Polymarket "signed into law in 2026?": ~35.9¢ (dropped from 37.8¢ on Russia sanctions news)
- Kalshi "Will Senate vote?": ~57¢ (expires Aug 8)
- Holdup: Ethics provision + Russia sanctions bill priority + midterm politics
- User's thesis: BTC could drop to $52-56K, bottom not in, 3-4 months without CLARITY Act
- Cron tracker: `008ba45a22f0` (paused Jul 27)
- Impact if passed: Regulatory clarity for tokenized RWAs, stablecoins, and agent trading
- Impact if delayed: Continued uncertainty, BTC downside pressure, institutions wait
- **Key insight:** Democrats have no incentive to give Trump a crypto win before midterms.
  The ethics provision was their price; now they're in no rush to move it forward.
  CFTC/FTC could act independently but won't without Congressional direction.

**FOMC:** Wed Jul 29 — rate decision, dot plot, press conference
**Oil meeting:** Tue Jul 28 — OPEC+ production decision
**Unemployment + Core PCE:** Fri Aug 1

### Interaction Flow

```
MACRO EVENT DETECTED (FOMC / CLARITY Act / Oil meeting)
  ↓
GTA analyzes: what does this mean for current positions + arb landscape
  ↓
GTA presents 2-3 clear options with reasoning
  ↓
User picks ONE
  ↓
GTA executes
  ↓
GTA reports outcome + next decision point
```

**Key principles:**
- The user stays in control of ALL directional decisions
- GTA does the research, the math, the execution
- The user makes the call — it's still their money, their strategy
- The agent prompts *with* context, never *without* it
- Every decision surfaces the relevant macro data (tweet, on-chain, funding rates)
- Over time, the user becomes a better trader because they see the reasoning behind every recommendation

**Example prompt to the user:**
```
🚨 GTA MACRO ALERT
This week: CLARITY Act vote Mon + FOMC Wed + Oil meeting Tue

Your AVAX arb is +$1.23 profit.
Macro vol incoming:
  [1] POWDER MODE → Move to USDC, wait
  [2] TRADE VOL → Spreads will blow out, arb window
  [3] NARRATIVE ROTATE → PAXG hedge, short BTC

What's your call?
```

This pattern applies across ALL GTA modes — arb, yield farming, narrative rotation. The agent never executes a macro-level decision without the user's input.

## 11. Flash Loan Agent Execution (Future)

Flash loans are **better for agents than humans** — purely mechanical, no judgment needed, just math and execution speed.

**Why agents win at flash loans:**
- Humans are too slow — by the time you see an opportunity, open a DeFi app, connect your wallet, and click "approve," the arb is gone
- Agents monitor, calculate, and execute in under a second
- Flash loans are smart contract calls — agents can make smart contract calls
- If any step fails, the whole thing reverts — no loss. If it succeeds, pure profit.

**GTA flash loan pipeline (planned):**
1. **Monitor** — scan for arb opportunities across venues (already done by GTA Arb Monitor)
2. **Calculate** — is the spread > gas + fees? (trivial math for an agent)
3. **Execute** — borrow via flash loan (Aave, Balancer, dYdX), arb the spread, repay, keep the profit
4. **All in one tx** — atomic, no counterparty risk

**Key insight:** The only missing piece is wiring our GTA monitor to an execution engine — and that's a build, not an invention. The detection layer already works.

## 12. Demo Site Card Pattern

When adding a subdomain dashboard to the demo site (`demo.html`), follow this pattern:

- **Title:** Full name with abbreviation in parentheses, e.g. "GenTech Trading Agent (GTA)"
- **Description:** What it does + what's coming next (e.g. "Flash loan execution engine incoming — agents that borrow, arb, and repay in one transaction")
- **Link:** "→ Live Dashboard" pointing to the subdomain
- **Icon + Status badge:** ● LIVE badge

This avoids confusion (GTA = Grand Theft Auto) and sets expectations for roadmap features.

## 13. GTA Naming Convention

Always use the full name **"GenTech Trading Agent (GTA)"** on any public-facing material. Never just "GTA" alone — it reads as Grand Theft Auto. The abbreviation in parentheses lets people connect the acronym to the full name after the first mention.

## 12. MCP Server Packaging (Phase 2 Distribution)

The GTA Arb scanner is packaged as a zero-dependency Python MCP server at:
```
/root/repos/gta-arb-mcp/
├── server.py    — MCP stdio transport server
├── README.md    — Documentation
└── .gitignore
```

**MCP tools registered:**
- `scan_arb` — Scan all 7 assets (BTC, ETH, SOL, AVAX, LINK, ONDO, PAXG) for cross-venue spreads

**Registration in Hermes:**
```bash
hermes config set mcp_servers.gta-arb '{"command": "python3",
  "args": ["/root/repos/gta-arb-mcp/server.py"],
  "enabled": true, "timeout": 30, "connect_timeout": 10}'
```

**Architecture:**
- No external dependencies (pure Python stdlib)
- Stdio transport (stdin/stdout JSON-RPC)
- Implements `tools/list` and `tools/call`
- Test: `echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | python3 server.py`

**Distribution path (Phase 2):**
1. ✅ MCP server built and registered in Hermes
2. ⬜ Push to GitHub (needs token/SSH)
3. ⬜ Publish as PyPI or npm package
4. ⬜ Document for developer onboarding

## References

- **Agentic Treasury MVP build (fused command center + coin rainbow dashboard, Aug 4):** `references/agentic-treasury-mvp-build.md` — full reproduction recipe, verified output, and the nginx-403 / stale-API-key / no-DNS pitfalls.
- **Solana Homebase treasury (Jupiter leg + orchestrator + Superteam tranche-2, Aug 5):** `references/solana-homebase-treasury.md` — the Solana-settlement Agentic Treasury, gta_solana_leg.py constants, the quote-without-keypair dry-run fix, same-chain-swap-not-bridge rule, and the grant tie-in.
- **Wallet funding addresses + verification (Aug 5):** `references/wallet-funding-addresses.md` — verified addresses for CDP server account / KeeperHub / Algorand / Solana, the "verify against the live system, don't derive from a secret" rule, and the exact funding amounts + priority order.
- **Treasury live demo capture (Aug 5):** `references/treasury-demo-capture.md` — the self-running `treasury_demo_capture.py` pattern (fused report + on-chain positions + Solana quote + settlement proof, read-only), and how to deploy it as the 2nd demo page (`treasury-demo.html`) including the nginx-403-on-write_file pitfall.

## 13b. Solana-homebase DeFi-community edge (Jordan's framing, Aug 5)
The *strategic* reason to make Solana the treasury homebase — beyond fast/cheap USDC — is that
**Solana is a liquidity network with its own builder communities**, all reachable from ONE wallet
through Jupiter (no bridging between DEXs):
- **Meteora** — dynamic liquidity pools + concentrated LP strategies
- **Orca** — concentrated-liquidity DEX, tight-range yield
- **Raydium** — the central AMM + staking/farms
- **+ 30 more routed via Jupiter** (Phoenix, Jito, etc.)

Idle USDC earns yield across the whole ecosystem, and each community is a place agents transact.
This is the headline story to lead with in any Solana demo/video/submission — it's the edge over EVM.

**Reusable submission asset:** one Solana-homebase MVP doubles as multiple entries — a grant's
tranche-2 unlock, an Arc demo, a Colosseum/Solana-hackathon submission, and a live reference
product. Build once, submit many times. The Solana Foundation USA grant (up to $10k, avg $8.2k,
~1wk response) and Superteam Agentic Engineering (200 USDG, tranche-2 needs Solana-integrated MVP
+ $200 coding-subs receipts) both feed the same engine. **Colosseum next window: Sep 28 – Nov 2, 2026.**
- Hyperliquid Python SDK: `/root/repos/hyperliquid-python-sdk/`
- Across Protocol: https://across.to
- GTA repo: https://github.com/ProtoJay4789/gentech-treasury-trader
- Coinbase for Agents: CDP API key env vars
- Q402 gasless payments: BNB trial (2000 free sends, expires Aug 15)
- Across V3 contract investigation (proxy, selectors, fill status): `references/across-v3-contract-investigation.md`
- Bridge Script (working depositV3): `/root/.hermes/profiles/gentech/scripts/deposit_v3_fixed.py`
- **GTA executor + Coinbase CDP SDK setup (env vars, async await pattern, auth-verification):** `references/gta-executor-and-cdp-sdk.md` — the dry-run-first execution engine pattern and how to wire `cdp-sdk` for the Coinbase spot leg.
- **Coinbase CDP swap execution blocker (gasFee:null upstream bug + method-signature fixes):** `references/coinbase-cdp-swap-execution-blocker.md`
- **Composio audit (authorized-proxy layer):** `references/composio-open-source-audit.md` — SDK is MIT open-source but auth/execution backend is still Composio cloud; "open-sourced SDK ≠ self-hostable backend" lesson for the authorized-proxy build.
- **KeeperHub MCP setup + wiring (DoraHacks Agents Onchain, kh_ key, execution paths):** `references/keeperhub-mcp-setup.md`
- **Delphi Agent Arena (Gensyn × Delphi prediction-market trading comp, Aug 2026):** `references/delphi-agent-arena.md` — zero-real-money-risk testnet comp ($10K, live Aug 10–24). `@gensyn-ai/gensyn-delphi-sdk` (ESM-only, `competition-testnet` network, keyless `health` smoke test), public competition subgraph for market reads, `m.spotImpliedProbabilities` field, contrarian strategy scaffold, and the human-gated testnet API key at delphi-api-access.gensyn.ai. Use when building an autonomous agent to trade the Arena.
- Robinhood MCP OAuth flow: see `mcp-integration-strategy` skill, `references/robinhood-mcp-oauth-flow.md`
- MCP auth patterns for URL-based servers: see `mcp-integration-strategy` skill, "URL-Based MCP Server Authentication" section
