---
name: portfolio-deployment
description: Deploy content from vault to ProtoJay4789.github.io portfolio website
---

# Portfolio Deployment Workflow

## 🔄 UPDATE Aug 30, 2026 — work moved to the gentechlabs org; GitHub Pages WORKS there

**Everything below the Aug 3 divider is personal-account (ProtoJay4789) history — still true for that account, no longer the deploy reality.** Current state:

- **Portfolio repo:** `gentechlabs/gentechlabs.github.io` (renamed via API from `gentechlabs/ProtoJay4789.github.io`, Aug 30). Org Pages serves from a repo named `<org>.github.io` — the rename is what made Pages work again.
- **Local source clone:** `/root/repos/ProtoJay4789.github.io` (branch `gh-pages`, remote has embedded token) — this is the push target for site changes.
- **Deploy:** commit + push to `gh-pages` → verify `curl -sL https://gentechlabs.github.io/ | grep -oE '<title>[^<]+'`.
- **Live URLs:** portfolio = https://gentechlabs.github.io · résumé = https://gentechlabs.net/resume.pdf (+ `/resume.html` on VPS `/var/www/gentechlabs/`).
- **Resume/CV always-current:** vault source `10-Labs/Resumes/Jordan_Master_Resume.{md,html,pdf}`; 6-hour **Resume Sync** cron (job `877b19f24f9f`) diffs vault → VPS → portfolio repo, Monday content check flags staleness. Jordan's rule: master resume always hosted + always updated.
- **gitignore gotcha:** portfolio repo denies `**/*.pdf` — force-add binaries: `git add -f resume.pdf`.
- **⏳ GitHub rename-limbo (open as of Aug 30):** after the repo rename, root page serves from cache but newly pushed files 404; Pages API shows "already enabled" (409) + empty build history + 403 on build trigger. GitHub finishes provisioning eventually (hours). Fallback while limbo persists: self-host on VPS (gentechlabs.net) and point site links there. Details in `github-repo-migration` skill.
- **Dead URLs — never print or link:** `protojay4789.github.io`, `github.com/ProtoJay4789` (for work links).

## ⚠️ HISTORICAL (Aug 3, 2026): personal-account Pages block — VPS was then the only target

**GitHub Pages is permanently broken for ProtoJay4789 (personal account).** The account has an infrastructure-level restriction that prevents Pages from ever deploying — 0 builds in history, Actions disabled at account level, the settings option removed from the UI. **Do NOT attempt to fix GitHub Pages.** The VPS is the permanent home.

**Confirmed Aug 3, 2026:** Even switching to legacy `gh-pages` branch mode and pushing a trigger commit does NOT deploy — the Pages build queue shows 0 builds ever. `POST /pages/builds` returns "queued" but the build never executes. The account is flagged at the infrastructure level. The VPS at `portfolio.gentechlabs.net` is the only working deployment target.

### Live Portfolio

