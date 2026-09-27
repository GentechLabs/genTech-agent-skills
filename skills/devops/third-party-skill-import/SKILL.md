---
name: third-party-skill-import
description: "Evaluate and import third-party agent skills into Hermes. Covers discovering skill repos, evaluating relevance, adapting OpenClaw/Clawdbot skills to Hermes format, and installing. Use when the user wants to bulk-import skills from external sources or evaluate a skill collection."
version: 1.1.0
author: Gentech
---

# Third-Party Skill Import

Evaluate, adapt, and install skills from external agent ecosystems (OpenClaw, Clawdbot, Claude Code, etc.) into Hermes.

> Version 1.1.0 — merged 2026-09-26 Council Overnight. The technique-harvest triage (*when the collection
> is an API manual*) was learned on one seat and three import-hygiene pitfalls on another. Both halves are
> kept; no section was dropped.


## Workflow

### 1. Discover Skill Sources

Common skill repositories:
- **OpenClaw Master Skills:** `github.com/LeoYeAI/openclaw-master-skills` (1600+ skills)
- **ClawHub:** `clawhub.com/skills/` (hub for OpenClaw skills)
- **Hermes Skills Hub:** `hermes skills search` / `hermes skills browse`
- **Individual repos:** GitHub search for `SKILL.md` files

### 2. Clone and Scan

```bash
# Clone to /tmp for evaluation (not permanent storage)
cd /tmp && git clone --depth 1 <repo-url>
cd <repo-name>

# Count skills
ls skills/ | wc -l

# Scan for relevant categories
ls skills/ | grep -iE "crypto|defi|solana|agent|finance|trading"
```

### 3. Eat the Meat, Spit Out the Bones

**Jordan's rule:** When a repo drops 13 skills, you cherry-pick the 7 that serve you. Never import an entire catalog. The question isn't "is this cool?" — it's "will we use this before it goes stale?"

Sort candidates into three piles:

| Pile | Action | Example |
|------|--------|---------|
| 🟢 **Directly useful** | Import now | Gateway doctor, stack doctor, interview-me |
| 🟡 **Valuable but partial** | Pick specific pieces | Field kit: 7/13 imported |
| 🔴 **Dead weight** | Skip entirely | Environment migration, token audit (don't have the data) |

**The test:** If you wouldn't miss it by next week, it goes in the 🔴 pile.

#### Harvest the technique, decline the dependency (when the collection is an API manual)

A large first-party collection from a vendor is often **not portable knowledge** — it is an **API
manual for a metered cloud**, with genuine technique woven through the vendor's own tool names.
Importing it installs that vendor into every agent's tool surface. That is a fourth outcome beside the
three piles: **read it, take the model-agnostic parts, adopt nothing.**

**Triage the collection by COUPLING before you read it.** For each skill, count references to the
vendor's own tool names per 1,000 words. Low ratio ⇒ the body is portable prose (principles, measured
findings); high ratio ⇒ a tool manual that means little without the cloud. Sort by that ratio and read
the low-coupling tail first — the transferable technique concentrates there. On a 65-skill gaming
collection it was roughly the bottom third, and it carried every measured finding worth keeping.

**Verify compatibility empirically BEFORE judging value** — "not compatible" and "not worth it" are
different verdicts and only the first is checkable:
- **Format** — if it is Agent Skills (`SKILL.md` + YAML frontmatter, agentskills.io) it is already our
  shape, so there is no adaptation step to budget for.
- **Transport** — read how it connects (`https://mcp.<vendor>/mcp`, Streamable HTTP + OAuth) and
  confirm Hermes speaks it natively: `hermes mcp add --url <url> --auth oauth`.
- **Endpoint** — probe it live. An unauthenticated `POST` returning **401** proves the server is real
  and auth-gated, as opposed to a hostname that resolves to nothing.

Then report the two claims separately: *compatible* (measured) and *worth it* (judged). A vendor can be
perfectly compatible and still be the wrong purchase.

