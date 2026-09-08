# ERC-8004 Metadata URI Update (fix AgentScan blanks) — proven Aug 11, 2026

**Trigger:** AgentScan / 8004scan shows blank `skills[]`, `domains[]`, `capabilities[]`
even though the metadata JSON is fully populated. Root cause: the on-chain
`metadata_uri` (aka `tokenURI`) points to a private/rate-limited/404 host, so the
indexer can't fetch it.

**Why our personal GitHub 404s:** ProtoJay4789 is rate-limited/flagged from
over-updating. `raw.githubusercontent.com/ProtoJay4789/...` returns 404. Host
discovery metadata on our own site (`gentechlabs.net`) — never rate-limited.

## The two-step fix (verified working)

### Step 1 — Host the metadata on our own site
Copy the metadata JSON to the nginx webroot so `/.well-known/` serves it:

```bash
cp gentech-avax-metadata.json /var/www/gentechlabs/.well-known/gentech-avax-metadata.json
chown www-data:www-data /var/www/gentechlabs/.well-known/gentech-avax-metadata.json
chmod 644 /var/www/gentechlabs/.well-known/gentech-avax-metadata.json
# verify both domains serve it (the api.* and root both map /.well-known/ to this root)
curl -s -o /dev/null -w "%{http_code}" https://gentechlabs.net/.well-known/gentech-avax-metadata.json  # 200
curl -s -o /dev/null -w "%{http_code}" https://api.gentechlabs.net/.well-known/gentech-avax-metadata.json  # 200
```

### Step 2 — Re-point the on-chain URI via setAgentURI
Registry contract: `0x8004A169FB4a3325136EB29fA0ceB6D2e539a432` (same on all
chains via CREATE2). Read the current URI with `tokenURI(uint256)` selector
`0xc87b56dd` + 64-hex agentId via `eth_call` on the chain RPC. Update with
`setAgentURI(agentId, newUri)` signed by the owner key.

Key points from the proven run (Avalanche, agent 1770, owner `0x7ebff…`):
- Key is at `/root/.blockrun/jordan-avax-secret` — read from disk in the script,
  NEVER pass through a tool arg (lands in transcript). chmod 600.
- **Ownership check first:** call `ownerOf(agentId)`; if it != signer address, abort.
- ABI: `setAgentURI(uint256,string)` nonpayable; `ownerOf(uint256)` view.
- gasPrice from `eth_getGasPrice`, chainId 43114, 20% gas buffer, wait for receipt.
- After sending, re-read `tokenURI` to confirm the new URI is live on-chain.
- Verify the URI is fetchable (200) from the same environment the indexer uses.

Web3 + eth_account are available in system python3 (no venv needed).

**Also update:** the registry row in `11-Mess Hall/marketplace-listings-registry.md`
for 8004scan to note the new URI + date. Do NOT point at raw.githubusercontent
for discovery metadata — use gentechlabs.net.
