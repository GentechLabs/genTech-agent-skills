---
name: web-deployment
description: Deploy HTML dashboards, demo suites, and subdomain pages to the VPS — including nginx config, portfolio linking, and DNS setup
category: gentech-ops
version: 1.0.0
author: Gentech
tags: [deployment, vps, nginx, subdomain, portfolio, demo, dns]
trigger: "When shipping a new dashboard, demo page, or product hub that needs to go live on gentechlabs.net. When adding a new subdomain. When updating the portfolio site."
---

# Web Deployment

## Purpose
Deploy new HTML pages, dashboards, and demo suites to the VPS, set up subdomains, and link everything from the portfolio site. One workflow for getting products live.

## Site Routing Rule (Jordan-approved Aug 16, 2026) — THE canonical routing decision

There are THREE public surfaces. Route every piece of content to exactly ONE of them, like the other routing layers (model routing, etc.). Never let them drift into overlap.

| Content type | Goes to |
|---|---|
| Company narrative, problems, roadmap, AAE stack, API services, case studies | **Main site** `gentechlabs.net` (`index.html`) |
| Personal work history, career, skills, experience, open-source PRs, connect | **Portfolio** `portfolio.gentechlabs.net` + `gentechlabs.net/portfolio/` (same `/var/www/portfolio/index.html`) |
| Live, working, touchable artifacts (demos, videos, endpoints, dashboards) | **Demo site** `gentechlabs.net/demo.html` |
| Internal ops (Mess Hall, vault health, considerations, cron counts, agent online-status, 24/7 ops detail) | **Vault only — NEVER public** |
| Token/support/ecosystem promotion (AAE Token, $TREASURY) | **Not on any public surface** |

**The rule in one line:** *Main site = the story. Portfolio = the person. Demo site = the proof. Internal = never public.*

**Portfolio audit performed Aug 16, 2026** — stripped the portfolio down to: header, stats (Repos/PRs Shipped/API Endpoints/Marketplaces — NOT cron jobs), Two-Agent Ops (framed as differentiator, not internal detail), About, The GenTech Journey, Open Source, Tech Stack, Connect, footer. Removed: V4 intro banner, Core Projects (→ demo/main), AAE Stack (dupe of main), 24/7 Agent Ops, API Services, Hackathons (stale), Agent Stack, Mess Hall, Support Ecosystem (token), One-Liner Deploy. Backup at `index.html.pre-audit-backup`.

**Pitfall — the portfolio is served at TWO URLs:** `portfolio.gentechlabs.net` (own nginx server block) AND `gentechlabs.net/portfolio/` (alias to the same `/var/www/portfolio/index.html`). Both point at the one file. Edit that file and both update. `/root/portfolio/` is a SEPARATE, older repo that is NOT the deployed source — do not confuse them.

## Deployment Workflow

### Step 1: Build the HTML Page — IN THE REPO, not the webroot
Build in the canonical repo (`/root/repos/gentechlabs.github.io/{path}`), commit + push, then `cp` to `/var/www/gentechlabs/` and `chown www-data:www-data`. **Never create pages only in the webroot** — webroot-only pages are orphans: invisible to git, lost on VPS rebuild, and one careless `cp` from being clobbered. Proven failure Sep 4, 2026: vanito.html's 87KB dashboard was overwritten from a wrong-source file that shared the name, and the original was unrecoverable; the sweep then found 11 more orphan pages (demo, portfolio, jordan, concept*, hub-backup, hub-launcher). Legacy orphans being fixed in place must be codified into the repo in the same pass. Use the dark theme (bg: #0a0e17, text: #e2e8f0, accent: #60a5fa) to match the existing suite.

### Step 2: Deploy to VPS
```bash
scp /var/www/gentechlabs/{name}.html root@2.24.195.196:/var/www/gentechlabs/
ssh root@2.24.195.196 "chown www-data:www-data /var/www/gentechlabs/{name}.html && chmod 644 /var/www/gentechlabs/{name}.html"
```