**The declining criterion:** when the collection wraps models or rails we already call directly,
adopting it inserts a metered middleman over capability we own. Take the technique, skip the dependency.

**Port into existing skills — do not install the collection.** Folding a few findings into the skills
that already own the territory keeps the library class-level, instead of adding 65 vendor-prefixed
skills nobody will ever load. **When an imported rule CONTRADICTS something our own skill already
teaches, that is the highest-value find of the whole exercise** — fix OUR skill in place and state
which way it now reads, rather than leaving two instructions in conflict. A collection that corrects
our own advice has already paid for itself.

#### The Decides-Alone Test (Jordan, 2026-09-20) — apply BEFORE the piles

Jordan clarified the rule: *"I just meant, take what's useful and lose the rest… for people who are like me
who just need to execute, execute, execute more than think and stuff — I just wanted the agent to be smarter
if it had to make decisions on its own."*

So there is a gate ahead of the three piles:

> **Does this make the agent better at deciding and acting ON ITS OWN — or does it make the agent deliberate
> more, surface more choices, and hand decisions back?**

**The first is meat. The second is a bone, even when the mechanism is genuinely clever.**

Most published agent tooling is built for an operator who *wants* to be consulted — guided, prompted, walked
through options. That is a real market and it is not us. **A mechanism that adds thinking without adding
decisions is a downgrade**, and it will show up as an agent that stops mid-run to ask a question it should
have answered itself.

**AND NAME THE BOUNDARY.** When you import a mechanism, state what it must **not** be allowed to mean, in
the same breath as what it is for. A mechanism absorbed without a boundary gets read in whatever direction
is most convenient to the agent.

*Worked failure, so this isn't abstract:* we absorbed "calibrated confidence — back off when unsure" (a
model-selection instruction) with no boundary. Inside a day it had become *"unsure about the model"* →
*"unsure about the task"* → *"ask Jordan."* Jordan caught it, not us. See `develop-and-verify` →
"Run to the Stopping Point" for the behavioural rule that came out of it.

### 4. Evaluate Relevance

For each candidate skill, check:
- **Does it solve a problem we have?** (not just "cool to have")
- **Does it require API keys we don't have?** (prefer no-key solutions)
- **Does it conflict with existing skills?** (check for duplicates)
- **Is it maintained?** (check last commit date)
- **Is it Hermes-compatible?** (can it be adapted?)

### 4. Read SKILL.md

Read the full SKILL.md to understand:
- What it does
- What it requires (env vars, binaries, APIs)
- What commands it uses
- How it stores data

### 5. Adapt to Hermes Format

OpenClaw/Clawdbot skills need adaptation:

| OpenClaw Pattern | Hermes Equivalent |
|------------------|-------------------|
| `uv run {baseDir}/scripts/...` | `python3 {baseDir}/scripts/...` or `terminal()` |
| `clawhub install ...` | `skill_manage(action='create')` |
| `{baseDir}` variable | Actual path to skill directory |
| `~/.clawdbot/skills/...` | `~/.hermes/profiles/<profile>/skills/...` |
| OpenClaw metadata | Hermes frontmatter |

**Key adaptation steps:**
1. Copy SKILL.md content
2. Update paths (replace `{baseDir}` with actual paths)
3. Update commands (replace `uv run` with `python3` or `terminal()`)
4. Update data storage paths
5. Keep the knowledge — the value is in the SKILL.md content, not the tooling

### 6. Install via skill_manage

```python
skill_manage(
    action='create',
    name='skill-name',
    content='---\nname: skill-name\ndescription: ...\n---\n\n# Skill Content...',
    category='appropriate-category'
)
```

### 7. Clean Up

```bash
rm -rf /tmp/<repo-name>
```

## Known Sources

See `references/external-skill-repos.md` for curated repos: Mercury Skills (147+, MIT, drop-in), Google Agent Skills (30, Cloud/Gemini), OpenClaw (1600+, needs adaptation). Includes install patterns and prefix conventions.

