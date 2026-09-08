# MCP Server Distribution — Alternative to PyPI/npm

When platform 2FA (PyPI, npm) blocks publishing, MCP servers with `uvx` direct-from-GitHub install bypass all registration gatekeeping.

## The Pattern

Package your API as an MCP server, publish to GitHub, and agents install directly:

```bash
# No PyPI, no npm, no 2FA — just git
uvx --from git+https://github.com/ProtoJay4789/cmc-x402-mcp.git cmc-mcp
```

## Why This Works

| Distribution Method | 2FA Required | Registration | User Install |
|--------------------|-------------|--------------|--------------|
| PyPI (pip install) | ✅ Yes | Account + 2FA | `pip install` |
| npm (npm install) | ✅ Yes | Account + 2FA | `npm install` |
| **MCP via GitHub** | **❌ No** | **None** | **`uvx --from git+...`** |
| Direct API endpoint | ❌ No | None | `curl` or `fetch` |

## Architecture

```
GitHub repo (public)
├── pyproject.toml      # uv-installable package
├── README.md           # Install + config instructions
├── SKILL.md            # PortalHQ discovery format (JSON Feed)
└── src/                # MCP server code
    ├── __init__.py
    └── server.py       # MCP tools with payment gating
```

## Distribution Channels (No Platform 2FA Required)

| Channel | How | Agent UX |
|---------|-----|----------|
| **GitHub README** | Copy the `uvx` command | Copy-paste one line |
| **PortalHQ Monad Feed** | Publish SKILL.md, submit to agents.portalhq.io | Auto-discovered via feed.json |
| **Atelier** | Web form, wallet connect | Browse and connect |
| **x402.org** | List your endpoint URL | Auto-discovered via x402scan |
| **Direct URL** | Share the endpoint | curl or fetch |

## Pitfalls

1. **No version pinning by default** — `uvx --from git+...` installs latest commit. Pin with `@v1.0.0` tag for stability.
2. **GitHub rate limits** — `uvx` caches builds, but frequent pulls may hit unauthenticated rate limits. Use `uv tool install` for persistent installs.
3. **No discovery** — GitHub-only means nobody finds you. Always submit SKILL.md to PortalHQ or list on Atelier alongside.

## Reference Implementation

- `/root/builds/cmc-x402-mcp/` — CMC Gateway as MCP server (6 tools, x402 gated)
- Install: `uvx --from git+https://github.com/ProtoJay4789/cmc-x402-mcp.git cmc-mcp`
- SKILL.md format at `https://agents.portalhq.io/monad/skills/feed.json`