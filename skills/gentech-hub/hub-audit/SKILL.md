---
name: hub-audit
description: "Audit GenTech hubs for stale data, broken HTML, and live data issues. Prevents GitHub Pages build failures and ensures dashboards stay fresh."
version: 1.7.0
author: gentech
tags: [gentech, hub, audit, dashboard, github-pages, html, validation]
---

# Hub Audit — Validate GenTech Hubs

**Purpose:** Audit all GenTech hubs (Jordan's and Vanito's) for data freshness, HTML integrity, and live data connectivity. Catches issues before they break pages.

## The Problem

- **Static hubs go stale** — No live data feeds, hardcoded HTML only
- **Broken HTML** — Unclosed tags, truncated JavaScript cause build failures
- **Missing data files** — Hub references JSON that doesn't exist
- **GitHub Pages failures** — "Build failed" emails from broken syntax
- **Stale timestamps** — Data never updates, shows old prices/stats

## The Solution

Systematic audit of all hub files:
1. Tag balance check (div, script, other elements)
2. Data source detection (fetch vs hardcoded)
3. Timestamp verification (lastUpdated fields)
4. External URL validation (404s, CORS)
5. File modification date review

## Audit Workflow

### Step 1: Find All Hubs

```bash
# Find HTML hub files (VPS deployment)
ls -la /var/www/gentechlabs/*.html
# Find hub data files
ls -la /var/www/gentechlabs/hub-vanita-data.json 2>/dev/null
```

**Expected files (VPS — deployed at `/var/www/gentechlabs/`):**
- `/var/www/gentechlabs/hub.html` — Main landing page
- `/var/www/gentechlabs/jordan.html` — Jordan's hub
- `/var/www/gentechlabs/vanito.html` — Vanito's hub (served at vanito.gentechlabs.net)
- `/var/www/gentechlabs/hub/data/` — Legacy hub system per-person JSON
- `/var/www/gentechlabs/hub-vanito-data.json` — JS-fetched data for vanito.html music tab

### Step 2: Check Tag Balance + File Permissions

```bash
# Check div tags (must be balanced)
grep -c '<div' /var/www/gentechlabs/vanito.html
grep -c '</div>' /var/www/gentechlabs/vanito.html

# Check script tags
grep -c '<script' /var/www/gentechlabs/vanito.html
grep -c '</script>' /var/www/gentechlabs/vanito.html

# Check fetch() calls (live data vs static)
grep -n 'fetch(' /var/www/gentechlabs/vanito.html

# ⚠️ CRITICAL: Check data file permissions
# Files created as root default to 600 — nginx reads as www-data
# A 403 Forbidden on a data file looks identical to a 404 to JS
for f in /var/www/gentechlabs/*.json /var/www/gentechlabs/hub/*.json; do
  [ -f "$f" ] && ls -la "$f" | awk '{print $1, $NF}'
done
# Expected: -rw-r--r-- (644) for all data files
```

**If unbalanced:** HTML syntax error → GitHub Pages will fail.

### Step 3: Detect Data Sources

```bash
# Search for fetch() calls (live data)
grep -n 'fetch(' /var/www/gentechlabs/vanito.html

# Check JS for expected data JSON
grep -n "\.json'" /var/www/gentechlabs/vanito.html
```

**Classification:**
- ✅ **Live hub** — Has `fetch()` + `cache: 'no-store'`
- ⚠️ **Static hub** — No fetch calls, hardcoded only

### Step 4: Verify Data Freshness

```bash
# Fetch live data file and check timestamp
curl -s https://raw.githubusercontent.com/.../data.json | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('lastUpdated', 'NO TIMESTAMP'))"
```

**Freshness check:**
- ✅ Timestamp from today → fresh
- ⚠️ Timestamp > 7 days old → stale
- ❌ No timestamp field → unknown (may never update)

### Step 5: Test External URLs

```bash
# Check if data URLs return 200
curl -I https://api.dexscreener.com/...

# Check CORS errors
curl -s -H "Origin: https://gentechlabs.net" https://api.dexscreener.com/...
```

