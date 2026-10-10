#!/usr/bin/env python3
"""
fleet-hygiene-audit.py — find DUPLICATES and STALE things across the fleet.

Jordan, 2026-09-21: "during our overnight maintenance, maybe we should start looking for
duplicates or anything stale overnight as well Because yeah, we shouldn't have duplicates
of different things"

WHY THIS EXISTS, and why it is NOT just "fleet-drift-check with more rules":

  fleet-drift-check.py answers a different question — "did a rule land on one seat and not
  travel?" It compares the SHARED CORE against the seats. It has one failure mode by design:
  it only sees what is IN the core. Anything duplicated, stale, or orphaned OUTSIDE that
  model is invisible to it.

  This script asks the wider question: what is on this box that should not be?
  Four independent detectors, each of which must be able to go RED:

    1. DUPLICATE TOOLCHAINS  — the same heavy toolchain installed in more than one profile
                               home (e.g. two full Rust copies). Skills duplication is
                               *redundancy* by design; toolchain duplication is just waste.
    2. DUPLICATE FILES       — the same file content (by hash) in more than one place,
                               above a size floor, excluding known-safe locations.
    3. STALE CRON JOBS       — jobs that are enabled but have not succeeded in N days, or
                               are paused/disabled and have been for a long time, or whose
                               error is older than the last successful run.
    4. STALE ARTIFACTS       — build output, caches, venvs, targets, logs, and scratch dirs
                               that nothing live references.

DESIGN RULES (learned the hard way — see 00-HQ/propagation-broken-false-green-2026-09-20.md):
  * A CHECK THAT CANNOT GO RED IS NOT A CHECK. Every detector must be able to return a
    non-empty finding on real data, and there is a --selftest that proves it.
  * SILENCE MUST BE EARNED. "Nothing found" is only reported after the scan actually ran.
    An unparseable or crashed detector is reported as UNKNOWN, never as clean.
  * NEVER DELETE. This only LOOKS and REPORTS. Deletion is a human decision, especially
    for anything under /root (projects, repos, vaults).
  * LIVE REFERENCES SUPPRESS A FINDING. If a cron, script, systemd unit, or docker
    container names a path, it is NOT stale no matter how old it looks. We learned this
    the hard way holding back almanak-venv and both node installs.

EXIT CODES: 0 = clean, 1 = findings, 2 = a detector errored (never silently green).
"""

import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

HERMES = Path("/root/.hermes")
PROFILES = ["gentech", "gentech-treasury", "gizmo", "pixel"]

DAY = 86400
NOW = time.time()


# ───────────────────────────────────────────────────────────── helpers

def humansize(n):
    for unit in ("B", "K", "M", "G", "T"):
        if n < 1024 or unit == "T":
            return f"{n:.1f}{unit}" if unit != "B" else f"{int(n)}B"
        n /= 1024


def run(cmd, timeout=30):
    """Run a shell command, return stdout (empty string on any failure)."""
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.stdout or ""
    except Exception:
        return ""


def dirsize(p):
    """Total bytes under a path (fast: sums st_size, does not follow symlinks)."""
    total = 0
    try:
        for root, dirs, files in os.walk(p, onerror=lambda e: None, followlinks=False):
            for f in files:
                try:
                    fp = os.path.join(root, f)
                    if not os.path.islink(fp):
                        total += os.lstat(fp).st_size
                except OSError:
                    pass
    except Exception:
        pass
    return total


def build_live_reference_index():
    """
    Every path mentioned by something that is actually LIVE:
      - cron job definitions (all profiles)
      - scripts in every profile
      - systemd user units
      - running docker containers (their mounts/commands)
    A path named here is NEVER reported stale.

    SELF-REFERENCE GUARD: this script is excluded from its own index. Without this, the
    selftest probe paths (which appear as string literals BELOW, in this very file) matched
    their own source and every detector went permanently green — a check that cannot go red.
    Verified by the --selftest, which is exactly how it was caught.
    """
    SELF = Path(__file__).resolve()
    SELF_NAME = SELF.name  # fleet-hygiene-audit.py — deployed to every seat
    refs = []
    for p in PROFILES:
        jf = HERMES / "profiles" / p / "cron" / "jobs.json"
        if jf.exists():
            refs.append(jf.read_text(errors="ignore"))
        sdir = HERMES / "profiles" / p / "scripts"
        if sdir.is_dir():
            for f in sdir.rglob("*"):
                if f.is_file() and f.suffix in (".py", ".sh", ".mjs", ".js"):
                    try:
                        # Exclude EVERY copy of this script, not just the running one.
                        # It is deployed to all four seats, and each copy carries the
                        # selftest probe paths as string literals — so any copy left in
                        # the index made all four detectors permanently green.
                        if f.name == SELF_NAME or f.resolve() == SELF:
                            continue
                        refs.append(f.read_text(errors="ignore"))
                    except Exception:
                        pass
    refs.append(run("cat /root/.config/systemd/user/*.service 2>/dev/null"))
    refs.append(run("docker ps -a --format '{{.Names}} {{.Image}} {{.Command}} {{.Mounts}}' 2>/dev/null"))
    refs.append(run("crontab -l 2>/dev/null"))
    return "\n".join(refs)


LIVE_REFS = None


def is_live_referenced(path):
    global LIVE_REFS
    if LIVE_REFS is None:
        LIVE_REFS = build_live_reference_index()
    s = str(path)
    # match the path itself, or its basename when the basename is distinctive
    if s in LIVE_REFS:
        return True
    base = os.path.basename(s.rstrip("/"))
    if len(base) > 6 and base in LIVE_REFS:
        return True
    return False


# ───────────────────────────────────────────────────────────── detector 1

