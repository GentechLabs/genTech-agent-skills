---
name: drive-file-transfer
description: Use when an agent must push files from the VPS/workstation to Google Drive, or pull them back. Covers the Composio path (agent file transfer), the rclone path (bulk), and the one hard rule — the vault never goes to Drive.
---

# Drive file transfer (agent → Google Drive)

**The rule that outranks everything here:** `${VAULT_DIR}` (the brain) **NEVER** goes
on Drive. It holds credentials, tokens and handoffs, and a copy on a third party's servers is
one we can never fully recall. **Vanito's work and agent deliverables: yes. The vault: no.**

## Path A — Composio (agent file transfer, the default)

**Verified live 2026-09-14.** Composio-managed OAuth — no Google Cloud project needed.

**Credential:** `COMPOSIO_API_KEY` in `${PROFILE_DIR}/.env` (never inline in config — config
gets committed, `.env` doesn't).

**Connection:** `user_id=gentech`, connected account `ca_e3m5YNqM4MRB` (googledrive, ACTIVE).
Check it any time:

```bash
curl -sS "https://backend.composio.dev/api/v3/connected_accounts" -H "x-api-key: $COMPOSIO_API_KEY"
```

**Run a tool** — `user_id` is REQUIRED alongside `connected_account_id`, or you get
`ActionExecute_ConnectedAccountEntityIdRequired`:

```bash
curl -sS -X POST \
  "https://backend.composio.dev/api/v3/tools/execute/GOOGLEDRIVE_CREATE_FOLDER" \
  -H "x-api-key: $COMPOSIO_API_KEY" -H "Content-Type: application/json" \
  -d '{"connected_account_id":"ca_e3m5YNqM4MRB","user_id":"gentech",
       "arguments":{"folder_name":"Folder Name"}}'
```

**Tool slugs that matter:** `GOOGLEDRIVE_CREATE_FOLDER` (takes `folder_name`, **not** `name`),
`GOOGLEDRIVE_CREATE_FILE_FROM_TEXT`, `GOOGLEDRIVE_UPLOAD_FILE`, `GOOGLEDRIVE_LIST_FILES`,
`GOOGLEDRIVE_GOOGLE_DRIVE_DELETE_FOLDER_OR_FILE_ACTION` (there is **no** `DELETE_FILE` slug).
**Delete arg is `fileId`** (verified 2026-09-14) — `GOOGLEDRIVE_GOOGLE_DRIVE_DELETE_FOLDER_OR_FILE_ACTION`
takes `{"fileId": "<id>"}`; both `id`/`item_id` and the bare `DELETE_FILE`/`GOOGLEDRIVE_DELETE` slugs
404 or "missing field". Move/rename slug is `GOOGLEDRIVE_MOVE_FILE` (takes `fileId`).

### 📎 BINARY files (PDF, PNG, MP4) — three steps, proven 2026-09-14

`CREATE_FILE_FROM_TEXT` is **text only**. Binaries need the staging flow:

```python
from composio import Composio
import hashlib, httpx
c = Composio(api_key=COMPOSIO_API_KEY)
data = open(path, "rb").read()
md5  = hashlib.md5(data).hexdigest()

# 1. presign — returns .key (the s3key) and .new_presigned_url
resp = c.client.files.create_presigned_url(
    filename="x.pdf", md5=md5, mimetype="application/pdf",
    tool_slug="GOOGLEDRIVE_UPLOAD_FILE", toolkit_slug="googledrive")

# 2. push the bytes
httpx.put(resp.new_presigned_url, content=data,
          headers={"Content-Type": "application/pdf"}, timeout=120)

# 3. attach it
c.tools.execute(slug="GOOGLEDRIVE_UPLOAD_FILE",
    arguments={"file_to_upload": {"name": "x.pdf", "mimetype": "application/pdf",
                                  "s3key": resp.key},
               "folder_to_upload_to": FOLDER_ID},
    connected_account_id=ACCT, user_id="gentech",
    dangerously_skip_version_check=True)
```

**⚠️ `files` lives on the INNER client: `c.client.files`, not `c.files`.** Checking `dir(c)`
and concluding "no file API" is **wrong** — that mistake was made once already. Look inside
`c.client`.

### 🔍 THE STEP THAT WAS MISSING — check the source before concluding "it doesn't exist"

**Jordan, 2026-09-14:** *"this only happened because I gave you the information for Composio,
but you didn't think — let me check out their GitHub first, let me look at their docs first
before I do this, to make sure to verify everything is in order."*

**Rule: "I looked and didn't find it" is NOT "it doesn't exist."**

Before reporting any capability as missing, do these **in order** — cheap, and each one is
seconds:

1. **The vendor's docs** — search them directly, don't skim:
   `https://docs.composio.dev/api/knowledge-search?q=<your question>`
2. **The vendor's GitHub** — search the code, not just the README:
   `gh api "search/code?q=repo:ComposioHQ/composio+<term>" --jq .total_count`
3. **One level deeper in the client** — `dir(c)` is not the whole object. Check `c.client`,
   sub-resources, and `inspect.signature` on anything promising.
4. **Then** conclude. A negative finding is a claim like any other and carries the same
   burden of proof.

**Why it matters here specifically:** this cost an hour and nearly produced a bug report
against a healthy 30k-star project. **A false negative reported outward is worse than a
missing feature — it spends someone else's time on our oversight.**


**Pitfall — argument names are not guessable.** `CREATE_FOLDER` takes `folder_name`, **not**
`name`. **Read the error and use what it names** — don't retry the same guess.

**Always read back.** A `successful: true` is the API's claim; `GOOGLEDRIVE_LIST_FILES` is the
proof. Verify with a listing before reporting success.

## Path B — rclone (bulk moves, e.g. multi-GB)

Composio is for **files**; rclone is for **bulk**. Vanito's 4.4 GB handoff is a Path B job.
Same rule applies: his work only, never the vault.

## Established folders

| Folder | ID | Use |
|---|---|---|
| GenTech - Vanito Handoff | `1VMA6WRGqSwrbUZkh5x1ur5ujU32pO6Dz` | Vanito's frozen work before he switches out (Oct) |

## Open items

- **Rotate the key** — it transited a chat channel, so copies exist that we can't scrub.
  Working now, but rotation is owed.
- Stale **Gmail** connections (4) all EXPIRED — re-auth only if Gmail is ever needed.
