# Account-Level GitHub Pages Block — Diagnosis Reference

## Context

ProtoJay4789's GitHub account has a **permanent account-level restriction** that prevents GitHub Pages from deploying. This is NOT a repo config issue — it's an account flag that blocks Actions execution entirely.

## Symptoms

| Symptom | Detail |
|---------|--------|
| `https://ProtoJay4789.github.io/` | HTTP 404 (always) |
| `POST /pages/builds` | Returns `{"status":"queued"}` but build never executes |
| `GET /pages/builds` | Returns `[]` — **0 builds ever** |
| `GET /pages` | `status: null`, `build_type: legacy`, `public: true` |
| `GET /actions/permissions` | `enabled: true`, `allowed_actions: all` |
| `POST /actions/workflows/.../dispatches` | HTTP 422 — `"Actions has been disabled for this user"` |
| `raw.githubusercontent.com` (public) | HTTP 404 |
| `raw.githubusercontent.com` (with auth token) | HTTP 200 — content is correct |
| `gh-pages` branch | Has `index.html`, `.nojekyll`, correct content |
| Repo visibility | `public`, `has_pages: true` |

## Diagnostic Sequence

```bash
# 1. Check Pages config
TOKEN=$(grep 'oauth_token:' /root/.hermes/profiles/gentech/home/.config/gh/hosts.yml | head -1 | awk '{print $2}' | tr -d '"')
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://api.github.com/repos/ProtoJay4789/ProtoJay4789.github.io/pages" | \
  python3 -c "import sys,json; d=json.load(sys.stdin); print(f'build_type: {d.get(\"build_type\")}, source: {d.get(\"source\")}, status: {d.get(\"status\")}')"

# 2. Check build history (0 = never deployed)
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://api.github.com/repos/ProtoJay4789/ProtoJay4789.github.io/pages/builds" | \
  python3 -c "import sys,json; d=json.load(sys.stdin); print(f'builds: {len(d)}')"

# 3. Check Actions permissions
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://api.github.com/repos/ProtoJay4789/ProtoJay4789.github.io/actions/permissions" | \
  python3 -c "import sys,json; d=json.load(sys.stdin); print(f'enabled: {d.get(\"enabled\")}, allowed: {d.get(\"allowed_actions\")}')"

# 4. Try workflow dispatch (will 422)
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  "https://api.github.com/repos/ProtoJay4789/ProtoJay4789.github.io/actions/workflows/deploy-portfolio.yml/dispatches" \
  -d '{"ref":"main"}' -w "\nHTTP %{http_code}"

# 5. Verify content exists (authenticated raw)
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://raw.githubusercontent.com/ProtoJay4789/ProtoJay4789.github.io/gh-pages/index.html" | head -5
```

## What DOESN'T Work

- ❌ Switching `build_type` between `legacy` and `workflow`
- ❌ Pushing to `gh-pages` branch with correct content
- ❌ `POST /pages/builds` to trigger a build
- ❌ Creating new workflow files
- ❌ Making repo public/private
- ❌ Adding `.nojekyll` file
- ❌ Any Pages API call — the build queue never processes

## What DOES Work

- ✅ `raw.githubusercontent.com` with auth token (content is correct)
- ✅ Git push to any branch (git operations are unrestricted)
- ✅ REST API calls (5,000/hr quota, not affected)
- ✅ VPS hosting at `portfolio.gentechlabs.net` (the permanent home)

## Root Cause

The account is flagged at the GitHub infrastructure level. The exact flag is not exposed via any API endpoint (`suspended_at: null`, `disabled: false`). The 422 on workflow dispatch is the definitive signal: `"Actions has been disabled for this user"` — this is an account-level restriction that repo-level settings cannot override.

The user confirmed: the Actions settings option has been **removed** from their personal account settings page entirely ("they took those options out... no longer available"). This means the restriction is permanent and cannot be resolved through the UI.

## Permanent Resolution

**VPS hosting at `portfolio.gentechlabs.net`** is the only working path. The nginx config already serves `/var/www/portfolio/` on both HTTP (port 80) and HTTPS (port 443, Let's Encrypt cert for `gentechlabs.net` wildcard).

Deploy command:
```bash
scp -o StrictHostKeyChecking=no /tmp/portfolio-latest.html root@2.24.195.196:/var/www/portfolio/index.html
```

Verify:
```bash
curl -s http://portfolio.gentechlabs.net/ | grep -c "x402"
curl -sk https://portfolio.gentechlabs.net/ | grep -c "x402"
```

## What NOT to Do

- Do NOT suggest re-enabling Actions — the option is gone from the account
- Do NOT suggest creating a new GitHub account — not worth it for Pages
- Do NOT keep debugging Pages API — the build queue will never process
- Do NOT suggest Cloudflare Workers as a proxy — VPS is simpler and already working
