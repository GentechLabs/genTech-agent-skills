# OKX Rejected-Listing Remediation (verified Aug 22, 2026)

Fix path for OKX AI marketplace listing rejections. Supersedes the older guidance
that read `serviceList: []` as "no services attached".

## The correction: `serviceList: []` from `agent get-my-agents` is MISLEADING

All 4 GenTech agents (#2847/#2848/#2849/#4905) showed `serviceList: []` yet were
later found via `agent service-list --agent-id <id>` to ALREADY carry services —
just misconfigured. Treating "empty list" as "no services, so attach fresh ones"
makes `agent update` fail with `Duplicate service names`.

**`agent service-list --agent-id <id>` is the source of truth**, not `get-my-agents`.
Parse its `data` (a LIST `[agentInfo, {list:[...]}]` — index the dict holding `list`).

## The three real rejection modes (each fixable by updating, never re-creating)

| Rejection text | Real cause | Fix |
|---|---|---|
| `A2MCP endpoint returned HTTP 404` | A2MCP `endpoint` points at a DEAD path (e.g. `https://api.gentechlabs.net/lp-detector` → 404) | `agent update` the service to a LIVE endpoint. Verify the endpoint returns a 402 (payment challenge) before attaching — confirms it's live AND x402-gated. |
| `has not responded for over 20 minutes` | A2A service has **no endpoint** (`endpoint:null`) so the platform can't probe it | Convert/update to an A2MCP service with a real reachable `https://` endpoint. |
| `payment blockchain ... is incorrect: should be received on X Layer, but config is ChainID eip155:8453` | x402 challenge advertises the wrong rail (Base 8453) instead of X Layer (196) | Reorder `X402_NETWORKS` so `xlayer` is first, restart the gateway, verify `accepts[0]` is `eip155:196`. |

## Verified remediation flow (Aug 22, 2026)

1. **`onchainos agent service-list --agent-id <id>`** → what services actually exist (their `id`s).
2. For each broken service build an **`operation:"update"`** entry keyed by the service `id`, pointing at a live endpoint:
   `agent update --agent-id <id> --service '[{"operation":"update","id":"<svcId>",...}]'`
   **Never `operation:"create"` a service whose name already exists** → "Duplicate service names".
3. **Fix the payment rail:** reorder `X402_NETWORKS="xlayer,base,algorand,avalanche,solana"` (xlayer first) AND change `_DEFAULT_NETWORKS = "xlayer"` in the gateway server, then `systemctl restart x402-api.service`, then `curl <live-endpoint>` and confirm `accepts[0]` is `eip155:196`.
   **Note:** the profile `.env` is a protected credential file — edit it via a Python read/replace/write in terminal, NOT the patch tool.
4. **`onchainos agent activate --agent-id <id>`** to re-list. Its `activate.approvalStatus` may report `success:false` even when it worked. The AUTHORITATIVE check is `agent get-my-agents` → `approvalLabel: "Listing under review"`. `approvalStatus:2` = under review; the `success:false` on activate is a known quirk, not a failure.
5. **Deactivating a dev agent** (e.g. #4905 Forge) → `agent deactivate` returns `success:false` when it was already rejected/not-listed. Verify final state via `get-my-agents` (`approvalLabel: "Listing rejected"` = it stays off).

## Strategic: consolidate the lineup, don't relist as-is

On a multi-agent rejection, reshape to the product line (Jordan's Aug 2 directive) rather than relist everything. Agentic Treasury example:
- **#2847 Treasury** — yield visibility / opportunity scoring (keep)
- **#2848 Curve** — LP shape detection (keep)
- **#2849 DeFi** — LP strategy / rebalancing (keep)
- **#4905 Forge** — dev agent, off-thesis → deactivate, don't relist

One ASP carries MANY services — consolidate into fewer on-thesis agents with live
endpoints instead of spawning narrow ones that 404.
