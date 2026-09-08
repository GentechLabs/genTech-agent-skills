# Wallet Key Inventory & the Auto-Store Rule

Session: Aug 22, 2026 — full treasury sweep + consolidation attempt.

## 🔑 KEY RULE (Jordan, Aug 22, 2026)

> **Whenever we create a wallet or rail, auto-generate AND store the private keys
> automatically. Jordan has no control over that. Never leave a funded wallet keyless.**

This is a hard operational rule. A wallet we create but don't store the key for is a
**trap**: the moment it receives funds, we can't move them.

### The failure this prevents

The treasury wallet `0xF9dc...734` (~$33) was created as a **receive-only** x402
`payTo` address. Its key was never stored. When Jordan wanted to sweep it to Coinbase,
we couldn't — no key on disk, not in session history, not CDP-managed. Money safe but
immovable.

**Pitfall — receive-only ≠ keyless:** a wallet set up purely to *receive* payments
(x402 payTo, settlement address) still accumulates funds. If you don't store its key at
creation, you've built a one-way trap. Every wallet we create — receive-only or not —
gets its key generated and stored at creation time.

## Key Inventory (what we hold vs. don't)

| Wallet | Address | Key on disk? |
|--------|---------|--------------|
| Signer/ops (Jordan's AVAX) | `0x7ebff188...96a` | ✅ `/root/.blockrun/jordan-personal-avax-key` |
| Arb (GTA test) | `0x3d117Bf...eCb` | ✅ `/root/.hermes/profiles/gentech/secure/gentech-arb-wallet.json` |
| Almanak Steward | `0x572ABd...037` | ✅ `/root/.blockrun/almanak-steward-key` |
| CDP exec | `0x934Cbf...C05` | ✅ `/root/.blockrun/cdp-wallet-secret` (DER EC key) |
| Remit test | `0x36795F...E93` | ✅ `/root/.blockrun/remit-test-wallet.json` |
| **Treasury (receive)** | `0xF9dcBFF7...734` | ❌ **NO KEY — receive-only, never stored** |

## Key locations

- Raw key files: `/root/.blockrun/` (chmod 600)
- JSON keyfiles: `/root/.hermes/profiles/gentech/secure/`

## Verify a key before trusting it

```python
from eth_account import Account
acct = Account.from_key(key)
assert acct.address.lower() == expected.lower()
```

## CDP wallet secret is DER-encoded, not raw

`/root/.blockrun/cdp-wallet-secret` is a **base64 DER EC key**, not a 64-hex string.
Decode it:

```python
import base64
from cryptography.hazmat.primitives import serialization
from eth_account import Account
dec = base64.b64decode(secret)
key = serialization.load_der_private_key(dec, password=None)
raw = key.private_numbers().private_value
acct = Account.from_key(raw)  # -> 0x934Cbf...C05
```

## Full-balance sweep technique (closes Revenue Monitor blind spots)

The Revenue Monitor was income-only + USDC-only on 4 chains (Base/Avalanche/BNB/Solana).
It missed HyperEVM, Celo, BSC native, and native gas entirely. The fix: a `get_full_balance_sweep()`
that iterates every known wallet × every chain × native + USDC via `eth_getBalance` +
`eth_call` (balanceOf), using a browser User-Agent to dodge RPC 403s.

Key points:
- Use `curl -A "Mozilla/5.0"` — several public RPCs (base.llamarpc.com, base-rpc.publicnode.com,
  1rpc.io/base, mainnet.base.org) return 403 to default curl UA.
- USDC `balanceOf` calldata: `0x70a08231` + 32-byte zero-padded address.
- Only keep chains with non-zero balance to keep the report clean.
- Sum USDC at $1.00 + native × per-chain price for a USD total.

This is now built into `/root/.hermes/profiles/gentech/scripts/revenue-monitor.py`
(`SWEEP_WALLETS`, `SWEEP_CHAINS`, `get_full_balance_sweep`, `sweep_total_usd`).
