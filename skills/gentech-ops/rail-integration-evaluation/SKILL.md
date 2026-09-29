---
name: rail-integration-evaluation
description: "Use when asked to evaluate a chain, rail, venue, or platform — HQ handoffs included."
version: 1.0.0
author: Gentech
license: MIT
tags: [research, defi, treasury, integration, chain-evaluation, rails]
---

# Rail / Home-Chain Integration Evaluation

**Trigger:** Jordan shares a chain, protocol, or tokenized-asset platform and wants to know
whether/how to integrate it as a treasury rail or home chain. Phrases that fire this:
"give it the full GenTech workup", "add them as home chains", "can we integrate ourselves",
"start searching these out and seeing how we can integrate". Also applies to any new
settlement rail, tokenized-equity platform, or agentic-payment network.

## The pattern (do this in order)
1. **Extract the source** — web_extract the tweet/video/link for the actual claim. Don't
   assume from the title.
2. **Vault check first** — search the vault for the name before researching (avoid duplicate
   intel). `search_files` for the platform name + `RWA|tokenized|agentic`.
3. **Research the integration surface** — web_search + web_extract the official docs. Look for:
   - Official SDKs (JS/TS, Python, Java, Go) — a real API means buildable, not vaporware.
   - API base URL + auth model (API key headers, OAuth, self-custodied vs managed wallets).
   - Order/transaction types (market/limit, proxied vs managed).
   - Sandbox/testnet + faucet (can we validate with no real money?).
   - Which chains it settles on (is it on one of OUR home chains — Avalanche/Base/Solana?).
   - **The chain set may be QUERY-ONLY, and a zero mention of our home chain IS the finding.** A
     tenant-configured platform publishes no fixed chain table, so count mentions of each home chain
     in the FULL docs text before assuming support; proven — `avalanche`/`43114`/`AVAX` appeared zero
     times while `solana` appeared 206, and the docs then told you to query the enabled set rather
     than read a list. Absence from the docs is a constraint to state, not an assumption to make in
     either direction: do not assume unsupported, and never assume supported because the product is
     "multi-chain". Say which axis you measured on.
   - **Verify "does an API exist" via the docs INDEX, not a guessed URL.** A 404 on
     `docs.example.com/docs/<product-name>` proves nothing — the page may just not exist
     at that path (verified false-negative risk on Jupiter Universal Deposit, Sept 2026:
     guessed URL 404'd, but fetching `developers.jup.ag/docs/llms.txt` — the full 98KB
     index — and grepping it confirmed no Universal Deposit section exists, i.e. a
     real "UI-only launch" verdict). Fetch the index (`/docs/llms.txt`, `llms-full.txt`,
     sitemap, or the monthly `/changelog`), grep it for the product name. Index has no
     section → UI-only → verdict Watch, re-check `/changelog` monthly. A guessed-URL
     404 produces confident-sounding "no API" verdicts that are simply wrong.
4. **Map to our stack** — does it fit the AAE thesis (self-custodied wallets, x402 rails,
   ERC-8004 identity, pre-execution governance)? "Don't compete, integrate" — wallet providers
   and custody rails are integration targets, not competitors.
5. **Honest caveats** — KYC/AML gating, custodial vs permissionless, human-gated steps.
   Flag what ONLY Jordan can do (signup, KYC, production keys).
6. **Verdict + next actions** — fit score (★), what Labs scaffolds, what Jordan does
   (human-gated checklist), where it sits in the treasury.

## Worked example — Dinari dShares (Aug 15, 2026)
- **What:** 724 tokenized US stocks/ETFs (full S&P 500) open to US investors, settling on the
  Dinari Financial Network (DFN), an **Avalanche L1** omni-chain orderbook. Also Arbitrum,
  Base, Plume; Solana imminent. dShares backed 1:1, dividends + corporate actions preserved.
- **Integration surface (verified):** B2B enterprise API `api-enterprise.sbt.dinari.com`
  (sandbox). SDKs `@dinari/api-sdk` (JS/TS), `dinari-api-sdk` (Python), Java, Go. Auth =
  API Key ID + Secret (headers `X-API-Key-Id`, `X-API-Secret-Key`) from Partners dashboard.
  Market + limit orders via Managed (Dinari creates tx) or Proxied/EIP-155 (self-custodied,
  we sign). Sandbox faucet mints 1,000 mockUSD. Cash leg is **USD+** (yield-bearing stablecoin).
- **Why it fits:** self-custodied wallets supported (AAE pattern), on our home chain (Avalanche),
  USD+ yield-bearing cash leg, complements Solana/Robinhood rails.
- **Caveats:** KYC/AML gating (human-gated), API integration not pure on-chain swap, managed
  vs self-custodied is a real design choice.
- **Verdict:** ★★★★☆ — greenlit as treasury integration candidate. Jordan: Partners signup +
  sandbox key + KYC. Labs: scaffold `dinari-rail` (Python SDK, sandbox test with faucet).