### Step 3: Verify
```bash
curl -sI "https://gentechlabs.net/{name}.html"
# Should return HTTP/2 200
```

**Deploying a sub-page into a subdirectory of the hub (PROVEN Aug 2026).**
The gaming tracker pages (POE2, Helldivers 2) live in `Gaming/` under the hub root,
not as top-level `{name}.html`. nginx `location / { root /var/www/gentechlabs; }`
serves any subpath, so a file at `/var/www/gentechlabs/Gaming/helldivers2.html`
is live at `https://gentechlabs.net/Gaming/helldivers2.html`. Flow:
1. Build the HTML + a sibling `.json` data file in the canonical repo
   (`/root/ProtoJay4789.github.io/<path>`).
2. `mkdir -p /var/www/gentechlabs/Gaming` and `cp` both files into it
   (no `chown` needed if you write as root and the site is read-only static).
3. Verify against the **live domain**: `curl -s -o /dev/null -w "%{http_code}"`
   on the `https://gentechlabs.net/...` URL — expect 200 on both the page AND the
   `.json` it fetches. The `.json` must return 200 too, or the page renders "could
   not load build data."
4. Wire it into the live hub's relevant tab: add an `<a class="link-card">` to the
   `link-grid` in `/var/www/gentechlabs/hub.html`, then `curl` the hub and `grep`
   for the new label to confirm it's live.

