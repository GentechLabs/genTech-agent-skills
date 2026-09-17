# Missing Cron Daemon

## Symptom
- `hermes cron list` returns empty or shows no jobs
- Job output directories exist but no new output files
- Agent logs show no cron-triggered activity despite scheduled times
- No `hermes-cron.service` process running

## Diagnosis
1. Check for cron daemon process:
   ```bash
   ps aux | grep hermes.*cron
   pgrep -f hermes.*cron
   ```
   If no output, daemon is not running.

2. Check systemd unit:
   ```bash
   systemctl --user status hermes-cron.service
   ```
   May show `Unit hermes-cron.service could not be found.` or `inactive (dead)`.

## Root Causes
- Cron service crashed or was killed
- Hermes update removed or renamed the cron service unit
- Systemd user instance not running or not loading units
- Cron daemon disabled (`systemctl --user disable hermes-cron.service`)

## Recovery
1. Ensure Hermes installation is intact:
   ```bash
   ls ${INSTALL_DIR}/venv/bin/hermes
   ```

2. Start cron daemon manually (temporary):
   ```bash
   hermes cron start
   ```
   Or if using systemd:
   ```bash
   systemctl --user enable --now hermes-cron.service
   ```

3. Verify daemon is running and jobs dispatch:
   ```bash
   ps aux | grep hermes.*cron
   hermes cron list
   ```

4. If service unit missing, regenerate from installed unit file or re-enable via `hermes setup`.

## Verification
- `hermes cron list` shows expected active jobs with next run times
- Job output appears in `~/.hermes/cron/output/<job-id>/` within scheduled window
- Subsequent watchdog checks report cron health OK