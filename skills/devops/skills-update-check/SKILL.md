---
name: skills-update-check
description: "Weekly skills + integration update checker. Scans hub skills for updates, checks Hermes version status, applies updates, and reports what changed. Designed for cron jobs that keep agents current."
version: 1.0.0
author: Gentech Labs
tags: [skills, updates, integrations, hermes, maintenance, cron]
trigger: "When checking for skill updates, verifying Hermes version, or running weekly maintenance. Also used when installing new skills to verify they're current."
---

# Skills Update Check

Keeps an agent's skills and integrations current. Scans for updates, applies them, and reports status.

## When to Use

- Weekly maintenance cron job (Sunday recommended)
- After installing new skills from GitHub or registries
- When Hermes feels "stale" or tools aren't working as expected
- Before hackathon submissions (ensure latest features)

## What It Checks

1. **Hub Skills** — Official + community skills from skills.sh registry
2. **Hermes Version** — Commits behind upstream, update availability
3. **Local Skills** — Count of global + profile skills installed
4. **Curator Health** — Runs, stale/active skills, last run time
5. **Applies Updates** — Auto-updates outdated hub skills
6. **UPSTREAM REPOS WE FORKED FROM** — see below. This is the layer `hermes skills check`
   cannot see, and it is the one that silently freezes.

## The Forked-Skill Blind Spot (Jordan, 2026-09-30)

> *"A lot of our skills came from forking or copying another GitHub. When I say we should check
> for skill updates, we should also include the original repos that are getting updated, so our
> clones can also catch the updates — similar to how we were 6,000 commits behind Hermes."*

**`hermes skills check` covers hub-INSTALLED skills. It does not cover a skill you hand-copied
out of someone's repo.** That copy froze on the day you copied it, and nothing watches it. The
skill's own pitfall list already said "not locally created ones" — forked ones are the
missing half.

### The mechanism

- **Registry:** `10-Labs/skills-distribution/.provenance/skills-provenance.json`
  (also mirrored to `devops/third-party-skill-import/references/`)
  Machine-readable: repo, upstream path, import date, local path, per skill.
- **Checker:** `scripts/upstream-skills-check.py` — cron `a9e29980346b`, Sunday 10:30 UTC.
  For each registered skill it asks GitHub for commits touching that path **since the import
  date**, and reports what moved. Silent when every upstream is quiet.

### Three things it gets right, each learned the hard way

1. **"Could not check" is NEVER reported as "up to date."** The first live run hit a
   `Bad credentials` token and correctly printed *"9 upstream(s) could NOT be checked (this is
   NOT 'up to date')"*. A watcher that launders an auth failure into a clean bill of health is
   worse than no watcher.
2. **A present-but-dead token is worse than no token.** `/root/.hermes/.env` carries a
   `GITHUB_TOKEN` that GitHub rejects. A single-source reader takes it, every call fails, and
   the naive report says everything is fine. The checker **collects candidates, PROBES each,
   and uses the first that actually authenticates** (`gh auth token` is the live one here).
3. **An empty result is verified, not assumed.** The 8 Hermes Field Kit skills return zero
   commits because their upstream genuinely has not moved since import — confirmed by querying
   the path directly (one commit, dated 3 days BEFORE our import). Check the filesystem, not
   just the field. But the ONLY field a skill record cannot be trusted to supply is its own
   provenance: `source:` in frontmatter is used inconsistently for template placeholders
   (`github.com/owner/repo`), doc references, and social attributions. `grep '^source:'` is not
   a provenance registry.

### Adding an import to the registry

Whenever you import a skill from an external repo, **add it to the registry in the same
change.** An import that isn't registered is a skill that freezes silently — the exact failure
the registry exists to prevent. Record: skill, local path, `owner/repo`, upstream path,
import date.

## CLI Reference — Skills Commands

Commands used during weekly scan, verified on Hermes v0.18.0 (Jul 2026):

### Hub Update Check
```bash
hermes skills check
# Output table: Name | Source | Status
# Status: up_to_date, update_available, unavailable
# "unavailable" = bundle-installed but upstream no longer provides separately
```
Only checks hub-installed/official skills, NOT locally-created ones.

### Browse Available Skills
```bash
hermes skills browse
# Paginated: 86,703 skills, page 1/4336. 101 official from Nous Research.
# Table: # | Name | Description | Source | Trust | Identifier
```
**Pitfall:** Does NOT accept `--limit`. Use `hermes skills search <query>` for targeted results.

### Search Across Registries
```bash
hermes skills search <query>
hermes skills search --source official <query>   # Nous Research only
hermes skills search --source skills-sh <query>  # community
hermes skills search --source github <query>     # GitHub-sourced
hermes skills search --source clawhub <query>    # ClawHub
# Full source list: all, official, skills-sh, well-known, github,
# clawhub, lobehub, browse-sh, nvidia, openai, anthropic,
# huggingface, voltage, gstack, minimax
```

### List Installed
```bash
hermes skills list               # Table format
hermes skills list-modified      # User-modified bundled skills
hermes skills diff               # Diff local vs upstream for a skill
```

**Pitfall:** `hermes skills list --json` does NOT exist on v0.18.0 (Jul 2026). The command returns an error. For scripting, use `hermes skills list` and parse the table output, or access the internal skills data directly via the profile directory.

### Curator Health
```bash
hermes curator status
# Shows: enabled/disabled, run count, last run, active/stale/archived
# counts, top 5 most/least active skills with activity scores
```

### Hermes Version
```bash
hermes --version
# Format: Hermes Agent vX.Y.Z (YYYY.M.D) · upstream <commit>
# Also shows Python, OpenAI SDK version, commits behind
```

## Cron Job Setup

```python
# Schedule: Every Sunday at 10 AM UTC
cronjob(
    action="create",
    name="Skills + Integration Update (Sunday)",
    schedule="0 10 * * 0",
    prompt="Run the skills update check script and report results.",
    deliver="telegram:<chat_id>"
)
```

## Report Format

The script outputs a clean Telegram-formatted report:
- ⚠️ Hermes version status (commits behind)
- ✅/📦 Hub skills status (updates available)
- 📂 Local skills count
- Applied updates list

## Key Insight for Agent Kit Users

Skills from GitHub and registries update frequently. Agents that don't check back fall behind on:
- Bug fixes in existing skills
- New features and capabilities
- Security patches
- Compatibility with latest Hermes version

**Always check back.** A weekly Sunday check keeps everything current without being noisy.

**Agent Kit integration (Jordan's directive, Jun 2026):** This skill should be included in the Agent Kit distribution so new installs automatically get weekly skill maintenance. Add to `cron/defaults.json` in the distribution as a starter job.

## Pitfalls

- `hermes skills check` only checks hub-installed skills (official + skills.sh), not locally created ones
- `hermes update` requires restart to take effect — flag but don't auto-restart
- Some skills may have breaking changes — review before updating in production
- Local skills (created by the agent) are never overwritten by updates
