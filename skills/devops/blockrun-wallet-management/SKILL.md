---
name: blockrun-wallet-management
description: "BlockRun wallet lifecycle — creation, funding, key restoration, address verification, and troubleshooting. Covers the MCP server's wallet system and how to handle wallet recreation."
---

# BlockRun Wallet Management

> Load this before any paid BlockRun operation (image generation, video, music, speech, RealFace, search). The wallet must be funded and the correct key must be active.

---

## 🏦 Wallet Architecture

BlockRun maintains **two wallets** — one on Base, one on Solana — and pays on ONE active chain at a time. Default is Base.

| Chain | Address (Gentech) | Explorer |
|-------|------------------|----------|
| Base (F8) | `0xebc8c71970EEb6973bd87F1FF146B3Ec4a5972f8` | basescan.org |
| Solana | `BX9ELMCGPy3qmGNrhH3c2W5NJmapSQ435k8hqE5K43XT` | solscan.io |

**Gentech's wallet:** The BlockRun MCP uses `getOrCreateWallet()` from `@blockrun/llm`. The Base address ends in `72f8` — Jordan calls it "the one ending in F8." This is the media wallet.

### Key Storage

The wallet private key is stored at `~/.blockrun/.session` (a 66-char hex string starting with `0x`). The MCP server reads this file on startup to derive the wallet address.

**⚠️ Dual-session-file pitfall:** There can be TWO `.session` files:
- `/root/.blockrun/.session` — the original, created on first BlockRun use
- `/root/.hermes/profiles/gentech/home/.blockrun/.session` — a profile-specific copy

The MCP server reads the **profile-specific copy** (`~/.hermes/profiles/gentech/home/.blockrun/.session`). If this file was created fresh (e.g. after a Hermes update or MCP server restart), it will have a **different private key** than the original, resulting in a different wallet address.

**Always check both files exist and match before assuming the wallet address is correct.**

**The wallet address is deterministically derived from the private key.** A different key = a different address.

---

## ✅ Pre-Operation Checklist

- [ ] Check balance: `blockrun_wallet action="status"` — must show > $2.00
- [ ] Verify the address matches where Jordan sends funds
- [ ] If balance is $0.00, check if the wallet was recreated (new key)
- [ ] Switch to correct chain: `blockrun_wallet action="chain" chain="base"` (for video/image/music/speech/RealFace)

---

## 🚨 Critical Pitfall: Wallet Recreation

**Issue:** The BlockRun MCP server creates a **brand new wallet** on first run. If the `~/.blockrun/.session` file is recreated (e.g. after a Hermes update, MCP server restart, or new install), a new key is generated and the old wallet address is lost.

**This means:** Jordan may have sent USDC to the OLD wallet address, but BlockRun is now looking at a NEW wallet with $0.00.

### Diagnosis

```bash
# 1. Check the current wallet address
# Run blockrun_wallet action="status" and note the address

# 2. Check if there are multiple .session files
ls -la ~/.blockrun/.session
ls -la ~/.hermes/profiles/gentech/home/.blockrun/.session  # profile-specific copy

# 3. Compare the keys
cat ~/.blockrun/.session
cat ~/.hermes/profiles/gentech/home/.blockrun/.session
```

### The Fix — Restore the Old Wallet Key

```bash
# 1. Find the old private key
# Options:
#   - Check ~/.blockrun/.session from a backup
#   - Check ~/.hermes/profiles/gentech/home/.blockrun/.session (profile copy)
#   - Ask Jordan for the old wallet address and derive the key
#   - Check if the key was saved in an env var or config file

# 2. Write the old key to the active .session file
echo "0xOLD_PRIVATE_KEY" > ~/.blockrun/.session

# 3. Verify the address matches
# Run blockrun_wallet action="status" — the address should now match
```

### Prevention

- **Back up `~/.blockrun/.session`** after the first successful wallet creation
- **Save the wallet address** to memory so you can detect if it changes
- **Check balance BEFORE every paid operation** — don't assume the wallet is still the same
- **If balance is $0.00 and Jordan says he sent funds**, ALWAYS verify the wallet address first

---

## 💰 Manual Balance Check (RPC fallback)

When the `blockrun_wallet` MCP tool is NOT loaded in a session (tool unavailable / MCP server not running), query the Base wallet balance directly via the public Base RPC. No API key needed — just the `.session` private key.

