---
name: service-health-monitoring
description: Monitoring backend services, ports, and public URLs on the GenTech VPS — with cron-based alerts
category: devops
---

# Service Health Monitoring

## When to use
- Setting up monitoring for backend services
- Checking if all ports and public URLs are healthy
- Creating alerting when services go down
- Auditing which services are running

## The Pattern
The Port Health Monitor is a no-agent cron script that:
1. Checks each backend port via SSH (`ss -tlnp | grep -E ':<port> '`) — TCP-level, not HTTP-level
2. Checks public URLs via HTTP (any response = alive, even 4xx/5xx)
3. Reports only on failure (silent when healthy)
4. Delivers to the origin chat so the user sees it

## Script Location
`${PROFILE_DIR}/scripts/port-health-monitor.py`

## Services Checked

**Verified port map (Aug 9, 2026 audit — cross-checked via `ss -tlnp` + `/proc/PID/cwd`):**

**GenTech API fleet (systemd, Python uvicorn):**
- 3099 — x402 Test Harness (`x402-test.service`, node) → `gentechlabs.net`
- 8080 — Deal Tracker API (`deal-tracker-api.service`) → 10-Labs/deal-tracker-api
- 8082 — Crypto Price API (`crypto-price-api.service`) → 10-Labs/crypto-price-api
- 8084 — Gas Price API (`gas-price-api.service`) → 10-Labs/gas-price-api
- 8086 — Token Security API (`token-security-api.service`) → 10-Labs/token-security-api  ⛔ RETIRED 2026-09-15 (duplicate of rugcheck; gateway serves it)
- 8088 — Rugcheck v2 API (`rugcheck-api.service`, sim mode) → /root/rugcheck/api → `rugcheck.gentechlabs.net`
- 8090 — x402 Gateway v2.0 (`x402-api.service`) → `api.gentechlabs.net`
- 8091–8096 — x402 backends (`x402-backend@.service` template): agent_discovery, defi_lp_analytics, wallet_analysis, nft_search, lineage_guard, treasury_defender
- 8765 — hermes-bridge (`gentech-bridge.service`)

**Infra:**
- 8402 ClawRouter proxy | 8011 ClawWork router | 9119 Hermes dashboard
- Docker: 3306 MySQL (datahub), 5432 Postgres (hummingbot), EMQX broker (1883/8883/18083/61613/8097-8099), trek :3002, multica :3001/:8081, rota :8000, hummingbot gateway :15888

**Public URLs (HTTP response check — any response = alive):**
- `https://gentechlabs.net` (→3099)
- `https://api.gentechlabs.net` (→8090)
- `https://rugcheck.gentechlabs.net/v1/health` (→8088)
- `https://gentechlabs.net/demo/v1/defender/classify/{chain}/{token}` (→8096)
- `https://yield.gentechlabs.net`, `https://arcade.gentechlabs.net`

Full audit recipe + verified port table: see `references/fleet-map.md`.
NOTE: the OLD monitor mapping (8080=Token Security, 8082=Wallet Analysis,
8086=Rug Check) was wrong — the reference file table is authoritative.

## Cron Schedule
Twice daily: `0 6,18 * * *` (6am/6pm ET)
Job ID: `eb6fffc08d0e`
Created: Jul 28, 2026 (replaced earlier port health check that was paused)