## Four chains Jordan flagged (Aug 15, 2026) — integration surfaces
- **NEAR** — NEAR AI Agent Market (market.near.ai): decentralized marketplace where agents
  transact with full economic agency, powered by NEAR Intents (chain abstraction, $25B volume,
  $41M fees). Compatible with OpenClaw, Claude, Codex. Sell-side: list an agent that bids on
  tasks and gets paid in NEAR. Also x402-native.
- **XRP Ledger** — XRPL AI Starter Kit (xrpl.org/docs/agents): x402-powered payments using XRP
  and RLUSD. Deterministic finality (3-5s), predictable costs, native multi-currency + DEX,
  no smart-contract risk. Claude Skills file + MCP docs server + tutorial. Testnet faucet.
  Sell-side: register an agent that transacts on XRPL.
- **Aethir** — decentralized GPU cloud (435K+ GPU containers, 93 countries), up to 86% cheaper
  than AWS/Azure/GCP. Grants, compute credits, LLM aggregator credits (50% discount), hackathon
  sponsorship. Sell-side: we're a *consumer* of compute (not a seller) unless we resell GPU
  capacity. Fit = infrastructure cost reduction + grant/credit opportunities.
- **Quant** — Overledger universal API connector (interoperability between TradFi + blockchains).
  Plugged x402 into Fusion (70+ chains, institutional settlement). **apis.io rates it agent
  readiness 3/100 (human-only)** — no MCP server, no machine-readable contract. Fit = weak for
  autonomous agent integration; institutional DvP settlement angle only.

## Worked example — Meteora DLMM (Sept 12 2026) — the BEST agent-ready rail found so far
- **What:** Solana's largest LP venue. DLMM = **bin-based** concentrated liquidity (discrete
  price bins), plus DAMM v1/v2, DBC, vaults.
- **Agent surfaces (all verified in docs):** an official **Agent Skill** that explicitly lists
  **Hermes** as a supported runtime (`MeteoraAg/meteora-invent/skills/meteora`); a read-only
  Documentation MCP; `llms.txt`; TypeScript + Rust SDKs (`@meteora-ag/dlmm@1.9.14`); a free REST
  Data API (`https://dlmm.datapi.meteora.ag`, 30 RPS, Swagger UI); 81 config-driven studio
  commands; published audits. Their skill's safety model mirrors ours (dryRun default,
  simulate-before-send, confirm before mainnet, re-read state after).
- **Devnet uses the SAME program ID as mainnet** (`LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo`)
  → the whole flow is testable with zero real capital. Rare and valuable.
- **Official base URL gotchas:** DLMM base is `https://dlmm.datapi.meteora.ag` (30 RPS), not
  guessed hostnames. Sort key is flat (`volume_24h`), but the volume value in returned pool
  objects is nested (`.volume["24h"]`). The user portfolio endpoint is `GET /portfolio?user=<wallet>`.
- **Shape intel applies here.** DLMM exposes `Spot` / `Curve` / `BidAsk` strategy families — the
  SAME families our shape detector drives (LFJ had them; Blackhole/Algebra does NOT). A bin venue
  is where our shape logic belongs.
- **A documented strategy IS "accumulate an asset via LP":** docs list "DCA into a token" =
  deposit quote single-sided + Bid-Ask/edge bins below spot → fills convert into the base token
  as price falls while fees accrue. When Jordan describes a strategy, check whether the venue
  already productises it — don't rebuild what the protocol ships.
- **The data API's `tvl` field is `tvl`, not `liquidity`** — querying the wrong key silently
  returned $0 for every pool and looked like "all pools are dead". Dump one full record to learn
  the schema before aggregating.
- **Cross-check the venue's own APR against a fee-based calculation; they disagree a lot.**
  Same pool: venue `apr` 163% vs 24h-fee annualisation 596%. Annualising one day of volume is
  the fantasy-APR trap — report both, label both as non-forecasts, and treat sustained volume
  as the only real input.
- **Check pool DEPTH before yield.** TAO pools ran $4K-$62K TVL — the honest constraint was
  size, not APR. A great rate on a $4K pool cannot absorb real capital.
- **`has_farm: false` is a POSITIVE signal** where emissions tokens are a melting ice cube: pure
  swap-fee revenue has no token-dump pressure and no unstake friction.
- **Unified multi-rail ruleset pattern:** when writing rules across heterogeneous chains
  (e.g., Avalanche EVM vs Solana DLMM), encode a common `defaults` schema (mode, capital split,
  schedule, dip ladder triggers, safety constraints) and let per-rail blocks override only
  chain-specific details (gas asset, venue, targets, signing path). This keeps cross-rail rules
  invariant while scaling out new venues.
- **Verdict ★★★★☆** — best agent-ready rail evaluated. Blockers were capital + pool depth, not
  capability.

- **Verify a rail's LAUNCH-DAY YIELD before rating it a yield home — venue availability is not utility.**
  A launch list ("Aave + Aerodrome day one") tells you contracts deployed, not that capital earns.
  Read the actual rates and depth. Arc mainnet, launch day (Sept 16 2026): Aave V4 USDC supply
  APY **0.00%** (Main spoke `suppliable` $0 against a full $56M cap) and Morpho Blue Arc USDC
  **0.00%** ($148.0M supplied vs **$9.79** borrowed); Aerodrome Slipstream Arc $300.8K TVL with
  only $27.7K on the USDC side. Verdict was WATCH, not deploy. **A lending market with supply >>
  borrow prints 0%** — read `supplyApy`/`suppliable` (Aave API) and `supplied` vs `borrowed`
  (Morpho API) together; a big TVL number is a supply-side fact and says nothing about yield.
