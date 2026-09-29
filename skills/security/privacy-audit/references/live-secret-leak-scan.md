# Live Secret Leak Scan — Cross-Check Tracked Files Against .env Values

Regex sweeps of a repository find key-*shaped* strings; they cannot distinguish a live key from a
placeholder, and they miss the ones that matter — a real value pasted into prose or a YAML backup.
**The reliable method is to load the authoritative values from the live `.env` files and search the
tracked tree for those exact values.** False positives collapse to zero, and every hit is a
credential you can prove is live.

## When to use this

- After any session that touched credentials, API keys, or wallet keys.
- Before pushing code, docs, or skills that might have been edited near secrets.
- After discovering one leak — one leak usually means the tree has not been audited before.

## Recipe

### 1. Load authoritative values by SECRET-KEY NAME

Do NOT use a blanket rule like "any value >= 20 characters." That matches benign env vars
(paths, URLs, channel IDs, public identifiers) and floods the report. Use the known secret key
names.

```python
import os, glob

SECRET_KEYS = {
    "API_SERVER_KEY", "HERMES_PEER_GENTECH_KEY", "HERMES_PEER_GENTECH_TREASURY_KEY",
    "HERMES_PEER_GIZMO_KEY", "HERMES_PEER_PIXEL_KEY", "KAPSO_API_KEY", "KAPSO_WEBHOOK_SECRET",
    "ATELIER_API_KEY", "GLM_API_KEY", "OPENROUTER_API_KEY", "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY", "TELEGRAM_BOT_TOKEN", "NOUS_API_KEY", "OLLAMA_API_KEY",
}

secrets = {}  # value -> key_name
for env_path in glob.glob("/root/.hermes/profiles/*/.env") + ["/root/.hermes/.env"]:
    if not os.path.isfile(env_path):
        continue
    for line in open(env_path, errors="ignore"):
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key in SECRET_KEYS and len(value) >= 8:
            secrets[value] = key
```

### 2. Search every tracked file for each value

Use `git ls-tree -r --name-only HEAD` to cover only tracked files. Reading from the index or
HEAD is safer than scanning the working tree, because the working tree may contain untracked
dumps that are not part of the push.

```python
import subprocess

repo = "/root/vaults/gentech"
files = subprocess.run(
    ["git", "ls-tree", "-r", "--name-only", "HEAD"],
    cwd=repo, capture_output=True, text=True, check=True
).stdout.split()

leaks = []
for f in files:
    try:
        text = subprocess.run(
            ["git", "show", f"HEAD:{f}"],
            cwd=repo, capture_output=True, text=True, timeout=8
        ).stdout
    except Exception:
        continue
    for value, key_name in secrets.items():
        if value in text:
            leaks.append((key_name, f))

print(f"Tracked files scanned: {len(files)}")
print(f"Live-secret leaks found: {len(leaks)}")
for key_name, f in leaks:
    print(f"  {key_name} in {f}")   # never print the value
```

### 3. Redact and commit as one action

Redaction without a commit leaves the leak ready to ride out on the next push.

- Replace each live value with a redaction marker keyed by name: `REDACTED-ATELIER_API_KEY`.
- Do NOT print the value in the commit message, the handoff, or the chat log.
- If a file was a credential `.env` tracked in git, use `git rm --cached <path>` and add the
  pattern to `.gitignore`, keeping the file on disk.

```bash
git add <redacted files>
git commit -m "security: redact live credentials from tracked files"
```

### 4. Verify against the remote, not the disk

After pushing, re-scan the remote ref (`vault/main` / `origin/main`) the same way. The disk can
be clean while the remote still carries the secret in an unpushed or cached state.

```python
# Replace HEAD with the remote ref:
# files = git ls-tree -r --name-only vault/main
# text = git show vault/main:<file>
```

### 5. Rotate, don't just delete

A secret that has been in a pushed commit is exposed even after the file is cleaned. Add a
rotation recommendation to the report by key NAME (not value). For peer keys or API keys, rotation
is usually mechanical and should be done immediately; for wallet private keys, rotation may be
more involved.

## Pitfalls

- **Scanning the working tree instead of the index** — untracked cache/scratch files will pollute
  the report and may contain legitimate transient values. Track only what ships.
- **Hidden directories survive a sync** — seat-local `.archive/`, `.cache/`, `.git/`-adjacent dirs,
  and profile scratch paths are excluded from the fleet skills/content sync by default and are
  therefore where old leaks linger longest. A glob like `glob.glob("/root/.hermes/profiles/*/.env")`
  does NOT see `/root/.hermes/profiles/gentech/.archive/secrets.env`. Enumerate hidden dirs
  explicitly or use `os.walk` with `followlinks=False` when the scan must be exhaustive.
- **Printing the secret while reporting it** — the report itself becomes a new leak. Report by
  `key_name + file_path` only.
- **Trusting `.gitignore` for the disk copy and ignoring the tracked index** — a pattern like
  `*.gz` excludes the payload from git, but the *index* of that payload may still be tracked and
  may contain file names or offsets that are sensitive. Verify which one pushed.
- **Forgetting `git rm --cached` for a tracked `.env`** — leaving a tracked `.env` in history is a
  standing leak even if its current content is redacted.
- **Not checking backups and config dumps** — `00-HQ/backups/`, pre-change `.yaml` snapshots,
  and whole-gateway config exports are credential dumps by another name.
