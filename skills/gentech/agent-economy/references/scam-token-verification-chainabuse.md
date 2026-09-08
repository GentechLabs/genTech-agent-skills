# Scam-Token Verification + Chainabuse Reporting (verified Aug 2, 2026)

When Jordan (or any user) reports unexpected tokens in a wallet, verify
on-chain BEFORE declaring scam vs real. He asked "did that come from the
GOAT Network people or from our services?" — rule out legit sources first.

## Verification recipe (all keyless, ~2 min)

1. **Get the exact wallet address from records** — screenshots truncate
   (`0x7ebff...1296a`); grep the vault for the full address before querying.
2. **Check real native/token balances** on the chain via public RPC:
   - AVAX/C-chain: `eth_getBalance` on `https://api.avax.network/ext/bc/C/rpc`
   - Official bridged token (BTC.b): compare against the KNOWN official
     contract — our wallet had 0 of the real BTC.b while showing fake RBTC.b.
3. **Decode token name/symbol** — `eth_call` `0x06fdde03` (name) and
   `0x95d89b41` (symbol). **Homoglyph tell:** scammers use Cyrillic
   `С`/`Ѕ` and dotted `Ḍ` so wallets render "USDC"/"AVAX" identically.
   Seen: `ÚSDС`, `USḌ Coin`, `UЅDС`, fake `AVAX`.
4. **Check DexScreener for real trading pairs** — a fabricated token has
   ZERO pairs/price (`/latest/dex/search?q=<symbol>` returns none).
5. **Check the value math** — "<0.00001 RBTC.b worth $460.51" = fake price
   feed (~$46M/coin). Real tokens don't price like that.
6. **Rule out legit sources in OUR records** — grep vault/repos for the
   party (e.g. GOAT grant = we APPLIED, never received; our services only
   RECEIVE USDC to `0xF9dc...`, never send tokens to Jordan's wallet).

## Verdict pattern

Scam airdrop/dust = unsolicited token, homoglyph name, zero pairs, fake
price feed. **Do NOT swap/sell/approve it** — interaction is the attack.
Real funds untouched (verify balances). Offer to report it.

## Chainabuse report (chainabuse.com/en/report)

Circle/TRM-run scam tracker — the right place for homoglyph/dust reports.

- **Description step:** paste full facts (wallet, token contracts, homoglyph
  names, why it's a scam). Auto-detects type — "Fraud - NFT Airdrop Scam".
- **Identifiers step:** addresses auto-fill from the description. Fix the
  chain selector if needed (Ethereum default ≠ Avalanche).
- **Privacy:** Public Report (alerts community) unless ongoing investigation.
- **Contact step:** toggle the "support" switch OFF to enable SUBMIT
  (it's ON by default and its consent blocks submit without victim info).
  No loss amount needed — nothing was actually lost.
- **Modal:** choose **SUBMIT ANONYMOUSLY** (no account, keeps user private).

## Browser SPA pitfalls (hit Aug 2, 2026)

- Chainabuse is a React SPA — ref-clicks on buttons sometimes don't fire.
  Drive with `browser_console` JS: find button by text, `.click()`.
- The "NEXT"/"Next" capitalization differs between steps — match by
  `textContent.trim().toUpperCase() === 'NEXT'`.
- Browser backend can 502 mid-flow (CDP WebSocket). Don't claim the report
  landed without a success confirmation; retry or hand the user the
  form + address list to finish.
