# browser-to-api — Verified PoC + Install Pitfalls (Aug 16 2026)

Validated the full `browser-trace` → `browser-to-api` flow end-to-end against our
own deal-tracker API (port 8080). Generated a valid OpenAPI 3.1 spec + a working
zero-dependency `client.mjs` that called the live API and returned real data.
Full run: `/root/poc-browser-api/.o11y/deal-tracker-poc/api-spec/`.

## Install pitfalls that WILL bite (all hit this session)

1. **`browse` CLI is NOT `/usr/bin/browse`.** On this VPS `/usr/bin/browse` is a
   symlink to `xdg-open`. The skill needs the real Browserbase CLI:
   `npm install -g browse` (v0.9.6). Verify with `browse --version` and
   `browse cdp --help` — if you get xdg-open help, you have the wrong binary.
2. **The Hermes skill installer DROPS support files.** `hermes skills install`
   only grabbed the entry-point script. `browser-trace` was missing `lib.mjs` +
   `snapshot-loop.mjs`; `browser-to-api` was missing 5 scripts (`emit.mjs`,
   `filter.mjs`, `infer.mjs`, `load.mjs`, `normalize.mjs`) + the whole `lib/` dir.
   Fix: clone `github.com/browserbase/skills` and copy the missing files into
   `~/.hermes/profiles/<profile>/skills/<skill>/scripts/`. Symptom:
   `ERR_MODULE_NOT_FOUND` for `lib.mjs` when running `start-capture.mjs` /
   `discover.mjs`.
3. **Chrome as root needs `--no-sandbox`.** `google-chrome --headless=new
   --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-o11y about:blank` dies
   with "Running as root without --no-sandbox is not supported." Add `--no-sandbox`.
4. **`browse network on` is REQUIRED for response-body schemas.** The CDP firehose
   (`browse cdp`) has request bodies but NOT response bodies. Without `browse network
   on` + snapshotting the bodies dir, the spec gets `{ description, content: <mimeType> }`
   skeletons instead of inferred JSON schemas. Snapshot the bodies dir BEFORE
   `browse network off` (the temp dir is shared per-session).
5. **Generated client function names are `getv1_health`** (no underscore between
   `get` and `v1`), not `get_v1_health`. Check `client.mjs` exports before calling.

## Verified output shape (deal-tracker PoC)

4 endpoints discovered — `/v1/deals`, `/v1/health`, `/v1/games/price-watch`,
`/v1/games/release-radar` — each with an inferred JSON schema, an `x-confidence`
extension (samples/statusCodes/normalizationFlags), and a working `client.mjs`.
The generated client successfully called the live API (10 deals, health status,
price-watch) — proving the "website → OpenAPI → working client" loop.

## Strategic fit (Jordan's framing)

This is the **inverse** of our normal flow: we hand-write APIs and expose them;
this auto-discovers an API from a website's traffic. For the GenTech Hub (Treasury,
Arcade, Cookbook, Travel, Gaming — websites with APIs behind them), it can
auto-generate OpenAPI specs → makes them discoverable + integrable by other agents
→ feeds the x402 gateway. Also a natural new chapter for the GenTech Academy
"Ship Paid APIs in a Weekend" course: "turn any website into a paid API in 5 minutes."
