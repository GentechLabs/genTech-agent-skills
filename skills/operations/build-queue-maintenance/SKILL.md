---
name: build-queue-maintenance
description: >-
  Maintain the canonical build queue at scripts/build_queue.json. After every
  add, remove, or status change, renumber all items sequentially so the highest
  ID always equals the total count. Never let IDs drift into the 80s/90s when
  there are only 10-15 items.
always: true
---

# Build Queue Maintenance

## Golden Rule

**After every modification to the build queue, renumber all items 1..N.**

The highest item ID must always equal the total item count. If there are 17
items, IDs are 1-17. Never 1, 2, 3, ... 87, 88, 91.

## When to Renumber

- After marking an item as `shipped` or `cancelled` (removes it from active)
- After adding a new item
- After re-prioritizing items
- After any bulk edit

## How to Renumber

1. Load `scripts/build_queue.json`
2. Sort active items by priority: `urgent → high → medium → low`
3. Assign sequential IDs 1..N to active items
4. Put cancelled/shipped items at the end with their own sequential IDs
5. Update `summary.total` to match `len(items)`
6. Update `summary.pending`, `summary.in_progress`, `summary.shipped`
7. Update `summary.needs_jordan` (count of active items with `needs_jordan: true`)
8. Update `gate_summary.human_gated` and `gate_summary.decision_gated`
9. Bump `version` by 1
10. Set `updated` to today's ISO date

## Priority Sort Order

```python
priority_order = {'urgent': 0, 'high': 1, 'medium': 2, 'low': 3, 'none': 4}
```

Within the same priority, sort by original ID (oldest first).

## Example

Before (17 items, highest ID 91):
```
#87 Paymenter Marketplace
#88 Pterodactyl Outreach
#89 WHMCS/Blesta Port
#90 Hippocratic AI
#91 Great Agent Hackathon
```

After renumber (17 items, highest ID 17):
```
#1  Keeperhub Hackathon (urgent)
#2  FrameForge (high)
...
#16 Hippocratic AI (low)
#17 OKX (cancelled)
```

## Standalone Renumber Script

For manual renumbering (without a Forge handoff), use:

```bash
python3 scripts/renumber_queue.py          # dry run (preview changes)
python3 scripts/renumber_queue.py --apply   # apply renumber
```

This is useful when you've manually added or removed items from the JSON file and
need to clean up IDs without going through the full tick script.

## Tick Script

The tick script at `scripts/tick_build_queue.py` handles the renumbering
automatically when run with `--apply`. It reads `forge-completions.md`,
updates the queue, and renumbers. Run it after every Forge handoff.

```bash
python3 scripts/tick_build_queue.py --apply
```

## Verification Before Removal

**Do not mark items as "disputed" or "cancelled" without direct evidence.**

The Kite AI incident (Jul 2026) proved this: an item was flagged as "disputed" (no source URL, $0K prize) and removed from the queue. Three days later, Kite AI was confirmed real — they had open-sourced 14 MIT-licensed x402 skills and had real engagement metrics we could have checked.

**Verification checklist before marking anything disputed:**

1. **Check the source URL** — if the build queue entry has a URL, fetch it with curl or web_extract. If there's no URL, search the web for the product name.
2. **Check social media** — search X/Twitter for the account/product name. Engagement metrics (likes, retweets, views) are evidence of existence.
3. **Check GitHub** — search for the org/repo. Even 0 stars with recent commits is evidence the project exists.
4. **Check the vault** — session_search the topic. We may have discussed it in a prior session.
5. **Ask Jordan first** — "Item #X was flagged as potentially fake. I checked [source/social/GitHub] and found [evidence]. Should I keep or remove it?"

**The cost of a false negative:** We miss a real ecosystem player, a real hackathon prize, or a real partnership opportunity. The cost of a false positive (keeping a dead item one more cycle) is near zero — it just sits in the queue until the next cleanup.

## Gate Summary Verification

After renumbering and updating status counts, verify the `gate_summary` section matches actual items:

```python
human_gated = sum(1 for i in data['items'] if i.get('human_gated', False))
decision_gated = sum(1 for i in data['items'] if i.get('gate_type') == 'decision')
autonomous = sum(1 for i in data['items'] if not i.get('human_gated', True))

data['gate_summary']['human_gated'] = human_gated
data['gate_summary']['decision_gated'] = decision_gated
data['gate_summary']['autonomous'] = autonomous
```

**Common drift pattern:** `human_gated` drifts when items are added/removed without updating the summary. The cancelled item (#22 OKX) still has `human_gated: true` — it counts toward the total even when cancelled. Always recount from `items[]` rather than incrementing/decrementing the old value.

## Git Push Rejection Handling

**REMOTE MAP (near-miss Aug 29, 2026 — do not repeat):** the vault has multiple remotes. `vault` = GentechLabs/gentech-vault.git (**the vault — push here**, `git push vault HEAD:main`). `origin`/`hub` = ProtoJay4789.github.io (**the portfolio site — NEVER push/pull vault content there**; different history, a `git pull --rebase origin main` in the vault tried to replay 430+ unrelated commits). The conflict recipe below is for the `vault` remote only — substitute `vault` for `origin`.

When `git push vault` is rejected because the remote is ahead (concurrent pushes from other agents or Jordan):

```bash
cd /root/vaults/gentech
git fetch vault
git pull --rebase vault main
# If rebase conflicts on build_queue.json, resolve with theirs:
git checkout --theirs scripts/build_queue.json
git add scripts/build_queue.json
git rebase --continue
git push vault HEAD:main
```

**Why this happens:** The vault has two remotes (`origin` = portfolio site, `vault` = gentech-vault.git). Other cron jobs or Jordan's manual edits can push to the same branch between the queue read and the commit. Always expect the remote to be ahead.

## gh CLI Auth Workaround for PR Checks

The `gh` CLI may fail with `GITHUB_TOKEN` env var conflict (stale token in env overrides valid token in `hosts.yml`). When this happens, use curl with the token extracted from `hosts.yml`:

```bash
GH_TOKEN=$(grep 'oauth_token:' ~/.config/gh/hosts.yml | head -1 | awk '{print $2}' | tr -d '"')
curl -s -H "Authorization: token $GH_TOKEN" \
  "https://api.github.com/search/issues?q=author:ProtoJay4789+type:pr+is:merged&per_page=10"
```

See the `github-auth` skill for the full GITHUB_TOKEN env var conflict resolution pattern.

## Why This Matters

- Clean IDs make the queue readable at a glance
- Prevents confusion when discussing item numbers ("#91" when there are 17 items)
- Makes maintenance scripts simpler
- Jordan doesn't have to mentally map "item 87" to "the 4th item"
