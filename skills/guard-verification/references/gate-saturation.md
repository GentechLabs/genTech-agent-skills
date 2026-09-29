# Gate-Saturation Verification

Fleet write gates (GitHub, Obsidian sync, etc.) throttle pushes to a fixed rate. When a push
returns `deferred`, the gate is doing its job, not failing.

## Procedure

1. **Stop retrying in a tight loop.** Every `deferred` response still consumes gate budget and delays
the drain. Three attempts spaced by the declared minimum are enough to confirm saturation.

2. **Treat committed local HEAD as source of truth while the gate is shut.** A successful `git commit`
is a real state change. The work is not lost; it is held.

3. **Verify the drain path.** Check that the drain cron or deferred-push job is enabled and its last
run is `ok`. If it is not, the held commits are at risk and should be reported as a separate blocker.

4. **Before declaring "pushed", confirm remote HEAD matches local HEAD.** If they differ, state
honestly: how many commits are held, which drain job is expected to carry them, and the last
measured status.

5. **Never let a green local suite substitute for a verified remote landing when other seats must
read the artifact.** A passing test on local HEAD is evidence the commit is good; it is not evidence
the fleet has it.

## Pitfalls

- **Retrying a deferred push until it succeeds burns the window that would have let the drain succeed.**
Stop at three spaced attempts.
- **Claiming "pushed" because the commit exists locally misrepresents the state to other seats.**
- **A drain job with `last=ok` but an old timestamp may be stuck silent.** Verify by comparing the
remote HEAD to local HEAD, not by reading the job's last status field alone.

## Verification

- [ ] Local commit verified (`git log -1`, files in HEAD).
- [ ] Three spaced push attempts all returned `deferred`.
- [ ] Drain job enabled and last run `ok` (or reported as blocker).
- [ ] Remote HEAD checked and mismatch count stated.
- [ ] Reply to peer notes the held commits, not just the local work.