**If 404/CORS:** Data fetch will fail, dashboard shows nothing.

### Step 6: Check File Modifications

```bash
ls -lh /var/www/gentechlabs/hub*.html /var/www/gentechlabs/jordan.html /var/www/gentechlabs/vanito.html
```

**Recent = good:** Modified within last 30 days means active maintenance.

### Step 7: Check GitHub Actions Build Status

After deploying a hub update, verify GitHub Pages actually rebuilt:

```
GH_TOKEN=$(gh auth token 2>/dev/null)
curl -s -H "Authorization: token $GH_TOKEN" \
  "https://api.github.com/repos/ProtoJay4789/ProtoJay4789.github.io/actions/runs?per_page=3&event=push" | \
  python3 -c "
import sys, json
d = json.load(sys.stdin)
for r in d.get('workflow_runs', []):
    print(f\"{r['head_commit']['message'][:50]:50s} {r['status']:12s}\")
"
```

If the most recent commit's status is `completed` + `success`, Pages is up to date.
If `in_progress` or `pending`, wait and re-check.
If `cancelled`, a newer commit superseded it — check the next one.

## Common Issues

### Issue 0: GitHub Merge Conflicts in JSON Data Files

**Symptom:** Hub fails to load, console shows "JSON.parse error" or "Unexpected token <".

**Detection:**
```bash
# Check for merge conflict markers (specific file)
grep -n "<<<<<<< Updated upstream" DeFi/defi-data.json

# Check ALL JSON files in the repo for markers (catches cross-contamination)
find . -name '*.json' -exec sh -c 'c=$(grep -c "<<<<<<< \|=======\|>>>>>>>" "$1" 2>/dev/null); [ "$c" -gt 0 ] && echo "🔴 $1 ($c markers)"' _ {} \;

# Verify JSON is valid
curl -s "https://raw.githubusercontent.com/.../defi-data.json" | python3 -m json.tool
# If error: Expecting value: line 1 column 1 (char 0) → file is corrupted
```

**Root Cause:** Git merge/rebase on another machine left unresolved conflicts pushed to `origin/main`.

**Two Cases:**

**Case A — Clean commit exists on remote:** The corrupted file is one of several commits. Restore from the last clean commit.
```
1. git log --oneline -135 | grep -v "auto: on-chain position update" | head -5
2. git reset --hard e363dc89
3. git show e363dc89:DeFi/defi-data.json > DeFi/defi-data.json
4. git push origin main --force-with-lease
```

**Case B — Remote HEAD is the corrupted commit:** No clean commit to restore from. Use a clean local copy (vault) as source of truth.
```
1. git fetch origin
2. git reset --hard origin/main            # Match remote exactly
3. cp /root/vaults/gentech/defi-data.json DeFi/defi-data.json  # Vault is clean
4. python3 -m json.tool DeFi/defi-data.json  # Verify valid
5. git commit -m "fix: Repair defi-data.json (N merge conflict markers)"
6. git push origin main
```

**Real-world case (Jul 12, 2026):** POE2 build sync pushed defi-data.json with 57 merge conflict markers to origin/main. Hub Nightly Sync diverged locally and could not rebase. Used Case B: reset to origin/main, restore from vault, commit repair, push. Replaced 456 corrupted lines with 20 clean lines.

**Verification after fix:**
```bash
curl -s "https://raw.githubusercontent.com/ProtoJay4789/ProtoJay4789.github.io/main/DeFi/defi-data.json" | python3 -m json.tool > /dev/null && echo "VALID" || echo "CORRUPTED"
```

**Prevention:** Add a post-rebase conflict marker scan to the sync script's push pipeline (see `cron-truth-layer` Anti-Pattern 9 — Sequence Vulnerability). The `sanitize_json_text()` function auto-strips markers before they reach the remote.

**Reference:** `references/github-merge-conflict-resolution.md` — Complete resolution guide and prevention tips.

### Issue 1: Missing Hub Data Files

**Symptom:** Dashboard shows "Failed to load data" or empty sections. Console shows 404 error for data file.

