# Circle Get-Listed + the fork-vs-upstream pitfall (Aug 2026)

Session-specific detail captured 2026-08-22. Two durable lessons for any GitHub-hosted
skills marketplace / curated x402 catalog.

## 1. Circle Agent Marketplace — the LISTING gate (not just the seller SDK)

The `agent-marketplace-integration` SKILL.md's Circle section covers becoming a seller.
This file records what it takes to actually GET LISTED, which is a separate manual gate.

**Live market (verified Aug 2026):** 83 services / 1,018 endpoints. Categories: Creative,
Data Enrichment, Financial Analysis, Infrastructure, Prediction Markets, Social
Intelligence, Web Search Research. Sellers flagged 1P (Circle direct) vs 3P (third-party).

**Get-listed requirements (from `developers.circle.com/agent-stack/agent-marketplace/get-listed.md`):**
1. Service must be payable: returns `402 Payment Required` when unpaid, serves the resource
   when paid.
2. **OpenAPI spec** published so agents can read inputs/outputs.
3. **Payout wallet address** submitted via the Google intake form
   (`https://forms.gle/7YFzvdmMcn1JH5tF6`).
4. **MANUAL REVIEW** — the team screens and **sanctions-checks** the payout wallet.
   Self-serve automated submission is "coming" but not live (as of Aug 2026).
5. Once approved: continuously health-checked, stays listed only while reachable.

**Agent-readiness score:** the sell page (`agents.circle.com/sell`) lets you check your
API's "agent-readiness score" in seconds and copy a fix-it prompt. Agents find you through
the Discovery API (filter by category/network/price) and the Circle CLI (`circle services search`),
so a well-described OpenAPI file is your storefront copy.

**Technical note:** the `@circle-fin/x402-batching` SDK is the Express path
(`createGatewayMiddleware({ sellerAddress })` → `gateway.require("$0.01")`). But you can also
accept **vanilla x402** alongside Gateway by running an `x402ResourceServer` with an x402
facilitator client — the 402 `accepts` array then offers BOTH rails and buyers pick whichever
they have funded. Accepting more chains = more reachable buyers.

**Our status:** bankr already returns 402 (x402 v2, 7 chains) — the core requirement is done.
Outstanding: OpenAPI spec + clean EVM payout wallet + intake form. Build queue #65.

## 2. THE PITFALL: a skill published to YOUR fork is NOT discoverable where agents look

When a platform's skills marketplace resolves `install <name> skill from <github-url>`, the
URL in your skill's own `catalog.json`/`SKILL.md` points at the **canonical repo** — but your
commit may only exist on **your fork** (`origin`), not on `upstream`.

**Concrete failure (Aug 2026):** our `gentech-x402` skill was committed + pushed to
`ProtoJay4789/bankr-skills` (our fork). Its `catalog.json` told agents to install from
`github.com/BankrBot/skills/tree/main/gentech-x402` — the **canonical** repo. A check showed
`git ls-tree upstream/main gentech-x402/` returned nothing: our skill was **NOT** in the real
Bankr repo, so agents pulling from the official repo couldn't find us.

**Diagnosis (always check remote-to-upstream, not just your fork):**
```bash
# 1. Where does the catalog tell agents to install from?
grep -i install <skill>/catalog.json
# 2. Is the skill actually on upstream/main? (canonical repo)
git ls-tree -r --name-only upstream/main | grep -i <skillname>   # empty = NOT published
git branch -r --contains <commit>   # does our commit appear on upstream?
# 3. Divergence check
git diff --stat upstream/main origin/main
```

**Fix — open a CLEAN upstream PR containing ONLY the new skill folder, off upstream/main:**
```bash
git fetch upstream main
git checkout -b add-<skill> upstream/main   # branch OFF upstream, not off your fork's main
git checkout main -- <skill>/               # pull ONLY the skill folder in
git commit -m "feat: add <skill> — <desc>"
git push origin add-<skill>
gh pr create --repo <Org>/<repo> --base main --head <you>:<branch>
```
Branching off `upstream/main` (not your fork's `main`) keeps the PR diff to just your new
folder — you avoid dragging in your fork's 18k-line divergence. Then VERIFY the folder
exists on upstream after merge (`git ls-x402 upstream/main <slug>/`), same as the pay-skills
"PR can be lost" pitfall.

**Rate-limit gotcha:** if `gh pr create` fails with `API rate limit already exceeded for
user <id>`, the account is over its GitHub API budget (ProtoJay'l78 is persistently
rate-limited/flagged). The branch is already pushed to the fork — hand Jordan the one-click
compare URL (`https://github.com/<Org>/<repo>/compare/main...<you>:<branch>`) so a human with
a healthy token opens the PR. Don't keep retrying the rate-limited account.
