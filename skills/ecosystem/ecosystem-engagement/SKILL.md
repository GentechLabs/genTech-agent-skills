---
name: ecosystem-engagement
description: >-
  Three-way repo scan (Contribute / Integrate / Use) + star-analyze-pollinate
  pattern for engaging with open-source projects in the x402 and AI-agent
  ecosystem. Used across x402 Foundation, Dexter-DAO, Xona Labs, hyre-mcp,
  kepano-obsidian, OpenSpace, Remotion, and others.
---

# Ecosystem Engagement

Standard playbook for engaging with open-source projects in GenTech Labs' ecosystem.

## Six-Way Engagement Scan

For every new repo or org encountered, classify into one of these engagement types:

### 🔧 Fork & Extend — Maintain a Fork, Build on Top

When a repo has high strategic value but you can't PR into it (fork restricted, review too slow, need custom features), **fork it, maintain it, and build your own plugins on top.** This turns the upstream into a platform you extend rather than a destination you PR into.

**Pattern:**
1. **Fork early** — before upstream gets too far ahead. Check `allow_forking` via API first.
2. **Add upstream remote** — `git remote add upstream https://github.com/original/repo.git`
3. **Fast-forward regularly** — `git fetch upstream && git merge upstream/master --ff-only`
4. **Track commit gap** — `git rev-list --count master..upstream/master` tells you how far behind
5. **Fix build breaks** — upstream dependency bumps often break forks. Fix locally rather than PRing (faster).
6. **Build custom plugins** — the fork's plugin system is your GenTech Shop extension surface

**Real example — Paperclip fork (Jul 27 2026):**
- Upstream: `paperclipai/paperclip` (74.8K stars, MIT, control plane for AI companies)
- Fork: `ProtoJay4789/paperclip` — forked April 13, caught up 1,026 commits on Jul 27
- Build fix: OpenTelemetry `resourceFromAttributes` deprecated in newer deps — patched locally
- Plugin target: GenTech Shop panel (build queue + service catalog + ClawWork squad management)
- Hermes adapter: built-in `hermes_local` and `hermes_gateway` — no plugin install needed
- PR upstream: Not needed — we extend through plugins, not core changes

**When to use:** Upstream is MIT/Apache, has a plugin system or adapter registry, we need custom surfaces (Shop, queue, squad mgmt), and the build cost of keeping a fork current is low (pnpm install + occasional build fix).

### 🛠️ Ecosystem Partnership — Build Complementary Skills

When a project's ecosystem has a skill/passport/plugin distribution model (skills.sh, Kite Passport, npx skills), the highest-leverage contribution is building **complementary skills** that bridge both ecosystems rather than PRing into their core repo.

**Pattern:**
1. **Identify their distribution model** — skills.sh, npx skills, MCP servers, plugins
2. **Analyze their skill format** — read 2-3 existing skills for conventions
3. **Build a skill that bridges your ecosystem to theirs** — your skill makes their services discoverable from your framework, or vice versa
4. **Register in their skills registry** — update their skills.json or equivalent
5. **Prepare a PR** — if forking is blocked (403), publish a standalone repo and note it

**Real example — GenTech Kite Passport (Jul 27 2026):**
- Kite AI uses skills.sh + npx skills add for distribution (14 MIT-licensed skills)
- Built `gentech-kite-passport/SKILL.md` — Hermes agent skill bridging Kite's 100+ paid APIs with Q402 Trust Receipts
- GenTech services (CAD, Arcade, ClawWork) registered as Kite catalog entries
- Kite repo fork blocked (403) → standalone repo at github.com/ProtoJay4789/gentech-kite-passport
- PR ready when fork restriction lifts

**When to use:** Fork blocked; ecosystem has distribution model but doesn't accept external PRs; skill bridges two ecosystems (Hermes Kite) without modifying either core.