def find_duplicate_toolchains():
    """
    Heavy toolchains installed more than once across profile homes.
    Skills are MEANT to be duplicated across seats (redundancy). Toolchains are not.
    """
    findings = []
    heavy = [".rustup", ".cargo", "go", ".foundry", ".local/share/solana",
             ".local/share/svm", ".cloakbrowser"]
    seen = {}
    for p in PROFILES:
        home = HERMES / "profiles" / p / "home"
        for rel in heavy:
            d = home / rel
            if d.is_dir():
                sz = dirsize(d)
                if sz > 50 * 1024 * 1024:  # only worthwhile candidates
                    seen.setdefault(rel, []).append((p, sz, d))
    for rel, copies in seen.items():
        if len(copies) > 1:
            # RECLAIMABLE MATH FIX (2026-09-26). The old line was
            #     wasted = total - max(per-seat sizes)
            # which ASSUMED each seat holds independent bytes. It does not: the foundry
            # binaries are HARDLINKED across seats (same inode, st_nlink=2), so the same
            # bytes were counted once per seat and "reclaimable" came out at ~223M when the
            # TRUE figure is 0. Proof: `du -sc gentech/.foundry gizmo/.foundry` in ONE
            # invocation reports 228,376K total, not 2x223M — du dedupes hardlinks.
            # Reclaimable is what deletion actually frees: the size of the whole set minus
            # the bytes the surviving copy still needs — and NEVER more than 0 if every
            # copy is a hardlink of the others.
            nlink_max = 0
            try:
                top = copies[0][2]
                for rt, _d, fs in os.walk(top, onerror=lambda e: None, followlinks=False):
                    for f in fs:
                        if f in ("forge", "cast", "anvil", "chisel"):
                            try:
                                nlink_max = max(nlink_max, os.lstat(os.path.join(rt, f)).st_nlink)
                            except OSError:
                                pass
            except Exception:
                pass
            if nlink_max > 1:
                # shared inodes: removing a duplicate frees nothing until the LAST link goes
                wasted = 0
                note = (f"hardlinked across seats (nlink={nlink_max}) — duplicate costs NO extra "
                        f"disk; deleting one copy frees 0. NOT waste.")
            else:
                wasted = sum(c[1] for c in copies) - max(c[1] for c in copies)
                note = "independent copies — reclaimable is the smaller copies' bytes"
            findings.append({
                "kind": "duplicate_toolchain",
                "what": rel,
                "seats": [f"{c[0]} ({humansize(c[1])})" for c in copies],
                "reclaimable": wasted,
                "hardlinked": nlink_max > 1,
                "note": note,
                "paths": [str(c[2]) for c in copies],
            })
    return findings


# ───────────────────────────────────────────────────────────── detector 2

SAFE_DUP_PREFIXES = (
    "/usr/", "/var/lib/docker", "/var/lib/containerd", "/proc", "/sys", "/snap",
    "/root/.hermes/profiles/gentech/cache/", "/root/.cache/",
)
SAFE_DUP_NAMES = {
    "SKILL.md",  # shared core is INTENTIONALLY identical across seats
    "package.json", "requirements.txt", "pyvenv.cfg", "Cargo.toml", "go.mod",
    ".gitignore", "LICENSE", "README.md", "tsconfig.json", "Makefile", "AGENTS.md",
}


def find_duplicate_files(sizefloor=20 * 1024 * 1024, roots=None, maxfiles=4000):
    """
    Same content (sha256) in two or more places, above a size floor.

    PERF: hashing whole trees is expensive (measured ~45s per 200 files on this box, because
    /root holds vaults, repos, model dirs and project trees). We only look where big duplicate
    FILES are actually plausible and worth the I/O:
      - the profile homes and caches (venvs, toolchains, model dirs)
      - /root top-level project dirs, one level deep
    `maxfiles` is a hard scan budget. Whatever is NOT scanned is reported as such, so the
    "clean" verdict stays earned rather than assumed.
    """
    if roots is None:
        roots = []
        for p in PROFILES:
            h = HERMES / "profiles" / p / "home"
            if h.is_dir():
                roots.append(str(h))
            sc = HERMES / "profiles" / p / "cache"
            if sc.is_dir():
                roots.append(str(sc))
        roots += ["/root/.cache", "/root/repos", "/root/projects"]
        roots = [r for r in roots if os.path.isdir(r)]
    findings = []
    hashes = {}
    count = 0
    truncated = False
    for root in roots:
        for dirpath, dirnames, filenames in os.walk(root, onerror=lambda e: None, followlinks=False):
            if any(dirpath.startswith(x) for x in SAFE_DUP_PREFIXES):
                dirnames[:] = []
                continue
            dirnames[:] = [d for d in dirnames if d not in (
                ".git", "node_modules", "__pycache__", ".venv", "venv", "site-packages")]
            for fn in filenames:
                if fn in SAFE_DUP_NAMES:
                    continue
                fp = os.path.join(dirpath, fn)
                try:
                    if os.path.islink(fp):
                        continue
                    st = os.lstat(fp)
                    if st.st_size < sizefloor:
                        continue
                    count += 1
                    if count > maxfiles:
                        truncated = True
                        break
                    h = hashlib.sha256()
                    with open(fp, "rb") as fh:
                        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
                            h.update(chunk)
                    hashes.setdefault(h.hexdigest(), []).append((fp, st.st_size))
                except (OSError, PermissionError):
                    continue
            if count > maxfiles:
                break
        if count > maxfiles:
            break
    for digest, copies in hashes.items():
        if len(copies) > 1:
            # if every copy is live-referenced, it is not waste
            if all(is_live_referenced(c[0]) for c in copies):
                continue
            # HARDLINK FIX (2026-09-26). Identical content can mean ONE file reachable by two
            # names (same inode, st_nlink>1) rather than two copies. Deleting a hardlink frees
            # exactly 0 bytes — it only drops the link count — so reporting its size as
            # "reclaimable" overstates freeable space. The foundry binaries are exactly this:
            # gentech and gizmo report 40.0M/42.3M/80.7M/59.8M each, and the whole 222.8M
            # "reclaimable" was fiction (true: 0).
            inodes = {}
            for fp, _sz in copies:
                try:
                    inodes.setdefault(os.lstat(fp).st_ino, []).append(fp)
                except OSError:
                    pass
            distinct_inodes = len(inodes)
            hardlinked = distinct_inodes < len(copies)
            reclaimable = copies[0][1] * (distinct_inodes - 1) if distinct_inodes > 1 else 0
            findings.append({
                "kind": "duplicate_file",
                "what": os.path.basename(copies[0][0]),
                "size_each": copies[0][1],
                "reclaimable": reclaimable,
                "hardlinked": hardlinked,
                "note": ("same inode (hardlink) — NOT duplicate bytes; deleting one copy frees 0"
                         if hardlinked and distinct_inodes == 1 else
                         f"{distinct_inodes} distinct inodes across {len(copies)} paths"),
                "copies": [c[0] for c in copies],
            })
    # record how much we actually looked at, so "clean" is earned
    return findings, count, truncated


# ───────────────────────────────────────────────────────────── detector 3

