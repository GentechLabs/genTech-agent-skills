# Private Repo — GitHub Pages Diagnosis

When a GitHub Pages site returns 404 for ALL URLs (root, index.html, subpages, raw.githubusercontent.com), the repo may be **private**.

## Diagnosis Flow

### Step 1: Check repo page on github.com
```bash
curl -s -o /dev/null -w "%{http_code}" "https://github.com/OWNER/REPO"
```
- **200** = public repo. Pages should work. Check workflow/build status.
- **404** = private repo. GitHub blocks anonymous access.

### Step 2: Check raw.githubusercontent.com
```bash
curl -s -o /dev/null -w "%{http_code}" "https://raw.githubusercontent.com/OWNER/REPO/main/hub-vanito.html"
```
- **200** = public. Files are accessible.
- **404** = private. Raw CDN also blocks without auth.

### Step 3: Confirm with auth
```bash
curl -s -o /dev/null -w "%{http_code}" -H "Authorization: token $PAT" \
  "https://raw.githubusercontent.com/OWNER/REPO/main/hub-vanito.html"
```
- **200 with auth** = confirmed private repo. Files exist, just not publicly served.

### Step 4: Check git tree (local clone)
```bash
cd /path/to/repo
git ls-tree HEAD hub-vanito.html
# If file shows up here, it exists on remote — the 404 is a visibility issue, not a missing file
```

## Root Causes

| Cause | Symptom | Fix |
|-------|---------|-----|
| **Repo is private** | All URLs 404, raw.githubusercontent.com also 404 | Make repo public, or use Cloudflare Worker proxy with PAT |
| **GitHub Actions disabled at account level** | Workflow dispatch returns 422 "Actions has been disabled for this user", Pages builds queue but never execute (0 builds ever), even legacy gh-pages branch won't deploy | User must go to their **personal account settings** (NOT repo settings): profile picture (top right) → Settings → scroll left sidebar to "Code, planning, and automation" → Actions → General → enable "Allow all actions" → Save. **The direct link `github.com/settings/actions` often 404s for personal accounts** — use the menu path instead. Repo-level settings alone won't fix this. |
| **GitHub Actions disabled at repo level** | Pages setting says "built" but no deployment | Enable Actions in repo Settings → Actions → General |
| **Workflow file missing/broken** | Pages build type is "workflow" but no runs | Check `.github/workflows/deploy-portfolio.yml` exists |
| **No CNAME configured** | protojay4789.github.io returns 404 | Pages should work without CNAME — check other causes first |

## Account-Level vs Repo-Level Actions Settings

GitHub has TWO separate settings for Actions:

1. **Repo-level** — `https://github.com/OWNER/REPO/settings/actions` — controls whether Actions can run in this specific repo
2. **Account-level** — `https://github.com/settings/actions` (may 404 for personal accounts) — controls whether your account can use Actions at all

**The account-level setting overrides the repo-level setting.** Even if the repo says "Allow all actions", if the account has Actions disabled, nothing will run.

**How to find the account-level setting when the direct link 404s:**
1. Click your profile picture (top right of any GitHub page)
2. Click "Settings" (last option in dropdown)
3. On the left sidebar, scroll down to "Code, planning, and automation"
4. Click "Actions" → "General"
5. Select "Allow all actions" and Save

## VPS Fallback (When Actions Is Blocked at Account Level)

If the account-level Actions block cannot be resolved (user can't find the setting, or it's permanently disabled), serve the portfolio from the VPS instead:

```bash
# 1. Start a Python HTTP server on the repo directory
cd /root/repos/ProtoJay4789.github.io
python3 -m http.server 8090 --bind 0.0.0.0

# 2. Add nginx proxy for a subdomain (e.g., vanito.gentechlabs.net)
# Add to /etc/nginx/sites-enabled/gentech:
# server {
#     listen 80;
#     server_name vanito.gentechlabs.net;
#     location / {
#         proxy_pass http://127.0.0.1:8090;
#         proxy_set_header Host $host;
#         proxy_set_header X-Real-IP $remote_addr;
#     }
# }

# 3. Access via VPS IP: http://VPS_IP:8090/hub-vanito.html
```

**Limitations of VPS fallback:**
- No HTTPS by default (unless nginx + certbot is configured)
- Requires the Python server to stay running (use background=true or systemd)
- VPS IP is not a shareable URL — needs a domain + DNS record
- Not suitable for production/public sharing without proper domain setup

## Fix Options

### Option A: Make repo public
1. Go to repo Settings → scroll to Danger Zone → Change visibility
2. Next push triggers Pages build
3. Site goes live within 2-5 min

### Option B: Cloudflare Worker proxy (keep private)
Deploy a Worker that proxies raw.githubusercontent.com with the PAT:
```js
export default {
  async fetch(request) {
    const url = new URL(request.url);
    const ghPath = url.pathname;
    const ghUrl = `https://raw.githubusercontent.com/OWNER/REPO/main${ghPath}`;
    const response = await fetch(ghUrl, {
      headers: { 'Authorization': `Bearer ${PAT}` }
    });
    return new Response(response.body, response);
  }
}
```

## Verification After Fix

1. `curl -s -o /dev/null -w "%{http_code}" https://protojay4789.github.io/` → **200**
2. `curl -s -o /dev/null -w "%{http_code}" https://protojay4789.github.io/hub-vanito.html` → **200**
3. `curl -s -o /dev/null -w "%{http_code}" https://raw.githubusercontent.com/OWNER/REPO/main/hub-vanito.html` → **200**
