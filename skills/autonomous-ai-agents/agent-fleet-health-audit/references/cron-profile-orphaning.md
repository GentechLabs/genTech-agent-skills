# Cron Job Profile Orphaning — Detection & Recovery

## Symptom
Jobs appear in `~/.hermes/cron/jobs.json` (or global registry) with `profile: ?` or `profile: null` and `last_run_at: null` — they never execute despite being enabled and scheduled.

## Root Causes
1. **Scheduler pipeline desync** — global jobs registry not loaded into agent cron registries
2. **Profile assignment missing** — job creation without specifying which agent should run it
3. **Cross-contamination** — agent-level `jobs.json` files contain jobs belonging to other agents (wrong `origin` field)

## Detection
```bash
# Check global registry for jobs with missing profile
hermes cron list --all | grep -E "profile.*\?"

# Inspect raw JSON
jq '.[] | select(.profile == null or .profile == "?")' ~/.hermes/cron/jobs.json

# Cross-check per-agent registries
for agent in yoyo dmob desmond gentech; do
  echo "=== $agent ==="
  jq '.[] | select(.origin and (.origin | contains($agent) | not))' ~/.hermes/profiles/$agent/cron/jobs.json 2>/dev/null || true
done
```

## Recovery Sequence
1. **Identify orphaned jobs**
   ```bash
   # List all jobs with no profile
   jq -r '.[] | select(.profile == null or .profile == "?") | "\(.id) \(.name)"' ~/.hermes/cron/jobs.json
   ```

2. **Determine correct owner agent**
   - Check job `origin` field or naming convention (e.g., "YoYo —" → yoyo profile)
   - If ambiguous, check job's `prompt`/`script` for agent-specific references

3. **Assign profile**
   - Edit `~/.hermes/cron/jobs.json` and set `"profile": "<agent>"` for each orphaned job
   - Alternatively, use `hermes cron assign --id <jobid> --profile <agent>` if available

4. **Reload cron registry**
   ```bash
   # Stop gateways, rebuild registry, restart
   systemctl --user stop hermes-gateway-*.service
   rm -f ~/.hermes/cron/jobs.db
   hermes cron rebuild-registry
   systemctl --user start hermes-gateway-*.service
   ```

5. **Validate**
   ```bash
   hermes cron list | grep -E "YoYo|DMOB|Desmond|Gentech"
   # Should show enabled state and upcoming next_run times
   ```

## Common Pitfalls
- **Do not assume** that `hermes cron list` output is complete — use `--all` flag to expose hidden/orphaned entries
- Jobs with `profile: null` in `jobs.json` will NOT be loaded into any agent's active registry regardless of `enabled: true`
- Cross-contamination: agent-level `jobs.json` files often contain jobs from other agents; these will fail with `profile does not exist` errors when executed
- After fixing profiles, always verify `jobs.db` is regenerated (non-zero filesize) and gateways restarted