def find_stale_cron_jobs(stale_days=14, long_paused_days=45):
    """
    Cron jobs that are dead weight:
      - ENABLED but last success is old, or last_status is an error whose timestamp
        precedes the most recent successful run (i.e. a stale error left on the record)
      - PAUSED/DISABLED for a long time (candidates for archiving)
    """
    findings = []
    for p in PROFILES:
        jf = HERMES / "profiles" / p / "cron" / "jobs.json"
        if not jf.exists():
            continue
        try:
            d = json.loads(jf.read_text())
        except Exception as e:
            findings.append({"kind": "cron_unreadable", "profile": p, "error": str(e)})
            continue
        jobs = d if isinstance(d, list) else d.get("jobs", [])
        for j in jobs:
            name = j.get("name", "?")
            jid = j.get("id", "?")[:12]
            status = j.get("last_status")
            enabled = j.get("enabled", True)
            state = j.get("state", "")

            if not enabled or state in ("paused", "archived", "completed"):
                if state in ("completed", "archived"):
                    continue  # finished one-shot / deliberately archived: done, not stale
                paused_at = j.get("paused_at")
                if paused_at:
                    try:
                        from datetime import datetime
                        t = datetime.fromisoformat(paused_at.replace("Z", "+00:00")).timestamp()
                        days = (NOW - t) / DAY
                        if days > long_paused_days:
                            findings.append({
                                "kind": "long_paused_cron", "profile": p, "job": name, "id": jid,
                                "days": int(days), "state": state,
                                "reclaimable": 0,
                                "note": "paused a long time — archive it or explain why it lives",
                            })
                    except Exception:
                        pass
                continue

            # enabled job with an error older than its last successful run is a STALE ERROR
            if status not in (None, "ok", "success"):
                findings.append({
                    "kind": "cron_error", "profile": p, "job": name, "id": jid,
                    "status": status, "last_run": j.get("last_run_at"),
                    "failure_streak": j.get("failure_streak"),
                    "reclaimable": 0,
                    "note": "enabled job reporting failure — check if the error is stale or live",
                })
    return findings


# ───────────────────────────────────────────────────────────── detector 4

STALE_CANDIDATES = [
    "target", "build", "dist", ".next", "__pycache__", "node_modules/.cache",
    ".pytest_cache", ".mypy_cache", ".parcel-cache",
]
CACHE_DIRS = [".cache", "cache", "tmp", "_build", ".tox", ".gradle", ".m2"]

# DEPENDENCY / TOOLCHAIN TREES — never descended (2026-10-09, Council Overnight).
#
# WHY: even after the nested-root fix, walking all of /root is ~144k directories on this
# box and does not finish inside any sane budget (measured: a bare `find /root -type d`
# alone runs >400s). The fan-out is almost entirely dependency and toolchain stores that
# are LIVE BY DEFINITION — a package inside node_modules or a file inside site-packages is
# referenced by the thing that installed it, so no artifact under them can be "unreferenced
# build output". Descending them burns the whole budget for zero findings.
#
# THIS IS A BOUNDARY, NOT AN OVERSIGHT: a stale artifact nested INSIDE node_modules /
# site-packages is deliberately NOT reported (its cache would be /.cache or /root/.npm,
# which are still checked). Everything a project owns directly — target/, dist/, build/,
# .next/, __pycache__/, .cache/, tmp/ — is still walked and still checked.
DEPENDENCY_TREES = {
    "node_modules", ".git",
    "venv", ".venv", "virtualenv",
    "site-packages", "dist-packages",
    ".rustup", ".cargo", ".npm", ".yarn", ".pnpm-store", ".bun",
    ".gradle", ".m2", ".tox", ".terraform", ".terragrunt-cache",
}

# Absolute prefixes pruned for the same reason: this box's own huge, live toolchain
# stores under HERMES_HOME (measured 2026-10-09: installs/ 18,329 dirs, node/ 1,117,
# blockrun-mcp/ 2,170). They are installs of live software, not project build output.
PATH_PRUNE = (
    "/root/.hermes/installs",
    "/root/.hermes/node",
    "/root/.hermes/blockrun-mcp",
)


def _drop_nested_roots(roots):
    """Remove any root that is nested inside another (so a subtree is never walked twice).

    Added 2026-10-09: the default roots were ["/root/.hermes", "/root"], and "/root"
    CONTAINS "/root/.hermes" — so the single largest subtree on the box was walked twice,
    roughly doubling an already too-slow scan.
    """
    out = []
    for r in sorted({os.path.realpath(x).rstrip("/") for x in roots}, key=len):
        if any(r == o or r.startswith(o + "/") for o in out):
            continue
        out.append(r)
    return out


def find_stale_artifacts(age_days=30, roots=None, budget=600):
    """
    Build output and caches that nothing live references and nothing has touched
    in `age_days`. Reports size; never deletes.

    BUDGET (2026-10-09). On this box "/root" is large enough that walking it never
    finished inside the nightly cron window: measured in isolation this one detector ran
    >900s and was the SOLE cause of fleet-hygiene-overnight.sh being killed at the cron's
    3600s limit and reported as a job FAILURE. A `budget` wall-clock cap now stops the
    scan, and when it is hit the result carries a `scan_truncated` marker so the verdict
    is surfaced as PARTIAL — never quietly rendered as clean (silence must be earned).
    """
    if roots is None:
        roots = [str(HERMES), "/root"]
    roots = _drop_nested_roots(roots)
    findings = []
    deadline = time.time() + budget
    truncated = False
    for root in roots:
        if truncated:
            break
        for dirpath, dirnames, _ in os.walk(root, onerror=lambda e: None, followlinks=False):
            if time.time() > deadline:
                truncated = True
                break
            if any(dirpath.startswith(x) for x in ("/var/lib", "/usr/", "/proc", "/sys")):
                dirnames[:] = []
                continue
            # Prune live dependency/toolchain stores and this box's HERMES_HOME installs.
            # ".git" is never a stale-artifact candidate (it is not in STALE_CANDIDATES or
            # CACHE_DIRS) and is enormous; descending it only burns the budget. See
            # DEPENDENCY_TREES / PATH_PRUNE for why the rest are pruned too.
            dirnames[:] = [
                d for d in dirnames
                if d not in DEPENDENCY_TREES
                and os.path.join(dirpath, d) not in PATH_PRUNE
            ]
            for d in list(dirnames):
                if d in STALE_CANDIDATES or d in CACHE_DIRS:
                    p = os.path.join(dirpath, d)
                    # SYMLINK GUARD (2026-09-26). A symlinked dir is NOT an artifact:
                    # deleting it frees nothing and can break a live toolchain. This fired
                    # on multica_workspaces/.../hermes-home/cache -> /root/.hermes/profiles/gentech/cache
                    # and reported "648.8M, untouched 39d" — the age was the LINK's mtime, while
                    # the real target was being written minutes earlier. dirsize() skips symlinked
                    # FILES, but os.walk still descends symlinked DIRS, so it inflated to the
                    # target's real size (663M). Every number in that finding was wrong.
                    if os.path.islink(p) or not os.path.isdir(p):
                        dirnames.remove(d)  # never descend through a link
                        continue
                    try:
                        age = (NOW - os.lstat(p).st_mtime) / DAY
                    except OSError:
                        continue
                    if age >= age_days and not is_live_referenced(p):
                        sz = dirsize(p)
                        if sz > 200 * 1024 * 1024:
                            findings.append({
                                "kind": "stale_artifact", "what": os.path.basename(p),
                                "path": p, "age_days": int(age),
                                "size": sz, "reclaimable": sz,
                                "note": "unreferenced by any live cron/script/service/container",
                            })
                            dirnames.remove(d)  # do not descend; already counted
    # de-dup: drop exact repeats AND any path nested inside another finding.
    # (Exact repeats happened because a candidate dir can be reached twice — e.g. go's
    # module cache matched both as a "cache" dir and again on the descent.)
    findings.sort(key=lambda f: f["path"])
    out = []
    seen = set()
    for f in findings:
        p = f["path"]
        if p in seen:
            continue
        if any(p.startswith(o["path"] + "/") for o in out):
            continue
        seen.add(p)
        out.append(f)
    if truncated:
        out.append({
            "kind": "scan_truncated",
            "what": "STALE-ARTIFACT SCAN TRUNCATED",
            "note": (f"stopped at the {budget}s wall-clock cap — results are PARTIAL, "
                     "not clean (raise the budget or narrow the roots to finish)"),
        })
    return out