**Pitfall — a freshly-written HTML file returns HTTP 403 (nginx can't read it).**
When you create a page with `write_file` directly into `/var/www/gentechlabs/`, the file lands
with mode `600` (owner root only). nginx runs as `www-data`, so it cannot read the file and
returns **403 Forbidden** even though the file exists and the path is correct. This is distinct
from a 404 (wrong path) or a stale-cache issue. Fix:
```bash
chmod 644 /var/www/gentechlabs/{name}.html
# then verify
curl -s -o /dev/null -w "%{http_code}" "https://gentechlabs.net/{name}.html"   # expect 200
```
**Confirmed Aug 5, 2026:** `treasury-demo.html` returned 403 after `write_file`; `chmod 644`
flipped it to 200. Always `chmod 644` any file you write into the web root (the `scp`+`chown`
deploy path in Step 2 already does this — the gap is when you `write_file` directly). Check
permissions FIRST when a new page 403s: `ls -la /var/www/gentechlabs/{name}.html` — if it shows
`-rw-------`, that's the cause, not nginx config or Cloudflare.

**Pitfall — GitHub Pages is NOT the live deployment (flagged account).**
On this account Pages serves from the `gh-pages` branch (not `main`) and raw
returns 404. Pushing to `main` does NOT make a page live, and a 404 from the
`protojay4789.github.io` URL does NOT mean the deploy failed. Always treat the VPS
nginx copy as the source of truth for "is it live," and verify with the
`gentechlabs.net` URL, not the Pages URL. Still `git pull --rebase` + push to
`main` to keep the repo canonical (survives VPS rebuilds), but the VPS copy is
what the user actually views.

**Pitfall — pick a clean local test port.** Port 8095 is occupied by another
service that responds `{"detail":"Not Found"}` (a FastAPI-style responder), which
looks like a broken deploy when you curl it. Use an uncommon port (e.g. 8137) and
bind `127.0.0.1` for `python3 -m http.server` test servers, and confirm the server
actually started (its own `OSError: [Errno 98] Address already in use` traceback
tells you the port was taken).

**Pitfall — verify CONTENT, not just HTTP 200 (Cloudflare stale cache).**
Aug 2, 2026: a replaced PDF kept serving the OLD file through Cloudflare
(`cf-cache-status: HIT`) even after the file on disk was correct. curl showed
200, but the bytes were the previous version — the user saw a 404 / wrong
content while the agent saw "200 OK". For binary/PDF/HTML replacements:
1. Download and check actual content: `pdftotext served.pdf - | grep -i 'expected title'`
   or `grep -oE '<title>[^<]*</title>'` on the served page.
2. Cache-buster forces Cloudflare revalidation: append `?v=20260802b` —
   if the busted URL shows new content, the edge was holding the old copy.
3. CF cache purge needs a token with **Cache Purge** permission — a zone-read
   token verifies (`/user/tokens/verify` → active) but returns 10000
   "Authentication error" on `POST /zones/{id}/purge_cache`. Don't fight it;
   use the cache-buster or serve the artifact from GitHub raw instead.
4. **Bulletproof fallback: host the artifact in the repo and link the raw URL**
   (`https://raw.githubusercontent.com/OWNER/REPO/main/path`) — no Cloudflare
   in the path, cannot serve stale content. Preferred for submission-critical
   files (hackathon deck PDFs, etc.).
5. Also verify the LOCAL disk copy matches what nginx serves: `curl -H "Host:
   gentechlabs.net" http://127.0.0.1/path` — if local is new but public is
   old, it's the CDN, not your deploy.

**Pitfall — platform extraction failures still have partial-data paths (Aug 30).**
A Facebook reel link failed full extraction (login wall), but `r.jina.ai` returned real
partial metadata (title, view counts, page info). Pattern: when a platform blocks full
extraction, take whatever partial data the probe DID return, then reconstruct the *topic*
via web research and deliver the substance — research the subject the link points at, not
just the link. "Cannot extract" is only the final answer when partial-data + topic
reconstruction both come up empty.

**Pitfall — same-name file from an old project.** Before linking a file that
"already exists" in the web root, check WHAT it is: `file {name}.pdf`,
`pdftotext` it, check the `<title>`. Aug 2, 2026: `arc-presentation.pdf` was
actually the previous TokenRiskOracle (Somnia) deck sitting in the directory
from an earlier hackathon — nearly got submitted to the wrong programme.
`ls -la` timestamps tell the story (old file predates the new HTML).

### Step 4: Set Up Subdomain (Optional)
If the page deserves its own subdomain (e.g., `yield.gentechlabs.net`, `arb.gentechlabs.net`, `demo.gentechlabs.net`):

Create nginx config on VPS:
```bash
ssh root@2.24.195.196 "cat > /etc/nginx/sites-enabled/{subdomain} << 'EOF'
server {
    listen 80;
    server_name {subdomain}.gentechlabs.net;
    root /var/www/gentechlabs;
    index {name}.html;
    location / { try_files \$uri \$uri/ =404; }
}
EOF
nginx -t && nginx -s reload"
```

Then add an **A record** in Cloudflare DNS. This is a manual step — Cloudflare API credentials are not stored, so the user must log into cloudflare.com and add the record themselves:

| Subdomain | Type | Value | Proxy Status |
|-----------|------|-------|-------------|
| `{subdomain}` | A | `2.24.195.196` | DNS only (grey cloud) |

**DNS-only (grey cloud)** is appropriate for demo pages and internal dashboards — no user data, no forms, no sensitive info. The subdomain resolves in ~60s. If SSL/HTTPS is needed later, flip to proxied (orange cloud) and run certbot on the VPS.

**Pitfall — subdomain won't work until DNS is added:** Nginx config alone isn't enough. Without the Cloudflare A record, the subdomain returns NXDOMAIN. Always tell the user explicitly which records to add and that they need to log in to Cloudflare to do it. Provide a ready-to-copy table like the one above.

### Step 5: Link from Portfolio
Add a nav link to the portfolio site:
```bash
ssh root@2.24.195.196 "sed -i 's|<li><a href=\"#experience\">exp</a></li>|<li><a href=\"#experience\">exp</a></li>\n        <li><a href=\"https://{subdomain}.gentechlabs.net\">{label}</a></li>|' /var/www/portfolio/index.html"
```

Also add a project card in the `#projects` section with description, tech tags, and link. Use `sed` to insert directly after the `<div class="projects-grid">` opening tag, matching the existing card format:

```bash
ssh root@2.24.195.196 "sed -i '/<div class=\"projects-grid\">/a\\
      <div class=\"project-card\">\
        <span class=\"project-icon\">🌈</span>\
        <h3>Dashboard Name</h3>\
        <p class=\"project-desc\">Description of what it does.</p>\
        <div class=\"tech-tags\"><span class=\"tech-tag\">Tag1</span><span class=\"tech-tag\">Tag2</span></div>\
        <div class=\"impact-metric\">📈 Live dashboard</div>\
        <a href=\"https://{subdomain}.gentechlabs.net\" class=\"project-link\">Live Dashboard →</a>\
      </div>' /var/www/portfolio/index.html"
```

Verify with `grep -c '{subdomain}.gentechlabs' /var/www/portfolio/index.html` — should return a count of project cards added.

**Pitfall — sed inserts get collapsed into single-line entries without proper formatting.** The `sed` command above inserts newlines literally. After inserting, verify the output has proper line breaks by checking with `grep -A 10 '{subdomain}' /var/www/portfolio/index.html`. If entries are collapsed, the `\` line continuations in the `a\\` block need adjustment — each `\` at line end produces a newline in the output.

### Step 6: Link from Demo Hub
If the new page is part of the product suite, add a card to `demo.html` in the appropriate section (Payment Infrastructure, DeFi Intelligence, Agent Infrastructure, Technical Stack).

## Deliver the Link — Build First, Send ONLY the Link

**User-verified pain point (Aug 2, 2026):** "Every time you're working on
giving me the link, the message gets cut off short." Cause: inlining long
status + HTML content in the same message as the link; Telegram truncates at
~4000 chars and the URL at the end never arrives.

**The pattern for ANY deliverable link (deploy page, demo, PDF, deck):**
1. Build the artifact on the server first — all tool calls, invisible to chat.
2. Verify it's live (`curl -o /dev/null -w '%{http_code}'` AND content check).
3. Then send a SHORT message with the link front-and-center, nothing after:
```
Here's the deploy page, boss:

https://gentechlabs.net/arc-deploy.html

Connect MetaMask, sign, done.
```
4. Never bury a link at the end of a long status recap. Status recap = separate
   message; link = its own message.
5. Never paste HTML/JS into chat — host it and link it. (See `message-length-discipline`
   skill for the full char-limit discipline; this is the deployment-specific
   delivery rule.)

## Demo Suite Structure

The demo hub at `gentechlabs.net/demo.html` is organized into sections:

| Section | Content |
|---------|---------|
| **Payment Infrastructure** | x402 Gateway, Q402 Gasless, Agent Kit |
| **DeFi Intelligence** | Yield Rainbow, GTA Arb Monitor, Narrative Rotation |
| **Agent Infrastructure** | Self-Evolution Harness, Agent Credit Score, GenTech Smash |
| **Technical Stack** | AI Models, Blockchain, Infrastructure |

Each card has: icon, status badge (LIVE/PREVIEW/SOON), title, description, and link.

## Portfolio Site Details

- **Location:** `/var/www/portfolio/index.html` (NOT `/var/www/gentechlabs/portfolio/`)
- **Nginx config:** `location /portfolio/ { alias /var/www/portfolio/; }`
- **Nav links** are in the `<ul class="nav-links">` section
- **Project cards** are in the `<div class="projects-grid">` section
- **Tech tags** use `<span class="tech-tag">` with accent color
- **Impact metrics** use `<div class="impact-metric">`

## Pitfalls

- **Portfolio is at `/var/www/portfolio/` NOT `/var/www/gentechlabs/portfolio/`** — different root. Always check nginx config before assuming path.
- **Subdomains need DNS records** — nginx config alone isn't enough. The user must add A records in Cloudflare DNS. Without DNS, the subdomain returns NXDOMAIN.
- **DNS-only subdomains** (grey cloud in Cloudflare) are fine for demo pages and internal dashboards — no user data, no forms, no sensitive info. If SSL/HTTPS is needed later, flip proxy to orange (proxied) and set up certbot on the VPS.
- **Nginx reload after config change** — always run `nginx -t` before `nginx -s reload` to catch syntax errors.
- **Conflicting server names** — if a subdomain is already defined in another config file, nginx will warn but still work. The first match wins.
- **Portfolio sed edits** — use exact match strings. The nav has specific indentation. Verify with grep after editing.
- **Cloudflare cache** — new pages may take a minute to appear. Use `curl -H "Cache-Control: no-cache"` to bypass.
- **Lesson pages must be proper HTML** — not plain markdown. Always wrap in a styled HTML template with DOCTYPE, head, body, and matching dark theme CSS. See `references/lesson-page-template.md` for the pattern.
- **`.gitignore` re-ignores media — force-add anything pages load (burned twice Sep 4).** A late `**/*.mp4` / `**/*.mp3` rule can override earlier negations, so `git add -A` silently skips files that sit in the working tree — Pages then 404s the asset (dead video/audio) with no commit error. Check with `git check-ignore -v <file>`, fix with `git add -f <file>`, and curl the live asset URL after push.
- **Webroot backup to GitHub — chunked pushes + release assets (proven Sep 4).** A single >1.2G git-over-HTTPS push dies silently (`send-pack: unexpected disconnect while reading sideband packet`) and may leave "Everything up-to-date" lies in the transcript — verify the remote SHA, never the push's exit text. Chunk the tree into ≤250MB commits, push each, and ship the tail as a GitHub release asset (2GB/file limit — different upload path, immune to the pack disconnect). Full suite snapshot: private repo `GentechLabs/gentech-webroot-backup`.
- **404 on existing file** — if nginx returns 404 for a file that exists with correct permissions (`www-data:www-data`, 644), the issue is likely a conflicting server_name in another config file. Run `nginx -T 2>&1 | grep -E "server_name|root |index "` to see all active server blocks. The `localhost` hostname won't match any server_name — always test with the proper `Host` header: `curl -sI -H "Host: gentechlabs.net" http://127.0.0.1/path`.
- **Mobile-only container** — the main site was originally `max-width: 480px` (phone column on desktop). When building new pages, use `max-width: 1100px` for responsive layout. Use `.card-grid` for 2-col tablet / 3-col desktop card layouts, and `.stack-grid` for multi-column stack displays.
- **Subdomain SSL certs can share the wildcard** — subdomains on the same VPS can reuse `/etc/letsencrypt/live/gentechlabs.net/fullchain.pem` in their nginx config. No need to run certbot for each one individually. Just reference the shared cert in the 443 server block.
- **Subdomains as AAE layer showcases** — each subdomain can represent a different AAE layer. Pattern: yield.gentechlabs.net = Layer 7 (Intelligence), narrative.gentechlabs.net = Layer 7 (Intelligence). The page header should include a badge row showing the layer number, status, and tech tags. Include a "Layer Context" card at the top explaining how this dashboard fits into the AAE stack.
- **Dashboard pages need market analysis sections** — when building a data dashboard, include a dynamic analysis section that interprets the current data for the user. Pattern: renderMarketAnalysis() function that reads the current data state and produces oversold/neutral/overbought analysis with recovery signals and user advice. The analysis should answer "when could the bear end?" and "how do I use this for my portfolio?"
- **Back-link on subdomain pages must go to the demo suite** — subdomain pages (yield, narrative, arb) should link back to `gentechlabs.net/demo.html` (not `gentechlabs.net` or an old hub page). Use `🏠 Home` as the link text, not `🏠 Hub` or `🏠 GenTech`.
- **Site content audit pattern** — when Jordan asks to audit the main site, the checklist is: remove personal hubs, gaming hubs, DeFi dashboards, Labs dead tabs, Mess Hall, Hackathon Track, Support/Token sections. Add: Problems We Solve, Roadmap, Case Studies. Update layer counts. Fix container width for desktop. Update bottom nav and settings modal to match new sections.
- **Subdomain as AAE layer showcase** — each subdomain can represent a different AAE layer. Pattern: yield.gentechlabs.net = Layer 7 (Intelligence), narrative.gentechlabs.net = Layer 7 (Intelligence). The page header should include a badge row showing the layer number, status, and tech tags. Include a "Layer Context" card at the top explaining how this dashboard fits into the AAE stack. Include a "Treasury Integration" card showing how the Agentic Treasury uses this data. The back-link should go to the demo suite, not the main site.

## VPS Maintenance — Disk Space Recovery

**Pattern proven Jul 28, 2026.** The VPS (193GB disk) fills up over time from logs, caches, and Docker artifacts. When Hostinger sends a "disk space almost full" alert, run this recovery sequence:

### Step 1: Diagnose
```bash
ssh root@2.24.195.196 "df -h / && echo '---' && du -sh /var/log/* /var/cache/* /root/.npm /root/.cache /var/lib/docker /tmp/* 2>/dev/null | sort -rh | head -15"
```

### Step 2: Clean Logs
```bash
# Vacuum journal to 500MB
journalctl --vacuum-size=500M

# Remove old rotated logs (keep current)
rm -f /var/log/syslog.1 /var/log/syslog.2.gz /var/log/syslog.3.gz /var/log/syslog.4.gz
rm -f /var/log/kern.log.1 /var/log/kern.log.2.gz /var/log/kern.log.3.gz /var/log/kern.log.4.gz
rm -f /var/log/dmesg.0 /var/log/dmesg.1.gz /var/log/dmesg.2.gz /var/log/dmesg.3.gz /var/log/dmesg.4.gz
```

### Step 3: Clean Caches
```bash
npm cache clean --force
pip cache purge
apt-get clean
```

### Step 4: Prune Docker
```bash
docker system prune -f
```

### Step 5: Clean Temp Files
```bash
rm -rf /tmp/*.mp4 /tmp/*.zip /tmp/node-* /tmp/kage-*
```

### Typical Recovery
| Source | Typical Size | 
|--------|-------------|
| Old syslog/journal | ~2GB |
| npm cache | ~2GB |
| pip cache | ~700MB |
| Docker unused images | ~10GB |
| Temp files | ~600MB |
| **Total recovered** | **~13-15GB** |

### Prevention
Set up a weekly cron for log cleanup:
```bash
# /etc/cron.weekly/clean-logs
#!/bin/bash
journalctl --vacuum-size=500M
find /var/log -name '*.gz' -mtime +7 -delete
find /var/log -name '*.1' -mtime +7 -delete
```

### Pitfalls
- **Don't delete current logs** — only rotated archives (`.1`, `.gz`). Current `syslog`, `kern.log`, `dmesg` are active.
- **Docker prune removes unused images** — running containers are unaffected. Safe to run anytime.
- **npm cache clean --force** is safe — it only removes cached packages, not installed ones.
- **Journal vacuum is safe** — it removes old archived journals, not current ones. The `--vacuum-size` flag keeps only the most recent entries up to that size.

## References

- `references/demo-suite-structure.md` — Full demo hub architecture and card patterns
- `references/site-content-architecture.md` — What belongs on the main domain vs subdomains. Read before deploying anything new.
- `references/github-pages-workflow-pitfalls.md` — Pages deploy workflow pitfalls + the Aug 30 repo-rename provision-limbo and VPS-mirror fix.
- `references/resume-hosting-pattern.md` — Always-current résumé/CV: vault source-of-truth → self-hosted URL → portfolio repo → Pages mirror, plus the 6-hour Resume Sync cron and content QA rules.
- `references/market-analysis-pattern.md` — Dynamic market analysis section for data dashboards. Three-state oversold/neutral/overbought analysis with recovery signals, user advice, 4-year cycle timing context, and dry powder (USDC/USDT market cap) tracking pattern.
- `references/game-loadout-tracker-pattern.md` — Reusable per-game build/loadout tracker (POE2, Helldivers 2): JSON schema, themed page, hub wiring, growth loop, verify checklist.
- `scripts/backup-webroot-push.sh` — Chunked webroot backup pusher (≤250MB commits, SHA-verified per push) for the backup pitfall above.