- **URL:** `https://portfolio.gentechlabs.net/` (HTTPS, Let's Encrypt cert)
- **Also at:** `https://gentechlabs.net/portfolio/` (nginx alias)
- **Server path:** `/var/www/portfolio/index.html` on `root@2.24.195.196`
- **DNS:** `portfolio.gentechlabs.net` → `2.24.195.196` (Cloudflare DNS-only, gray cloud)

### Deploy Command

```bash
# 1. Get latest from gh-pages branch (authenticated)
TOKEN=$(grep 'oauth_token:' /root/.hermes/profiles/gentech/home/.config/gh/hosts.yml | head -1 | awk '{print $2}' | tr -d '"')
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://raw.githubusercontent.com/ProtoJay4789/ProtoJay4789.github.io/gh-pages/index.html" \
  > /tmp/portfolio-latest.html

# 2. Push to VPS
scp -o StrictHostKeyChecking=no /tmp/portfolio-latest.html root@2.24.195.196:/var/www/portfolio/index.html

# 3. Verify
curl -s http://portfolio.gentechlabs.net/ | grep -c "x402"
curl -sk https://portfolio.gentechlabs.net/ | grep -c "x402"
```

### Backup Pattern

Before overwriting on VPS, SSH in and backup:
```bash
ssh root@2.24.195.196 "cp /var/www/portfolio/index.html /var/www/portfolio/index.html.bak$(date +%s)"
```

### GitHub Repo Status

The repo at `/root/repos/ProtoJay4789.github.io/` is a **secondary mirror only** — it holds the source but cannot deploy. The `gh-pages` branch has correct content (verified via authenticated raw.githubusercontent.com), but GitHub will never serve it. The old vault path `/root/vaults/gentech/github/ProtoJay4789.github.io/` no longer exists.

### Full Diagnosis Reference

See `references/account-level-pages-block-diagnosis.md` for the complete diagnostic sequence, symptoms, and what does/doesn't work.

---

Deploy content from vault (`/root/vaults/gentech/`) to portfolio website (`/root/vaults/gentech/github/ProtoJay4789.github.io/`).

---

## Trigger Conditions

When the user asks to:
- "Ship" or "deploy" content to the portfolio
- "Add to the portfolio site"
- "Update the portfolio"
- "Deploy [content] to portfolio"

---

## Portfolio Site Structure

**Key file:** `index.html` (main portfolio page)

**Sections:** (in order, with `id=` attributes)
- `sec-about` - About section
- `sec-journey` - Journey section
- `sec-projects` - Projects section
- `sec-stack` - AAE Stack section
- `sec-apis` - API Services section
- `sec-casestudies` - Case Studies section

**Navigation requires updates in 4 places when adding a section:**
1. Bottom nav bar (around line 1350) - adds a nav button
2. Settings modal options (around line 850) - adds a settings option
3. Section mapping in JS (around line 1364) - adds to `map` object
4. Scroll spy array in JS (around line 1378) - adds to `sections` array

---

## Deploying Standalone Pages to Subdirectories

Not all deployments modify `index.html`. Sometimes you deploy a new standalone page to a subdirectory (e.g., `DeFi/defi-dashboard.html`).

### Correct File Path

The portfolio repo root is at:
`/root/vaults/gentech/github/ProtoJay4789.github.io/`

A file at `repo-root/DeFi/defi-dashboard.html` in the tree must be written to:
- `/root/vaults/gentech/github/ProtoJay4789.github.io/DeFi/defi-dashboard.html`

**Do NOT write from the vault root** (e.g., `/root/vaults/gentech/DeFi/defi-dashboard.html`) — git will see the file at path `github/ProtoJay4789.github.io/DeFi/defi-dashboard.html` which GitHub Pages will not serve.

### Verify Correct Path After Adding

```bash
cd /root/vaults/gentech/github/ProtoJay4789.github.io
git ls-tree HEAD DeFi/defi-dashboard.html
# Expected: DeFi/defi-dashboard.html
# Wrong:    github/ProtoJay4789.github.io/DeFi/defi-dashboard.html
```

### Fallback: GitHub API When Git Push Is Blocked

The vault's working tree (untracked files from ongoing sessions) frequently blocks `git checkout`, `git stash`, and `git pull`. When standard git deployment fails:

**For existing files (update):**
```bash
GH_TOKEN=$(gh auth token 2>/dev/null)
# Get current SHA
SHA=$(curl -s -H "Authorization: token $GH_TOKEN" \
  "https://api.github.com/repos/ProtoJay4789/ProtoJay4789.github.io/contents/DeFi/file.html" | \
  python3 -c "import sys,json; print(json.load(sys.stdin)['sha'])")
# Base64 encode new content
B64=$(base64 -w0 /path/to/new/file.html)
# Update via PUT
curl -s -X PUT -H "Authorization: token $GH_TOKEN" -H "Content-Type: application/json" \
  -d "$(python3 -c "import json; print(json.dumps({'message':'Update file','content':'$B64','sha':'$SHA'}))")" \
  "https://api.github.com/repos/ProtoJay4789/ProtoJay4789.github.io/contents/DeFi/file.html"
```

**For new files:** Omit `sha` from the JSON payload.

### CDN Propagation

After deployment:
- **raw.githubusercontent.com** updates within ~30s (CDN cache: 5 min max-age)
- **GitHub Pages CDN** (protojay4789.github.io) takes 2-5 min to rebuild and flush cache
- **Git blob API** is the only uncached definitive source

### Build Type: "workflow" vs Default

This repo uses **"workflow" build type** (GitHub Actions), NOT the default Pages builder. This means:

1. **You CANNOT trigger a manual rebuild** via `POST /pages/builds` — the API returns 403 "The repository does not have a GitHub Pages site" even though Pages IS configured
2. **You MUST push a commit** (even empty with `--allow-empty`) to trigger a rebuild
3. The API-based file update (PUT `/contents/path`) creates a commit and DOES trigger an Actions run automatically

### Checking Build Progress

After deployment, check GitHub Actions for build status:

```
GH_TOKEN=$(gh auth token 2>/dev/null)
curl -s -H "Authorization: token $GH_TOKEN" \
  "https://api.github.com/repos/ProtoJay4789/ProtoJay4789.github.io/actions/runs?per_page=3&event=push" | \
  python3 -c "
import sys, json
d = json.load(sys.stdin)
for r in d.get('workflow_runs', []):
    print(f\"{r['head_commit']['message'][:50]:50s} {r['status']:12s} {r['conclusion'] or '...':10s}\")
"
```

Status: `completed` = done, `in_progress` = building, `pending` = queued.
Conclusion: `success` = deployed, `cancelled` = superseded, `failure` = build broke.

### Verifying Deployed Content (Four Levels)

**Level 1 — Git tree (file at correct repo-relative path):**
```
cd /root/vaults/gentech/github/ProtoJay4789.github.io
git ls-tree HEAD DeFi/file.html
# Expected: DeFi/file.html
# Wrong:    github/ProtoJay4789.github.io/DeFi/file.html
```

**Level 2 — Git blob (content confirmed, UNCACHED — definitive):**
```
GH_TOKEN=$(gh auth token 2>/dev/null)
curl -s -H "Authorization: token $GH_TOKEN" \
  "https://api.github.com/repos/ProtoJay4789/ProtoJay4789.github.io/git/blobs/<SHA>" | \
  python3 -c "import sys,json,base64; d=json.load(sys.stdin); print(base64.b64decode(d['content']).decode()[:200])"
```

**Level 3 — Browser snapshot (visual, may be cached):**
Navigate URL, check `<title>` in the returned snapshot.

**Level 4 — Raw URL (cache-busting):**
```
curl -s "https://raw.githubusercontent.com/ProtoJay4789/ProtoJay4789.github.io/main/DeFi/file.html?cb=$(date +%s)" | grep '<title>'
```

### Multi-File Dashboard Deployments

When a dashboard loads data from multiple JSON files (rainbow, rotation, macro), deploy ALL files in the same batch. The dashboard shows fallback/loading until every file exists on the remote.

**Preferred order:**
1. Create all data files locally first (within the repo tree)
2. Push content (HTML) + data files (JSON) in a single API batch
3. Verify ALL raw URLs return 200
4. Check GitHub Actions for the final build to complete

## Deployment Workflow

### 1. Read Content from Vault

```python
# Read the source content (e.g., case studies, one-pager)
with open('/root/vaults/gentech/00-HQ/case-studies.md', 'r') as f:
    content = f.read()
```

### 2. Generate Matching HTML

The portfolio uses specific styling:
- Section wrapper: `<div id="sec-NAME" style="margin-top: 18px;">`
- Section title: `<div class="section-title">🔥 Title</div>`
- Cards: `<div class="card project-card">` with `card-header`, `project-tech`, `card-desc`
- Status badges: `<span class="status-badge status-live"><span class="status-dot"></span> Live</span>`
- Tags: `<span class="tag tag-blue|cyan|green">Label</span>`

**Copy an existing section as a template** and adapt the content.

### 3. Find Insertion Point

Use search to find markers:

```python
# Read portfolio HTML
with open('/root/vaults/gentech/github/ProtoJay4789.github.io/index.html', 'r') as f:
    html = f.read()

# Find insertion point (e.g., after "Browse All APIs →")
insert_marker = '<a href="https://gentechlabs.net" target="_blank" class="link-btn">🧪 Browse All APIs →</a>'
next_section = '<!-- ═══ NEXT_SECTION ═══ -->'

if insert_marker in html and next_section in html:
    # Insert between them
    updated = html.replace(insert_marker + '\n\n' + next_section,
                          insert_marker + '\n\n' + new_section + '\n' + next_section)
```

### 4. Update Navigation (4 places)

**Bottom nav:** Add button after last existing nav item

```html
<button class="nav-item" onclick="scrollToSection('sec-NAME')">
  <span class="icon">🔥</span>
  <span>Title</span>
</button>
```

**Settings modal:** Add option after last existing option

```html
<button class="settings-option" onclick="scrollToSection('sec-NAME');closeSettings()">
  <span style="font-size:1.3em;">🔥</span>
  <div><strong>Title</strong><br><span style="font-size:0.8em; color:var(--dim);">Subtitle</span></div>
</button>
```

**JavaScript section mapping:** Add to `map` object

```javascript
const map = {
  'sec-about': 0,
  'sec-journey': 1,
  'sec-projects': 2,
  'sec-stack': 3,
  'sec-apis': 4,
  'sec-NAME': 5  // Add this
};
```

**JavaScript scroll spy:** Add to `sections` array

```javascript
const sections = ['sec-about', 'sec-journey', 'sec-projects', 'sec-stack', 'sec-apis', 'sec-NAME'];
```

### 5. Use execute_code for Multi-Location Changes

Do NOT use `patch` for multi-location updates. Use `execute_code`:

```python
# More reliable for replacing multiple occurrences
content = content.replace(old_pattern, new_pattern)
# Write back
with open('index.html', 'w') as f:
    f.write(content)
```

### 6. Commit and Push

```bash
cd /root/vaults/gentech/github/ProtoJay4789.github.io
git add index.html
git commit -m "Descriptive commit message"
git push
```

---

## Git Credential Status

**Vault repo** (`gentech-vault`):
- ✅ Credentials configured
- Pushes work fine via HTTPS

**Portfolio repo** (`ProtoJay4789.github.io`):
- ❌ May not have credentials configured
- Current remote: `https://github.com/ProtoJay4789/ProtoJay4789.github.io.git`
- Push fails with: `could not read Username`

**Fix options:**
1. User pushes manually from their machine
2. Configure credentials on VPS (SSH key or OAuth token)
3. Use personal access token in remote URL

**Do NOT:** Hardcode tokens in scripts. Use environment variables or user configuration.

---

## Pitfalls

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| Using `patch` for multi-location changes | Only first occurrence replaced, navigation broken | Use `execute_code` with Python string replacement |
| Missing one of 4 navigation updates | Section exists but can't scroll to it or no settings option | Check all 4: bottom nav, settings, JS map, JS sections array |
| Not matching portfolio CSS style | Content looks out of place | Copy existing section as template, use same class names |
| Assuming credentials are configured | Push fails with auth error | Check credentials first, have user push manually if missing |
| Gitignore exception ordering | New media files (mp4, png) not pushed because gitignore denies them | Place exception (`!pattern`) AFTER the blanket deny (`**/*.ext`). Later gitignore rules override earlier ones, so deny-first, then allow. |
| **Wrong repo-relative path for subdirectory pages** | GitHub Pages returns 404 or old content | Verify with `git ls-tree HEAD path/to/file` — file must be at path relative to repo root, not nested under vault structure |
| **git push blocked by vault working tree** | `git checkout` aborts with "untracked files would be overwritten" | Use GitHub API fallback — don't try to force through vault interference |
| **CDN shows stale content after deploy** | raw.githubusercontent.com correct, GitHub Pages shows old version | Wait 2-5 min for Pages build. Verify via Git blob API for definitive status |
| **Private repo blocks GitHub Pages** | All URLs return 404, raw.githubusercontent.com also 404 without auth | Check repo visibility: `curl -s -o /dev/null -w "%{http_code}" "https://github.com/OWNER/REPO"` — 404 = private. Fix: make repo public, or deploy via Cloudflare Worker proxy using the PAT |
| **Actions disabled at account level (PERMANENT)** | Workflow dispatch returns 422 "Actions has been disabled for this user", no workflow runs appear. Pages builds queue but never execute (0 builds ever). Even legacy gh-pages branch won't deploy. The user confirmed the Actions settings option has been **removed** from their personal account settings entirely. | **This is permanent and unfixable.** Do NOT suggest re-enabling Actions or creating new workflows. The VPS at `portfolio.gentechlabs.net` is the only working deployment target. See `references/account-level-pages-block-diagnosis.md` for the full diagnostic sequence. |
| **CDN caches old private-repo 404** | After making repo public, raw.githubusercontent.com still returns 404 for hours | The CDN edge caches the "private repo" response aggressively. Use the GitHub API with auth (`curl -H "Authorization: token $PAT"`) to verify files exist. For immediate access, serve from VPS instead. |
| **gh-pages orphan branch doesn't trigger legacy build** | Pushing a gh-pages branch with all files doesn't deploy — Pages build queue shows 0 builds ever | The account-level Actions block prevents even legacy (non-workflow) Pages builds from executing. The `POST /pages/builds` API returns "queued" but the build never runs. Only fix is resolving the account-level Actions block or using VPS fallback. |
| **Pages build_type mismatch** | Pages configured but site returns 404 after push | Check `build_type` in Pages API response. If `"legacy"`, the default Pages builder is active but the workflow file expects `"workflow"` mode. Switch via `PUT /pages` with `{"build_type":"workflow"}`. If the PUT returns empty, the switch may have already been applied — re-check with GET. |
| **Pages status is null** | Pages API returns `"status": null` even though `has_pages: true` | Null status means Pages is configured but hasn't completed its first build yet. Push a commit or trigger a workflow dispatch to kick off the initial deployment. |
| **Repo flipped private→public→private kills Pages** | After flipping back to private, `has_pages` becomes `false` and Pages is deactivated | Re-flip to public, then re-enable Pages via `POST /pages` with `{"source":{"branch":"main","path":"/"}}`. Then switch build_type to `"workflow"` via `PUT /pages` with `{"build_type":"workflow"}`. Push a commit to trigger the first build. |

---

## Verification Checklist

After deployment:
- [ ] File pushed to VPS via SCP
- [ ] Backup created on VPS (`index.html.bak*`)
- [ ] `curl -s http://portfolio.gentechlabs.net/` returns HTTP 200
- [ ] `curl -sk https://portfolio.gentechlabs.net/` returns HTTP 200
- [ ] Content verified (e.g., `grep -c "x402"` or check for expected text)
- [ ] GitHub repo `gh-pages` branch updated (secondary mirror, for source control only)

---

## Example: Adding a New Section

```python
# 1. Generate HTML section
new_section = '''  <!-- ═══ NEW SECTION ═══ -->
  <div id="sec-new" style="margin-top: 18px;">
    <div class="section-title">🔥 New Section</div>
    <div class="card-desc" style="margin-bottom: 12px;">Description here.</div>

    <div class="card project-card">
      <div class="card-header">
        <span class="card-title">Item Title</span>
        <span class="status-badge status-live"><span class="status-dot"></span> Live</span>
      </div>
      <div class="project-tech">
        <span class="tag tag-blue">Tech</span>
        <span class="tag tag-cyan">Stack</span>
      </div>
      <div class="card-desc">Item description here.</div>
    </div>
  </div>'''

# 2. Insert at correct location
# 3. Update navigation (4 places)
# 4. Commit and push
```

---

## Related Infrastructure

### Portfolio Sync Script (`portfolio_sync.py`)

The portfolio has an automated daily health check at `scripts/portfolio_sync.py` (both profile and `/root/.hermes/scripts/` paths). It:
1. Pulls latest from `origin/main`
2. Reads canonical `data/projects.json`
3. Verifies consistency with `projects.json` and `index.html` (V4 — no inline JSON, so consistency is data:root only)
4. Syncs if needed and pushes

**The method signature for continuous work:** When deploying content, the sync script may overwrite your changes if it runs on its schedule after you. Always push your deployment changes, then let the health check confirm consistency on its next run. If the sync script detects a DRIFT and resets, it means your file paths were wrong (see file path pitfalls above).

### Cron Job

- **Name:** `Portfolio Health Check — Sync + Verify + Deploy`
- **Job ID:** `ce23c5df747b`
- **Schedule:** `15 12 * * *` (daily at 12:15 UTC / 8:15 AM ET)
- **Toolsets:** terminal, file
- **Script:** `portfolio_sync.py`

## Consistency Across Artifacts

**User preference:** When updating information like agent stack, deployed services, or pricing, ensure consistency across ALL public-facing artifacts. Do NOT update just one — update everywhere that information appears.

**Artifacts to keep in sync:**

| Artifact | Path | Purpose |
|----------|------|---------|
| Portfolio website | `github/ProtoJay4789.github.io/index.html` | Public showcase |
| One-pager | `00-HQ/gentech-one-pager.md` | Ecosystem introductions |
| Agent Kit v2 spec | `02-Labs/agent-kit/AGENT-KIT-V2-SPEC.md` | Product documentation |
| Build queue | `00-HQ/build-queue.md` | Internal roadmap |
| Audit reports | `Audits/*.md` | Verification evidence |

**When updating:**

1. Identify what changed (e.g., new model, new API, updated endpoint count)
2. Search across all artifacts for related mentions
3. Update every occurrence with the new information
4. Commit and push all changes together

**Example workflow:**

```python
# User says: "Update agent stack to include GLM-5.2"

# 1. Search for "agent stack" across vault
import os
for root, dirs, files in os.walk('/root/vaults/gentech'):
    for file in files:
        if file.endswith('.md') or file.endswith('.html'):
            path = os.path.join(root, file)
            with open(path, 'r') as f:
                content = f.read()
            if 'agent stack' in content.lower():
                # Update this file
                updated = content.replace(old_stack, new_stack)
                with open(path, 'w') as f:
                    f.write(updated)

# 2. Commit all changes together
git add .
git commit -m "Update agent stack across all artifacts - add GLM-5.2"
git push
```

**Why this matters:** 
- User said "I wanted to make sure it's synced everywhere"
- Inconsistent information looks unprofessional
- Different docs saying different things confuses people
- Melinda, grant reviewers, and collaborators read multiple artifacts

---

## Related Files

- Portfolio site: `/root/vaults/gentech/github/ProtoJay4789.github.io/index.html`
- Vault content: `/root/vaults/gentech/00-HQ/*.md`
- Reference: See `references/portfolio-structure.md` for full CSS classes
- **Design strategy:** See `references/portfolio-design-strategy.md` for job-seeking vs founder showcase mode, section ordering, and content rules
- **Link delivery pattern:** See `web-deployment` skill's "Deliver the Link" section for the verified pattern (build first, verify, send link as its own message — never bury at end of status recap)

---

*Last updated: July 14, 2026 — Added standalone subdirectory deployment, GitHub API fallback, CDN propagation verification, path verification pitfalls*