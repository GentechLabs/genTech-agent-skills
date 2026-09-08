# On-Chain Entry Detection Reference

## Event Discovery

LFJ V2.2 uses ERC-1155 `TransferBatch`, NOT `TransferSingle`.

```python
TRANSFER_BATCH_SIG = "0x4a39dc06d4c0dbc64b70af90fd698a233a518aa5d07e595d983b8c0526c8f7fb"
```

Topic layout (ERC-1155 TransferBatch):
- topics[0]: event sig
- topics[1]: operator (indexed address)
- topics[2]: from (indexed address)
- topics[3]: to (indexed address)

Data layout:
- First 32 bytes: offset (always 0x40 = 64)
- Next 32 bytes: length (number of bin IDs)
- Remaining: bin IDs (each 32 bytes), then values (each 32 bytes)

## Wallet Activity for 0x7ebff188f2Eba16518C02864589b1403a5d1296a

Pool: `0x864d4e5ee7318e97483db7eb0912e09f161516ea` (LFJ AVAX/USDC 5bps)

| Metric | Value |
|--------|-------|
| First deposit | Block 88,171,640 (Jun 17, 2026 03:05 UTC) |
| Current entry | Block 89,376,281 (Jul 3, 2026 11:53 UTC) |
| Calendar days | 16.5 |
| Active days (4h+) | 16 |
| Total deposits | 41 |
| Total withdrawals | 24 |
| First withdrawal | ~Block 88,667,778 (Jun 23, 2026) |

ATH daily fee: $5.00/day (Grunt tier, achieved ~April 2026)

## Block Time Estimation

Avalanche C-Chain: ~73,900 blocks/day ≈ 1.2 seconds/block.

```python
blocks_per_day = 73603  # Calibrated Jun 17 - Jul 3
seconds_per_block = 1.2
```

## Key Queries

```python
# Deposits (to=wallet) — topics[3] = wallet
params = [{
    "address": POOL_ADDRESS,
    "fromBlock": hex(start),
    "toBlock": hex(end),
    "topics": [TRANSFER_BATCH_SIG, None, None, WALLET_TOPIC]
}]

# Withdrawals (from=wallet) — topics[2] = wallet  
params = [{
    "address": POOL_ADDRESS,
    "fromBlock": hex(start),
    "toBlock": hex(end),
    "topics": [TRANSFER_BATCH_SIG, None, WALLET_TOPIC]
}]
```

## Rate Limiting

Public Avalanche RPC limits eth_getLogs to 2048-block chunks and 429s on rapid requests. Batch block timestamp queries in groups of 5 with 300ms+ delay between batches.

BlockRun RPC (via blockrun_rpc MCP) handles larger ranges but costs $0.002/call.
