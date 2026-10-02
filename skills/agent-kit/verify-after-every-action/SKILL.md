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

## Name the thing before you read it (the wrong-identifier class)

**A verification can be a correct observation of the WRONG NAME, and that failure is indistinguishable from a
finding.** Five in one day (2026-10-01), each producing a confident wrong answer from intact data:

| asserted on | actually true | it read as |
|---|---|---|
| a marker field `shadow` | the field is `mode` | "the proxy would ENFORCE" — while it said shadow |
| record keys `verdict` / `status` | they are `event` / `reason_code` | "verdict=None" — the record was correct |
| `API_SERVER_KEY` from the shared `.env` | the key is **per profile** | a 401 read as "the path is broken" |
| `hermes-gateway-<seat>.service` | those are the RETIRED units; the live one has no suffix | a stale script read as "already fixed" |
| `claim(..., expires_at=)` | the signature is `claim(jti, exp)` | a crash read as "the store is broken" |
| a "session id" from `ls sessions/` | that was a request-dump filename | a plausible string passed off as fact |

**THE RULE: before asserting on an identifier, READ it — the signature, the record's keys, or the variable's
source.** One line each. **When a check surprises you, suspect the name you used before you suspect the system.**

**Why this deserves its own section:** every other trap in this skill is about a system that lies. This one is
about *you* lying to yourself with a tool that is working perfectly — and it is worse, because the evidence
looks real. A wrong finding costs a peer a teardown and costs you their trust in your next one.

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

## ⚠️ `/health` 200 does NOT mean the gateway accepts work

**A gateway can serve 200 on `/health` and `/v1/models` while refusing every agent turn with 503.**
Measured on a live seat:

```
GET  /health            -> 200        (green)
GET  /v1/models         -> 200        (green)
POST /v1/chat/completions -> 503 {"code":"gateway_draining"} in 0.0014s   (every turn refused)
```