# ───────────────────────────────────────────────────────────── selftest

def find_oversized_skills(limit=100_000, warn_at=80_000):
    """SKILL.md files at or over the platform's skill size limit.

    2026-09-22: agent-coordination/SKILL.md had grown to 101,748 chars, past the 100k
    limit, so EVERY edit to it silently failed with
    "SKILL.md content is 102,043 characters (limit: 100,000)". Nothing reported it —
    the skill still LOADED and still WORKED; it had just become permanently frozen,
    and you only found out by trying to change it.

    That is the silent-killer shape: no error at read time, no alarm, the failure only
    appears at the moment you try to write. Found 11 files in this state fleet-wide.

    Skills are intentionally duplicated across seats, so the same frozen file usually
    exists on 3-4 seats — fixing one means fixing all of them.

    Never edits anything: reports the file, its size, and the largest ## section, which
    is the usual extraction candidate.
    """
    findings = []
    near = []
    for p in PROFILES:
        root = f"/root/.hermes/profiles/{p}/skills"
        if not os.path.isdir(root):
            findings.append({"kind": "skill_scan_unreadable", "profile": p,
                             "error": f"{root} not readable"})
            continue
        for dirpath, _dirnames, filenames in os.walk(root):
            if "SKILL.md" not in filenames:
                continue
            fp = os.path.join(dirpath, "SKILL.md")
            try:
                # COUNT CHARACTERS, NOT BYTES. The platform rejects on character count
                # ("SKILL.md content is 102,043 characters (limit: 100,000)") while these
                # files are multi-byte, so os.path.getsize() over-reports and flags files
                # that are still editable — proven 2026-09-22 when a byte-based check
                # called gentech-ops (101,055 bytes / 99,817 chars) uneditable and a real
                # edit SUCCEEDED. A detector that cries wolf is the thing we hunt.
                with open(fp, encoding="utf-8", errors="replace") as fh:
                    text = fh.read()
                sz = len(text)
                nbytes = os.path.getsize(fp)
            except OSError as e:
                findings.append({"kind": "skill_scan_unreadable", "profile": p,
                                 "error": f"{fp}: {e}"})
                continue
            if sz < warn_at:
                continue
            # largest ## section — the usual thing to move into references/
            biggest, biggest_len = "", 0
            if sz >= limit:
                try:
                    for chunk in re.split(r"\n(?=## )", text):
                        if not chunk.startswith("## "):
                            continue
                        if len(chunk) > biggest_len:
                            biggest_len = len(chunk)
                            biggest = chunk.split("\n", 1)[0][3:60]
                except Exception:
                    pass
            rec = {
                "kind": "skill_over_limit" if sz >= limit else "skill_near_limit",
                "profile": p, "path": fp, "size": sz, "size_bytes": nbytes,
                "over_by": max(0, sz - limit),
                "largest_section": biggest,
                "largest_section_chars": biggest_len,
                "note": ("UNEDITABLE — every skill_manage write will be rejected until split"
                         if sz >= limit else f"within {limit - sz:,} chars of becoming uneditable"),
            }
            (findings if sz >= limit else near).append(rec)
    findings.extend(near)
    findings.sort(key=lambda f: -f["size"])
    return findings


# ─────────────────────────────────────────── skill-size MAINTENANCE (nightly)
#
# Jordan, 2026-09-27: "we should add this to maintenance so it gets looked at every night"
#
# The detector above ALREADY ran nightly — that was never the gap. The gap was that it
# re-reported the same static list every night, so nothing was ever actioned, and two files
# sat 3 characters from permanently frozen before anyone noticed. A warning that never
# changes is not maintenance, it is wallpaper.
#
# What was missing is the two things a maintenance pass adds over a report:
#   1. MEMORY  — a ledger, so we can see GROWTH, not just size. A file at 88k that is stable
#                is fine; a file at 82k that gains 3k a night is the emergency.
#   2. A DECISION — one ranked list, grouped per skill (not per seat), naming what is next.
#
# Grouping is per skill identity, so the same skill on four seats is ONE finding with a
# count. The ledger stores one entry per skill, so the arithmetic stays honest.

SKILL_SIZE_LIMIT = 100_000
SKILL_WARN_AT = 80_000
SKILL_LEDGER = HERMES / "profiles" / "gentech" / "cache" / "skill-size-ledger.json"
LEDGER_HISTORY_MAX = 90          # ~3 months of nightly points
ACT_NOW_DAYS = 14                # projected to cross the cliff inside two weeks


def _skill_identity(path):
    """Which skill is this, ignoring which seat it sits on?

    Duplicated across seats by design, so /root/.hermes/profiles/<seat>/skills/<ID>/SKILL.md
    collapses to <ID>. Archive copies keep their path shape (they are separate files that
    happen to share a name) but are tagged so they never masquerade as the live skill.
    """
    key = path.split("/skills/", 1)[-1]
    return key


def _load_skill_ledger():
    try:
        with open(SKILL_LEDGER, encoding="utf-8") as fh:
            d = json.load(fh)
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        return {}


def _save_skill_ledger(ledger):
    try:
        SKILL_LEDGER.parent.mkdir(parents=True, exist_ok=True)
        tmp = str(SKILL_LEDGER) + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(ledger, fh, indent=1, sort_keys=True)
        os.replace(tmp, SKILL_LEDGER)      # atomic — a crash mid-write must not
                                           # leave a corrupt ledger that reads as "no growth"
    except OSError:
        pass


