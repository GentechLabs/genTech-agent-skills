---
name: link-research-summary
description: "Research and summarize links Jordan shares — GitHub repos, X/Twitter posts, articles. Fetch content efficiently, extract key info, provide structured analysis with context and implications."
version: 1.6.0
author: Gentech
license: MIT
tags: [research, summary, github, twitter, link-analysis]
---

# Link Research & Summary

When Jordan shares a URL, research it and provide a structured summary. Optimize for speed and depth.

## URL Type Detection

| URL Pattern | Method | Tool |
|---|---|---|
| `github.com/{owner}/{repo}` | GitHub API | `curl` + `python3` |
| `x.com/{user}/status/{id}` or `twitter.com/...` | **fxtwitter API (MUST TRY FIRST)** | `curl api.fxtwitter.com` |
| `facebook.com/share/v/...` or `facebook.com/.../videos/...` | **No automated extraction** | `web_search` for context, ask Jordan to describe |
| `clawhub.ai/skills*` or `clawhub.ai/skills?search=*` | ClawHub browse | `browser_navigate` → search → click listing |
| Agent tooling / API products (no URL, just name) | DuckDuckGo lite + direct API probe | `curl` the product API endpoints |
| **Web research (any URL)** | **Jina Reader (FIRST)** | **`curl r.jina.ai/URL`** |
| **GitHub repo/README** | **GitHub API** | **`curl api.github.com/repos/...`** |
| Other URLs | Agent Reach or curl | `agent-reach doctor` → `curl -sL URL` |

## ⚡ Web Research Toolkit (Jul 2026 — Firecrawl Replacement)

### 🚫 NEVER draw a NEGATIVE from a docs dump you haven't proved complete

**`llms.txt` / `llms-full.txt` are convenience indexes, not the documentation.** Mintlify (and similar hosts)
publish `llms-full.txt` as a **curated subset that silently omits dedicated pages.**

**Measured on Glider's docs (2026-09-25):** `llms.txt` listed **60 pages**; `llms-full.txt` was 49,818 chars and
**did not contain pages that provably existed** — *"Patch strategy fees"* → absent; the
`/v2/strategies/{strategyId}/fees` endpoint → absent. I searched the subset, found nothing, and published *"no fee
mechanism is documented."* **It was wrong.** The mechanism is `GET`/`PATCH /v2/strategies/{strategyId}/fees`, with
scopes `fees:read` / `fees:write` — sitting on a page the dump never included.

**Searching a subset and finding nothing FEELS like evidence. It is not.** Same failure shape as the false PR
receipts: **absence from a list is not absence.**

**Three rules:**
1. **Grep the actual PAGES before claiming something isn't documented.** On Mintlify, resolve real URLs from
   `llms.txt` and fetch `https://docs.<host>/<page>.md` — the raw markdown works and renders nothing JS.
2. **Prove the corpus is complete before drawing a negative from it** — probe for a page you *know* exists
   (`"Create Strategy"` → present, `"Patch strategy fees"` → absent ⇒ the dump is partial, so the negative is void).
3. **Search singular AND plural: `\bfees?\b`, not `\bfee\b`.** I nearly published "there is no fee mechanism"
   because I searched the singular while the docs name it **`fees`** throughout.

**When a peer agent or a DM partner contradicts one of your findings, re-verify immediately** rather than
choosing a side. Treasury's correction was right, mine was wrong — the corrected line is worth more than the
original claim.


When Firecrawl/web_extract/browser tools are unavailable, use these curl-based tools:

### Jina Reader (any URL → markdown, no API key)
```bash
curl -s "https://r.jina.ai/URL"
```
Returns Title + URL Source + clean Markdown. **First attempt for any URL.**
**Limitations:** GitHub blocked (use API). Rate-limited on aggressive use (wait 2 min).

### GitHub API (structured JSON)
```bash
# Repo detail
curl -s "https://api.github.com/repos/owner/name"
# README (base64 decode)
curl -s "https://api.github.com/repos/owner/name/readme" | python3 -c "import json,sys,base64; print(base64.b64decode(json.load(sys.stdin)['content']).decode())"
# Search
curl -s "https://api.github.com/search/repositories?q=KEYWORD&sort=stars&per_page=5"
```

### fxtwitter API (X/Twitter)
```bash
curl -s "https://api.fxtwitter.com/i/status/TWEET_ID"
```

### Agent Reach (v1.4.0, 60k ⭐, installed)
`agent-reach doctor` → checks RSS, V2EX, Bilibili, Reddit, YouTube channels.

### Direct curl
```bash
curl -sL "URL"              # basic fetch
curl -sI "URL"              # headers only
```

**Rule:** Ask "can I curl this?" before any browser work. Most services have API endpoints.

## ⚡ X/Twitter Quick Reference (USE THIS FIRST)

When you see `x.com/*/status/*` or `twitter.com/*/status/*`:

```bash
# STEP 1: fxtwitter API (works from VPS, no auth, reliable)
curl -s "https://api.fxtwitter.com/i/status/{TWEET_ID}" | python3 -c "
import json, sys
d = json.load(sys.stdin)['tweet']
print(f\"Author: {d['author']['name']} (@{d['author']['screen_name']})\")
print(f\"Text: {d['text']}\")
print(f\"Date: {d['created_at']}\")
urls = [u.get('url') for u in d.get('urls', [])]
if urls: print(f\"URLs: {urls}\")
media = d.get('media', {})
if media.get('photos'): print(f\"Photos: {[p.get('url') for p in media['photos']]}\")
if media.get('videos'): print(f\"Videos: {[v.get('url') for v in media['videos']]}\")
# Quoted tweets — check for text AND articles (long-form tweets)
qt = d.get('quote') or d.get('quoted_tweet')
if qt:
    print(f\"Quoted: @{qt['author']['screen_name']}: {qt['text'][:200]}\")
    art = qt.get('article', {})
    if art and art.get('title'):
        print(f\"Article: {art['title']}\")
        print(f\"Preview: {art.get('preview_text','')[:500]}\")
"
```

**Pitfall:** Quoted tweets can contain long-form articles (`article.title`, `article.preview_text`) that aren't in `text`. Always check the `article` field on quoted tweets — the real substance is often there, not in the 280-char text.

**If fxtwitter fails, try these in order:**
1. **Twitter oEmbed API** — `curl -s "https://publish.twitter.com/oembed?url=https://x.com/i/status/{TWEET_ID}"` — returns HTML blockquote with tweet text, author name, and date. No auth needed, works from VPS. Parse the HTML or extract from JSON `html` field.
2. `web_search(query="site:x.com {TWEET_ID}")` — search engines index tweets
3. `web_search(query="@{author} {keywords from URL context}")` — broader search
4. `browser_navigate` → `browser_snapshot` — last resort (often times out from VPS)
5. Ask Jordan to paste the content

**DO NOT skip fxtwitter and go straight to `web_extract`** — `web_extract` uses DDGS backend which cannot extract URL content. It WILL fail for X/Twitter links.