**Detection:**
```bash
# Check if data file exists on GitHub
curl -I "https://raw.githubusercontent.com/.../hub-vanito-data.json"
# Output: HTTP/1.1 404 Not Found
```

**Root Cause:** Hub HTML references JSON data file that was never created or pushed to GitHub.

**Fix:**
1. Create placeholder JSON file with minimal structure (lastUpdated, name, avatar, tagline, status, projects[], stats{})
2. Commit and push to GitHub: `git add hub-vanito-data.json && git commit -m "feat: Add placeholder data file" && git push origin main`
3. Verify file is accessible: `curl -s "https://raw.githubusercontent.com/.../hub-vanito-data.json" | python3 -m json.tool`

**Template:**
```json
{
  "lastUpdated": "2026-07-01T16:30:00.000Z",
  "name": "Vanito",
  "avatar": "Vanito",
  "tagline": "PoE2 Warrior",
  "steamId": "76561198132811363",
  "status": "Active",
  "projects": [],
  "stats": { "level": 0, "builds": 0, "gold": 0 }
}
```

**Reference:** `references/missing-hub-data-files.md` — Complete creation guide and templates.

### Issue 2: Static Hub (No Live Data)

**Symptom:** Hub shows static values, never updates.

**Detection:** No `fetch()` calls, no `DATA_URL` constant.

**Fix:**
1. Create JSON data file with timestamps
2. Add `fetch()` with cache-busting
3. Use `cache: 'no-store'` option

**Example:**
```html
<script>
const DATA_URL = 'https://raw.githubusercontent.com/.../data.json';

async function loadData() {
    const resp = await fetch(DATA_URL + '?' + Date.now(), { cache: 'no-store' });
    const data = await resp.json();
    // render data
}
</script>
```

### Issue 8: Missing Data File Causes JS JSON Parse Error (Not Direct 404)

**Symptom:** Feature tab shows "Error loading [feature]" but page itself loads fine. Browser console shows `SyntaxError: Unexpected token '<', "<html>... is not valid JSON`. No 404 visible to the user.

**Root cause:** JS `fetch('data.json')` resolves to a URL where the file doesn't exist. Nginx returns a 404 HTML page. The fetch promise resolves successfully (connection worked), but `response.json()` fails because the body is HTML, not JSON. The catch block renders the generic error message — the 404 is hidden from the user.

**Diagnosis chain:**
```bash
# 1. Does the file exist on the server?
ls -la /var/www/gentechlabs/hub-vanito-data.json

# 2. What content-type is nginx returning?
curl -sI "https://vanito.gentechlabs.net/hub-vanito-data.json" | grep -i content-type
# text/html = 404 error page. application/json = correct.

# 3. Check nginx access log for the actual HTTP status
tail -n 20 /var/log/nginx/*.access.log 2>/dev/null | grep "data.json"
```

**Fix — Two parts:**

**Part A — Create the data file** with valid JSON matching the JS expected schema (check `fetch()` call in the HTML for the expected structure).

**Part B — Fix file permissions** — files created as root default to 600, but nginx reads as www-data:
```bash
chmod 644 /var/www/gentechlabs/hub-vanito-data.json
chown www-data:www-data /var/www/gentechlabs/hub-vanito-data.json
```

**Verification:** `curl -s "https://example.com/data.json" | python3 -m json.tool` should return valid JSON with `content-type: application/json`.

**Prevention:** Any data file served by nginx must be 644 + www-data. After creating, always check content-type header before assuming the file is accessible.

**Real-world case (Jul 25, 2026):** Vanito's hub music tab showed "Error loading music". The JS fetched `hub-vanito-data.json` which didn't exist on the VPS. Fixed by creating the file and setting correct permissions.

### Issue 9: Unclosed HTML Tags

**Symptom:** GitHub Pages build fails with "Unclosed tag" error.

**Detection:** Unbalanced div/script tags.

**Fix:** Add missing closing tags. Use `grep` to find where the opening tag has no closing match.

### Issue 10: Data Pushed to Pages Repo But VPS Webroot Never Updated (NEW — Sep 3, 2026)

