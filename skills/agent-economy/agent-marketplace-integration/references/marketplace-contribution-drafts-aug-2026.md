# Marketplace Contribution Drafts — Aug 2026

Jordan's directive (Aug 12): when a marketplace is broken/frozen/never-paid, find a way to
CONTRIBUTE and help fix it — GitHub issue/PR if they have one, or a contact channel if not.
This file holds the verified targets + drafted reports so a future session can file them
without re-researching.

## 1. Agoragentic — FROZEN (platform_custody_frozen)
- **GitHub:** `rhein1/agoragentic-integrations` (verified: real repo, issues enabled, 18 open,
  actively soliciting test reports in Discussion #214). No existing custody-freeze issue.
- **Draft issue title:** `platform_custody_frozen blocks all paid execution for sellers — status + path to unfreeze`
- **Body points:** `POST /api/quickstart` works (agent registered); `market.json` reports
  `payment.wallet.operational: false`, `status: "temporarily_unavailable"`, `reason:
  "platform_custody_frozen"` across wallet/x402_edge/x402_legacy/x402; featured listings all
  `paid_execution_enabled: false`; `availability.status: "read_only"`. Sellers can register +
  list but cannot earn. Offer to help test once unfrozen (consistent with Discussion #214).
- **Agent id:** `32e94bca-4911-45ed-a21d-1ae681ba736e` (registered Aug 12).

## 2. Agent Bazaar — BROKEN (register endpoint 404s)
- **⚠️ NO public GitHub.** `The-Swarm-Corporation/agent-bazaar-implementation` is a *different*
  research-paper project (Swarms), NOT the agentbazaar.dev platform. The SDK's
  `runningoffcode/agentbazaar` repo is 404 (private/deleted). **Do NOT file on the Swarms repo.**
- **Contact:** `@agentsbazaar` on X (from docs/SDK). No public Discord/email found.
- **Draft report:** `POST /agents/register` returns HTTP 404 NOT_FOUND via both the official
  `@agentsbazaar/sdk` and raw REST (follows redirect to `www.agentbazaar.dev`). Expected 200
  with `{agent:{pubkey,slug}, websocket:{url,token}}` per docs. Platform shows near-zero
  activity (-3 agents, -$0.05 volume) — early-stage regression blocking the whole onboarding path.

## 3. BountyBook — NEVER PAID OUT (verifier crash + payout rail dead)
- **No public GitHub.** Contact: Discord `discord.gg/BXKTe44Y`, X `@_ptonik` (built by @_ptonik).
- **Draft post:** reproduced code_test verifier crash on job `0a1c6ae8` (inline `outputData`,
  exact documented shape, twice) → `Verification error: Cannot read properties of undefined
  (reading 'length')`, `checksFailed:["ipfs_fetch"]`. Root cause: oracle reads
  `spec.success_condition.required_fields.length` while code_test specs carry `required_files`.
  Plus payout rail never fires: verified jobs show `payout_status=failed` with no
  `payout_tx_hash`, treasury `0x1bc6c2268260c391C7871cF9f2Dfa43207F72f2b` zero lifetime USDC
  outflows on Base. No USDC has ever moved. Operator already has a $150 fix offer open
  (job 8a7bd232) — they know; our report adds independent confirmation + the payout-rail finding.

## 4. Nevermined — NOT broken, just gated on Jordan's API key
- **GitHub:** `github.com/nevermined-io/payments` (public, active, Apache-2.0). No contribution
  needed yet — just needs the NVM_API_KEY (on Jordan's action list).

## Filing guidance
- Agoragentic issue is the highest-value: real reproducible platform bug on an actively-maintained
  repo soliciting test reports. File via `gh issue create` (account ProtoJay4789 is rate-limited/
  flagged — consider a cleaner account or have Jordan file manually).
- Agent Bazaar + BountyBook have no GitHub → hand Jordan the drafted X DM / Discord post to send.
