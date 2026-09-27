# 📦 Portable skill paths — the `${VAR}` convention

**Why:** a skill is our *method* — the part worth handing to a collaborator. When it hardcodes
this box's filesystem, it stops being method and becomes a transcript of one machine.
Two goals depend on this fix, and they share it: the **agent kit** and **Vanito's copy**.

## The variables

| Variable | On this box | Meaning |
|---|---|---|
| `${VAULT_DIR}` | `${VAULT_DIR}` | the brain — docs, handoffs, config |
| `${PROFILES_DIR}` | `${PROFILES_DIR}` | all Hermes profiles |
| `${PROFILE_DIR}` | `${PROFILES_DIR}/<you>` | your own profile |
| `${SCRIPTS_DIR}` | `${PROFILE_DIR}/scripts` | your scripts |
| `${INSTALL_DIR}` | `${INSTALL_DIR}` | the Hermes install |

## The rules

1. **Never write a literal `/root/...` in a skill body.** Use `${VAULT_DIR}/...`.
2. **If a real path is genuinely needed as an example, label it** — *"on this box: `${VAULT_DIR}`"*
   — so the reader knows it's a value, not a requirement.
3. **Credentials never appear in a skill.** Skills carry *method*; the box keeps the *keys*.
   A `.env` reference is fine; a key is not.
4. **`$p` / `<profile>` loop variables are fine** — but they must be *defined* in the snippet.

## Why not literal paths

A literal path fails silently and specifically: the file still opens, the text still reads,
and the reader on another machine simply runs it against a directory that doesn't exist.
**Nothing errors — it just quietly does the wrong thing.** That's the defect class this
fleet spent 2026-09-13 removing.

## Checklist before shipping a skill

```
python3 ${SCRIPTS_DIR}/skill-portability-check.py <path-to-skill>
```

Clean output = portable. Any hit = fix before it ships.