**Symptom:** Sync pipeline reports success (repo commit + push all green), raw.githubusercontent.com serves fresh data, but the LIVE site (`gentechlabs.net/defi-data.json`) still serves weeks-old data.

**Root cause:** `gentechlabs.net` and `vanito.gentechlabs.net` are served by **nginx on the VPS from a plain webroot** (`/var/www/gentechlabs/`) — NOT from a git checkout, NOT from GitHub Pages. Pushing to the Pages repo only updates GitHub; nothing copies the fresh JSON into the webroot. The pipeline was verifying the wrong target.

**Deployment topology (three targets, verify the SERVING one):**
```
vault source → Pages repo (github) → [NOT SERVING for gentechlabs.net]
                                  └→ VPS webroot /var/www/gentechlabs/ ← nginx serves THIS
```

**Detection:**
```bash
# Compare webroot vs repo copy directly:
diff <(python3 -c "import json; print(json.load(open('/var/www/gentechlabs/defi-data.json'))['lastUpdated'])") \
     <(python3 -c "import json; print(json.load(open('/root/ProtoJay4789.github.io/DeFi/defi-data.json'))['lastUpdated'])")
# Also confirm the webroot is NOT a git checkout:
cd /var/www/gentechlabs && git rev-parse --is-inside-work-tree 2>/dev/null || echo "plain webroot — push does NOT update it"
```

**Fix — add a webroot deploy step after the push step:**
```python
# Step 5.5: Deploy to VPS webroot (nginx serves /var/www/gentechlabs)
import shutil
shutil.copy2(f"{REPO_PATH}/DeFi/defi-data.json", "/var/www/gentechlabs/defi-data.json")
os.chmod("/var/www/gentechlabs/defi-data.json", 0o644)
```

**Real-world case (Sep 3, 2026):** defi-data.json served Aug 11 data on Sep 3 (23 days stale) despite the sync script "working" — the script pushed to the Pages repo but never touched `/var/www/gentechlabs/`. Fixed by adding the webroot copy step; live site verified fresh within one run. Note: the Pages repo's remote already points at GentechLabs (`gentechlabs.github.io`) — the legacy folder name `/root/ProtoJay4789.github.io` is just a local directory name, not the deploy target.

**Lesson: an audit must trace data to the SERVING target.** A pipeline can be green end-to-end (vault fresh, repo pushed, CDN reachable) while the user sees stale data. Always finish with: fetch the live URL a real browser would hit and compare `lastUpdated` against the source.

### Issue 3: Broken Data URL

**Symptom:** Dashboard shows "Failed to load data" or empty sections.

**Detection:** `curl -I` returns 404, or browser console shows CORS error.

**Fix:**
- Correct the URL path
- Add CORS headers if using custom API
- Use `no-cache` query string to bypass CDN caching

### Issue 4: Stale Timestamp

**Symptom:** Dashboard shows prices from weeks ago.

**Detection:** `lastUpdated` field is old or missing.

**Fix:**
- Update data pipeline to write current timestamp
- Add cron job to refresh data daily
- Add age indicator on dashboard (e.g., "Updated 2h ago")

### Issue 5: Live Verification False Failure (SHA-Specific URL)

**Symptom:** Hub sync script reports "Live verification: HTTP 404" for a defi-data.json URL, but the data file is valid and GitHub Pages responds 200.

**Root cause:** The verification function used the local `git rev-parse HEAD` SHA to build a `raw.githubusercontent.com/{sha}/path` URL. If the local commit was never pushed (push failed, rebase conflict), the SHA doesn't exist on GitHub → 404. The function reported this as a data issue when it was actually a deployment gap.

**Fix — Fallback URL chain:** Try the SHA-specific URL first (cache-busting), then fall back to the `main` branch ref. This way a failed push doesn't cascade into a false 404 alarm.