- **Circle/Arc docs are agent-readable markdown — fetch the `.md` / `llms.txt` endpoints, don't scrape the site.**
  `https://docs.arc.io/llms.txt` (index), `<page>.md` (raw markdown of any doc page, e.g.
  `/arc/references/contract-addresses.md`, `/arc/references/evm-differences.md`),
  `https://developers.circle.com/llms.txt`. This is how to pull contract tables (USDC, CCTP,
  Gateway, USYC) as clean text. **Then verify each address on-chain** (`eth_getCode`, `eth_chainId`)
  — a docs table is a claim; bytecode is proof. Docs also LAG: Circle's own llms.txt still read
  "Arc is currently available on Testnet only" while mainnet sat at block 21.15M.
- **The Arc RPC requires a User-Agent — a bare request returns HTTP 403.** Send a UA
  (`GenTech-Steward/1.0`) on every call; bare urllib/curl gets Cloudflare
  `403 / error code: 1010`. No fallback endpoint exists (rpc.arc.io,
  arc-mainnet.rpc.circle.com, rpc.arc.network do not resolve) — the UA is the only fix.
  **Mechanism that bites:** our scripts default to BARE urllib, so a naive Arc probe reads
  403 and can be mis-filed as "chain is down" or parsed as a zero. In any rail adapter,
  make the RPC helper send a UA and RAISE on transport failure — never return a falsy
  value, or a dead endpoint masquerades as a zero balance. Reference adapter:
  `arc_rail.py` in the treasury script set (UA on every request, raises instead of
  returning falsy, prices gas in USDC cents, reports read_capable/write_capable).
