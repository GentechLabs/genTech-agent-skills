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

## ⚠️ `VAULT_DIR` must be defined on every seat

Many skills in this core reference `${VAULT_DIR}` so they stay portable across
machines with different vault locations. **That only works if the variable actually
exists** — and for a long time it did not: 110 files here referenced it while no seat
defined it, so every such command expanded to a bare `/09-Green*` and **failed silently**
(exit 2, no output), which looks identical to "nothing found". A portability pass had
replaced working absolute paths with the variable and never added the definition.

**Set it in the profile's `.env`** (`~/.hermes/profiles/<profile>/.env`):

```bash
VAULT_DIR=/root/vaults/gentech      # on the VPS; Forge: whatever the desktop vault path is
```

`.env` is the right home because Hermes loads it for the agent's shell environment, so
the variable is present when a skill's commands run. Adding a line takes effect **without
a gateway restart**.

**Verify it resolves before trusting any skill that uses it:**

```bash
echo "${VAULT_DIR:-UNSET}"          # must print a path, never UNSET
ls -d ${VAULT_DIR}/09-Green*        # must list dirs; empty output means the var is unset
```

An unset variable fails **silently**, so a quick "it ran fine" is not evidence. Test the
expansion.

**Assert a NON-ZERO count on a string you know is present — not just that the variable is
set.** `[ -n "${VAR}" ]` proves the variable exists; it does not prove the scan *ran*. The
failure we were fixing was a scan reporting clean because it never looked, so the check has to
distinguish "found nothing" from "looked nowhere":

```bash
n=$(grep -rl 'VAULT_DIR' ${VAULT_DIR}/10-Labs/skills-distribution 2>/dev/null | wc -l)
[ "$n" -gt 0 ] || { echo "SCAN DID NOT RUN (0 matches on a known-present string)"; exit 1; }
echo "scan ran: $n files"
```

A count of 0 from a tree you *believe* contains the string is the signal, the same way a
wrong corpus filename silently parses 0 blocks instead of 117. **A zero is only trustworthy
when you have proved the search had somewhere to look.**

## Every path variable a skill references must be DEFINED

The `VAULT_DIR` case below is not unique — it is one member of a class. Four path
variables appear in this core and all four were undefined in the agent's shell:

| Variable | Files | Refs | Value |
|---|---|---|---|
| `${PROFILE_DIR}` | 128 | 317 | `/root/.hermes/profiles/<seat>` — **per seat** |
| `${VAULT_DIR}` | 113 | 261 | `/root/vaults/gentech` |
| `${PROFILES_DIR}` | 32 | 164 | `/root/.hermes/profiles` |
| `${INSTALL_DIR}` | 36 | 129 | `/usr/local/lib/hermes-agent` |

**All four now set in each profile `.env`** (the profile one — the *global*
`~/.hermes/.env` is **not** forwarded into the agent's shell; that was verified, and
putting them there does nothing). `PROFILE_DIR` is seat-specific; the other three are
identical everywhere.

**A variable that expands to empty is not a missing value — it is a relocated root.**
`${VAR}/x` silently becomes `/x`, so the command returns nothing and reports success-shaped
output. The check is therefore `[ -n "${VAR}" ]` per variable, not a content diff.

Verify after setting, and allow a few seconds — the tool-shell snapshot is regenerated on a
cadence, so a variable can take a moment to appear:

```bash
for v in PROFILE_DIR VAULT_DIR PROFILES_DIR INSTALL_DIR; do
  eval "val=\$$v"; printf "%-14s [%s]\n" "$v" "${val:-UNSET}"
done
```

## ⚠️ `VAULT_DIR` must be defined on every seat

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
