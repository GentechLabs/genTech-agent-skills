# DAO / Security-Fund Questionnaire — Additional Question Shapes (Aug 2026)

Companion to `dao-fund-questionnaire.md`. Captures the question types that surfaced in the TheDAO Security Fund application session (Aug 25, 2026) beyond the core shapes already documented. Same honest-first-operator posture applies throughout.

## Co-sponsorship questions

**"Are you interested in raising funding from co-sponsors? (Yes/Maybe/No)"**
→ **Maybe** is the honest default for a first-time operator. Don't claim sponsors you don't have lined up — overclaiming hurts a security fund more than a "maybe." Signal real interest + a credible target list (protocols whose security the round directly serves), but don't commit to unsecured sponsorships. If the user wants higher odds, "Yes" is the strategic choice — flag the tradeoff explicitly.

**"What would co-sponsors receive in return?"**
Value prop for sponsors:
- Security coverage where it matters to them (the round hardens the ecosystem they operate in)
- Co-branded visibility on a public, auditable round (logo, recognition in payout/accounting trail)
- Direct line to funded security researchers (talent + intel pipeline)
- Mission-aligned goodwill (security is reputation-positive)
Support them with: simple tier structure, regular progress reports, public ledger, no-surprises accounting.

**"What are your current leads for co-sponsors?"**
Be honest: **warm ecosystem touchpoints, not signed sponsors.** Name the real relationships (e.g. Solana Foundation/pay-skills PR, Algorand Foundation outreach, Superteam grant) + a targeting thesis (protocols/wallets/agent-payment companies whose users get exploited in the round's focus area). State plainly: zero confirmed dollars. NEVER fabricate a sponsor list.

## Prototype / demo questions

**"Provide a link to a prototype or demo"**
They want a **visual, try-it-out demo of the round itself**, not a tech stack. Build a vibe-coded interactive page and host it on the live site (`gentechlabs.net/<name>.html`). Include: matching pool, governance mix, live payout ledger, an interactive QF-match slider (breadth vs depth), and sample funded projects in the round's focus area. Verify it resolves with a live HTTP check before pasting. A working prototype is the strongest possible answer.

**"Is your interface mobile-friendly?"**
Confirm + verify. Use a responsive layout: viewport meta tag, `repeat(auto-fit, minmax(300px,1fr))` grid (stacks to one column at phone width), flexbox. Verify no horizontal overflow. NOTE: browser `resizeTo`/CDP `Emulation.setDeviceMetricsOverride` may NOT take effect in the harness (viewport stays at desktop width) — confirm mobile-friendliness from the responsive CSS itself (auto-fit grid guarantees stacking at phone width), not from an emulated viewport.

## Closing questions

**"Do you commit to publishing a public retrospective/learnings report?"**
→ **Yes, committed** — treat it as a core deliverable, not an afterthought. Cover: what got funded and why, what worked/didn't, honest failures, full public payout ledger. A security fund's credibility rests on transparency; an honest retrospective (including mistakes) builds trust and improves the next round.

**"Is there anything else we should know?"**
Close by tying the whole application together: first-time honesty, real strengths (ops/auditability), the AI-assisted standard, the live prototype link, and the transparency commitment. End on "under-promise and over-deliver" — the consistent through-line.

## Session-specific facts (TheDAO Security Fund, Aug 2026)
- Program: TheDAO Security Fund on Gitcoin — revived the 2016 DAO's 75,000+ ETH (~$220M) to fund Ethereum security via quadratic funding, retroactive grants, ranked-choice RFPs. ~$8M/yr staking yield. $220M+ matching pool.
- Jordan's chosen focus: **AI-agent / autonomous-payment security** (agents hold keys, sign txs with no human per-step) — wallet-authorization UX, phishing, prompt-injected txs, spending caps.
- Decision-quality standard chosen: **A (AI-assisted decision-making)** — the honest, achievable pick for a first-time operator.
- Allocation: **D (Hybrid)** — open voters (QF) + curated voters (ETHSecurity Badge holders) + AI (anti-sybil/auditability).
- Pool size: min $25K / ideal $75–100K / max $250K.
- Prototype built: `gentechlabs.net/thedao-round-prototype.html` (interactive QF slider, ledger, governance mix, sample projects).
- Co-sponsor leads: warm (Solana Foundation/pay-skills, Algorand Foundation, Superteam) — zero signed.