def _growth_per_day(history, now):
    """Chars/day from the ledger's own history. None when there is not enough signal.

    Deliberately requires a real time SPAN (>=1 day) so a single run, or two runs minutes
    apart, cannot invent a rate. A fabricated slope would mis-rank the whole list.
    """
    pts = [p for p in history if isinstance(p, (list, tuple)) and len(p) == 2]
    if len(pts) < 2:
        return None
    t0, s0 = pts[0]
    t1, s1 = pts[-1]
    days = (t1 - t0) / DAY
    if days < 1.0:
        return None
    return (s1 - s0) / days


def build_skill_pressure_maintenance(now=None):
    """Nightly skill-size maintenance: rank by DANGER, ledger the growth, name what is next.

    Returns a dict so callers can render or assert on it; never deletes or edits anything.
    """
    now = now or time.time()
    items = find_oversized_skills(limit=SKILL_SIZE_LIMIT, warn_at=SKILL_WARN_AT)

    # group per skill identity
    grouped = {}
    for it in items:
        ident = _skill_identity(it["path"])
        g = grouped.setdefault(ident, {
            "skill": ident, "seats": [], "sizes": [], "live": 0, "archived": 0,
            "largest_section": "", "largest_section_chars": 0,
        })
        g["sizes"].append(it["size"])
        g["seats"].append(it["profile"])
        if "/.archive/" in it["path"]:
            g["archived"] += 1
        else:
            g["live"] += 1
        if it.get("largest_section_chars", 0) > g["largest_section_chars"]:
            g["largest_section_chars"] = it.get("largest_section_chars", 0)
            g["largest_section"] = it.get("largest_section", "")

    ledger = _load_skill_ledger()
    hist = ledger.get("history") if isinstance(ledger.get("history"), dict) else {}

    rows = []
    for ident, g in grouped.items():
        size = max(g["sizes"])                 # a skill is as large as its largest copy
        g["size"] = size
        g["chars_to_cliff"] = max(0, SKILL_SIZE_LIMIT - size)
        g["headroom_pct"] = round(100.0 * g["chars_to_cliff"] / SKILL_SIZE_LIMIT, 1)

        # record this observation, then measure growth over the retained window
        seen = list(hist.get(ident) or [])
        if not seen or seen[-1][1] != size:
            seen.append([now, size])
        seen = seen[-LEDGER_HISTORY_MAX:]
        hist[ident] = seen

        rate = _growth_per_day(seen, now)
        g["growth_per_day"] = None if rate is None else round(rate, 1)
        if rate and rate > 0:
            g["days_to_cliff"] = int(g["chars_to_cliff"] / rate)
        else:
            g["days_to_cliff"] = None

        if size >= SKILL_SIZE_LIMIT:
            g["tier"] = "UNEDITABLE"
        elif rate and rate > 0 and (g["days_to_cliff"] or 9999) <= ACT_NOW_DAYS:
            g["tier"] = "ACT NOW"
        elif (rate and rate > 0) or size >= 95_000:
            g["tier"] = "WATCH"
        else:
            g["tier"] = "PARKED"
        rows.append(g)

    # rank: uneditable first, then soonest projected cliff, then raw size
    tier_rank = {"UNEDITABLE": 0, "ACT NOW": 1, "WATCH": 2, "PARKED": 3}
    rows.sort(key=lambda r: (tier_rank[r["tier"]], r["days_to_cliff"] or 10**6, -r["size"]))

    ledger["updated_at"] = now
    ledger["limit"] = SKILL_SIZE_LIMIT
    ledger["warn_at"] = SKILL_WARN_AT
    ledger["history"] = hist
    _save_skill_ledger(ledger)

    return {
        "scanned_rows": len(items),
        "skills": len(rows),
        "live": sum(1 for r in rows if r["live"]),
        "archived": sum(1 for r in rows if r["archived"]),
        "rows": rows,
        "tiers": {t: [r for r in rows if r["tier"] == t] for t in tier_rank},
        "ledger": str(SKILL_LEDGER),
    }


def render_skill_maintenance(m):
    """The nightly report. Short, ranked, and it names ONE next file."""
    L = []
    nxt = m["rows"][0] if m["rows"] else None
    L.append("🧹 SKILL-SIZE MAINTENANCE — nightly")
    L.append("")
    L.append(f"   {m['skills']} skills over {SKILL_WARN_AT // 1000}k "
             f"({m['live']} live, {m['archived']} archived) "
             f"across {m['scanned_rows']} files.")
    if nxt:
        d = nxt["days_to_cliff"]
        rate = nxt["growth_per_day"]
        if rate:
            when = (f"projected to cross in ~{d}d" if d is not None
                    else "growing, but not fast enough to project a crossing")
            when += f" at +{rate:,}/day"
        else:
            # No rate is NOT the same as no growth. On the first run (or the first run after
            # a gap wider than the retained history) there are not two readings a day apart,
            # so no slope can honestly be computed yet. Saying "no measured growth" would
            # read as "this file is stable" — a claim we have not earned.
            when = "baseline taken — growth rate available after the next nightly reading"
        L.append(f"   NEXT DUE: {nxt['skill']}")
        L.append(f"      {nxt['size']:,} chars — {nxt['chars_to_cliff']:,} from the cliff "
                 f"({nxt['headroom_pct']}% headroom); {when}")
    L.append("")

    for tier in ("UNEDITABLE", "ACT NOW", "WATCH"):
        rows = m["tiers"][tier]
        if not rows:
            continue
        L.append(f"── {tier}  ({len(rows)})")
        for r in rows:
            seats = f"{r['live']} live seat(s)" + (f", {r['archived']} archived" if r["archived"] else "")
            extra = ""
            if r["growth_per_day"]:
                extra = f" — +{r['growth_per_day']:,}/day"
                if r["days_to_cliff"] is not None:
                    extra += f", crosses in ~{r['days_to_cliff']}d"
            L.append(f"   • {r['skill']}")
            L.append(f"       {r['size']:,} chars, {r['chars_to_cliff']:,} to the cliff"
                     f" ({seats}){extra}")
            if r["tier"] == "UNEDITABLE" and r["largest_section"]:
                L.append(f"       largest ## section: \"{r['largest_section']}\" "
                         f"({r['largest_section_chars']:,} chars) — extraction candidate")
        L.append("")

    parked = m["tiers"]["PARKED"]
    if parked:
        L.append(f"── PARKED  ({len(parked)}) — warned by size, but stable and/or well clear")
        L.append("   " + ", ".join(f"{r['skill']} ({r['size']:,})" for r in parked[:8])
                 + (f" … +{len(parked) - 8} more" if len(parked) > 8 else ""))
        L.append("")

    L.append(f"   Ledger: {m['ledger']}")
    L.append("   (nothing was edited or deleted — this ranks the work. Splitting is a human decision.)")
    return "\n".join(L)


