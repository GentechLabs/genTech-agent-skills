# Multi-target sync: why every audit reads green across a real loss

Case type: a shared source of truth is propagated to N replicas (fleet seats, environments, hosts) by
a sync that replaces any replica whose content differs.

## The mechanism

On any difference the sync `rmtree`s the receiver's copy and `copytree`s the source over it. Correct
for propagation, destructive for a receiver-only edit — and the receiver is where people naturally
write, because that is the copy the running system actually reads.

## Blind-spot map

| Audit | Compares | What it cannot see |
|---|---|---|
| sync `--check` | receiver vs source | runs AFTER a replace — nothing left to differ, so it says "no drift" |
| divergence audit | receiver vs receiver | a loss confined to ONE receiver has no witness to disagree with it |
| upstream audit | upstream vs receiver | clean whenever upstream was not involved |

A loss with no second witness is invisible to all three. **Three greens is not three independent
confirmations when all three are blind in the same direction.**

## Attributing a disappearance: the controlled experiment

To decide whether content vanished because a program replaced it (or a person removed it, or a merge
moved it), run one controlled experiment rather than arguing from correlation:

1. In the **same session**, make an edit to the *durable* location (the source, not the copy) of a
   **different** artifact. Leave it in place.
2. Compare outcomes. Exactly one variable differs — which side got the edit.
   - source-side edit **survives** → the source is durable; the mechanism is the overwrite
   - copy-side edit **gone** → the copy is not a durable home
3. Corroborate with `mtime`: a receiver file whose mtime falls inside the window of a **source-only**
   commit is strong evidence of a replace rather than a merge.
4. Check that commit is a **pure addition** (`+N / -0`) carrying none of the missing content — that
   rules out "it was merged elsewhere" and leaves the overwrite as the only explanation.

This converts "the content disappeared and I think I know why" into a reproduction a reviewer can
re-run.

## Where to write, and why the rule alone was not enough

The rule "edit the durable source, never the replica" was already documented and still failed, because
nothing detected the violation. Enforcement beats documentation:

- add the receiver-vs-source comparison helper (see SKILL.md rule 2) and call it on every acting path
- make the warning name the files and point at the durable location
- ship the both-ways test, and a control proving silence

## Recovery

1. Put the lost content into the **durable source**, not back into the replica.
2. Run the propagation, then confirm byte-identity: one hash across the source and every replica
   (one md5, N paths — a single value, not N values to eyeball).
3. Re-run the guard's test and every audit in the blind-spot map.
4. Note in the report which audits were blind, so the next reader does not treat their green as
   evidence.
