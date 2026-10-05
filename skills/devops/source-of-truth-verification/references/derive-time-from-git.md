# Deriving a Clock from Git History

When a data artifact stores **state but not time** — no `created_at`, no `updated_at`, no versioning — the question "when did this change?" and "is it moving?" cannot be answered from the artifact itself. If that artifact lives in a git repo, the clock is already there: every commit that touches the file carries an immutable timestamp. Reading the history is usually better than stamping the file, because history is retroactive, writer-independent, and read-only.

## When to use this pattern

- A JSON/CSV/YAML file is the source of truth but has no date fields.
- Adding timestamps would require touching many writers, and a forgotten writer would silently corrupt the timeline.
- You need to know movement retroactively (existing items, not just future ones).
- Multiple agents or scripts mutate the file, so a single "update on write" hook is unreliable.

## When NOT to use this pattern

- The file is not tracked in git, or its history is regularly rewritten/grafted/shallow.
- The file is moved or renamed often — `git log -- <path>` only sees the path as it existed at each commit.
- You need sub-second or real-time freshness; git commits are coarse.
- The file's logical identity does not match the file path (e.g., content imported from another system with its own clock).

## The core technique

1. List commits that touch the file:  
   `git log --format='%H|%aI|%s' --reverse -- <path>`
2. Reconstruct the artifact at each commit:  
   `git show <sha>:<path>`
3. Compare adjacent snapshots and emit events (`created`, `changed`, `returned`, `removed`).
4. Timestamp each event with the **newer** commit's author date.

The comparison key is the hard part. Use a stable identity derived from the item itself (e.g., a normalized name), not the file's internal `id`, because renumbering/migration scripts change ids while the item stays the same.

## Identity and signature rules

- **Identity key**: choose a field that survives renumbering and bulk restructuring. A normalized name is usually right; an internal numeric id is usually wrong.
- **Signature**: decide what counts as "movement". For a build queue, status + assignment is meaningful; a note edit is not. A bulk re-add (same status) should be a `returned` event, not a `changed` event, or age metrics will reset falsely.
- **Birth ledger**: an item must only be born once. Track seen identities in a set as you walk history oldest→newest; any later appearance of a known identity is a `returned`, never a `created`.

## Required honesty about the evidence base

- Count and report unreadable snapshots (path didn't exist at that commit, JSON parse failed, etc.).
- If a change happens between two readable commits, it is dated at the **later** readable commit. This can shift an event across a time-window boundary.
- If **no** snapshot is readable, raise — do not report "no movement". "Could not look" and "nothing moved" are different answers, and confusing them is the single worst failure mode for this kind of tool.

## Minimal output shape

A command-line tool should expose at least:

- `summary --hours N` — N move(s) in last N hours, M shipped, latest event.
- `moved --hours N` — list of events with timestamps.
- `age --min-days D` — open items untouched for D+ days, dated from the last meaningful change.
- `item <id-or-key>` — full life story of one item.
- `--selftest` — checks against independently known facts from the same history.

## Verification

- Confirm an independently known fact (e.g., "#4 shipped on 2026-10-03") against the derived timeline.
- Simulate total read failure (patch `git show` to return nothing) and confirm the tool refuses rather than reporting zero.
- Simulate a renumbered item and confirm it is not reported as a new birth.
