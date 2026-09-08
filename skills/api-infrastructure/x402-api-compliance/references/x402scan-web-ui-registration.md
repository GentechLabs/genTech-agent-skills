# x402scan Web UI Registration Walkthrough

This documents the step-by-step browser-based registration flow on x402scan.com, as experienced July 17, 2026.

## The Flow

### 1. Navigate to x402scan.com

Start at the homepage: `https://www.x402scan.com`

- Click **"Add your API"** button
- This opens the registration form inline

### 2. Enter your gateway URL

The registration form has:

- A `https://` prefix label
- A textbox with placeholder `api.example.com` — type `api.yourdomain.com`
- An **"Add"** button (initially disabled)
- A **"Set up x402 with a prompt"** button
- A **"Have your agent create an OpenAPI spec for your resource"** button

### 3. After entering URL — scanner runs

The scanner automatically probes your gateway and reports findings:

**If no discovery document found:**
- "No discovery document found at this origin."
- "15 unprotected endpoints skipped" — your non-x402 routes
- The **"Add"** button stays disabled

**Root cause:** The scanner probes `/openapi.json`. If it exists but has no `x-payment-info` on endpoints, the endpoints are invisible.

### 4. Options to proceed

**Path A — "Have your agent create an OpenAPI spec"**
- Opens the "Become Discoverable" docs page
- Key instruction: `npx -y @agentcash/discovery@latest discover "<URL>"`

**Path B — "Set up x402 with a prompt"**
- Same docs page with the full agent prompt to copy-paste

### 5. The fix

Our OpenAPI spec existed but had no `x-payment-info` on any endpoint. Required:

1. `info.contact.email` in OpenAPI
2. `info.x-guidance` — free-text instructions
3. `x-payment-info` on each endpoint with `price`, `protocols`
4. `responses["402"]` on each endpoint
5. `components.securitySchemes.x402`

### 6. Registration endpoint (programmatic)

After fixing the spec, register via the agentcash MCP:

```
POST https://x402scan.com/api/x402/registry/register-origin
Body: { "origin": "https://api.yourdomain.com" }
Auth: SIWX wallet (via agentcash fetch_with_auth)
```

### 7. Validate before registering

```bash
npx -y @agentcash/discovery@latest discover "https://api.yourdomain.com"
npx -y @agentcash/discovery@latest check "https://api.yourdomain.com/v1/endpoint"
```

Fix all warnings except `FAVICON_MISSING` before registering.
