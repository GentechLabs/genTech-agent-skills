---
name: memory
description: Persistent memory management — save, load, rotate
category: core
priority: critical
---
# Memory Management
Handle persistent memory across sessions. Save durable facts, load context.

## Memory Dietician — Automatic Size Enforcement

Memory files grow over time and degrade agent performance. The Memory Dietician is a no-agent cron job that runs nightly and enforces size limits on the four context files:

| File | Limit | Behavior |
|------|-------|----------|
| MEMORY.md | 2,100 chars | Reports when over limit |
| USER.md | 1,300 chars | Reports when over limit |
| witness-log.md | 1,500 chars | Auto-trims resolved entries > 7 days old |
| context-weight.md | 1,200 chars | Reports when over limit |

**Installation:** Script at `scripts/memory-dietician.py`, cron job named "Memory Dietician — Nightly Trim" running at 5:00 UTC daily. Silent when healthy, reports only when trimming or over limit.

**Key lesson (Jul 28, 2026):** Someone built an elaborate memory stack around Hermes, then deleted it and restored defaults — the agent worked dramatically better. More memory = worse performance. Keep MEMORY.md and USER.md lean. The Memory Dietician enforces this automatically.

**Manual pruning guidelines:**
- MEMORY.md: Condense Vanito/HIKARI entries. Remove redundant model routing info. Keep Seedance limitations (face bypass hierarchy, no lip-sync).
- USER.md: Keep financial context (rent $795, burn $1,700/mo), collaborator preferences (Vanito's detail-obsessed workflow).
- witness-log.md: Only unresolved or recently resolved entries. Trim anything older than 7 days with a resolved status.
- context-weight.md: Focus on active priorities. Stale project entries (unstarted hackathons, pending items without action) are noise.