**Critical: `web_extract` Backend Limitation**
The current `web.extract_backend` is set to `ddgs` (DuckDuckGo), which is search-only and **cannot extract URL content**. Any call to `web_extract` will fail with "DuckDuckGo (ddgs) is a search-only backend and cannot extract URL content." 
- For URL extraction, use **TinyFish Fetch** (primary) or **`browser_navigate`** (fallback).
- `web_search` still works fine with DDGS backend — only URL extraction is broken.
- To fix permanently: set `web.extract_backend` to `firecrawl`, `tavily`, `exa`, or `parallel` in config.

### TinyFish Search & Fetch (Primary Web Research Tool)

TinyFish provides structured, agent-friendly web data. **Search and Fetch are free.**

**API Key:** `TINYFISH_API_KEY` in vault `secrets.env`. Set as env var before calling.

**Search** — fast structured web search, JSON results, rank-stable:
```bash
curl -s "https://api.search.tinyfish.ai?query=YOUR+QUERY" \
  -H "X-API-Key: $TINYFISH_API_KEY"
```

**Fetch** — any URL → clean markdown/JSON/text. Full browser rendering, strips nav/scripts/cookie banners:
```bash
curl -s -X POST https://api.fetch.tinyfish.ai \
  -H "X-API-Key: $TINYFISH_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://example.com"]}'
```

**When to use TinyFish vs browser tools:**
- **TinyFish Search** replaces DuckDuckGo scraping and `web_search` for structured queries
- **TinyFish Fetch** replaces `web_extract` and `browser_vision` for reading specific pages
- **Browser tools** still needed for: interactive flows (clicking, forms), JS-heavy SPAs, auth-gated content, or when TinyFish returns incomplete data

**Pitfall:** TinyFish Fetch returns clean text but may miss content loaded by heavy JavaScript. If the result looks incomplete, fall back to `browser_navigate` + `browser_snapshot`.

### Terminal curl as double-fallback escape hatch

When both `web_extract` (DDGS backend failure) AND `browser_navigate` (timeout) fail on the same batch of URLs, use `terminal` + `curl -sL` to fetch raw content directly. This is especially effective for GitHub repos where `raw.githubusercontent.com` gives clean markdown without any bot detection:

```bash
# GitHub READMEs — bypass all web tools entirely
curl -sL "https://raw.githubusercontent.com/{owner}/{repo}/main/README.md" | head -150

# GitHub docs/specs — often in /docs/ directory
curl -sL "https://raw.githubusercontent.com/{owner}/{repo}/main/docs/filename.md" | head -150

# Any raw text file — .md, .txt, .json, .yaml all work
curl -sL "https://raw.githubusercontent.com/{owner}/{repo}/main/path/to/file"
```

**When to use this pattern:** Any time you need content from a GitHub repo's file tree and both web_extract and browser have failed. Also works for raw content on other hosts (e.g., `raw.githack.com`, self-hosted docs). Fall back to this AFTER 2 failed web tool attempts on the same URL batch — don't start here.

**Pitfall:** `terminal curl` is foreground-only. For 3+ URLs, consider using `execute_code` with `from hermes_tools import terminal` to batch them in a loop rather than making sequential terminal calls.

**Also available:** MCP server at `https://mcp.tinyfish.ai`, Python SDK (`pip install tinyfish`), CLI (`npm install -g @tiny-fish/cli`).

> **Full API reference:** See `references/tinyfish-api-reference.md` for endpoints, auth, response formats, and SDK usage.

### Phonetic Variant Search (Name Correction Pattern)

When Jordan mentions a project/product name that returns zero results in vault and session history, **try phonetic variants before giving up**. Voice messages and casual speech often produce misspellings or alternate renderings of proper nouns.

**Pattern:**
1. Search vault + sessions for the exact name → 0 results
2. Try phonetic alternatives: `GenLayer` ↔ `JinLayer` ↔ `Jin Layer` ↔ `Gen Layer`
3. Search web with variants: `"JinLayer" blockchain`, `"GenLayer" blockchain`
4. If web search returns a strong match for a variant, confirm with Jordan: "Did you mean [X]?"
5. Proceed with research on the confirmed name

**Common variant types:**
- J/G confusion: `GenLayer` → `JinLayer` (voice recognition error)
- Spacing: `OpenAI` → `Open AI`
- Abbreviations: `Anthropic` → `Anthro`
- Hyphenation: `x402` → `x-402` → `X402`

**Why this matters:** Jordan uses voice messages frequently. Voice-to-text produces systematic errors on proper nouns, especially less well-known project names. The agent should adapt, not ask Jordan to repeat himself.

### Agent Tooling & Skill Marketplaces

When Jordan references a product by name (not a URL) — especially agent frameworks, skill registries, DeFi APIs — research it via:

**Domain Probing (do this FIRST — before search engines):**
1. **Try predictable domains** in this order: `https://{name}.ai`, `https://{name}.sh`, `https://{name}.dev`, `https://{name}.com`, `https://app.{name}.ai`, `https://cli.{name}.ai`, `https://docs.{name}.com`
2. **Check page source for links** — `browser_console` with `Array.from(document.querySelectorAll('a')).map(a => a.href)` to find hidden docs/app/CLI links
3. **Look for SKILL.md or docs files directly** — `curl -s "https://{domain}/SKILL.md"` or `https://{domain}/docs` — many agent tools publish setup instructions this way
4. **Search engines LAST** — only if domain probing fails. Google/Bing/DuckDuckGo all have aggressive bot detection that wastes time

**Why domain probing first:** Search engines are unreliable for new/niche tools (bot detection, indexing lag). Direct domain guessing is faster and more reliable — most agent tools use `{name}.ai` or `{name}.sh`.

**After finding the site:**
5. **Hit the API directly** — many agent-tooling products expose REST APIs. Try `curl` on common endpoints (`/api/skills`, `/api/v1/health`, `/docs`) to verify the API actually works before recommending it
6. **Check ClawHub** (`clawhub.ai/skills?search={name}`) — many agent skills are listed there with security scan results
7. **Look for `[ARSENAL-HOSTED]` or `[DEMO MODE]` tags** in skill descriptions — hosted means they run the infra, demo means it returns fake data

See `references/agent-tooling-evaluation.md` for the full methodology.

### Agent Marketplaces (where agents work, not just tools)

When Jordan shares a platform where AI agents register, bid on tasks, and get paid — that's an agent marketplace, not a tool registry. Key difference: these are revenue opportunities for our agents, not tools they consume.

**Evaluate using**: `references/agent-marketplace-evaluation.md` — covers platform maturity, SDK/MCP/API integration, registration flow, reputation system, payment model, token economics, and Gentech fit assessment.

**Integration priority**: MCP server support = plug-and-play with Hermes. REST API = custom cron job. SDK-only = more effort.

**Gentech angle**: Register agents early (free), build reputation while budgets are low, automate task monitoring via MCP/REST when volume grows.

## ERC-8004 Agent Registry (8004scan.io)

When researching on-chain AI agents, use the 8004scan public API:

```bash
curl -sk "https://8004scan.io/api/v1/agents?limit=20" \
  -H "Accept: application/json" \
  -H "User-Agent: Mozilla/5.0 (compatible; GenTechLabs/1.0; +https://gentechlabs.net)"
```

Returns JSON with `items` array (each: name, chain_id, owner_address, x402_supported, total_score, description, created_at) and `total` count.

**Chain IDs:** 1=Ethereum, 8453=Base, 196=X Layer, 97=BNB Testnet

