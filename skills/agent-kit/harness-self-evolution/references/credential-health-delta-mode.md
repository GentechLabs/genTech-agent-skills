# credential-health delta-mode masking repeated failures (Aug 5, 2026)

## Symptom
`bash scripts/credential-health.sh` prints `credential-health: all probes OK` (exit 0)
while the underlying probe genuinely fails — e.g. `gh auth status` returns "token is
invalid" / exit 1, or the direct token test returns 401.

## Root cause
`_log_status()` in `scripts/credential-health.sh` dedups log writes via delta mode:

```bash
last_status=$(grep "| ${provider}=" "$CREDENTIAL_LOG" | tail -1 | grep -oP "${provider}=\K\S+")
if [[ "$last_status" == "$status" ]]; then
    return 0            # ← early return skips ALL_OK=false
fi
echo "[...] | ${provider}=${status} | ..." >> "$CREDENTIAL_LOG"
if [[ "$status" != "200" ]] ... ; then
    ALL_OK=false        # ← only reached on a NEW status
fi
```

A 401 is logged once. Every subsequent 401 hits the early `return 0` and never reaches
the `ALL_OK=false` update, so `ALL_OK` stays true and the probe reports green forever.

## Fix (shipped, commit 62de7f2)
Move the `ALL_OK=false` update BEFORE the delta-mode early return:

```bash
if [[ "$status" != "200" ]] && [[ "$status" != "SKIP" ]] \
    && [[ "$status" != "FORMAT_OK" ]] && [[ "$status" != "NO_ACCOUNT" ]] \
    && [[ "$status" != "NO_KEYPAIR" ]] && [[ "$status" != "PAY_OK" ]]; then
    ALL_OK=false        # always — even when the log write is suppressed
fi

if [[ "$last_status" == "$status" ]]; then
    return 0
fi
echo "[...] | ${provider}=${status} | ..." >> "$CREDENTIAL_LOG"
```

Now a repeated 401 still flips ALL_OK and the probe returns exit 1 ("one or more probes
FAILED").

## Verification
- `bash -n scripts/credential-health.sh` — syntax clean
- With a dead token: `bash scripts/credential-health.sh` → `one or more probes FAILED`, exit 1
  (previously the false `all probes OK`, exit 0)

## Generalised rule
A delta/suppression gate that skips an audit-write must NOT skip the state update the
final result depends on. Dedup the log line, never the failure signal. The result boolean
and the log-dedup are two different effects of one function call — a guard that returns
early for dedup must do the state bookkeeping before the return.
