# Cron HOME Environment Bug

**Problem:** Cron jobs fail with "file not found" errors pointing to `/root/home/.hermes/...` even though the config exists at `/root/.hermes/...`.

**Root Cause:** The cron daemon inherits a HOME environment that doesn't match the user's actual home directory. When Python scripts use `os.path.expanduser('~/.hermes/...')`, this expands to `$HOME/.hermes/...`. If `HOME=/root/home` (non-existent) instead of `/root`, the path is invalid.

**Typical Error:**
```
ERROR: AAE config missing: [Errno 2] No such file or directory: '/root/home/.hermes/scripts/.lfj-aae-config.json'
```

**Detection:**
1. Check cron log path — if it shows `/root/home/` instead of `/root/`, HOME is wrong
2. Run `ps aux | grep cron` and inspect environment: `cat /proc/<cron-pid>/environ | tr '\0' '\n' | grep HOME`
3. Compare against `getent passwd root` — root's home should be `/root`

**Why This Happens:**
- Cron on some systems defaults HOME to `/home/<user>` derived from passwd, but root's home is `/root`. A misconfiguration can leave HOME as `/root/home`.
- The crontab entry itself may set `HOME` incorrectly.
- Systemd user instances may inject a different HOME than expected.

**Fix Options:**
1. **Fix crontab entry** — either remove any `HOME=` line or set it correctly:  
   `HOME=/root` at top of crontab or inline:  
   `*/10 * * * * HOME=/root /usr/bin/env python3 /path/to/script.py`
2. **Patch the script** — avoid `os.path.expanduser('~/.hermes/...')`. Use:
   ```python
   import os
   HERMES_HOME = os.environ.get('HERMES_HOME', '/root/.hermes')
   CONFIG_PATH = os.path.join(HERMES_HOME, 'scripts', '.lfj-aae-config.json')
   ```
   Or use absolute paths directly: `/root/.hermes/scripts/...`
3. **Set HOME globally for cron** — edit `/etc/crontab` or `/etc/environment` to define `HOME=/root` for root user.
4. **Verify fix:** After change, manually run the cron command with `env -i HOME=/root /usr/bin/env python3 script.py` to simulate corrected environment.

**Related Pitfalls:**
- Stale `.pyc` files can persist after fixing the path — delete `__pycache__/` in script directory to prevent continued failures.
- Cron may have already written error entries to the log; fixing the bug won't clear them. Verify by checking log mtime updates after next scheduled run.

**Affected Scripts (May 03 2026):**
- `${PROFILES_DIR}/yoyo/scripts/defi-milestone-tracker.py` — fixed by explicit path; still needs `.pyc` cleanup.
