#!/usr/bin/env python3
"""
Hermes Agent Fleet Health Checker
Run: python verify_fleet_health.py

Prints PASS/FAIL for each agent plus overall fleet status.
Exit code: 0 if all healthy, 1 if any degraded, 2 if critical failures.

Usage in cron:
  */5 * * * * /usr/local/lib/hermes-agent/venv/bin/python /root/.hermes/skills/autonomous-ai-agents/agent-fleet-health-audit/scripts/verify_fleet_health.py
"""
import subprocess, json, os, sys, re, datetime

AGENTS = ["yoyo", "dmob", "desmond", "gentech"]
HERMES_BIN = "/usr/local/lib/hermes-agent/venv/bin/python -m hermes_cli.main"

def run(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return r.stdout, r.stderr, r.returncode

def check_process(agent):
    """Return (running:bool, pid:int|None, state:str)"""
    out, _, _ = run(f"pgrep -f 'hermes.*{agent}'")
    pids = [p for p in out.strip().split('\n') if p]
    if not pids:
        return False, None, "NO_PROCESS"
    # Validate each PID with ps - multiple may appear; take first valid
    for pid_str in pids:
        try:
            pid = int(pid_str)
        except:
            continue
        out, _, _ = run(f"ps -p {pid} -o stat,cmd")
        lines = out.strip().split('\n')
        if len(lines) < 2 or lines[0].startswith('PID'):
            continue  # invalid PID
        parts = lines[1].split()
        state = parts[0] if parts else "UNKNOWN"
        cmdline = ' '.join(parts[1:]) if len(parts) > 1 else ""
        # Filter: must be actual gateway run command
        if 'gateway run' not in cmdline:
            continue
        if 'Z' in state:
            return False, pid, "ZOMBIE"
        if 'D' in state:
            return True, pid, "STALLED_IOWAIT"
        return True, pid, "RUNNING"
    return False, None, "NO_VALID_GATEWAY_PROCESS"

def check_log_freshness(agent, max_age_seconds=300):
    """Return (fresh:bool, age_seconds:float)"""
    log = f"/root/.hermes/profiles/{agent}/logs/gateway.log"
    if not os.path.exists(log):
        return False, float('inf')
    stat = os.stat(log)
    mtime = datetime.datetime.fromtimestamp(stat.st_mtime)
    # Read up to 5 last lines to find actual entry timestamp
    out, _, _ = run(f"tail -5 {log}")
    entry_time = None
    for line in reversed(out.split('\n')):
        line = line.strip()
        if not line:
            continue
        match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
        if match:
            try:
                entry_time = datetime.datetime.strptime(match.group(1), '%Y-%m-%d %H:%M:%S')
                break
            except:
                continue
    if entry_time is None:
        return False, float('inf')
    age = (datetime.datetime.now() - entry_time).total_seconds()
    return age <= max_age_seconds, age

def check_errors(agent):
    """Return list of recent ERROR/CRITICAL entries across both logs"""
    errors = []
    for logtype in ['errors.log', 'gateway.log']:
        log = f"/root/.hermes/profiles/{agent}/logs/{logtype}"
        if not os.path.exists(log):
            continue
        out, _, _ = run(f"tail -100 {log}")
        for line in out.split('\n'):
            if any(sev in line.upper() for sev in [' ERROR ', ' CRITICAL ', ' FATAL ']):
                errors.append(line.strip())
    # Deduplicate and return last 5
    seen = set()
    uniq = []
    for e in errors:
        if e not in seen:
            uniq.append(e)
            seen.add(e)
    return uniq[-5:]

def check_marshal_corruption(agent):
    """Check for bytecode corruption errors in recent logs"""
    for logtype in ['errors.log', 'gateway.log']:
        log = f"/root/.hermes/profiles/{agent}/logs/{logtype}"
        if not os.path.exists(log):
            continue
        out, _, _ = run(f"tail -150 {log}")
        if re.search(r'EOFError.*marshal|marshal.*data too short', out, re.IGNORECASE):
            return True
    return False

def check_tts_failure(agent):
    """Check for recent TTS 401 errors"""
    err_log = f"/root/.hermes/profiles/{agent}/logs/errors.log"
    if not os.path.exists(err_log):
        return False
    out, _, _ = run(f"tail -20 {err_log}")
    return bool(re.search(r'elevenlabs.*401|tts.*401|invalid.*api.*key', out, re.IGNORECASE))

def check_cron_orphaned(agent):
    """Check if agent's cron job has never run"""
    try:
        with open('/root/.hermes/cron/jobs.json') as f:
            jobs = json.load(f).get('jobs', [])
    except Exception as e:
        return False, f"JSON parse error: {e}"
    for job in jobs:
        name = job.get('name', '')
        if agent.lower() in name.lower():
            last_run = job.get('last_run_at')
            if last_run is None:
                return True, name
    return False, None

def check_master_service():
    """Check if hermes-gateway.service is healthy"""
    out, _, code = run("systemctl --user status hermes-gateway.service --no-pager")
    if code != 0:
        return False, "systemctl status command failed"
    lowered = out.lower()
    if "active: failed" in lowered or "failed" in lowered:
        return False, "Service in failed state"
    if "loaded" not in lowered:
        return False, "Service not loaded"
    # Check if disabled
    if "disabled" in lowered and "preset: enabled" not in lowered:
        return False, "Service disabled (won't auto-restart)"
    return True, "Active and running"

def main():
    results = {}
    fleet_status = "OK"  # OK, DEGRADED, CRITICAL
    issues = []

    print("=== Hermes Fleet Health Check ===\n")
    
    # Master service check
    master_ok, master_msg = check_master_service()
    print(f"Master service: {'✓ PASS' if master_ok else '✗ FAIL'} — {master_msg}")
    if not master_ok:
        fleet_status = "CRITICAL"
        issues.append(f"Master service: {master_msg}")

    for agent in AGENTS:
        print(f"\n--- {agent.upper()} ---")
        
        # Process
        running, pid, state = check_process(agent)
        if running:
            print(f"  Process: ✓ PID {pid} ({state})")
        else:
            print(f"  Process: ✗ {state} (PID was {pid})")
            fleet_status = "CRITICAL"
            issues.append(f"{agent}: gateway process down ({state})")
        
        # Log freshness (skip if process already down)
        if running:
            fresh, age = check_log_freshness(agent)
            if fresh:
                print(f"  Log activity: ✓ recent ({age:.0f}s)")
            else:
                print(f"  Log activity: ⚠ stale ({age/60:.0f} min)")
                fleet_status = "DEGRADED"
                issues.append(f"{agent}: stale logs ({age/60:.0f} min)")

        # Errors
        errors = check_errors(agent)
        if errors:
            print(f"  Recent ERRORs: {len(errors)} found")
            fleet_status = "DEGRADED"
        else:
            print(f"  Recent ERRORs: none")

        # Marshal corruption
        if check_marshal_corruption(agent):
            print(f"  Bytecode corruption: ⚠️ DETECTED")
            fleet_status = "CRITICAL"
            issues.append(f"{agent}: bytecode corruption (restart needed)")

        # TTS failure
        if check_tts_failure(agent):
            print(f"  TTS: ✗ 401 Invalid key")
            fleet_status = "DEGRADED"

        # Cron orphaned
        orphaned, jobname = check_cron_orphaned(agent)
        if orphaned:
            print(f"  Cron job: ⚠️ never executed ({jobname})")
            fleet_status = "DEGRADED"

    print(f"\n=== FLEET STATUS: {fleet_status} ===")
    if issues:
        print("Issues detected:")
        for issue in issues:
            print(f"  • {issue}")
        sys.exit(1 if fleet_status == "DEGRADED" else 2)
    else:
        print("All agents healthy.")
        sys.exit(0)

if __name__ == "__main__":
    main()
