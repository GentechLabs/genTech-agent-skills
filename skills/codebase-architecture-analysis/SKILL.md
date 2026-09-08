---
name: codebase-architecture-analysis
description: "Systematically analyze a codebase to understand its architecture, data model, API surface, and server setup. Covers monorepos with Prisma/tRPC/Next.js/Express/Fastify patterns."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [codebase, architecture, analysis, monorepo, prisma, trpc, api, data-model]
    related_skills: [codebase-inspection, multi-repo-audit, project-audit]
prerequisites:
  commands: []
---

# Codebase Architecture Analysis

Systematically analyze a codebase to understand its architecture, data model, API surface, and server setup. Produces a structured summary suitable for onboarding, documentation, or handoff.

## When to Use

- User asks to "read and summarize" or "analyze the architecture" of a project
- Onboarding to a new codebase
- Preparing for a code review or contribution
- Understanding how layers connect (DB → API → UI)
- User asks "what does this project do" or "how is this structured"

## Approach: Layer-by-Layer Analysis

Follow this reading order to build understanding from data to interface:

### 1. Project Structure (2-3 files)
- Read root `package.json` → identify workspaces, monorepo tooling (pnpm, turborepo, moon)
- List key packages/apps to understand the high-level architecture
- Identify the tech stack (frameworks, ORMs, API layers)

### 2. Data Model (1-2 files)
- Find Prisma schema (`*.prisma`), Drizzle schema, or TypeORM entities
- Understand core entities, relationships, and enums
- Note JSON fields that store structured data (settings, state, config)

### 3. API Layer (3-5 files)
- Find router definitions (tRPC routers, Next.js API routes, Express routes)
- Map the API surface: what resources are exposed, what operations (CRUD, custom)
- Understand authentication/authorization patterns
- Note input validation (Zod schemas, etc.)

### 4. Server Setup (2-3 files)
- Find server entry point (Fastify/Express/Next.js)
- Understand how API is mounted, middleware stack
- Find how frontend is served (static files, SSR, etc.)

### 5. Business Logic (2-5 files)
- Find core processing/engine code
- Understand the main workflow (bot processing, trade execution, etc.)
- Trace how API calls flow to business logic

### 6. Supporting Layers (as needed)
- Exchange integrations, external services
- Event systems, streams, real-time features
- Configuration, environment variables

## Output Format

Produce a structured summary with sections:
- **Project Structure** - monorepo layout, key packages
- **Database Layer** - models, relationships, key fields
- **API Layer** - routers, endpoints, auth
- **Web UI** - frontend setup, how it's served
- **Business Logic** - core processing, workflows
- **Key Files** - paths to important files for future reference

## Tips

- **Start broad, then dive deep** - package.json first, then schema, then specific files
- **Follow the imports** - trace from entry points to understand dependencies
- **Look for patterns** - many projects use similar structures (router → handler → service → db)
- **Note JSON fields** - they often store flexible configuration (settings, state, metadata)
- **Check for extended clients** - Prisma `$extends`, custom model methods reveal business logic

## Borrowed: Persistent Repo-Context Map (from NanoNets/Graft, Aug 4 2026)

For repos we work in repeatedly, don't cold-start orientation every session — **build the map once, reuse it.** Borrowed from Graft (832★, MIT). Three mechanisms.

> **SHIPPED (Aug 5 2026): a tested, pure-stdlib implementation of all three lives at `scripts/context-graph/`** (queue #35). Use the tools instead of hand-porting:
> - `repo_map.py <repo>` → builds `.repo-map/{repo-map.md, graph.json, fingerprint.json}` (per-subsystem what/crux/depends_on/used_by). Python + JS/TS.
> - `repo_map_check.py <repo> [--rebuild]` → content-hash staleness check; exit 1 on drift (fails loudly), `--rebuild` auto-regens.
> - `blast_radius.py <repo> <file-or-module> [--transitive]` → resolve direct + transitive dependents before an edit.
> - `test_context_graph.py` → 3/3 pass.
> Verified end-to-end: iagent-x402 (20 files/6 subsystems, `blast_radius helpers.py` = 8 direct/12 transitive), gold-402 (standalone scripts = true-negative), agent-warfare (JS imports resolve). Wire-in: run `repo_map.py` once per repo, `repo_map_check.py --rebuild` at session start, `blast_radius.py` before multi-file edits.

### 1. Persistent repo map — "onboard once, not every time"
After the analysis below, commit a **compact repo-context markdown map** into the repo (gitignored `graph/` folder) or the vault. Shape per subsystem:
- **Summary** — plain-English: what this subsystem does
- **Crux** — the 2-5 lines that actually carry the logic (guard, skip condition, state change) — store as **text, not line numbers** (numbers drift; the lines don't)
- **Sources** — the exact files, each tracked by content hash (tells you when a node went stale)
- **Links** — typed `[[wikilinks]]`: `depends_on`, `part_of`, `uses`, `implements`, `produces`

Load this map into context at session start instead of re-grepping/reading from zero.

### 2. Staleness-aware refresh — "describe the code as it is right now"
Before acting on a mapped repo, run a **cheap structural freshness check**: stat file mtimes / content hashes against the map's fingerprint (~3ms). If anything moved (uncommitted edits included), re-gen the crux/references before proceeding. **Fail loudly on drift** (like `graft check` exits 1) rather than acting on a stale map.

### 3. Blast-radius on edit — "who depends on this"
Before editing a shared symbol/file, resolve its callers/imports/dependents (via the map's `uses`/`depends_on` links, or a callers-style query) and print the blast radius inline — the same nudge Graft's post-edit hook gives.

**Do NOT adopt the Graft CLI/dependency** (NanoNets control plane, global hooks into `~/.codex`/`.claude`/`.cursor`, 33-day-old project). Port the ~200-line structural core into our own design.

> Reference: `09-Green Room/specs/graft-context-graph-borrow.md`. Queue item #35.
> Implementation detail + import-resolution pitfalls: `references/context-graph-toolkit.md`.

## Pitfalls

1. **Don't read every file** - focus on the structural files that reveal architecture
2. **Skip test files initially** - they're useful later but not for architecture understanding
3. **Note commented-out code** - it often reveals planned features or past decisions
4. **Check for env vars** - they reveal external dependencies and configuration
5. **Look at package.json dependencies** - they reveal the actual tech stack
6. **Store crux as text, not line ranges** - line numbers drift when unrelated code shifts above them
7. **Empty allow-list must mean DENY** - if a map's link/scope list is empty, don't treat it as "everything allowed"

## Example: OpenTrader Analysis

For a monorepo with packages: `app/`, `packages/trpc/`, `packages/prisma/`, `packages/db/`, `packages/bot/`:

1. Root `package.json` → pnpm workspaces, moon tooling
2. `packages/prisma/src/schema.prisma` → User, ExchangeAccount, Bot, SmartTrade, Order models
3. `packages/trpc/src/routers/appRouter.ts` → bot, exchangeAccount, smartTrade routers
4. `packages/bot/src/server.ts` → Fastify server, tRPC adapter at `/api/trpc`
5. `packages/bot/src/processing/bot/bot.processing.ts` → strategy execution engine
6. `packages/db/src/xprisma.ts` → extended Prisma client with custom model methods

Result: Complete understanding of the data model, API surface, and bot processing architecture.