**Use cases:**
- Find agents with `x402_supported: true` (potential x402 gateway customers)
- Track agent registration volume by chain
- Discover named agents (not "Agent #xxxxx") with descriptions
- Monitor Base chain (8453) for ecosystem growth

**Monitor cron job:** Runs hourly, delivers to Labs group. Script at `/root/.hermes/scripts/8004scan-monitor.py`.

> **Reference:** `references/8004scan-agent-monitor.md` — full API reference, monitor script details, and ecosystem context.

## Monid — Agent-Native Tool Router

When researching agent tool marketplaces or considering listing our x402 services, Monid is the primary platform to evaluate:

- **1,300+ tools** across 13+ providers, pay-per-call, one balance
- Supports **x402 payments** natively
- Lists **Blockrun** (our MCP provider) — already in our ecosystem
- **Become a provider:** `https://forms.gle/NLPchCCwnTP6zQhV8`
- **Docs:** `https://monid.ai/docs`

> **Reference:** `references/monid-platform-evaluation.md` — full evaluation, API reference, competitive landscape, and next steps.

## GitHub Repos (Primary Pattern)

Use the GitHub REST API — no auth needed for public repos, no rate limit issues for occasional requests.

### Step 1: Get repo metadata + README in parallel

```bash
# Metadata (stars, license, language, description) — API is reliable for this
curl -s "https://api.github.com/repos/{owner}/{repo}" | python3 -c "
import json, sys
data = json.load(sys.stdin)
for key in ['full_name', 'description', 'stargazers_count', 'forks_count', 'language', 'license', 'created_at', 'updated_at', 'topics']:
    print(f'{key}: {data.get(key, \"N/A\")}')"

# README content — prefer raw.githubusercontent.com over API (more reliable, full content, no base64)
curl -sL "https://raw.githubusercontent.com/{owner}/{repo}/main/README.md" | head -120
# If 'main' branch doesn't exist, try 'master'
```

**Why raw URL over API:** The GitHub API `/readme` endpoint returns base64-encoded content and can hit rate limits. `raw.githubusercontent.com` gives plain markdown directly and almost never fails. Use `head -120` to get the intro + features without downloading the whole file.

### Step 1b: "Check Brain" — Searching Our Own History

When Jordan says "check brain", "we looked into X", or references past research, he's asking you to search both session history AND vault for prior discussions on that topic. Do this BEFORE writing a fresh summary.

```bash
# Session history search (recent decisions, conversations, context not yet in vault)
session_search(query="topic keywords")

# Vault content search (documented research, notes, assessments)
grep -rli "topic keywords" "$VAULT" --include="*.md"
```

If you find past work, reference it: "We covered this on [date] — [brief summary of what was concluded]. Anything new you want to add?"

### Step 2: Analyze & Summarize

Structure the summary as:
1. **What it is** — one-liner description
2. **Key features/capabilities** — bullet list
3. **Why it matters** — context, positioning vs alternatives
4. **Relevance to GenTech** — how it connects to our projects
5. **Action** — save to vault? Try it? Bookmark?

### Pitfalls
- README truncation at 8000 chars is usually fine; the important stuff is in the first section
- If README is missing, check the repo description and topics for context
- Some repos have massive READMEs — focus on Quick Start and Features sections
- `license` field can be null — note "no license" explicitly

## Search Engine & Site Blocking

### Cloudflare / Bot Detection on Target Sites

When the target site (not a search engine) shows Cloudflare "Verify you are human" or similar:

1. **Browser approach:** Click the checkbox, wait for verification. Cloudflare Turnstile sometimes passes on retry.
2. **If browser fails:** Try `curl` with browser User-Agent — some Cloudflare challenges are JS-only and curl gets through.
3. **If both fail:** Search for the content elsewhere:
   - `curl -sL "https://lite.duckduckgo.com/lite/?q=QUERY" -A "Mozilla/5.0 ..."` (see below)
   - PR/press releases: try `prnewswire.com`, `businesswire.com`, `globenewswire.com` directly
   - GitHub repos: use `raw.githubusercontent.com` (bypasses Cloudflare entirely)
   - Cached versions: `webcache.googleusercontent.com` (unreliable, often blocked too)

### DuckDuckGo Lite as Search Fallback

When Google/Bing/DuckDuckGo all block the browser with CAPTCHAs, use the lite HTML endpoint via curl — it almost never triggers bot detection:

**Pitfall — empty results:** DuckDuckGo lite intermittently returns valid HTML with zero result links (empty `result-link` class matches). This happens silently — no error, just no output. If two consecutive queries return nothing, skip DDG lite entirely and fall back to `browser_navigate` directly to the product's website or docs. Don't burn time retrying DDG lite variations.

```bash
curl -sL "https://lite.duckduckgo.com/lite/?q=YOUR+QUERY" \
  -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" 2>/dev/null | \
  python3 -c "
import sys, re
html = sys.stdin.read()
# Extract result links and snippets
links = re.findall(r'class=.result-link.>(.*?)</a>', html)
snippets = re.findall(r'class=.result-snippet.>(.*?)</td>', html, re.DOTALL)
for i, (link, snip) in enumerate(zip(links, snippets)):
    clean = re.sub(r'<[^>]+>', '', snip).strip()
    print(f'{i+1}. {link}')
    print(f'   {clean}')
    print()
"
```

**Pitfall:** DuckDuckGo lite is HTML-only, no JavaScript. It works because it looks like a basic form submission, not a bot. Don't upgrade to the standard DuckDuckGo URL — that triggers CAPTCHAs.

### CAPTCHA Blocking on Search Engines (Browser)

Google, DuckDuckGo, and Bing frequently block headless browsers with CAPTCHAs. When this happens:

1. **Skip search engines entirely** — go directly to the target site
2. For model/library research → `huggingface.co/{org}` or `huggingface.co/models?search={query}`
3. For code → `github.com/{org}` or `github.com/search?q={query}`
4. For docs → the project's own docs site

Direct site browsing is often faster than search anyway, since you land on the exact content instead of a results page.

### CloakBrowser — CAPTCHA/Bot Detection Bypass (New Tool)

When standard browser tools hit Cloudflare Turnstile, reCAPTCHA, or other bot detection walls:

**Install:** `pip install cloakbrowser` (Python) or `npm install cloakbrowser` (JS)

**What it does:** Stealth Chromium with 49 C++ source-level patches. Passes 30/30 bot detection tests including Cloudflare Turnstile, reCAPTCHA v3 (0.9 human score), FingerprintJS, and BrowserScan.

**Python usage (drop-in Playwright replacement):**
```python
from cloakbrowser import launch
browser = launch()  # auto-downloads stealth binary
page = browser.new_page()
page.goto("https://cloudflare-protected-site.com")
# humanize=True for mouse/keyboard behavioral stealth
```

**When to use:** Luma registration forms, DoraHacks CAPTCHA, Cloudflare-protected sites, any headless browser block. Replaces the old "ask Jordan to click" pattern for Cloudflare Turnstile.

**Pitfall:** 200MB binary download on first run. Not needed for simple pages — only deploy when standard browser tools hit detection walls.

### `browser_vision` Model Failures

`browser_vision` can fail with "Not supported model" errors when the configured vision model is unavailable or misconfigured. The screenshot is still captured even when analysis fails.