- **Arc has TWO USDC decimal counts — off by 10^12 if you mix them.** Native gas token is
  **18-decimal** USDC; the ERC-20 at `0x3600…0000` is **6-decimal** (verify with
  `decimals()` on-chain, don't assume). Any code using one decimal constant for both
  "USDCs" produces magnitudes 10^12 off. Price gas on the native side, token flows on the
  ERC-20 side, decimal-split explicit in both.
- **On launch day of a new rail, the deliverable is RAIL READINESS, not capital action.**
  Arc is a live rail but NOT a yield home (day-one yield 0.00% — see above), so the work
  is making the rail safe to drive so later action needs no debugging under pressure:
  (1) build/verify an adapter against LIVE RPC reads; (2) register the chain in
  `exit-rails.json` as `WATCH_NOT_YIELD` (RPC quirks, decimals, gas model, CCTP domain,
  funding path, deploy triggers); (3) add the token to `capital-guard-rails.json` with a
  non-ACTIVE status so the guard REFUSES entry for the right reason — verify the refusal
  actually returns, a check that can't fail isn't a check; (4) run the existing
  venue/venue-compat selftests to prove nothing broke. **Flag the known gap honestly**
  (e.g. venue-compat not yet listing the new venue) — both layers refusing (one by
  status, one by unknown-venue) agree today, but promotion to ACTIVE will fail for the
  wrong reason until the gap is closed. Funding path for launch-ready rails is native
  (CCTP burn on source chain → mint on destination), never a traditional bridge.
- **Enroll the venue matrix in the sync BEFORE trusting it.** A compatibility/venue
  script stored OUTSIDE the sync-listed vault directory (e.g. a repo-parent folder)
  escapes the sync drift protection entirely — edits never propagate to the copies the
  cron runs. If a guard/matrix script lives outside the synced dir, either move the
  canonical copy into the synced dir (with a comment in the sync script explaining where
  the working original lives — the convention `capital-guard.py` uses) or explicitly
  enroll its path in `sync-treasury-scripts.sh`. Then md5-verify ALL copies (vault,
  vault-synced copy, repos, profile) match.
- **Selftest every new venue, and make the refusal REASONED.** After registering a venue
  in the compat matrix, add a selftest case (`<venue>, deposit, {} → must refuse`) to the
  matrix's selftest suite — a check that cannot fail is not a check; a venue lookup that
  silently matches nothing 'passes' forever. The refusal should name its reasons ("no
  execution adapter + no yield venue"), not fall through by accident. Run the full
  selftest, then sync, then md5-verify.
- **Chain IDs: Arc mainnet is 5042; 5042002 is the TESTNET.**

## Dry powder vs transit rail — the hop-count rule beats the rate

When evaluating a rail as a HOME for dry powder / reserves, score BOTH axes and accept
only where both win:
1. **What it pays to WAIT** — read the actual supply APY and utilization of the rail's
   yield venues (Aave-style `supplyApy`/`suppliable cap`, Morpho-style `supplied` vs
   `borrowed`). Launch-day zero is common; a market with supply >> borrow prints 0.00%
   no matter how big the TVL looks. Compare against where the reserve sits NOW (e.g.
   base-asset money-market APY on the home chain) — the bar is "beat the current
   location", not "nonzero".
2. **How far it is from ACTION** — dry powder must sit ONE HOP from the venue it deploys
   into. Two hops = one bridge/CCTP step between the deploy decision and the deployment,
   on exactly the day speed matters. A rail that pays 0.00% AND is a bridge-hop away from
   every active venue loses on both axes at once — it is a TRANSIT RAIL, not a home.

**Transit-rail handling:** build/verify the adapter, register in exit-rails +
capital-guard with a WATCH status, document the decimal/gas/RPC quirks in the venue
matrix, refuse entry (reasoned: "no execution adapter + no yield venue"), set a
re-review date. Nothing else — "set up so we're good if we ever go over" means the rail
is drivable and refusing for the RIGHT reason, not that capital sits there.

**The flip case (machine-checked, never remembered):** if the ACTIVE VENUE moves to that
rail, or its reserve APY rises above the current reserve location's, the rail becomes
both earner and zero-hop home. Encode explicit deploy triggers (sustained APY threshold
for N days, USDC-side pool depth ≥ $X, reserve floor ≥ $Y) in the rail's config so the
machine flags the flip instead of a human remembering.

- **Chain IDs details (Arc):** ERC-20 USDC is the same address on both mainnet and testnet
  (`0x3600…0000`, 6 decimals, verified on mainnet); native USDC gas is accounted in 18
  decimals (divide by 1e12 to display). Arc-specific gotchas: `maxFeePerGas` floor 20 Gwei;
  `address(0)` sends revert; a system emitter `0xffff…fffe` logs EVERY USDC transfer
  (de-duplicate in any log reader); local sim needs `arc-anvil`, not vanilla anvil.
When revenue is $0 despite many live APIs + listings, diagnose BEFORE concluding it's a
marketplace/API/listing problem:
1. Read the revenue tracker (`revenue-tracker.json`): total_revenue_usd, tx_count, per-chain.
2. Count live revenue-capable APIs + live listings (registry).
3. **If supply + distribution are healthy but revenue is ~$0, the problem is DEMAND** — the
   agent economy is nascent (whole-ecosystem agentic volume ~$55M in 2026 vs $3.12T projected
   by 2031). We're early in the right business, not in the wrong business.
4. Paths to near-term income while waiting: (a) sell to humans not just agents, (b) go where
   money already is (hackathons, treasury rails like Dinari), (c) go DEEP on the 1-2 marketplaces
   with real volume (e.g. AgentLux First-Hire Guarantee) instead of thin on 10.

## Worked example — Schwab (Aug 28, 2026) — the NEGATIVE case: a real institution ≠ a rail
- **What:** Charles Schwab (largest US brokerage, ~$13T, 40M accounts) announced adding SOL,
  AVAX, LINK to Schwab Crypto accounts (verified vs pressroom.aboutschwab.com, 08/27/2026).
  Jordan asked: "is that a potential rail we can add?"
- **Verdict: NOT a treasury rail.** Distinction that decides it:
  - **A rail is programmatic** — an API/SDK the agent drives 24/7 with no human in the loop
    (Across/CCTP, Jupiter, Almanak, LFJ). That's what "rail" means for the treasury.
  - **Schwab is a retail brokerage** — a human opens an account, logs in, clicks. No agent
    API for moving treasury funds; not a DeFi venue. It's a *personal banking tool for Jordan*,
    not a capital-movement rail.
- **What it IS:** (1) Jordan's travel banking — Schwab Bank Investor Checking has no foreign
  transaction fees + unlimited worldwide ATM fee rebates (great for his Cebu trips; requires a
  linked Schwab One brokerage, which is $0-minimum, US-resident + SSN, 18+). (2) A structural
  adoption signal — first Schwab Crypto expansion beyond ETH/BTC, logged in the
  country-adoption-tracker as ✅ VERIFIED (institutional distribution, not sovereign).
- **Lesson:** when Jordan asks "is X a rail?", separate the two questions — *is it a programmatic
  capital-movement rail for the treasury?* (needs an API/SDK) vs *is it a useful tool for Jordan
  personally?* (banking, travel, adoption signal). A platform can be a strong YES on the second
  and a clear NO on the first. Don't force a retail tool into the rail bucket.

## Worked example — BlackOpal nOPAL RWA vault (Aug 30 2026) — the THIRD classification
- **Source:** @leeky_k_crypt: "8-12% yield RWA vault to Avalanche, $54M 30-day surge, zero
  historical default rates."
- **Verified (issuer blog + 3 independents):** Plume blog — live on AVAX since Jul 22 2026
  (so "expands to Avalanche" meant LIVE-LAST-MONTH, not launching-now); Crypto Briefing; BSC
  News; Bybit RWA Earn listing (Aug 27, USDC subscribe/redeem). nOPAL = tokenized share of
  BlackOpal's LiquidStone II vault buying Brazilian merchant card receivables at a discount,
  settled via Visa/Mastercard, registered in Brazil's Central Bank C3 registry, FX-hedged.
- **Why the classification changed the verdict:** it is neither a capital-movement RAIL (no
  API/SDK to drive) nor a PERSONAL tool — it is a yield venue. Third bucket:
  **DEPLOY CANDIDATE.** When a shared product is a yield venue for treasury capital, it goes
  on the farm shortlist behind the council's gate and gets compared net-of-costs (hedge drag,
  lockup, gating) against the current LP baseline. "On our home chain" (AVAX = preferred farm
  target) moves it UP the shortlist; it never moves capital before a gate ruling.
- **Verdict: ⭐⭐⭐☆ deploy-candidate/Watch.** Real yield source (receivables discount, not
  emissions) + C3 registry + Tier-1 network settlement = legitimate; unproven contract,
  unknown lockup, probable permissioning = no capital until terms are read.
- **Private-credit marketing caveats (Challenger eyebrows by default):** "8-12% with zero
  historical default rates" is the genre's favorite line — every private credit fund says it
  until the first defaults. Before capital: hedge-cost drag on headline APY, lockup/redemption
  terms, KYC/permission gating (institutional-grade usually ≠ wallet-enterable), young
  contract risk. Compare REALIZED net APY — never chase a launch-week print.

## Worked example — a STRATEGY-PROVIDER venue (the FOURTH classification)

Some platforms are neither a capital rail, a personal tool, nor a yield venue: they are a
**marketplace where someone else's capital runs YOUR strategy**. The treasury is on the SUPPLY
side — a provider, not a depositor — so the whole rail scorecard is the wrong instrument and
"does it support our home chain / our wallet" is the wrong first question.

- **Classify by which side of the trade we sit on.** Ask: does this platform move OUR capital
  to a venue we control (rail), or does it distribute our STRATEGY to capital we do not control
  (venue-for-us-as-supplier)? A gated B2B API, enrolled portfolios, an owner-signed payout path
  and a provider console are the markers of the second. Name the bucket before researching
  chains and gas — otherwise you evaluate a supply arrangement with a demand-side rubric.
- **The monetization test is a CHANNEL test, and the tell is ASYMMETRY between the two sides.**
  A distribution channel documents its terms (enrollment, referral, revenue share, payout); a
  producer-side SDK documents none, because it stops at the venue boundary. Proven: a peer
  platform's SDK had zero hits for distribution/enrollment/revenue-share concepts while the
  candidate's docs described enrollment and a settable fee — decisive for *channel-adjacent, not
  competitor*. **Count the terms on BOTH sides and compare**; a competitor would need the same
  distribution machinery, and its absence is the finding.
- **A platform can be COMPLEMENTARY in category while being strictly LESS expressive than the
  tool we already run** — that makes it a distribution target, not a replacement. Check whether
  its strategy model (target weights + a rebalance schedule) can even represent our edge (an
  intent/backtest framework): if only a simple rebalancing subset maps, "integrate" means selling
  the subset, and saying so is part of the verdict.
- **Find the fee MECHANISM by its unit, not its marketing name** — see the vocabulary rule in
  `claim-provenance`. Here the platform had no revenue share at all; it had a **tenant-scoped
  per-transaction fee we set ourselves** (`swapBps`-style, an "integrator fee" in bps), charged
  on the output side of every swap. That is structurally our own x402 model, and it inverts the
  "no cut means free labour" fear from the opposite direction.
- **The publish/private flag is the MONETIZATION SWITCH, not a listing toggle.** A tenant-scoped
  fee means: as provider AND distributor we set the fee and earn; if we publish the strategy for a
  third party to enrol, THEIR tenant sets it and we earn whatever their configuration says.
  Publishing to discovery without deciding this deliberately is the free-labour outcome. Read the
  flag as an economic decision and flag it as the load-bearing one in the writeup.
- **Check whether the platform owns the implementation we think we own.** A provider console that
  also assigns "select assets, assign weights, set rebalance timing" and a provider-managed
  signing key means we own the THESIS and the platform owns the IMPLEMENTATION — a smaller
  surrender than "we contribute nothing", still a dependency, and the honest split belongs in the
  report.
- **Verify the fee ACCRUAL path before treating the mechanism as income.** A documented, settable
  fee with no documented accrual/payout address is a fee you cannot yet collect: say so as a
  narrow open question ("where does it accrue, how is it paid out?"), not as "there is no fee".
- **Verdict shape for this bucket: Watch + borrow, and the console key is a JORDAN decision.**
  When the platform cannot touch our capital (wrong chains), the fee only pays if we own
  distribution, and nothing is currently blocked, the correct ask is to PARK the key request with
  the accrual question attached — requesting an account is a human-gated step, never an agent's
  action. Borrow the mechanisms worth copying (signed/idempotent authorization bound to a chain
  set, session-key states as TYPED errors rather than silent no-ops, and metadata explicitly
  labelled "display only, not a computed return" — our ESTIMATE-vs-MEASURED rule, productised).

## Worked example — Blackhole rail build (Sept 8 2026) — building a rail on a fork
- **Ask:** Jordan greenlit Blackhole (ve3,3 DEX, Avalanche) as the next yield rail for the
  WAVAX/USDC pair. Task: spec the adapter. Outcome: a VERIFIED spec, not a faked execute script.
- **The fork-detection trap — the single most expensive lesson here.** A fork's pools do NOT
  all use one contract set. Blackhole's WAVAX/USDC pool is an **Algebra (V3 concentrated-
  liquidity) pool**, NOT the legacy Thena-V1 set. They use different NFPMs, different farming,
  different deployers. Writing ABI calls against the wrong set = silent reverts. **Before ANY
  ABI work, determine the pool's version:** call the version-detection contract
  (`AlgebraPoolAPI.pairToDeployer(pool)`) to route to the correct NFPM/Farming set. Never
  assume "it's a Thena fork → use Thena V1 addresses."
