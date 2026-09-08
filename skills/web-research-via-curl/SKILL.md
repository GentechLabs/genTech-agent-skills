---
name: web-research-via-curl
version: 1.0
author: Gentech AI
class: research
description: Web research using curl-based extraction. Agent Reach is the default web tool (62K ⭐, MIT, zero API fees). Firecrawl is dead (Nous Portal credits exhausted). Covers Jina Reader, GitHub API, fxtwitter, Agent Reach CLI, and platform-specific API patterns.
---

# Web Research via Curl

## Overview
Research methodology using curl-based extraction. **Agent Reach is the default web tool** (62K ⭐, MIT, zero API fees). Firecrawl is dead (Nous Portal credits exhausted). Uses Agent Reach CLI, Jina Reader, GitHub API, fxtwitter, and platform-specific API patterns.

## Tool Hierarchy (Default → Fallback)
0. **Tavily** — the CONFIGURED search backend (`backend: tavily` in config.yaml). The `web_search` tool routes here automatically. Verify it's live before ever declaring "search is down": `curl -s -X POST "https://api.tavily.com/search" -H "Content-Type: application/json" -d '{"api_key":"<TAVILY_API_KEY>","query":"test","max_results":1}'` (key in `.env` as `TAVILY_API_KEY`).
1. **Agent Reach** (`agent-reach doctor` first to check availability) — primary for all platforms
2. **Jina Reader** (`curl -s "https://r.jina.ai/URL"`) — any non-GitHub webpage → clean markdown
3. **GitHub API** (`curl -s "https://api.github.com/repos/owner/name"`) — structured JSON
4. **fxtwitter/vxtwitter** — X/Twitter post data
5. **Direct curl** — raw HTML fallback

## Core Principle
Before browser work, ask: "Can I curl this?" Most services have reader-friendly endpoints that return cleaner data than rendered HTML.

## Tools

### 1. Jina Reader (any web page → markdown, no API key)
```bash
curl -s "https://r.jina.ai/URL"
```
Use as FIRST ATTEMPT for any URL. Returns Title + clean Markdown. Blocked on GitHub — use API instead.

### 2. GitHub API (structured JSON)
```bash
# Repo details
curl -s "https://api.github.com/repos/owner/name"

# README (decode base64)
curl -s "https://api.github.com/repos/owner/name/readme" | python3 -c "import json,sys,base64; print(base64.b64decode(json.load(sys.stdin)['content']).decode())"

# Search repos by keyword, sorted by stars
curl -s "https://api.github.com/search/repositories?q=$QUERY&sort=stars&per_page=5"

# User starred repos (paginated 100/page)
curl -s "https://api.github.com/users/$USER/starred?per_page=100&page=1"
```

### 3. fxtwitter API (X/Twitter post data)
```bash
curl -s "https://api.fxtwitter.com/i/status/$TWEET_ID" | python3 -c "import json,sys; d=json.load(sys.stdin); t=d['tweet']; print(t['text'])"
```
Tweet ID = numeric portion after /status/ in the URL.

### 4. Agent Reach (62K ⭐, MIT, v1.4.0 installed)

**Default web tool.** Replaces Firecrawl entirely. Zero API fees.

**Diagnostic first:**
```bash
agent-reach doctor
```
Shows which channels are available (✅) vs need setup (❌).

**Channels available immediately (zero config):**
- Web scraping (Jina Reader) — `curl https://r.jina.ai/URL`
- Semantic search (Exa) — free, no API key
- YouTube — subtitles + search (yt-dlp, JS runtime configured)
- GitHub — full access (gh CLI authenticated)
- V2EX, RSS, WeChat articles

**Channels needing cookie setup (user action):**
- Reddit — `rdt login` or Cookie-Editor export
- Twitter/X — Cookie-Editor export
- XiaoHongShu, LinkedIn, Instagram — Cookie-Editor export

**Jina Reader is the primary page-to-markdown tool:**
```bash
curl -s "https://r.jina.ai/URL"  # Returns clean markdown
```
GitHub blocks anonymous Jina access — use GitHub API instead.

### 5. Direct curl
```bash
curl -sL "URL"                          # basic fetch
curl -sL -A "Mozilla/5.0" "URL"         # with user-agent
curl -sI "URL"                          # headers only
```

## Quick Reference

| Target | Command |
|--------|---------|
| GitHub repo | `curl -s api.github.com/repos/owner/name` |
| GitHub README | `curl -s api.github.com/repos/owner/name/readme` → base64 |
| GitHub search | `curl -s api.github.com/search/repositories?q=...` |
| X/Twitter post | `curl -s api.fxtwitter.com/i/status/ID` or `curl -s api.vxtwitter.com/user/status/ID` |
| X/Twitter with media | `curl -s api.vxtwitter.com/user/status/ID` (returns mediaURLs array) |
| Instagram post | Use `curl -s -H 'User-Agent: Mozilla/5.0' URL` → grep for `og:video:secure_url` or `og:image` meta tags |
| YouTube video | `yt-dlp --get-url -f best URL` |
| Any webpage | `curl -s r.jina.ai/URL` |
| Raw HTML | `curl -sL URL` |

