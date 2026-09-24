# Resume/CV always-current hosting pattern (Aug 30, 2026)

## The problem
A résumé that lives in one file goes stale, and a résumé that lives in five files drifts.
Jordan asked for the master résumé to be hosted on the website suite AND "always kept
updated." The solution is a single vault source-of-truth + generated artifacts + a sync cron.

## Source of truth
Vault: `${VAULT_DIR}/10-Labs/Resumes/Jordan_Master_Resume.{md,html,pdf}`

- The `.md` is the editable master (header rule: email + GitHub org + portfolio + Telegram —
  NO location, per Jordan's format preference).
- The `.html` is the print-styled version (WeasyPrint-compatible: @page letter, 9.5pt,
  single page target). Regenerate PDF from HTML whenever HTML changes:
  `python3 -c "from weasyprint import HTML; HTML('Jordan_Master_Resume.html').write_pdf('Jordan_Master_Resume.pdf')"`
- QA loop: `pdfinfo | grep Pages` must say 1 (a 2-page resume with a near-empty page 2
  happened — fix by trimming content + tightening CSS, then re-render), and render a
  preview with `pdftoppm -png -r 60` + vision check before declaring done.

## Hosted surfaces (three, by purpose)
1. **Self-hosted (primary, reliable):** `/var/www/gentechlabs/resume.pdf` + `resume.html`
   → live at `https://gentechlabs.net/resume.pdf` and `/resume.html`. `chown www-data:www-data`.
   This is the URL given out — it depends on nothing.
2. **Portfolio repo (canonical history):** `/root/repos/ProtoJay4789.github.io/` — `resume.md`
   and `resume/index.html` committed. NOTE: repo `.gitignore` has `**/*.pdf` — a PDF needs
   `git add -f`. The local clone's remote points at `ProtoJay4789/...` (old account) — push
   still lands via redirect, but re-point to the org when convenient.
3. **GitHub Pages mirror:** `gentechlabs.github.io/resume.*` — **the file is committed to `main`, but
   the hostname serves NOTHING (measured 2026-09-16).** Root, `index.html` and `resume.md` all return
   **404 · "Site not found · GitHub Pages"** while the Pages API reports the site configured, source
   `main`, and the last deploy `success`. Cause: the `GentechLabs` account is invisible to anonymous
   visitors — auth 200 / anon 404 on the profile, on every repo page, and on every
   `raw.githubusercontent.com/GentechLabs/**` path, while the API reports the repos
   `"visibility":"public"`; `search/repositories?q=user:GentechLabs` → 422 **`User flagged as spammy.`**
   The separate `Gentech-Labs` org *does* serve publicly (anon 200). The old "rename provision-limbo /
   it will self-heal" note is **wrong** — the last deploy *succeeded* and still serves nothing. It is
   the account, not the pipeline. **Repo-presence is not liveness: never write "live 200" here.**

## Verify public links by ANONYMOUS resolution, never by spelling

A link scan that greps for the *right string* proves nothing about whether a recruiter can open it.
For every URL printed on a public-facing document:

```bash
curl -s -o /dev/null -w '%{http_code}\n' https://github.com/<owner>        # anonymous: no auth, no -H
curl -s -o /dev/null -w '%{http_code}\n' https://github.com/<owner>/<repo>
```

**Always include a control in the same minute** (`github.com/torvalds` → 200,
`raw.githubusercontent.com/torvalds/linux` → 200). Without a control a 404 is indistinguishable from
our IP being blocked, a rate limit, or a GitHub wobble; with one, the auth/anon split proves *which
side* is invisible. Measured 2026-09-16 on the master résumé: the `GitHub` line
(`github.com/gentechlabs`) and the `Portfolio` line (`gentechlabs.github.io`) are both **anonymous
404**, and the `SELECTED PROJECTS (github.com/gentechlabs)` heading points at the same invisible
account — so "64 shipped public repositories" is not publicly checkable either. **Two of four contact
lines broken while the weekly check kept calling them "clean" because they were spelled correctly.**
Repointing them is an identity decision that collides with the standing "all work uses `GentechLabs`"
directive → **flag to Jordan, do not edit.**

## The push path has its own failure mode — check the credential, not just the diff

The portfolio clone's `origin` may embed a PAT in the URL. When that token is revoked, `git push` dies
with `remote: Invalid username or token` — a dead sync path that raises **no drift signal at all**,
because on the day it breaks there is nothing to copy. Before reporting a clean run:

```bash
cd /root/repos/gentechlabs.github.io && GIT_TERMINAL_PROMPT=0 git ls-remote origin main
```

If it fails, repair (no secret handling needed — `credential.helper=store` and `gh auth git-credential`
both work) and re-verify:

```bash
git remote set-url origin https://github.com/GentechLabs/gentechlabs.github.io.git
git ls-remote origin main      # must print the remote sha
grep -c ghp_ .git/config       # must print 0 (no plaintext PAT left behind)
```

## Links from the portfolio
The portfolio index "Connect" section carries: `📄 Résumé / CV` → `https://gentechlabs.net/resume.pdf`
and `🏛️ x402 Council APIs` → `https://api.gentechlabs.net/docs`. Point at the self-hosted URL,
never the flapping .io one.

## Drift testing: hash the ORIGIN, not the public URL

`gentechlabs.net` sits behind Cloudflare with **Email Obfuscation ON**. It rewrites the résumé's
contact line on the way out:

```
<a href="/cdn-cgi/l/email-protection" class="__cf_email__" data-cfemail="462c29…">[email&#160;protected]</a>
```

and appends `<script src="/cdn-cgi/scripts/5c5dd728/cloudflare-static/email-decode.min.js">`.
**Consequence:** `curl -sL https://gentechlabs.net/resume.html | sha256sum` can *never* equal the
master's hash, and that is **not drift** — it is a false alarm that will make you re-sync a file
that is already correct.

- **Test for drift at the origin:** `curl -s http://127.0.0.1/resume.html | sha256sum` — must equal
  the vault master. Same for `resume.pdf` (PDFs pass through unmodified, so the public URL is fine).
- **Use the public URL only to confirm it is served** (`curl -o /dev/null -w '%{http_code}'` → 200,
  or compare byte *size*, which Cloudflare's rewrite changes by a known few hundred bytes).
- Corollary: an HTML hash mismatch between public and origin is **expected**; an **origin** mismatch
  against the vault master is real drift.

## Weekly-check trap: a "Selected Project" can be a fork with zero own commits

Before crediting a listed project, check `gh api repos/GentechLabs/<repo> --jq '.fork'` and
compare ahead_by against the parent. Four résumé lines (r402, ra2a, iAgent, ard-spec) are
**unmodified upstream forks** — qntx, Injectivelabs, ards-project — where our actual work is an
**open, unmerged PR** in the upstream repo. Under a heading like "Selected Projects — GenTech Labs"
that framing overclaims. Verify authorship by commit email/login, not by the repo merely existing
under the org; also note `users/GentechLabs.public_repos` **includes forks** (66 total vs 50
non-fork), so a "N public repos" headline inflates unless it says "own repos".

## The sync cron ("Resume Sync — vault → web + portfolio repo", every 6h)
Prompt outline (job id 877b19f24f9f):
1. `diff -q` the three pairs (vault pdf/html vs /var/www/gentechlabs, vault md vs repo resume.md)
2. Any drift → copy vault → web (`chown www-data:www-data`), verify `curl 200`, commit+push repo copy
3. Monday-only content QA: 1 page still, no dead protojay4789.github.io links, "In Progress"
   certs that finished, repos shipped in last month missing from project list
4. Report: silent ("[SILENT]") when clean; short report when synced or stale

## Drift-testing the repo copy: diff `origin/main`, never the working tree (measured 2026-09-23)

`diff -q vault/Jordan_Master_Resume.md repo/resume.md` compares the vault against the clone's
**working tree** — and the working tree can hold a rebuild that was never committed. On 2026-09-23
the 15:04 rebuild (`Website: gentechlabs.net`, `60+ shipped builds`) had been copied into the clone,
so the diff was clean, while `HEAD` and `origin/main` still carried the 12:01 text
(`Portfolio: portfolio.gentechlabs.net`, `64 shipped public repos`). The markdown surface was a full
rebuild stale and a diff-only run would have reported "[SILENT]".

**Always diff the committed surface:**

```bash
cd /root/repos/gentechlabs.github.io
git status --short resume.md            # ' M resume.md' = uncommitted drift
GIT_TERMINAL_PROMPT=0 git fetch origin main -q
git show origin/main:resume.md | md5sum # must equal the vault master md5
```

If they differ: `git add resume.md` — stage that file **alone** (the clone routinely carries other
agents' unpushed commits), commit, push, then re-verify `git show origin/main:resume.md | md5sum`
against the vault. Disclose any commits the push carried that were not yours.

## Content rules encoded (Jordan's standards)
- Work GitHub = `github.com/gentechlabs` org (personal GentechLabs unused for work)
- Portfolio URL = `gentechlabs.github.io` (after rename; `protojay4789.github.io` is dead)
- AI-training/evaluation gig platforms (Outlier, Mercor, DataAnnotation, Surge AI) count as
  work experience for these resumes; assessments are the screening, never pay to apply
