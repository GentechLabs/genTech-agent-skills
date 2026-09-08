# Bulk Provider Switch via jobs.json

When switching cron jobs between providers (e.g. opencode-go → ollama-cloud), the `cronjob action=update` tool and `hermes cron edit` CLI do NOT support `--model` or `--provider` flags. The actual working approach is editing `jobs.json` directly.

## Discovery (July 26, 2026)

- `cronjob` is NOT a shell command (`cronjob: command not found`)
- `hermes cron edit` does NOT accept `--model`, `--provider`, or `--base-url` arguments
- The canonical data store is `~/.hermes/profiles/<profile>/cron/jobs.json`
- Direct JSON editing + gateway auto-reload = the working approach

## Batch Provider/Mode Switch Pattern

### Step 1: Read and Verify Current State

```bash
cd ~/.hermes/profiles/gentech

python3 -c "
import json
with open('cron/jobs.json') as f:
    data = json.load(f)
targets = ['list-of-job-ids']
for j in data['jobs']:
    if j['id'] in targets:
        print(f\"{j['id']} | prov={j.get('provider','?')} | model={j.get('model','?')}\")
"
```

### Step 2: Update All Jobs in Batch

```python
import json

with open('/root/.hermes/profiles/gentech/cron/jobs.json') as f:
    data = json.load(f)

target_jobs = ['id1', 'id2', ...]  # List of job IDs

for job in data['jobs']:
    if job['id'] in target_jobs:
        job['provider'] = 'new-provider'  # e.g. 'ollama-cloud'
        # Normalize model name (remove provider prefix if present)
        if job.get('model') and 'deepseek-v4-flash' in job['model']:
            job['model'] = 'deepseek-v4-flash'

with open('/root/.hermes/profiles/gentech/cron/jobs.json', 'w') as f:
    json.dump(data, f, indent=2)
```

### Step 3: Verify All Jobs Updated

```bash
python3 -c "
import json
with open('/root/.hermes/profiles/gentech/cron/jobs.json') as f:
    data = json.load(f)
targets = ['list-of-job-ids']
all_ok = True
for j in data['jobs']:
    if j['id'] in targets:
        ok = j.get('provider') == 'ollama-cloud'
        print(f\"{'✅' if ok else '❌'} {j['id'][:12]} prov={j.get('provider','?')}\")
        if not ok: all_ok = False
print(f'All target jobs: {\"✅ ALL ON TARGET\" if all_ok else \"❌ SOME STILL WRONG\"}')
"
```

### Step 4: Gateway Picks Up Changes Automatically

The Hermes gateway reads `jobs.json` on each tick. No restart needed once the file is written. Verify the gateway is running:

```bash
hermes cron status  # Should show "Gateway is running"
```

## Model Name Normalization

Cron jobs may have model names in different formats:
- `deepseek/deepseek-v4-flash` (provider-prefixed)
- `deepseek-v4-flash` (bare, no prefix)

When switching to a provider that uses bare model names (like ollama-cloud), normalize to the provider's expected format. Standard for ollama-cloud is `deepseek-v4-flash` (no provider prefix).

## Cleanup After Switch

If a one-shot orchestrator job was created to trigger the switch (e.g. job id `090e6c76e407`), disable it after completion:

```python
for job in data['jobs']:
    if job['id'] == 'switchover-job-id':
        job['enabled'] = False
        job['state'] = 'completed'
```

## Why This Works Over CLI Approaches

| Method | Supports --model/--provider? | Supports batch? |
|--------|------------------------------|-----------------|
| `hermes cron edit` | ❌ | ❌ |
| `cronjob action=update` | N/A (not a real CLI tool) | ❌ |
| Direct `jobs.json` edit | ✅ (all fields) | ✅ (JSON batch) |

## Verification: Excluding No-Agent Script Jobs

