# TinyFish API Reference

## Base URLs
- **Search:** `https://api.search.tinyfish.ai`
- **Fetch:** `https://api.fetch.tinyfish.ai`
- **Agent:** `https://agent.tinyfish.ai` (metered — multi-step browser automation)
- **Browser:** managed cloud browser (metered)
- **MCP:** `https://mcp.tinyfish.ai`

## Authentication
Header: `X-API-Key: $TINYFISH_API_KEY`
Key stored in: vault `secrets.env`

## Search Endpoint
```bash
curl -s "https://api.search.tinyfish.ai?query=YOUR+QUERY" \
  -H "X-API-Key: $TINYFISH_API_KEY"
```
Response: JSON with `results[]` array. Each result has `title`, `url`, `snippet`.

## Fetch Endpoint
```bash
curl -s -X POST https://api.fetch.tinyfish.ai \
  -H "X-API-Key: $TINYFISH_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://example.com"]}'
```
Response: JSON with `results[]` array. Each result has `url`, `final_url`, `title`, `description`, `language`, `text`.

## Agent Endpoint (Streaming)
```bash
curl -N -X POST https://agent.tinyfish.ai/v1/automation/run-sse \
  -H "X-API-Key: $TINYFISH_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://target.com", "goal": "Extract all product prices as JSON"}'
```
Returns SSE stream with events. Goal is natural language.

## Python SDK
```bash
pip install tinyfish
```

## CLI
```bash
npm install -g @tiny-fish/cli
tinyfish auth login
tinyfish search query "web automation tools"
tinyfish fetch content get https://example.com
```

## Key Features
- **Free tier:** Search + Fetch are free with generous rate limits
- **Full browser rendering** on Fetch (not just HTTP GET)
- **Token-efficient:** Strips nav, scripts, cookie banners from fetched pages
- **Rank-stable:** Search results don't shuffle between calls
- **Stealth:** Built-in rotating proxies and stealth profiles

## When to Use
- **Search:** Replace DuckDuckGo scraping, web_search for structured queries
- **Fetch:** Replace web_extract, browser_vision for reading specific pages
- **Agent:** Complex multi-step flows (form filling, multi-page navigation)
- **Browser:** Custom Playwright/Selenium scripts needing a managed browser

## Limitations
- Fetch may miss content from heavy JS SPAs (fall back to browser_navigate)
- Agent endpoint is metered — use Search + Fetch for simple tasks
- No auth-gated content (needs logged-in sessions) unless using Agent with Vault
