---
name: credential-security-behavior
description: "How Hermes security layers interfere with credential handling — redaction, approval prompts, and write sanitization. Patterns for safely storing API keys, PATs, and tokens."
version: 1.1.0
author: Gentech
license: MIT
metadata:
  hermes:
    tags: [security, credentials, tokens, api-keys, troubleshooting]
---

# Credential Security Behavior in Hermes Agents

When agents handle credentials, Hermes applies three security layers that can interfere with storage and verification. Understanding these is critical for building reliable automation.

## The Three Layers

### 1. Secret Redaction (Display Only)
All tool output is scanned for credential patterns (github_pat_*, ghp_*, api keys). Matches are truncated to `prefix...suffix` in display. File on disk may be correct, but you cannot verify through tool output.

### 2. Terminal Security Scanner (Blocks Execution)
Commands containing credential patterns are blocked until user approval. Pattern: `[HIGH] GitHub Fine-Grained PAT detected`. Blocks echo, printf, python3, and any command containing the token string.

### 3. Write Tool Sanitization
write_file may truncate credential content before writing. Output shows redacted version; actual file content may differ.

## Safe Storage Patterns

**Pattern 1: Indirect Write**
```bash
echo "Paste token:" && read TOKEN && echo -n "$TOKEN" > ~/.token && wc -c ~/.token
```
Verify with `wc -c` (byte count), never `cat`.

**Pattern 2: Environment Injection**
```bash
source .env  # Credentials in env, not file reads
export TOKEN=***  # Functional, redacted from display
```

**Pattern 3: Interactive Auth**
```bash
gh auth login  # User handles credential entry directly
hermes auth add  # Hermes credential flow
```

## Verification Workarounds
- `wc -c` — byte count (not redacted)
- `sha256sum` — hash comparison (not redacted)
- `file exists?` — stat check (not redacted)
- `head -c N` — partial read (may still be redacted)
- `cat` — full content read (always redacted)

## Configuration
```bash
hermes config set security.redact_secrets false  # Disable display redaction (NOT recommended)
hermes config set approvals.mode smart           # Smart approval (recommended middle ground)
```

## Pitfalls

### gh CLI vs .env File Mismatch (CRITICAL)
`gh auth login` updates the `gh` CLI's own token store (`~/.config/gh/hosts.yml`) but does NOT update `GITHUB_TOKEN` in `.env`. Cron jobs, scripts, and Hermes tools read from `.env`, not from `gh`. You can have `gh auth status` showing "Logged in" while every cron fails with "Bad credentials."

**Fix:** After any GitHub token rotation, explicitly update BOTH places:
1. `gh auth login --with-token < ~/.github-token`
2. `GITHUB_TOKEN=` in `/root/.hermes/profiles/gentech/.env`

**Verification:** Test the `.env` token independently (not through `gh`):
```bash
python3 /root/.hermes/profiles/gentech/scripts/gh-check.py
```
This checks the `.env` token directly against the GitHub API, bypassing `gh` CLI entirely.

**Rule:** After every credential rotation, verify immediately with a real API call in the same turn. If the test fails, surface it to the user right away. Do not wait for a cron cycle to discover it.

**Cross-profile note:** Each Hermes profile has its own `.env`. When Forge gets a token from Jordan, same rule applies — don't just update `gh`, update the `.env` too. The `.env` is what scripts and cron jobs read.

### Fine-Grained PATs: API ≠ Git Push
A GitHub fine-grained PAT can pass API authentication (`/user`, `/repos`) but fail `git push` if it lacks `Contents: Read and Write` permission on the target repository. Detection: `gh auth status` shows "token is invalid" even though `curl -H "Authorization: Bearer $TOKEN" https://api.github.com/user` succeeds.

**Fix:** Go to GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens → ensure `Contents: Read and Write` is granted for the specific repo (or "All repositories"). Alternatively, use a classic PAT with `repo` scope, which covers everything.

### Credential Write Verification
When `redact_secrets` is enabled (default), tool output always shows truncated credentials — even when the file was written correctly. The agent can report "written successfully" but display `github_pat_11AV5...ufMo` instead of the full token.

