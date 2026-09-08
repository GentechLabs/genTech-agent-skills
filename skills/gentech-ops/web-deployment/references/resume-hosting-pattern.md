# Resume/CV always-current hosting pattern (Aug 30, 2026)

## The problem
A résumé that lives in one file goes stale, and a résumé that lives in five files drifts.
Jordan asked for the master résumé to be hosted on the website suite AND "always kept
updated." The solution is a single vault source-of-truth + generated artifacts + a sync cron.

## Source of truth
Vault: `/root/vaults/gentech/10-Labs/Resumes/Jordan_Master_Resume.{md,html,pdf}`

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

## The sync cron ("Resume Sync — vault → web + portfolio repo", every 6h)
Prompt outline (job id 877b19f24f9f):
1. `diff -q` the three pairs (vault pdf/html vs /var/www/gentechlabs, vault md vs repo resume.md)
2. Any drift → copy vault → web (`chown www-data:www-data`), verify `curl 200`, commit+push repo copy
3. Monday-only content QA: 1 page still, no dead protojay4789.github.io links, "In Progress"
   certs that finished, repos shipped in last month missing from project list
4. Report: silent ("[SILENT]") when clean; short report when synced or stale

## Content rules encoded (Jordan's standards)
- Work GitHub = `github.com/gentechlabs` org (personal ProtoJay4789 unused for work)
- Portfolio URL = `gentechlabs.github.io` (after rename; `protojay4789.github.io` is dead)
- AI-training/evaluation gig platforms (Outlier, Mercor, DataAnnotation, Surge AI) count as
  work experience for these resumes; assessments are the screening, never pay to apply
