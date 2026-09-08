#!/usr/bin/env python3
"""
Context Save Bridge — REAL content capture (v2.0)
==================================================
Replaces the blank-template bridge generator. Pulls ACTUAL recent work from
the profile's session DB (state.db) and writes an actionable resume file.

Key upgrade over v1.x: instead of empty placeholders, this captures
  - recent active project titles (from session titles + last activity)
  - the last real user/assistant exchanges (decisions, blockers, next steps)
  - explicit BLOCKERS / NEXT STEPS / DECISIONS extraction via keyword scan
  - current 00-STATE.md content

Usage:
  python3 context-save.py [--profile gentech|pixel|...] [--minutes 720]

The gateway restart script calls this before clearing sessions, so overnight
work (midnight → 6:25 AM) is actually captured, regardless of when it happened.
"""
import argparse
import json
import os
import re
import sqlite3
from datetime import datetime, timezone

VAULT = "/root/vaults/gentech"
HERMES_ROOT = "/root/.hermes/profiles"
BRIDGE_DIR = os.path.join(VAULT, "09-Green Room", "context-bridge")
STATE_FILE = os.path.join(VAULT, "00-STATE.md")

# Keywords that flag actionable lines worth keeping in the resume file.
BLOCKER_KEYWORDS = ("blocker", "blocked", "blocking", "waiting", "waiting on",
                    "stuck", "need", "needs", "depend", "pending", "awaiting")
NEXT_KEYWORDS = ("next", "next step", "then ", "todo", "to do", "pending",
                 "continue", "resume", "up next", "follow-up", "follow up")
DECISION_KEYWORDS = ("decided", "decision", "agreed", "we agreed", "going with",
                     "chose", "locked", "locked in", "approved", "greenlit",
                     "confirmed", "we'll use", "we will use")


def now_ts():
    return datetime.now(timezone.utc)


def parse_ts(ts):
    """state.db stores unix epoch floats; return as datetime."""
    try:
        return datetime.fromtimestamp(float(ts), tz=timezone.utc)
    except (TypeError, ValueError):
        return None


def find_state_db(profile):
    p = os.path.join(HERMES_ROOT, profile, "state.db")
    return p if os.path.exists(p) else None


def pull_recent(profile, minutes):
    """Return (recent_messages, recent_sessions) from the profile's session DB."""
    db = find_state_db(profile)
    if not db:
        return [], []
    cutoff = now_ts().timestamp() - (minutes * 60)
    try:
        con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    except sqlite3.Error:
        return [], []
    messages, sessions = [], []
    try:
        # Non-tool messages (skip tool payloads and empty) from the window.
        for role, ts, content in con.execute(
            "SELECT role, timestamp, content FROM messages "
            "WHERE timestamp >= ? AND role IN ('user','assistant') "
            "ORDER BY id DESC LIMIT 400", (cutoff,)
        ):
            if not content or not content.strip():
                continue
            t = parse_ts(ts)
            messages.append({"role": role, "ts": t, "text": content.strip()})
        messages.reverse()  # chronological
        # Session titles with recent activity.
        for sid, title, src, ts in con.execute(
            "SELECT id, title, source, last_activity_at FROM sessions "
            "WHERE last_activity_at >= ? ORDER BY last_activity_at DESC LIMIT 12",
            (cutoff,)
        ):
            t = parse_ts(ts)
            sessions.append({"id": sid, "title": title, "source": src, "ts": t})
    except sqlite3.Error:
        pass
    finally:
        con.close()
    return messages, sessions


def summarize(messages, max_chars=3500):
    """Turn the raw messages into a compact actionable summary."""
    if not messages:
        return "No recent user/assistant messages captured in the window."
    chunks, blockers, nexts, decisions = [], [], [], []
    for m in messages:
        text = re.sub(r"\s+", " ", m["text"]).strip()
        low = text.lower()
        if not text or len(text) < 4:
            continue
        # Skip cron boilerplate that isn't real work.
        if ("IMPORTANT: You are running as a scheduled cron job" in text
                or "respond with exactly \"[SILENT]\"" in text
                or "suppress delivery" in text):
            continue
        if m["role"] == "user":
            chunks.append(f"• (Jordan/user) {text[:400]}")
        else:
            chunks.append(f"• {text[:400]}")
        # Classify actionable lines.
        for kw in BLOCKER_KEYWORDS:
            if re.search(rf"\b{re.escape(kw)}\b", low):
                blockers.append(text[:300]); break
        for kw in NEXT_KEYWORDS:
            if re.search(rf"\b{re.escape(kw)}\b", low):
                nexts.append(text[:300]); break
        for kw in DECISION_KEYWORDS:
            if re.search(rf"\b{re.escape(kw)}\b", low):
                decisions.append(text[:300]); break
    body = []
    if chunks:
        body.append("## Activity (auto-captured)\n" + "\n".join(chunks[:40]))
    if decisions:
        body.append("## Likely Decisions\n" + "\n".join(f"- {d}" for d in dedupe(decisions)[:12]))
    if blockers:
        body.append("## Possible Blockers\n" + "\n".join(f"- {b}" for b in dedupe(blockers)[:12]))
    if nexts:
        body.append("## Possible Next Steps\n" + "\n".join(f"- {n}" for n in dedupe(nexts)[:12]))
    body.append("> NOTE: keyword-based extraction is best-effort. Treat these as hints;"
                " the Activity section above is the reliable record.")
    return "\n\n".join(body)[:max_chars]


def dedupe(items):
    seen, out = set(), []
    for it in items:
        key = re.sub(r"[^a-z0-9]", "", it[:60].lower())
        if key and key not in seen:
            seen.add(key); out.append(it)
    return out


def session_titles(sessions):
    if not sessions:
        return "- No active sessions in window."
    out = []
    for s in sessions:
        title = s["title"] or f"(untitled {s['source']})"
        when = s["ts"].strftime("%H:%M") if s["ts"] else "?"
        out.append(f"- {title} — {when}")
    return "\n".join(out[:12])


def build_snapshot(profile, minutes):
    ts = now_ts().strftime("%Y-%m-%d_%H%M")
    path = os.path.join(BRIDGE_DIR, f"context-{ts}.md")
    messages, sessions = pull_recent(profile, minutes)
    summary = summarize(messages)

    state_content = ""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            state_content = f.read()

    snapshot = f"""# 🔄 Context Bridge — {ts}

## Session State
- **Saved:** {now_ts().strftime('%Y-%m-%d %H:%M')}
- **Profile:** {profile}
- **Capture window:** last {minutes} min (real content auto-pulled)
- **Resume From:** `09-Green Room/context-bridge/context-{ts}.md`

## Active Sessions (last {minutes} min)
{session_titles(sessions)}

{summary}

## 00-STATE.md (last known)
```
{state_content[:2000]}
```

## Resume Instructions
- Restore context from the Activity / Decisions / Blockers / Next Steps above.
- Check your lane's handoff folder in `01-HANDOFFS/` for pending work.
- Continue from the next steps listed.
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(snapshot)
    # Point latest-context symlink at the newest save.
    latest = os.path.join(BRIDGE_DIR, "latest-context.md")
    try:
        if os.path.islink(latest) or os.path.exists(latest):
            os.remove(latest)
        os.symlink(os.path.basename(path), latest)
    except OSError:
        pass
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", default="gentech",
                    help="Hermes profile whose session DB to capture (default: gentech)")
    ap.add_argument("--minutes", type=int, default=720,
                    help="How far back to capture (default 720 = 12h)")
    args = ap.parse_args()
    path = build_snapshot(args.profile, args.minutes)
    print(f"SAVED:{path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
