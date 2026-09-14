---
name: verify-after-every-action
description: "After any change, verify it took effect; if not, fix now."
tags: [verification, self-healing, fleet, model-routing, deploy, agent-kit]
trigger: "After ANY state-changing action: config change, model/provider switch, fleet sync, deploy, cron edit, handoff. Jordan's standing rule: verify it worked, and if not, fix it now."
related_skills:
  - ../deploy-and-verify/SKILL.md
  - ../cron-truth-layer/SKILL.md
  - ../auto-fix-preflight/SKILL.md
  - ../develop-and-verify/SKILL.md
version: 1.0.0
author: Gentech Labs
---

# Verify After Every Action — Universal Post-Action Verification Layer

> "After almost everything we do, we should add a verification layer to it so that we always verify that things are being done. If it does work, we immediately troubleshoot, fix it, and then... because this happens a lot." — Jordan, Sep 7 2026

## The Core Rule

**Every state-changing action ends with a verification step. If verification fails, troubleshoot and fix IMMEDIATELY — do not move on, do not report "done" without proof.**

This is the standing layer that ties together the existing verification skills:

| Existing skill | Covers | This skill adds |
|---|---|---|
| `deploy-and-verify` | Deployments (HTTP, content, visual) | The universal trigger: apply to ALL actions, not just deploys |
| `cron-truth-layer` | Cron data freshness | The "verify it took effect" step after config/model changes |
| `auto-fix-preflight` | Detect → Fix → Verify → Report | The immediate-troubleshoot discipline |
| `develop-and-verify` | Build pipeline (DEV → AUDIT) | The fleet-model-change worked example |

## The Universal Cycle

```
1. ACT      — Make the change (config, deploy, model, cron, fleet, handoff)
2. VERIFY   — Prove it took effect (read back the actual state, not the intent)
3. PASS?    → report with proof, done
4. FAIL?    → TROUBLESHOOT immediately (root-cause, don't guess)
5. FIX      — Apply the fix
6. RE-VERIFY — Confirm the fix worked
7. REPORT   — Tell the user what broke, what you fixed, and the proof
```

**The agent NEVER says "done" without a verification step.** "Done" means verified, not declared.

## Verification = Read Back the ACTUAL State, Not the Intent

The #1 failure: the agent reports what it *intended* to happen, not what *actually* happened. Verification must read the real on-disk / live / on-chain state.

| Action | Verify by reading |
|---|---|
| Config change | `grep`/`config get` the actual file, not the set command's success |
| Model/provider switch | Read `config.yaml` model block + `jobs.json` pins, not the `config set` output |
| Fleet sync | Read ALL profiles' config, not just the source |
| Deploy | `curl` the live URL + content check, not the push success |
| Cron edit | Read `jobs.json` for the job, not the edit command's exit code |
| Handoff | Confirm the file exists in the target dir, not just that you wrote it |

**Rule:** a successful tool call is NOT a successful task. The tool may have written to the wrong place, been overridden, or the running process may not have picked it up. Always read back the target.

## The Fleet-Model-Change Worked Example (the trigger for this skill)

**The problem:** Jordan changes HQ's model/provider, expects the fleet to follow, but treasury/gizmo/pixel stay on the old provider. The config on disk is correct but the running gateways serve stale config, or cron jobs keep their baked-in pins.

**The verified sequence after ANY fleet model/provider change:**

