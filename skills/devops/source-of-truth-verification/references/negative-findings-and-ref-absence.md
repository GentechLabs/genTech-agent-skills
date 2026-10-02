# Negative Findings and Ref Absence

**What this is:** rules for proving that something is *missing* or *absent* without overclaiming,
and for distinguishing the several ways a git ref or object can fail to resolve.

## "Absent from this tree" is not "absent from everywhere"

A negative finding is a claim like any other. Before reporting a capability as missing,
unsupported, or broken, say where you looked and what the scope of the claim is.

| What you can honestly say | What you checked |
|---|---|
| "Not in this clone" | `git ls-tree -r HEAD --name-only`, `git cat-file -e <obj>` |
| "Not on the remote branches I can see" | `git ls-remote --heads <remote>` after a fresh fetch |
| "Not a valid object name in this clone" | `git rev-parse --verify <ref>` and `git cat-file -e <sha>` |
| "Does not exist" | All of the above, plus any other clone the fleet is known to read |

**Never drop the scope.** A file missing from your checkout may be present in a peer's branch; a
ref missing from the shared clone may exist in another agent's working clone. Unqualified
negatives make other people chase defects that don't exist.

## A git ref can be missing in more than one way — and the diagnostics differ

When `git merge-base --is-ancestor <ref> HEAD` returns non-zero, the exit code alone does not tell
you whether the ref is **diverged** or **unresolvable**. Distinguish them before interpreting:

```bash
# rc=0  -> ref is an ancestor of HEAD (fast-forward safe)
# rc=1  -> ref exists but is NOT an ancestor of HEAD (diverged / behind / would need force)
# rc=128 -> ref does NOT resolve to any object in this clone (missing ref, typo, or object absent)

git merge-base --is-ancestor <ref> HEAD; echo "rc=$?"
git rev-parse --verify <ref> >/dev/null 2>&1; echo "resolves=$?"
```

A script that treats rc=128 as rc=1 will call a missing ref a "non-fast-forward" and tell the user
to investigate an alarm that is not an alarm. Conversely, a script that treats rc=1 as rc=128 will
silently try to create a ref that already exists and diverges.

**Rule:** always run `rev-parse --verify` before `merge-base --is-ancestor` when the ref's existence
is not guaranteed. Branch on the resolved outcome:

- **Ref does not resolve** → the artifact is absent; report absence with scope, not divergence.
- **Ref resolves and is ancestor** → healthy baseline.
- **Ref resolves and is NOT ancestor** → genuine divergence; only then discuss force/reset.

## A remote baseline ref that exists in only one clone is not off-box

An "off-box backup" or "fleet baseline" must be readable from more than one seat. If a ref is named
in a commit or handoff but cannot be found via `git ls-remote` or the shared clone, the only places
left are untracked local copies. That is not a baseline — it is a local branch with a fancy name.

Before treating such a ref as authoritative:

1. `git ls-remote --heads <remote> 'refs/heads/<prefix>*'` — is it on the remote at all?
2. `git rev-parse --verify <ref>` in the shared clone — can every seat see it?
3. `git cat-file -e <stated-tip>` — does the stated tip even exist as an object here?

If all three are negative, report: "ref X is not readable from any shared location; if it exists, it
is only in your working clone." Do not create a new baseline to quiet the alarm unless you own the
artifact and the rule permits it.

## Don't create a baseline to quiet an ownership-unresolved alarm

If an artifact is recorded as owned by someone else (e.g. "Jordan's, never force") and the existing
ref is absent, creating a fresh ref makes the failure metric go green without resolving who owns it
or whether the old one is recoverable. That is compensation, not a fix.

**Rule:** capability to create the ref is not permission to create it. Verify the dry-run gate is
open, report that it is open, and hand the decision to the owner named in the record.

## Probes

```bash
# Does the remote have any ref matching this prefix?
git ls-remote --heads <remote> 'refs/heads/<prefix>*'

# Does the ref resolve locally?
git rev-parse --verify <ref> >/dev/null 2>&1 && echo exists || echo missing

# Does the stated tip exist as an object?
git cat-file -e <sha> 2>/dev/null && echo object-present || echo object-absent

# Is it an ancestor of HEAD?
git merge-base --is-ancestor <ref> HEAD; echo "rc=$?"
```
