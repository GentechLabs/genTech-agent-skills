# Cloudflare Workers Deployment — x402 APIs

**Date:** June 27, 2026
**Repo:** `ProtoJay4789.github.io`
**Worker:** `gentechlabs-api` (x402 payment infrastructure)

---

## Deployment Transcript

### Initial Deploy Error (KV Placeholder Invalid)

```
✘ [ERROR] A request to the Cloudflare API (/accounts/.../workers/scripts/gentechlabs-api/versions) failed.
  KV namespace 'your-kv-namespace-id' is not valid. Please verify the namespace_id in your configuration. [code: 10042]
```

**Root cause:** `wrangler.toml` had placeholder KV ID that never got replaced with a real namespace ID.

### Fix Applied

1. **Disabled KV binding temporarily** in `wrangler.toml`:

```toml
# KV namespace temporarily disabled
# Create via: wrangler kv:namespace create "NONCE_STORE"
# Then uncomment and add the ID below
# [[kv_namespaces]]
# binding = "NONCE_STORE"
# id = "your-kv-namespace-id"
```

2. **Updated worker name** from `gentechlabs` to `gentechlabs-api` to match Cloudflare CI expectations.

3. **Graceful degradation in code** — x402 verification already had:

```typescript
// x402-verification.ts line 165
if (env?.NONCE_STORE) {
  await env.NONCE_STORE.put(proof.nonce, JSON.stringify({...}), { expirationTtl: 86400 });
}
```

4. **Committed and pushed** to GitHub. Cloudflare GitHub Integration auto-deployed.

### Successful Deploy Log

```
Executing user build command: npm install
up to date, audited 64 packages in 1s
Success: Build command completed

Executing user deploy command: npx wrangler deploy
Total Upload: 18.31 KiB / gzip: 4.82 KiB
Your worker has access to the following bindings:
- KV Namespaces: (none — temporarily disabled)
- Vars: ENVIRONMENT = "production"
✅ Published gentechlabs-api
```

---

## GitHub Integration Configuration

**Cloudflare Dashboard → Workers & Pages → Overview → "Connect to Git"**

| Field | Value |
|-------|-------|
| **Repository** | `ProtoJay4789.github.io` |
| **Project name** | `gentechlabs-api` |
| **Production branch** | `main` |
| **Framework preset** | None |
| **Root directory** | `/` |
| **Build command** | `npm install` |
| **Deploy command** | `npx wrangler deploy` |

---

## How to Enable KV Later (Optional)

For replay protection (prevent payment reuse):

```bash
cd /root/repos/ProtoJay4789.github.io
npx wrangler kv:namespace create "NONCE_STORE"
```

Copy the returned ID, uncomment `[[kv_namespaces]]` in `wrangler.toml`, paste the ID, push to GitHub.

---

## Worker Routes

| Route | Pattern | Zone |
|-------|---------|------|
| API | `https://gentechlabs.net/api/*` | `gentechlabs.net` |
| v1 endpoints | `https://gentechlabs.net/v1/*` | `gentechlabs.net` |

---

## Key Files

- `wrangler.toml` — Worker configuration
- `src/worker.ts` — 485 lines, 16 endpoints with x402 integration
- `src/x402-verification.ts` — 297 lines, on-chain Base USDC verification
- `package.json` — Dependencies: `@types/node`, `wrangler`, `typescript`

---

## Pitfalls Discovered

| Pitfall | Impact | Fix |
|---------|--------|-----|
| KV placeholder ID | Deploy fails with `code: 10042` | Create real namespace or disable binding |
| Worker name mismatch | CI auto-overrides + warning | Match CI name in `wrangler.toml` |
| No TS check before push | Deploy fails silently with syntax errors | Run `npx tsc --noEmit` before commit |

---

## Verification

```bash
# Health check
curl https://gentechlabs.net/v1/health

# Should return: {"status":"healthy","timestamp":"..."}
```