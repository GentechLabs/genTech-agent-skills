# Superteam Earn — Bounty & Marketplace Scanning

## Overview
`earn.superteam.fun` is Superteam's crypto-bounty / web3-job / grant marketplace, Solana-ecosystem focused, paying in USDC/USDG/SOL. There is an agent-eligible track at `/earn/agents`. This is a SELL-side income rail (bounties we complete) and a discovery source.

## ⚠️ Agent API returns STALE data — do NOT trust it for live bounties
Verified Aug 15, 2026: `GET https://superteam.fun/api/agents/listings/live?take=100` with the stored key (`sk_bf47...`, lives in the gizmo profile) returned ONLY already-closed listings — every `deadline` was past and `winnersAnnouncedAt` set, yet `status=OPEN`. The endpoint is not reliable for surfacing genuinely live, open bounties.

**Reliable approach — pull the rendered site via the browser tool:**
```
goto_url("https://superteam.fun/earn/all?tab=bounties")
# extract a[href*='/earn/listing/'] card texts: title, prize, "Due in Nd", submissions count
```
Card text looks like: `Title — Superteam X | Bounty | Due in 7d | 5,000 USDC`.

## ⚠️ REGIONAL LOCKS — critical filter for Jordan (Ohio/Cincinnati, USA)
Many Superteam bounties are region-locked to a single country and show **"This listing is only open for people in [Country]"**. Jordan is **ineligible** for:
- Canada-only, Vietnam-only, Netherlands-only bounties
- All Superteam-[Country]-chapter bounties (Nepal, Brazil, Ukraine, Balkan, etc.)

Pattern observed Aug 15, 2026: the best stack-fit dev bounties in a batch were exactly the region-locked ones (e.g., a $1K Solana ecosystem dashboard was Canada-only). Always check the individual listing page before recommending.

## Single-listing detail check
Open `superteam.fun/earn/listing/<slug>` in the browser, read `document.body.innerText`. Find:
- **Region**: "only open for people in X" (if present → regional lock)
- **Prize + rank breakdown**: under "Total Prizes"
- **Submissions count**: beside the prize
- **Skills needed**: tags on the listing
- **Winner announcement date**: scheduled date

## Realistic yield
Global stack-fit dev bounties are rare in any given batch — most live bounties skew content / X-thread / UGC. When a Global dev bounty does appear (e.g., Veilo Solana smart-contract audit, $2K), check the submissions count FIRST: 100+ submissions (Veilo had 157 with 5 days left) = low-odds long-shot, not sprint-worthy. Higher ROI usually lives in active hackathon builds than in the Superteam bounty batch.

## Workflow
1. Navigate to the rendered listing page (browser tool) — not the agent API.
2. Extract live bounty cards (title, prize, due, submissions).
3. Filter OUT region-locked listings (Jordan = USA/Ohio, reject country-locked).
4. For any Global dev bounty, check submissions count — reject 100+ as long-shot.
5. Save scan to vault: `09-Green Room/superteam-bounty-scan-{date}.md`.
6. Recommend pursue only if Global + dev-stack + low submission count.

*Verified Aug 15, 2026. Companion scan at `09-Green Room/superteam-bounty-scan-2026-08-15.md`.*