**Fallback pattern:**
1. Check if `browser_vision` returned a `screenshot_path` — the image exists even if analysis failed
2. If vision fails, describe the image content based on context clues (page title, URL, surrounding elements)
3. For image analysis, try alternative approaches: `browser_get_images` to confirm the image loaded, then describe based on context
4. If the image is critical, ask the user to describe it or paste the text

**Known failure mode:** `gemini-3-flash-preview` returns 400 — this is a provider config issue, not a bug in the browser tool.

## Mobile Screenshot Extraction (Hackathon Pages, Forms, Registration Screens)

When Jordan sends multiple screenshots of the same page (common for hackathon registration, Devpost pages, or form flows):

1. **Don't treat each screenshot as separate research** — they're views of the same page, scrolled. Synthesize across all screenshots into ONE coherent summary.
2. **Extract structured data** — For hackathon pages, pull: name, deadline, prizes, tracks, requirements, participants, organizer. For forms: fields, labels, pre-filled values.
3. **Cross-reference screenshots** — Later screenshots often show content below the fold (requirements, tracks, submission rules) that earlier screenshots miss. The full picture emerges only when you combine them.
4. **Present as a single briefing** — Not "screenshot 1 says X, screenshot 2 says Y" but a unified summary: "Here's the hackathon: [name], deadline [date], $[prize], tracks are [list]."

**Pitfall:** Jordan sends screenshots because he's on mobile and can't copy-paste. He expects the agent to do the synthesis work, not ask him to re-share or clarify. If a screenshot is ambiguous, use vision_analyze with a specific question rather than asking Jordan.

## Articles & Blog Posts
curl -s -L "https://api.fxtwitter.com/status/{id}" | python3 -c "
import json, sys
data = json.load(sys.stdin)
tweet = data.get('tweet', {})
print('URLs:', [u.get('url') for u in tweet.get('urls', [])])
media = tweet.get('media', {})
if media.get('photos'):
    for p in media['photos']: print('Photo:', p.get('url'))
if media.get('videos'):
    for v in media['videos']: print('Video:', v.get('url'))
if tweet.get('quoted_tweet'):
    qt = tweet['quoted_tweet']
    print('Quoted:', qt.get('author', {}).get('screen_name'), qt.get('text')[:200])
"
```

**Pitfall:** Many promotional tweets (hackathon announcements, product launches) put the registration/link in a reply thread or card, not in the tweet text itself. If fxtwitter shows no URLs, check the card field or navigate to the tweet in browser to find the actual link.

### Pitfalls
- Tweet images often contain key context (title cards, charts) that `xurl read` doesn't capture — use `browser_vision`
- **Video-only tweets**: If a tweet has a video but no URLs/text links, the fxtwitter API returns the video URL but not a transcript. The video may contain the actual product demo, announcement details, or links shown on screen. Either watch the video via `browser_navigate` to the video URL, or look for supplementary links in the tweet's card field or replies.
- Quoted tweets may have the real substance — read both the main tweet and the quote
- **xurl auth failures (401):** If `xurl read` returns 401 Unauthorized, fall back to the fxtwitter API directly: `curl -s "https://api.fxtwitter.com/status/{id}" | python3 -c "import json,sys; d=json.load(sys.stdin)['tweet']; print(d['text'])"`. No auth needed, works reliably. Parse nested fields like `author`, `urls`, `media`, `quoted_tweet` from the JSON response.
- `xurl read` returns 401 Unauthorized frequently (May 2026) — always try fxtwitter first
- Tweet text may not contain URLs even when the tweet is promoting something — extract from `urls`, `media`, and `card` fields

## Facebook URLs

Facebook blocks automated extraction aggressively — `web_extract` (DDGS backend) and `browser_navigate` both timeout. There is no reliable API fallback.

**When Jordan shares a Facebook link:**
1. **Try `web_search`** with the URL or key phrases from the URL — sometimes search engines index the content
2. **Try `web_search`** with the video/post title or author name — broader search may find coverage elsewhere
3. **If search fails, ask Jordan** to describe what the video/post is about — he'll give you the gist in one message
4. **Once you have the topic**, research it via standard web search and provide the analysis Jordan expects

**DO NOT:**
- Loop on `browser_navigate` to facebook.com — it will timeout every time
- Try `web_extract` — DDGS backend cannot extract URL content
- Ask Jordan to copy-paste the full video transcript — he's on mobile, just ask for the topic

**Pattern:** Facebook links are conversation starters, not extraction targets. Jordan shares the link to introduce a topic, then explains it himself. Roll with that — your job is to research the topic once he explains it.

---

## YouTube Videos

When Jordan shares a YouTube link:

1. **oEmbed API (try FIRST — fastest, most reliable):** Extract the video ID from the URL (`v=` or path after `youtu.be/`), then:
   ```bash
   curl -s "https://www.youtube.com/oembed?url=https://youtu.be/{ID}&format=json"
   ```
   Returns JSON with `title`, `author_name`, `thumbnail_url`. No auth, no bot detection, works from servers. Use the title to search for transcripts and deeper context via `web_search`.

2. **Search for transcript/deeper context:** Once you have the title from oEmbed, search for written coverage:
   ```bash
   web_search(query="site:youtube.com \"{video_title}\" transcript")
   web_search(query="{video_title} summary")  # blog posts, articles discussing the video
   ```

3. **`video_analyze`** — only if the video file is accessible and under 50MB. Rarely works for YouTube content.

**Fallback chain when oEmbed fails (rare):**
- `yt-dlp --dump-json --no-download` — works but frequently hits bot detection from server IPs
- `browser_navigate` to the YouTube page — often times out
- `web_extract` — will fail (DDGS backend limitation, YouTube URL extraction not supported)

**Pitfall:** YouTube videos are rarely under 50MB. `video_analyze` works best for short clips. For full-length videos, rely on oEmbed metadata → search → web coverage summaries.
**Pitfall:** `yt-dlp` and `browser_navigate` to YouTube are unreliable from server IPs (bot detection). Always try oEmbed first — it bypasses all bot detection because it's a simple oEmbed spec endpoint.

## Articles & Blog Posts

Use `browser_navigate` → extract content → summarize.

### Step 1: Extract content

Use the fast JS extraction from the "Other URLs" section above. If the page has an `<article>` tag, pull it directly.

### Step 2: Summarize

Structure as:
1. **What it is** — title, author, publication, date
2. **Core thesis** — the main argument or technical contribution
3. **Key details** — bullet points of the important specifics
4. **Context & positioning** — how it fits into the broader landscape
5. **Relevance to GenTech** — what this means for our projects/builds
6. **Action** — save to vault? Build on it? Bookmark for later?

### Pitfalls
- Some blog posts require cookie consent banners — dismiss them before extracting
- Medium posts may have paywall truncation — check if full content loaded
- For technical deep dives, focus on architecture/protocol sections, skip marketing fluff
- Dates matter — check if the content is current (tech moves fast)

Fall back to `browser_navigate` → extract → summarize.

### Fast article extraction

For blog posts with semantic HTML, extract text via JS console — much faster than scrolling snapshots:

```javascript
// Try article tag first (most blogs/docs)
document.querySelector('article')?.innerText?.substring(0, 15000)

// Fallback: main content area
document.querySelector('main')?.innerText?.substring(0, 15000)

