---
name: privacy-audit
description: "Scan GitHub repos, local codebases, AND live web surfaces (docroots, systemd journals, edge cache, access logs) for exposed personal information — wallet addresses, email, API keys, tokens, private keys, cloud credentials, and PII. Produces an actionable report with severity levels and rotation steps. Consolidated: absorbs former privacy-sweep."
tags: [security, privacy, github, api-keys, pii]
trigger: "When Jordan asks to check repos or live services for personal info — e.g. an audit of anything revealed that shouldn't have been revealed — before pushing code, after a session that touched credentials, or after adding new API keys or wallet addresses to any project."
version: 1.2.0
author: Gentech
---

# Privacy Audit

Scan all repos for personal information that shouldn't be public. Run before pushes, after credential changes, or on request.

> Version 1.2.0 (Council 2026-09-27) — **Correlated Exposure** added: an identifier is never judged alone.
> Authored on gentech-treasury and promoted into the core, byte-for-byte, no content changed. Sharpens the two
> severity rows: a bare wallet address is *Info alone* — never clear it on that basis until the correlation sweep
> (personal name / live balance / tx hash / physical identity beside it) comes back empty.
>
> Version 1.1.0 — the repo sweep and the live-surface audit were two half-skills, one on each seat. Merged
> 2026-09-26 Council Overnight: this is the union, with no section dropped. The repo half proceeds top-down;
> the exposure half starts at *Live-Surface Exposure Audit*.

## What to Scan

| Category | Patterns | Severity |
|----------|----------|----------|
| **API Keys** | `sk_live`, `sk_test`, `api_key=`, `AIza`, `ghp_`, hex strings in .env | 🔴 Critical |
| **Private Keys** | `PRIVATE_KEY`, `MNEMONIC`, `SEED_PHRASE` | 🔴 Critical |
| **Cloud Credentials** | `AWS_SECRET`, `MINIO_`, service account keys | 🔴 Critical |
| **GitHub Tokens** | `ghp_`, `gho_`, `github_pat_` | 🔴 Critical |
| **Wallet Addresses** | `0x[0-9a-fA-F]{40}` | 🟡 Info ALONE — but see *Correlated Exposure* |
| **Email** | `@gmail`, `@yahoo`, `mailto:` | ⚠️ Medium |
| **LinkedIn/Social** | `linkedin.com/in/`, Discord | ⚠️ Medium |

## Scan Commands

```bash
# API keys in .env files
grep -rn "API_KEY\|SECRET\|TOKEN" REPO/ --include="*.env" | grep -v node_modules

# Wallet addresses in code
grep -rn "0x[0-9a-fA-F]\{40\}" REPO/ --include="*.{md,json,js,py,html,yaml}" | grep -v node_modules

# Email addresses
grep -rn "@gmail\|@yahoo\|mailto:" REPO/ --include="*.{md,json,js,py,html}" | grep -v node_modules
```

**Alternative (faster):** Use Hermes `search_files` tool with `file_glob` filter — ripgrep-backed, faster than shell grep for large repos. Pattern: `search_files(pattern="0x7ebff188", path="/root/repos", file_glob="*.{md,json,js,py,html,env}")`

## Scope the scan before trusting a negative

A box-wide recursive grep churns on `node_modules`, caches, and build debris and can time out before covering the tree — then the empty result reads as "clean." Scan the directories that can actually execute or ship: the project tree, the profiles' `.env` files, scripts dirs, and vault config paths. Verify a "no matches" result names the paths it covered, and re-run scoped (project dir, `file_glob` filter) if the first sweep timed out or matched only hidden/gitignored files by accident.

Note: content search tools skip hidden/gitignored files by default and report them separately — an `.env` hit can be reported as a warning instead of a match. When auditing, read the known env paths directly rather than relying on the sweep alone.

## Severity Response

| Level | Action |
|-------|--------|
| 🔴 Critical (API keys) | Rotate immediately. Revoke old key. |
| ⚠️ Medium (email/LinkedIn) | Confirm intentional. Portfolio = OK. Code comments = remove. |
| 🟡 Info (wallet alone) | A bare address in code is low risk — but NEVER clear it on that basis. First check whether anything NAMES a person beside it (see *Correlated Exposure*). |

## Report Format

```markdown
## 🔍 Privacy Sweep — [DATE]

### 🚨 CRITICAL
| Repo | File | Key Type | Action |
|------|------|----------|--------|
| repo | .env | ElevenLabs `bb15...` | Rotate |

### ⚠️ PERSONAL INFO
| Repo | What | Files |
|------|------|-------|
| repo | email | 3 files |
```

## Cross-Check Tracked Files Against LIVE env Values

