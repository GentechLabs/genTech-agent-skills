# Agent Reach Setup Notes (Jul 2026)

Installed at `/usr/local/lib/hermes-agent/venv/bin/agent-reach` v1.4.0.
Starred by Jordan at github.com/Panniantong/Agent-Reach (62k ⭐).

## Working Channels (no setup needed)
- **Any webpage** → `curl https://r.jina.ai/URL` (Jina Reader)
- **GitHub** → `curl api.github.com` (authed via `gh` — see auth fix below)
- **YouTube** → yt-dlp with JS runtime configured (see fix below)
- **RSS/Atom feeds** → read via curl
- **V2EX** → public API
- **Bilibili** → yt-dlp + API
- **Semantic search** → Exa (free, auto-configured)

## GitHub Auth Fix (Jul 29, 2026)
The `GITHUB_TOKEN` env var was stale/expired and overriding the valid stored gh CLI credentials.
- **Symptom:** `gh auth status` showed "Logged in" but Agent Reach reported "not authenticated"
- **Root cause:** `$GITHUB_TOKEN` env var takes precedence over stored credentials in `~/.config/gh/hosts.yml`
- **Fix:** `unset GITHUB_TOKEN` then `gh auth switch --user ProtoJay4789`
- **Verification:** `gh auth status` shows "Active account: true" with valid token scopes

## YouTube Fix (Jul 29, 2026)
yt-dlp needs a JS runtime for some operations:
```bash
mkdir -p ~/.config/yt-dlp
echo '--js-runtimes node' >> ~/.config/yt-dlp/config
```
Verify: `agent-reach doctor | grep youtube` should show ✅

## Needs One-Time Setup (user action)
- **Reddit** → `rdt login` (browser-based auth) or Cookie-Editor export
- **Twitter/X** → Cookie-Editor export from browser

## Not Configured
- LinkedIn, Xiaohongshu, Weibo, 小宇宙

## Why Not Firecrawl
Firecrawl exhausted Nous Portal credits. Agent Reach + Jina Reader + GitHub API + fxtwitter cover all research needs with zero API fees. BlockRun search tools (blockrun_search, blockrun_exa, blockrun_surf) are pay-per-call alternatives when Agent Reach doesn't cover the use case.
