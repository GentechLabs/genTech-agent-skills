# SPC Founder Fellowship — Verified Application Details (Aug 1, 2026)

South Park Commons Founder Fellowship — $1M backing for frontier-tech founders.
Fall 2026 cycle. **Deadline: Aug 2, 11:59pm PT** (verified Aug 1, 2026).

## Terms (verified from southparkcommons.com/news/f26-founder-fellowship/)

- $400K upfront for 7% (standard SAFE) + $600K guaranteed in next external round
- Up to $1M in credits (Anthropic, OpenAI, Baseten, Microsoft, GCP, AWS, Render, Figma…)
- 8-week in-person bootcamp (SF / NYC / Bangalore), then ongoing residency
- Interviews announced by Aug 30; program runs late Sep – late Nov
- Solo founders accepted (strong bias for applicants who can build/prototype)

## Live Form (Airtable embed at southparkcommons.com/apply)

`https://airtable.com/embed/appxDXHfPCZvb75qk/pag8h6Xe52XNke3ai/form`

**Verified fields — the form is SHORTER than any drafted version:**

1. Which best describes where you are in your journey today? (dropdown, required)
2. Full Name (required)
3. Email (required)
4. Phone number (required)
5. LinkedIn profile (required)
6. Where will you be based? (dropdown, required)
7. How did you hear about the application? (listbox: SPC Community Member / SPC Staff /
   Friend / X-Social / SPC Blog / SPC Event / Other)
8. Please briefly elaborate on the above (optional)
9. What personal/professional product, project, or achievement are you most proud of?
   Link + brief, <1000 chars (required)
10. Share 2-3 artifacts that illustrate your ability to do high-quality work (required)
11. Stay in touch checkbox (checked by default)
12. Anything else to add? (optional)

## Lesson: verify the LIVE form before finalizing

Our Jul 30 draft included sections that DON'T exist on the live form (Founding team?
Funding in last 6 months? Problem space elevator pitch? Why you?). Those are excellent
"Anything else to add?" candidates, not form fields. When the user shares an apply URL:

1. `web_extract` the apply page — but Airtable embeds often return only the embed shell,
   so `browser_navigate` the actual `airtable.com/embed/...` URL and read the snapshot.
2. Map draft answers to the REAL field list; archive non-existent questions.
3. List the actual blanks the user must supply (phone, LinkedIn, location, how-heard).
4. Flag the deadline in the user's local time with a buffer — "tomorrow" from the user
   may mean the submission must happen TODAY.

## Jordan's strong draft answers (kept at vault: 09-Green Room/spc-fellowship-draft.md)

- **Proudest achievement:** AgentEscrow + x402 Payment Gateway (HTTP 402 protocol layer,
  contracts on Avalanche/Base, CLARITY Act compliance, self-evolution harness; 16+ paid
  endpoints live at api.gentechlabs.net) — real infrastructure managing real capital.
- **2-3 artifacts:** Multi-Agent Voice System (4 agents, ElevenLabs TTS); DeFi LP
  Rebalancing Engine (Avalanche LFJ, live DexScreener data); Agent Credit Score
  (0-850 for AI agents, 22/22 tests, MIT).
- **Links (VERIFIED working Aug 1 — do not use personal-account URLs, they 404):**
  api.gentechlabs.net · gentechlabs.net · github.com/Gentech-Labs/agent-credit-score ·
  github.com/Gentech-Labs/genTech-agent-kit

## Pitfall: personal-account GitHub links 404 on web (flagged account)

Before the submission we drafted links under `ProtoJay4789/...` (genTech-agent-kit,
programmable-money-x402, ProtoJay4789.github.io portfolio) — **all 404 on the web**
even though the GitHub API reports them public. The working public copies live under
the **Gentech-Labs org** (21+ repos). Rule: before putting ANY link in an application,
verify it returns 200 with `curl -s -o /dev/null -w "%{http_code}" <url>` — a broken
link in a fellowship/hackathon submission is worse than no link. Same rule in
`agent-economy` §12 and `references/arc-hackathon-submission-packaging.md`.
