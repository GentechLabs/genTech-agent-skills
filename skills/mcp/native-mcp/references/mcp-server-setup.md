# MCP Server Setup Pattern

**Purpose:** Adding new MCP (Model Context Protocol) servers to Hermes Agent.

## What MCP Servers Provide

- 1000+ app integrations (Composio, Q402, etc.)
- OAuth-handled authentication
- Direct API calls (faster than browser)
- Better scoped permissions

## Setup Pattern

### 1. Identify MCP Server Details

```
Name: COMPOSIO
Transport: HTTP
URL: https://connect.composio.dev/mcp
Auth: OAuth (interactive browser login required)
```

### 2. Attempt Hermes CLI First

```bash
# Try CLI (may not work for all MCP servers)
hermes mcp add <name> <url> --transport http
```

**Pitfall:** `hermes mcp add` may not support all transports. Fall back to manual config.

### 3. Manual Config (When CLI Fails)

**Step A: Create Config Snippet**

```bash
cd /root/.hermes/profiles/gentech
cat >> config-mcp-<name>.yaml << 'EOF'
mcp_servers:
  <name>:
    enabled: true
    url: <url>
    connect_timeout: 60
    timeout: 120
EOF
```

**Step B: Manual Edit (Required)**

```bash
nano ~/.hermes/profiles/gentech/config.yaml
```

Add to `mcp_servers:` section:

```yaml
  <name>:
    enabled: true
    url: <url>
    connect_timeout: 60
    timeout: 120
```

**Step C: Restart Hermes**

```bash
hermes restart
# Or restart the gateway process
```

## Security Guard

Hermes config file is security-protected:
- Patch/write_file tools REFUSE to modify it
- Manual edit or `hermes config` CLI required
- This prevents unauthorized config changes

## Existing MCP Servers (Gentech Setup)

| Name | URL | Purpose |
|------|-----|---------|
| blockrun | command + npx | BlockRun integration |
| coinbase | command + cdp | Coinbase SDK tools |
| hive | command + node | HIVE API integration |
| pay | command + pay | PayAI payments |
| brickken | https://mcp.brickken.com/mcp | Brickken tools |
| wurk | https://wurkapi.fun/mcp | WURK.FUN marketplace |
| q402 | command + npx | Q402 payment tools |

## Composio MCP Server

**What it provides:**
- 1000+ app integrations
- OAuth auto-handled
- Faster than browser automation
- Better scoped permissions

**Key apps for GenTech:**
- X/Twitter — posting, DMs, timeline (solves xurl auth blocker!)
- GitHub — PR management, issues, deployments
- HubSpot — CRM, sales workflows
- Slack — messages, channels
- Notion — docs, databases

**Setup:**
```yaml
mcp_servers:
  composio:
    enabled: true
    url: https://connect.composio.dev/mcp
    connect_timeout: 60
    timeout: 120
```

⚠️ **Composio requires interactive OAuth** — The initial authorization requires a browser login flow that cannot be done from a headless VPS. Run `hermes mcp login composio` on a machine with a browser to complete the OAuth flow. After token is cached, the connection works from any environment.

## Verification

After restart, verify MCP server loaded:

```bash
hermes tools | grep -i mcp
```

Or check Hermes logs for MCP connection errors.

## Common Pitfalls

1. **Config write rejected** — Use manual edit or `hermes config` CLI
2. **Timeout too short** — Increase to 120s for slow MCP servers
3. **URL incorrect** — Verify HTTP vs HTTPS, port numbers
4. **OAuth not working** — Some MCP servers require pre-registration
5. **Server not running** — Check MCP server health separately
6. **Composio OAuth requires browser** — Cannot authenticate from headless VPS. Run `hermes mcp login composio` on a desktop machine first, then the cached token works everywhere.

## When to Use MCP vs Browser

| Situation | Use MCP | Use Browser |
|-----------|---------|-------------|
| API-based action | ✅ | — |
| Form submission | ✅ | ✅ (fallback) |
| OAuth required | ✅ (auto-handled) | ❌ |
| Visual verification | — | ✅ |
| CAPTCHA | — | ✅ (with user) |
| Simple GET/POST | ✅ | — |
| Complex interaction | — | ✅ |
