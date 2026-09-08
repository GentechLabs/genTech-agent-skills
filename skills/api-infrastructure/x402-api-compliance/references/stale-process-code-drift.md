# Stale-Process Code Drift — the "dexter unreachable" settlement blocker (Aug 19, 2026)

## Symptom
Every x402 self-settle fails `payment_proof_invalid / dexter unreachable` even though the
on-disk gateway code (in the service `WorkingDirectory`) already removed Dexter and routes
Base→CDP. The gateway looks healthy (health endpoint 200, services listed) but no payment
ever settles.

## Root cause
The running `x402-api.service` process was started **before** the `server.py` code edit, so
it is executing a **previous version** of the file whose verify dispatch still routes through
a dead Dexter facilitator. The on-disk code is correct; the process is stale. This is the
code-drift twin of the stale-credential trap (process holds old env) — here the drift is the
loaded source file, not the env.

## Diagnosis — confirm which server.py the process actually loaded
```bash
# 1. Find the gateway PID on its port
ss -tlnp | grep ':8090' | grep -oP 'pid=\K[0-9]+'
# 2. Its cwd = the loaded source dir
readlink /proc/<pid>/cwd
# 3. grep the ACTUAL loaded file for the dead path
grep -rl "dexter unreachable" <that-cwd>/server.py   # hit = stale code running
```
Compare against the current on-disk code in the service `WorkingDirectory`
(`systemctl cat x402-api.service` → `WorkingDirectory=`). If they differ, the process is stale.

## Fix
```bash
systemctl restart x402-api.service
```
No config change needed — the restart loads the current on-disk code. Verify the new PID's
cwd + that the dead path is gone from the loaded file, then re-run the self-settle.

## Proof it worked (Aug 19, 2026)
After restart, the first real on-chain settlement landed: arb wallet `0x3d117…` Base USDC
dropped **0.466002 → 0.451002 = 0.015 USDC settled** through the CDP facilitator. Gateway log
confirmed `cdp returned valid=True reason='verified + settled'`. The client-side 402 was a
response-handling artifact, not a rejection.

## Rule
When deployed code was edited, the running process is stale until restarted. **Verify process
start time + which file it loaded BEFORE debugging the protocol.** A plain restart beats a
code "fix" for a non-existent bug. Same class as the stale-credential trap in the main skill.