**Always run this method after any session that touches credentials, and before pushing.** Regex
sweeps find shapes; they cannot tell a live key from a placeholder. **The reliable method is to
load the authoritative values and search for them.** False positives collapse to zero, and every
hit is a credential you can prove is live.

Use `references/live-secret-leak-scan.md` for the exact recipe and a reusable script. Standing
rules below.

- **Redact in the working tree; the commit is what carries it.** A leak found but not committed
  rides out on the next push. Redaction and commit are one action.
- **Do not print the matched value** in the report. Print the key NAME and the file path — the
  reader can find it, and the value does not get copied into a second wrong place (the chat log,
  the handoff, the terminal history).
- **Rotate, don't just delete.** A key already pushed is exposed even after the file is fixed;
  redaction closes the future, rotation closes the past. Say this plainly in the report.
- **Backups and config dumps are where keys concentrate.** `backups/`, `*.yaml` config snapshots,
  pre-change copies. An archive of a config is a credential dump if it is committed.
- **Check a tracked `.env` immediately** — it is a standing leak by definition, and `git rm
  --cached` + an ignore rule fixes it without losing the file on disk.
- **A `.gitignore` saves you from the disk copy, not the history.** If a pattern like `*.gz`
  excludes the payload, the tracked index can still be clean while the payload sits on disk —
  verify which of the two actually pushed before claiming exposure.

## Live-Surface Exposure Audit

When the question is "what has actually been revealed" about a deployed box — docroots, journals, caches — that is a different scan than the repo sweep. Order matters: classify what is *served* before trusting what is *on disk*.

1. **Inventory every docroot before scanning.** Parse `root` directives out of `/etc/nginx/sites-enabled/`, then hunt sensitive artefacts inside them:
   ```bash
   find DOCROOT -maxdepth 3 \( -iname '*.env*' -o -iname 'MEMORY.md*' -o -iname 'USER.md*' -o -iname '*.tar.gz' -o -iname '*.pem' -o -iname '*.key' -o -iname '*resume*' \)
   ```
   A directory that is only unreachable by perm coincidence (e.g. 0700 root under a docroot whose server runs as www-data) is a latent exposure, not a control — one chmod or one deploy running as root publishes it. Report latent paths as risk even while they currently 403.
2. **Classify by response BODY, never by log status.** Fetch each sensitive path through the public URL and inspect the content: a leak is git-config text, env assignments, or memory content in the body. Status codes lie in both directions — a CDN can record 200 while serving the origin's 404 body, and SPA fallbacks can 200 with HTML. Confirm what exists on disk before calling anything "served".
3. **Mine the access log for what scanners hunt and what succeeded.**
   ```bash
   grep -hE '"(GET|POST|HEAD) [^"]*(\.env|\.git|backup|secret|credential)[^"]*"' /var/log/nginx/access.log | awk '{print $9, $7}' | sort | uniq -c | sort -rn
   ```
   Two reads: high probe counts mark paths scanners expect to exist (move or rename them — they get found eventually), and ANY sensitive probe with 200/206 is an incident → rotate immediately.
4. **Check the systemd journal for secret echo.** An unparseable line in an `EnvironmentFile` makes systemd log that assignment *with its value* on every service start. Count it: `journalctl -u UNIT | grep VAR_NAME | wc -l`. Any hit = confirmed leak: rotate the key first, fix the `.env` syntax second (EnvironmentFiles must be parseable: no `export ` prefixes, no digit-leading variable names — those two defects are the usual culprits; pre-validate by starting the unit once and grepping the journal for `Ignoring invalid environment assignment`), then purge history (`journalctl --rotate && journalctl --vacuum-time=1d`).
5. **Check edge caching of sensitive paths.** `curl -s -D - -o /dev/null URL | grep -i cf-cache-status` — `DYNAMIC` is fine; `HIT` on anything sensitive means cached copies persist at the edge even after origin removal.
6. **PII in intentionally-public files** (resumes, landing pages): extract text (`pdftotext`), report which FIELDS are present (email/phone/street/zip/socials/employer) without printing values, and get an explicit keep-public-or-gate decision — cached copies outlive origin removal.
7. **State the scope honestly.** Name what was NOT covered; git history is the most common place a "removed" secret still lives, so a complete audit needs a history pass over every repo (gitleaks or `git log -p`).

**Report hygiene:** identify secrets by variable name, file, and line number only — never reproduce the value, not even truncated.

## Pre-Publish Secret Scan (gate for ANY public source/artifact publish)

Before putting source code, configs, or docs on a public URL, scan them — this is a gate,
not a post-check:

1. Scan against BOTH: (a) every actual value in local `.env`/credential stores (a grep for
   each real secret value catches leaks pattern-matching misses), and (b) generic key-pattern
   classes (`sk_`, `ghp_`, `AKIA`, `0x{40}`, PEM headers, bearer tokens).
