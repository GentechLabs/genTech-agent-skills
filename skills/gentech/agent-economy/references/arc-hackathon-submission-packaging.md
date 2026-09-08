# ARC Programmable Money Hackathon — Submission Packaging (Aug 1, 2026)

**Hackathon:** Encode Club Programmable Money (Circle × Arc), Agentic Economy track.
**Submission repo:** `Gentech-Labs/programmable-money-x402` (org copy — personal copy 404s on web).
**Working code repo:** `arc-x402-gateway` (57 tests passing).

## The Consolidation Trap

The submission repo (`programmable-money-x402`) originally contained ONLY stub
READMEs in `agent/`, `gateway/`, `sdk/`, `dashboard/` — while the actual working
gateway lived in a separate `arc-x402-gateway` repo. Judges click the submission
repo. If it's stubs, the build doesn't exist to them.

**Fix — consolidate real code into the submission repo:**

```bash
cd /root/programmable-money-x402
mkdir -p gateway/src gateway/tests
cp /root/repos/arc-x402-gateway/src/*.py gateway/src/
cp /root/repos/arc-x402-gateway/tests/test_*.py gateway/tests/
cp /root/repos/arc-x402-gateway/pyproject.toml gateway/
cp /root/repos/arc-x402-gateway/.env.example gateway/
cp /root/repos/arc-x402-gateway/LICENSE . 2>/dev/null
cp /root/repos/arc-x402-gateway/.gitignore . 2>/dev/null
```

Then fill the missing pieces:
- **`sdk/client.py`** — the buyer-side `X402Client`: call → 402 challenge → sign proof (HMAC simulation) → retry with `Authorization: x402 <proof>` → paid data. This was the missing agent-side half; the gateway alone (seller side) is not an agent-to-agent demo.
- **`examples/agent_demo.py`** — end-to-end: health → paid price → paid analyze → paid stream.
- **`dashboard/index.html`** — static playground showing 402 → pay → response for judges (fetch with no header → 402; POST `/v1/simulate-pay`; retry with header).

## Verify in the Consolidated Location

```bash
cd gateway && python3 -m pytest tests/ -q          # 57 passed
```

Run the server on a FREE port — 8088 is often the production gateway
(`ss -tlnp | grep 8088` to check). Use 8095:

```bash
# background=true (long-lived server)
cd gateway && RECIPIENT_ADDRESS=0x... PORT=8095 python3 -m src.gateway
# then in a separate call:
curl -s localhost:8095/v1/health
curl -s -o /tmp/402.json -w "%{http_code}" "localhost:8095/v1/price?symbol=ETH&tier=standard"  # expect 402
cd /root/programmable-money-x402 && sed -i 's|8088|8095|' examples/agent_demo.py && python3 examples/agent_demo.py
```

## Org-Mirror Rule (flagged account)

After pushing to `ProtoJay4789/programmable-money-x402`, the web URL 404'd while
the API said public. Create under the org + push + verify:

```bash
curl -s -X POST -H "Authorization: token $TOKEN" \
  https://api.github.com/orgs/Gentech-Labs/repos \
  -d '{"name":"programmable-money-x402","description":"x402 payment gateway on Arc — programmable money for the agent economy","private":false}'
git remote add org https://github.com/Gentech-Labs/programmable-money-x402.git
git push org main
curl -s -o /dev/null -w "%{http_code}" https://github.com/Gentech-Labs/programmable-money-x402   # expect 200
```

Put the ORG URL in the submission form + README. See `agent-economy` §12 pitfall
and `grant-application` Pitfall 8 for the same rule.

## Remaining for submission (Aug 3 target)

1. Deploy on Arc testnet — needs faucet USDC (faucet.circle.com) + wallet confirm
   (build queue lists `0x7ebf...296a`).
2. 3-min demo video + deck.