**Safe verification methods (not redacted):**
- `wc -c` — byte count confirms full token was written
- `sha256sum` — hash comparison
- `stat` or `ls -la` — file existence and size
- `python3 -c "print(len(open('file').read().strip()))"` — programmatic length check

**Unsafe (always redacted):**
- `cat`, `head`, `tail` — full content read
- `read_file` tool — displays redacted content
- Any command that outputs the token string

### HOME Path Redirection — Affects ALL Config Files
Hermes profiles set `HOME` to `~/.hermes/profiles/<name>/home` at runtime. Any tool or script that uses `$HOME` to find or store config files will land in the profile's home, not `/root/`. This is NOT limited to git credentials — it affects every config-aware tool.

**Affected configs encountered so far:**
- **Git credentials:** `~/.git-credentials` → `~/.hermes/profiles/<name>/home/.git-credentials`
- **Pay wallet:** `~/.config/pay/accounts.yml` → `~/.hermes/profiles/<name>/home/.config/pay/accounts.yml` (keypair at `/root/.config/pay/` won't be found via `$HOME`)
- **Any CLI with `~/.config/` defaults** — apply the same logic

**Fix:** Always verify the resolved path when writing or reading credential configs:
```bash
# Check what $HOME resolves to
python3 -c "import os; print(os.path.expanduser('~'))"

# Check where a specific config file would land
python3 -c "import os; print(os.path.expanduser('~/.config/pay/keypair.json'))"
```

**Prefer explicit paths** (`/root/.config/pay/accounts.yml`) over `$HOME`-based paths in shell scripts that may run in Hermes runtime. When you must use `$HOME`, extract the path from the tool's own error output when possible, or hardcode `/root/` paths for well-known configs.

**Verification:**
```bash
ls -la /root/.config/pay/accounts.yml  # Explicit path — works in any context
```

## Key Lesson
The agent can write credentials correctly but cannot verify them through normal tool output. Always use indirect verification methods (byte counts, hashes, existence checks).

## ElevenLabs Key Format (sk_ prefix)
ElevenLabs now requires API keys to start with `sk_`. Old-format keys (e.g. `82a9e2...`) are rejected with `invalid_api_key_prefix` — "API key must start with 'sk_'." This is a provider format change, not a propagation issue.

**Fix:** Get a fresh key from elevenlabs.io → Profile → API Keys (starts with `sk_`). Update ALL locations atomically:
- `/root/.hermes/profiles/gentech/.env`
- `/root/.hermes/profiles/gentech-treasury/.env`
- `/root/.hermes/.env`
- Scripts read via `os.environ.get("ELEVENLABS_API_KEY")` — so the `.env` update is what matters.

**Verify immediately** with a real API call:
```bash
curl -s "https://api.elevenlabs.io/v1/user" -H "xi-api-key: $KEY"
```
A valid key returns `{"user_id":...}` with subscription info. Check the prefix first: `[[ $KEY == sk_* ]] && echo YES || echo NO`.

## Token Privacy Protocol

When handling sensitive information (API keys, tokens, passwords):

1. **Receive** — Token arrives in conversation
2. **Store** — Write to shared secure path (`/root/.cloudflare-token` for Cloudflare tokens), `chmod 600`
3. **Confirm** — Verify the file was written correctly (`wc -c`, `sha256sum`, `stat`)
4. **Deliver** — Note the path in Forge's handoff so the other agent knows where to find it
5. **Clean** — After confirming delivery, do not echo the value back. The token value stays OUT of conversation history.

**Violation:** Never leave a raw token value visible in chat. Once stored and confirmed, delete the original token text from your response and use only the path reference.

## Classic vs Fine-Grained PATs

**Classic PATs with `repo` scope are more reliable for agent use.** They work for:
- API calls (`/user`, `/repos`, etc.)
- Git operations (push, pull, clone)
- GitHub CLI (`gh` commands)

**Fine-grained PATs** require explicit `Contents: Read and Write` permission on each repository. They often pass API tests but fail git push with "Invalid username or token."

**Recommendation:** For agent automation, use classic PATs unless you need fine-grained repository isolation.

## Git Remote URL Token Embedding

**Problem:** Git remote URLs can contain embedded tokens:
```
origin  https://ghp_OLD_TOKEN@github.com/user/repo.git
```

This overrides the credential helper — even if `~/.git-credentials` has the correct token, git uses the embedded token from the URL.

**Detection:** `git remote -v` shows a token in the URL.

**Fix:**
```bash
git remote set-url origin https://github.com/user/repo.git
```

**Prevention:** Never set remote URLs with tokens. Use credential helpers instead.

## GITHUB_TOKEN Env Var Override

**Problem:** The `GITHUB_TOKEN` environment variable takes precedence over stored credentials. If it contains an expired/invalid token, `gh auth login` fails even with valid stored credentials.

**Detection:** `gh auth status` shows "token is invalid" but `curl -H "Authorization: Bearer $TOKEN" https://api.github.com/user` works.

**Fix:**
```bash
# Option 1: Update the env var
export GITHUB_TOKEN=new_valid_token

# Option 2: Remove the env var and use stored credentials
unset GITHUB_TOKEN

# Option 3: Fix in .env file
sed -i 's/GITHUB_TOKEN=.*/GITHUB_TOKEN=new_valid_token/' ~/.hermes/.env
```

**Pitfall:** The `GITHUB_TOKEN` env var is set in multiple places:
- `~/.hermes/.env` (global profile env)
- `~/.hermes/profiles/<name>/.env` (profile-specific env — **takes precedence** over global)
- Shell profile (`~/.bashrc`, `~/.profile`)
- System environment

**Priority order (highest wins):** At Hermes startup, profiles load their own `.env` which overrides the global `.hermes/.env`. If you cleaned the global env but the profile-specific `.env` still has a stale `GITHUB_TOKEN`, `gh auth status` will report "token is invalid" because the env var shadows every other credential source — including the valid token in `~/.config/gh/hosts.yml`.

**Fix when `gh` CLI has a valid token but `GITHUB_TOKEN` env is stale:**
```bash
# 1. Identify which .env file has the stale value
grep -n 'GITHUB_TOKEN' ~/.hermes/.env ~/.hermes/profiles/*/.env ~/.bashrc 2>/dev/null

# 2. Comment out or remove the stale line in the profile-specific .env
sed -i 's/^GITHUB_TOKEN=.*/# GITHUB_TOKEN removed - use gh hosts.yml token instead/' ~/.hermes/profiles/gentech/.env

# 3. Verify — but note that the current shell STILL has the stale env var exported.
#    New Hermes sessions will pick up the cleaned .env automatically.
#    To test immediately: unset GITHUB_TOKEN && gh auth status
```

**Cron-job note:** Since cron jobs spawn fresh shells, they DO pick up the cleaned `.env` immediately. The stale shell is only this Hermes session; next Hermes restart, it's gone.

Check all locations when troubleshooting — and remember profile-specific `.env` wins over the global one.

## Gitconfig Credential Helper Chain

**Problem:** Git can have multiple credential helpers in a chain. If `gh auth git-credential` is first in the chain and fails, it may return stale credentials before the `store` helper is tried.

**Detection:** `git credential fill` returns wrong token even after updating `~/.git-credentials`.

**Fix:** Simplify the gitconfig to use only the `store` helper:
```ini
[credential]
    helper = store
```

Remove any `gh auth git-credential` entries from `~/.gitconfig` or profile-specific gitconfig.

**Verification:**
```bash
git credential fill <<EOF
protocol=https
host=github.com
EOF
# Should show username and password from ~/.git-credentials
```

## Complete Credential Setup Checklist

When setting up a new agent or rotating tokens:

1. **Generate token:** Classic PAT with `repo` scope (recommended) or fine-grained with `Contents: Write`
2. **Save to file:** Write to `~/.github-token` (or profile-specific path)
3. **Update git-credentials:** Write to `~/.git-credentials` (verify path with `python3 -c "import os; print(os.path.expanduser('~/.git-credentials'))"`)
4. **Update .env:** Set `GITHUB_TOKEN` in `~/.hermes/.env`
5. **Update gh CLI:** `gh auth login --with-token < ~/.github-token`
6. **Clean remote URLs:** `git remote set-url origin https://github.com/user/repo.git` (no embedded tokens)
7. **Simplify gitconfig:** Remove conflicting credential helpers
8. **Verify:** Test API, git push, and `gh` CLI separately
