# Session Monitoring Commands

## Quick Context Check

Check message count and compression status across all active sessions:

```bash
/usr/local/lib/hermes-agent/venv/bin/python3 -c "
import sqlite3, os
from datetime import datetime, timedelta

db_path = '/root/.hermes/profiles/gentech/sessions/sessions.sqlite3'
if not os.path.exists(db_path):
    print('No session database found')
    exit(0)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get sessions active in last 24 hours
threshold = datetime.now() - timedelta(hours=24)
cursor.execute('''
    SELECT id, title, message_count, created_at, last_message_at
    FROM sessions
    WHERE last_message_at >= ?
    ORDER BY last_message_at DESC
''', (threshold.isoformat(),))

sessions = cursor.fetchall()
if not sessions:
    print('No active sessions in last 24 hours')
    exit(0)

print(f'{"Title":<40} | {"Msgs":>5} | {"Last Msg":<20}')
print('-' * 75)

for sid, title, msg_count, created_at, last_msg in sessions:
    title = title[:38] if title else 'Untitled'
    last_msg_time = datetime.fromisoformat(last_msg).strftime('%Y-%m-%d %H:%M')
    print(f'{title:<40} | {msg_count:>5} | {last_msg_time:<20}')

conn.close()
"
```

## Memory Status Check

Check if memory is approaching 85% limit:

```bash
/usr/local/lib/hermes-agent/venv/bin/python3 -c "
import sqlite3, os

db_path = '/root/.hermes/profiles/gentech/sessions/sessions.sqlite3'
if not os.path.exists(db_path):
    print('No session database found')
    exit(0)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check memory tables
cursor.execute('SELECT COUNT(*) FROM memory_entries')
mem_count = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM user_profile_entries')
user_count = cursor.fetchone()[0]

print(f'Memory entries: {mem_count} (limit: 2200)')
print(f'User profile entries: {user_count} (limit: 1375)')
print(f'Memory usage: {mem_count / 2200 * 100:.1f}%')
print(f'User profile usage: {user_count / 1375 * 100:.1f}%')

if mem_count / 2200 > 0.85 or user_count / 1375 > 0.85:
    print('WARNING: Approaching memory limit - clean up required')

conn.close()
"
```

## Context Compression Status

Check which sessions have been compressed:

```bash
/usr/local/lib/hermes-agent/venv/bin/python3 -c "
import sqlite3, os

db_path = '/root/.hermes/profiles/gentech/sessions/sessions.sqlite3'
if not os.path.exists(db_path):
    print('No session database found')
    exit(0)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute('''
    SELECT title, message_count, compressed_message_count,
           CASE 
             WHEN compressed_message_count IS NULL THEN 0
             ELSE compressed_message_count
           END as actual_compressed
    FROM sessions
    WHERE last_message_at >= datetime('now', '-24 hours')
    ORDER BY message_count DESC
''')

sessions = cursor.fetchall()
if not sessions:
    print('No recent sessions')
    exit(0)

print(f'{\"Title\":<40} | {\"Msgs\":>5} | {\"Compressed\":>10} | {\"Ratio\":>6}')
print('-' * 70)

for title, msg_count, compressed_count, actual_comp in sessions:
    title = title[:38] if title else 'Untitled'
    ratio = actual_comp / msg_count * 100 if msg_count > 0 else 0
    print(f'{title:<40} | {msg_count:>5} | {actual_comp:>10} | {ratio:>5.1f}%')

conn.close()
"
```

## Context Bridge Status

Check which context-bridge files exist and their recency:

```bash
ls -lt /root/vaults/gentech/09-Green\ Room/context-bridge/
```

The `latest-context.md` symlink always points to the most recent bridge. If missing, no auto-save has been triggered yet this session.

## Usage Notes

- **Run from gateway terminal or system cron** — not from within an active session
- **Check daily** — before morning standup to spot bloat early
- **Alert threshold** — memory > 85%, messages > 30 per session
- **Bridge urgency** — memory ≥85% triggers auto-save; memory ≥90% is emergency
- **When to act** — if multiple sessions exceed thresholds, suggest `/new` or gateway restart

## Integration with Session Hygiene

These commands are the monitoring side of the session-hygiene skill's triggers:
- Memory pressure (>85%) → clean duplicates, remove stale entries
- Context bloat (>25 messages) → suggest fresh session, save context bridge
- Topic switch → detect via title patterns or manual `/new`
- Context bridge → script at `scripts/context-save.py` generates bridge in `09-Green Room/context-bridge/`

## Integration with Session Startup

After `/new`:
- `session-startup` reads `09-Green Room/context-bridge/latest-context.md` at step 4
- If a bridge exists, the agent resumes projects, decisions, and blockers
- If no bridge exists, falls back to handoffs folder, then session search

Use these commands to verify the skill's automated behaviors are working correctly.
