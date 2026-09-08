---
name: Autonomous Web Research
version: 1.1
author: Gentech AI
class: research
description: Strategies for conducting web research when standard search tools are unavailable, covering browser navigation, content extraction, and overcoming bot detection.
---

# Autonomous Web Research

## Overview
Strategies for conducting comprehensive web research when standard web search tools are unavailable or limited. This skill covers techniques for extracting information from websites that employ bot detection, require authentication, or have dynamic content that's difficult to scrape.

## When to Use
- Web search tools (e.g., Firecrawl) are not configured or require API keys
- Websites employ aggressive bot detection (reCAPTCHA, Cloudflare)
- Dynamic content requires JavaScript execution
- Authentication is required to access information

## Workflow

### 0. MCP-First Check — Before Any Browser Work
Before navigating websites or fighting with bot detection, check if an MCP server can do the job. Pay catalog ($0.001–$0.10/call) offers APIs for many blocked-search scenarios:
- **Tripadvisor** — search hotels, restaurants, attractions ($0.01/call)
- **Google Places** — nearby/text search for businesses ($0.001/call)
- **BRIJ Travel** — flight search and booking ($0.10/call)
- **Wolfram Alpha** — computational queries ($0.01/call)
- **ScreenshotOne** — render pages as images ($0.01/call)

**Rule (Jul 24 2026):** If a web scrape hits a paywall, CAPTCHA, or bot detection, check `mcp__pay__search_catalog()` for relevant APIs BEFORE spending time on browser work. Example: Agoda blocked browser scraping → Tripadvisor MCP could search Lapu-Lapu hotels directly.

### 1. Direct Navigation to Official Sources
Start with official sources (company blogs, documentation, official announcements) as they are most reliable.

**Technique**: Use browser navigation to access official websites directly rather than relying on search engines.

### 2. Content Extraction via Browser Snapshots
When dynamic content prevents easy scraping, use browser snapshots to capture page content.

**Technique**: 
- Navigate to the target page
- Use `browser_snapshot` to capture full page content
- Parse the snapshot for relevant information
- Scroll down to load more content if needed

### 3. Direct URL Access for Specific Content
If you know the specific content you need, try to construct the direct URL.

**Technique**:
- From the blog or documentation index, identify patterns in URLs
- Navigate directly to the content page
- Use `browser_click` to interact with elements if needed

### 4. Terminal-Based Content Retrieval
For documentation and content-rich sites, use terminal commands to fetch content directly.

**Technique**:
- Use `curl` to download HTML pages
- Use `curl` to access static content files (e.g., documentation index files)
- Parse the downloaded content for relevant information

### 5. Search Within Sites
When direct access is blocked, use site-specific search if available.

**Technique**:
- Locate search functionality on the site
- Use `browser_type` and `browser_press` to submit search queries
- Extract results from the search results page

### 6. Handling Bot Detection
When encountering bot detection challenges:

**Techniques**:
- Accept cookies when prompted
- Use browser navigation with delays between actions
- Try accessing different pages first to establish a browsing pattern
- If detection persists, switch to alternative sources

### 7. Information Synthesis
Combine information from multiple sources to build a comprehensive picture.

### 8. Authenticated / agent-gated pages — remote CDP attach to Jordan's browser
When a page needs Jordan's LOGIN (not just a fetch): attach Gentech's browser stack to a Brave instance on his PC (`gentechhq`, tailnet 100.102.61.86) over Chrome DevTools Protocol, and drive it with his sessions.

- **One-time on his PC:** dedicated-profile Brave `--remote-debugging-port=9222 --user-data-dir="C:\gentech-brave-profile" --no-first-run` + `tailscale serve --bg --tcp=9222 tcp://127.0.0.1:9222` (tailnet-only; default-profile CDP is blocked since Chromium M136).
- **Gentech attach:** `BU_CDP_URL=http://100.102.61.86:9222` env into `ensure_daemon()` — harness-native, verified in `browser_harness/daemon.py`. Pre-flight: `curl http://100.102.61.86:9222/json/version`.
- **Full procedure + fallbacks + security rules:** vault `00-HQ/brave-cdp-bridge-setup.md`. Status Sep 3 2026: path verified, end-to-end attach not yet live-tested (Jordan hasn't run his side).
- **Use for:** DoraHacks forms, Discord faucets, AKINDO access forms — anything Jordan currently does the 2-minute human step for. Automation profile = build tasks only, never banking/personal email.

**Technique**:
- Cross-reference information from official blogs, documentation, and third-party sources
- Look for patterns and confirmations across sources
- Document findings systematically

## Pitfalls
- **Don't rely solely on search engines** when tools are unavailable - they often lead to bot detection
- **Don't give up** when encountering access restrictions - try alternative approaches
- **Do verify information** from multiple sources when possible
- **Do document your methodology** so it can be replicated in future sessions
- **Search engines may universally block from server IPs** — Google, Bing, and DuckDuckGo all serve CAPTCHAs from certain server IPs (confirmed May 2026). If all three block, stop retrying and fall back to: (1) vault-tracked URLs, (2) direct URL guessing from known patterns, (3) `curl -sL` for status codes and raw HTML, (4) ask Jordan to search manually.
- **Low-res screenshot? Don't ask for a re-screenshot — recover the live page.** vision_analyze on compressed Telegram screenshots often can't read fine print (table cells, dates, criteria weights, prize splits). Instead: extract the exact hero title from what IS legible → `web_search` that exact title → `web_extract` the live page. Platform pages (AKINDO, Devpost, Luma) extract fine — only DoraHacks blocks. Proven Sep 3 2026: recovered every illegible detail of the SoSoValue×AKINDO buildathon (timeline, judging criteria, submission counts, prize network) with zero asks. Re-screenshot request = last resort.

## Tools Used
- browser_navigate
- browser_click
- browser_type
- browser_press
- browser_scroll
- browser_snapshot
- terminal (curl)

## References
This skill was developed during a LayerZero DVN security monitor check where web search tools were unavailable, requiring creative approaches to gather information from official sources while avoiding bot detection.