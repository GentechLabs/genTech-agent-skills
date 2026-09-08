# BlockRun MCP — Adding New Image Models

When BlockRun's backend supports a new model (e.g. bytedance/seedream-5-pro) but the MCP tool schema's model enum doesn't include it yet, patch the MCP server source directly.

## Where the Enum Lives

The blockrun MCP server is at `@blockrun/mcp`. The image model enum is in `dist/index.js`:

```
var IMAGE_MODELS = [
  "bytedance/seedream-5-pro",  // ← add new models here
  "zai/cogview-4",
  "google/nano-banana",
  ...
];
```

And the pricing table:

```
var GENERATE_MODEL_COST = {
  "bytedance/seedream-5-pro": 0.018,  // ← add pricing here
  "zai/cogview-4": 0.015,
  ...
};
```

## Patching the Running Server

The server runs from `npx @blockrun/mcp@latest`, which caches in the npx directory. Find the path:

```bash
# Find the running MCP server process
ps aux | grep "blockrun.*mcp" | grep -v grep

# Then patch the file at that path
```

**For npx-cached installs**, the path is typically:
`/root/.npm/_npx/<hash>/node_modules/@blockrun/mcp/dist/index.js`

## Patches Required

1. Add the model id to `IMAGE_MODELS` array
2. Add the pricing entry to `GENERATE_MODEL_COST` object
3. Optionally update the tool description text

## Verifying It Worked

Call `blockrun_image` with the new model id. If the tool schema enum is still cached from session start, restart the MCP connection:

```bash
# Kill the MCP process — Hermes will restart it
pkill -f "@blockrun/mcp"
```

Then try the tool call again. If the schema hasn't updated (cached per-session), the patched copy will load on next session start.

## Wallet Note

The wallet is server-managed — killing the MCP process doesn't lose funds. BlockRun manages the wallet server-side. The `.session` file at `~/.blockrun/.session` is the local signing key, not the balance source.

**CRITICAL: Do NOT run a standalone script that calls `getOrCreateWallet()` from `@blockrun/llm`**: it will overwrite the `.session` file with a new wallet key, causing the MCP server to lose its signing key on restart. The MCP connection will recover on next Hermes session restart (BlockRun's backend re-associates the wallet), but the immediate result is a "payment rejected" error. Always patch through the existing MCP server, not through standalone scripts.

## Updating the Config for a Local Patched Copy

For a permanent local patched install (doesn't get overwritten by npx cache updates):

```bash
# Install locally
mkdir -p ~/blockrun-mcp && cd ~/blockrun-mcp
npm init -y
npm install @blockrun/mcp@latest

# Patch the local copy
# Edit node_modules/@blockrun/mcp/dist/index.js — add model to IMAGE_MODELS and GENERATE_MODEL_COST

# Update Hermes config to use local copy instead of npx
hermes config set mcp_servers.blockrun.command node
hermes config set mcp_servers.blockrun.args '["/root/blockrun-mcp/node_modules/@blockrun/mcp/dist/index.js"]'
```
