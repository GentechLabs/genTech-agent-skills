# Pitfalls — the develop-and-verify ledger (INDEX)

Split into parts **2026-09-28** when the single file reached 93,842 chars against the platform's **100,000-char
per-file** cap. **Items were MOVED WHOLE, never rewritten**, so every item still carries its own provenance line.

## Parts — counts and digests read at 14:27:12Z

| part | items | chars | md5 |
|---|---|---|---|
| `references/pitfalls-1.md` | 60 | 32,298 | `68ac26e76875b784d757a50bebe2162d` |
| `references/pitfalls-2.md` | 52 | 31,686 | `cd09593a676bb3b32faf4e5073f7951f` |
| `references/pitfalls-3.md` | 58 | 56,302 | `7ada03e776fe019e05c3763bff5b21be` |

**`references/pitfalls-3.md` is the LIVE part** — new lessons append there. When it approaches the cap, freeze it and
open part 4 the same way (whole items, never a rewrite). The single pre-split file is kept at
`references/pitfalls.md.pre-split` as the immutable record of what the parts were moved from.

## Provenance check — re-run this after ANY extraction and compare

**The rule is stated because a number published for comparison without the pattern that produced it cannot be
compared.**

> **RULE: lines beginning `- **` whose text CONTAINS `<seat>`, CASE-SENSITIVE, over the part files.**

```
BASELINE (the single file, read 2026-09-28, md5 6ef72284d4ca9c6689125569f05a2e99, 143 items, 93,842 chars):
    pixel 18 · gentech 18 · labs 3 · treasury 2 · gizmo 1
AT THE SPLIT (22:03:19Z) — the same rule over pitfalls-1/2/3 reproduced the baseline EXACTLY:
    pixel 18 · gentech 18 · labs 3 · treasury 2 · gizmo 1      <- the equality test, and it PASSED
SINCE THE SPLIT lessons have been appended to the LIVE part, so totals GROW — that is growth, not a rewrite:
    pixel 35 · gentech 29 · labs 4 · treasury 7 · gizmo 2      (read 14:27:12Z)
```

**HOW TO USE THIS: the equality to check is the one measured AT THE MOMENT OF AN EXTRACTION — recount every item before and after the
move and every number must be identical. A later total that is HIGHER is growth (new lessons), not damage; what would indicate a
rewrite is a number that moves with no items added, or an item count that does not match the parts.**

**A check that cannot fail is worse than no check, because it spends the trust the real finding will need.**