## Key Design Decisions
- **TCP-level check** (is the port open?) rather than HTTP-level (is there a /health endpoint?). Backends may not have a /health endpoint but are still running.
- **Silent on success** — only alerts when something is down. No noise.
- **No-agent mode** — the script runs standalone, no LLM cost per tick.
- **SSH-based** for port checks (can't check internal ports from outside).

## Pitfalls
- **4xx responses are NOT failures** — they mean the server is alive but the endpoint doesn't exist. Only 5xx, timeouts, and connection refused are real failures.
- **A 200 does NOT mean the target exists — a catch-all route answers EVERY path, and it reads as a pass.** The inverse of the rule above, and the more dangerous direction: a vhost or SPA with a fallback (`try_files $uri $uri/ /index.html`, a wildcard route, or a custom error page that still returns 200) serves the SAME successful response for a path that exists and for one that never has. Measured: a game subdirectory returned **200** while the game had never been deployed — the real directory answered **403**; the 200 was the arcade's SPA fallback serving the root page. Nothing in the status code distinguishes them. **Always run a CONTROL probe against a deliberately nonsense path in the same namespace** (e.g. `/cabinet/definitely-not-a-game-xyz/`) and compare the **served content**, not the code: when the control returns the same status AND the same title/body, the probe has established nothing about the target. Cite a matched `<title>` (or a body fingerprint) as the evidence of liveness — never the status code alone.
- **`/health` 200 does NOT mean the service accepts work.** A concurrency cap can refuse every real request (`HTTP 429 Too many concurrent runs`) while `/health` and `/v1/models` both return 200 — measured on the gentech gateway for 9 minutes straight. The 429 gate is `active_agent_work_count()` (pending admissions + in-flight turns + live run tasks); `/health` never consults it. **Liveness = one real POST, not a status read.**
- **Do not probe your own api_server from inside its own turn.** If you run as the agent the gateway serves, a self-POST queues behind the turn issuing it — and it *consumes* the concurrency slot you are testing, so the probe can wedge the seat it is measuring. Probe from outside, or use the async `/v1/runs` path and poll it. A `000` on a timeout sized below real latency reads as "dead peer" but may only mean "slow".
- **Wait one polling cycle before declaring "needs an operator."** A transient that clears on its own and a wedge that genuinely needs a restart are the same picture at t+0. Poll twice before escalating; the measured case cleared in 9 min with the process PID unchanged (no restart was ever needed).
- **SSL cert mismatches** on subdomains (e.g., `demo.gentechlabs.net` using the main domain's cert) cause false positives. Use `-k` flag or check via HTTP first.
- **Cloudflare** can return 403 for requests without proper headers. Check from the VPS directly to bypass.
- **A systemd unit existing does NOT mean the service runs.** The x402-backend@<name> units + port drop-ins can exist but be disabled/inactive — the Aug 9, 2026 audit found treasury_defender (:8096) had a PORT=8096 drop-in but the unit was dead, causing a 502 on the defender URL. Always check `systemctl is-active` and `systemctl is-enabled` before assuming a backend is up; fix with `systemctl enable --now x402-backend@<name>`.
- **nginx 502 with a listener gap = dead backend.** Cross-check `grep -rnE "proxy_pass" /etc/nginx/sites-enabled/` ports against `ss -tlnp`; every proxied port must be listening.
- **cad.gentechlabs.net → :5188 → 502 is EXPECTED** when Forge's laptop is offline (VPS proxies to Forge's local Vite dev server). Check vault agent-brain notes before treating it as a bug.
- **Test the real route, not the nginx prefix.** treasury_defender routes are mounted under `/demo/v1/defender/...`, so the bare prefix `/demo/v1/defender/` 404s while `/demo/v1/defender/classify/{chain}/{token}` returns 200. The 404 on the prefix is normal.
- **Two endpoints that name the same subject must be verified to AGREE, not each verified to work.** Measured on sovereign-router402 (Sep 15): `POST /score {"name":"gpt-oss:120b"}` returned **85/Poor** while `POST /route` returned **529/Fair** for the same model, both advertised and payable through the public gateway. `/score` built its profile from the request body alone and never consulted the candidate pool `/route` reads, so each endpoint was individually "working" — the defect lived strictly in the disagreement. **Fix pattern:** when a paid endpoint accepts an identifier for an entity the service already holds, resolve the held entity instead of scoring an empty shell, and **return which source was used** (`scored_profile_source: registered|supplied`) so a caller can never be unsure what was scored. **Test pattern:** assert equality across the two paths for every registered entity, and run the new test against base — the base run is what proves the test can fail.

  - **A call that is ACCEPTED and never ANSWERED emits no error at all — every error-based health check
    reads it as healthy.** Measured 2026-09-28 on the peer-DM leg. Every seat returned `202 Accepted` with a
    run id, so "did the call fail?" answered *no* on every check; meanwhile the replies never arrived. The
    caller saw `status: running, output: None` indefinitely — no rejection, no timeout, no message.
    **The failure is silent outward and loud only inward**, which is why the sender side could not reproduce it
    and the receiving seat's log was the only place the error existed (`HTTP 429 … session usage limit`).
    **Check the terminal state, not the transport:** `did a run I started ever reach `completed`/`failed`?`
    A run that is still `running` long past its expected duration IS the alarm. Transport health (200/202,
    listener up, port open) is orthogonal to whether the work finished — verifying the first and reporting
    the second is the false-pass this section exists to prevent.
  - **Corollary — read the FULL log, never a `tail`, when reporting a count.** The same session that found the
    above reported "no rate-limit events since 04:00Z" from a `tail`; the full log showed **10 events within the
    hour** and two seats reported as "none" actually had 8 and 7. A `tail` is a window, not a census. Any count
    quoted from a log is true only at its instant — write it as `"0 since 04:00Z as of 17:53Z"` or do not write it.
  - **Shared credentials make per-seat health a fiction.** All four VPS seats authenticate to ONE provider
    account (the limit error names the same account on every seat), so one seat's burst stalls the others. A
    per-seat "provider OK" check can read green while the shared quota is exhausted — and the correct response to
    that limit is to **stop and wait**, never retry, since retrying adds load to the resource that is empty.
  - **Verify the INSTRUMENT before trusting the number — a glob that silently omits files looks exactly like a log
    with no entries.** Both return a number; only one is a measurement. Measured 2026-09-28: a rate-limit census
    used `grep … $D/*.log`, but `*.log` matches files *ending in* `.log` and the rotated files are `agent.log.1`,
    `.2`, `.3` — so the entire rotation was invisible and the count read **8** where the true value was **40**
    (5x). It was reported as a *correction* of an earlier count, so the same broken instrument was trusted twice.
    **Before quoting any log-derived count: `ls` the pattern and read how many files it actually matched.**
  - **Count the artifact's own identifier, not matching lines.** One HTTP error is typically logged several times
    across `agent.log` + `errors.log` (measured **4.6x**, one ref appearing 6 times), so a line-match count
    inflates against the real event count. The unit of count must be the unique event id (a `ref` UUID), and the
    window must be stated: **`pixel 71, gentech 40 (unique 429 refs, as of 18:40Z)`** — never a bare number.
    Four instruments (a `tail`, a line-match, a ref-count, and the glob that selects the files) gave four different
    answers for one log; only the last two paths together are the artifact.
  - **An instrument must PRINT THE WINDOW IT USED — the files it matched and how many.** The rule above says
    verify the glob; this is the way to make that verification automatic instead of a discipline someone has to
    remember. A tool that emits `scanned: 10 files (agent.log agent.log.1 agent.log.2 errors.log …)` makes its own
    blind spot self-evident on first use. **Build the self-report into the instrument and it stops mattering whether
    the next seat read the doc.** Any log/scan tool whose output does not name what it read is one silent omission
    away from a wrong answer that looks authoritative.
  - **Beware a metric whose error has a SIGN — a decaying count reads as improvement.** Measured 2026-09-28: a
    ref-count taken with `*.log` was 5x low on one seat and 0x low on another, because rotated files sit in
    `agent.log.1` (unreachable to `*.log`) — and gzipped files (`.gz`) are unreachable to *any* `*.log` at any time.
    So the same instrument read 73 today and **0 for the same events after rotation**, while the events were
    unchanged. **An undercount is stable and comparable; a decay is not comparable to itself and reads as a
    trend.** A multiplier can be corrected for — a decaying metric *rewards* the mistake, so the fifth run looks
    better on worse data. Prefer instruments whose output cannot improve as input decays.
  - **A provider fallback ladder can be exhausted END TO END — check every rung before calling the second one the
    fix.** Measured 2026-09-28: rung 1 hit an account quota, rung 2 was skipped (`credential pool is exhausted
    (every entry in cooldown)` — the skip is itself a cooldown cascade), and rung 3 failed for
    `Free model capacity exhausted`. **"Add a fallback" is not a remedy when one is configured and being skipped.**
    A stall with no rejection at the sender and no error at the receiver is the signature of a fully saturated
    ladder, not a transport fault.
  - **A tool's NEGATIVE answer is a fact about the tool, not about the world. Go look at the disk.** Measured
    2026-09-28: `ob sync --path <vault>` printed `No sync configuration found`, and two seats independently treated
    that as *"the exclusion config was removed / is not on disk"* — and reasoned onward from it for hours, including
    filing an open item saying the exclusion list *"cannot be checked, only guessed."* The config **was** on disk the
    whole time (596 bytes, readable) and its contents **overturned the conclusion built on its absence**. The command
    answered a narrower question than the one asked (it reported its own setup state, not the presence of a file).
    **`not found` from a wrapper is not `absent` from the filesystem.** Before reporting anything as missing or
    unreadable, `find`/`ls` for it directly, and quote the path — a negative from a convenience command has no
    standing as a fact about storage.
  - **When two careful people reach opposite conclusions from the same log, one of them is reading a different
    window, not a different log.** Preferred resolution order: (1) name the exact file(s) each read, (2) agree the
    unit of count (unique event id, never matching lines), (3) state the instant, (4) only then compare figures.
    Three disputes in one session — `8 vs 40`, `129 vs 70`, `448.9 MB vs 124.3 MB` — all resolved to a file-set or
    type-set difference, never to a disagreement about the underlying events. **The number was never in dispute; the
    instrument was.**
  - **There is no universal event identifier — every producer has its own, and assuming otherwise is the same bug
    one level up.** Measured 2026-09-28 across three providers in one fleet: **ollama-cloud** stamps a per-request
    `ref: <uuid>`; **opencode-go** stamps **no `ref`** but does carry `metadata.workspace` (`wrk_…`) and a
    `limitName`; **clawrouter** carries **no identifier at all** — message text and timestamp only. So a
    `ref`-based count silently omits **348 of 545** limit events fleet-wide (**64%**), and it would have done so
    with a perfect glob and a perfect window. **Three providers, three identity regimes.** Counting "the artifact's
    own id" is right; assuming the id has one format is the error underneath it. Enumerate per-producer identity and
    count each in its own terms; where no id exists, say so and label that class weakest rather than merging it.
  - **Whatever ENUMERATES the events must itself be data, or the tool inherits the bug it was built to catch.**
    A census built to fix a hardcoded glob shipped with a **hardcoded pattern list** for the ref-less class — so a
    third ref-less producer (`clawrouter`, 208 events, disjoint from the one it counted) was invisible to it. **The
    same defect, one level up, for the same reason, and invisible for the same reason.** A literal list of what to
    look for is a blind spot with a comment; make the class list configuration, so a new producer is a config line
    rather than a release.
  - **When a fix ships, check its blind spot at the class level, not just the instance level.** A tool can pass every
    case you hand it while omitting an entire category of input — verify by asking *"what KIND of thing could this
    not see?"* rather than *"are the numbers it printed correct?"* The ref-count above printed correct, reproducible,
    self-reported-window numbers and still missed two thirds of the fleet's events.

### A limit charged on ACCUMULATION cannot be explained by a ledger of the PRESENT

Measured 2026-09-28: a sync failed with `"Vault limit exceeded"` against a 1GB plan. Four independent
ledgers of the LOCAL vault were built (124MB, 148MB, 220MB, 2.5GB) and every one of them said it
FITS — so all four were right and none of them explained the failure. The limit was charged against
the REMOTE, which accumulates the current files **plus a version for every write plus a tombstone
for every delete**. A vault that churns hard can exceed a plan while its *present* content is a
fraction of it. **Before explaining a quota failure with a size, establish that your size measures
the same side of the wire, and the same moment, that the quota is charged on.**

- **The two biggest items on disk were both acquitted — and by DIFFERENT mechanisms.** One was
  disqualified by FILE CLASS (source extensions that are never uploadable); the other by the
  PER-FILE SIZE CAP (1,349MB of a 1.6G tree sat in 53 files above the 5MB threshold, so only 276MB
  was ever eligible). **A ledger alone acquits nothing: "it fits" is only a conclusion once you can
  name the filter that makes it fit.** Two filters agreeing on one conclusion is stronger evidence
  than either ledger, and neither was visible in the totals.
- **Apply every known gate before believing a payload size** — the class filter AND the per-file cap.
  A tree's on-disk size is not its uploadable size, and the gap is usually where the answer hides.
- **State the label.** "Candidate mechanism, not measurable now" is a finding; asserting the cause
  from a ledger that measures the other side is not.

### A GENERATED file is not a policy document — measure the tool's own readout

The same failure produced a config file read twice, nine minutes apart, with **different contents**
(596 bytes / ~10 entries, then 3,172 bytes / 63 entries). Both readers were correct and neither was
wrong about the world: **the sync client GENERATES that file on startup**, and the first read landed
before the client ran. 93% of the entries were auto-discovered caches, not authored policy.

- **Read the status command, not the config file.** `tool status` answers authoritatively; the
  config is an implementation detail the tool rewrites under the reader.
- **A generated artifact carries a time, and any conclusion drawn from it inherits that time.**
  Stamp the ledger with the artifact's generation time, and never compare a reading of a generated
  file against a failure from an earlier generation of it.
- **Corollary to "a tool's negative answer is a fact about the tool":** a tool's *positive* file
  contents are also a fact about the tool. What it materializes is a snapshot, not the policy.

### Counting across DESTINATIONS manufactures a number that is not an event count

Measured 2026-09-28: a rate-limit census reported one class at 140 and another at 208. Both were **line
counts, not event counts** — because the logger writes **the same event to both `agent.log*` and
`errors.log*`**, and the census's own contract (rotation-seeing, across all three log families) walked
into both. Proved by **set equality, not count equality**: `set(agent) == set(errors)` is TRUE, and a
single event was found verbatim in both files. **Equal counts can be coincidence; set equality cannot.**

- **Before summing across files, ask whether one is a MIRROR of another.** Two destinations with equal
  counts on every seat are one event written twice, not two sources agreeing.
- **A self-reported WINDOW is necessary and not sufficient.** The tool printed which files it matched —
  and a reader still cannot see, from a file list, that two of them mirror each other. **A window report
  gives the SCOPE, never the RELATIONSHIPS inside it.** Publish the relationships too, or dedupe.
- **The fix needs no event identifier.** The classes here had no ref — only "no id at all" — yet the
  duplication is exactly removable because **the two destinations emit byte-identical lines, so the
  LINE ITSELF is the key.** Never accept "this class has no identifier" as a reason the count cannot be
  tightened; check whether the text is stable, because a stable text IS an identifier.
- **Report the DECOMPOSITION, not a corrected total.** raw = distinct + destination mirror + relog.
  Measured fleet-wide: **raw 416 = 172 distinct + 150 mirror (~35%) + 94 relog (~22%)** — a raw count
  running ~2.4x the distinct-line count. The mirror held at 58–63% of the reduction on six of eight
  seat/class pairs, so it is a property of WHICH LOGGER writes, not of log levels: **measure it per
  class, never assume it.**
- **Prefer the tightest MEASURED figure to the loosest safe bound.** A floor of distinct seconds is
  true and collapses bursts — `raw 24 -> distinct lines 10 -> distinct seconds 3` on one seat — and it
  undercounts hardest during exactly the contention that causes the limits. **Name all three (floor,
  best estimate, artefact) rather than choosing one and hiding the others.**

### Check CONTAINMENT before summing over sub-patterns — a disjunction is a max, not a sum

Measured 2026-09-28: a census defined a class as `GoUsageLimitError|Go usage limit exceeded` — and the SECOND
pattern **contains** the first. Every line matching A also matched B, so the counter returned the larger branch
(208) rather than the sum, and the published total was **140 short of what a sum would have said and 108 over the
true distinct count.** Worse, both patterns had been reported as **two separate findings** in an earlier note, when
they were one counter and its subset.

- **Before summing over sub-patterns, test set containment.** `set(A) <= set(B)` — if true, `A|B` is a MAX and any
  total built from both branches is wrong by construction.
- **Two patterns is not two findings.** Reporting both as counts is inflation with a structural cause, and it is
  worse than a double-count because the numbers are individually defensible.
- **The tell: two unrelated classes landing on an EXACTLY equal total is not a coincidence, it is a
  wrong-subject read** — the same fingerprint as identical values across distinct subjects.
- **A class whose members are named in several ways needs ONE definition and a containment check**, not a union
  written by hand.

### Calibrate an estimator ladder against a TRUTH class before publishing a lead figure

Measured 2026-09-28: three estimators of one quantity were proposed — raw lines, distinct text lines, distinct
seconds — and the intuitive ranking was wrong. A class carrying **genuine per-event ids** supplied ground truth, so
the ladder could be **scored rather than argued**:

```
raw 1316  ->  distinct LINES 689 (3.04x truth)  ->  distinct SECONDS 223 (0.98x truth)  ->  TRUTH 227
```

- **The tighter estimator was the COUNTER-intuitive one.** Distinct text lines reads like a per-event count and is
  **structurally looser (3.0x)**, because **one episode is re-logged with VARYING text on each retry** — so
  text-lines counts retry variants while seconds groups them into the episode they were.
- **Text is not an event identifier when the text varies.** Before treating "identical text" as a key, verify the
  producer emits it identically for the same event — which must be measured per class, since one class may emit
  stable text and another may not.
- **A count that UNDER-reads truth is a FLOOR, not a ceiling, and floors are what a money decision wants.** A
  ceiling invites over-spend; a floor is the conservative direction. Name which one you are quoting.
- **A real defect's magnitude is STABLE under better instruments.** If every improvement in measurement shrinks the
  count, **what is moving is the measurement error** — and the finding that never budged is the real one. Three
  successive tightening steps in one night all reduced the number and none reduced the defect.
- **This is the opposite of a decaying count**: there, better instruments revealed MORE events; here they reveal
  FEWER, because the earlier figures were inflated by artefacts nobody had named yet.
- **Never assume a property generalises to a sibling class.** A mirror property held 4/4 for one class, 3/4 for
  another (one seat's lines never reached the second destination), and 0/4 for a third written by a single logger.
  **A property measured where it cannot hold is not evidence about the property.**
