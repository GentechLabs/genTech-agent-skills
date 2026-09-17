# Agent Tooling & Skill Marketplace Evaluation

Methodology for evaluating AI agent tools, skill registries, and DeFi execution APIs.

## Research Sequence

### 1. Discovery (DuckDuckGo lite)
```bash
curl -sL "https://lite.duckduckgo.com/lite/?q={product}+skills+marketplace+AI+agents" \
  -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" 2>/dev/null | \
  python3 -c "
import sys, re
html = sys.stdin.read()
links = re.findall(r'class=.result-link.>(.*?)</a>', html)
snippets = re.findall(r'class=.result-snippet.>(.*?)</td>', html, re.DOTALL)
for i, (link, snip) in enumerate(zip(links, snippets)):
    clean = re.sub(r'<[^>]+>', '', snip).strip()
    print(f'{i+1}. {link}')
    print(f'   {clean}')
    print()
"
```

### 2. ClawHub Check
Navigate to `https://clawhub.ai/skills?search={name}` — look for:
- Security scan results (VirusTotal, ClawScan, Static analysis)
- Download/install counts (adoption signal)
- `[ARSENAL-HOSTED ✓]` tags = they run the RPC/API infra
- `[DEMO MODE]` tags = returns example data, not live

### 3. API Probe
Hit the product's API directly to verify it works:
```bash
# Common patterns for agent tooling APIs
curl -sL "https://{domain}/api/skills?limit=5" -H "Accept: application/json"
curl -sL "https://{domain}/api/v1/health"
curl -sL "https://{domain}/api/skills?search={intent}&limit=5"
```
If the API returns structured JSON with skill definitions, schemas, and execution endpoints — it's real. If it returns HTML or a "Schedule a Demo" page — it's vaporware or enterprise-gated.

### 4. Docs Check
Most agent tooling products have docs at `docs.{domain}` or `{domain}/docs`. GitBook-hosted docs are common. Check for:
- Authentication model (API key, OAuth, etc.)
- Pricing/free tier
- Chain/network support
- Integration examples

## Red Flags
- Main site DNS failure (NOT_FOUND, ERR_NAME_NOT_RESOLVED)
- Zero downloads / very low view counts on ClawHub
- Skills marked `[DEMO MODE]` — not production-ready
- ClawScan "Review recommended" flag
- No documentation for API key registration
- Product is a side project of a different main business

## Positive Signals
- `[ARSENAL-HOSTED ✓]` — they run the infrastructure, no user keys needed
- Working REST API with structured JSON responses
- Schema definitions for inputs/outputs
- Active X/Twitter presence with regular updates
- Partnerships with known protocols
- MIT or permissive license

## Vault Save Location
`03-Projects/Research/{product-name}-assessment-{date}.md`

Use the deep-dive assessment format from the main skill's "Vault Save Format for Evaluations" section.
