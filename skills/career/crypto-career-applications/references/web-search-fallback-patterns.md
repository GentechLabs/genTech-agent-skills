# Web Search Blocker & Fallback Patterns

**Date:** July 5, 2026  
**Context:** Job scan attempt failed due to missing FIRECRAWL_API_KEY

---

## Blocker: web_search Requires Firecrawl

**Error message:**
```
Error searching web: Web tools are not configured. Set FIRECRAWL_API_KEY for cloud Firecrawl or set FIRECRAWL_API_URL for a self-hosted Firecrawl instance. Log in to Nous Portal to use managed Firecrawl web tools: run `hermes model`. Billing and credits are managed at https://portal.nousresearch.com/billing.
```

**Fix:**
1. Run `hermes model` to open Hermes model configuration
2. Navigate to https://portal.nousresearch.com/billing
3. Configure Firecrawl billing and credits
4. Set FIRECRAWL_API_KEY in Hermes config

**Impact:** ALL web discovery blocked without this key — job scanning, opportunity discovery, research, etc.

---

## Fallback Pattern: Job Boards Are SPAs

**Problem:** Most modern job boards are JavaScript Single Page Applications (SPAs). `curl` returns HTML skeleton only (client-side rendered).

**Tested Sources:**

| Source | curl result | Actual status |
|--------|-------------|---------------|
| crypto.jobs | 3,695 lines (skeleton HTML) | SPA — needs browser |
| web3.career | 13 lines (redirect) | SPA — needs browser |
| Remotive | 548 lines ("Page Not Found") | 404 — broken URL |
| SailOnChain | 1 char | Unclear |

**Pattern:**
- curl returns `<!DOCTYPE html>` + head section + empty body
- No actual job listings in HTML
- JavaScript renders content on client side
- browser toolset required for real content

---

## Browser Toolset Access (If Available)

**When web_search is blocked but browser tools work:**

1. Use `browser_navigate` to load job board page
2. Wait for JavaScript to render (may need `browser_wait`)
3. Use `browser_snapshot` to capture rendered content
4. Use `browser_console` with JavaScript selectors for structured data:
   ```javascript
   document.querySelectorAll('table tr')  // web3.career tables
   document.querySelectorAll('.job-card')  // generic job cards
   ```

**Note:** If browser tools timeout or fail, the site likely has aggressive bot detection (Cloudflare, DataDome). Fall back to discovery-only via web_search snippets or manual scan.

---

## Manual Scan Pattern (When All Tools Blocked)

**If web_search + browser both blocked:**

1. Jordan manually scans via browser
2. Copy job listings to vault for processing
3. Agent filters and scores via existing validation rules
4. Agent drafts applications using portfolio-first templates

**Not ideal but functional.**

---

## cron-job Troubleshooting

**Existing scanner:** "5-Star Opportunity Scanner — Hackathons + Jobs + Grants" (job_id: 71d5c3e3b245)

**Status check:**
```bash
hermes cron list | grep "5-Star Opportunity Scanner"
```

**If scanner errored:**
1. Check `last_status` and `last_delivery_error`
2. Verify web_search is available (FIRECRAWL_API_KEY configured)
3. Verify job sources are accessible (test each URL via curl or browser)
4. Check scanner prompt for outdated exclusion lists

---

## Key Takeaways

1. **web_search is the primary tool** — configure Firecrawl API key early
2. **SPAs require browser tools** — curl is insufficient for job boards
3. **Existing cron may need debugging** — check status before building new scanner
4. **Manual scan is fallback** — not ideal but keeps pipeline moving