- **Pull the OFFICIAL deployed-addresses table, then on-chain verify.** GitBook docs expose
  clean markdown at `<page>.md`; `docs.example.xyz/technical-amm-documentation.md` had the FULL
  contract table (BLACK token, RouterV2, NFPM for both CL pool sets, GaugeManager, swapRouter,
  nonfungiblePositionManager, AlgebraPoolAPI). Fetch the table, THEN call `token0()/token1()/
  fee()/factory()` via eth_call on the pool to confirm token order (WAVAX=token0, USDC=token1),
  fee tier, and factory — so every address you encode is grounded, not a guess. A guessed NFPM
  address had zero bytecode (2 chars); the real one from docs had live code.
- **Fork token address can differ from the canonical asset** — Blackhole lists its own `wAVAX`
  and `black` in the prod table; the on-chain pool returns the canonical WAVAX/USDC. Trust the
  on-chain `token0()/token1()` over any docs table for token order in ABI args.
- **The emissions rail is a 3-leg flow, not one call:** NFPM.mint(position NFT) → stake NFT in
  the gauge (earn BLACK in-range) → harvest + convert BLACK → pool tokens → re-mint. Never
  hold the farm token; convert immediately.
- **Don't present a spec as a build.** Verified addresses + a design are a SPEC. The executable
  adapter still needs: protocol ABI, a tick-space range builder (adapted from LFJ's bin logic
  — Algebra uses `tick = log1.0001(price)` snapped to tickSpacing), a dry-run eth_call sim on
  a test wallet with real funds, THEN a real round. Same develop→test→verify→run loop as LFJ.
  State the open items honestly.
