# Paperclip Plugin Build — Working Recipe (verified Aug 2026)

Paperclip (paperclipai/paperclip, fork HenkDz/paperclip) is a control plane for
AI-agent companies. Building a plugin for it has one critical gotcha.

## The scaffold trap (hit live)

`@paperclipai/create-paperclip-plugin` scaffolds a standalone plugin OUTSIDE the repo,
but it pins a **stale SDK snapshot** (`@paperclipai/shared@0.3.1` via a local
`.paperclip-sdk/*.tgz`). The SDK's dist expects exports (`PLUGIN_STATUSES`,
`PLUGIN_CATEGORIES`, `PLUGIN_CAPABILITIES`, `PLUGIN_UI_SLOT_TYPES`) that don't exist in
that shared version → esbuild fails with `No matching export in .../@paperclipai/shared`.

**Fix: build the plugin INSIDE the repo workspace** where `@paperclipai/plugin-sdk`
resolves via `workspace:*` (the repo's own plugins like `plugin-llm-wiki` build fine).

## Working recipe (inside repo)

```bash
cd /root/paperclip-fork/packages/plugins
mkdir -p gentech-shop/src/ui gentech-shop/tests
# Model package.json on an existing plugin (plugin-llm-wiki) — use workspace:* for the SDK
cp plugin-llm-wiki/package.json gentech-shop/
cp plugin-llm-wiki/esbuild.config.mjs gentech-shop/
cp plugin-llm-wiki/tsconfig.json gentech-shop/
cp plugin-llm-wiki/vitest.config.ts gentech-shop/
# Edit package.json: name, description, keywords, author
# Write src/manifest.ts, src/worker.ts, src/ui/index.tsx, tests/plugin.spec.ts
cd gentech-shop
pnpm install
pnpm build   # → dist/manifest.js, dist/worker.js, dist/ui/index.js
pnpm test    # vitest — write a spec or it exits 1 with "No test files found"
```

## Plugin structure (minimal)

- **`src/manifest.ts`** — `PaperclipPluginManifestV1`: id, apiVersion, version,
  displayName, categories, capabilities, entrypoints (worker + ui), ui.slots.
- **`src/worker.ts`** — `definePlugin({ setup(ctx) {...}, onHealth() {...} })` +
  `runWorker(plugin, import.meta.url)`. Register data providers with
  `ctx.data.register(name, fn)`, actions with `ctx.actions.register(name, fn)`.
- **`src/ui/index.tsx`** — React component using `usePluginData`, `usePluginAction`
  from `@paperclipai/plugin-sdk/ui`. Export the component named in the slot's
  `exportName`.
- **`tests/plugin.spec.ts`** — vitest using `createTestHarness` from
  `@paperclipai/plugin-sdk/testing`.

## Capabilities needed for a dashboard widget

`events.subscribe`, `plugin.state.read`, `plugin.state.write`,
`ui.dashboardWidget.register`. Slot type `dashboardWidget` with `exportName`.

## Dev server

`pnpm dev` runs the Paperclip server (fork auto-detects port 3101 if 3100 is taken).
Health check: `curl http://localhost:3101/api/health` → `{"status":"ok",...}`.
