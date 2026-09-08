# AgentScan / Registry Metadata-URI 404 — Empty Skills/Domains Root Cause (Aug 7, 2026)

## Symptom
An agent is live on a registry (AgentScan, 8004scan, etc.) with a good description, but
`skills: []`, `domains: []`, `capabilities: []` are all empty — even though the metadata
JSON is fully populated. The agent is effectively invisible to capability-based searches.

## Root cause
The registry's `metadata_uri` field points to a URL the registry **cannot fetch
unauthenticated**. In our case the metadata lived at
`raw.githubusercontent.com/ProtoJay4789/ProtoJay4789.github.io/main/gentech-avax-metadata.json`
which returned **404** to an unauthenticated request. The registry has no auth, so it got
a 404 and showed blank skills/domains. The metadata file itself was fine — the *hosting*
was the problem.

## Diagnosis recipe
1. Fetch the agent detail from the registry API (e.g. `GET https://agentscan.info/api/agents/{uuid}`).
   Note the `metadata_uri` and `classification_source` fields.
2. `curl -s -o /dev/null -w "%{http_code}" <metadata_uri>` — if it's 404/403 unauthenticated,
   that's the bug.
3. Confirm the file IS on the remote: `git ls-tree origin/main --name-only | grep <file>`
   and `curl` the GitHub API contents endpoint (with token) — the file can be tracked and
   present on the remote yet still 404 on raw.githubusercontent.com (a GitHub raw-URL quirk
   that can persist even for public repos).
4. `classification_source: "ai"` means the registry derives skills/domains via AI from the
   metadata — it can't if the fetch fails.

## The fix
Host the metadata at a **publicly reachable** URL, then point the registry's `metadata_uri`
at it. Steps:
1. Push the metadata JSON to a **public** repo (e.g. `Gentech-Labs/programmable-money-x402`).
   Verify the raw URL returns HTTP 200 unauthenticated:
   `curl -s -o /dev/null -w "%{http_code}" https://raw.githubusercontent.com/<org>/<repo>/main/<file>`
2. Update the registry's `metadata_uri` to the new public URL.

## The blocker (honest limit)
Updating the on-chain `metadata_uri` (or the ERC-8004 `agentURI`) is a **write that needs
the owner wallet's signature**. The agent must never hold the owner's private key. Check
whether any key on the box derives to the owner address before promising to do it solo —
if not, it's a manual step for the human (sign the URI update from the owner wallet), and
you should say so plainly rather than claim you can do it.

## Exact signing path (Avalanche ERC-8004, verified Aug 2026)
- **Contract:** `0x8004A169FB4a3325136EB29fA0ceB6D2e539a432` (ERC-8004 Identity Registry, Avalanche C-Chain)
- **Function:** `setAgentURI(uint256 agentId, string newURI)`
- **Args:** `agentId` = the agent token id (e.g. `1770`), `newURI` = the new public metadata URL
- **Sign from the owner wallet** (the one that registered the agent) — signing from any other
  wallet reverts. Confirm the owner address with the human BEFORE they sign so they don't
  waste gas on the wrong account.
- **Doable from a phone** via the OKX Wallet app or MetaMask mobile: switch to Avalanche
  C-Chain, open the contract, call `setAgentURI`, confirm the signature. Costs a little AVAX gas.
- **Before pushing the human to sign, try the no-sign path first:** if the original
  `metadata_uri` repo is actually public but the raw URL 404s, re-commit the file (bump a
  field) to force the raw CDN refresh, or flip repo visibility public via the API. These
  sometimes resolve the URL with zero on-chain changes. Only fall back to the on-chain
  `setAgentURI` signature when the URL genuinely can't be made public.

## Related
- The on-chain IPFS metadata (`agentURI`) is the registered source of truth and is separate
  from the GitHub `metadata_uri` the registry reads. Both may need updating.
- `onchainos` CLI only manages XLayer agents — it does NOT manage Avalanche/other-chain
  ERC-8004 identities. Don't try to update a non-XLayer agent through it.
