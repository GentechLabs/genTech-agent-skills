# Bankr Skill Listing — Stuck in Fork, Never Merged Upstream (Aug 24, 2026)

## The situation
Jordan asked "what happened with our Bankr listing update?" The answer: the 7-service
`gentech-x402-services` skill (incl. Treasury Defender) was committed to OUR fork
`ProtoJay4789/bankr-skills` on branch `add-gentech-x402-skill`, but it was **never merged
into the platform's main repo** (`BankrBot/skills`). So the "listing" never went live on Bankr.

## How to verify merge state (git, no API quota)
A flagged/rate-limited GitHub account (ProtoJay4789) blocks `gh pr list` (GraphQL rate-limit
error). Fall back to pure-git checks that need no API quota:

```bash
cd <fork-repo>            # e.g. /root/bankr-skills
git fetch upstream main
# 1. Is our skill commit an ancestor of upstream main? (MERGED vs NOT-MERGED)
git merge-base --is-ancestor <skill-commit> upstream/main && echo MERGED || echo NOT-MERGED
# 2. Does the skill file exist in upstream main? (PRESENT vs ABSENT)
git cat-file -e upstream/main:skills/<name>/SKILL.md && echo PRESENT || echo ABSENT
```

Observed (Aug 24): `155c842` → NOT-MERGED; `skills/gentech-x402-services/SKILL.md` → ABSENT
from `upstream/main`. The branch exists only on our fork (`origin/add-gentech-x402-skill`).

## What to do
If NOT merged, the PR is either never-submitted, closed, or orphaned (fork deleted). Re-submit
the PR from the fork branch to `BankrBot/skills`. Same class of pitfall as the Pay-Skills
PR #190 that never merged (see umbrella Pitfalls section).

## Related
- Umbrella: `agent-marketplace-integration` → "Integration Reference: Bankr" section
- The skill file itself: `/root/repos/genTech-agent-kit/skills/bankr/SKILL.md` (committed,
  pushed to `Gentech-Labs/genTech-agent-kit` org remote — that copy IS live; the Bankr
  *platform* listing is the one stuck in the fork).
