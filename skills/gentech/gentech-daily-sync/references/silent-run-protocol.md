# Silent-Run Protocol — Delivery Mode Decision Tree

## When This Applies

Every daily sync runs as a cron job. The output mode depends on how the cron job is configured, not on a hardcoded rule.

## Decision Tree

```
Is this a cron/scheduled job?
├── YES → Read the cron job's instruction text
│   ├── "Your final response will be delivered to the user" → DELIVER OUTPUT
│   │   Produce a concise actionable summary as your final response.
│   │   Do NOT use [SILENT]. The system handles delivery.
│   │
│   └── No delivery mention / "vault-only" / "background" → SILENT
│       Write to vault files only (daily summary, working memory).
│       Respond with exactly "[SILENT]" and nothing else.
│
└── NO → Interactive session → DELIVER OUTPUT
    Full markdown summary as final response.
```

## Why This Exists

The original skill assumed all cron jobs should be silent. In practice, Jordan configured some cron jobs to deliver summaries directly. The skill must respect the job's actual configuration.

## What "Deliver Output" Means

- Produce a concise, actionable summary (not the full vault-format daily digest)
- Lead with the most critical item (e.g., "LP is OUT OF RANGE")
- Use Jordan-facing language (direct, action-oriented)
- Include specific next steps with owners
- Keep to ~500 words max — Jordan skims, doesn't read essays

## What "[SILENT]" Means

- Update vault files (daily summary, working memory)
- Commit to git
- Do NOT produce any output content
- The system suppresses delivery entirely

## Anti-Patterns

- ❌ Using [SILENT] when the cron job says to deliver
- ❌ Delivering verbose vault-format content when Jordan needs a quick summary
- ❌ Asking "should I deliver?" — just check the job instruction
- ❌ Combining [SILENT] with content — it's one or the other