## Naming Rules

**Skill names MUST be class-level, not product-specific.** When the user says "install solana-agent-toolkit" or "install goplus-security-api", the agent should evaluate the repo but name the installed skill at the class level:

- ❌ `solana-agent-toolkit` → too specific, tied to one product
- ✅ `solana-agent-patterns` or just integrate into existing `solana` skill
- ❌ `goplus-security-api` → too specific, API-product name
- ✅ `token-security-audit` or integrate into existing `solidity-security`

**The test:** Would this skill name still make sense 6 months from now, after the product rebrands, pivots, or dies? If not, it's too specific. Class-level names survive product lifecycle changes.

## Pitfalls

- **Check for a platform-specific installer FIRST.** Repos often ship one `curl | bash` script PER agent (`*-claude-code-setup.sh`, `*-hermes-setup.sh`, `*-openclaw-setup.sh`). Read the repo README before running anything and pick the installer for OUR agent (Hermes) — not whichever you spot first. Proven Aug 3, 2026: Minara ships both `claudecode-minara-skill-setup.sh` AND `hermes-minara-skill-setup.sh`; running the Claude Code one landed the skill in `~/.claude/skills/` instead of the Hermes skills dir, then had to be relocated.
- **Vet for trojan subscription funnels before installing.** Some "free" skills are marketing funnels: free CLI + skill install, then a paywall behind a paid API key / subscription before the tool is usable (e.g. Minara = free install, then $20–50/mo just to touch the API key). Before installing, check the skill's auth surface (frontmatter `primaryEnv` / `requires` / `Credentials` section) and the product's pricing page. If it's a rent-the-API walled model and we're building the same thing ourselves, skip it — or keep it as competitive intel (their pricing page is a live signal for what the market tolerates). Proven Aug 3, 2026: installed Minara, discovered the subscription funnel, uninstalled.
- **Never trust an installer's self-reported "already set up / logged in" echo.** Setup scripts often mis-detect success — e.g. Minara's installer ran `minara whoami`, which isn't a real subcommand (it just prints usage), so the script treated the failure as "Logged in: yes" and skipped the real auth. Always verify state yourself with the tool's *documented* command (`minara account`, not a guessed alias) before telling the user setup is complete. A false-positive login echo means the user believes they're authenticated when they're not. Proven Aug 3, 2026: `curl | bash` installer for Minara reported "Logged in: yes" but `minara account` returned "You are not logged in."
- **Check where files actually landed under a Hermes profile.** Because the profile overrides `$HOME`, a generic installer that writes to `~/.claude/`, `~/.minara/`, etc. resolves to `<profile>/home/.claude/`, NOT `/root/.claude/`. After any third-party installer, `ls` the target dir and confirm the real path before reporting location.
- **Don't bulk-install everything.** Cherry-pick 5-10 relevant skills, not 100+.
- **Before adopting a vendored harness-style skill, verify its own machinery works.** Run the vendor's
  test suite and validate an intentionally-mistaken draft against its schema validators — a harness that
  catches your planted errors (bad schema fields, inflated severity) is machinery you can trust; one that
  waves through garbage is documentation, not tooling. This also surfaces the exact field contracts your
  future writes must satisfy, before they cost correction cycles in a real run.