```bash
# 1. ACT — change the source profile (gentech)
hermes --profile gentech config set model.default <model>
hermes --profile gentech config set model.provider <provider>
hermes --profile gentech config set model.base_url <url>

# 2. VERIFY — read back ALL profiles' ACTUAL config (not the set output)
for p in gentech gentech-treasury gizmo pixel; do
  echo "--- $p ---"
  grep -A3 '^model:' ${PROFILES_DIR}/$p/config.yaml | grep -E 'default|provider'
  grep -A2 '^fallback_model:' ${PROFILES_DIR}/$p/config.yaml | grep -E 'provider|model'
done

# 3. If any profile DRIFTED → run the fleet sync
python3 ${VAULT_DIR}/00-System/agent-profiles/fleet_model_sync.py --check
python3 ${VAULT_DIR}/00-System/agent-profiles/fleet_model_sync.py

# 4. VERIFY the sync actually propagated (the sync can report success but skip profiles)
#    Re-read ALL profiles' fallback_model — the sync's own "updated" count is NOT proof

# 5. Check auxiliary slots (a common silent drift — they don't follow the main model)
#    grep the auxiliary block for provider/model on every profile

# 6. Check cron pins (jobs keep their baked-in provider_snapshot)
#    python3 -c "import json; ..." on each jobs.json, count provider distribution

# 7. Gateways read config at STARTUP — a running gateway serves stale config until restart
#    Check ExecMainStartTimestamp; if stale, restart (from a separate shell)
```

**Known silent-drift traps (all hit in production):**
- **Auxiliary slots don't follow the main model.** `auxiliary.<slot>.provider/.model` live per-profile and must be set separately. Treasury+gizmo were on retired `opencode-go/mimo-v2.5` while the main model was already on ollama-cloud. **Always grep the auxiliary block after a model change.**
- **Aux models must be checked for EXISTENCE on the provider you point at, not just set.** A model name is provider-specific: `z-ai/glm-5.3-flash` on **nous** is the same model as `glm-5.3-flash` on **ollama-cloud**, but most names are not portable. Read the provider's model catalog (`cache/model_catalog.json`) and confirm the id is really there before trusting a slot. A slot naming a model the provider doesn't serve fails silently at call time.
- **After retiring a provider, sweep for its models by NAME, not just by provider key.** z.ai was unused at the `provider:` level, yet the audit policy carried 20 `glm-*` references per profile — enough to mislead the next engineer. Sweep: `grep -rn -iE '<vendor>|<model-family>'` across configs AND skills, then re-verify zero.
- **Aux verification must be by resolved value, not by the file.** `hermes -p <profile> config get auxiliary` shows what the runtime actually uses; flat keys like `compression_model:` in `config.yaml` can be stale text superseded by the `auxiliary:` block. When the two disagree, the rendered output wins — and the stale flat key is a trap waiting for the day the block is removed.
- **`fleet_model_sync.py` reports success but skips profiles.** Its "updated: none needed" can be wrong. Re-read the raw config files, don't trust the sync's own count.
- **`HERMES_PROFILE=<p>` env var does NOT scope `config set`.** It writes to the calling profile. Use `hermes --profile <p> config set`.
- **Cron jobs keep their `provider_snapshot`.** A model change doesn't re-pin them. Check `jobs.json` provider distribution.
- **Gateways snapshot config at startup.** Disk config correct ≠ running gateway correct. Check `ExecMainStartTimestamp`.
- **`fallback_model` can drift independently.** It's a separate block; the fleet sync may update the main model but leave fallback on the old provider.

## Access Changes Need a Human-Path Check (hardening trap)

Before any access change — disable password auth, firewall default-deny, move the SSH port —
verify the human who owns the box still has a working path in, and prove it **as them**, not as
root-via-automation. A box whose only keys belong to automation locks the owner out.

- Provider web consoles (Hostinger hPanel etc.) typically use **password** auth — disabling it
  silently kills the owner's usual path. Consoles can also be blocked by ufw, since they connect
  from provider infrastructure.
- Take a **path inventory** before changing anything: who needs in, by what path, proven how.
- Install the replacement path FIRST, test it, then close the old one.
- "I added the key" is not evidence. A logged-in shell is.

Full checklist + inventory + recovery: `00-System/vps-access-compatibility.md`.

## The Immediate-Troubleshoot Discipline

