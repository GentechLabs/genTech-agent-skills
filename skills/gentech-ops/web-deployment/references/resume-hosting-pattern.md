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
3. **GitHub Pages mirror:** `gentechlabs.github.io/resume.*` — blocked in rename provision-limbo
   (see SKILL.md GitHub Pages section). The sync cron pushes repo files regardless so the
   mirror self-heals when GitHub finishes provisioning.

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

## Content rules encoded (Jordan's standards)
- Work GitHub = `github.com/gentechlabs` org (personal GentechLabs unused for work)
- Portfolio URL = `gentechlabs.github.io` (after rename; `protojay4789.github.io` is dead)
- AI-training/evaluation gig platforms (Outlier, Mercor, DataAnnotation, Surge AI) count as
  work experience for these resumes; assessments are the screening, never pay to apply