```python
def verify_live():
    """Verify with URL fallback chain."""
    # 1. Try SHA-specific URL (cache-busting, accurate for just-pushed commits)
    sha = subprocess.run(["git", "rev-parse", "HEAD"], ...).stdout.strip()
    if sha:
        urls_to_try.append(
            f"https://raw.githubusercontent.com/user/repo/{sha}/path/data.json"
        )
    # 2. Fall back to stable branch ref
    urls_to_try.append(
        "https://raw.githubusercontent.com/user/repo/main/path/data.json"
    )

    for url in urls_to_try:
        try:
            req = urllib.request.Request(url)
            resp = urllib.request.urlopen(req, timeout=10)
            data = json.loads(resp.read())
            # Validate required sections...
            if all_sections_present:
                return True, []
            return False, missing
        except Exception:
            continue
    return False, ["All verification URLs failed"]
```

**Why not just use `main` always:** SHA-specific URLs bypass CDN caches — important for verifying fresh pushes. The fallback ensures the verification still works when the SHA URL fails.

**Real-world case (Jul 12, 2026):** hub-sync-nightly.py used only SHA-specific URL. When git push failed (divergent remote with 26 commits), `verify_live()` returned 404 for the unpushed SHA. Fixed by adding `main` branch fallback.

### Issue 6: Deployed Content Stale on GitHub Pages (CDN Cache)

**Symptom:** New content confirmed via raw.githubusercontent.com or Git blob API, but GitHub Pages still shows old version.

**Root cause:** Pages uses CDN caching (2-5 min typical) + GitHub Actions build queue.

**Diagnosis:**
1. Check blob content (definitive, no cache): `curl -s -H "Authorization: token $GH_TOKEN" "https://api.github.com/repos/ProtoJay4789/ProtoJay4789.github.io/git/blobs/<SHA>" | python3 -c "import sys,json,base64; d=json.load(sys.stdin); print(base64.b64decode(d['content']).decode()[:200])"`
2. Check Actions build status (see Step 7 above)
3. If build completed successfully but Pages still stale → CDN propagation (wait 2-5 min)

**Prevention in hub dashboards:** Add a `lastUpdated` timestamp rendered from the JSON data file rather than relying on the page serving timestamp. Users see when data was refreshed, not when the page was deployed.

### Issue 7: raw.githubusercontent.com Returns 404 for main Branch (CDN Gap)

**Symptom:** `curl -I "https://raw.githubusercontent.com/owner/repo/main/path/file.json"` returns HTTP 404, but the file is confirmed valid via the GitHub API and the Actions build completed successfully.

**Root cause:** `raw.githubusercontent.com` is a separate CDN from the GitHub API and GitHub Pages. It can return 404 for files that exist on the `main` branch when:
- The CDN edge node hasn't picked up the latest commit (cache propagation delay)
- The file path is case-sensitive and doesn't match (e.g., `DeFi/` vs `defi/`)
- The raw CDN has a transient outage for a specific repo/branch combination

**Real-world case (Jul 21, 2026):** Hub Nightly Sync pushed `DeFi/defi-data.json` to `ProtoJay4789.github.io` (commit `370e3248`, valid JSON, 15/15 sections, Actions build completed with `success`). But `raw.githubusercontent.com/ProtoJay4789/ProtoJay4789.github.io/main/DeFi/defi-data.json` returned 404. The GitHub API confirmed the blob was valid (13,595 bytes, all sections present). The raw CDN was simply not serving the file.

**Diagnosis — Three-layer verification chain:**

```bash
# Layer 1: raw.githubusercontent.com (fastest, but unreliable)
curl -sI "https://raw.githubusercontent.com/owner/repo/main/path/file.json"
# -> 404 does NOT mean the file is missing

# Layer 2: GitHub API blob content (definitive, no cache)
GH_TOKEN=$(cat /path/to/token)
curl -s -H "Authorization: token $GH_TOKEN" \
  "https://api.github.com/repos/owner/repo/contents/path/file.json?ref=main" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Size: {d.get(\"size\")}, SHA: {d.get(\"sha\")[:12]}')"
# -> If this returns valid data, the file IS on GitHub

# Layer 3: GitHub Actions build status (confirms deploy ran)
curl -s -H "Authorization: token $GH_TOKEN" \
  "https://api.github.com/repos/owner/repo/actions/runs?per_page=3&event=push" \
  | python3 -c "
import sys, json
d = json.load(sys.stdin)
for r in d.get('workflow_runs', []):
    msg = r.get('head_commit', {}).get('message', '?')[:60]
    print(f'{msg:60s} {r[\"status\"]:12s} {r[\"conclusion\"] or \"-\":12s}')
"
# -> If latest commit shows completed + success, data is deployed
```

