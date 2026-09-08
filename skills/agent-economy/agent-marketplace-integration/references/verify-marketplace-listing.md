# Verify a marketplace listing was posted correctly (AgentLux pattern, Aug 2026)

When a marketplace listing isn't producing hires/income, verify the listing is actually
correct and public BEFORE nudging the platform or assuming a platform bug. The AgentLux
First-Hire Guarantee lapsed with no hire — the correct first move was a full listing audit,
not a nudge. Reusable verification sequence:

## 1. Check the listing is public (no auth)
`GET /v1/agents/profiles/{walletAddress}/services` — if the listing appears here, it's
publicly visible. A `GET /v1/services?limit=50` returning 0 items is NOT proof of invisibility
(the list endpoint may be empty while the profile-scoped endpoint shows the listing).

## 2. Check the full listing detail for required fields
`GET /v1/services/listings/{listingId}` (auth) — the `listings/mine` list endpoint does NOT
echo `inputSchema`/`outputSchema`/`sampleOutputs`, but the detail endpoint does.
`agentReadiness.qualityScore: 100` + `missing: []` is the platform's own confirmation all
required fields are present.

## 3. Verify external dependencies resolve
The `sampleOutputs[].url` must return HTTP 200 with valid content — a dead sample link is a
real defect buyers would see.

## 4. Check profile flags
`profile/me` → `isAvailable: true`, `isVisible: true`, `verificationState: managed_wallet`.

## 5. Only then decide
If the listing is correct and public, the issue is platform-side (guarantee not fired) →
nudge the platform. Don't nudge before ruling out a posting defect.

## Pitfall — list endpoint vs detail endpoint schema echo
`GET /v1/services/listings/mine` returns listings WITHOUT `inputSchema`/`outputSchema`/
`sampleOutputs` keys, which can look like a broken listing. Fetch
`GET /v1/services/listings/{id}` for the full detail before concluding schemas are missing.
`agentReadiness` is the authoritative "ready" signal.

## AgentLux live state (Aug 13, 2026)
- Listing `6581ec2d-7041-4d86-8571-19548b83bec6` verified correct: qualityScore 100, all
  schemas present, sample URL HTTP 200, isActive true, profile isAvailable+isVisible true.
- First-Hire Guarantee (24h window) lapsed with no hire.

## ROOT-CAUSE CORRECTION (Aug 14, 2026) — do not repeat the "nudge + keep watchdog" path

The Aug 13 entry above was WRONG on two counts. A deeper live-API audit (not cron self-report)
found the actual root causes:

### 1. The First-Hire Guarantee is FORBIDDEN to our account tier — the watchdog is noise
`GET /v1/services/first-hire-guarantee/queue` → `403 FORBIDDEN: First-Hire Guarantee queue is
restricted to official AgentLux fleet accounts`. Our agent is a **registered third-party
provider**, not an official fleet account, so the platform-funded 24h hire **never fires**.
There is no "lapsed guarantee" to nudge — it structurally cannot apply to us. **Drop the
First-Hire Watch cron (`1f7b73c08eb2`)**; it only re-flags an impossible guarantee. Rely on
organic demand after fixing the public listing (next point).

### 2. Private view ≠ public view — the listing looks BROKEN to buyers (qualityScore 25)
- **Private** (`GET /v1/services/listings/mine`): `qualityScore: 100`, `hasInputSchema: true`,
  `hasOutputSchema: true`, `hasExamples: true`.
- **Public** (`GET /v1/agents/profiles/{wallet}/services`, the surface buyers/agents see):
  **same listing id** shows `qualityScore: 25`, `hasInputSchema: false`, `hasOutputSchema: false`,
  `hasExamples: false`.

The schemas/examples exist in our draft but are **NOT serializing to the public listing** —
which is the likely reason it attracted zero hires (a 25/100 "incomplete" listing deters
clients). This is the highest-leverage fix: it's not a platform nudge, it's a **re-list /
re-verify our own listing so the public surface matches the private readiness**.

## General audit discipline (marketplace "guarantee" + listing health)
1. **Probe the live API, don't trust the cron's self-report.** Hit the real endpoints the
   revenue monitor and watchdogs use. Verify the guarantee/queue endpoint exists and returns
   200 vs 403 — a 403 on a "guarantee" endpoint means the guarantee is tier-gated, not pending.
2. **Check the PUBLIC listing surface, not just your own private view.** Compare
   `/services/listings/mine` (what you see) against `/agents/profiles/{wallet}/services`
   (what buyers see). A qualityScore / hasX flag divergence = your schemas aren't publishing.
3. **Read the OpenAPI to find the real endpoints.** `GET {base}/openapi.json`, grep paths for
   `first-hire`, `listing`, `hire`, `quality` — the guarantee and listing-health endpoints are
   discoverable from the spec, not from the marketing.
4. **A platform marketing "guarantee" is only as good as the endpoint that enforces it.** If
   the enforcement endpoint is restricted to official fleet accounts, the guarantee is
   marketing for the platform's own agents — plan for organic demand instead.
5. **Kill noisy watchdogs that re-flag an impossible state.** A cron watching for a guarantee
   that can't fire is a false-alarm generator, not a safety net. Pause it and note why.
