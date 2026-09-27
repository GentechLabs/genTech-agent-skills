# VPS Migration from GitHub Pages

Full workflow for moving static sites from GitHub Pages to a self-hosted VPS.

## Why Migrate
- Avoid GitHub API rate limits (5,000/hr primary, 60/min secondary)
- No GitHub account dependency (404/deletion risk)
- Own your infrastructure
- Faster deployment (local copy vs git push)

## Steps

### 1. Copy Files to VPS
```bash
mkdir -p /var/www/portfolio/data
cp index.html /var/www/portfolio/
cp -r data/* /var/www/portfolio/data/
```

### 2. Add Nginx Server Block
```nginx
server {
    listen 80;
    server_name subdomain.your-site.net;
    root /var/www/portfolio;
    index index.html;
    try_files $uri $uri/ =404;

    location /data/ {
        alias /var/www/portfolio/data/;
        add_header Access-Control-Allow-Origin *;
        add_header Content-Type application/json;
    }
}
```
Test: `sudo nginx -t && sudo systemctl reload nginx`

### 3. Fix File Permissions
Nginx needs read access. If file shows 403:
```bash
chmod 644 /var/www/your-site/*.html
chmod 644 /var/www/your-site/data/*
# Check: stat -c "%a %U:%G" /var/www/your-site/file.html
```

### 4. Update Cron Jobs
Change from git push to local cp. Example update:
- Old: `git add . && git commit -m "sync" && git push`
- New: `cp /path/to/source/* /var/www/portfolio/`

### 5. Handle Cloudflare
**If proxied (orange cloud):** Purge cache after every update:
- Dashboard → Caching → Purge Everything
- Or use API: `curl -X POST "https://api.cloudflare.com/client/v4/zones/{zone_id}/purge_cache"`

**If DNS-only (grey cloud):** Changes appear immediately. Use for testing.

**If changes still don't appear:** Check for a Cloudflare Worker intercepting root traffic. See skill SKILL.md section "Cloudflare Worker Interception Trap".

### 6. Update Cron Names
Old names like `...→ GitHub Pages` should be renamed to `...→ VPS` to reflect the new target.

## Common Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| 403 on new file | File permissions too strict | `chmod 644` |
| Old page shows | Cloudflare cache | Purge cache or grey cloud |
| Old page shows after purge | Cloudflare Worker intercepting | Remove root route from Worker |
| Nginx warns "conflicting server name" | Duplicate server blocks | Remove duplicate blocks |

## Cron Jobs to Redirect
These are the cron types that typically push to GitHub and should be redirected to VPS:
- Portfolio Health Check
- Hub Nightly Sync
- Music sync
- Gaming hub sync
- Brain backup