// Last resort: full body
document.body.innerText.substring(0, 15000)
```

Increase the 15000 limit for longer technical articles. If JS extraction returns nothing useful, fall back to `browser_snapshot` → read from snapshot.

### "Add to vault" from conversation context

When Jordan says "add to vault" referencing content already in the chat (not a fresh URL):

1. **Reconstruct the source URL** from the conversation context if possible
2. **Fetch the full article** — the message in chat is often truncated
3. **Search the vault** for existing related notes before creating new ones
4. **Create the note** with full structured content (not just the truncated chat message)
5. **Cross-reference** from any related existing notes

### Tweet images/graphics

When X posts include images, charts, or graphics that aren't in the tweet text, use `browser_vision` to read them:

```
browser_vision(question="What does the image/graphic in this tweet show?")
```

This catches visual context that `xurl read` misses — title cards, infographics, charts, screenshots.

## Online Courses & Tutorials

When Jordan shares an online course or tutorial (freeCodeCamp, Coursera, YouTube tutorial, etc.):

### Step 1: Extract the curriculum
Fetch the course description/outline. For YouTube:
- Use oEmbed API for title/author
- `web_extract` the video page for the description (YouTube's HTML includes the full description with chapter markers, links, and tools mentioned)

For dedicated course platforms (freeCodeCamp, Udemy, etc.):
- Use `web_extract` for the landing page
- Focus on the module/curriculum list — that's the substance

### Step 2: Map to our capability level

Don't just summarize the course — compare it against what we've already shipped:

| Course Topic | Our Status | Gap? |
|-------------|------------|------|
| Agent loops, tools | ✅ Already built (Agent Kit, MCP, plugins) | No gap — skip |
| Structured outputs | ✅ Output Enforcer shipped | No gap — course validates direction |
| Guardrails | 🟡 In ideas (brainstormed this session) | Gap — build needed |
| Personality | 🟡 In ideas | Gap — build needed |

### Step 3: Generate build ideas from gaps

Every gap between the course content and our current stack is a potential build opportunity. Present them as:

```
**Idea N: [Name]**
- What: [one-liner]
- Why us: [differentiation vs course baseline]
- Effort: [time estimate]
- Status: [in queue / needs greenlight]
```

### Step 4: Strategic verdict

- **Watch** — confirms our direction, no action needed
- **Fill gap** — course reveals something we should build (add to build queue)
- **Skip** — we're past this content entirely

### Pitfalls
- Don't dismiss a course as "too basic" without checking if it covers something we haven't implemented
- The most valuable signal from a course is often what it emphasizes that we don't have yet, not what it teaches
- FreeCodeCamp courses are for beginners — but the module list reveals what the ecosystem considers "core knowledge"

This pattern was proven Jul 2026: freeCodeCamp AI Agents course → identified 4 gaps (Output Enforcer, Guardrails, Personality, HITL) → 1 shipped in same session.

## 🎯 Opportunity Wiring — Making Links Concrete

**Critical workflow — this comes BEFORE deep analysis, not after.**

After extracting a link's content, the FIRST thing to determine is: where does this go in the vault? Jordan's rule: **don't just discuss — add to the list.** If your analysis doesn't end with vault changes, you're doing it wrong.

### Step 0: Categorize the finding

| Category | Example | Target File(s) |
|----------|---------|---------------|
| **Quick win** | $500 grant, 10-min submission, easy registration | `00-HQ/jordan-queue.md` (under Quick Wins) |
| **Hackathon / time-bounded prize** | OKX Genesis $100K, deadline Jul 17 | `00-HQ/build-queue.md` as item 0 (URGENT) + `jordan-queue.md` active hackathons |
| **Infrastructure / feature** | New adapter, runtime pattern, service template | `00-HQ/build-queue.md` (with status/impact/time/action-items structure, numbered sequentially) |
| **Strategic thesis / product expansion** | New asset class, new market, ecosystem play | `09-Green Room/aae-product-vision.md` or `09-Green Room/ideas.md` (as BIG PLAY or line item) |
| **Decision needed** | Integration choice, architecture fork, partner eval | `11-Mess Hall/considerations.md` (with options + impact + priority) |
| **Ecosystem signal** | Competitor move, partnership, funding round | `09-Green Room/ideas.md` (market context update) |
| **Grant / funding opportunity** | Builder grants, incubator applications | `00-HQ/build-queue.md` as ecosystem item + `jordan-queue.md` quick win |

### Step 1: Check brain FIRST (mandatory, not optional)

Before writing ANY analysis, search vault + session history for related content:

```
session_search(query="topic keywords")
search_files(target="content", pattern="topic", path="$VAULT")
```

**Why this matters:** Jordan frequently shares links that extend topics we've already discussed. If you skip the brain check, you'll:
- Write a summary from scratch when we already have one
- Miss existing entries that need expansion (e.g., GrowStreams existed, but the Vara ecosystem was new)
- Propose action items that are already queued
- Look like you don't remember prior context

**What to do with findings:**
- **Topic exists** → read it, then extend/update rather than rewrite
- **Topic exists in different form** (GrowStreams the app vs Vara the ecosystem) → expand the existing entry with new context
- **Topic confirmed new** → proceed with analysis + vault wiring

### Step 2: Multi-target analysis — one link, multiple vault files

One link can trigger multiple vault entries at different levels. Example from this session:
- **Vara Network tweet** → Grants program (item 13 build-queue) + PolyBaskets architecture (item 14 build-queue) + Vara.eth runtime eval (item 15 build-queue) + GrowStreams context (jordan-queue expansion)

**When a link contains multiple distinct signals, wire each one to its appropriate file.** Don't dump everything into one entry.

### Step 3: Big-idea capture pattern

When a link triggers a strategic insight or "aha" moment from Jordan (e.g., "This is awesome — yield on stocks"), don't just add task items. Create a narrative document section:

1. **Capture the thesis** in Jordan's own framing (he often says the killer line: "all we have to do is adopt their system")
2. **Map to existing work** — connect it to what we're already building
3. **Add structured detail** — strategies, faction updates, phases, risks
4. **Add action items** at the bottom (these can also be cross-referenced in build-queue)
5. **Insert into the right vision document** (usually `aae-product-vision.md` or `ideas.md`)

**Format for big-idea sections:**
```
---
## 🆕 {Title}

*Added: {date} — {trigger source}.*

### Thesis
> *"{Jordan's quote or framing}"*

