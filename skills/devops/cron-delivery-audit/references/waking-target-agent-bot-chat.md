# Waking a Target Agent via bot-chat Delivery

**Problem:** Writing a vault handoff file does NOT wake the receiving agent. A
handoff can sit OPEN for days if the target agent never runs a session that
reads its inbox.

**Proven Aug 24, 2026:** a build handoff to Gizmo (Labs) sat OPEN 2 days
(Aug 22→24) because only the vault file was written. Triggering via
`deliver="bot-chat:gizmo"` got it picked up immediately.

## The Pattern

Actively trigger the target agent with a one-shot cron job delivered to its
bot-chat:

```bash
cronjob action=create deliver="bot-chat:<profile>" schedule=<now or soon> \
  prompt="<agent>, pick up the OPEN handoff at <path> — <task summary>"
cronjob action=run job_id=<id>   # fire immediately, don't wait for schedule
```

- `deliver="bot-chat:<profile>"` injects the prompt into that profile's Bot
  Chat as a real message — the target agent reads it, acts, and responds.
- Use the **profile name** (`gizmo`, `gentech-treasury`), not the display name
  (Gizmo, The Steward).
- Fire it with `action=run` right away rather than waiting for the schedule.

## Heads-up to a Third Agent

Same pattern works for a **heads-up to a third agent** (e.g. notify Treasury of
a build's tooling/access) so it can align without being asked:

```bash
cronjob action=create deliver="bot-chat:gentech-treasury" schedule=<now> \
  prompt="The Steward, heads-up from Gentech (HQ): <what we're building + what access we have>"
cronjob action=run job_id=<id>
```

## Key Detail

The vault handoff is the *durable record*; the bot-chat delivery is the *wake-up
call*. Both are needed — the file for searchable memory, the delivery to get
the work moving. Don't rely on the watcher cron alone to surface work to a
target agent that isn't running a session.