2. Before dismissing any hit as a known-public value, TEST your own allow-list: run the
   filter against a value you KNOW is benign and confirm it matches. A case-sensitivity or
   escaping bug in the allow-list makes the scanner silently re-flag known-public values (or
   worse, pass real secrets) — an untested filter's output is not an honest result.
3. After publishing, re-scan the SERVED BYTES (`curl` each published URL and grep the
   response bodies), not just the files on disk — what nginx actually serves is the exposure.
4. Verify the publish anonymously with a positive control (a URL that must be 200) and a
   negative control (a path that must 404), so a proxy/CDN cache masking a missing file can't
   fake a clean result.
5. State honestly which parts of the plan are NOT done (e.g. a mirror host needing account
   creation is a user-gated step) — don't let an unexecuted step ride along as shipped.

## Check Repo Visibility
```bash
gh repo view "OWNER/REPO" --json visibility -q '.visibility'
```

## Scope of an Exposure Audit

An audit that finds ONE leak vector has not audited exposure — it has audited that vector. When
any exposure surfaces, enumerate the vectors and sweep them all in one pass (systemd journal,
public docroot, nginx access logs, edge cache, git history). The access-log sweep found real
incidents independent of the trigger: `.git` probes returning 200, a publicly downloadable
resume (PII fields: email, phone, street/zip, socials — extracted with pdftotext), and 18 probes
against `/backups/.env`. Classify 200s by response BODY, never by status (CDN 200s can carry the
origin's 404 body — verify what was actually served before calling anything a leak).

## Rotation Is Part of the Audit

"Rotate" for a leaked key means: generate a replacement, write it ONLY to non-leaking stores (project `.env` 0600, not any systemd-read env), purge leaked copies from every store that captured them (journals, logs, stale envs), scrub staging copies of the value, and verify the new key is live by deriving/using it — before declaring the finding closed. A rotation that swaps the key but leaves the leak mechanism in place re-leaks the new key the same way.

Concretely (the journal-leak mechanics): a secret stored under a digit-leading env name (e.g. `0G_*`) in a **systemd-read** `.env` is rejected by `EnvironmentFile=` parsing and echoed — value included — to the journal on every service start, compounding across restarts. Fix at the root: confirm no code consumes the variable (name-only grep across code trees), move the key to the owning project's own 0600 `.env` (and prove no systemd unit references it), then purge the journal: `journalctl --rotate && journalctl --vacuum-time=1m` — a day-granularity vacuum keeps the very archives being purged, so use a tight window. Verify zero both via `journalctl | grep -c <KEY_NAME>` AND a direct grep of `/var/log/journal/`.

**Verify the rotation by derivation, not by shape.** Derive the address from the stored key (`eth_account.Account.from_key(key).address`) and compare to the stored address — a count of key-shaped lines proves presence, not correctness. And after any state-changing rotation script crashes, read the on-disk target BEFORE re-running: a traceback raised in a print statement after the writes leaves correct partial state, and a blind re-run can overwrite state you have not audited.

Also sweep git history for the leaked value (`git log --all -S "<value>"`) before concluding scope — but distinguish name-hits (discussions/audits mentioning the var) from value-hits (actual secret in a blob). A gitignored env's absence from history is expected; verify with a path-specific `git log --all -- <path>` that returns nothing.

A leaked-but-never-funded key still warrants rotation — the exposure is the capability, not the balance.

## Proactive Git-History Secret Sweep

A secret removed from a file usually still lives in commit history. When Jordan asks "did we ever accidentally commit personal info", sweep ALL repos' history for unknown leaks — not just a known value:

1. **Enumerate every repo on the box** (`find <roots> -maxdepth 3 -name .git -type d` across vault, app, and site roots) and count commits per repo so coverage is visible in the report.
2. **Scan committed blob content, not diffs.** A pickaxe `git log -S` with one narrow regex (e.g. 64-hex) misses token-shaped secrets (`sk-`, `ghp_`, bot tokens, PEM headers). Enumerate `git rev-list --all --objects`, keep blobs only (`git cat-file -t` = blob), and grep each blob's content for the high-confidence pattern set: private-key assignments, `sk-`, `ghp_`, `xox[baprs]-`, `AIza`, PEM `BEGIN … PRIVATE KEY`, password/secret assignments.
3. **Classify every suspect WITHOUT printing the value.** Print only structure and identity:
   - Path context: `tests/positive/` fixtures hold fake secrets by design — a hit there is a sample, not a leak.
   - Structural fake-tests: a hex key with 16 distinct chars is a realistic-looking fixture; 1–2 distinct chars is obviously synthetic; `YOUR_`/`xxxx`/`deadbeef` = placeholder.
   - Format-validate before alarming: a genuine Google key is exactly 39 chars starting `AIzaSy` — a 40-char `AIza…` string failing that is a redacted sample, not a key.
   - Compare any candidate to the LIVE key by sha256 prefix (never the value) to decide rotation vs clearance.

**Never print a candidate secret into the report or chat** — the audit output must not become the new leak. Identity is conveyed by hash prefix and length only.

## Exposed-File Remediation (served docroots)

When sensitive files (memories, brain backups, env dumps) are found under a served web root:

1. **Find the producer before moving anything** — grep crons/scripts for the write path. Fixing only the files re-leaks them on the producer's next run; repoint the producer at a root-owned path outside every docroot (e.g. `/root/backups/<topic>/`) and chmod the copy 0600.
2. **Checksum-verify copies before deleting originals** — `md5sum` each copied file against its original; a `cp` exit-0 alone is not identity. Remove the exposed dir only after every file MATCHes.
3. **Remove only the offending subdir** — the docroot often serves unrelated live content; verify those files still exist after the cleanup.
4. **Live-verify the seal externally**: curl the old URL and expect 404 (the missing dir + try_files covers it; an explicit nginx location guard is optional belt-and-braces). A 200 here means the exposure is still open.

## Correlated Exposure — Never Judge an Identifier Alone

**An address is low risk or critical entirely depending on what sits NEXT to it.** `0x…` alone in a
code comment is noise. The same `0x…` on a page titled with a person's name, beside their live
balance, is the exact pairing attackers assemble by hand.

The documented attack shape: targets are enumerated **from public chain data first**, and only then is
identity attached to each one. The chain gives up the money; a public page gives up the person. This is
why the real-world consequence is physical — verified industry counts show home-invasion robberies of
crypto holders rising sharply year over year, with a single country accounting for most cases. Exposure
here is not reputational.

### The correlation sweep (do this before clearing ANY identifier)

For every wallet/address/handle found, answer: *what in the same artifact, directory, or page tells a
reader WHOSE it is?* Specifically co-locate against:

1. A personal name — page `<title>`, heading, filename (`jordan-defi.html`), tenant/owner field.
2. A live monetary figure — balance, position value, holdings, TVL attributable to them.
3. A transaction hash — **this is a one-hop lookup, not an opaque value.** Any explorer resolves it to
   the SENDER, plus amounts and timing. Redacting an address while leaving its tx hashes is security
   theatre; sweep for `0x[a-fA-F0-9]{64}` as well as 40-hex.
4. Anything that identifies the physical person — full name, email, address, employer, photo.

**Report the PAIR, not the parts.** "Wallet + live balance on a page naming its owner" is one finding
with one severity, and it is critical. Listing them as three separate low-severity items is how the
exposure survives a passing audit.

### Classify a 40-hex string by `eth_getCode` before calling it a person

Regex alone cannot tell a wallet from a pool/router contract, and a naive pattern sweep will both
over-report (`0x…` pool addresses are protocol infrastructure and fine to publish) and under-report
(a 64-hex tx hash sliced to its first 40 chars is NOT an address, but a 32-byte hash **is** a sender
lookup). Call `eth_getCode`; `0x` (empty) = EOA/person, non-empty = contract.

### Fix by redaction-in-the-payload, not redaction-in-the-render

Mask at the SOURCE that produces the public artifact and let every downstream consumer inherit the
masked value. A page script that slices an address is one careless edit from printing it whole again,
and any sibling consumer of the same JSON still publishes it. Ship `wallet_masked` (`0x572A…5037`) in
the payload, **delete the raw key entirely**, and render whatever the payload carries. Mask rather than
remove where the user must still recognise their own account — the tail is what makes the page
verifiable by its owner while removing the handle a stranger would paste into an explorer.

**Verify the seal on the LIVE URL, both tenants/instances.** Re-fetch the served bytes and assert:
raw key absent, zero 64-hex hashes, and every remaining 40-hex string is a contract. Then run the sweep
for the SIBLING surface — these pages are generated from a template, so one tenant being clean says
nothing about the other.

### Crawler policy: prefer per-page `noindex` over a site-wide `robots.txt`

For a named-person page on an otherwise-public site, add
`<meta name="robots" content="noindex, nofollow, noarchive, nosnippet">` to the PAGE. A site-wide
`Disallow` would take the legitimate public portfolio down with it, and — the subtle part — a
`robots.txt` the crawler refuses to fetch cannot stop indexing. Per-page meta leaves the rest of the
site crawlable while de-indexing the sensitive pages.

## Prevention
- `.env` files in `.gitignore`
- Use env vars for wallet: `process.env.WALLET_ADDRESS`
- Portfolio email/LinkedIn: intentional, keep only in HTML