### What Changed
{Bullet points of what's new/different}

### How It Works
{Table or structured list}

### Why This Is Ours to Own
{Unique positioning vs competition}

### Connection to Build Queue
{Bullet list of build items this touches}

### Recommended Next Steps
- [ ] {step with deadline where applicable}
```

### Step 4: Priority displacement

Time-bounded opportunities (hackathons, grants, competitions with hard deadlines) **take the #0 slot** in the build queue. When one is found:

1. Create item 0 in `build-queue.md` under URGENT with the full breakdown
2. Add to `jordan-queue.md` under Active Hackathons as P0
3. All other items become secondary until submission is live
4. Update the Execution Strategy phase to reflect the displacement

### Step 5: Wire to appropriate files

For each category, add the content using the file's existing structure:

**build-queue.md items** follow this shape:
```
### {#}. {Title}
**Status**: Ready to start / Design pending / Research complete
**Impact**: {one-line value proposition}
**Deadline**: {if time-bounded, with days remaining}
**Estimated Time**: {duration}
**Action Items**:
- [ ] {step 1 with date range}
- [ ] {step 2}
```
Then number sequentially after the last item in the section.
When inserting item 0, renumber existing items.

**jordan-queue.md quick wins** are flat checklist items with brief context. Under Active Hackathons, use P0/P1/P2 labels with deadlines.

**considerations.md** entries get explicit options (choose 1-3) plus why, impact, and priority.

**ideas.md / aae-product-vision.md** additions get enough context to stand alone — the user reads these to understand the thesis, not just the task.

### Step 6: Cross-reference between files

After adding, link related items so the vault is navigable:
- `build-queue.md` → refer to `considerations.md` (e.g., "See also: Condor eval in considerations.md")
- `jordan-queue.md` → refer to `build-queue.md` (e.g., "See build-queue.md item 13")
- `ideas.md` → refer to `aae-product-vision.md` (e.g., "See aae-product-vision.md for full special edition thesis")

### Step 7: Confirm with user

Brief summary of what was added where, so Jordan knows the files changed and can find things later. Keep it to 3-5 bullets with file names and what changed.

### Pitfall: Single-file tunnel vision
The most common mistake is dumping everything into one file. If the finding spans multiple categories (e.g., a grant opportunity that also validates a product strategy), wire it to all relevant files with cross-references. The user will notice if you missed a file.

### Pitfall: Discussing without committing
When Jordan says "check the brain" or "why not add to the list", he's telling you to stop analyzing and start wiring. After the initial summary, the next step is vault updates — not another round of analysis. **If you haven't made a vault change after analyzing a link, you skipped a step.**

### Pitfall: Brain-check after analysis
Don't analyze first, then check the brain. Check the brain FIRST, then analyze with context. This prevents redundant analysis and lets you extend existing work rather than restarting from scratch.

### Pitfall: New platform announcements with no API yet
When a major protocol announces a new product (e.g., Ondo Network / Ondo Perps) but has no GitHub repos, no SDKs, no API docs yet:
- Don't try to integrate — there's nothing to integrate
- Don't dismiss — the announcement validates the thesis (non-custodial perps, RWA-native execution layer)
- **Capture the roadmap** in the vault: Phase 1 (API discovery) → Phase 2 (arb scanner venue) → Phase 3 (execution) → Phase 4 (RWA-native products)
- **Set a watch** — bookmark their docs site, check GitHub org periodically
- **Build readiness** — ensure the GTA architecture is venue-agnostic (MCP adapters) so when the API drops, integration takes hours not weeks
- **Don't over-analyze** — a product announcement without shipped code is a signal, not a spec. 3-4 sentence summary is enough.

---

## Vault Integration

When Jordan says "add to vault", "save this", or shows sustained interest, save a structured research note to the vault.

### Step 1: Find existing related notes

Before creating a new note, search the vault for related content:

```bash
# Search by filename
find "$VAULT" -name "*.md" -iname "*keyword*"

# Search by content
grep -rli "keyword" "$VAULT" --include="*.md"
```

Read any related notes to understand what's already documented and avoid duplication.

### Step 2: Create the research note

Save to the appropriate vault location:

| Topic | Location |
|-------|----------|
| Tech tools / protocols | `03-Projects/{ProjectName}/` (e.g., `03-Projects/AAE/`) |
| Hackathon research | `03-Projects/Hackathons/` |
| DeFi/market data | `00-HQ/Market/` |
| Travel | `00-HQ/Travel/{Country}/` |
| General research | `03-Projects/Research/` (create if needed) |

**Note naming convention:** `kebab-case-descriptive-name.md`

**Required frontmatter in vault notes:**
```markdown
# Title

**Source:** [source description](URL)
**Date:** YYYY-MM-DD
**Author:** author name
**Tags:** #tag1 #tag2

---

## TL;DR
(2-3 sentence summary)

---

## Key Sections
(structured content with tables, headers, bullet points)

---

## GenTech Relevance
(1-2 paragraphs: how this connects to our projects/builds)

## Open Questions
(anything unanswered)

## Sources
(links to original materials)
```

### Step 3: Cross-reference existing notes

If related notes were found in Step 1, update them with cross-references:

```markdown
## Related
→ See [[path/to/new-note]] (date, source description)
### Step 2: If the post links to something (GitHub repo, article), follow that link too
```bash
# METHOD 1: fxtwitter API (PRIMARY — reliable from VPS, no auth needed)
curl -s "https://api.fxtwitter.com/i/status/{TWEET_ID}" | python3 -c "
import json, sys
data = json.load(sys.stdin)
tweet = data.get('tweet', {})
print('Author:', tweet.get('author', {}).get('name'), '@' + tweet.get('author', {}).get('screen_name', ''))
print('Text:', tweet.get('text'))
print('Date:', tweet.get('created_at'))
print('Views:', tweet.get('views'))
print('Likes:', tweet.get('likes'))
print('URLs:', [u.get('url') for u in tweet.get('urls', [])])
"

# METHOD 2: xurl (if auth is configured)
xurl read https://x.com/i/status/{id}

# METHOD 3: Browser (if both fail — rarely needed)
# browser_navigate → browser_snapshot
```

This returns JSON with tweet text, author, engagement metrics, URLs, media, and quoted tweets.

### Pitfall: xurl returns 401
`xurl read` frequently returns `401 Unauthorized` (May 2026). Try fxtwitter next. If fxtwitter also fails, use browser_navigate + browser_snapshot. Accept cookies first (ref `e9` or `e12` typically) and re-snapshot if page doesn't fully load.

### Pitfall: X/Twitter browser and xurl blocked from server IP
`browser_navigate` to x.com times out and `xurl read` returns 401 without auth setup. **But fxtwitter API works reliably from VPS IPs.** Always use fxtwitter as the primary method:
1. **fxtwitter API** — `curl -s "https://api.fxtwitter.com/i/status/{TWEET_ID}"` — works reliably, no auth needed
2. **If fxtwitter fails** — ask Jordan to screenshot or describe the content
3. **Do NOT burn time on browser_navigate to x.com** — it will timeout. Skip it entirely.

### Agent Reach Twitter Cookie Setup
For persistent X/Twitter access, configure Agent Reach with browser cookies:
1. User installs Cookie-Editor extension in Chrome/Edge
2. User logs into x.com
3. User clicks Cookie-Editor, copies `auth_token` and `ct0` cookie values
4. Agent runs: `agent-reach configure twitter-cookies <auth_token> <ct0>`
5. Verify: `agent-reach doctor` should show Twitter as available

**Security:** `auth_token` is sensitive — never paste in group chats. DM or save to local file.

### Fallback Chain (X/Twitter)
1. **fxtwitter API** (primary) — `curl -s "https://api.fxtwitter.com/i/status/{TWEET_ID}"` — works reliably from VPS, no auth
2. **web_search with tweet ID** — `web_search(query="site:x.com {TWEET_ID}")` or `web_search(query="@{author} {keywords}")` — search engines often index tweets and return snippets with the full text
3. **xurl CLI** — only if auth is configured (`xurl auth status` shows valid tokens)
4. **Ask Jordan** to screenshot or paste content — fastest path when API fails
5. **browser_navigate to x.com** — MIGHT work with stealth features (worked Jun 2026), but still unreliable. Try fxtwitter first.

**Pitfall:** `web_search` with tweet IDs works surprisingly well — search engines index public tweets and return snippets containing the full text. This is a reliable fallback when fxtwitter is down or rate-limited. Try `site:x.com {TWEET_ID}` first, then broader searches with author name + keywords.

### Step 2: If the post links to something (GitHub repo, article), follow that link too

### Step 2: Summarize

1. **Product viability probe** — Try to access the actual product, not just the landing page:
   - Test `app.{domain}`, `cloud.{domain}`, `docs.{domain}`, `api.{domain}` — DNS failures = red flag
   - Check if there's a working API or just a "Schedule a Demo" page
   - Note: enterprise-only sales model vs self-serve developer access
   - **NPM/PyPI verification**: If the project claims an SDK or CLI, check package registries: `curl -s "https://registry.npmjs.org/{package}" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('name'), d.get('dist-tags',{}).get('latest'))"` — no result = package doesn't exist yet (vaporware or pre-launch). Also try scoped variants (`@org/name`).
   - **Name collision check**: In crypto, multiple projects often share names (e.g., "Hive" = marketplace, trading swarm, AND social blockchain). Always verify you're evaluating the right one by cross-referencing Twitter handle, website domain, and contract address. Don't assume the project in the tweet is the same as what Google returns for the name.
- **Product naming conflict**: Before committing to a product/project name, search for existing companies with the same or similar name. TradeOff Financial Corp. (fantasy stock trading platform, CEO Mike Rufail) already exists and would be a direct competitor if we used "Trade Off" as our game name. Always check: web search for the name, domain availability, X/Twitter handle availability, and USPTO trademark database. A name collision can force a rebrand after you've already built brand equity. Found May 28, 2026 — forced us to reconsider "Trade Off" as a game name.

2. **GitHub deep check** (beyond repo metadata):
   - Team size (People tab) — small team + enterprise claims = concern
   - Follower count — low followers = low traction
   - Recent commit activity — are they actually building?
   - Issue/PR activity — community engagement?

3. **Vault + session cross-reference** — Before writing the assessment:
   - Search vault for existing notes on the project, team, or competitors
   - Read related notes to understand what's already documented
   - Cross-reference with active hackathon projects and AAE architecture
   - Search session history with `session_search` for dynamic context — recent decisions, ongoing work, team discussions that aren't in the vault yet (e.g., "search for Kite AI", "search for AgentEscrow sprint status")

4. **Strategic verdict** — End with a clear recommendation:
   - **Build on it** — actively integrate into our stack
   - **Watch** — interesting but too early / wrong chain / wrong buyer
   - **Ignore** — not relevant or vaporware
   - Include specific reasons tied to our current stack (Solana, AAE, hackathon deadlines)

5. **Ecosystem compatibility** — When evaluating a project on a different chain/platform:
   - What tooling would we need to rebuild? (language, SDKs, frameworks)
   - What existing integrations carry over vs need replacement?
   - Is the ecosystem mature enough to support our use case?
   - Does it complement or compete with our Solana stack?
   - **Don't dismiss without research** — unfamiliar ≠ irrelevant. Jordan expects proper comparison before ruling out.

### Vault Save Format for Evaluations

Save strategic assessments to `02-Labs/Assessment-{ProjectName}-deep-dive-{date}.md`:

```markdown
# {Project} — Deep Dive Assessment

## What They Are
(1-2 paragraphs)

## The Product
(What actually exists vs what's claimed)

## GitHub Analysis
(team size, repos, activity, red flags)

## Registration & Testing Workflow

When Jordan says "yes why not" or "let's try it" after an assessment:

1. **Find the signup flow** — check the product's website for `/login`, `/signup`, or `Register via API` links. Most agent tooling APIs have email+password signup.
2. **Register via API** (if available) — many have `POST /api/auth/signup` with `{email, password}` that returns `{user, api_key}`. This is faster than browser signup.
3. **Save credentials** to vault: `secrets.env` (for API keys) with `PRODUCTNAME_API_KEY=xxx`. Never echo the key back in chat. Also save a reference note to `03-Projects/Research/{product-name}-credentials.md` with base URL, usage example, and context.
4. **Test 2-3 skills live** — pick the most relevant skills for our stack (Solana, Ethereum DeFi). Use `POST /api/execute` with `skill_id` + `input` params.
5. **Verify real data** — confirm responses contain live on-chain data (block numbers, real prices, actual TVL), not demo/placeholder data.
6. **Report results** — brief summary of what works, what doesn't, and next steps.

### Handling Secrets Shared in Chat

When Jordan pastes an API key, secret token, or credential directly in chat:

1. **NEVER echo the key back** — don't repeat it, don't include it in summaries, don't paste it in code blocks
2. **Save to vault secrets.env** — `echo 'KEY_NAME=value' >> ${VAULT_DIR}/secrets.env`
3. **Confirm save without revealing the value** — "Saved to vault secrets.env. Never stored in conversation."
4. **Add a memory note** that the key exists and where, without including the actual value
5. **If the key needs to be in a .env file for a project**, copy it there too: `grep KEY_NAME ${VAULT_DIR}/secrets.env >> /path/to/project/.env`

### Arsenal API (Sumplus) — Known Pattern
- **Base URL:** `https://arsenal.sumplus.xyz`
- **Signup:** `POST /api/auth/signup` → returns `{user, api_key}` (64-char hex, permanent)
- **Execute:** `POST /api/execute` with `Authorization: Bearer {api_key}`
- **Search:** `GET /api/skills?search={intent}&limit=5`
- **Verified working:** Jupiter Aggregator (Solana quotes), DefiLlama (TVL queries)
- **Known issues:** `get_token_price` on Jupiter fails with "Route not found" for multi-token queries

## Red Flags / Concerns
(numbered list)

## Relevance to GenTech / AAE

### What Overlaps
(bullet points)

### What Doesn't Fit
(bullet points)

### Verdict: **Watch / Build On / Ignore**

(1-2 paragraphs with reasoning)

## Action Items
- [ ] specific next steps
```

### Pitfalls
- Don't confuse marketing copy with shipped product — always probe for working endpoints
- "Launching today" is marketing language, not proof of deployment
- Testimonial from a single company is not social proof
- Cross-chain integration adds complexity — factor this into relevance assessments

## Ecosystem & Competitor Announcement Analysis

When Jordan says "let's investigate" about a protocol pivot, competitor move, or ecosystem announcement (not just a product/tool link), expand the analysis beyond "what it is" to strategic mapping.

### Additional Steps for Ecosystem Analysis

1. **Read the primary source** — blog post, announcement, whitepaper. Use `browser_navigate` → `browser_snapshot` or JS console extraction for full content.
2. **Check their GitHub** — not just metadata, but **shipping signals**:
   - Commit recency ("10 hours ago", "last week") = actively building
   - PR merge activity = code being integrated
   - Branch count = parallel workstreams
   - "Testnet on X, mainnet audited on separate cadence" = maturity stage
3. **Map to our stack** — identify where their move overlaps with our projects, where it competes, and where it validates our thesis.
4. **Identify strategic signals**:
   - **Open standard play** — contributing to Linux Foundation, W3C, etc. = aiming to become infrastructure, not a product
   - **Backed-by-heavyweights** — a16z, WEF, Ethereum Foundation advisors = credibility signal
   - **"We built X before the market was ready"** — timing validation, not failure
   - **Drop-in compatibility** — "works with existing x402 servers" = adoption strategy via incumbent ecosystem

### Output Structure for Ecosystem Analysis

1. **What happened** — the announcement, date, source
2. **Why it matters** — 3-5 bullet points of strategic significance
3. **Validation for us** — how it confirms or challenges our thesis
4. **Overlap mapping** — where their stack intersects ours
5. **What we should do** — star/fork/contribute, differentiate, or ignore
6. **Offer deeper dive** — spec docs, GitHub analysis, or integration mapping

### Pitfalls
- Don't confuse "announced" with "shipped" — check GitHub for commit activity
- An 8-year-old project pivoting to agents validates the timeline, but doesn't mean they've shipped the new thing yet
- "Contributing to Linux Foundation" is aspirational until merged — check if the contribution actually landed
- Price data (CoinMarketCap, TradingView) is noise for strategic analysis — focus on tech and adoption

## Accelerator & Venture Fund Links

When Jordan shares an accelerator, venture fund, or incubator URL (e.g., `alliance.xyz`, `colosseum.com`, `era.xyz`):

### Step 1: Extract core details
- **Funding amount** — what they invest per startup
- **Equity/terms** — what they take in return (if disclosed)
- **Application deadline** — hard deadline or rolling
- **Batch timeline** — when it starts, how long, in-person vs remote
- **Demo Day** — investor showcase details
- **Portfolio** — who they've backed before

### Step 2: Map to our projects
- Which of our projects (AAE, Rugcheck, Aegis) fits their thesis?
- Do they explicitly back AI + crypto? Solana? Social gaming?
- What's the competitive landscape in their portfolio?

### Step 3: Assess fit
- **Solo founder friendly?** — some accelerators require 2+ co-founders
- **Stage match?** — pre-seed, seed, or growth? Are we early enough?
- **Chain/ecosystem alignment?** — Solana-focused vs multi-chain
- **Geographic requirements?** — SF, NYC, remote?
- **Application complexity** — 20-min form vs full pitch deck + essays

### Step 4: Timeline urgency
- Days until deadline vs current workload
- What's needed for application (team info, pitch deck, repo links, essays)
- Can we submit a quality application before the deadline?

### Pitfalls
- **"Apply in under 20 minutes"** is marketing — the real work is deciding what to submit, not filling the form
- Accelerator deadlines are hard cutoffs — no extensions
- Some accelerators (Colosseum) require hackathon wins as entry — check if there's a direct application path
- $500k funding sounds huge but check the terms — equity, pro-rata rights, board seat requirements
- "Demo Day" is the real value — investor access, not just the money

## Output Style

- Use tables for comparisons
- Use emoji sparingly for section headers
- Keep summaries scannable — Jordan should get the gist in 10 seconds
- Always end with a clear "what next" or action suggestion

### ⚡ Arcade Thesis Mapping — Link Analysis Lens

When Jordan shares a link — especially about AI models, game engines, 3D tools, or crypto games — the default analytical frame is: **how does this serve the arcade + x402 vision?**

### The Three Questions

Every link gets evaluated through these lenses in order:

1. **Arcade component** — Does this build the lobby (3D env), the cabinets (games), or the characters (NPCs)?
2. **Payment layer** — Can x402 sit on top? Microtransactions, premium features, tournament entry?
3. **Orchestration** — Can we direct this with agents instead of doing it manually?

### Mapping Categories

| Link Type | Arcade Lens | Examples This Session |
|-----------|-------------|----------------------|
| **AI model releases** (Kimi K3, DeepSeek, Llama) | Can we run it locally? Cost vs capability? Does it support our agent stack (tool use, structured output)? | Kimi K3 (2.8T MoE, 1M ctx, open weights) — 2.5x intelligence per compute unit. Same team as AgentENV. |
| **Agent runtime infrastructure** (AgentENV, E2B, Firecracker) | Sandbox runtime for ClawWork agents? Firecracker microVMs, sub-50ms snapshots, fork for parallel workers. | AgentENV (382⭐, MIT, Rust) — powers Kimi K3's agentic RL training. 4 days old but from kvcache-ai (Moonshot AI infra arm). |
| **Domain-specific agent squads** (EVM Cortex) | Pre-built agent teams for specific domains. Fork + extend with our x402 skills. Deploy ClawWork agents through them for paid work. | EVM Cortex (24⭐, MIT, TS) — 50 agents, 94 skills for Ethereum protocol engineering. Has ERC-8004 skill. Forked at GentechLabs/evm-cortex. |
| **Training infra** (MoonEP) | Only relevant for multi-GPU MoE training (8+ ranks). Overkill for single-GPU QLoRA fine-tune. | MoonEP (323⭐, 3 days old) — Expert Parallelism for MoE training. Part of Kimi K3 stack. |
| **Voice/audio** (HF Speech-to-Speech) | Arcade narrator / Halo announcer. Toggle on/off per cabinet. WebSocket, no WebRTC needed. | HF S2S (6.5K⭐) — VAD→STT→LLM→TTS pipeline. OpenAI Realtime API compatible. |
| **Agent control planes** (Paperclip, Multica) | Which one to build GenTech Shop + build queue on. Paperclip wins for plugin system + Hermes native support. | Paperclip (74.8K⭐) for Shop. Multica for ClawWork squad mgmt. Both running locally. |
| **Crypto games** (Off the Grid, MapleStory Universe) | Partnership target for x402? Marketplace integration? Arcade as mini-game in their ecosystem? | GUNZ marketplace rebuild (July) — x402 pitch window |
| **Agent frameworks** (Google ADK, Microsoft autogen) | Contribution target for x402 auth scheme? Can agents play arcade cabinets? | ADK x402 auth scheme built and PR-ready |
| **3D asset tooling** (text-to-cad, iCity, CityBuilder3d, Blender addons) | **text-to-cad** (10.6k ⭐, MIT): Python build123d → GLB pipeline. Generate arcade lobby elements from text descriptions. | text-to-cad → arcade cabinet (4KB GLB), arcade stairs with neon railing (17KB GLB) |
| **AI companion/character** (Airi, Neuro-sama clones) | NPC host for the lobby? Cabinet characters that react to gameplay? VRM/Live2D avatars we can deploy? | Airi (43k ⭐) — lobby greeter, cabinet taunt characters |

### Output Style for Arcade Links

Skip the "what is X" explanation. Lead with the verdict:

```
**{Project Name}** — {stars/license/stack}

**Arcade potential:** {one-line thesis}
**x402 angle:** {one-line}
**Orchestrator-friendly:** {yes/no — see orchestrator-friendly filter}

**Verdict:** {Build on it / Watch / Ignore}
```

### Pitfall: Don't explain the obvious

When Jordan shares a link about a **hot topic** (Kimi K3, Claude, GPT, crypto game with 100K+ players), the threshold for "obvious" is high. He's not asking what it is — he's asking what WE can do with it. Skip the architecture explainer, go straight to the thesis mapping.
