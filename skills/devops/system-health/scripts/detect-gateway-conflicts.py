#!/usr/bin/env python3
"""
Gateway Port Conflict Detector
Detect and resolve multiple gateway processes binding to same ports
"""

import subprocess
import json
import sys
from typing import List, Dict, Tuple

def get_gateway_processes() -> List[Dict]:
    """Find all running gateway processes"""
    try:
        result = subprocess.run(
            ["ps", "aux"], 
            capture_output=True, text=True, check=True
        )
        
        processes = []
        for line in result.stdout.split('\n'):
            if 'gateway' in line and 'python' in line:
                parts = line.split()
                if len(parts) >= 2:
                    pid = parts[1]
                    cmd = ' '.join(parts[10:])
                    if '--port' in cmd:
                        # Extract port number
                        port = cmd.split('--port')[1].split()[0] if '--port' in cmd else 'unknown'
                        processes.append({
                            'pid': pid,
                            'cmd': cmd,
                            'port': port
                        })
        return processes
    except subprocess.CalledProcessError:
        return []

def get_port_usage() -> Dict[str, str]:
    """Get which ports are currently in use"""
    try:
        result = subprocess.run(
            ["netstat", "-tlnp"], 
            capture_output=True, text=True, check=True
        )
        
        port_usage = {}
        for line in result.stdout.split('\n'):
            if 'LISTEN' in line and '.py' in line:
                parts = line.split()
                if len(parts) >= 7:
                    port = parts[3].split(':')[-1]
                    pid = parts[6].split('/')[0]
                    port_usage[port] = pid
        return port_usage
    except subprocess.CalledProcessError:
        return {}

def check_conflicts() -> Tuple[List[Dict], List[str]]:
    """Check for port conflicts"""
    processes = get_gateway_processes()
    port_usage = get_port_usage()
    
    conflicts = []
    all_ports = []
    
    for process in processes:
        port = process['port']
        if port != 'unknown' and port in port_usage:
            # Check if multiple processes are using the same port
            port_processes = [
                p for p in processes if p['port'] == port
            ]
            
            if len(port_processes) > 1:
                conflicts.append({
                    'port': port,
                    'processes': port_processes,
                    'pids': [p['pid'] for p in port_processes]
                })
        all_ports.append(port)
    
    return conflicts, all_ports

def display_status():
    """Display current gateway status"""
    print("=== Gateway Port Conflict Detector ===")
    print()
    
    conflicts, all_ports = check_conflicts()
    
    if conflicts:
        print("🚨 CONFLICTS DETECTED:")
        for conflict in conflicts:
            print(f"  Port {conflict['port']} used by PIDs: {', '.join(conflict['pids'])}")
        print()
    
    print("📊 Current Gateway Processes:")
    processes = get_gateway_processes()
    if processes:
        for process in processes:
            print(f"  PID {process['pid']}: {process['port']} - {process['cmd'][:60]}...")
    else:
        print("  No gateway processes found")
    print()
    
    print("🔍 Port Usage:")
    port_usage = get_port_usage()
    if port_usage:
        for port, pid in port_usage.items():
            print(f"  Port {port}: PID {pid}")
    else:
        print("  No Python processes found in LISTEN state")
    
    if conflicts:
        print("\n⚠️  CONFLICT RESOLUTION:")
        print("Run with --resolve to automatically fix conflicts")
        return 1
    else:
        print("✅ No conflicts detected")
        return 0

def resolve_conflicts():
    """Resolve port conflicts by killing redundant processes"""
    conflicts, _ = check_conflicts()
    
    if not conflicts:
        print("No conflicts to resolve")
        return 0
    
    print("🔨 RESOLVING CONFLICTS:")
    for conflict in conflicts:
        port = conflict['port']
        pids = conflict['pids']
        
        # Keep the first process, kill others
        for pid in pids[1:]:  # Skip first (keep it)
            print(f"  Killing PID {pid} (port {port})")
            try:
                subprocess.run(["kill", "-9", pid], check=True)
                print(f"    ✅ PID {pid} killed")
            except subprocess.CalledProcessError as e:
                print(f"    ❌ Failed to kill PID {pid}: {e}")
        
        # Clean up stale lock files
        print(f"  Cleaning stale lock files for port {port}")
        try:
            subprocess.run(
                ["find", "/root/.hermes/profiles", "-name", f"gateway.*{port}*", "-delete"], 
                capture_output=True
            )
            print("    ✅ Lock files cleaned")
        except subprocess.CalledProcessError as e:
            print(f"    ❌ Failed to clean lock files: {e}")
    
    print("\n✅ Conflicts resolved")
    return 0

def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] == "--resolve":
        return resolve_conflicts()
    else:
        return display_status()

if __name__ == "__main__":
    sys.exit(main())