# Publishing Skills to EduHub & ClawHub Registries

DeepTutor and ClawHub both speak the **Agent-Skills format** — a `SKILL.md` with YAML frontmatter (`name`, `description`, `tags`, `version`). Skills published to either registry are installable by DeepTutor, Claude Code, Codex, and any agent that supports the format.

## Prerequisites

- A skill directory with `SKILL.md` and optional `reference/`, `templates/`, `scripts/` directories
- A **publish token** from the target registry (obtained via OAuth login)

## Authentication

### ClawHub (via `clawhub` CLI)

```bash
# Device flow — prints a URL to visit in browser
clawhub login --no-browser

# Or pass token directly (if generated via ClawHub website)
clawhub login --token <token>

# Verify auth
clawhub whoami
```

### EduHub (via `deeptutor skill login`)

```bash
# Browser OAuth (options: github, google)
deeptutor skill login github --hub eduhub --no-browser

# Prints an OAuth URL. Open it in browser to authorize.
```

**Pitfall:** GitHub OAuth may fail if your GitHub account is flagged / restricted from authorizing third-party apps. If this happens, try `deeptutor skill login google --hub eduhub --no-browser` instead. If that also fails (localhost callback issue), the skill can still be submitted via the **GitHub issue template** at `github.com/HKUDS/DeepTutor/issues/new?template=eduhub.yml`.

## Publishing

### To ClawHub

```bash
clawhub skill publish ./my-skill \
  --slug my-skill \
  --name "My Skill" \
  --owner <handle-or-org>
```

### To EduHub

```bash
deeptutor skill publish ./my-skill \
  --track skills-interests \
  --hub eduhub \
  --yes
```

Tracks available:
- `academics`: student-facing study, tutoring, writing, practice, assessment
- `companions`: motivation, planning, reflection, coaching, wellbeing
- `skills-interests`: coding, music, public speaking, hobbies, practical skills
- `educators`: teacher/admin tooling, lesson planning, rubrics, classroom design

## SKILL.md Format Requirements

```yaml
---
name: skill-name-in-kebab-case
description: "Clear description of what it teaches and when to use it."
tags:
- relevant-tag-1
- relevant-tag-2
version: 1.0.0
---
```

Rules:
- `name` becomes the slug — keep it short, use kebab-case, ≤ 64 chars
- `description` states what the skill does AND when it should trigger (for agent-selection)
- `version` is semver (1.0.0 for initial release)
- Only plain Markdown — no executable code in the SKILL.md body (agents read it as a playbook)
- No secrets in SKILL.md — it's a public manifest

## Verification

After publishing, verify the skill installs cleanly:

```bash
# From EduHub
deeptutor skill install eduhub:my-skill

# From ClawHub (if DeepTutor is installed)
deeptutor skill install clawhub:my-skill@1.0.0

# Or via standalone eduhub CLI
eduhub skill inspect my-skill
eduhub install my-skill --workdir /tmp/test-install --dir skills
test -f /tmp/test-install/skills/my-skill/SKILL.md
```

## Pitfalls

- **OAuth localhost callback** — The `deeptutor skill login` CLI opens a local callback server on `localhost:44745`. If you're running the command on a remote VPS, the browser on your local machine can't reach that port → the OAuth flow fails. Workaround: either run the login locally where the browser is, or use the **ClawHub device flow** (`clawhub login --no-browser`) which prints a verification URL instead.
- **Flagged GitHub account** — If your GitHub account can't authorize third-party apps, use Google OAuth or skip browser auth entirely and use a direct API token.
- **No --dry-run for `deeptutor skill publish`** — Unlike most CLIs, DeepTutor's `skill publish` doesn't have a dry-run flag. You commit directly. Validate your SKILL.md frontmatter manually before publishing.
- **EduHub is education-focused** — Skills should fit one of the four tracks. Infrastructure/skills like "x402-payments" can use `skills-interests` (coding sub-track).
- **Version collisions** — Once a version is published on EduHub, you can't overwrite it. Always increment version for changes. Use `deeptutor skill update` to roll back or release new versions.
- **Security gate** — EduHub runs automated security checks on published skills. New releases stay out of public install surfaces until verification completes.