- **Shape families are NOT universal across venues.** Blackhole (Algebra V3 CL) is a
  **range-only** rail — the strategy lever is range width + re-center timing, with NO
  Curve/Bid-Ask/Spot shape families. LFJ and Meteora DLMM both have the bin-shape families
  our shape intelligence drives. When a rail is range-only, the shape detector does not apply
  there — the machine runs the simple rail autonomously and the shape intel stays parked for
  the bin venues. Don't force shape logic onto a range-only venue.
- **Ground a rail runbook in LIVE on-chain state, not the last plan.** Before writing a
  deployment/operating runbook for a yield rail, run the position reader + farm report +
  adapter dry-run to confirm what is actually deployed. A rail that was "waiting on funds"
  last week may already be live and farming — a runbook that repeats the old "awaiting
  capital" status is stale the moment it's written. If the position is live, the runbook
  becomes an operating manual + scale path, not a deployment plan.
- **Pull a pool's REAL yield split from vfat by token, not protocol name.** vfat's
  `search_yield_opportunities` returns nothing when you filter by protocol name (e.g.
  `protocols:["Blackhole"]`) — the protocol field is often null on the returned items.
  Search by the underlying token (e.g. `search:"WAVAX"` + `chainIds:[43114]` +
  `farmTypes:["concentrated"]`), then match the returned item by its pool address. The
  `options[].aprBasis.components` array splits headline APR into `swapFees` (the real fee
  core) vs `staking` (emissions) — always read the fee component, never the headline APR.
  The `guaranteedAprPricePercentRange` shows the range width the APR assumes full-time
  in-range, so you can sanity-check it against the position's actual range.
- **Cross-check a pool's APR across yield-data sources — they disagree and the gap is
  meaningful.** DefiLlama (`yields.llama.fi/pools`, filter by pool id) attributes ALL
  APR to rewards for CL pools (`apyBase: 0`, everything in `apyReward`) and reports the
  boosted/max rate — e.g. Blackhole WAVAX/USDC showed 698% on DefiLlama vs vfat's 216.5%
  (26.9% real swap fees + 189.6% emissions, the average). DefiLlama is a good DISCOVERY
  + TVL cross-check but its APR overstates what you'd actually earn; vfat's
  `aprBasis.components` split (swapFees vs staking) is the honest number. Never quote a
  rewards-only headline as the yield; always read the fee component.
