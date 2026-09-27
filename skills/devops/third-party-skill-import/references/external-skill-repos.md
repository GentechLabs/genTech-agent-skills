# External Skill Repos — Curated Sources

Known repos with Hermes-compatible skills. Updated July 2026.

## Hermes Field Kit (tonysimons — asimons81)

- **Repo:** `github.com/asimons81/hermes-field-kit`
- **Count:** 13 operational skills for Hermes Agent
- **Format:** `skills/<name>/SKILL.md` — drop-in compatible
- **License:** Apache 2.0
- **Author:** Tony Simons (same author as "The Operator's Guide to Hermes Agent")
- **High-value picks:** `hermes-gateway-doctor`, `hermes-stack-doctor`, `hermes-skill-audit`, `hermes-profile-audit`, `interview-me`, `x-post-writer`, `repo-readiness-audit`, `hermes-update-doctor`
- **Import date:** Jul 26, 2026 — 8 skills installed under `gentech-ops/`
- **Install:** Clone to /tmp, copy skill dirs to `~/.hermes/profiles/<profile>/skills/<category>/`

## Mercury Skills (cosmicstack-labs)
- **Repo:** `github.com/cosmicstack-labs/mercury-agent-skills`
- **Count:** 147+ skills across 23 categories
- **Format:** `categories/<category>/<skill-name>/SKILL.md` — drop-in compatible
- **License:** MIT

## Google Agent Skills
- **Repo:** `github.com/google/skills`
- **Count:** 30 skills for Google Cloud products
- **Format:** `skills/cloud/<skill-name>/SKILL.md`

## OpenClaw Master Skills
- **Repo:** `github.com/LeoYeAI/openclaw-master-skills`
- **Count:** 1600+ skills
- **Format:** Requires adaptation (uses `{baseDir}`, `uv run` patterns)
- **See:** `references/openclaw-evaluation-notes.md` for adaptation notes

## Installation Pattern (Mercury/Google/Field Kit)

```python
import shutil, os

skills_dir = os.path.expanduser("~/.hermes/profiles/<profile>/skills")
src = "/tmp/<cloned-repo>/skills"

for name in skills_to_install:
    src_path = os.path.join(src, name)
    dest_path = os.path.join(skills_dir, f"mercury-{name}")
    if os.path.exists(os.path.join(src_path, "SKILL.md")):
        shutil.copytree(src_path, dest_path)
```

**Prefix convention:** `mercury-` for Mercury, `google-` for Google. Field Kit skills use original names (class-level, no prefix needed).
