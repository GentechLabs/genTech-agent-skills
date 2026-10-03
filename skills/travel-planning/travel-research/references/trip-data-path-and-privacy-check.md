# Trip Data Path & Privacy Check

## When to use this reference

You are about to update a shared/public travel hub, dashboard, or itinerary feed that is generated from a source file in the vault and served from a public repo or webroot.

## Data-path audit

A travel record often exists in three generations at once:

1. **Vault source** — the JSON/Markdown an agent edits
2. **Generated live feed** — e.g. `travel-live.json`, rebuilt by a cron script
3. **Served public copy** — repo, webroot, GitHub Pages

### Find the live source before editing

```bash
# Which file does the generator actually read?
grep -R "travel-.*\.json" ${PROFILE_DIR}/scripts/ ${PROFILE_DIR}/cron/ -l

# Example of a healthy, explicit data path
# build-travel-live.py line 43:
#   source = Path("/root/vaults/gentech/Travel/travel-jordan.json")
# If the generator reads the vault, edit the vault source.
# If the generator reads the repo, edit the repo source.
```

### Sync after editing

```bash
# Run the generator (it usually writes multiple surfaces)
python3 ${PROFILE_DIR}/scripts/build-travel-live.py

# Or copy explicitly if no generator exists
cp ${VAULT_DIR}/Travel/travel-jordan.json \
   /root/repos/gentechlabs.github.io/Travel/travel-jordan.json
cp ${VAULT_DIR}/Travel/travel-live.json \
   /var/www/gentechlabs/Travel/travel-live.json

# Compare bytes across all surfaces
md5sum ${VAULT_DIR}/Travel/travel-*.json \
       /root/repos/gentechlabs.github.io/Travel/travel-*.json \
       /var/www/gentechlabs/Travel/travel-*.json
```

### Verify the live surface

```bash
# Read the served bytes, not the local file
curl -s https://gentechlabs.net/Travel/travel-live.json | python3 -m json.tool
curl -s https://gentechlabs.net/Travel/travel-jordan.json | python3 -m json.tool
```

**Failure pattern:** the agent updates the repo JSON, reports "done", but the web page still shows the old plan because the cron generator overwrites the repo file from the vault every 24 hours. Fix: edit the source the generator reads.

## Companion privacy

When a traveler changes status (e.g. solo → couple), two records need care:

1. **Trip JSON** — set `traveler` to the display string and add a machine-readable `companion` field:
   ```json
   {
     "traveler": "Jordan & Josephine",
     "companion": "Josephine",
     "companion_note": "Traveling together. Added 2026-10-01."
   }
   ```
   This prevents a future agent from inferring the relationship from a display string that could change.

2. **Photos** — a partner's photo must not be published on a public surface without explicit approval.

### Photo sweep before publishing

```bash
# Is the photo sitting untracked in a public repo?
git -C /root/repos/gentechlabs.github.io status --porcelain | grep -i "\.jpg\|\.png\|\.webp"

# If yes, move it to the private vault (vault is a separate repo and .gitignore excludes *.jpg)
mkdir -p ${VAULT_DIR}/00-HQ/private-photos/
mv /root/repos/gentechlabs.github.io/Travel/images/<name>.jpg \
   ${VAULT_DIR}/00-HQ/private-photos/<name>-YYYY-MM-DD.jpg
```

**Risk:** public-site repos that other agents commit to with `git add -A` will sweep untracked images into a commit and publish them. **Moving the file is not enough** if a stale process or another agent still has it in the repo; keep it out of any directory that deploys to the web.

**Decision boundary:** publishing a companion's photo is the traveler's call, not the agent's. If a photo arrives, store it privately, report that you have it, and ask before publishing.

## Related skills

- `public-artifact-verification` — verify outward-facing artifacts as the consumer sees them
- `source-of-truth-verification` — find the code/file that actually runs