- **When a rail's position reader is hardcoded to one venue, it silently misvalues on
  another.** The fee ledger's `snapshot()` used an LFJ-only withdraw-sim; after capital
  moved to Blackhole CL it read $0 LP, so `total` = just the dry-powder reserve. The
  reserve delta got misread as "measured fees" and a near-zero time window annualized
  into a fantasy APR (818,494%). Fix: make the position-valuation reader POOL-AWARE —
  read the live position value from `discover_positions` (which handles every rail)
  instead of a rail-specific withdraw-sim. Any reader that hardcodes one rail will
  misvalue on another; the chain never lies, the reader does.
- **Separate ESTIMATE from MEASURED in yield reporting.** Until the fee ledger has clean
  rail-only snapshots (2-3 days), show a clearly-labeled ESTIMATE (venue data, e.g. the
  vfat APR split) and leave the measured line null/None — never let a broken read dress
  up as a measured number. Jordan's standing ask: give prediction numbers until real
  data lands, but label them as predictions.
- **When capital moves off a rail, close it out of the config AND pause its crons.**
  Remove the exited pool from `treasury_config.json` (both vault + executed copies,
  md5-verify) so discovery stops probing it and emitting "no position" noise. Also
  pause the old-rail-specific crons (macro reposition/stand-down jobs) that keep firing
  no-op withdraw-redeploys against the empty rail — edit jobs.json with a backup, set
  `enabled=false` on every job whose name matches the retired rail. Re-add only if we
  choose to go back. **Re-verify after pausing: new old-rail crons can be created after
  your sweep** (a macro scheduler re-arms them per event), so re-list enabled jobs
  matching the retired rail and pause the stragglers — one pass is rarely enough.
- **A rail adapter can run from a DIFFERENT copy than the one you edit — sync all copies
  or the fix never takes effect.** The treasury cron ring runs scripts from THREE
  locations: the vault (source of truth), the GitHub-pages repos checkout, and the
  profile scripts dir. The watchdog execs the REPOS copy; the farm report execs the
  VAULT copy. A vault edit does NOT propagate to the repos copy the watchdog runs —
  that's how a Blackhole-aware fee-ledger fix stayed in the vault while the watchdog
  kept running the old LFJ-only version (stale ledger, $0 LP read, fantasy APR). Fix:
  keep a `sync-treasury-scripts.sh` that copies vault → repos + profile and md5-verifies
  all three, and schedule it on a cron (e.g. every 15m) so any vault edit propagates
  automatically. After any rail-adapter change, md5-check the copy the cron actually
  runs — the executed copy is what matters, not the one you edited.

## Pitfalls
- **A fork's pools can use DIFFERENT contract sets (Algebra V3 vs legacy V1).** Before writing
  any ABI calls against a DEX fork, detect the pool's version via its version-detection
  contract (`pairToDeployer(pool)`) and route to the correct NFPM/Farming pair. Assume-the-
  fork-protocol-set = silent reverts.
- **Pull the protocol's own deployed-addresses table before writing addresses.** A guessed
  contract address that "should exist" may have zero bytecode. GitBook docs expose markdown at
  `<page>.md`; grep the technical docs + llms.txt for the full contract table. Then on-chain
  verify token order, fee, and factory via eth_call before encoding any ABI.
- **A spec is not a build.** Verified addresses + a design ≠ a working deploy script. The
  adapter needs its own dry-run→test→verify→run cycle on test capital before touching real
  money. Don't present a grounded spec as a running artifact.

- **A legitimate financial institution is NOT automatically a treasury rail.** Size, trust, and
  adoption (Schwab $13T/40M accounts) do not make something a rail. A rail requires a programmatic
  API/SDK the agent can drive 24/7. Retail brokerages/banks are human-click tools — classify them
  as personal-banking or adoption signals, not rails.
- **Don't confuse "announced" with "shipped"** — a real API/SDK means buildable; a landing page
  with no SDK is a signal, not a spec. Check package registries (npm/PyPI) to verify SDKs exist.
- **apis.io agent-readiness score** is a fast triage for whether a platform is autonomous-agent
  friendly (MCP server, machine-readable contract) vs human-only. Low score = weak fit for our
  autonomous rails.
- **KYC/AML rails are human-gated** — flag the signup/KYC step as Jordan-only, never assume the
  agent can complete it.
- **"Don't compete, integrate"** — custody rails and wallet providers are integration targets,
  not competitors. We're the orchestration/identity layer; they're the custody/execution layer.

## Worked example — Jupiter Universal Deposit (Sept 2 2026) — launch-week product, no API yet
- **Source:** Jordan pasted @JupiterExchange post 2095161972274999712: "You don't need a
  bridge anymore. Introducing Universal Deposit." Send token from ETH/Base/Arbitrum/Sui →
  receive USDC in Solana wallet, routing/bridging/swapping handled automatically, **flat
  $0.30 fee** regardless of size ($100 or $10M). Live on Jupiter Mobile + wallet extension,
  jup.ag/deposit. Same-day thread: Solana official account amplifying ("All roads lead to Solana").
- **Rail test (per the index-probe method above):** fetched `developers.jup.ag/docs/llms.txt`
  and grepped — no Universal Deposit section. Only Lend Earn deposit (`/lend/v1/earn/deposit`)
  and Trigger vault deposit (`/trigger/v2/deposit/craft`) exist. Verdict: **consumer UI-first
  launch, no programmatic surface** — not a drivable rail yet.
