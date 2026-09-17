Drift-guard working set — shared classes and their ground truth.

## Cron-invoked scripts: what a deployable entry point looks like
- The scheduler resolves each job's script real path and refuses any job whose real path leaves the profile's scripts dir. A vault-symlinked entry point for a cron script is silently never scheduled. Deployed entry points for cron scripts must be a regular-file COPY inside the profile's scripts dir (not a symlink). Same rule for port monitors or anything cron runs.
- When a guard cracks down on entry-point copies violating that, an earlier fix may become invalid — reconcile by reading the cron code, not guessing.

## Served page/asset verification
- Verify as a logged-out visitor: probe anonymously with a browser UA; the auth/anon split is the decisive test for visibility classes (dead assets, private repos, invisible issues).
- Own-domain assets on hub pages can be silently 404 to anon users while the page looks fine to a logged-in maintainer. Probe ALL served pages' image/iframe/audio/hard-coded URLs, not just the ones in the report.
- A served .json can still fail to parse (merge-conflict markers committed by accident). Treat parse failure as distinct from 404, and sweep for other files that apparently exist but will not parse.
- Store live-tree candidates for every asset and pick one by probing for the first that answers 200 — never trust a stored/previous value that has not been probed.
- Validate the whole page, not just the asset being fixed: a guard that checks only "did image resolve" misses contact/homepage and non-service URLs.
- A substring match can false-positive ("gentechlabs.net/v1" matches "api.gentechlabs.net/v1") — validate with an anchored check before reporting counts.

## Falsifiability
- Add assertions as falsifiable both ways: prove it FIRES by staging an obviously bad state, then RESTORE and prove it goes clean. Record the proof so the next reader knows the guard can be trusted.
- If an installed fix changes how the scheduler executes scripts, run the cron-script-path check immediately after; a fix may break its own scheduler entry.