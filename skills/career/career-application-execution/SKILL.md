---
name: career-application-execution
description: Draft, consolidate, track, and submit job/internship applications — especially multi-opportunity batches using vault-based coordination
trigger: After opportunity evaluation is complete, when ready to draft/submit applications; user says "let's apply", "submit applications", or "prepare application packets"
input: Evaluated opportunities with role details, resume variant mapping, user personal details (name, LinkedIn, portfolio)
output: Ready-to-submit application packets (cover letters + tracking) and submission checklist
---

# Career Application Execution — Drafting to Submission

## Overview
This skill governs the **execution phase** after opportunity research and evaluation. It covers turning evaluated opportunities into actual submissions: drafting tailored cover letters, consolidating multi-application packets, tracking, and final submission. It emphasizes **vault-based coordination** and **batch processing** to minimize context-switch.

## When to Use
- `career-platform-research` has produced go/no-go recommendations
- Multiple opportunities need to be applied to in a single batch
- User has confirmed which roles to pursue and is ready to draft/submit
- Need to maintain version control across cover letters and track submission dates

## Pre-Flight: Intent Clarification

**CRITICAL CHECK BEFORE PROCEEDING:** When a user shares a link to a company's careers page, product page, or announcement, you MUST clarify their intent before diving into analysis. Common intents:

| User Says / Links | Likely Intent | Your Response |
|---|---|---|
| "Check these guys out" / company careers URL | 🔍 **Job-fit evaluation** — they want to know if they qualify | Lead with role fit assessment, not partnership or competitive analysis |
| "Saw this, interesting project" / product or doc link | 🤝 **Partnership or integration** — they want tech fit analysis | Lead with technical overlap, integration possibilities |
| "What do you think of X?" / product launch or blog | 📊 **Competitive or market intelligence** | Lead with positioning, threat/opportunity assessment |

**Pitfall:** Defaulting to partnership/competitive analysis when the user wanted job-fit evaluation wastes time and requires a correction. When in doubt about intent, ask a short clarifying question before producing a full analysis.

**If intent is job evaluation:** Skip directly to Role Fit Assessment (below) — do not write partnership recommendations, competitive positioning, or market analysis. The user needs ONE thing: "Do I fit this role?"

## METHODOLOGY — Five-Phase Workflow

### Link Format Rule (User Preference)
When sharing job application links on Telegram, send bare URLs on their own line — NOT wrapped in markdown tables or [text](url) format. Telegram makes bare URLs tappable. Example:

```
Binance Pioneer Talent — AI Agent Developer

https://himalayas.app/companies/binance/jobs/pioneer-talent-program-ai-agent-developer

Deadline: June 22, 2026
```

This applies to ALL job/apply links shared in conversation.

### Phase 1: Inventory & Gap Analysis
1. **Check existing application drafts** in vault (`04-Entertainment/Applications/` or similar)
   - Look for: `{Company}-{Role}-CoverLetter.md` standalone files
   - Look for: consolidated docs like `College.xyz-{Name}-{Roles}.md`
2. **Identify gaps** — which roles lack cover letters?
3. **Catalog resume variants** available (`02-Labs/Resumes/`):
   - Growth-focused resume
   - Analyst-focused resume
   - Master/General resume
   - Verify file existence and PDF generation

### Phase 2a: Standalone Draft Creation (for missing roles)
For each missing role, create a standalone cover letter file following `career-platform-research` template structure:
- Use company/role-specific emphasis from the evaluation doc
- Include: subject line, why-I'm-interested, why-I-fit, contributions, links, sign-off
- Keep length: 200–300 words (concise but substantive)
- Save as: `{Company}-{Role}-CoverLetter.md`

**Do not** edit consolidated master yet — keep versioned.

### Phase 2b: Single-Role Direct Email Application (Crypto/AI Startup Pattern)

For crypto-native startups that accept applications via email (no portal), use this alternate flow:

