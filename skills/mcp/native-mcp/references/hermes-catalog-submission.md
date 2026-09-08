# Hermes MCP Catalog Submission

Full example manifest and PR template for submitting an MCP server to the Hermes Agent MCP Catalog.

## Example manifest.yaml

```yaml
manifest_version: 1

name: gentech-shop
description: Game deals, price comparisons, and UE5.8 MCP bridge — query 35+ stores from your agent.
source: https://github.com/ProtoJay4789/genTech-shop

transport:
  type: stdio
  command: "npx"
  args: ["-y", "@gentech/shop-mcp@0.1.0"]
  version: "0.1.0"

auth:
  type: none

post_install: |
  GenTech Shop connects to api.gentechlabs.net for game data. No API key needed for basic queries.
  1. Run `hermes restart` to pick up the new tools
  2. Ask your agent "find me cheap games" or "what's on sale right now"
  3. For UE5.8 integration, also run `hermes mcp install unreal-engine`
```

## Catalog rules checklist

- [ ] Exact version pin (e.g. `@scope/pkg@1.0.0`, not `@scope/pkg@latest`)
- [ ] Version released at least 14 days before PR (supply chain cooldown)
- [ ] Git-based installs pin a full 40-char commit SHA
- [ ] No reserved/bundled name (check existing entries in optional-mcps/)
- [ ] post_install covers server-side setup the user must do
- [ ] auth section matches what the server actually requires

## PR template

```
## Summary

Adds <name> to the Hermes MCP Catalog.

<description>

## Transport

<type: stdio or http>

## Auth

<none, api_key, or oauth>

## Supply chain

- <package> version <x.y.z> released <date> (>14 days ago)
- Exact version pinned in manifest.yaml

## Testing

- `hermes mcp install <name>` — installs successfully
- `<tool_name>` tool discovered and functional
```

## Existing entries reference

| Entry | Transport | Version pin |
|-------|-----------|-------------|
| blender | stdio (`uvx blender-mcp==1.6.4`) | `1.6.4` (released 2026-06-11) |
| n8n | stdio (git clone) | Full SHA `7a9ae007` |
| linear | HTTP (remote) | N/A (HTTP) |
| unreal-engine | HTTP (localhost) | N/A (HTTP) |
