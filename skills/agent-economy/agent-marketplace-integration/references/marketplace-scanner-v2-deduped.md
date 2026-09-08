# Marketplace Scanner V2 — Deduped NEW-Only Hunting Pattern

**Proven Aug 5, 2026 (the "crown job", queue #42).** Reusable pattern for any
"scan for new marketplaces without re-reporting what we already have" task.

## The core problem
A naive marketplace scanner re-reports platforms we're already on every run —
noise, wastes tokens, and hides genuinely new opportunities. The V2 fix:
**seed the scanner with a machine-readable exclusion list, then only hunt NEW
platforms**, each scored with "why be there" + income estimate + entry friction.

## Architecture (two pieces)

### 1. `marketplace-seed.py` — the exclusion-list parser
Parses `11-Mess Hall/marketplace-listings-registry.md` into JSON:
- `already_listed` — platform names from the `🟢 LIVE LISTINGS` table rows
- `watchlist` — names from the `🟡 PENDING / WATCHLIST` table
- `known_not_pursued` — names from the `⚪ KNOWN BUT NOT PURSUED` section
- `all_keywords` — every URL host + `**Bold**` name across the whole file
- `rule` — self-documenting dedup rule

Markdown parsing gotchas (verified):
- Strip `**` bold markers and `[name](url)` links from table cells.
- Split the file on `## ` section headers to classify rows by status section.
- `known_not_pursued` tables may be sparse — rely on `all_keywords` for the
  robust dedup match.

### 2. The cron prompt — DEDUP + NEW-ONLY + why/income/friction
Attach the seed script as the cron's `script=` so its JSON is auto-injected.
Prompt instructs the agent to:
1. Read the seed exclusion list (injected or run it).
2. **DEDUP RULE:** a marketplace is NEW only if its name AND domain do NOT
   appear in `already_listed`, `watchlist`, `known_not_pursued`, or
   `all_keywords`. If matched, SKIP — we already have a presence there.
3. Hunt NEW sell-side marketplaces with `web_search` (free), and for each NEW
   candidate deliver:
   - **Why we should be there** — what it does, who hires on it, what's in it
   - **Income estimate** — realistic $/mo or $/task (be honest, don't inflate)
   - **Entry friction** — open-entry? needs >$50 stake? remote?
4. Append genuinely-worthy NEW platforms to the registry as WATCHLIST rows
   (append, don't overwrite), and flag them for Jordan.
5. Auto-bid Hive separately (WIN tasks, don't just report).

## Output shape
Report has a dedicated **`🌐 NEW Marketplaces Found (deduped vs registry)`**
section — this is the crown job, not the Hive task table.

## Live-test result (Aug 5, 2026)
One run found 3 genuinely new sell-side platforms — BotWork (P2P agent
freelance, Base escrow, first-mover), Freelance AI by PayAI (reuses a
facilitator already in our stack), Amadeus Agent Hub (DeFi agents, cross-chain)
— each with why/income/friction, all verified not in the registry, appended as
watchlist rows 11–13.

## Why "Forge = desktop lane" matters for routing
Anything needing a desktop (MetaMask signing, browser login, local files,
websites Jordan must open) routes to Forge regardless of group — see
`01-HANDOFFS/sync-protocol.md`. When a marketplace registration requires
Jordan at a desktop (wallet link, KYC, browser login), route it to
`gentech-to-forge/` (or tag it "Forge (desktop)") so it lands on the right lane.
