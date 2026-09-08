# VPS Migration — Offloading from GitHub

**Date:** July 22, 2026
**Reason:** GitHub API rate limits (5,000 req/hr) being exhausted by cron jobs pushing data to GitHub Pages.

## What Moved

| Service | From | To | Size |
|---------|------|----|------|
| Portfolio site | GitHub Pages (ProtoJay4789.github.io) | VPS (portfolio.gentechlabs.net) | 56 KB |
| Music data | GitHub Pages push | VPS static files | 531 MB |
| Gaming hub data | GitHub Pages push | VPS static files | ~50 MB |
| Vault backup | GitHub push | VPS backup directory | 1.4 GB |

**Total:** ~2 GB moved. VPS has 52 GB free.

## Cron Jobs Redirected

| Job | Old Behavior | New Behavior |
|-----|-------------|-------------|
| Portfolio Health Check | Push to GitHub Pages | Copy to /var/www/portfolio/ |
| Hub Nightly Sync | Push JSON to GitHub Pages | Write to VPS |
| vanito-music-sync | Push music to GitHub | Copy to VPS |
| Gaming Hub Sync | Push build data to GitHub | Copy to VPS |
| Brain Backup | Push vault to GitHub | Copy to VPS backup dir |

## GitHub API Savings

~15 API calls/day eliminated. Combined with 5 deleted cron jobs, ~40% reduction in GitHub API usage.

## Remaining GitHub API Consumers

- PR Maintainer (4x/day — checks 18 repos for PRs)
- Contribution Crunch (weekly — checks branches)

## Nginx Config

Portfolio served at `/var/www/portfolio/` with server block for `portfolio.gentechlabs.net`:

```nginx
server {
    listen 80;
    server_name portfolio.gentechlabs.net;
    root /var/www/portfolio;
    index index.html;
    try_files $uri $uri/ =404;
}
```

## Pitfalls

- Nginx location blocks for `/data/` need explicit `alias` directives
- File permissions must be `chmod 644` and `chown www-data:www-data`
- Test with `curl -H "Host: portfolio.gentechlabs.net" http://localhost/`