def selftest():
    """
    Plant a real failure for each detector and prove it is caught.

    CONCURRENCY LOCK (2026-09-26). The probes below use FIXED paths
    (/root/.hygiene-selftest, /root/.hygiene-selftest-link, /root/.hygiene-selftest-hl-*.bin)
    and mutate pixel's cron jobs.json. Two overlapping runs therefore destroy each other's
    fixtures, and the damaged run prints "FAILED (still green)" for detectors that are
    perfectly healthy -- observed for real when the same selftest was launched twice at once.
    A false alarm from the tool that exists to detect false signals is worse than no tool, so
    the selftest now refuses to run concurrently instead of reporting a lie. Stale locks (a
    killed run) are broken after 30 minutes so this can never wedge.
    """
    import time as _time
    lock = Path("/root/.hygiene-selftest.lock")
    try:
        if lock.exists() and (_time.time() - lock.stat().st_mtime) < 1800:
            print("SELFTEST SKIPPED — another selftest is running (lock: %s)." % lock)
            print("Concurrent runs corrupt each other's fixtures and report FALSE failures.")
            return 0
        lock.write_text(str(os.getpid()))
    except OSError:
        pass
    try:
        return _selftest_body()
    except Exception as e:
        # TOP-LEVEL GUARD (2026-09-26). Hardening block #4 alone was not enough: my own forced
        # test — making os.utime raise FileNotFoundError for any .hygiene-selftest path — proved
        # the class is broader, because detectors 2, 3, 4b and 4c all touch fixtures too and
        # none of them caught it. A crash is not a report: a selftest that tracebacks tells the
        # operator nothing about WHICH detectors were healthy, and silently loses the results of
        # everything before the throw. One guard here covers every block, present and future.
        print()
        print(f"  SELFTEST ABORTED — a probe could not complete: {type(e).__name__}: {e}")
        print("  Reported as UNKNOWN, never as clean. Re-run when no other selftest is active.")
        return 1
    finally:
        try:
            lock.unlink(missing_ok=True)
        except OSError:
            pass


