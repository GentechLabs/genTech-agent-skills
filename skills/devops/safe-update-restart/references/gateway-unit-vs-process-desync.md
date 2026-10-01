# Gateway unit/process desync — probe and reconstruction

When a fleet update or restart fails partway, the **systemd unit** and the **gateway process**
can diverge. The two canonical shapes:

- **Unit `active`, process old** — stale code; the restart never actually happened.
- **Unit `inactive` / `failed`, process alive** — partial restart; systemd lost the unit but
  the orphan gateway is still serving traffic.

Both look healthy from a single signal. Both are caught only by reading both signals.

## The liveness probe

Read unit state and process existence independently, in the same pass. On a multiplexed host
there is only one unit and one process; on a per-profile host there is one per seat. The probe
must match the topology (see `gateway-multiplexer-topology.md`).

```bash
export XDG_RUNTIME_DIR=/run/user/0 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/0/bus

# multiplexed host
unit=$(systemctl --user is-active hermes-gateway.service 2>/dev/null)
pid=$(systemctl --user show -p MainPID --value hermes-gateway.service)
printf '%-18s unit=%-12s mainpid=%s\n' "fleet" "${unit:-unknown}" "${pid:-0}"

# retired per-profile host
for p in gentech gentech-treasury gizmo pixel; do
  unit=$(systemctl --user is-active hermes-gateway-$p.service 2>/dev/null)
  pid=$(pgrep -f "profile $p gateway run" | head -1)
  printf '%-18s unit=%-12s pid=%s\n' "$p" "${unit:-unknown}" "${pid:-NONE}"
done
```

A profile with `pid=NONE` is down. A profile with `unit=inactive` and a real PID is the
partial-restart case.

## Reconstructing the window from systemd

```bash
systemctl --user show hermes-gateway-<profile>.service \
  -p ExecMainPID \
  -p ExecMainStartTimestamp \
  -p ExecMainExitTimestamp \
  -p ActiveEnterTimestamp \
  -p ActiveExitTimestamp \
  -p InactiveEnterTimestamp \
  -p InactiveExitTimestamp \
  -p NRestarts \
  -p Result
```

The gap between `ActiveExitTimestamp` and the next `ActiveEnterTimestamp` is the outage
window as far as systemd is concerned. If a gateway process existed during that window, it
was an orphan.

## Confirming an orphan is actually serving

```bash
journalctl --user -u hermes-gateway-<profile>.service \
  --since '<window-start>' --until '<window-end>' --no-pager
```

Look for:

- request/response lines while the unit was `inactive`
- warnings about mixed modules, old code, or a previous update that did not finish
- the eventual `Started` line that brought systemd back into sync

## Manual rerun of the monitor

If a monitor fires with a desync, do not assume the current state matches the alert:

```bash
cd /root/.hermes/profiles/gentech/scripts
python3 fleet-liveness.py
```

Empty output = healthy now. Non-empty output = the desync is still present. The monitor's
schedule (`*/30 * * * *` in the live case) means an alert can describe a transient state that
already healed.

## What to do when you find a desync

1. **Do not trust the orphan.** It is running code that systemd no longer manages; a later
   operator may restart the unit and be surprised by stale behaviour.
2. **Kill the orphan and restart the unit from a fresh session** — not from inside the gateway
   that may be the orphan. Use a one-shot cron or a detached subprocess if you are running
   inside a gateway.
3. **Verify** with the probe above until `unit=active` and the PID is new and matches the
   install mtime.

## Why both signals are required

`systemctl is-active` can return `active` while the process holds pre-update modules. `pgrep`
can return a PID while systemd considers the unit `inactive`. Each signal answers a different
question; only together do they answer "is this gateway healthy and current?"
