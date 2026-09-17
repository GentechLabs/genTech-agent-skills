# Kite AI Verification — Case Study

## What Happened
- Jul 25: Forge flagged Kite AI (#78) as disputed — "no source URL, no prize, $0K"
- Jul 27: Jordan shared a real Kite AI tweet + GitHub repo proved it's authentic
- Kite AI passport-skills repo: 14 MIT-licensed x402 skills, 0 stars at the time, but actively maintained

## Lesson: "Disputed" ≠ "Fake"

Just because a project has:
- 0 GitHub stars at discovery
- No obvious source URL in the queue entry
- An unusual or exaggerated-sounding claim

...doesn't mean it's fake. Kite AI was real, actively building, and directly relevant to our x402 work.

## Correct Protocol

When a queue item appears questionable:

1. **Don't mark as disputed** based on absence of evidence. Absence of evidence is not evidence of absence.
2. **Search harder** — check for tweets, press releases, product websites, NPM/PyPI packages.
3. **Check their GitHub** — 0 stars doesn't mean 0 activity. Check commit recency, issue activity.
4. **Check the actual product** — many agent tools launch quietly before getting stars.
5. **If still uncertain**, flag as UNVERIFIED (not DISPUTED) and note what's missing.

## Red Flags That Actually Matter
- No working product after 6+ months of announced launch dates
- GitHub repo that's only a README with no code
- Claims of "100K+ users" with no testimonials or case studies
- Team size of 1-2 with enterprise-grade claims
- Multiple name/identity changes (pivot without explanation)

A 0-star GitHub repo with actual code and recent commits is NOT a red flag — it's an early-stage project.
