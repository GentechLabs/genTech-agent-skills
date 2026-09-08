# Collaborator Skill Permission Testing — Session 2026-07-06

## Summary

User requested collaborator skill access system: Vanito should be able to use Gentech skills across all groups, with permissions enforced.

## What Was Built

**Collaborator identification skill enhanced:**
- Added `can_use_skill()` function to detect.py
- Added `get_skill_permission_matrix()` function
- Updated mapping.json with skill permission matrix
- Created testing guide and summary documents

## Skill Permission Matrix

| Skill | Jordan | Vanito |
|-------|--------|--------|
| entertainment | ✅ | ✅ |
| metaglasses | ✅ | ✅ |
| gaming | ✅ | ✅ |
| social-content | ✅ | ✅ |
| deploy | ✅ | ❌ |
| finance | ✅ | ❌ |
| defi | ✅ | ❌ |
| defi-operations | ✅ | ❌ |
| x402-payments | ✅ | ❌ |
| cron-truth-layer | ✅ | ❌ |

## How It Works

**Before any skill execution:**
1. Detect collaborator (Jordan vs Vanito)
2. Load collaborator profile
3. Check skill permission matrix
4. Allow or block skill execution

**Example (Vanito tries to deploy):**
```
[VANITO]: "Deploy x402 to production"

[GENTECH]:
1. Detect: Vanito (pattern: "deploy")
2. Load profile: Vanito
3. Check permission: deploy skill → ❌ Blocked
4. Response: "You don't have permission for this operation. Only Jordan can deploy to production."
```

## Testing Plan

Created: `00-HQ/collaborator-identification-testing-guide.md`

**6 test cases:**
1. Vanito uses entertainment skill → ✅ Allowed
2. Vanito tries to deploy → ❌ Blocked
3. Vanito in Labs group → ✅ Context preserved
4. Jordan in any group → ✅ Full access
5. Vanito uses gaming skill → ✅ Allowed
6. Vanito tries to access finance → ❌ Blocked

**All tests apply to all groups (HQ, Strategies, Labs, Entertainment).**

## Key Files

**Skill (Hermes profile):**
- `~/.hermes/profiles/gentech/skills/gentech-ops/collaborator-identification/SKILL.md`
- `~/.hermes/profiles/gentech/skills/gentech-ops/collaborator-identification/detect.py`

**Vault (Git):**
- `00-HQ/collaborators/jordan.md`
- `00-HQ/collaborators/vanito.md`
- `00-HQ/collaborators/mapping.json`
- `00-HQ/collaborator-identification-testing-guide.md`
- `00-HQ/collaborator-identification-summary.md`

## User Feedback

User: "make sure it applies in all groups and we'll test it when Vanito ask something"

Response: Updated SKILL.md to explicitly state "Works across all groups" and created testing guide.

## Next Steps

- Wait for Vanito to test in any group
- Verify permissions work as expected
- Adjust if needed

---

*Session: July 6-7, 2026*
*Status: Built, awaiting test*