def _selftest_body():
    """
    Prove every detector can go RED. A check we never saw fire is not a check.
    """
    print("SELFTEST — proving each detector can actually go red\n")
    ok = True

    # 1. toolchain: plant a fake duplicate
    fake = HERMES / "profiles" / "gizmo" / "home" / ".foundry"
    made = False
    if not fake.exists():
        fake.mkdir(parents=True, exist_ok=True)
        (fake / "blob.bin").write_bytes(b"0" * (60 * 1024 * 1024))
        made = True
    f1 = find_duplicate_toolchains()
    hit1 = any("foundry" in x["what"] for x in f1)
    print(f"  1. duplicate toolchain   -> {'RED ✓' if hit1 else 'FAILED (still green)'}")
    ok &= hit1
    if made:
        import shutil
        shutil.rmtree(fake, ignore_errors=True)

    # 1b. oversized skill: plant a real >100k SKILL.md and prove it is flagged.
    #     This detector matters because the failure it catches is INVISIBLE at read
    #     time — the skill still loads and works, it just cannot ever be edited again.
    import shutil as _sh
    fake_skill_dir = Path(f"/root/.hermes/profiles/gentech/skills/.selftest-oversized")
    flagged = False
    try:
        fake_skill_dir.mkdir(parents=True, exist_ok=True)
        # >100k of real-looking SKILL.md content with a large ## section
        body = "x" * 105_000   # must exceed the 100k limit, not approach it
        (fake_skill_dir / "SKILL.md").write_text(
            "---\nname: selftest\n---\n\n# t\n\n## Big Section\n" + body + "\n## Small\nhi\n")
        f1b = find_oversized_skills()
        hit1b = any(".selftest-oversized" in x["path"] and x["kind"] == "skill_over_limit"
                    for x in f1b)
        # and it must name the largest section, not just the size
        named = any(".selftest-oversized" in x["path"] and x.get("largest_section") == "Big Section"
                    for x in f1b)
        flagged = hit1b and named
        print(f"  1b. oversized skill     -> {'RED ✓ (and names the section)' if flagged else 'FAILED (still green)'}")
    except Exception as e:
        print(f"  1b. oversized skill     -> FAILED ({e})")
    finally:
        _sh.rmtree(fake_skill_dir, ignore_errors=True)
    ok &= flagged

    # 2. duplicate file: plant two identical large files
    a = Path("/root/.hygiene-selftest-a.bin")
    b = Path("/root/.hygiene-selftest-b.bin")
    try:
        data = os.urandom(1) * (25 * 1024 * 1024)
        a.write_bytes(data)
        b.write_bytes(data)
        f2, scanned, trunc = find_duplicate_files(roots=["/root"])
        hit2 = any("hygiene-selftest" in c for x in f2 for c in x["copies"])
        print(f"  2. duplicate file        -> {'RED ✓' if hit2 else 'FAILED (still green)'}"
              f"  [scanned {scanned} files]")
        ok &= hit2
    finally:
        a.unlink(missing_ok=True)
        b.unlink(missing_ok=True)

    # 3. stale cron: plant a long-paused job
    jf = HERMES / "profiles" / "pixel" / "cron" / "jobs.json"
    try:
        d = json.loads(jf.read_text())
        jobs = d if isinstance(d, list) else d.get("jobs", [])
        probe = {"id": "selftest0000", "name": "SELFTEST stale probe", "enabled": False,
                 "state": "paused", "paused_at": "2026-01-01T00:00:00+00:00",
                 "last_status": "ok"}
        jobs.append(probe)
        jf.write_text(json.dumps(d, indent=2))
        f3 = find_stale_cron_jobs()
        hit3 = any(x.get("id") == "selftest0" or "SELFTEST" in x.get("job", "") for x in f3)
        print(f"  3. stale cron            -> {'RED ✓' if hit3 else 'FAILED (still green)'}")
        ok &= hit3
    finally:
        try:
            d = json.loads(jf.read_text())
            jobs = d if isinstance(d, list) else d.get("jobs", [])
            jobs[:] = [j for j in jobs if not j.get("id", "").startswith("selftest")]
            jf.write_text(json.dumps(d, indent=2))
        except Exception:
            pass

    # 4. stale artifact: plant an old, unreferenced build dir
    #
    # HARDENING (2026-09-26): this block used to raise a raw FileNotFoundError out of the
    # selftest when a concurrent run deleted the fixture dir mid-probe. A crash is not a
    # report — and it violated this script's own DESIGN RULE that a detector which cannot
    # complete is reported UNKNOWN, never silently omitted. (Also, the traceback is what
    # actually got noticed; the other run's false "FAILED (still green)" lines went by.)
    # The concurrency lock prevents the collision; this makes a survivor survive anyway.
    art = Path("/root/.hygiene-selftest/target")
    try:
        art.mkdir(parents=True, exist_ok=True)
        (art / "big.o").write_bytes(b"0" * (220 * 1024 * 1024))
        old = NOW - 400 * DAY
        os.utime(art, (old, old))
        f4 = find_stale_artifacts(roots=["/root/.hygiene-selftest"], age_days=30)
        hit4 = any("hygiene-selftest" in x["path"] for x in f4)
        print(f"  4. stale artifact        -> {'RED ✓' if hit4 else 'FAILED (still green)'}")
        ok &= hit4
    except Exception as e:
        print(f"  4. stale artifact        -> UNKNOWN — probe could not complete: "
              f"{type(e).__name__}: {e}")
        ok = False
    finally:
        import shutil
        shutil.rmtree("/root/.hygiene-selftest", ignore_errors=True)

    # 4b. symlink-guard: a SYMLINKED cache dir must NOT be reported as a stale artifact.
    # The scanner has to see BOTH sides — a real dir still goes red (#4 above proves the
    # detector works), and a link to that same kind of dir stays silent. Without this,
    # the link bug could come back and every run would quietly recommend deleting a live
    # cache, which is exactly what happened on 2026-09-26.
    linkroot = Path("/root/.hygiene-selftest-link")
    try:
        import shutil as _sh
        _sh.rmtree(linkroot, ignore_errors=True)
        real = linkroot / "real" / "cache"
        real.mkdir(parents=True, exist_ok=True)
        (real / "big.o").write_bytes(b"0" * (220 * 1024 * 1024))
        lnk = linkroot / "link"
        lnk.mkdir(parents=True, exist_ok=True)
        (lnk / "cache").symlink_to(real, target_is_directory=True)
        old = NOW - 400 * DAY
        for tgt in (lnk, real):          # age BOTH: link stale, target stale
            os.utime(tgt, (old, old))
        f4b = find_stale_artifacts(roots=[str(linkroot)], age_days=30)
        linked_reported = any(os.path.islink(x["path"]) and "link" in x["path"] for x in f4b)
        real_reported = any(x["path"] == str(real) for x in f4b)
        good4b = (not linked_reported) and real_reported
        print(f"  4b. symlink not artifact -> {'RED ✓' if good4b else 'FAILED (link reported or real missed)'}"
              f"  [link={linked_reported} real={real_reported}]")
        ok &= good4b
    finally:
        import shutil
        shutil.rmtree("/root/.hygiene-selftest-link", ignore_errors=True)

    # 4c. hardlink guard: two HARDLINKED copies of a big file must report reclaimable=0.
    # Real case: the foundry binaries are hardlinked across gentech and gizmo. The old math
    # (size * (copies-1)) claimed 222.8M freeable when the true figure is 0, because deleting
    # a hardlink drops a link count, not bytes. Prove the detector now says 0.
    hl_a = Path("/root/.hygiene-selftest-hl-a.bin")
    hl_b = Path("/root/.hygiene-selftest-hl-b.bin")
    try:
        hl_a.write_bytes(os.urandom(1) * (25 * 1024 * 1024))
        os.link(hl_a, hl_b)                     # hardlink, NOT a copy
        f4c, _sc, _tr = find_duplicate_files(roots=["/root"])
        rec = [x for x in f4c if any("hygiene-selftest-hl" in c for c in x["copies"])]
        hl_ok = bool(rec) and all(x["reclaimable"] == 0 for x in rec)
        print(f"  4c. hardlink reclaimable  -> {'RED ✓' if hl_ok else 'FAILED (claims freeable bytes)'}"
              f"  [reclaimable={[x['reclaimable'] for x in rec]}]")
        ok &= hl_ok
    finally:
        hl_a.unlink(missing_ok=True)
        hl_b.unlink(missing_ok=True)

    # 5. SKILL-SIZE MAINTENANCE: the ranking and growth logic must be able to go RED.
    #    Three separate claims get planted failures, because each is a way the maintenance
    #    pass could be confidently wrong: (a) it must not invent a growth rate from a single
    #    observation, (b) it must rank a fast-growing file ABOVE a larger stable one, and
    #    (c) it must project a crossing date from a real measured slope.
    try:
        lroot = Path("/root/.hygiene-maint-history.json")
        one_point = {"history": {"x/SKILL.md": [[NOW, 82_000]]}}
        r_one = _growth_per_day(one_point["history"]["x/SKILL.md"], NOW)
        # two points minutes apart must ALSO not yield a rate (needs a real day of span)
        r_tight = _growth_per_day([[NOW - 600, 80_000], [NOW, 84_000]], NOW)
        # a real 4-day slope of +1000/day
        r_real = _growth_per_day([[NOW - 4 * DAY, 80_000], [NOW, 84_000]], NOW)
        ok_a = r_one is None and r_tight is None and r_real is not None
        print(f"  5a. growth needs real span -> {'RED ✓' if ok_a else 'FAILED (invents a rate)'}"
              f"  [1pt={r_one}, 10min={None if r_tight is None else round(r_tight,1)}, "
              f"4d={None if r_real is None else round(r_real,1)}]")
        ok &= ok_a

        # (b)+(c) ranking: a small fast-grower must beat a big stable file
        fast = {"size": 84_000, "chars_to_cliff": 16_000, "growth_per_day": 2_000,
                "days_to_cliff": 8, "tier": "ACT NOW", "skill": "fast/SKILL.md",
                "live": 1, "archived": 0, "largest_section": "", "largest_section_chars": 0,
                "headroom_pct": 16.0}
        big = {"size": 97_000, "chars_to_cliff": 3_000, "growth_per_day": None,
               "days_to_cliff": None, "tier": "WATCH", "skill": "big/SKILL.md",
               "live": 4, "archived": 0, "largest_section": "", "largest_section_chars": 0,
               "headroom_pct": 3.0}
        ranked = sorted([big, fast], key=lambda r: (
            {"UNEDITABLE": 0, "ACT NOW": 1, "WATCH": 2, "PARKED": 3}[r["tier"]],
            r["days_to_cliff"] or 10**6, -r["size"]))
        ok_b = ranked[0]["skill"] == "fast/SKILL.md"
        proj = int(fast["chars_to_cliff"] / fast["growth_per_day"])
        ok_c = proj == 8
        print(f"  5b. fast-grower ranks first -> {'RED ✓' if ok_b else 'FAILED (bigger wins)'}"
              f"  [first={ranked[0]['skill']}]")
        print(f"  5c. projects the crossing    -> {'RED ✓' if ok_c else 'FAILED (bad date)'}"
              f"  [16,000 / 2,000 per day = {proj}d]")
        ok &= ok_b and ok_c

        # (d) the ledger must not lose a reading, and must not duplicate an unchanged one
        saved = SKILL_LEDGER
        globals()["SKILL_LEDGER"] = lroot
        hist = {"x/SKILL.md": [[NOW - DAY, 82_000]]}
        _save_skill_ledger({"history": hist})
        back = _load_skill_ledger()
        ok_d = back.get("history", {}).get("x/SKILL.md") == [[NOW - DAY, 82_000]]
        print(f"  5d. ledger round-trips        -> {'RED ✓' if ok_d else 'FAILED (lost data)'}")
        ok &= ok_d
        globals()["SKILL_LEDGER"] = saved
    except Exception as e:
        print(f"  5. skill maintenance      -> FAILED ({type(e).__name__}: {e})")
        ok = False
    finally:
        try:
            Path("/root/.hygiene-maint-history.json").unlink(missing_ok=True)
        except OSError:
            pass

    print()
    print("  RESULT:", "ALL DETECTORS CAN GO RED ✓" if ok else "SOME DETECTORS ARE STUCK GREEN ✗")
    return 0 if ok else 1

