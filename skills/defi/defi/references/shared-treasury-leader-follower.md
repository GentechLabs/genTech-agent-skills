# Shared Treasury / Leader-Follower

One operator's treasury can follow another's STRATEGY directives when they are in the same LP. The
leader decides shape, ratio and geometry; the follower's treasury resolves that policy locally,
never executes the leader's capital actions.

## Why this is correct, not merely social

A shape/ratio directive is transferable because it is a **pool property**, not an account property.
The two books are on the same pair, the same bin step, and the same fee tier, so the question *"what
shape fits this chop?"* has the same answer for both. A directive that crosses does not carry any
opinion about either wallet's size, cash needs, or risk budget.

## What CAN be followed (pool policy)

- `shape` — curve, bid-ask, spot, or another supported shape
- `ratio` — token/stable split, e.g. 0.40 stable weight
- `geometry` — the same geometry label (curve, bid-ask, etc.)

These are the only fields a follower may import.

## What MUST NEVER be followed (account-local)

- withdraw, exit, send, or any movement of capital
- the churn cap
- the gas floor and the gas float
- bill pulls and reimbursements
- any absolute dollar amount

The reason is size. If one book is $248 and the other is $39, an action proportionate for the leader
may be ruinously expensive for the follower. **The leader's instruction is a policy the follower
resolves, never an order it executes.**

## Consent record

A follow relation must be recorded on the follower's tenant record with:

| Field | Meaning |
|---|---|
| `follow` | the leader tenant name |
| `follow_consent` | `true` |
| `follow_consent_at` | ISO-8601 date |
| `follow_scope` | human-readable scope: pool properties only, never capital actions |

If `follow_consent` is missing, the resolver refuses to inherit with a loud message. Consent can be
revoked at any time by removing the `follow` field.

## Resolution order

1. Tenant's own directive (operator pin)
2. Leader's directive (only if consent is recorded)
3. The autonomous regime map
4. The machine's direct market read

A tenant's own pin beats the leader. The leader beats the regime map.

## Inheritance must be printed

Every pass must state whose strategy is in force. Example:

```
dadrian   shape curve · ratio 0.4 · geometry curve
          source: INHERITED from jordan (leader; consent on record)
```

An instruction silently inherited is not an instruction.

## Verification

Run the resolver:

```bash
python3 steward_directive.py --tenant <follower>
```

Expected: the follower's strategy, the leader's name, and a consent note.

## Safety boundaries

- If a followed shape change would cost a cycle the follower's churn cap forbids, the follower waits
  and says so. The leader's intent does not override the follower's budget.
- If the leader has no active directive, the follower falls through to the regime map and reports
  "leader has no directive right now."
- A missing or malformed leader directive must be reported; it must not silently clear the follow
  relation.

## Gamification warning

A future social-trading scoreboard must score **discipline**, not headline APY. Reward fewer
unnecessary rebuilds, lower gas per dollar earned, more days in range, and measured income. Scoring
on APY would reward the exact churn behaviour that a leader-follower system is meant to prevent.

## Implementation reference

- `steward_directive.py` — the resolver that returns `(fields, source, note)`
- `tenants.json` — the consent record lives on the follower tenant
- `operator-shape-directive.md` — the leader's own directive format