- **Check for API key requirements.** Skills needing keys you don't have are dead weight.
- **Adapt paths.** OpenClaw uses `{baseDir}`, Hermes uses actual paths.
- **Keep the knowledge.** The value is in SKILL.md content, not the wrapper tooling.
- **Don't duplicate.** Check if a similar skill already exists before creating.
- **Don't use product names for skill names.** Always use class-level names (see Naming Rules above).
- **Use prefixes when installing from external repos.** When a repo's skill names could collide with existing Hermes skills, prefix the installed names: `mercury-` for Mercury Skills, `google-` for Google Skills. Our `solidity-security` skill existed before we imported `security-audit` from Mercury — without prefixes, name collisions would overwrite existing skills. Proven Jun 6, 2026.
- **Read the repo's own bundle manifests separately from its skills.** A repo's `skills/CLAUDE.md` (or root README) can describe a DIFFERENT product than the skills in it — shared-repo convention files drift or get copied from unrelated projects. Never summarize a repo from one file at its root; read each `skills/<name>/SKILL.md` you would actually import. The root doc told you nothing about the repo you cloned.
- **Audit an installer's BLAST RADIUS before ever running it, and prefer read-only evaluation for very fresh repos.** Some installers edit EVERY profile's config.yaml (a shared `enabled:` plugin list) and write into EVERY profile's `.env` in one run — a repo days old with a handful of stars has no track record to justify multi-profile writes. Clone to /tmp, read the install source for exactly which paths it touches and whether it backs up + writes atomically, use `--check` / `--no-write` flags if present, and default to evaluating without installing at all.
- **A hosted-API dependency is a data-egress decision, not just a cost decision.** Skills built around a third-party cloud service often send prompt text out (with masking tiers, private-profile modes, or features-only modes). For sensitive lanes (treasury, credentials), check the privacy modes in the source before wiring a live channel into it — and read the injection/defense surfaces it happens to cover, since enabling inbound integrations opens those surfaces.
- **MCP server repos need build step.** Unlike plain SKILL.md repos, repos with MCP servers (like COTI) have TypeScript/JavaScript that must be compiled before the tools work. Always check for `package.json` with build scripts, `tsconfig.json`, or `run-stdio.ts`. If the repo has `npm run build`, run it before installing skills. Proven Jun 14, 2026: COTI skills repo had 8 SKILL.md files + 2 MCP servers requiring `npm install && npm run build`.

## 🌐 The npx skills Ecosystem — Discovery & Publishing

A major addition to the agent skill landscape: the `npx skills` ecosystem (by vercel-labs/skills, 25.8k★). Skills are markdown files with YAML frontmatter, stored in a `skills/{name}/SKILL.md` directory structure in any GitHub repo. The CLI (`npx skills`) installs them into 72+ agent platforms (Claude Code, Codex, Cursor, OpenCode).

### Ecosystem Landscape (Jul 2026)

| Package | Stars | Focus | Install cmd |
|---------|-------|-------|-------------|
| `vercel-labs/skills` | 25.8k | The CLI itself | `npx skills` |
| `emilkowalski/skills` | 8.5k | UI animation, design engineering | `npx skills add emilkowalski/skills` |
| `ConardLi/garden-skills` | 9.4k | Web design, image gen, RAG, video | `npx skills add ConardLi/garden-skills` |
| `GentechLabs/genTech-agent-kit` | — | Agent dev, x402, DeFi, RWA stocks | `npx skills add GentechLabs/genTech-agent-kit` |
| Solana Foundation | — | Agent skills, SKILL.md at solana.com | `npx skills add solana-foundation/...` |

### Installing Skills from the Ecosystem

```bash
# Install all skills from a repo
npx skills add owner/repo

# Install specific skills
npx skills add owner/repo --skill skill-name

# List available skills without installing
npx skills add owner/repo --list

# Search across all repos
npx skills find agent
npx skills find defi --owner GentechLabs
```

### Publishing Our Own Skills

Any GitHub repo with a `skills/` directory (or root `SKILL.md`) is automatically installable by the ecosystem. To publish:

1. **Create the skills directory structure:**
   ```
   repo/
   ├── SKILL.md              # Root-level skill (discovered by default)
   └── skills/
       ├── skill-name/
       │   └── SKILL.md       # Individual skill (with --skill flag)
       └── another-skill/
           └── SKILL.md
   ```

2. **SKILL.md format (YAML frontmatter + markdown):**
   ```yaml
   ---
   name: my-skill
   description: "What this skill teaches. One clear sentence."
   ---
   
   # My Skill
   
   Content here.
   ```