When verification fails, do NOT:
- Move on to the next task and "come back to it"
- Report the failure and ask the user what to do
- Assume the fix will work without re-verifying

DO:
1. **Root-cause** — read the actual error/state, don't guess. Check logs, read the file, probe the endpoint.
2. **Fix it now** — apply the fix in the same session.
3. **Re-verify** — confirm the fix actually took effect.
4. **Report** — "Found X, fixed it, verified: [proof]."

## Verification Checklist (run after every action)

- [ ] Read back the actual target (file, config, URL, on-chain) — not the tool's success message
- [ ] For fleet changes: ALL profiles verified, not just the source
- [ ] Auxiliary slots checked (they don't follow the main model)
- [ ] Cron pins checked (they don't auto-follow)
- [ ] Running processes checked (gateways read config at startup)
- [ ] If anything failed: root-caused, fixed, re-verified
- [ ] Reported with proof, not just "done"

## ⚠️ Hermes config has TWO paths for the same setting

`auxiliary.<slot>.provider` **and** a top-level `<slot>_provider` both exist, and both route real
traffic. Setting one does **not** set the other. `hermes config get auxiliary` will cheerfully
report **zero** references to a retired provider **while the top-level key still points at it.**

Confirmed affected slots: `vision` · `web_extract` · `compression` · `mcp` · `skills_hub` ·
`triage_specifier` · `curator` · `session_search` · `approval`.

**Rule: after any provider change, grep the RAW config for the old provider across the whole file —
never trust one section's rendered output.**

```bash
grep -n '<old-provider>' ${PROFILES_DIR}/*/config.yaml
```

**This bit twice in one day** — a vision repoint that looked complete (top-level key still on the old
provider), and an aux "all clean" check that missed eight live routes.
**When a setting can live in two places, checking one is not checking it.**

## ⚠️ A monitor is only a monitor if someone reads it

A scheduled check with the right threshold that delivers to `local` is **a diary, not an alarm.**
Before trusting any watchdog, verify **where its output goes** — not just that it exits 0.

Real case: an Ollama usage watchdog ran every 6h at a 70% threshold, fired correctly, and wrote to a
file — **so the account hit 100% with a perfectly working alarm sitting unread.**

**Check the DELIVERY TARGET, not the exit status.**

## Why This Matters

Jordan's words: "this happens a lot." The fleet-model-change is one instance of a recurring class: config changes that don't propagate, deploys that don't take effect, cron edits that don't stick. The verification layer catches these BEFORE the user does — turning the user from QA tester back into the boss.

**The agent that verifies is the agent that can be trusted to act autonomously.**

## Negative Findings Need Proof Too

**Jordan, 2026-09-14:** *"you didn't think — let me check out their GitHub first, let me look at
their docs first before I do this, to make sure to verify everything is in order."*

**"I looked and didn't find it" is NOT "it doesn't exist."** A negative finding is a claim like
any other and carries the same burden of proof as a positive one.

**Before reporting ANY capability as missing, absent, unsupported, or broken, check the source
— in this order:**

1. **The vendor's docs** — search them directly (`?q=` endpoints beat skimming a page).
2. **The vendor's repo** — search the *code*, not just the README:
   `gh api "search/code?q=repo:<org>/<repo>+<term>" --jq .total_count`
3. **One level deeper in the object.** `dir(x)` is not the whole API. Check nested clients,
   sub-resources, and `inspect.signature` on anything promising.
4. **Only then** conclude — and label it as *"not found after checking X, Y, Z"* rather than
   *"does not exist."*

**Why:** the real cost isn't the hour lost. It's that a false negative gets reported outward —
as a bug report, a blocker, or a "can't be done" — **and spends someone else's time on our
oversight.** Missing something is ordinary. **Announcing that it's missing is the error.**

**Same family as every other rule here:** a signal that misnames its cause is worse than no
signal. "The capability doesn't exist" is a signal. Make sure it's true before you send it.