1. **Extract resume content** — The resume is only available as PDF. Use `pdftotext` to extract content for reference:
   ```
   pdftotext "/path/to/Resume.pdf" -
   ```

2. **Draft cover letter** with these specific structural choices that match this user's style:
   - **Subject line**: `{Role} — {Name} — {Hook Phrase}` (e.g., "Research Engineer Intern — Jordan Jones — Agentic Systems + DeFi Infrastructure Builder")
   - **Opening**: Direct, warm, no "I am writing to express my interest" boilerplate
   - **Body structure**:
     - 3-4 shipped artifacts as bullets (never just "I worked on X" — always "I shipped X, it does Y, Z people use it")
     - Reference the company's specific research focus, product, or recent announcement (proves you read their stuff)
     - Frame the intern angle positively: "I can prove shipping velocity without a credential"
   - **Honest constraints section**: If the user has a day job or time-bound commitment (Amazon Thu-Fri), disclose it directly. Crypto-native startups value honesty over resume-gloss. Better to say "I work Thu-Fri, the rest is full-time on this" than to imply unlimited availability.
   - **Closing**: Offer to hop on a call, reference something specific about their work (their Chief Scientist's constrained autonomy research, their D0 product, etc.)

3. **Save cover letter** to `10-Labs/Resumes/{Company}-{Role}-CoverLetter.md`

4. **Application tracking entry** — Add to build queue as a new item with:
   - Status: "Draft ready — Forge to send"
   - Steps checklist: Read cover letter → Attach resume PDF → Send to {email} → Optional: DM founder on X
   - Founder X handle and company handle for optional DM outreach
   - Track reply: [ ]

5. **Optional X DM** — After sending, DM the founder/CTO with a 1-2 sentence intro:
   - Mention you just applied
   - One-sentence hook on what you build that's relevant to them
   - Ask for a conversation

### Phase 3: Consolidation
Patch the master application document (e.g., `College.xyz-Jordan-Hibachi-Injective.md`) to integrate new role:
1. Add role to **Target Roles** header
2. Insert **Role Overview** section (mission, needs, requirements, comp)
3. Add to **Distinguishing Factors** under Application Strategy
4. Insert **Cover Letter Template** section with full letter
5. Update **Tracking** checklist with new role entry
6. Update **Social Media Templates** to include new company/handle
7. Expand **Decision Framework** table if multi-offer scenario possible
8. Update **Notes / Customization** with role-specific tips

**Commit message style:** "Add {Role} to college.xyz application batch — cover letter, strategy, tracking."

### Phase 4: Cross-Check & Delegation
- **Resume mapping:** Confirm each role gets correct resume variant (Growth→Growth_Resume, Analyst→Analyst_Resume, Product→Master or tailored)
- **DMOB handoff:** Send message to GenTech HQ or DMOB group:
  - "Verify resume PDFs exist for [list roles]"
  - "Prepare simple tracking sheet (date, resume used, status)"
- **Personal details fill-in:** Create checklist of brackets to replace: [Name], [Email], [LinkedIn], [Portfolio], [Quantifiable achievements]

### Phase 5: Submission Execution
- User submits all applications in **single batch** (same sitting)
- Use direct links or college.xyz portal
- Screenshot confirmations or log submission URLs for tracking
- Optional: post social media templates (Twitter/LinkedIn) to signal interest
- Mark tracking checklist as submitted with dates

## OUTPUT TEMPLATE

```markdown
# Application Packet — [Date] — [User]

## Applications Submitted
| Company | Role | Resume Used | Date | Portal Link |
|---------|------|-------------|------|-------------|
| Hibachi | Growth Intern | Jordan_Growth_Resume.pdf | 2026-05-05 | [link] |
| Injective | PM Intern | Jordan_Master_Resume.pdf | 2026-05-05 | [link] |
| No Limit Holdings | Investment Analyst Intern | Jordan_Analyst_Resume.pdf | 2026-05-05 | [link] |

## Follow-Up Schedule
- [ ] Day 3–5: DM hiring managers (handles listed)
- [ ] Week 2: Follow-up email if no response
- [ ] Update tracking sheet with status changes

## Social Posts
- [ ] Twitter posted (URL)
- [ ] LinkedIn posted (URL)

## Next Steps
- [ ] Prepare for potential interviews (see `interview-prep` skill)
- [ ] Update portfolio with recent projects if needed
```

## AI-Native & Web3 Roles

When applying to AI-native or Web3 companies for "Demo Engineer", "Builder", "Developer Advocate", or "Ecosystem" roles, the application strategy shifts significantly. These companies value **shipping speed over production quality** and **AI tool fluency over years of experience**. See `references/ai-native-web3-roles.md` for detailed patterns, signals to look for in job descriptions, and application strategy adjustments.

**Key adjustment:** Lead with your hackathon repos, live demos, and agent projects as your primary credentials. Frame AI orchestration (multi-agent fleets, autonomous workflows) as your differentiator. **Be honest on wins vs. submissions — Jordan has hackathon experience and shipped builds, but NO wins yet.** Present velocity through completed builds, working code, and live deployments, not claimed victories. Don't over-index on Solidity depth — demo roles care about showing what's possible.

### AI Job Search Framework (28.1K ⭐)

The [ai-job-search](https://github.com/MadsLorentzen/ai-job-search) repo (28.1K ⭐, MIT) is an AI-powered job application framework built on Claude Code. The creator used it to land an AI engineer role after 69 applications, 20 interviews, 1 signed contract. It automates the full pipeline:

| Command | What It Does |
|---------|-------------|
| `/setup` | Fill in profile once |
| `/scrape` | Search job portals, get fit ratings |
| `/apply <url>` | Evaluate fit, draft tailored CV + cover letter in LaTeX, reviewer agent critiques and revises |
| `/interview` | Prep mode |

**Integration with this skill:** Fork the repo, fill in Jordan's profile, and use it to automate the Phase 2-5 workflow. The `/apply` command replaces manual cover letter drafting. The reviewer agent catches what Flash misses — good use of K2.7.

**GenTech Academy angle:** Package as a module — "AI-Powered Job Search" case study showing real results.

**Queued at:** build queue #20 [HIGH] — fork + set up Jordan's profile.

**Target companies (remote):** Zapier, Supabase, Temporal, Render, Linear, Cresta, Fieldguide, Chainguard, Vanta, RevenueCat. Micro1 called Jordan a top prospect — AI test after GOAT meeting.

## Crypto Research / Agent Roles — Cover Letter Strategy

When the role is a **research engineer, founding researcher, or agentic systems role** at a crypto/AI startup, the cover letter strategy shifts further:

| Do This | Not This |
|---|---|
| Lead with 3-4 **shipped production systems** with real users | Lead with education credentials or theory |
| Frame intern/early career as "shipping velocity without credentials" | Apologize for lack of formal experience |
| Reference their **specific research focus** (paper, product feature, founder tweet) | Generic "I'm passionate about crypto" |
| Disclose honest **time constraints upfront** | Pretend unlimited availability |
| Mention hackathon track record as proof of velocity | List coursework |
| Close with a **specific technical connection** to their work | Generic "hope to hear from you" |

**Key insight for crypto research intern roles:** These companies hire for **ownership mindset**, not credentials. The cover letter should read like a co-founder pitch, not a job application.

**Cover letter structure template:**
```
Subject: {Role} — {Name} — {Hook Phrase}

Hi {Founder/Team},

I'm {Name} — {one-line identity}.

I saw you're hiring for {Role} focused on {specific area}. Here's what I've shipped:

- **{Project 1}** — {One-line: what it does + proof of life}
- **{Project 2}** — {Same pattern}
- **{Project 3}** — {Same pattern}

Why this role: {2-3 sentences tying their specific focus to your experience}

Time honesty: {Current constraints and flexibility}

Best,
{Name}
{Contact links}
```

## Chain Foundation Grant Applications

When applying to blockchain ecosystem grants (Solana Foundation, Chainlink BUILD, Arbitrum Foundation, etc.), the strategy differs from job applications. Grants fund **projects**, not people. Lead with the artifact, not the resume.

### Grant Application Structure

| Section | Content | Length |
|---------|---------|--------|
| **Project Name** | Clear, descriptive (e.g., "Agent Registry — Open Infrastructure for AI Agents on Solana") | 1 line |
| **One-Liner** | What it does + why it matters | 1 sentence |
| **Problem** | What problem does this solve for the ecosystem? | 1 paragraph |
| **Solution** | How does your project solve it? | 1 paragraph |
| **Why [Chain]** | Why is this chain the right home? (speed, cost, ecosystem, community) | 3-5 bullets |
| **Artifacts** | Proof of work — repos, tests, deployments, hackathon wins | Table |
| **Milestones** | Concrete deliverables with timelines | Table |
| **Funding Request** | Amount + use of funds | 1 paragraph |
| **Team** | Who you are + track record | 1-2 sentences |

### Grant-Specific Tips

1. **Lead with the artifact, not the resume** — "128 tests passing, deployed on Solana" beats "self-taught developer"
2. **Frame as ecosystem value** — "Brings AI agents to Solana" not "I need money for my project"
3. **Attach hackathon wins** — They prove you ship, not just plan
4. **Non-dilutive preferred** — Grants > equity deals for early-stage
5. **Rolling applications** — Apply anytime, don't wait for "the right moment"
6. **Reuse narrative** — One core story, customized per chain's focus areas

### Grant Target Checklist

Before applying, verify:
- [ ] Project fits the chain's focus areas
- [ ] We have working code (not just a concept)
- [ ] Artifacts are public (GitHub, testnet deployments)
- [ ] Milestones are concrete and time-bound
- [ ] Funding request is reasonable for the scope

**See:** `references/grant-application-patterns.md` for chain-specific templates and examples.

## Grant Applications

For Web3/AI ecosystem grants (Solana Foundation, Chainlink BUILD, Arbitrum, etc.), see `references/grant-applications.md` for grant categories, application template, and strategy. Grant applications differ from job applications — you're pitching a project, not yourself.

## PITFALLS & EDGE CASES

1. **Pitfall**: Defaulting to partnership/competitive analysis when user wants job-fit evaluation.
   - **Root cause:** The agent sees a company link and produces technical/ecosystem analysis instead of role-fit assessment.
   - **Fix:** When user shares a company URL, run the intent clarification check first (see Pre-Flight section). If intent is unclear, ask a short question: "Are you looking at these guys for a job, partnership, or just intel?" before writing a full analysis.
   - **Correction history (Jul 8, 2026):** Agent analyzed Donut AI as a partnership opportunity. User corrected: "the reason why I sent this was because I was curious to see if we fit any of the roles."

1. **Pitfall**: Submitting before resume verification — PDF missing or wrong variant.
   - **Fix**: DMOB sign-off required before submission morning. Check `02-Labs/Resumes/` for file existence.
   - **Verification**: `ls 02-Labs/Resumes/` → confirm all three PDFs present.

2. **Pitfall**: Inconsistent personal details across letters (different name spelling, missing LinkedIn).
   - **Fix**: Create a single `personal-details.md` snippet and paste into each letter before finalizing.
   - **Verification**: Read all three letters side-by-side; spot-check brackets.

3. **Pitfall**: Forgetting to update consolidated doc after creating standalone letter.
   - **Fix**: Always perform Phase 3 immediately after Phase 2. The standalone file is draft; the consolidated doc is source of truth.
   - **Verification**: grep for company name in consolidated doc; ensure present.

4. **Pitfall**: Not noting application portal quirks (some require separate account creation).
   - **Fix**: When evaluating, note "Application portal: Greenhouse / Lever / external". Allocate extra time for account setup.
   - **Verification**: Click each APPLY button before batch session to confirm flow.

5. **Pitfall**: Missing social media handles in follow-up step.
   - **Fix**: During consolidation, research and note Twitter/LinkedIn handles of hiring managers in the document.
   - **Verification**: Check each company's career page or Twitter bio for team members.

6. **Pitfall**: Applying to roles requiring multilingual skills without checking first.
   - **Fix**: Before applying, verify language requirements in job description. Skip roles requiring multilingual if not qualified.
   - **Verification**: Search job description for "language", "multilingual", "bilingual", "English + [language]".

8. **Pitfall**: Verifying job links by HTTP status only — pages return 200 but jobs are expired/filled/redirected.
   - **Root cause:** curl/browser tools can't bypass bot detection on job boards. HTTP 200 means the page loads, NOT that the job is live. Greenhouse, Lever, and Workday pages always return 200 even when showing "position filled" or redirecting to a different listing. This has failed TWICE (Jun 18 and Jun 19, 2026) — 4 out of 5 listings were dead or mismatched despite returning HTTP 200.
   - **Fix:** ALWAYS extract full page content (`web_extract` or `browser_snapshot full=true`) and READ the actual page before sharing. Check for:
     - Job title matches the listing (not redirected to a different role)
     - Requirements section (look for hidden: bachelor's degree, 3+ years, seniority labels)
     - Application status ("position filled", "no longer accepting", "closed")
     - Relocation fine print (check for "must be in X city", "relocation required")
     - Apply button exists and is clickable
   - **Verification checklist (run for EVERY link before sharing):**
     1. ✅ Page content extracted and read (not just HTTP 200)
     2. ✅ Job title matches search result
     3. ✅ No degree requirement beyond "preferred"
     4. ✅ No experience requirement beyond 0-3 years
     5. ✅ English-only (no bilingual requirement)
     6. ✅ Truly remote (no hidden relocation)
     7. ✅ Apply button present
   - **Standard:** When sharing job links, add a status badge: ✅ VERIFIED (all 7 checks pass) or ⚠️ CHECK (couldn't fully verify). NEVER present unverified links as confirmed. If you can't extract the page content, say so — don't guess.
   - **User correction (Jun 19, 2026):** "almost same problem as last time... The Lightblocks link is no longer available... the OpenZeppelin one is expired... the EigenLayer description said they wanted a senior. Even I got mad at that one because why not put senior agentic AI engineer."

9. **Pitfall**: Resume header includes location when user prefers email-only.
   - **Fix**: Use email in header, not location. Remove LinkedIn if not ready.
   - **Verification**: Check header format: Email, GitHub, Portfolio, Telegram (no location, no LinkedIn).

8. **Pitfall**: Education section empty or outdated.
   - **Fix**: Add current learning (e.g., "Cyfrin Updraft — In Progress") with focus areas.
   - **Verification**: Education section shows active learning, not just degrees.

## Resume Formatting Preferences

**CV = Resume (Jordan uses these interchangeably).**

**Header format (Jordan's preference):**
```
# Jordan Jones — Resume (Master)

**Email:** jordanjones0902@gmail.com
**GitHub:** https://github.com/ProtoJay4789
**Portfolio:** https://protojay4789.github.io
**Telegram:** @ProtoJay4789
```

**Education format:**
```
## EDUCATION

**Cyfrin Updraft** — In Progress
- Solidity fundamentals, security patterns, smart contract development
- Learning approach: AI agent codes, humans audit
```

**PDF generation workflow:**
1. Write resume as markdown (`Jordan_Master_Resume.md`)
2. Convert to PDF using WeasyPrint (not pandoc)
3. Use tables for skills section
4. Keep to 2 pages max

**Primary Goal format:**
```
**Primary Objective:** Transition from Amazon Flex to full-time remote crypto role.

**Strategy:**
1. Learn Solidity via Cyfrin Updraft → create projects that solve real problems
2. Hackathon wins → establish public credibility + prize income
3. Agent Kit v2 → distribute modular agent framework
4. DeFi Model → deploy API endpoint
5. Protocol contributions → open-source recognition
```

**Note:** No relocation timeline — Jordan stays in Cincinnati for family. Goal is remote job, not relocation.

## Grant Applications (Non-Dilutive Funding)

Grant applications differ from job applications — they're **project-focused**, not person-focused. The evaluation criteria is "does this project advance the ecosystem?" not "is this person qualified?"

### Grant Application Workflow

**Phase 1: Research**
1. Search for active grant programs (web_search: "[chain] grants 2026 apply")
2. Extract: amount, focus areas, application URL, deadline, review timeline
3. Check eligibility: crypto-native (they WANT crypto) vs blockchain-agnostic (frame as AI/utility)
4. Save research to `03-Strategies/Grant-Applications-Queue.md`

**Phase 2: Framing**
- **Crypto-native grants** (Solana Foundation, Chainlink BUILD, Arbitrum): Lead with the project, mention chain explicitly
- **Blockchain-agnostic grants** (EF, OWASP, OpenAI): Lead with the PROBLEM we solve, NOT the blockchain. "AI agent security tooling" not "Solana smart contract"
- **Key insight:** "ETH price ≠ Ethereum ecosystem value" — L2s (Base, Arbitrum) have separate ecosystems and grant programs

**Phase 3: Drafting**
Create standalone draft at `02-Labs/{Program}-Grant-Application-DRAFT.md`:
- **Project Name** — one-liner
- **Problem Statement** — what problem does this solve?
- **Solution** — how does it work?
- **Why [Chain/Ecosystem]** — alignment with their goals
- **Artifacts** — proof of work (repos, tests, deployments)
- **Milestones** — deliverables + timeline
- **Funding Request** — amount + use of funds
- **Team** — track record

**Phase 4: Queue Management**
- Update `03-Strategies/Grant-Applications-Queue.md` with new entry
- Update `00-HQ/hackathon-tracker.md` Grant Applications section
- Track status: Draft → Submitted → Under Review → Accepted/Rejected

### Grant-Specific Patterns
- **Reuse narrative across applications** — multi-agent systems, AI agent economy, Solana-native
- **Attach existing artifacts** — hackathon submissions prove shipping velocity
- **Cross-reference hackathon wins** for credibility
- **Non-dilutive preferred** — all grants should be non-dilutive (no equity)
- **Landing rate target:** 3-5 of 7+ applications

### Grant Queue Template
```markdown
| # | Grant Program | Amount | Focus | Status | Notes |
|---|---------------|--------|-------|--------|-------|
| 1 | Program Name | $X-Y | Focus area | 🟢 DRAFT READY | Apply: URL |
```
## RELATED SKILLS

- `career-platform-research` — research → evaluation → recommendation phase
- `gentech.vault-compliance-audit` — track deadlines and follow-ups in vault
- `agent-coordination` — handoff patterns to DMOB and GenTech HQ

## Support Files

- `references/grant-application-template.md` — Template for grant applications (crypto-native + blockchain-agnostic). Includes narrative patterns, artifact tables, milestone format, and active grant targets.
- `references/application-batch-2026-05-04.md` — Previous application batch details
- `references/ai-native-web3-roles.md` — Patterns for AI-native/Web3 demo roles
- `references/crypto-startup-email-application-example.md` — Full worked example: Donut AI direct email application (cover letter structure, tracking pattern, DM outreach)
- `hackathon` — hackathon submissions as grant credentials

## MAINTENANCE
College.xyz UI changes may affect APPLY button behavior or external form flows. Revalidate quarterly.
Grant program URLs and focus areas change quarterly — revalidate each quarter.

---
**Status:** Available