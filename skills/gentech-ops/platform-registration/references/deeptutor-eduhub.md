# DeepTutor EduHub — Skill Publishing

DeepTutor (30K+ ★, Apache-2.0, Jul 2026) ships an education-focused skill registry called **EduHub** at `eduhub.deeptutor.info`. It also supports **ClawHub** as a first-class source.

## Agent-Skills Format

Uses the open Agent-Skills format — a folder with `SKILL.md` (YAML frontmatter + Markdown body) and optional reference files. Same format as ClawHub/OpenClaw.

**Required frontmatter:** `name`, `description`. Optional: `version`, `tags`.

## Tracks (EduHub Classification)

When publishing to EduHub, choose one track:
- `academics` — study, tutoring, writing, practice, assessment
- `companions` — motivation, planning, reflection, coaching, wellbeing
- `skills-interests` — coding, music, hobbies, practical skills ← fits our x402 skill
- `educators` — teacher/admin tooling, lesson planning, classroom design

## Publishing Workflow

1. **Login** (browser OAuth — GitHub or Google):
   ```bash
   deeptutor skill login --hub eduhub
   # Or with --no-browser to print a login link
   deeptutor skill login --hub eduhub --no-browser
   ```

   **Known pitfall — GitHub account flagged:** If your GitHub account is flagged/restricted from authorizing third-party apps (common for accounts with prior flags), GitHub OAuth will fail. Fix: use Google OAuth instead:
   ```bash
   deeptutor skill login google --hub eduhub --no-browser
   ```
   This produces a Google OAuth URL. Open in a browser, authorize, and the CLI picks up the token.

2. **Publish**:
   ```bash
   deeptutor skill publish ./my-skill-dir \
     --track skills-interests \
     --version 1.0.0 \
     --yes
   ```

3. **Update**: `deeptutor skill update` (interactive — lists your skills, rollback or release new)

## Installation

```bash
deeptutor skill search "x402 payments"
deeptutor skill install x402-payments                    # EduHub default
deeptutor skill install clawhub:x402-payments@1.0.0     # ClawHub
deeptutor skill install eduhub:x402-payments@1.0.0      # Explicit EduHub
```

## Safety Gate

Every install checks registry security verdict (flagged packages refused), zip-slip/zip-bomb protection, text/script suffix whitelist, `always:` frontmatter stripping, and provenance write to `.hub-lock.json`.

## Key Difference from Other Platforms

| Feature | EduHub | ClawHub | Glama |
|---------|--------|---------|-------|
| Content type | Teaching/education skills | General agent skills | MCP servers |
| Format | SKILL.md + refs | SKILL.md + refs | glama.json |
| Registration | GitHub OAuth + CLI | GitHub OAuth + CLI | Dashboard |
| Submission | `deeptutor skill publish` | `npx skills publish` | GitHub release |
| Versioning | Semver with rollback | Yes | Per release |

## x402 Payments Skill Reference

A complete EduHub-ready skill package lives at `/root/x402-payments-eduhub/`. Includes SKILL.md with payment flow, supported networks (Algorand, Robinhood, Base), GenTech kit integration, session management, and verification steps.
