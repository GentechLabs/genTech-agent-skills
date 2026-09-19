# Skills Distribution — shared skills for all agents

This folder is the **canonical source** for custom (non-hub) skills that agents
need. Any agent (Forge on desktop, gizmo/pixel/treasury on VPS) can pull a
skill from here into its own profile.

## Layout
```
10-Labs/skills-distribution/
    <category>/<skill-name>/
        SKILL.md
        references/...
        scripts/...
```

## How to install a skill from here
Copy the skill folder into your profile's skills dir:

```bash
# Forge (desktop) — replace <profile> with your profile name
cp -r /path/to/vault/10-Labs/skills-distribution/<category>/<skill-name> \
      ~/.hermes/profiles/<profile>/skills/<category>/
```

On the VPS, the vault is at `${VAULT_DIR}/`. On Jordan's desktop,
clone the vault (GentechLabs/gentech-vault) or pull the folder via Obsidian
sync.

## Current skills
- `development/develop-and-verify` — the consolidated develop-and-verify
  pipeline (DeepSeek V4 Flash DEV → Kimi K2.7 CODE AUDIT on Ollama
  Cloud). Two-phase build pattern with pre-publish audit checklist.
  **z.ai/GLM is retired — do not route the audit phase to it.**

## Convention
- When a new custom skill is created/updated on the VPS, copy it here so all
  agents stay current.
- Keep the folder structure matching the profile skills layout
  (`<category>/<skill-name>/`).
- This is the durable distribution path — prefer it over one-off handoffs.

## Fleet-wide propagation (the "one change, all follow" tool)
`00-System/agent-profiles/fleet_skills_sync.py` copies every skill in this
folder into ALL VPS profiles (gentech, gizmo, pixel, gentech-treasury),
preserving the category subdir. Run it after any skill change here:

```bash
python3 ${VAULT_DIR}/00-System/agent-profiles/fleet_skills_sync.py --check  # dry-run
python3 ${VAULT_DIR}/00-System/agent-profiles/fleet_skills_sync.py          # apply
```

**Provider-agnostic rule (Jordan, Sep 8):** skills are tied to MODELS, not
providers. Both Hermes and Ollama Cloud carry the same models, so a skill works
on either. Do NOT hard-pin a skill to a single provider (OpenCode Go was a
single-provider dependency that became a blocker when its monthly limit hit).
Name the model (e.g. `kimi-k2.7-code`, the current audit model — **not** the retired
GLM family), let the provider be whichever of the two we're on.