`/health` reports liveness of the HTTP surface, not admission. `/v1/models` reports a static list.
**Neither exercises the turn path.** When checking whether a peer can actually be reached, POST a
real request (or use the peer's async `run` + `status`); a curl to `/health` proves nothing about
whether work is accepted.

Source: `gateway/platforms/api_server.py` `_gateway_is_draining()` → `runner._draining or
runner._external_drain_active` → 503 `gateway_draining` with `Retry-After: 1`.

## ⚠️ A pending-state marker with presence-only semantics wedges the thing it guards

The drain above was caused by a single stale file:

```
<profile>/fleet_restart_pending      (written by an updater that could not act on its own unit)
  started=... pid=3375872 expected_sha=1a990f3062...

hermes_cli/update_cmd_fleet.py:192
  if _fleet_restart_pending_marker_path().is_file():
      return True            # presence alone — no expiry, no identity check, no discharge path
```

**One un-discharged marker ⇒ an obligation that never resolves ⇒ the gateway refuses all work.**
The updater that wrote it correctly skipped its own unit (acting on it would terminate the updater)
— but the marker it left behind had no way to record that the obligation was handled by anyone else.

**Design rule:** any "pending/owed/needs-restart" marker must carry an identity (expected sha or
version), an expiry, and a discharge path — and the read path must verify identity, not just
existence. **An artifact that cannot express its own resolution becomes a permanent false alarm,
and a permanent false alarm masks the real one.**

**Corollary for repair order:** never clear such a marker without first performing the work it
tracks. Deleting it converts a loud failure (refusing turns) into a silent stale one (serving old
code, no warning) — strictly worse, because nothing remains to signal the state.

## ⚠️ A receipt that reports work it skipped is worse than no receipt

**Verify a reported action against the artifact it claims to have changed — not against the list it
wrote about itself.** A fleet updater recorded all four gateways as restarted while the one running
the update had `NRestarts=0` and a 5-hour-old process serving code 446 commits behind:

```
receipt:  restarted_services: [treasury, gentech, gizmo, pixel]
          failed_units: []   incomplete: false   phase_error: ""
reality:  treasury/gizmo/pixel  started 23:46  NRestarts=1   code 1a990f3062
          gentech (self)        started 18:44  NRestarts=0   code 5dea46d13d  <- never restarted
```

**Probable cause and the generalisable lesson:** the updater ran *inside* the profile it would have
restarted, so restarting that unit would have killed the updater. Skipping was CORRECT; **recording
the skip in the success list was the bug.** A self-exclusion needs its own field (`skipped: [reason]`),
never the success list.

**How to check any "X was restarted/deployed/applied" claim:**
```bash
systemctl --user show <unit> -p ExecMainStartTimestamp -p NRestarts -p MainPID
# then compare the running code identity against the installed one
python3 -c "import json;print(json.load(open('<profile>/gateway_state.json'))['code_sha'])"
git -C <install> log -1 --format=%h
```
`NRestarts=0` + an old start timestamp refutes a "restarted" claim outright, whatever the receipt says.

**Corollary — self-referential operations must exclude themselves explicitly.** Any tool that
restarts/replaces the process running it will hit this: the safer behaviour is to skip itself AND
say so loudly, because the one seat that silently didn't update is the one whose reports you are
reading. Version skew across a fleet presents as "that one seat just doesn't answer."

### ⚠️ A probe from a privileged vantage point proves nothing about exposure

**Before reporting "X is publicly reachable", verify your OWN source can reach it as an outsider.**
A test that succeeds only because the prober is whitelisted is a false positive of exactly the shape
this file exists to prevent — and it reads as diligence.

Real case: a gateway backend on `:8082` returned **200** when probed at the host's public IP, and
this was nearly filed as "direct-to-IP bypass, bigger blast radius than reported." **Invalid.** The
probe ran *on* the VPS, so its source address was the box's own public IP — which the firewall
explicitly whitelists (`ufw: Anywhere ALLOW IN <operator-ip>`). Only **80/443** were open to
`Anywhere`; `8082` was **not publicly reachable at all**.

```bash
# 1. What can the general internet reach?
ufw status numbered            # look for 'Anywhere' entries only — a named IP is a whitelist

# 2. What address am I probing FROM?
curl -s https://api.ipify.org   # if it matches a whitelist rule, your result is void

# 3. Prefer the real public path (DNS name -> CDN -> origin) over IP:port
curl -s -o /dev/null -w '%{http_code}\n' https://public-hostname/path
```

**Rule: state the privilege of the probe alongside the result.** "200 from inside the allowlist"
and "200 from the open internet" are different findings, and only the second is a security finding.
Same family as the self-request deadlock and the stale-claim probes: *a test must be able to
distinguish the target's condition from the tester's.*

### ⚠️ A monitor that SKIPS the broken state can never report it

**Before trusting a health check, confirm it actually inspects the state that goes wrong.**

A cron health monitor contained `if not enabled: continue` and **zero occurrences of the word
"paused"** anywhere in the file. A doorbell job had been paused for 14 hours; the monitor reported
**"ok"** at the end of it. The check was not wrong — it was structurally blind, because the failure
mode *was* the state it skipped.

Same family as a probe that only hits `:443` while the leak lives on `:80`, or a test that only runs
on the happy path. **The blind spot is in the check, not the system.**

**Rule:** enumerate the states your check never visits, and ask which of them would be a failure.
Then either test them or state plainly that they are uncovered.

### ⚠️ Turning off a notification path means you must change how you SEND

**If you disable a wake/doorbell/watch mechanism, every workflow that relied on it breaks silently.
Disabling the notification is a SEND-SIDE change, not just a receive-side one.**

A wake trigger ("scan inbox, DM the agent when a new handoff appears") was paused. Handoffs kept being
filed as vault files — the *record* half of "DM to wake, vault to record" — and nobody was ever woken.
A live security finding sat unread for 5 hours and was then fixed within 20 minutes of an actual DM,
which proves the file was fine and only the doorbell was missing.

**Rule:** when you switch off a wake path, immediately substitute a delivery mechanism for anything
urgent (DM at filing time), and audit what else fed off that path. A relay that writes a file and
calls it delivered is not delivery.

### ⚠️ A stale note is more dangerous than no note — check the artifact you READ, not the one you wrote

**When a fix lands, the note describing the OLD state is still there and still authoritative-looking.
A reader finds it, believes it, and re-debugs a fixed bug — or mis-scopes a live one.**

Three times in one week, the same shape:
- A relay filed into an inbox whose doorbell had been switched off — the file was correct, delivery
  was not, and the sender believed "filed" meant "delivered."
- A "BLOCKED" note kept re-alerting after the task was done, because the DONE note was a *different
  file* the reader never opened.
- A registry entry describing a bug that had already been fixed in live source, which made the
  remaining fix look larger than it was.

**The pattern: the artifact describing the fix is not the artifact the reader finds.**

**Rule:** when you ship a fix, update the artifact that DESCRIBES the broken state in the same
change — not a new adjacent file. And when you read a status claim, check it against live state
before acting on it, because the note may predate the fix it contradicts.

## ⚠️ A static file can shadow the route you deployed to

**"I verified it on the public endpoint" is worthless if you verified a DIFFERENT public URL than
the one consumers read.** A deploy can land in the service while the canonical public path keeps
serving an old file, because a webserver matches a longer location prefix first.

Real case (2026-09-15): a manifest fix was deployed and "verified on the public endpoint" — true of
`/.well-known/x402-bazaar`, **false of the canonical `/.well-known/x402`**, which nginx served from
disk because the prefix is longer than the `/` proxy rule:

```nginx
location /.well-known/ { root /var/www/site; }      # ← longer prefix, WINS
location /            { proxy_pass 127.0.0.1:8090; } # ← the service your fix is in
```

So the service route was never reached for that path. Three artifacts then disagreed — served file
(10 services), the service's own copy (11), the sibling doc (14) — and the canonical one had been
**stale for 16 days** while consumers read it.

**Prove which artifact a URL serves by HASH, not by reading a field:**
```bash
curl -s https://host/path | sha256sum
sha256sum /var/www/site/path          # identical sha = you are reading the static file
nginx -T | grep -A2 'location .*well-known'   # which rule actually matches
```

**Rule: identify the artifact behind the URL before trusting anything read from it.** When a path
exists both on disk and as a service route, one of them is invisible — and it is usually the one you
deployed to. Prefer deleting the shadow so there is ONE source.

### ⚠️ A DOCUMENTED claim is not a TESTED one — eligibility is not trigger

**When a vendor's doc says X causes Y, treat it as a hypothesis. Find the log line that proves it.**

A platform doc said endpoints become *"eligible for indexing AFTER A SUCCESSFUL SETTLED PAYMENT."*
That was read as **"a settle triggers indexing"**, and money was about to be spent on a plan derived
from it. **It was wrong.** The catalogs were being filled by **crawlers** reading our 402 challenges,
with **zero payments** — visible only in our own nginx access log.

**What made the misreading convincing:** the predicted effect and an unrelated cause happened in the
**same minute**, so the timestamp "confirmed" the theory. The actual trigger was an earlier fix that
changed our responses from `307` to `402` — a crawler could not see a challenge before it.

**Rules:**
- **"Eligible for" does not mean "triggered by."** A precondition describes what is *allowed*, not what
  *happens next*.
- **A correlation that lands inside the same minute is the most seductive and least reliable kind.**
  Look for the *other* actor before concluding causation.
- **Check your own access logs for crawlers/bots by User-Agent** before designing anything payment-based.
  `grep <Candidate-UA> /var/log/nginx/access.log*` — if an index can be filled by a crawl, no spend is
  needed.
- **Prefer the free measurement over the paid one.** Waiting one cycle and re-measuring cost $0; the
  settle plan would have cost real money to test a model that was already disproved in our logs.

- **Never read `ls` of a folder root as 'there is nothing here'.**
- **A hash quoted in a note or commit message goes stale the moment the file changes
  again — quote the COMMIT instead.** `git show <commit>:<path>` always resolves to
  exactly what you measured; a bare md5 cannot, and the reader has no way to tell whether
  they are testing your revision or a newer one. Two agents can each be right and still
  disagree, purely because the artifact moved between their measurements. When handing an
  artifact to another seat: name the commit, state the size, and attach the blob.
- **Before saying a peer's finding is stale, reproduce it against the revision they
  named.** "Superseded" and "wrong" are different verdicts, and only the reproduction
  distinguishes them. Confirm their measurement on their revision, then show it closed on
  the live one.
- **A hash quoted in a note or commit message goes stale the moment the file changes
  again — quote the COMMIT instead.** `git show <commit>:<path>` always resolves to
  exactly what you measured; a bare md5 cannot, and the reader has no way to tell whether
  they are testing your revision or a newer one. Two agents can each be right and still
  disagree, purely because the artifact moved between their measurements. When handing an
  artifact to another seat: name the commit, state the size, and attach the blob.
- **Before saying a peer's finding is stale, reproduce it against the revision they
  named.** "Superseded" and "wrong" are different verdicts, and only the reproduction
  distinguishes them. Confirm their measurement on their revision, then show it closed on
  the live one.
- **"All four seats" is a claim about the seats you can see.** When you generalise a
  delivery ("now on every seat"), you are asserting it at the RECEIVER — and the seat you
  cannot see is exactly the one that doesn't have it. Count the seats from the roster, not
  from the machines you happened to touch, and say which set you actually verified.
  Same family as the stale refs: a delivery asserted from the sender's position.
- **Never sweep git refs WITHOUT fetching first.** `git ls-tree -r <ref>` over a stale
  remote-tracking ref is a false-negative machine: it reports "absent from every branch"
  for a commit that exists upstream, and the absence looks exactly like proof. A search
  of refs is only as current as the refs. **`git fetch --all --prune` before any
  "I checked every ref" claim** — otherwise the honest statement is "absent from my
  LOCAL VIEW of the refs", which is a different and much weaker claim.
  Parallel to the false green: a sweep that cannot find anything and a sweep that had
  nothing to find produce identical output.

**A listing's shape is not a statement about content.** Directories and dotfiles at a folder root say nothing
about what is inside them — and a lane whose root looks empty is often just **archived**.

**The test that is actually honest:** ask git what it tracks, recursively.

```bash
# WRONG - sees the root only, and "no .md here" is not "no notes here"
git ls-files 01-HANDOFFS/<lane>/
ls 01-HANDOFFS/<lane>/

# RIGHT - catches _archive/, _closed/ and every nested note
git ls-tree -r HEAD --name-only | grep "01-HANDOFFS/<lane>/"
```

**Two real instances in one week, both mine:**
1. `_lane-state.json` — I read top-level keys that don't exist at that level, saw `None`, and reported the
   agent's lane as "degraded". The values were intact under `measured`.
2. `forge-to-gentech/` — I ran `ls` on the root, saw `_archive/`, `_closed/` and dotfiles, and wrote that the
   lane "contains no `.md` notes at all". **39 archived notes were one level down.**

**Why this class is worse than a normal miss:** it converts "I used a command that could not see the data"
into a **claim about another agent's diligence** — "this seat went silent" — which is both false and
unflattering. An empty lane root usually means **the archiving workflow ran**, which is the system working.

**Rule:** before saying anything is absent, name the command you used and ask whether it could have seen the
thing. Prefer a recursive git query over any directory listing, and never generalise from one missing file to
the state of a whole lane.

## Why This Matters

Jordan's words: "this happens a lot." The fleet-model-change is one instance of a recurring class: config changes that don't propagate, deploys that don't take effect, cron edits that don't stick. The verification layer catches these BEFORE the user does — turning the user from QA tester back into the boss.

**The agent that verifies is the agent that can be trusted to act autonomously.**

## Config has TWO paths — never check one and call it done

Settings like aux providers/vision can live in **two places**: a top-level `<slot>.provider`
AND `auxiliary.<slot>.provider`. Setting one does NOT set the other, and a sweep of only
one path misses the other. Before declaring a provider switch "done fleet-wide":

1. **Walk the ENTIRE config tree** (every key/value recursively), flag every value
   containing the dead/old provider name — do NOT pre-filter to known slots.
2. Check BOTH paths for every aux slot: top-level `<slot>.provider` and
   `auxiliary.<slot>.provider`.
3. **Verify by resolved value, not by what the file looked like** — a name in the file is
   not proof the running process uses it.
4. Re-check after a change: an exhaustive re-walk returning ZERO hits of the old provider
   = done. One known-slot spot check = NOT done.

Real incident (2026-09-14): Treasury + gizmo kept firing a nous fallback warning for hours
because the earlier "fleet switched to ollama-cloud" check only swept `auxiliary.*` and MISSED
`vision.provider = nous` at the top path. Took 3-4 tries. The fix that actually worked was an
exhaustive recursive walk of every profile's config tree.

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

## ⚠️ A line number is a fact about a REVISION, not about the code

**Cite the symbol, not the line.** Four copies of one file on one machine gave four different
answers for the same code, because each was a different revision:

```
models.py:1412    live VPS install (5dea46d13)   <- published by one seat
models.py:1384    a checkout (fcd7df372c)        <- cited by the other seat
models.py:1259    our PR head (9033a596)         <- a third number
github main:1434  the PR's actual BASE           <- what a public comment needs
```

The symbol `_PROVIDER_CATALOG_FETCHERS["ollama-cloud"]` was identical in all four. The line number
rotted within a day as `main` moved — and a maintainer clicking the cited line on `main` finds
unrelated code and stops trusting the rest of the report.

**Rules:**
- Reference the **symbol / key / function name**. It survives refactors and rebases.
- If a line number is genuinely needed, **pin the revision in the same sentence**
  (`models.py:1434 @ 40f2702b2`). Unpinned, it silently becomes a false claim.
- **Name the revision of the FILE, not the repo HEAD.** They differ whenever a commit doesn't
  touch that file — which is most commits. Labelling a copy with `git log -1` (repo HEAD) and then
  quoting a line from it is a mislabel, and it happened to two of four copies in the case above.
- **Before attributing a number to a change, check the change touches the file at all.**
  `git show --stat <sha> | grep <file>` — a PR whose diff is one file cannot have moved lines in
  another. Quoting a line and naming a PR that never touched that file reads as authoritative and
  is checkable in seconds — by a reviewer who will then distrust everything else in the report.

**Self-test before publishing any file/line/version claim:** *if a reader opens exactly what I
cited, at the revision I named, will they see what I said?* If the revision is unnamed, the answer
is unknowable and the claim is not yet checkable.

### ⚠️ `git show --stat` reports the WHOLE TREE when a commit is GRAFTED

**An empty `%p` means the commit is grafted — not that it is a root commit, and not that the
parent object is missing.** A graft (`.git/shallow`) suppresses traversal while the parent object
sits in the pack. Proved by adding a tip to `.git/shallow` in a full clone:

```
parent object present          -> cat-file -t = commit
add tip to .git/shallow        -> parent object STILL present (cat-file -t = commit)
                                  %p = ''            (git's GRAFTED VIEW)
                                  --stat = whole tree
                                  raw object still contains 'parent 8f6d5bc...'
```

**`git log --format=%p` is a DERIVED VIEW, not the object. It lies under a graft.** So:

```bash
# is it grafted?  (empty %p here is a graft, not a root)
[ -f .git/shallow ] && grep -q "$(git rev-parse <sha>)" .git/shallow

# is it REALLY a root commit?  read the raw object — zero parent lines = true root
git cat-file -p <sha> | grep -c '^parent'
```

**Boundary sets differ per clone, so the same commit can be grafted on one box and not another.**
The same command against the same commit gave opposite output on two machines in one session
(10 boundaries vs 51). A reading is only valid for the clone it was taken in — quote the clone
state alongside it.

**Prefer the PR API over local `--stat` for "what does this PR touch":**
`gh api repos/<owner>/<repo>/pulls/<n>/files --jq '.[] | {filename, additions}'`. It reads from the
host, not your clone, so local object state cannot fool it.

### ⚠️ State the METRIC, not just the number

**Two correct measurements of different quantities look like a contradiction.** "Lines in the tree"
is undefined until you say whose counting:

```
git diff --numstat <empty> HEAD, summed text additions : 3,162,920   (binaries = 0, no-NL = +1)
wc -l over every file's contents                       : 3,297,689   (counts newlines inside binaries)
reconciled exactly: 3,162,920 + 135,134 (newlines in 91 binaries) - 365 (files w/o trailing NL)
```

Neither figure was wrong. The apparent 134,769 gap was **a metric difference wearing the same
word**, and it cost both seats a round of guessing (one guessed "binaries", which overshot).

**Name the unit in the sentence:** `numstat additions (text)` vs `wc -l (all bytes)`; `characters`
vs `bytes`; `files` vs `paths` (a `find -name` census counts directories too). If two numbers about
the same thing disagree, **suspect the definitions before suspecting the arithmetic.**

**Clone state is not a revision.** A shallow boundary, a detached HEAD, a grafted parent, an
uncommitted edit — all are local states that masquerade as facts about a commit. A content hash or
line number is meaningless unless paired with the artifact it describes (`<file> @ <blob|rev>`).

**Before citing any file/line/version fact, ask which revision you measured.** "I read it in the
file" is not sufficient when several revisions of that file exist locally.

## ⚠️ Measure with `-type f`, and count BYTES not characters

Two measurements that look verified and are not. Both produced wrong numbers that were reported
outward and propagated to another seat before anyone re-ran them.

**1. `find -name '*.ext'` matches DIRECTORIES too.** Foundry writes build output as
`out/<Name>.sol/` **directories**, empty, one per artifact. A census that omitted `-type f`
reported "329 `.sol` files" when the truth was **92 files + 237 directories** — and the number
was carried into a peer's report as evidence for a defect class that didn't exist.

```bash
find . -name '*.sol' -type f -not -path './.git/*' | wc -l   # the real count
find . -name '*.sol' -type d -not -path './.git/*' | wc -l   # what you were counting
```

**Any extension census, size audit, or "N files were dropped" claim needs `-type f`.** Then
divide the result into tracked / untracked / **untracked-AND-not-gitignored** — only the last
category is a transport or deployment gap. An ignored file is not a missing file.

**2. `len(str)` is characters; `len(s.encode())` is bytes.** Reported a file as `11211 B` when
git said `11224`. A 13-char gap from multibyte characters (`·`, `—`, `✅`). The **sha256 was
correct** because it hashed `.encode()` — so the two numbers in the same table disagreed and
neither looked wrong.

```bash
wc -c < file          # bytes (authoritative)
git cat-file -s <blob>  # bytes, straight from git
hashlib.sha256(raw).hexdigest()  # hash the BYTES, then size them the same way
```

**Rule: derive every quantity in a report from the same representation, and prefer the tool that
measures the artifact itself (`wc -c`, `git cat-file -s`) over one you compute in Python.**

## ⚠️ Scope your claim to what you measured

**A single-tree observation is not a fleet-wide claim.** Writing *"Nothing closure-related is
`git ls-files`-tracked"* after checking **only my own checkout** generalised one seat to every
seat — and the artifact was, at that moment, present in a peer's branch. The claim was true of
my tree and false of the fleet.

**Say "not in this tree" when that is what you checked.** If the finding is going to a peer, it
is going to be acted on: an unqualified negative makes them rebuild something that exists, or
chase a defect that doesn't. Cost-free precision: name the scope in the sentence.

**Corollary for receiving:** when a peer hands you a measurement, **re-run it before building on
it** — a number you inherited was not verified by you. In the incident above, a peer's report
carried my wrong `.sol` figure forward; the seat that trusted the peer's number passed the error
along. Re-measuring a two-minute census is cheaper than a wrong report to a third party.

### ⚠️ A check that validates a COPY of the thing is not a check on the thing

**A guard that mirrors the values it guards — instead of reading them — reports green while the
real source is broken.** The mirror and the source are two artifacts, and only one of them is live.

Real case (2026-09-15): a new `test_eip712_domains.py` guarded EIP-712 domains by comparing a
**hardcoded `SHIPPED` dict** against pinned on-chain separators. Nothing read the actual source
(`server.py`'s `NETWORKS`, `server.mjs`'s `PRICE`); even its `--live` flag only re-read the chain,
still taking the shipped name/version from the literal. Proven by re-injecting the real defect into
the real source (edit confirmed landed) and running the guard untouched:

```
guard output: 5/5 PASS, "ALL DOMAINS CORRECT", exit 0
real source : the celo rail was genuinely mis-signed
```

Its author's "proven both ways" was **circular** — the BUG replay mutated the *test file's own* dict,
so it demonstrated the comparison arithmetic, not that the source was watched. The one failure mode
that had already bitten us (source drifting from the mirror) was the one case it could not see.

**Rule: a verification must READ the artifact it claims about.** Derive the shipped side from code
(import the config object, parse the source, or probe the running service). Pinned truth values are
fine — pinning the *expected* side is correct — but the *actual* side must never be a copy.

**Prove any guard can fail on the REAL system, not on its own fixture:** make the genuine defect
recur in the genuine source and confirm the guard goes red. If reverting the source doesn't flip the
result, the guard is a mirror.

## ⚠️ Never draw the test sample from the implementation under test

**The most dangerous kind of wrong number is one that is arithmetically correct.** A coverage
matrix whose inputs come from the code being measured will report a *self-consistent* figure that
looks like evidence and discriminates nothing.

**Real case (2026-09-14):** measuring whether a vendor-prefix strip covers a model catalogue, the
slug list was drawn largely **from the lookup table the code consults**. Nine of ten test slugs
were values *in that table*. Result: a values-only predicate and a keys-or-values predicate scored
**identically** (216/240 each) — the sample could not tell them apart, because every slug was
already a member of the set being tested. Re-measured on an **independently-drawn** list (domain
knowledge: real aggregator prefixes plus key-form tokens), the same two predicates came out
**240/360 (66%)** vs **336/360 (93%)** — a 27-point gap the circular sample had hidden.

**Rule: the test sample must come from the DOMAIN, not from the artifact.** If your inputs appear
verbatim inside the thing you are testing, you are measuring self-consistency.

```
# CIRCULAR — slugs taken from the table under test
SLUGS = list(_VENDOR_PREFIXES.values())

# INDEPENDENT — slugs taken from how the domain actually presents them
SLUGS = ['mistralai','z-ai','deepseek',..., 'glm','claude','kimi','gpt']  # incl. forms the table lacks
```

**Include at least one input you expect to FAIL.** A sample where every case passes cannot
falsify anything. The absent slug (`mistralai`) and the key-form slugs (which values-only misses)
are what turned a flat 90% into a discriminating 66% vs 93%.

**Same family as every rule here:** a number that can't be wrong is worse than no number, because
it gets reported outward as evidence.

## Deployment drift: ONE canonical file + symlinks (a copy can go stale, a symlink cannot)

When a tool exists in several places and the file that RUNS is not the file you edited, "copy the newest
file over" is not a deployment — it MOVES the drift.

1. **Pick the canonical path by capability, not preference.** A tool that imports siblings relative to
 its own file can only live where those siblings are. If one directory is the only one that has them,
 the choice is FORCED — say so instead of presenting it as a judgement call.
2. **Make every other entry point a symlink to canonical.** The caller's path is unchanged (cron
 `script:` resolves by name), so nothing downstream needs editing.
 **⚠️ EXCEPT when CRON runs that path directly — there a symlink is a dead job, not a deployment.**
 The scheduler resolves each job's `script:` against `HERMES_HOME/scripts` and REFUSES the job when
 the real path escapes that dir (`cron/scheduler_script.py:_resolve_script_path`, Hermes 0.21.3):
 *"Blocked: script path resolves outside the scripts directory"*. A refused job never starts — it
 produces no red check, only a silent `last_error` in the job file. **Measured 2026-09-16: three jobs
 across two profiles were dead this way** (gentech `port-health-monitor` 18:00Z, gentech
 `nightly-maintenance` — latent, would have died 04:30Z, gizmo `api-health-check` 07:01Z) because the
 canonical+symlink pattern had been applied to paths cron executes. For a path cron executes, the
 correct form is a **byte-identical COPY inside that profile's own `scripts/` dir**, and the guard's
 job is to catch a copy that goes STALE (sha256 vs canonical) rather than to demand a symlink.
 Symlinks stay correct for every entry point nothing schedules.