### 🛠️ Contribute — PR-based contribution
- Scan open issues (especially `good first issue`, `help wanted`, `security`)
- Look for gaps our existing work fills (Zod validation, compliance patterns, x402 experience)
- Check if forking is restricted (Dexter-DAO, Xona Labs block API forking → manual web UI)
- **Pitfall:** Some repos block API forking. Check `allow_forking` before attempting automated fork. If blocked, save code locally and note "manual fork needed" in handoff.
- **Multi-issue PRs:** When a repo has several related issues (e.g. Xona Labs #5 Zod validation, #2 tweetnacl fix, #3 fail closed), batch them into one PR on one branch. Saves review cycles.
- **PR-ready handoff:** Save code + instructions to `10-Labs/<project>-pr-ready.md` for manual submission.

### 🔗 Integrate — Cross-pollinate tools
- Does their tooling complement ours? (Solana tools → our EVM gateway, their SDK → our stack)
- Cross-pollination: our compliance patterns into their payment flow, their tools into our gateway
- Document the integration plan in `10-Labs/<project>-integration-plan.md`

### 🤝 Connect — Relationship play (no code contribution)
- Fellow solo builder in the same ecosystem (e.g. hyre-mcp, cryptoeights)
- No open issues to fix — the play is a conversation, not a PR
- **Pattern:** Star → clone → analyze → open an issue introducing yourself
  - "Fellow x402 builder. We run a production gateway. Here's what I'm thinking..."
  - Cover: our compliance → their payment flow, their tools → our gateway, our gateway → their ecosystem
- First star, first potential contributor — high signal-to-noise ratio
- Save integration plan to `10-Labs/<project>-integration-plan.md`

### 📦 Use — Adopt their patterns
- Can we adopt their patterns directly? (kepano vault structure, Remotion skills)
- Low effort, high signal — star the repo, clone, analyze
- **kepano pattern:** Add `_base.md` files to vault folders with YAML frontmatter + `[[links]]` to related folders
- **Remotion pattern:** Install agent skills via `npx skills add <org>/<repo> --yes`

#### "Eat the Meat" — Extract & Bank the Reusable Mechanism (Aug 3, 2026)

When Jordan says **"eat the meat"** (or "eat the meat, spit out the bones") on a link, he means: **don't just summarize the repo — clone it, extract the reusable mechanism, and BANK it into a skill reference so a future build uses it automatically.** This is a first-class workflow, not a one-off. It applies when:
- Jordan explicitly says "eat the meat" on a link
- A link contains a genuinely reusable pattern (deterministic animation, a state machine, a build technique, a clean abstraction) that maps to a skill we already have
- The technique is worth copying even if the product isn't worth forking

**The workflow:**
1. **Clone the source** locally (`git clone --depth 1 <repo> /tmp/<name>`)
2. **Find the mechanism** — the reusable pattern, not the product. Grep for the core helpers (`function damp`, `const smoothstep`, the state-machine modes, the key constants). For a single-file Three.js app: `grep -n "function \|const state\|=> {"`.
3. **Write it up as a condensed reference** — the building blocks, the 3-5 tunable constants, WHY it prevents the failure it prevents, and the exact GenTech targets that should reuse it.
4. **Bank it** via `skill_manage(action=write_file)` into the relevant umbrella skill's `references/` directory. The file name must be class-level (`threejs-deterministic-transition.md`), NOT session-specific.
5. **Add a one-line pointer** in that skill's SKILL.md so future agents know the reference exists.
6. **Clean up** the `/tmp` clone.
7. **Report** what was extracted and where it was banked.

**Verified (Aug 3, 2026):** MengTo complete-shelf → extracted the deterministic `hero→opening→detail→closing` state machine + normalized `transitionTime` + `damp()`/`smoothstep()` easing → banked to `arcade-cabinet/references/threejs-deterministic-transition.md` (with a pointer added to the arcade-cabinet SKILL.md). This is the pattern a future arcade build pulls automatically.

**Rule:** A link Jordan says "eat the meat" on that yields no skill-bankable mechanism is a missed extraction. If it's worth his attention, it's worth checking for a reusable pattern.

### 💰 Propose x402 Integration — Open-source monetization play
- Repo's product is useful but creator relies on donations; has clear API surface agents would pay for
- **Pattern:** Identify → Open issue → Offer to build → Reference existing x402 work
  1. **Identify** — Solo dev or small team, active (commits within days/weeks), clear API/CLI surface
  2. **Assess** — Would agents pay per-call or per-output? Is there a clear value exchange?
  3. **Open issue** — Title: "Proposal: x402 Payment Integration" with sections: Summary, The Gap, The Solution, Why This Fits, What I'm Offering, About Me + links to existing x402 work (AgentKit PR, other integrations)
  4. **Engage** — Reply to maintainer questions, offer to draft the PR
  5. **Track** — Add to build queue as pending, note the issue URL and date
- **Pitfall — Star count vs actual engagement:** A repo with 69k+ stars but only 315 commits and v0.1.2 may have inflated stats. Assess by commit frequency and code quality, not stars alone.
- **Pitfall — Language gap:** If primary language isn't English, keep issues concise. Maintainer likely reads English even if docs aren't.
- **Success metric:** Issue opened and maintainer replied is a win. Opens the conversation for later PR.
- **Real examples (Jul 23, 2026):** Obsidian Mind #142 (3.6k⭐), MiroFish #743 (69k⭐), img2threejs #17 (2.5k⭐), GOAT bitvm2-gc #49 (4⭐)

### 🏗️ Platform Integration — MCP server or API connection
- Platform opened an API/MCP for agents (e.g. Robinhood Agentic Trading, OKX AI)
- **Pattern:** Read docs → configure MCP in Hermes → document tools → add to build queue
- Save integration reference to `10-Labs/<project>-integration.md`
- Add setup task to build queue for Jordan
- **Pitfall:** Platform integrations often need a real account (KYC, funding) before they work. Document the setup steps clearly so Jordan can complete them.
- **Pitfall:** Some platforms (Robinhood) require US-based accounts. Note geographic restrictions in the integration reference.
- **Comparison analysis:** When a platform opens agentic access to a traditional service (e.g. Robinhood brokerage), compare it against the on-chain equivalent (e.g. Base DeFi). Document which strategies work better on which platform — they're complementary, not competing.

#### Robinhood Agentic Trading — Specific Pattern
- **MCP URL:** `https://agent.robinhood.com/mcp/trading`
- **Hermes config:** `hermes config set mcp_servers.robinhood '{"enabled": true, "url": "https://agent.robinhood.com/mcp/trading", "connect_timeout": 30, "timeout": 120}'`
- **30+ tools** across 6 categories: Account (portfolio, PnL), Watchlists (create/update/follow), Market Data (OHLCV, fundamentals, technical indicators, earnings), Equities (positions, quotes, orders, place/cancel), Options (chains, instruments, quotes, place/cancel), Scanners (create/run scans)
- **Requirements:** US-based Robinhood account, Agentic account opened via desktop browser, funded with dedicated budget
- **Safety:** review_equity_order / review_option_order before placement, push notifications on every trade, disconnect anytime
- **Comparison vs Base DeFi:** Robinhood = traditional assets (equities, options, SIPC insured, regulated, market hours). Base = on-chain (permissionless, 24/7, composable, self-custody, global). They're complementary — Agentic Treasury routes capital to whichever market offers best risk-adjusted return.

## Star → Analyze → Engage

1. **Star** the repo — first signal of engagement
2. **Clone + analyze** — understand architecture, find gaps
3. **Classify** — which of the five engagement types fits?
4. **Engage** — open issue, submit PR, adopt pattern, or configure integration

## When to Engage

- Repo is x402-native or agent-economy adjacent
- Solo dev or small team (high signal-to-noise ratio)
- Active within last 3 months
- No existing contributors from GenTech Labs
- Platform just launched agentic features (Robinhood, etc.)

## Corporate GitHub Scouting — Big-Tech Org Analysis

When scouting large tech corporations (Google, Microsoft, Sony, Nintendo, etc.) for open-source contribution opportunities:

### Methodology

1. **Check org basics**
   ```bash
   curl -s "https://api.github.com/orgs/<name>" | python3 -c "import json,sys;d=json.load(sys.stdin);print(f'Repos: {d.get(\"public_repos\")} · Followers: {d.get(\"followers\")}')"
   ```
   - Google: 2.9k repos, 76k followers
   - Microsoft: 8.2k repos, 126k followers  
   - Sony: 145 repos, 1k followers (mostly AI research)
   - Nintendo: 0 repos (confirmed dead — no open-source surface)

2. **Check alternate org handles** — Not all divisions live under the main org:
   - `google-gemini` for Gemma models (not under `google` org)
   - `sonyinteractive` for PlayStation (11 repos, 30 followers)
   - `devkitPro` for Nintendo homebrew (97 repos, 789 followers — community, not corporate)

3. **Map repos to your domain keywords**
   - For each org, search repos by star count and filter by relevant topics: `ai`, `agent`, `llm`, `mcp`, `payment`, `security`, `game`
   - Use `browser_navigate` to the org's repository page and browse manually since GitHub API search for org repos is limited
   - Watch for repos NOT in the primary org (e.g., Gemma models are in `google-gemini`, not `google`)

4. **Identify the contribution angle** — Not every star-heavy repo is a good target:
   - **Look for open issues** — `365 open` on `google/adk-python` means active community
   - **Check for existing auth/extension hooks** — ADK has `CustomAuthScheme`, `AuthProviderRegistry`, `AuthenticatedFunctionTool`
   - **Check license** — Apache 2.0 or MIT signals PR-friendly
   - **Check recent commit activity** — commits within hours/days = active maintenance

5. **Rank by impact for Gentech**

   | Tier | Company | Best Repo | Stars | Why | Contribution Angle |
   |------|---------|-----------|-------|-----|-------------------|
   | 🥇 | **Google** | `google/adk-python` | 21k | Agent framework, pluggable auth, MCP support | x402 CustomAuthScheme — first payment-enabled auth in a major agent framework |
   | 🥇 | **Google** | `google-gemini/gemma.cpp` | 7k | Open LLM, runs locally | DeFi agent fine-tuning on Gemma |
   | 🥈 | **Microsoft** | `microsoft/autogen` | 60k | Agent framework, largest agent repo | x402 payment tools for multi-agent systems |
   | 🥈 | **Microsoft** | `microsoft/semantic-kernel` | 28k | LLM integration SDK | x402 auth provider for paid API calls |
   | 🥈 | **Microsoft** | `microsoft/ai-agents-for-beginners` | 70k | Agent education | Contribute agent payment patterns as educational content |
   | 🥉 | **Sony** | `sony/mocopi-receiver-plugin-blender` | 14 | Motion capture → Blender | Arcade 3D lobby animation pipeline |
   | — | **Nintendo** | N/A | 0 | No corporate open source | Target devkitPro/homebrew community instead |

6. **Log findings** — Save scouting results to the build queue with:
   - Org name, repo count, follower count
   - Top 3 most relevant repos with star counts
   - Recommended contribution angle
   - Any alternate orgs found (e.g., google-gemini)

### Pitfalls

- **Giant orgs are slow to review PRs** — Microsoft has 8k+ repos, expect long review cycles. Small focused repos (`google/adk-python` specifically) are better targets.
- **Nintendo is a black hole** — 0 corporate repos across all variations (nintendo, nintendo-ca, nintendo-europe, nintendo-america, nintendo-japan). Homebrew community (devkitPro, smealum, fincs, mtheall) is the only adjacent surface.
- **Sony is mostly research papers** — 145 repos, mostly ML paper implementations with 5-40 stars. `mocopi-receiver-plugin-*` repos (Blender/Unreal/Maya) are the only developer-tooling exceptions.
- **Stats can be misleading** — An org with 125k followers may have 8k repos but most are unmaintained forks. Check recent commit dates, not just star counts.
- **Corporate capture** — Google's ADK was built by researchers, not PLG. PRs about payments/monetization may get pushback. Frame as "enabling agent autonomy" not "adding payments."
- **API rate limits on org listing** — GitHub API returns partial results for orgs with 8k+ repos. Use browser-based pagination for comprehensive scans.

## Mission Shift (Jul 21, 2026) — Strategic Listing, Not Random Contribution

**Jordan directive:** We are no longer contributing to random repos. The strategy is now **strategic ecosystem listing** — placing our services where agents and builders discover tools. The north star: *"Enabling anyone to get paid for what they build."*

**What changed:**
- Before: Submit PRs to any relevant awesome-list or directory
- After: Only submit to repos that directly reach our target audience (agent builders, x402 developers, DeFi operators)
- Before: Scan 50+ repos per run
- After: 4 repos per run, rotating through a tracking file
- Before: Multiple crons (PR Scout, Heretic Maintainer, x402 Compliance Scout, Ecosystem Lister)
- After: Single PR Maintainer cron, 4x daily, 4 repos per run

**Pitch for every listing:**
> "Enabling anyone to get paid for what they build — x402 micropayments, agent treasuries, DeFi yield automation."

**Tier 2/3 items** (needs Jordan decision or costs >$0.10) go to the build queue for overnight or Forge processing. The PR Maintainer only handles Tier 1 (inbox check, simple listing PRs).

## Rate Limit Management — 4-Repo Rotation Strategy

The PR Maintainer runs 4x daily (8:30am, 12:30pm, 4:30pm, 8:30pm ET) and checks exactly **4 repos per run** to stay within GitHub's 5,000 REST + 5,000 GraphQL points per hour.

### Rotation File

Maintain a tracking file at `/root/.pr-maintainer-rotation.txt`:

```
last_run: 2026-07-21 20:30
repos_checked: repo1, repo2, repo3, repo4
repos_pending: repo5, repo6, repo7, ...
```

### Priority Order for Repo Selection
1. Repos with open PRs that need attention (inbox)
2. Ecosystem directories we're not yet listed in
3. Repos with recent activity or comments
4. Random rotation for the rest

### Per-Run Budget
- 4 repos = ~8-12 API calls max. Well within 5,000/hr budget.
- If rate limited, report it and stop. Next run picks up where you left off.
- Use web search for ecosystem discovery (free, no API cost).

### Auto-Refresh
After all pending repos are checked, the rotation resets and starts over. This prevents stale repos from being ignored indefinitely.

## PR Portfolio Verification

When maintaining a PR portfolio (e.g. `/root/vaults/gentech/10-Labs/pr-portfolio.md`), entries can become aspirational — PRs that were *intended* to be created but never actually submitted due to rate limits, fork failures, or other issues. Always verify before reporting.

### PR Existence Verification

**Pattern:** Check each PR URL directly. A 404 means the PR was never created.

```bash
# Preferred: web_extract (no API rate limit)
# Check via web_extract — returns 404 page if PR doesn't exist
web_extract(urls=["https://github.com/owner/repo/pull/NUMBER"])

# Fallback: gh CLI (subject to rate limits)
gh pr view NUMBER --repo owner/repo --json number,state,title,url,author
# "GraphQL: API rate limit already exceeded" = rate limited, switch to web_extract
```

**Pitfall — gh CLI rate limits:** The `gh pr view` command uses GraphQL API which shares the 5,000-point/hour limit. When rate-limited, ALL `gh pr view` calls fail. Switch to `web_extract` (direct HTTP) which uses unauthenticated requests and has no practical rate limit.

**Pitfall — Aspirational PR entries:** PR portfolio entries with PR numbers (e.g. `#443`, `#733`) may be placeholders for PRs that were never created. The PR number was reserved optimistically but the `gh pr create` command failed (rate limits, fork issues). Always verify the PR actually exists on GitHub before treating it as real.

**Pitfall — Token death makes ALL PRs aspirational.** On Jul 22 2026, the GitHub token was revoked and the ProtoJay4789 account returned 404. The REST API continued returning cached PR data (from the token's last valid state), but every single PR returned 404 when verified via browser. The entire portfolio of 30+ PRs across 25+ repos was confirmed gone. **When the token is suspect, do NOT trust any API output — verify via browser or web_extract.** A PR that exists only in API output but not on the web is a phantom.

### Fork Existence Verification

Before a PR can exist, the fork must exist. Check the fork URL:

```bash
web_extract(urls=["https://github.com/YOUR_USERNAME/fork-repo-name"])
# 404 = fork doesn't exist or was deleted
```

**Pitfall — Fork deleted after failed PR attempt:** The ecosystem lister cron may have created a fork, attempted `gh pr create`, hit rate limits, and the fork was garbage-collected or deleted. The PR number in the portfolio is a ghost — the fork is gone, the PR was never created.

### "Already Listed" Claim Verification

When a portfolio entry says "Already listed" for a repo, do NOT trust it without verification. Check the actual upstream README:

```bash
# Fetch the raw README and search for your listing
web_extract(urls=["https://raw.githubusercontent.com/owner/repo/main/README.md"])
# Search for "GenTech", "gentechlabs", or your project name
```

**Pitfall — False "Already listed" claims:** A portfolio entry may claim a listing exists when it doesn't. The entry may have been written optimistically (assuming a PR was merged) or may reference a different project's listing. Always grep the actual README for your project name.

**Pitfall — Partial matches:** A repo may mention your project indirectly (e.g. an Avalanche registry address in a deployment table) without attributing it to your project by name. This is NOT a listing — it's a coincidental reference. A real listing has your project name, description, and link.

### PR Portfolio Audit Pattern

When asked to audit a PR portfolio:

1. **Read the portfolio file** — understand what's claimed
2. **Check each PR URL** — web_extract each one (batch in groups of 3-5)
3. **Check each fork URL** — verify the fork exists
4. **Verify "Already listed" claims** — check the actual upstream README
5. **Report findings** — table with PR#, repo, claimed content, actual status

**Example report format:**

| # | Repo | PR# | Claimed Content | Actual Status |
|---|------|-----|-----------------|---------------|
| 1 | owner/repo | #123 | Feature X | **404 — never created** |
| 2 | owner/repo2 | Already listed | Project Y | **NOT FOUND in README** |

### Rate Limit Workaround

When `gh` CLI is rate-limited (common with 5,000-point/hour GraphQL limit), use `web_extract` for PR and fork verification:

```python
# web_extract hits the GitHub web UI directly, bypassing API rate limits
# Returns 404 page for non-existent PRs/forks
# Returns the actual page content for existing PRs/forks
```

This is the preferred method for bulk PR portfolio sweeps. Save `gh` for operations that need write access (creating PRs, merging).

## References

- `references/solo-builder-outreach.md` — Solo builder outreach pattern: star → analyze → open issue introducing yourself. For 0-5 star repos where the play is a relationship, not a PR.
- `10-Labs/hyre-mcp-integration-plan.md` — Example integration plan
- `10-Labs/dexter-dao-pr-ready.md` — Example PR-ready handoff
- `10-Labs/xona-labs-pr-ready.md` — Example multi-issue PR handoff
- `references/pr-portfolio-verification.md` — Full session transcript: 10 PRs + 9 forks verified, "Already listed" claims audited, rate limit workaround pattern
- `references/ecosystem-research-workflow.md` — Structured research pipeline for unfamiliar ecosystem projects: repo scan → ecosystem context → integration analysis → document → update queue. Used for Injective iAgent and Circle Skills research.
