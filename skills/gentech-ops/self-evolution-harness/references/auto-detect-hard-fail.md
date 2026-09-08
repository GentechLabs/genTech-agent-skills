# Auto-Detect + Hard-Fail Pattern

## Problem

All 5 harness scripts (credential-health.sh, execution-loop.sh, skill-automation.sh, harness-gardener.sh, harness-verify.sh) need to know `HERMES_HOME` to write to the correct facts/ directory. They auto-detect it from the script's location, but if that fails (e.g. script invoked via symlink, from a non-standard workdir, or with readlink unavailable), they silently fell back to `$HOME/hermes-harness` — a path that doesn't exist on this system.

## The Fix (evolve-8, Jul 28 2026)

Replace the silent fallback with a hard error:

```bash
if [[ -z "${HERMES_HOME:-}" ]]; then
    echo "FATAL: cannot determine HERMES_HOME — set HERMES_HOME env var or run from harness/ or harness/scripts/" >&2
    exit 1
fi
```

## Verification

1. `grep -c 'hermes-harness' scripts/*.sh skill-automation.sh` — must return 0
2. `bash scripts/credential-health.sh 2>&1 | grep -q 'FATAL: cannot determine HERMES_HOME'` — must succeed when run outside harness dir without HERMES_HOME set
3. `test ! -f harness/harness/facts/credential-health.log` — phantom log must be gone

## Phantom Path Bug History

- **evolve-2 (Jul 26):** credential-health.sh created with `$HOME/hermes-harness` fallback
- **evolve-3 (Jul 27):** Auto-detect added but fallback kept
- **evolve-8 (Jul 28):** Fallback replaced with hard error. Phantom 0-byte log at `harness/harness/facts/credential-health.log` removed.