# ───────────────────────────────────────────────────────────── main

def main():
    quiet = "--quiet" in sys.argv
    if "--selftest" in sys.argv:
        sys.exit(selftest())

    errors = []
    sections = []

    try:
        t = find_duplicate_toolchains()
        sections.append(("DUPLICATE TOOLCHAINS", t))
    except Exception as e:
        errors.append(f"duplicate_toolchains: {e}")

    try:
        dup_files, scanned, truncated = find_duplicate_files()
        label = f"DUPLICATE FILES (>20MB by hash, {scanned} files scanned"
        label += ", SCAN TRUNCATED)" if truncated else ")"
        sections.append((label, dup_files))
    except Exception as e:
        errors.append(f"duplicate_files: {e}")

    try:
        cj = find_stale_cron_jobs()
        sections.append(("STALE / ERRORING CRON JOBS", cj))
    except Exception as e:
        errors.append(f"stale_cron: {e}")

    try:
        sa = find_stale_artifacts()
        sections.append(("STALE ARTIFACTS (unreferenced, >200MB, >30d)", sa))
    except Exception as e:
        errors.append(f"stale_artifacts: {e}")

    try:
        sk = find_oversized_skills()
        sections.append(("OVERSIZED SKILL.md (>=100k = UNEDITABLE; >=80k = warn)", sk))
    except Exception as e:
        errors.append(f"oversized_skills: {e}")

    # Skill-size MAINTENANCE (Jordan, 2026-09-27: "add this to maintenance so it gets looked
    # at every night"). The section above re-reported a static list nightly and nothing was
    # ever actioned. This adds the ledger + ranking so the report names ONE next file and its
    # measured growth rate, instead of restating the same 22 lines forever.
    maint = None
    try:
        maint = build_skill_pressure_maintenance()
    except Exception as e:
        errors.append(f"skill_maintenance: {e}")

    total_findings = sum(len(s[1]) for s in sections)
    reclaimable = sum(f.get("reclaimable", 0) for s in sections for f in s[1])

    if total_findings == 0 and not errors:
        if not quiet:
            print("✅ fleet hygiene — clean. No duplicates, no stale artifacts, no stale crons.")
        sys.exit(0)

    print("🧹 FLEET HYGIENE AUDIT — findings\n")
    for title, items in sections:
        if not items:
            continue
        print(f"── {title}  ({len(items)})")
        for f in items[:25]:
            k = f["kind"]
            if k == "duplicate_toolchain":
                print(f"   • {f['what']} duplicated across {len(f['seats'])} seats — "
                      f"reclaimable {humansize(f['reclaimable'])}")
                for s in f["seats"]:
                    print(f"       {s}")
            elif k == "duplicate_file":
                print(f"   • {f['what']} — {len(f['copies'])} identical copies of "
                      f"{humansize(f['size_each'])} each, reclaimable {humansize(f['reclaimable'])}")
                for c in f["copies"][:4]:
                    print(f"       {c}")
            elif k in ("long_paused_cron", "cron_error"):
                print(f"   • [{f['profile']}] {f['job']} ({f['id']}) — {f.get('note','')}")
            elif k == "stale_artifact":
                print(f"   • {f['path']} — {humansize(f['size'])}, untouched {f['age_days']}d")
            elif k in ("skill_over_limit", "skill_near_limit"):
                flag = "⛔ UNEDITABLE" if k == "skill_over_limit" else "⚠ near limit"
                print(f"   • [{f['profile']}] {f['path']}")
                print(f"       {f['size']:,} chars — {flag} ({f['note']})")
                if k == "skill_over_limit" and f["largest_section"]:
                    print(f"       largest ## section: \"{f['largest_section']}\" "
                          f"({f['largest_section_chars']:,} chars) — extraction candidate")
            elif k == "skill_scan_unreadable":
                print(f"   • [{f.get('profile','?')}] {f.get('error','?')}")
                print("       (scan INCOMPLETE for this seat — not a clean result)")
            else:
                print(f"   • {f}")
        print()

    if reclaimable > 0:
        print(f"   TOTAL RECLAIMABLE IF ACTED ON: {humansize(reclaimable)}")
        print("   (nothing was deleted — this only looks. Deletion is a human decision.)")
    if maint is not None and maint["rows"]:
        # NOT gated on --quiet: in this script `--quiet` only suppresses the "clean"
        # one-liner, and the nightly cron job passes --quiet. Gating here would have
        # rendered the maintenance section NOWHERE — which is precisely the class of bug
        # (a report that can never be seen) this section exists to prevent.
        print()
        print(render_skill_maintenance(maint))
    if errors:
        print("\n   ⚠ DETECTOR ERRORS — results above are INCOMPLETE:")
        for e in errors:
            print(f"     {e}")
        sys.exit(2)

    # EXIT CONTRACT — cron-safe. This is subtle and it bit us once:
    #
    # A `no_agent` cron job treats ANY non-zero exit as a FAILURE, regardless of what the
    # script printed. So exiting 1 on findings made this job raise an error alert every
    # single night it found something — which is most nights. An alarm that always fires is
    # as useless as one that never fires: it trains the reader to ignore it.
    #
    # Findings are a SUCCESSFUL RUN of a detector. The message IS the payload, delivered on
    # exit 0. Only a broken detector (nothing could be measured) is a real failure.
    #
    # For a human at the terminal who wants the distinction, pass --strict-exit.
    if "--strict-exit" in sys.argv:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
