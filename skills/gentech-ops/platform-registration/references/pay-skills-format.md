# Pay-Skills Format Requirements

Validated against solana-foundation/pay-skills PR #154 (Jun 24, 2026).

## Frontmatter Schema

```yaml
---
name: <service-slug>           # Required. Match directory/name.
title: "Human Readable Name"   # Required. Include "GenTech Labs —" prefix.
description: "..."             # Required. 64-255 chars. No markdown.
use_case: "Use when..."       # Required. 32-255 chars. MUST start with "Use".
category: <enum>               # Required. One of: ai_ml, security, finance, shopping, travel, media, compute, productivity, data, identity
service_url: https://...       # Required. MUST be HTTPS. No HTTP, no localhost, no IPs.
openapi:
  url: https://.../openapi.json  # Fully-qualified HTTPS URL. OR:
  # content: |                   # Inline JSON for small specs (1-5 endpoints).
---
```

## Validation Rules

| Field | Min | Max | Notes |
|-------|-----|-----|-------|
| description | 64 | 255 | Plain text, no markdown links |
| use_case | 32 | 255 | Must start with "Use" |
| service_url | - | - | HTTPS only, domain required |
| endpoint desc | 32 | 120 | Per-endpoint description |

**Rejected:**
- HTTP service_url
- IP address in service_url
- Missing `use_case` field
- Description too short/long
- Pricing on endpoints that don't return 402
- `openapi: { path: openapi.json }` (local filesystem path) — rejected by the registry validator. Use `url:` (remote HTTPS) or `content:` (inline embed) instead.

## OpenAPI Source

The `openapi` field supports three mutually-exclusive variants:

| Variant | Syntax | Registry valid? | Use case |
|---------|--------|----------------|----------|
| Remote URL | `url: https://service.com/openapi.json` | ✅ Yes | Large specs (6+ endpoints) |
| Inline JSON | `content: \|` (YAML literal block) | ✅ Yes | Small specs (1-5 endpoints) |
| Local path | `path: openapi.json` | ❌ No (rejected) | Local `pay server start --openapi` only |

## GenTech Services

| File | Service | Status |
|------|---------|--------|
| providers/gentech/x402-gateway/PAY.md | x402 Gateway (16 endpoints) | ✅ PR #192 (Jul 16, 2026) |

## Submission Process

1. Fork solana-foundation/pay-skills
2. Create `providers/gentech/<service>/PAY.md`
3. Commit with message: `feat: Add GenTech Labs — <service>`
4. Push to fork
5. Create PR against solana-foundation/pay-skills main
