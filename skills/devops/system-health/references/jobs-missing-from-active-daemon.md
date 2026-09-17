### Job Definitions Present in Snapshot but Missing from Active Daemon

**Pattern:** Jobs exist in historical or backup `jobs.json` files (e.g., `~/.hermes/state-snapshots/<timestamp>/cron/jobs.json` or `~/.hermes/cron/jobs.json`) but do not appear in `hermes cron list` output. These jobs show `last_run_at: null` and `hermes cron status <job_id>` returns a usage error (unknown job ID).

**Typical cause:** Profile configuration was written to disk but never registered with the cron daemon, or a migration/restore incomplete. Observable when:
- A fresh multi-agent setup finishes but agent-specific dailies never fire.
- After a hermes-agent upgrade or state restore where the cron scheduler's in-memory registry was not repopulated from the on-disk config.
- Gateway restarts that don't re-hydrate the cron scheduler from `jobs.json`.

**Diagnostic commands:**
```bash
# 1. Check active cron daemon
hermes cron list

# 2. Check on-disk config (primary)
cat ~/.hermes/cron/jobs.json | python3 -m json.tool | grep -E '"id"|"name"'

# 3. Check state snapshot (if recent backup exists)
cat ~/.hermes/state-snapshots/$(ls -t ~/.hermes/state-snapshots | head -1)/cron/jobs.json | \
  python3 -m json.tool | grep -E '"id"|"name"'

# 4. Diff: jobs in snapshot but not active
python3 -c "
import json, subprocess, os
# Load active
active = subprocess.run(['hermes','cron','list'], capture_output=True, text=True).stdout
active_ids = set()
for line in active.split('\n'):
    if line.strip().startswith('[') and len(line.strip()) > 3:
        parts = line.split()
        if len(parts) > 0:
            active_ids.add(parts[0].strip('[]'))
# Load on-disk
with open(os.path.expanduser('~/.hermes/cron/jobs.json')) as f:
    disk = json.load(f)
disk_ids = {j['id'] for j in disk.get('jobs', [])}
missing = disk_ids - active_ids
print('Missing from active daemon:', missing)
"
```

**Recovery path:**
```bash
# Re-register missing jobs from on-disk config
# Option A: restart all gateways (simplest; hermes auto-registers jobs at startup)
hermes gateway run --profile desmond --replace
hermes gateway run --profile dmob    --replace
hermes gateway run --profile gentech --replace
hermes gateway run --profile yoyo    --replace

# Option B: explicit cron create for each missing job (if gateway restart not desired)
for job_id in $(cat ~/.hermes/cron/jobs.json | python3 -c "
import json, sys
data = json.load(sys.stdin)
for j in data.get('jobs', []):
    if j['id'] in ('<missing-id-1>','<missing-id-2>'):  # populate from diff
        print(f\"{j['id']} {j['name']} {j['schedule']['expr']}\")
");
do
  hermes cron create --name "<job name>" --schedule "<cron expr>" --prompt "<prompt text>" --profile <profile>
done
```

**Validation:**
```bash
# After recovery, confirm all expected jobs appear
hermes cron list | grep -E '<job-name-pattern>'

# Check next_run_at is in the future
hermes cron list | grep -A1 '<job-id>'
```

**Related:** See also `references/watchdog-health-2026-05-01.md` for session evidence — 4 agent dailies (Desmond Creative Sync, Gentech HQ Update, YoYo LP Watchlist, DMOB Labs Standup) discovered missing from active daemon despite existing in snapshot.
