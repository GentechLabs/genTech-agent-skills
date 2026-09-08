# On-Chain Entry Detection for LFJ V2.2 Positions

Detect when a wallet first entered a concentrated liquidity pool by scanning ERC-1155 TransferBatch events.

## Event Signature

LFJ V2.2 uses **TransferBatch** (not TransferSingle) for bin share management:

```
event TransferBatch(
    address indexed operator,
    address indexed from,
    address indexed to,
    uint256[] ids,
    uint256[] values
)
```

- **Topic0**: `0x4a39dc06d4c0dbc64b70af90fd698a233a518aa5d07e595d983b8c0526c8f7fb`
- **Topic2** (indexed `from`): `0x0` = mint (deposit), wallet address = withdraw
- **Topic3** (indexed `to`): `0x0` = burn (withdraw), wallet address = deposit

## Query Pattern

```python
TRANSFER_BATCH_SIG = "0x4a39dc06d4c0dbc64b70af90fd698a233a518aa5d07e595d983b8c0526c8f7fb"
WALLET_TOPIC = "0x000000000000000000000000" + WALLET[2:].lower()

# Find earliest deposit (to=wallet)
params = [{
    "address": POOL_ADDRESS,
    "fromBlock": hex(from_block),
    "toBlock": hex(end_block),
    "topics": [TRANSFER_BATCH_SIG, None, None, WALLET_TOPIC]
}]
```

### Chunked Search (Rate Limit Workaround)

The public Avalanche RPC limits eth_getLogs to **2048 block ranges**. To find first deposit:

1. Start from current block, search backwards in 2048-block chunks
2. Collect all deposit events, stop when 50+ empty chunks
3. Sort by block ascending, take the earliest
4. Get that block's timestamp via `eth_getBlockByNumber`
5. Cache the result so subsequent runs are instant

```python
CHUNK = 2048
from_block = max(17000000, current_block - 2000000)
all_deposits = []

end = current_block
while end > from_block:
    start = max(end - CHUNK, from_block)
    # eth_getLogs params
    end = start - 1
    time.sleep(0.1)  # avoid rate limiting

# Sort ascending, take earliest
all_deposits.sort(key=lambda x: x['block'])
first_deposit = all_deposits[0]

# Get timestamp
payload = json.dumps({
    "jsonrpc": "2.0", "method": "eth_getBlockByNumber",
    "params": [hex(first_deposit['block']), False], "id": 1
}).encode()
```

## RPC Alternatives

| Provider | Rate Limit | Cost | Notes |
|----------|-----------|------|-------|
| Public Avalanche RPC (`api.avax.network`) | ~10 req/min | Free | Liberal 429; use time.sleep(0.2) |
| BlockRun RPC (`blockrun_rpc` tool) | 10,000 block range per log query | $0.002/call | Higher limit, needs wallet funded |

## Parsing TransferBatch Data

The `data` field is ABI-encoded:
```
offset (32 bytes)  → always 0x40 = 64
length (32 bytes)  → number of bins
bin_ids[]          → length × 32 bytes each
values[]           → length × 32 bytes each
```

Extraction:
```python
data_hex = log['data']
offset = int(data_hex[2:66], 16)         # usually 64
length = int(data_hex[66:130], 16)        # number of bins
bin_start = 2 + offset * 2 + 64          # skip offset + length
bins = []
for i in range(length):
    bin_hex = data_hex[bin_start + i*64 : bin_start + (i+1)*64]
    bins.append(int(bin_hex, 16))
```

## Cache Pattern

Avoid re-querying every time: store the result in a JSON file and check it first.

```python
ENTRY_CACHE_FILE = "~/.hermes/scripts/.lfj-entry-cache.json"

# Check cache first
try:
    with open(ENTRY_CACHE_FILE) as f:
        cache = json.load(f)
    if cache.get("first_deposit_block"):
        return cache
except (FileNotFoundError, json.JSONDecodeError):
    pass

# ... do the search ...

# Cache result
result = {
    "first_deposit_block": block,
    "first_deposit_tx": tx,
    "first_deposit_date": date,
    "days_active": days,
    "total_deposits": count,
    "last_verified": timestamp,
}
with open(ENTRY_CACHE_FILE, "w") as f:
    json.dump(result, f, indent=2)
```

## AAE Reputation Use

Time-in-pool is a verifiable on-chain metric for agent reputation:
- **Days active**: First deposit date → current date
- **Consistency score**: Total deposits / days active (more frequent = more active)
- **Rebalance count**: Number of deposit-withdraw cycles
- **Pool commitment**: Longest continuous position without full withdrawal

## Reference Wallet

Our wallet (0x7ebff188f2Eba16518C02864589b1403a5d1296a):
- **First deposit**: Block 88,171,640 (Jun 17, 2026)
- **Time in market**: 16.5 days (and counting)
- **Total deposits**: 41 events
- **Current position**: Block 89,376,281 (Jul 3, 2026) — 33 bins, $46.33 position
