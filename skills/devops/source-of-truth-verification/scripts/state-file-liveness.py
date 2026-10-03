#!/usr/bin/env python3
"""state-file-liveness.py — measure which state files are live, stale, or orphaned.

A state file's name does not prove it is produced or consumed. This script scans
code (scripts that name it) and cron job definitions, then reports:
  LIVE   = named by a script or job, and written recently
  STALE  = named by a script or job, but untouched for N days
  ORPHAN = not named by any script or job

It also flags same-named files in multiple locations whose sizes diverge,
because an audit that picks the wrong copy of a pair reaches a wrong conclusion.

Exits 1 if any orphan or divergent copy is found — useful as a guard.
"""
import argparse
import json
import os
import sys
import time


def walk(root, want):
    if not os.path.isdir(root):
        return []
    out = []
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in ('.git', '__pycache__', 'node_modules', '.pytest_cache', '.venv')]
        out += [os.path.join(dp, f) for f in fn if want(f)]
    return out


def main():
    p = argparse.ArgumentParser(description='Measure state-file liveness across code and cron jobs.')
    p.add_argument('--state-dirs', required=True, nargs='+', help='directories holding state files')
    p.add_argument('--code-dirs', required=True, nargs='+', help='directories holding producer scripts')
    p.add_argument('--jobs-json', help='cron jobs.json to inspect for job-level producers')
    p.add_argument('--stale-days', type=float, default=7.0)
    p.add_argument('--diverge-pct', type=float, default=20.0)
    p.add_argument('--exclude', nargs='*', default=['package.json', 'build_queue.json'],
                   help='basenames to ignore')
    args = p.parse_args()

    now = time.time()
    code = {}
    for d in args.code_dirs:
        for path in walk(d, lambda f: f.endswith(('.py', '.sh'))):
            try:
                code[path] = open(path, encoding='utf-8', errors='ignore').read()
            except OSError:
                pass

    jobs_blob = ''
    if args.jobs_json and os.path.exists(args.jobs_json):
        try:
            jobs_blob = open(args.jobs_json, encoding='utf-8', errors='ignore').read()
        except OSError:
            pass

    state_paths = []
    for d in args.state_dirs:
        state_paths.extend(walk(d, lambda f: f.endswith('.json')))

    by_name = {}
    for path in state_paths:
        b = os.path.basename(path)
        if b in args.exclude:
            continue
        by_name.setdefault(b, []).append(path)

    rows = []
    divergent = []
    for name, paths in sorted(by_name.items()):
        producers = sorted({q for q, t in code.items() if name in t and os.path.basename(q) != name})
        prompters = []
        if jobs_blob:
            try:
                for j in json.loads(jobs_blob).get('jobs', []):
                    if name in json.dumps(j):
                        prompters.append(j.get('name', '?'))
            except json.JSONDecodeError:
                pass
        newest = max(os.path.getmtime(p) for p in paths)
        age = (now - newest) / 86400
        sizes = [os.path.getsize(p) for p in paths]
        if len(paths) > 1 and max(sizes) > 0:
            spread = (max(sizes) - min(sizes)) / max(sizes) * 100
            if spread > args.diverge_pct:
                divergent.append((name, paths, sizes, spread, age))

        if producers or prompters:
            verdict = 'STALE' if age > args.stale_days else 'LIVE'
        else:
            verdict = 'ORPHAN'
        rows.append((verdict, name, age, producers, prompters, paths, sizes))

    order = {'ORPHAN': 0, 'STALE': 1, 'LIVE': 2}
    rows.sort(key=lambda r: (order[r[0]], -r[2]))

    print(f'code scripts: {len(code)} | state files: {len(state_paths)} | cron jobs read: {bool(args.jobs_json)}')
    print()
    print(f'{"verdict":7s} {"file":36s} {"age":>7s}  producers / prompters')
    for v, name, age, prod, pr, paths, sizes in rows:
        print(f'{v:7s} {name:36s} {age:>6.1f}d  scripts={len(prod)} jobs={len(pr)}')
        for path, sz in zip(paths, sizes):
            print(f'             {sz:>10,d}B  {path}')

    if divergent:
        print()
        print(f'DIVERGENT COPIES (>{args.diverge_pct}% size spread): {len(divergent)}')
        for name, paths, sizes, spread, age in sorted(divergent, key=lambda x: -x[3]):
            print(f'  {name}  spread {spread:.0f}%  newest {age:.1f}d')
            for path, sz in sorted(zip(paths, sizes), key=lambda x: -x[1]):
                print(f'    {sz:>10,d}B  {path}')

    if any(r[0] == 'ORPHAN' for r in rows) or divergent:
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()
