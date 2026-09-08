# Queue Reorganization Pattern (Jul 2026)

## Trigger

When the user asks to reorganize the build queue by priority, renumber items, or clean up ordering.

## Process

1. Load `build_queue.json`
2. Categorize each item:
   - **Revenue/income** — subscription hubs, paid APIs, grant apps, token launches, x402 services, anything that generates money. These go **first**, regardless of difficulty.
   - **Quick wins (easy)** — content, docs, light integrations
   - **Medium builds** — agents, dashboards, features
   - **Hard builds** — complex infrastructure, character APIs, journals
   - **Blocked → Jordan** — any item with `needs_jordan: true` OR `status: blocked`
3. Sort within each group: `in_progress` first, then by priority (high > medium > low)
4. Concatenate groups in order: Revenue → Quick → Medium → Hard → Jordan
5. Renumber sequentially from 1
6. Write back to file

## Renumbering Tips

- Use `insert()` at position, not append + sort, when adding new revenue items
- **Never do a full file rewrite** from `execute_code(json.dumps(data))` — use targeted array operations instead
- The tick script (`build_queue_tick.py`) is READ-ONLY — it never writes the queue
- Blocked items get `status: "blocked"` + `blocked_on: "jordan"` so the tick auto-routes them to the Jordan list

## Concurrent Write Protection Pitfall

**Jul 2026:** A concurrent cron (poker session) full-overwrote `build_queue.json`, losing 8 newly-added items (Arc Gateway, Lens AI, Hackathon, Circle Grant, etc.)

**Fix applied:** Items are now inserted at position 3-4 (after the first 3 revenue items) using targeted array insert, not a full file rewrite.

**Prevention rules:**
- Only one agent mutates the queue per tick
- The tick cron (`no_agent=True`) is READ-ONLY — verify, never write
- Nightly Build Session uses `patch` on specific fields, never full-file dump
- If you must rewrite (e.g. full renumbering), do it in isolation — no concurrent cron running