3. **No registration needed** — any public GitHub repo works. The CLI resolves `owner/repo` to `github.com/owner/repo` and scans for skill files.

4. **Discoverability:** Add GitHub topics (`skills`, `agent-skills`, `mcp`, `x402`) so `npx skills find` picks you up.

5. **Versioning:** Tagged releases = skill version pinning for users.

### Gap Analysis

The npx skills ecosystem currently focuses on UI/design/creative skills. **No one publishes agent infrastructure skills** — x402 payments, DeFi, multi-chain settlement, RWA tokenized stocks. That's our lane.

### Key Difference from Hermes Skills

| Dimension | Hermes Skills | npx skills Ecosystem |
|-----------|---------------|---------------------|
| **Scope** | Our agent's procedural memory | Universal agent skill distribution |
| **Format** | YAML frontmatter + markdown | Same format (compatible) |
| **Installs via** | `skill_view(name)` | `npx skills add owner/repo` |
| **Audience** | Gentech agents | Any agent on 72+ platforms |
| **Distribution** | Vault-based | GitHub-based, world-readable |

Hermes skills are our internal operational knowledge. npx skills are our external, installable-by-anyone agent content. The format is the same — so content written for one can be cross-published to the other after review.

When a third-party skill repo includes MCP servers (TypeScript/JavaScript), follow this workflow:

### 1. Clone All Repos
```bash
cd /root/projects/<integration-name>
git clone <skills-repo>       # SKILL.md files
git clone <mcp-server-repo>   # MCP server code
git clone <messaging-repo>    # Additional servers if needed
```

### 2. Build MCP Servers
```bash
# Check for build scripts
cat <server>/package.json | grep -A 5 '"scripts"'

# Install dependencies
cd <server> && npm install

# Build (if build script exists)
npm run build

# Verify output
ls dist/  # or build/
```

### 3. Create stdio Wrapper (if needed)
Some MCP servers need a `run-stdio.ts` entry point:
```typescript
#!/usr/bin/env node
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import createServer from "./index.js";
const server = createServer({ config: { debug: false } });
const transport = new StdioServerTransport();
await server.connect(transport);
```

### 4. Install Skills
Copy SKILL.md files into Hermes skill directory:
```python
skill_manage(action='create', name='skill-name', content='...', category='...')
```

### 5. Configure MCP Servers in Hermes
Add to `config.yaml` under `mcp.servers`:
```yaml
mcp:
  servers:
    server-name:
      command: npx
      args: ["tsx", "/absolute/path/to/run-stdio.ts"]
```

### 6. Verify
Test with a simple tool call through the MCP server.

**Example: COTI Integration (Jun 2026)**
- Cloned 3 repos: `coti-skills`, `coti-mcp`, `coti-agent-messaging`
- Built both MCP servers (TypeScript → JavaScript)
- 8 SKILL.md files ready for installation
- MCP servers: `coti-mcp` (30+ tools), `coti-agent-messaging` (18 tools)
- **Status:** Build interrupted, needs completion

## Example: OpenClaw Master Skills Import

1. Cloned `github.com/LeoYeAI/openclaw-master-skills` (1609 skills)
2. Scanned for crypto/finance/agent categories
3. Evaluated top candidates:
   - `agent-team-orchestration` → multi-agent dispatch ✅
   - `agent-security-hardening` → prompt injection defense ✅
   - `stock-analysis` → Yahoo Finance, rumor scanner ✅
   - `bitmart-wallet` → 12 endpoints, no API key ✅
   - `vincent-trading-engine` → Polymarket specific, skip ❌
   - `binance-derivatives` → Binance specific, skip ❌
4. Adapted and installed 4 skills
5. Saved vault reference: `03-Projects/Research/openclaw-master-skills.md`
6. Cleaned up `/tmp/`

## When to Use

- User shares a link to a skill repository
- User wants to "install all skills from X"
- User asks "what skills are available for X"
- Building a new project and need specialized skills
