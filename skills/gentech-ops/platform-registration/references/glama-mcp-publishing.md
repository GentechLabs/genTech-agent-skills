# Glama MCP Server Publishing Checklist

Glama (`glama.ai`) is an MCP server directory and quality scoring platform. Servers listed on Glama get discovered by AI agents using MCP-compatible clients.

## The Score Check (What Glama Measures)

| Status | Item | Impact |
|--------|------|--------|
| 🔴 | **No LICENSE** | Servers without a LICENSE cannot be installed — score locked below 20% |
| 🔴 | **No Glama release** | Must create a release in Glama dashboard — unlocks Coherence + Tool scoring |
| 🔴 | **No glama.json** | Missing config file |
| 🔴 | **No recent usage** | No one has used it — solves itself over time |
| 🟢 | **Has README** | ✅ Easy win |
| 🟢 | **Author verified** | ✅ Connect GitHub to Glama |
| 🟢 | **Has maintenance** | ✅ Keep repo active with recent commits |
| ⚪ | Server Coherence | Unknown until release created |
| ⚪ | Tool Definition Quality | Unknown until release created |

## The Fix Checklist (In Order)

### 1. Add LICENSE to repo root
```bash
curl -s https://raw.githubusercontent.com/github/choosealicense.com/gh-pages/_licenses/mit.txt | \
  sed 's/\[year\]/2026/;s/\[fullname\]/ProtoJay4789/' > LICENSE
git add LICENSE && git commit -m "Add MIT license" && git push
```

### 2. Create glama.json in repo root
```json
{
  "name": "your-server",
  "description": "One-line what it does.",
  "author": { "name": "ProtoJay4789", "url": "https://github.com/ProtoJay4789" },
  "repository": "ProtoJay4789/your-server",
  "categories": ["Category1", "Category2"],
  "related": ["ProtoJay4789/related-server"]
}
```

### 3. Add Glama badges to README
Badge URLs: `https://glama.ai/mcp/servers/{owner}/{repo}/badges/score.svg`

```markdown
[![Glama Score](https://glama.ai/mcp/servers/ProtoJay4789/your-server/badges/score.svg)](https://glama.ai/mcp/servers/ProtoJay4789/your-server)
```

### 4. Create Glama release (dashboard only — no API)
Go to `glama.ai/mcp/servers/{owner}/{repo}` → **Admin tab** → **"Create Release"**.
This is manual. Unlocks Server Coherence + Tool Definition Quality scoring.

### 5. Verify
```bash
curl -s -o /dev/null -w "%{http_code}" https://glama.ai/mcp/servers/ProtoJay4789/your-server/badges/score.svg
curl -s https://glama.ai/api/mcp/v1/servers/ProtoJay4789/your-server | python3 -m json.tool
```

## Pitfalls
- **LICENSE exists locally but not on GitHub** — Commit and push. Glama checks GitHub, not your local copy.
- **Badge returns 404** — Glama hasn't indexed yet. Can take 24h for new repos, or needs release created.
- **Score stuck at 17%** — No LICENSE + No Release + No glama.json. Fix all three.
- **spdxLicense: null in API** — API cache lag. Badge resolves if score is non-zero.
- **No Glama release = no installation** — Users cannot install your server through Glama without it.
- **🔴 mcp v2 removed `mcp.server.fastmcp` — fresh builds fail at import.** The `mcp` package at **v2.0.0** split FastMCP into a standalone `fastmcp` package. Any server importing `from mcp.server.fastmcp import FastMCP` passes local tests (old cached env) but fails Glama's CI, which installs `requirements.txt` fresh (resolving `mcp>=1.0.0` → 2.0.0) then imports the server → `ModuleNotFoundError: No module named 'mcp.server.fastmcp'`. **Fix:** `from fastmcp import FastMCP` + pin `fastmcp>=2.0.0` in requirements/pyproject. **Proven Aug 4, 2026:** Glama emailed "build failed" for genTech-shop; root cause was exactly this. Also caught the same latent bug in genTech-agent-kit before it hit the wall.
- **🔴 Verify a fresh build BEFORE relying on Glama's CI.** Glama's build installs deps from scratch and imports the server — it does NOT reuse your local venv. Reproduce it locally before pushing: create a fresh venv, `pip install -r requirements.txt`, then `python -c "import server"` and confirm all tools register (`await mcp.list_tools()`). A server that "works locally" can still fail Glama's clean build.
- **🔴 After fixing one repo, grep ALL repos for the same latent bug.** A dependency-version breakage (like the mcp v2 FastMCP split) is systemic — every repo with the same import will fail the same way. `grep -r "mcp.server.fastmcp" /root/repos/` and fix every hit, not just the one that emailed you.

## Real Example: genTech-shop
Went from 17% to live after: LICENSE pushed, glama.json added, badges added, release created. Date: 2026-07-25.