```bash
# 1. Derive the address from the private key (both .session files should match)
python3 -c "
from eth_account import Account
acct = Account.from_key(open('/root/.blockrun/.session').read().strip())
print(acct.address)
"

# 2. USDC balance on Base (USDC contract 0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913)
ADDR="ebc8c71970EEb6973bd87F1FF146B3Ec4a5972f8"   # <-- substitute derived address, bare 40-hex, NO 0x
DATA="0x70a08231000000000000000000000000${ADDR}"
curl -s --max-time 20 https://mainnet.base.org -H "Content-Type: application/json" \
  -d "{\"jsonrpc\":\"2.0\",\"method\":\"eth_call\",\"params\":[{\"to\":\"0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913\",\"data\":\"$DATA\"}, \"latest\"],\"id\":1}"

# 3. Native ETH balance
curl -s --max-time 20 https://mainnet.base.org -H "Content-Type: application/json" \
  -d "{\"jsonrpc\":\"2.0\",\"method\":\"eth_getBalance\",\"params\":[\"0x$ADDR\", \"latest\"],\"id\":1}"
```

Convert the hex result to dollars:
```python
usdc = int('0xHEX', 16) / 1e6   # USDC has 6 decimals
eth  = int('0xHEX', 16) / 1e18
```

**Pitfall — double `0x`:** the address variable must be the bare 40-hex (no `0x` prefix) when concatenated into the `balanceOf` data field. Using `0x$ADDR` with ADDR already `0x`-prefixed yields `0x...0x...` → RPC rejects with `Invalid params`. Strip the `0x` for the data field, re-add it only for the `eth_getBalance` address param.

## 💰 Funding

### Base (for video, image, music, speech, RealFace)

Send USDC on Base network to the active wallet address. Jordan sends from his wallet.

**Minimum for a single clip:** ~$1.66 (keyframe $0.06 + Seedance 4s $1.60)
**Recommended minimum:** $5.00

### Solana (for search, chat, RPC)

Switch chain first:
```
blockrun_wallet action="chain" chain="solana"
```

Then fund the Solana address with USDC SPL.

---

## 🔄 Chain Switching

```bash
# Check current chain
blockrun_wallet action="status"

# Switch to Base (for video/image/music/speech/RealFace)
blockrun_wallet action="chain" chain="base"

# Switch to Solana (for search/chat/RPC)
blockrun_wallet action="chain" chain="solana"
```

**Base-only operations:** video, music, speech, RealFace, price (paid calls)
**Either chain:** image generation

---

## 📊 Spending Report

```bash
blockrun_wallet action="report"
```

Shows global spend, per-agent budgets, and total calls made.

---

## 🔍 MCP Tool Discovery When Server Is Parked

When the BlockRun MCP server failed to connect at gateway startup (parked), you can discover available tools by running the MCP server manually:

```bash
cd /root/.hermes/blockrun-mcp
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | timeout 5 node node_modules/@blockrun/mcp/dist/index.js
```

This returns all 19 tools (`blockrun_wallet`, `blockrun_image`, `blockrun_video`, `blockrun_chat`, `blockrun_models`, `blockrun_music`, `blockrun_speech`, `blockrun_realface`, `blockrun_search`, `blockrun_exa`, `blockrun_markets`, `blockrun_price`, `blockrun_dex`, `blockrun_modal`, `blockrun_phone`, `blockrun_surf`, `blockrun_rpc`, `blockrun_defi`, `blockrun_polymarket`) with full schemas — useful when diagnosing why tools aren't in your agent tool list.

**Key insight**: `blockrun_image` supports GPT Image 2 as its default model; `clawrouter_image_generate` does NOT. To use GPT Image 2, you need the MCP server connected (requires gateway restart — cannot be done from inside the gateway due to Hermes' SIGTERM guard).

After funding or restoring a key, verify the wallet works:

```bash
# 1. Check balance shows > $0.00
blockrun_wallet action="status"

# 2. Make a tiny paid call (cheapest option)
# blockrun_image with model="zai/cogview-4" costs $0.015
```

---

## 📎 Reference Files

- `references/sakura-wallet-recovery-2026-07-30.md` — Wallet recovery transcript (dual `.session` key mismatch fix)
- `references/direct-sdk-invocation.md` — **Direct BlockRun Node SDK** (`ImageClient`, `VideoClient`) invocation when the `blockrun_image` / `blockrun_video` MCP tools are NOT loaded in a session. Covers img2img keyframe via `client.edit`, Seedance 2.0 video via `client.generate` (public-URL `imageUrl` seed required, `generateAudio` baked-in score), response shape, and cost (~$3.20 for 10s). Read this to generate paid images/video without the MCP tools.