When switching LLM-using cron jobs, you must identify which jobs are **no-agent script runners** (they don't use an LLM at all — they just run a script and deliver stdout). These should NOT be switched.

### How to Identify No-Agent Jobs

From `jobs.json`, a no-agent job has:
```json
"no_agent": true,
"script": "some-script.py"
```

These jobs don't consume LLM inference — they run a local script and deliver its output directly. Changing their provider/model has no effect and is unnecessary.

### Verification Pattern

After switching, verify:
1. **All target jobs** are on the new provider/model
2. **No no-agent jobs** were accidentally switched (they should still have their original provider, or `null` if they never had one pinned)

```python
import json

with open('/root/.hermes/profiles/gentech/cron/jobs.json') as f:
    data = json.load(f)

target_ids = ['list-of-llm-job-ids']
untouched_ids = ['list-of-no-agent-job-ids']

# Check target jobs
for j in data['jobs']:
    if j['id'] in target_ids:
        ok = j.get('provider') == 'ollama-cloud' and j.get('model') == 'deepseek-v4-flash'
        print(f"{'✅' if ok else '❌'} {j['id'][:12]} — {j['name']}")

# Check no-agent jobs were NOT touched
for j in data['jobs']:
    if j['id'] in untouched_ids:
        if j.get('provider') == 'ollama-cloud':
            print(f"❌ {j['id'][:12]} — was accidentally switched!")
        else:
            print(f"✅ {j['id'][:12]} — untouched (provider={j.get('provider')}, no_agent={j.get('no_agent')})")
```

### Common No-Agent Jobs to Exclude

These are typically script-only jobs that should never be switched:
- **CMC Bullish Watchlist** (`cmc-watchlist.py`) — no-agent, no model
- **Gaming Hub Sync** (`gaming-hub-sync.py`) — no-agent, may have stale provider
- **POE2 Build Health** (`gaming-hub-sync.py`) — no-agent, may have stale provider
- **Rate Limit Monitor** (`rate-limit-escalation.py`) — no-agent
- **Vault Watcher** (`vault-watcher-health.sh`) — no-agent, no model
- **GTA Watcher** (`tradesta-watcher.py`) — no-agent, no model
- **GTA Arb Monitor** (`gta-arb-monitor.py`) — no-agent, no model
- **V4 Nightly Maintenance** (`nightly-maintenance.py`) — no-agent, no model
- **API Safety Suite** (`run_safety_suite.py`) — no-agent, no model
- **Fed Event Reminder** (`fed-event-tracker.py`) — no-agent, no model (may be paused)

**Note:** Some no-agent jobs may have a stale `provider: opencode-go` from a previous bulk update that didn't exclude them. This is harmless — the provider field is ignored when `no_agent: true`. But if you want a clean state, you can null them out separately.

## Examples

### Example A: 29-Job ollama-cloud Switch (Jul 27, 2026)

Switched all 29 active LLM-using cron jobs from `opencode-go` (model `deepseek/deepseek-v4-flash`) → `ollama-cloud` (model `deepseek-v4-flash`). Verified all 29 on target, and confirmed 10 no-agent script jobs were NOT touched.

**Job IDs switched:** `cb641608c250`, `79978ef2d03e`, `7ec71332b97c`, `2477e763a78f`, `794982294306`, `fcca23360df2`, `5fb8a3cf8160`, `945edf9409af`, `d8d1c3adbbb4`, `1cd4dd8b3cf0`, `f854e4283771`, `5ef7027eb1db`, `80fd54684d86`, `41f8e6d0e24b`, `c20a22345ba7`, `1c25463fc281`, `e28c895e6a11`, `71d5c3e3b245`, `c00b01c74988`, `e7b632043e30`, `1c1a191de1d2`, `d9e3c68e65e9`, `22d8ad319fd4`, `5f92a9b10032`, `6e771a4bf8a3`, `c1fc1e48409a`, `ac3040c8bf15`, `06af3cfee20c`, `f3e90d867b9c`

**Model name normalization:** `deepseek/deepseek-v4-flash` (provider-prefixed, OpenCode Go format) → `deepseek-v4-flash` (bare, ollama-cloud format).

**Key insight:** `provider_snapshot` entries in jobs.json are historical records, not active provider settings. They do NOT need updating during a provider switch.

### Example B: 20-Job ollama-cloud Switch (Round 1, Jul 26)

Switched 19 jobs from `opencode-go` (model `deepseek/deepseek-v4-flash`) + 1 job from `nous` → `ollama-cloud` (model `deepseek-v4-flash`). All 20 verified on target provider after single file write. Gateway required no restart. Used Python JSON manipulation.

### Example B: 19-Job opencode-go Return (Round 2, Jul 26, this session)

ollama-cloud free tier hit its weekly limit within hours, causing HTTP 429 errors on all LLM cron jobs. Switchback used `patch(replace_all=true)` on jobs.json:

```
old_string='"provider": "ollama-cloud"'
new_string='"provider": "opencode-go"'
replace_all=true
```

Then normalized model names in a second pass:
```
old_string='"model": "deepseek-v4-flash"'
new_string='"model": "deepseek/deepseek-v4-flash"'
replace_all=true
```

Also normalized 2 already-on-opencode-go jobs (Gaming Hub Sync, POE2 Build Health) that still had the old bare model name `"deepseek-v4-flash"`. Clean, fast, no restart needed.

### Example C: 4-Profile Fleet Straggler Sweep (Sep 2, 2026)

Fleet-wide migration to glm-5.3-flash: profiles were flipped via `hermes --profile <P> config set model.default glm-5.3-flash` (verified with `--profile` gets), but cron jobs keep their individually baked-in pins — a global config change does NOT touch jobs.json. Verified sweep pattern in ONE execute_code pass:

```python
import json, os
profiles = ['gentech', 'gentech-treasury', 'gizmo', 'pixel']
base = '/root/.hermes/profiles'
for p in profiles:
    with open(f'{base}/{p}/cron/jobs.json') as f:
        data = json.load(f)
    llm = [(j['id'], j['name'], j.get('provider'), j.get('model'))
           for j in data['jobs'] if j.get('enabled') and not j.get('no_agent')]
    noagent = [j['id'] for j in data['jobs'] if j.get('enabled') and j.get('no_agent')]
    print(f"{p}: {len(llm)} LLM jobs, {len(noagent)} no_agent")
    for jid, name, prov, model in llm:
        if model != 'glm-5.3-flash':  # straggler filter
            print(f"  STRAGGLER {jid} | {name} | {prov}/{model}")
```

Sep 2 result: gentech had 4 nemotron stragglers (c00b01c74988, b14fe104bd1d, 8c8d133f59d7, 3f523dff7d1a) among 23 LLM jobs; treasury (10), gizmo (2), pixel (4) already clean; 37 no_agent jobs untouched. Then per-profile batch re-pin: backup jobs.json first (`jobs.json.bak-model-switch-0902`), set `provider` + `model` on stragglers only, json.dump, read-back verify each target. No gateway restart needed — scheduler reads jobs.json each tick (verified live).

**Key lesson:** never assume a global config flip made the fleet uniform. Jobs carry `provider_snapshot`/pinned values from creation; only a per-job sweep proves the fleet state. Stragglers fail closed (drift_skip) on their next run if unpinned, or silently run the old model if pinned — both wrong after a fleet migration.

## Pitfalls

- **`patch()` with `replace_all` is safe for simple JSON string replacements** — proven working for swapping `"ollama-cloud"` → `"opencode-go"` or normalizing model names. The pattern: `old_string='"provider": "ollama-cloud"', new_string='"provider": "opencode-go"', replace_all=true`. Do NOT use `patch()` for structural changes (adding/removing fields, reordering arrays) — use Python `json.load` + `json.dump` for those.
- **Always back up jobs.json** before editing: `cp jobs.json jobs.json.backup`
- **One-shot jobs** that created this switch task should be disabled post-run to prevent re-triggering
- **Model name format matters** — OpenCode Go uses `deepseek/deepseek-v4-flash` (with slash prefix). Ollama Cloud uses `deepseek-v4-flash` (no prefix). Wrong format = 400 error at inference.
