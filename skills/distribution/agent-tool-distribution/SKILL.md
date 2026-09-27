---
name: agent-tool-distribution
description: "How to distribute GenTech APIs and tools — skip PyPI, use GitHub direct install, MCP servers, SKILL.md manifests, and the plugin routing system."
---

# Agent Tool Distribution

## Canonical Kit Repo (Critical — Two Local Clones Exist)

**CANONICAL: `/root/repos/genTech-agent-kit`** — branch `main`, matches GitHub
`GentechLabs/genTech-agent-kit`. THIS is where all kit work happens and pushes
from. Has the versioned package structure (`src/gentech_agent_kit/`,
`pyproject.toml`, `uv.lock`, `skills/`, `poker/`).

**STALE: `/root/genTech-agent-kit`** — branch `master`, old v1 layout with
`erc-8004/`, `plugins/pika-mcp`, `docs/`. Do NOT push here. It carries some
untracked ERC-8004 registration files (register.py, upload-to-ipfs.sh,
agent-metadata*.json) that were folded into the canonical repo under
`a2a/identity/` (Aug 1, 2026). If you need those files, read them from
`a2a/identity/` in the canonical repo.

**Pitfall discovered Aug 1, 2026:** the v0.4.0 commit message claimed
"self-evolution, Q402, wakeup-protocol, Obliteratus" shipped — but the commit
only touched README.md and SKILL.md. Zero actual files. Always verify what a
commit actually contains (`git show --stat <sha>`) before trusting the message,
and never assume a feature is shipped because the README says so.

**Kit versioning reality:** v0.4.0 describes itself as "full stack" but the
packaged skills are only x402-payments, output-enforcer, robinhood-chain +
poker daemon. The a2a module (discover → talk → self-audit) was added Aug 1,
2026 — see `a2a/README.md`.

## a2a Module — Agent-to-Agent Communication (Added Aug 1, 2026)

The kit now ships the full A2A lifecycle under `a2a/`:

| Component | Path | What It Is |
|-----------|------|-----------|
| **discovery/** | `a2a/discovery/discovery.py` | ERC-8004 registry monitor (8004scan API, no key) with built-in triage — drops testnet/spam/smoke, scores x402+desc+Base+reputation |
| **workspace/** | `a2a/workspace/buzz_seed.py` | Generic Buzz bridge seeder — any Hermes profile, idempotent, stdlib-only |
| **self-audit/** | `a2a/self-audit/` | Self-Evolution Harness pattern — 4 roles (Evolution/Critic/Verifier/Gardener) + agent constitution |
| **identity/** | `a2a/identity/register.py` | ERC-8004 on-chain registration (7 chains) + Pinata IPFS upload |

**When packaging anything new into the kit:**
1. Verify against GitHub first (`gh api repos/GentechLabs/genTech-agent-kit/git/trees/main?recursive=1`) — don't trust local clones
2. Work in `/root/repos/genTech-agent-kit`, NOT `/root/genTech-agent-kit`
3. Secret scan before push: no `/root/` absolute paths, no API keys, no private keys, no personal emails (except the public jordanjones0902@gmail.com which is already in kit docs)
4. Run syntax checks (`python3 -m py_compile`, `bash -n`) + a live E2E test of any script that hits an API
5. Push, then verify the GitHub tree contains the new files

## Skill Distribution Hygiene & Portability (Layer 7 Gate)

Before packaging, publishing, or distributing skills to any external target (npx skills, ClawHub, EduHub, or repository export):

1. **Path variable convention** — Never use hardcoded machine paths (`/root/...`). Always use portable environment variable placeholders:
   - `${VAULT_DIR}` for vault paths (default `/root/vaults/gentech`)
   - `${PROFILES_DIR}` and `${PROFILE_DIR}` for Hermes agent profile directories
   - `${SCRIPTS_DIR}` for helper scripts
   - `${INSTALL_DIR}` for runtime/library paths
   - *Rule: Skills carry METHOD; the host environment keeps the KEYS and PATHS.*

2. **Zero embedded credentials** — Never write file paths to keys (`/root/.github-token`, `/root/.env`, etc.) inside skills. Reference standard environment variable names (`GITHUB_TOKEN`, `API_KEY`) instead of filesystem locations.

3. **Org identity enforcement** — All distributed and repo references must use the current organization (`GentechLabs`), never legacy personal namespaces or usernames.

4. **Safety backup before bulk edits** — When performing automated or regex-based refactoring across a skill library, always take an archive backup (`tar -czf ...`) and verify archive integrity first.

5. **Portability audit gate** — Run the automated portability checker (`scripts/skill-portability-check.py` or equivalent) across the tree before release. See full specification in `references/portable-paths.md`.

## Core Principle — Skip PyPI

PyPI requires 2FA with multi-code verification that is unreliable. Jordan was locked out after 5+ code attempts. Do NOT use PyPI as a distribution channel.

## Primary Distribution Path — GitHub Direct Install

```bash
# Install directly from GitHub (uv)
uvx --from git+https://github.com/GentechLabs/gentech-agent-kit.git gentech-kit

# Or install as a tool
uv tool install git+https://github.com/GentechLabs/gentech-agent-kit.git
```

This works everywhere, no registration, no 2FA, no gatekeepers.

## MCP Server Distribution (Agent-Native)

Package each API as an MCP (Model Context Protocol) server. Agents add one line to their config:

```json
{
  "mcpServers": {
    "gentech-kit": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/GentechLabs/gentech-agent-kit.git", "gentech-kit"],
      "env": { "CMC_API_KEY": "your-key-here" }
    }
  }
}
```

## SKILL.md Format (PortalHQ Discovery)

For PortalHQ / Monad Agent Hub listing, publish a SKILL.md in the repo root:

```yaml
---
name: gentech-agent-kit
description: "One install. Full stack. Your agent, running. Market data, DeFi intelligence, payment rails."
---
```

The JSON Feed format for PortalHQ:
```json
{
  "id": "gentech-agent-kit",
  "title": "GenTech Agent Kit",
  "content_text": "MCP server with CoinMarketCap data...",
  "_monad": {
    "skill_url": "https://raw.githubusercontent.com/GentechLabs/gentech-agent-kit/main/SKILL.md",
    "category": "defi",
    "tags": ["market-data", "x402", "defi"],
    "chains": ["eip155:8453"],
    "wallet_pattern": "none",
    "status": "active",
    "host": "GenTech Labs",
    "logo_url": "https://..."
  }
}
```

## Plugin Routing System (Auto-Discovery)

The Agent Kit has a plugin system that auto-discovers new tools. The plugin system is structured as a package directory (`plugins/__init__.py`), not a flat module, to support submodule imports.

### Architecture

```
src/gentech_agent_kit/
  plugins/                    # Package directory (was plugins.py)
    __init__.py                # Plugin discovery + registration logic
    algorand_x402/             # Example plugin
      __init__.py              # Exports register_gentech_plugin(mcp)
      plugin.json              # Manifest file
```

### How to Build a New Plugin

1. **Create a plugin directory** (`src/gentech_agent_kit/plugins/<name>/`)

2. **Create a plugin manifest** (`plugin.json`):
   ```json
   {
     "name": "DeFi Intelligence",
     "version": "0.1.0",
     "module": "gentech_agent_kit.plugins.defi_intel",
     "description": "LP health, pool rebalance, yield rankings"
   }
   ```
   The `module` field must be the full Python import path (`gentech_agent_kit.plugins.<name>`).

3. **Implement `register_gentech_plugin(mcp: Any)`** in `__init__.py`:
   ```python
   def register_gentech_plugin(mcp: Any) -> None:
       @mcp.tool()
       def my_tool() -> str:
           return "result"
   ```
   The function receives the FastMCP server instance and registers tools via `@mcp.tool()`.

4. **Also set `__plugin_manifest__`** at module level for package-based discovery:
   ```python
   __plugin_manifest__ = {
       "name": "DeFi Intelligence",
       "version": "0.1.0",
   }
   ```

5. The Agent Kit loads it automatically at startup via two discovery paths:
   - **File-based**: Scans `plugins/*/plugin.json` manifests
   - **Package-based**: Scans installed `gentech_*` packages for `__plugin_manifest__`

6. `kit_info()` tool shows all active plugins.

### Example: Algorand x402 Gateway Plugin

**plugin.json:**
```json
{
  "name": "Algorand x402 Gateway",
  "version": "0.1.0",
  "module": "gentech_agent_kit.plugins.algorand_x402",
  "description": "x402-priced data endpoints on Algorand via GoPlausible facilitator"
}
```

**__init__.py** registers 3 tools: `algorand_x402_info`, `algorand_verify_payment`, `algorand_get_quote`. Integrates with GoPlausible facilitator for payment verification + settlement (Algorand Global x402 Challenge).

### Plugin System Gotchas

- `plugins.py` must be a package (`plugins/__init__.py`), not a flat module — submodule imports break otherwise
- `_PLUGIN_DIR` resolves relative to `plugins/__init__.py`: use `os.path.dirname(os.path.dirname(__file__))` to reach the parent, then `plugins/` from there
- Plugins are discovered twice (file scan + package scan) — harmless but logs "Tool already exists" warnings
- Use `Any` type annotation for the `mcp` parameter to avoid FastMCP stub issues in linters

## Skills Ecosystem Distribution (npx skills)

A zero-friction distribution channel. The `npx skills` CLI (by Vercel Labs, 25k+ stars) lets any user install skill files into their AI coding agent (OpenCode, Claude Code, Codex, Cursor, 72+ agents).

### How It Works

1. Create a `skills/<name>/SKILL.md` in the repo (YAML frontmatter + markdown)
2. Users install via:
   ```bash
   # Install all skills from the repo
   npx skills add GentechLabs/genTech-agent-kit

   # Install a specific skill
   npx skills add GentechLabs/genTech-agent-kit --skill x402-payments
   ```
3. Skills auto-discover when users run `npx skills find agent`

### Directory Structure

```
repo-root/
├── SKILL.md                    # Root skill (installed by default)
├── skills/
│   ├── x402-payments/SKILL.md  # Individual installable skills
│   ├── output-enforcer/SKILL.md
│   └── robinhood-chain/SKILL.md
```

### Skills We Ship

| Skill | Install | Content |
|-------|---------|---------|
| Main (root SKILL.md) | `npx skills add <repo>` | Kit overview, tools, cost optimization |
| x402-payments | `+ --skill x402-payments` | Payment flow, facilitators, multi-chain |
| output-enforcer | `+ --skill output-enforcer` | Schema validation, circuit breaker |
| robinhood-chain | `+ --skill robinhood-chain` | Tokenized stocks, USDG via Naven |

### Format Rules

- YAML frontmatter must have `name` and `description` (quoted as strings)
- Description becomes the skill's tagline in search results
- Each skill dir can contain references/, templates/, scripts/ (loaded on demand)
- No secrets in SKILL.md — it's a public manifest

### Why Skills Over Other Channels

- Zero friction: `npx skills add <repo>` works on any GitHub repo
- No registration, no 2FA, no API key
- Reaches 72+ agent types automatically
- Skills are markdown — readable before installing
- Updates from GitHub — `npx skills update` pulls latest

### Pitfalls

- Root SKILL.md installs by default when no --skill flag used — make it a useful overview
- Skills are markdown only, no code execution. Use for teaching agents how to use tools
- Don't duplicate the README — skills teach how to use the tools, not just list them
- Every skill needs to be self-contained — agents read one skill at a time

## Skill Registry Distribution (EduHub / ClawHub)

Publish Agent-Skills-format skills to registries that DeepTutor, Claude Code, and Codex search. Both **EduHub** (30K+ DeepTutor users) and **ClawHub** (general-purpose skill registry) use the same SKILL.md format.

```bash
# ClawHub
clawhub skill publish ./my-skill --slug my-skill --name "My Skill" --owner <handle>

