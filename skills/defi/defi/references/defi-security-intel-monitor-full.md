---
name: defi-security-intel-monitor
description: "Autonomous DeFi security incident monitoring and intelligence reconnaissance. Gather post-incident updates from official blogs, protocol statements, governance proposals, competitor responses, and on-chain/off-chain stats dashboards. Compile structured intelligence reports with risk assessment and action items, then save to vault."
version: 1.0.0
author: Gentech
tags: [defi, security, intelligence, monitoring, reconnaissance, incident-response, protocol-analysis]
trigger: "When asked to monitor a DeFi protocol for security updates, post-incident changes, or ongoing risk assessment. Also triggered by scheduled cron jobs for security watch tasks, or when evaluating protocol safety after an exploit, hack, or governance event."
---

# DeFi Security Intelligence Monitor

Run autonomous reconnaissance on a DeFi protocol after (or during) a security-relevant event. Gather evidence from official sources, detect protocol-level changes, assess competitor dynamics, and produce a structured intelligence report.

## Workflow

### 1. Define Scope
Identify what you are monitoring for:
- Protocol-level changes (smart contract upgrades, new governance proposals)
- Official statements (blog posts, Twitter/X threads, Discord announcements)
- Security policy changes (new minimums, enforced configurations)
- Competitor responses (rival protocols capitalizing on the incident)
- On-chain/off-chain statistics (Dune dashboards, protocol metrics)

### 2. Gather Official Sources

**Primary targets:**
- Official blog: `https://PROTOCOL_DOMAIN/blog` — navigate, scroll, extract post titles/dates
- Incident statements: Direct URLs if known, or search blog archive
- Official social: X/Twitter, Telegram, Discord announcements

**Technique — Blog enumeration:**
```
browser_navigate → https://PROTOCOL/blog
browser_console → Array.from(document.querySelectorAll('main a[href*="/blog/"]')).map(...)
```

**Technique — Full post extraction:**
```
browser_navigate → POST_URL
browser_console → document.querySelector('article').innerText
```

### 3. Search for Protocol-Level Changes

**Primary method: direct browser navigation.** Web search (Google, DDG) is frequently blocked by bot detection in headless environments. Do not rely on it as the primary source.

**Direct targets to check:**
- Official blog archive (navigate, scroll, enumerate post titles/dates)
- GitHub releases page: `https://github.com/ORG/REPO/releases`
- GitHub commit history (filter post-incident date range): `https://github.com/ORG/REPO/commits/main/`
- Governance portals: Snapshot (`snapshot.org/#/PROTOCOL`), Tally, protocol forum
- Official docs changelog / integration checklist pages

**Terminal extraction from JS-rendered docs/blog (fallback when browser_console fails):**
```
curl -s URL | sed 's/>/\n/g' | grep -oP 'https://[^<"]+' | head -20
```

**GitHub activity verification (critical for detecting post-incident code reaction):**
Check commit history and releases for any commits tagged after the incident date. **Zero post-incident commits is itself a finding** — "no visible code-level reaction" should be explicitly stated in the report.

**If you must search:**
```
"PROTOCOL_NAME DVN fix" OR "PROTOCOL_NAME mandatory security" OR "PROTOCOL_NAME governance proposal"
```
- Accept that search may return empty; document the gap honestly rather than inferring no news.

### 4. Check On-Chain / Analytics Dashboards

**Dune Analytics:**
- Navigate to `https://dune.com/browse/dashboards?q=PROTOCOL+KEYWORD`
- Common block: Cloudflare bot detection may block automated access
- **Workaround:** Try `BROWSERBASE_ADVANCED_STEALTH=true` if available; otherwise document the gap and rely on cached baselines

**Protocol-specific explorers:**
- LayerZero Scan, Etherscan contract read, Subgraph endpoints
- Use direct API calls when available

### 5. Competitor Intelligence

Search for rival protocols capitalizing on the incident:
- `"Wormhole PROTOCOL_NAME"` / `"Axelar PROTOCOL_NAME"` / `"Hyperlane PROTOCOL_NAME"`
- Check competitor blogs and X accounts for contrast marketing
- **Note:** Competitor responses are often organic (community tweets) rather than formal PR. Formal blog posts are the signal to capture.

### 6. Compile Report

Structure the intelligence report with these sections:

```markdown
# PROTOCOL Security Monitor — Intelligence Report

**Checked:** DATE UTC
**Analyst:** NAME, ROLE @ Gentech
**Sources:** List primary sources

## Executive Summary
**Risk Level: UNCHANGED / IMPROVED / WORSENED**

## 1. Protocol-Level Changes
Finding: [What changed or didn't change]

## 2. Official Blog & Communications
[Table of recent posts with relevance ratings]

## 3. Public Response Assessment
[Beyond blame — what concrete actions were taken?]

## 4. Security Standards
[New minimums? Still recommendation-only?]

## 5. Competitor Responses
[Detected or not detected]

## 6. Dashboard / Statistics
[Verified numbers, or document block]

## 7. Action Items
[Table: Priority | Action | Owner]

## Risk Assessment
[Per-dimension status table]
```

### 7. Save to Vault

- Path: `/root/vaults/gentech/03-Strategies/PROTOCOL-SECURITY-monitor.md`
- Append with date header; maintain running log
- Use `mkdir -p` to ensure directory exists

## Known Obstacles & Workarounds

| Obstacle | Workaround |
|----------|-----------|
| Google search bot detection (sorry page) | Use browser_navigate directly to known URLs; skip search |
| Dune Cloudflare block | Document gap; try direct API query URLs; use BROWSERBASE_ADVANCED_STEALTH if on Scale plan |
| X/Twitter login wall | browser_navigate to profile may still expose posts in snapshot; use xurl CLI if authenticated |
| DuckDuckGo/Bing no results | Search engines may block headless curl; rely on direct site navigation |
| Official docs are JavaScript-heavy | Use browser_console to execute JS selectors and extract innerText |

## Risk Level Rubric

- **IMPROVED:** Protocol enacted an on-chain upgrade or mandatory minimum that materially reduces recurrence risk
- **UNCHANGED:** No protocol-level change; only operator-level or recommendation-level responses
- **WORSENED:** New attack vectors discovered, protocol remains silent, or contagion risk increased

## Example: LayerZero DVN Post-KelpDAO

**Scope:** Monitor for mandatory DVN minimums, competitor responses, and Dune stats migration.

**Key finding:** LayerZero Labs (as a DVN operator) blocked 1/1 configs, but the protocol still allows them. No governance proposal detected. Risk: UNCHANGED.

**Saved to:** `/root/vaults/gentech/03-Strategies/layerzero-dvn-monitor.md`