3. **⚠️ `os.path.abspath(__file__)` does NOT resolve symlinks — use `os.path.realpath(__file__)`.**
 This is the trap that makes a naive symlink fix fail: the symlinked entry point reports the
 *symlink's* directory as its own and looks for siblings there, in a directory that has none. Fix
 realpath FIRST, or you ship the same false red you were removing.
4. **Prove the guard is falsifiable before trusting it.** Inject a real copy where a symlink belongs,
 confirm the drift check fires, then restore. An unfailable guard is the defect, not the fix.
5. **A stale copy of an OPERATIONAL script is a hazard, not untidiness.** Read what the old copy is
 MISSING before treating drift as cosmetic. A stale maintenance script lacking a protected-paths
 denylist would delete a live service's `node_modules` and crash-loop it on next restart — and a
 running process masks the damage until it restarts.
6. **Establish "stale" vs "a different artifact" BEFORE overwriting.** Identical docstrings plus a diff
 dominated by additions means same tool, older generation. A different docstring means a genuinely
 different artifact, and overwriting it destroys intent.
7. **A sibling-less deployment target is worse than none** — it turns every run into an
 `indeterminate`/false red. Distinguish "probe could not run" from "thing is broken" as separate
 states, then check which one your deployment actually produces.

## ⚠️ "The file is on disk" is not "the file is served" — check the EDGE, not just the origin