# EduHub (via DeepTutor CLI)
deeptutor skill publish ./my-skill --track skills-interests --hub eduhub --yes
```

**Full reference:** `references/registry-publishing-deeptutor-clawhub.md`

### Published Skills (Jul 26)

| Skill | Registry | Status |
|-------|----------|--------|
| genTech-agent-kit (root) | EduHub | 🟡 Prepped, blocked on OAuth |
| x402-payments | EduHub | 🟡 Prepped, blocked on OAuth |
| x402-payments | ClawHub | 🟡 Prepped, needs publish token |

**OAuth limitation:** `deeptutor skill login` opens a local callback server on `localhost:44745`. From a remote VPS, the browser can't reach that port → the OAuth flow fails. ClawHub's device flow (`clawhub login --no-browser`) prints a verification URL instead, which works better for remote deployments. (Jul 26 session: GitHub account flagged, Google OAuth also blocked by localhost callback issue.)

## Glama MCP Server Quality Score

Glama scores every published MCP server (TDQS 70% + Coherence 30%) and a low score hurts discoverability. **Key lever: the score stays ~17% until a "Glama release" is created on Glama's admin console** — no release = both scored dimensions read zero, regardless of how well the repo is maintained. A missing LICENSE or glama.json is usually just a stale scan. Full mechanics, TDQS rubric, and the release/resync workflow: `references/glama-mcp-score.md`.

## Glama MCP Server Quality Score

Glama scores every published MCP server (TDQS 70% + Coherence 30%) and a low score hurts discoverability. **Key lever: the score stays ~17% until a "Glama release" is created on Glama's admin console** — no release = both scored dimensions read zero, regardless of how well the repo is maintained. A missing LICENSE or glama.json is usually just a stale scan. Full mechanics, TDQS rubric, and the release/resync workflow: `references/glama-mcp-score.md`.

### FastMCP import split breaks Glama/CI builds (`mcp` v2, proven Aug 4 2026)

Glama (and any fresh CI) installs `requirements.txt` from scratch, so a **Python MCP server breaks on build** if it imports the old FastMCP path. The `mcp` package at **v2.0.0+** removed `mcp.server.fastmcp`; FastMCP moved to a **standalone `fastmcp` package**. Glama emails a "build failed" on the first push that hits it.

```python
# WRONG — removed in mcp v2, breaks Glama/CI build
from mcp.server.fastmcp import FastMCP
# CORRECT — FastMCP is now standalone
from fastmcp import FastMCP
```
```txt
# requirements.txt — must add fastmcp explicitly
mcp>=1.0.0
fastmcp>=2.0.0
```

**Diagnosis:** `pip show mcp` → if >=2.0.0, the old import path is dead. Confirm with `python -c "import mcp.server; print(dir(mcp.server))"` (fastmcp absent) and `python -c "from fastmcp import FastMCP"` (works).

**Pitfall — check sibling repos too.** The same dead import commonly sits in every repo that copied the pattern. After fixing one (genTech-shop), `grep -rn "mcp.server.fastmcp" /root/repos/` surfaced it in genTech-agent-kit the same day. Fix them all, not just the one that errored.

**Verify in a clean venv**, not the cached one, so you know a fresh Glama/CI build passes: `python3 -m venv /tmp/v && /tmp/v/bin/pip install -q -r requirements.txt && /tmp/v/bin/python -c "import server; print('ok')"`.

## Other Distribution Channels

| Channel | Status | How |
|---------|--------|-----|
| **GitHub repos** | ✅ Live | Point to github.com/GentechLabs/ |
| **MCP server** | ✅ Live | `uvx` from GitHub |
| **npx skills** | ✅ Published | 3 skills live: x402-payments, output-enforcer, robinhood-chain |
| **Cursor Directory** | 🆕 Needs Jordan | cursor.directory/plugins/new — sign in with GitHub, submit MCP server listing. OOBE Protocol's SAP MCP already listed here (Jul 22, 2026). Our x402 gateway, DeFi Intelligence, Agent Search all fit as installable MCPs. |
| **Atelier** | 🟡 Needs Forge | app.useatelier.ai/agents/register |
| **PortalHQ / Monad** | 🆕 New priority | Publish SKILL.md, submit to feed |
| **Docker** | ⏸️ Optional | `docker pull ghcr.io/protojay4789/...` |
| **Direct endpoint** | ✅ Already live | Just needs marketing |

## Standalone Plugin Pattern — "Publish Beside, Not Inside"

For high-traffic repos with strict contribution guidelines (94%+ rejection rates, domain-specific barriers, zero-dependency policies), the best distribution is a **standalone plugin repo** rather than a PR into their core.

| Repo profile | Signal | Approach |
|-------------|--------|----------|
| Very high stars (250k+) | Strict maintainer, explicit "no third-party" policy | Standalone plugin only |
| Domain-specific rejections | "Your skill belongs in its own plugin" (CLAUDE.md) | Standalone plugin |
| Zero-dependency policy | "No dependencies on third-party projects" | Standalone plugin |
| Moderate stars, open to plugins | Marketplace/registry exists | Can PR into registry after standalone is proven |

Create a separate repo with `.claude-plugin/plugin.json`, `.codex-plugin/manifest.json`, and skills/ directory. Users install via `/plugin marketplace add <org>/<repo>` then `/plugin install <name>`. Zero rejection risk, organic discovery, no dependency on their release cycle. Proven: GenTech Superpowers plugin (4 skills, live alongside 257k⭐ Superpowers).

Do NOT PR into the parent repo's marketplace unless third-party listings are explicitly supported. Superpowers rejected domain-specific skills at 94% rate.

## Why Not npm/PyPI/Other Registries

- PyPI: 2FA lockout risk, multiple backup codes, unclear which is active
- npm: Same 2FA issues
- pip install from GitHub works identically to PyPI
- Our audience (AI agents) call HTTP endpoints or load MCP configs — they don't `pip install`

## Pitfalls

- Do NOT add `.env` files or hardcoded API keys to any repo
- SKILL.md should never contain secrets — it's a public manifest
- When building a new API, always add it to the Agent Kit plugins/ dir so it auto-discovers
- Test with `uvx --from <repo-url>` before announcing — ensures the packaging works