**Fix — Use GitHub API as authoritative source, not raw CDN:**

When verifying data after a push, use this priority:
1. **GitHub API blob content** (definitive, no cache) — check file exists and is valid JSON
2. **GitHub Actions build status** — confirm deploy ran for the expected commit
3. **raw.githubusercontent.com** — best-effort, treat 404 as "CDN not propagated" not "data missing"

```python
def verify_data_on_github(repo_owner, repo_name, path, token):
    """Verify data exists on GitHub via API (not raw CDN)."""
    import urllib.request, json

    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{path}?ref=main"
    req = urllib.request.Request(url, headers={
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    })
    resp = urllib.request.urlopen(req, timeout=10)
    data = json.loads(resp.read().decode())

    # Decode base64 content and validate JSON
    import base64
    content = base64.b64decode(data["content"]).decode()
    parsed = json.loads(content)
    return parsed, data["sha"]
```

**Key insight:** `raw.githubusercontent.com` 404 is NOT evidence of a data problem. It is a CDN propagation issue. The GitHub API is the authoritative source. Always use the API for verification, not the raw CDN.

**Prevention in hub sync scripts:** Add a GitHub API verification step as the primary check, with raw CDN as a best-effort secondary. Never report "data missing" based on raw CDN 404 alone.

## Audit Report Template