## Social Media Study Workflow

When Vanito (or any collaborator) sends a social media link to study ("figure out how they made this"):

### Step 1: Extract metadata and media URL
```bash
# X/Twitter — vxtwitter returns structured JSON with mediaURLs array
curl -s "https://api.vxtwitter.com/USERNAME/status/TWEET_ID" | python3 -c "
import json, sys
d = json.load(sys.stdin)
print('Text:', d['text'])
print('Video:', d['mediaURLs'][0] if d['mediaURLs'] else 'No video')
print('Duration:', d['media_extended'][0].get('duration_millis', 'N/A'), 'ms')
print('Size:', d['media_extended'][0].get('size', 'N/A'))
"

# Instagram — grep og:video meta tags from page source
curl -s -H 'User-Agent: Mozilla/5.0' "https://www.instagram.com/p/SHORTCODE/" | \
  grep -oP 'https://scontent[^"]+\.mp4[^"]*' | head -1

# Instagram description
curl -s -H 'User-Agent: Mozilla/5.0' "https://www.instagram.com/p/SHORTCODE/" | \
  grep -oP '(?<=og:description" content=")[^"]+'
```

### Step 2: Download the video
```bash
curl -L -o /tmp/study-clip.mp4 "VIDEO_URL"
```

### Step 3: Analyze technical specs
```bash
ffprobe -v quiet -print_format json -show_format -show_streams /tmp/study-clip.mp4 | python3 -c "
import json, sys
d = json.load(sys.stdin)
for s in d['streams']:
    print(f\"{s['codec_type']}: {s.get('codec_name','?')} {s.get('width','?')}x{s.get('height','?')} {s.get('r_frame_rate','?')}fps\")
print(f\"Duration: {d['format']['duration']}s\")
"
```

### Step 4: Extract frames for vision analysis
```bash
mkdir -p /tmp/study-frames
ffmpeg -i /tmp/study-clip.mp4 -vf "fps=1,scale=320:-1" /tmp/study-frames/frame-%03d.jpg -y
```

### Step 5: Analyze key frames with vision_analyze
- Start (frame-001), midpoint (frame-MID), and final (frame-LAST)
- Describe: art style, camera angle, composition, technique, prompt structure
- Compare frames to understand motion flow and timing

### Step 6: Save findings to skills
- Create or update a skill under `film-production/` category
- Include: aspect ratio, clip length, art style, prompt structure, camera work
- Reference the video URL for future viewing

## Platform-Specific Patterns

### X/Twitter — Use vxtwitter (NOT fxtwitter) for media
vxtwitter returns richer data than fxtwitter:
- `mediaURLs[]` — direct video/mp4 URLs
- `media_extended[].duration_millis` — exact length
- `media_extended[].size` — resolution
- `text` — full tweet text with line breaks

### Instagram — Use curl with mobile User-Agent
Instagram blocks most scraping but the Open Graph meta tags are readable:

| Field | Command |
|-------|---------|
| Account | `grep -oP 'instagram\.com/[^/]+'` from redirected URL |
| Description | `grep -oP '(?<=og:description" content=")[^"]+'` |
| Video URL | `grep -oP 'https://scontent[^"]+\.mp4[^"]*' | head -1` then `sed 's/&amp;/\&/g'` |
| Date | `grep -oP '2026-\d+-\d+'` from timestamps |
| Likes | `grep -oP '\d+(?= likes)'` |

All require `-H 'User-Agent: Mozilla/5.0'` header.

### YouTube — Use yt-dlp (if installed)
```bash
yt-dlp --get-url -f best "URL"  # Get direct video URL
yt-dlp --get-description "URL"   # Get description
yt-dlp --write-info-json --skip-download "URL"  # Full metadata
```

## Pitfalls
- **Verify the CONFIGURED backend before declaring a tool down** — when a search/extract tool appears broken, check config.yaml (`backend:` / `search_backend:` / `extract_backend:`) to see what it actually routes to, then probe THAT endpoint directly. A "Nous search is down" assumption is wrong when the config points at Tavily and Tavily is live. Never broadcast a tool-down handoff to other agents until you've confirmed the real backend is unreachable — a false alarm makes agents distrust the channel.
- **Stale GITHUB_TOKEN env var overrides gh CLI auth** — If `gh auth status` shows "Logged in" but Agent Reach reports "not authenticated," check if `$GITHUB_TOKEN` is set to an expired/invalid token. The env var takes precedence over stored credentials. Fix: `unset GITHUB_TOKEN` then `gh auth switch --user <account>` to activate the valid stored token. The env var may be set in `.env` or the shell profile.
- GitHub: 60 req/hr unauthenticated, 5K/hr with `gh auth login`
- Jina blocks GitHub (abuse) — use API
- Jina rate-limits anonymous access. Wait 2 min on 403
- Search engines (Google/Bing/DDG) block this server IP — direct URL only
- fxtwitter occasionally returns empty — retry after delay
- **Instagram requires mobile User-Agent header** — default curl UA may get blocked
- **Instagram video URLs expire** — download immediately after extracting
- **X/Twitter blob URLs** are protected — never extract from blob:, always use vxtwitter API