- **Verdict: 🔧 Watch + borrow.** Borrowed mechanisms: (1) **flat-fee rail pricing** ($0.30
  flat vs %-based bridges = benchmark for our rail-fee accounting); (2) **one-deposit funding
  pattern** (money in from anywhere → strategy wallet receives USDC → agent deploys per
  regime — maps directly to Jordan's multi-wallet strategy support). Spit out: one-way-to-
  Solana bias (our yield engine is LFJ/AVAX), opaque underlying bridge routing.
- **Action on file:** watch `developers.jup.ag/changelog` monthly; when the API ships,
  scaffold connector #2 in the almanak SDK alongside the existing `jupiter_lend` client
  (same no-auth REST pattern). No capital action.
- **Bonus intel from the org scan:** Jupiter is the most agent-friendly rail in crypto —
  keyless 0.5 RPS API for agents (no signup), MCP docs server, `@jup-ag/cli` for terminal
  agents, skills via `npx skills add`. Their docs issue #832 is literally titled "Building
  the Most AI-Friendly Developer Resource." Watch `jup-ag` GitHub (202 repos, pushes daily).

## Worked example — Orderly Network perps via Pangolin (Sept 29 2026) — a CLOB derivative rail
- **Source:** Jordan shared a Pangolin Perps post and asked: *"Can we use this rail for AVAX
  perps? If so what tokens are available to us?"* The right entity to evaluate was not
  Pangolin's front end but **Orderly Network**, the omnichain CLOB it sits on. Orderly's own
  docs state they have *"no official front end; builders create DEXes and trading interfaces
  on top."*
- **Same-chain, same-collateral verification:** Orderly Vault on Avalanche
  `0x816f722424b49cf1275cc86da9840fbd5a6167e9` — verified on-chain as **2,429 bytes of code
  holding 89,841.08 USDC**, byte-identical to the Base and Optimism deployments and returned
  by Orderly's own MCP for chainId 43114. Collateral is **native USDC
  `0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E`** — the exact asset we already hold. No bridge,
  no wrapped asset, gasless trading once a key is activated. This settled an apparent
  contradiction: Orderly's narrative docs omitted Avalanche from the settlement list, but the
  contract surface included it. **Settle on the contract, not the prose.**
- **Market coverage:** 133 active markets. Buy-list assets: AVAX 20x, LINK 20x, SOL/BTC/ETH 100x,
  TAO 10x, XAUt 10x; COQ had no perp. Plus RWA perps (NVDA, TSLA, GOOGL, XAU, XAG, WTI, EURUSD).
- **Funding-rate correction (claim-provenance):** First instantaneous read showed AVAX funding
  at **+53.2%/yr**; over 60 funding periods (~20 days) the sustained average was **+14.27%/yr**
  (56/60 positive). The 53% was one reading at the top of its own range. **A snapshot is not a
  standing property.** ETH paid better at +18.51%/yr (60/60 positive).
- **Real mechanism and size:** Persistently positive funding ⇒ longs pay shorts ⇒ a short perp
  against spot we already hold collects funding delta-neutrally. At $146 and 2x: ~$13.89/yr
  gross; round-trip taker fees $0.058; $146 filled at +0.010% slippage. **Fees and depth were
  not the blockers; liquidation risk on the short leg and thin OI ($417K) were.**
- **Verdict: real rail, wrong size.** Worth revisiting as the weekly cadence compounds the book.
  Filed to `references/perp-rail-evaluation.md`.

## Perp / CLOB derivative rail evaluation checklist

When evaluating a perpetuals or CLOB derivative rail, use this checklist in order:

1. **Front end vs engine.** Identify the actual clearing/settlement engine (Orderly, dYdX,
   Hyperliquid, GMX, etc.) and verify the front end is just one interface.
2. **Collateral asset and chain.** Confirm the deposit token is a stablecoin or asset we
   already hold on a chain we can reach without bridging.
3. **Vault/contract verification.** `eth_getCode` on the deposit/position contract; compare
   bytecode across chains if the engine claims multi-chain deployment; check the MCP/docs
   chainId return against the contract.
4. **Market list and leverage.** Read the active market list from the engine's API; confirm
   leverage tiers and whether each buy-list asset is present.
5. **Funding persistence, not snapshot.** Fetch multiple funding periods; report the sustained
   average, the positive-ratio, and note the instantaneous high. Never quote a single funding
   reading as the yield.
6. **Depth and fees for the actual size.** Probe the orderbook at the capital amount we would
   deploy, not at $1M or $10K. Report slippage and round-trip taker fees.
7. **Risk surface.** Open interest, liquidation mechanics, isolated vs cross margin, and any
   KYC/gating. A great rate on a $400K OI pool cannot absorb real capital.
8. **Verdict shape.** Real mechanism + reachable + right size = deploy candidate; real
   mechanism + reachable + wrong size = watch and revisit on book growth; no programmatic
   surface or wrong-chain collateral = not a rail.

See `references/perp-rail-evaluation.md` for the full recipe, API endpoints, and arithmetic.