```markdown
# Hub Audit Report — $(date)

| Hub | File | Last Modified | Data Status | Issues |
|-----|------|---------------|-------------|--------|
| Landing | hub.html | $(date) | ✅ STATIC | Links to Jordan, Vanito, Portfolio |
| Jordan | jordan.html | $(date) | ✅ STATIC | 4 tabs, no data fetches |
| Vanito | vanito.html | $(date) | ✅ LIVE | Music data: hub-vanito-data.json |

## Deployment Verification

- [ ] Raw content accessible via raw.githubusercontent.com
- [ ] Git blob content matches expected
- [ ] GitHub Actions build completed with `success`
- [ ] GitHub Pages serves correct content (after CDN propagation)
- [ ] VPS webroot copy (`/var/www/gentechlabs/*.json`) matches the repo copy — nginx serves the webroot, not GitHub (Issue 10)
- [ ] LIVE URL fetched (not pipeline output) and `lastUpdated` is fresh

## Issues Found

### Student Hub — Archived (first student departed Aug 2026)
- **Status:** ARCHIVED — first student departed Aug 2026; template removed. Method kept in 10-Labs/academy-playbook/orchestrator-playbook-distilled.md

## Recommendations

1. Deploy a student hub only when Jordan greenlights a new student
2. Add lastUpdated timestamps to all data files
3. Test data URLs weekly
```

## Pitfalls

### Don't Assume No News Is Good News
Just because the hub loads in browser doesn't mean it's correct. Check the actual data values and timestamps.

### GitHub Pages Cache Can Mislead
Adding `?Date.now()` isn't always enough. Use `cache: 'no-store'` option in fetch.

### Compression Can Timeout Long Sessions
This session used `/compress` which timed out due to context length. Not critical — just cleanup. Don't retry if not needed.

### MiMo-v2.5 Leaves Broken HTML
MiMo hits timeouts on long builds and leaves incomplete code. Use GLM-5.2 for all HTML/dashboard work to get complete patches.

### Stale Data With Zero Errors = Check the Producer Cron EXISTS
A data file weeks stale with NO failure logs usually means the sync script lost its cron job (consolidation drops orphaned jobs silently) — not that the script is broken. Check `hermes cron list | grep <script-name>` FIRST; a script with zero jobs runs never. Proven Sep 3, 2026: hub-sync-nightly.py had no job AND a rebase-cascade bug; re-wired as `22b2467ded55` (22:10 UTC nightly, no-agent) with `--failure-deliver telegram` so future breaks alert the principal instead of dying silently. While there, prefer merge `--strategy-option theirs` over rebase for fully-regenerated files (see cron-truth-layer Anti-Pattern 11).

### One Failed Probe ≠ Down (Cloudflare/IPv6 Flap)
A single curl returning 000/timeout can be a transient edge/IPv6 flap — the same URL connected fine over IPv6 seconds later (200 in 70ms). Before declaring a subdomain down: retest http AND https, and confirm the vhost exists in `nginx -T` server_name output. Escalate only on repeated failures.

## Integration with Gentech Ops

Run hub audit weekly as a cron job:

```bash
# cron: hub-audit-weekly.sh
# Runs every Sunday at 10 AM

echo "Hub Audit Report - $(date)" > /tmp/hub-audit-report.md

# Run all checks on VPS hub files
for hub in hub.html jordan.html vanito.html; do
    echo "Checking $hub" >> /tmp/hub-audit-report.md
    bash /root/.hermes/profiles/gentech/skills/gentech-hub/hub-audit/scripts/check-hub-tags.sh "/var/www/gentechlabs/$hub" >> /tmp/hub-audit-report.md 2>/dev/null || echo "Tag check skipped" >> /tmp/hub-audit-report.md
    bash /root/.hermes/profiles/gentech/skills/gentech-hub/hub-audit/scripts/check-hub-data.sh "/var/www/gentechlabs/$hub" >> /tmp/hub-audit-report.md 2>/dev/null || echo "Data check skipped" >> /tmp/hub-audit-report.md
done

# Check data file permissions
ls -la /var/www/gentechlabs/hub-vanita-data.json >> /tmp/hub-audit-report.md 2>/dev/null || echo "hub-vanita-data.json: MISSING" >> /tmp/hub-audit-report.md

mv /tmp/hub-audit-report.md /root/vaults/gentech/11-Mess Hall/hub-audit-$(date +%Y%m%d).md
```

## Linked Files

**Scripts:**
- `scripts/check-hub-tags.sh` — Automated tag balance verification
- `scripts/check-hub-data.sh` — Data source validation and URL testing

**References:**
- `references/github-pages-build-errors.md` — Common build failure patterns
- `references/github-merge-conflict-resolution.md` — How to fix merge conflicts in JSON data files on GitHub
- `references/missing-hub-data-files.md` — Creating placeholder data files for new hubs
- `references/personal-hub-link-pattern.md` — Link pattern for personal hubs (Christel, Vanito, others). Always use deployed GitHub Pages URLs, not raw GitHub markdown files.

Use these scripts for automated audits and quick checks.

## References

- `references/github-pages-build-errors.md` — Common build failure patterns
- `scripts/check-hub-tags.sh` — Tag balance verification script
- `scripts/check-hub-data.sh` — Data source validation script

## Version History

- **1.7.0** (Sep 3, 2026) — Added pitfalls: stale-data-with-zero-errors → check producer cron exists (orphaned sync script pattern); single-probe flap ≠ down (IPv6/Cloudflare transient).
- **1.6.0** (Sep 3, 2026) — Added Issue 10 (webroot deploy gap: nginx webroot ≠ Pages repo; verify the SERVING target). Deployment Verification checklist extended.
- **1.5.1** (Jul 25, 2026) — Updated hub inventory: Christel removed, Academy student template added.
- **1.4.0** (Jul 21, 2026) — Added Issue 7 (raw.githubusercontent.com 404 CDN gap). Three-layer verification chain: GitHub API blob content (authoritative) > Actions build status > raw CDN (best-effort).
- **1.1.0** (July 1, 2026) — Added Issue 0 (merge conflict resolution) and Issue 1 (missing data files). Added reference docs for both issues.
- **1.0.0** (June 26, 2026) — Initial release. 3 hubs audited, static hubs identified.

---

*"Tough love for the agent economy."*