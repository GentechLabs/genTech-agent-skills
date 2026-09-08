# Critic Restoration Verification

Session: evolve-9 (2026-07-28)

## Problem

The Harness Critic cron job failed repeatedly with `ollama HTTP 402` because its prompt was 6,580 bytes of detailed workflow instructions already present in a skill file. The bloated prompt consumed ~960K input tokens per run and exhausted the free ollama-cloud tier.

## Fix

1. Move the detailed workflow into a skill file (e.g. `harness-critic` or `self-evolution-harness`).
2. Trim the cron prompt to essential instructions plus a reference to the skill.
3. Remove the old job and recreate it with the lean prompt.

## Verification Commands

Hermes cron CLI has quirks worth knowing:

- `hermes cron list --json` currently returns empty/invalid JSON; do not rely on it.
- `hermes cron show '<Job Name>'` returns exit code 2 with no output; do not rely on it.
- The reliable way to inspect a job is plain `hermes cron list` combined with `grep` and context:

```bash
cd /root/.hermes/profiles/gentech
hermes cron list | grep -B 1 -A 12 'Harness Critic'
```

Look for:
- Active job ID (e.g. `8f71e23cbfd6 [active]`)
- Correct schedule (`2 */4 * * *`)
- Next run timestamp in the near future
- Correct workdir (`/root/.hermes/profiles/gentech/harness`)

## Self-Confirming Prediction Pattern

When the fix is "restore the Critic," the falsifiable prediction can be confirmed by the Critic's own next run:

- Prediction: "The Critic runs successfully on the next scheduled tick and produces a critique entry."
- Confirmation: the next Critic cycle executes, reads the recommendation, verifies it, and appends a new `Critique Entry` to `facts/critique-log.md`.

This is a special case where the QA loop's restoration is proved by the QA loop itself operating. Log the confirmation explicitly in the critique entry so the trace is obvious.

## Checklist

- [ ] Old failing job removed (`hermes cron remove <old-id>`)
- [ ] New job created with trimmed prompt (`hermes cron create ...`)
- [ ] New job shows `[active]` and a plausible next run time
- [ ] Next Critic cycle executes and appends to `critique-log.md`
- [ ] No constitutional violations (prompt still references documented skill workflow)