A file can be correctly installed, byte-identical to the repo, and still **404 for every visitor**,
because a CDN is serving a cached 404 from before the install. This is indistinguishable from a missing
file unless you look for it, and it makes a completed fix look failed.

The tell is in the response headers of the 404 itself:

```
HTTP/2 404   server: cloudflare   cf-cache-status: HIT   age: 61   cache-control: max-age=14400
```

Three probes separate "missing" from "cached-missing" — run all three before concluding anything:

1. **Bytes, with the encoding pinned.** `curl -H 'Accept-Encoding: identity'`. Comparing compressed
   bytes against an on-disk file yields a mismatch that looks like drift and is not. (This one cost me a
   false `served != webroot` against a colleague's correct measurement.)
2. **Cache-busted.** Append a unique query (`?cb=$(date +%s)`). 200 here + 404 on the bare URL = edge cache.
3. **The origin directly.** `curl -H 'Host: <domain>' http://127.0.0.1/<path>`. This removes the CDN from
   the question entirely.

If it is the edge and you hold no purge token, changing the URL the page asks for (a version query) fixes
it for real visitors immediately. **Revert that workaround once the edge revalidates on its own** — an
unpurgeable cache is a temporary condition, and leaving token noise in the markup is a permanent one.
Warn anyone re-measuring in the window: they will see 404 on a file that is correctly installed.

## ⚠️ Probing page assets: extract EVERY fetch-capable attribute, and resolve RELATIVE refs

A guard that greps a page for `https://yourdomain.com/...` misses exactly the refs that break. Two
independent blind spots, both silent:

- **Relative refs.** `music/film-v8.mp4` is the common form and an absolute-only regex never sees it.
- **Attributes other than `src`/`href`.** `<source src>`, `poster`, `data-src` and `srcset` all fetch
  bytes. A `<video preload="none">` with a dead `<source>` renders a perfect poster and only fails when a
  visitor presses play — and nothing logs it, because there is no handler.

Extract `src`, `href`, `poster`, `data-src` and `srcset` (splitting the candidate list), accept both
relative and own-domain absolute URLs, then assert **two separate things**: the file exists under the
webroot (install gap, rename) **and** it answers an anonymous fetch (edge cache, nginx). They fail
independently and need to be reported independently — the filesystem cannot see the second one.

**Dedupe before probing.** The same poster appears on every card; probe each unique path once and map back
to the pages that use it, or a health check fires hundreds of live requests and gets disabled.

## ⚠️ A falsifiability test must never mutate the thing it is testing

Proving a guard works by planting a defect directly into the **live** artifact is a self-inflicted
outage. The window is small, which is exactly why it survives review — and it has one fatal property:
**if the run is killed between plant and restore, the restore assertion can never fire.** The mutation
simply stays, on a production page, with nobody watching for it. This happened: a test that copied
`/var/www/gentechlabs/hub-vanito.html`, planted a dead link in it, and restored it afterwards left a
visitor clicking a planted 404 on the live hub for ~34 seconds.

The rule: **the test writes to a throwaway copy, never to production.** Three properties make it work:

1. **Scratch root, symlinked tree.** `mkdtemp()`, then symlink every entry of the real webroot into it
   *except the artifact under test*, which is **copied**. Reads pass through the symlinks so refs still
   resolve and the baseline stays honest (`missing 0`); the only writable object is the copy.
   Symlinking rather than copying matters when the tree holds gigabytes of media.
2. **Make the guard's root injectable** (`os.environ.get("GENTECH_WEBROOT", <default>)`). A checker whose
   scope is hardcoded cannot be tested without touching what it checks.
3. **Startup restore-check.** Before doing anything, assert the live artifact carries no test marker and
   **strip any it finds** — that is the only recovery path for a run that already died mid-window. Then
   assert at the end that the live artifact is byte-identical to how it started.

A guard against this that is worth copying: keep the plant marker a single distinctive token, so both the
startup check and the end-state assertion are one grep. And **verify the recovery path itself** — plant
into a scratch copy by hand, run the startup check, and confirm it strips the marker and restores the
exact original hash. An untested recovery path is a guess.
