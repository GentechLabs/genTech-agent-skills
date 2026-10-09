# Regulatory Intelligence → Treasury Action Translation

A regulatory feed is only useful if the operator can answer one question from it: **can we do anything differently because of this?** This reference gives the four-label taxonomy and the plain-language flow for converting SEC / CFTC / agency rulemaking into a treasury decision.

## The four labels

Every item gets exactly one label. The label goes FIRST, before any detail.

| Label | Meaning | Example trigger |
|---|---|---|
| **NOTHING** | Touches nothing we hold, route through, or build. | An exchange's internal SRO rule, an options listing on a BTC ETF, an enforcement action against a party we do not use. |
| **BUILD** | Changes what we are ALLOWED to build or ship. | A custody rule that affects how an agentic treasury holds keys; a token-registration requirement for a feature. |
| **RAIL** | Changes WHICH venue or rail we should prefer. | A venue loses a surveillance-sharing agreement; a new clearing rule makes one rail cheaper or riskier than another. |
| **WINDOW** | Opens a clock: something must be done by a date or it lapses by default. | A comment window closing on a proposed rule that would touch our rails; a registration deadline. |

## The top-line rule

If every item is **NOTHING**, say so at the top in one sentence:

> Nothing today reaches us — here is the pattern worth knowing.

Then report the pattern: a repeated shape (e.g. "size + surveillance connectivity as a membership test"), how many times it has appeared, and what it means for future rail selection. The pattern is often more valuable than the item.

## The plain-language constraint

- No section numbers, no statute names, no agency jargon in the answer.
- Define any unavoidable term in the same line.
- Write it as if explaining on the phone to the person who owns the money.
- State which assets / rails / venues are named and which are not. "AVAX, WAVAX, USDC, LFJ, SOL: zero occurrences" is a useful sentence.

## Process precision

- **Proposal ≠ rule ≠ law.** Never upgrade an item's status.
- **Effective immediately** is different from **open for comment** — say which.
- A final rule with no comment window belongs under "WHERE IT SITS IN THE PROCESS"; do not place it on a comment-window board.

## Ownership

Only if the label is **BUILD**, **RAIL**, or **WINDOW** include a "WHAT WE'D DO ABOUT IT" section with one concrete next action and who owns it (Jordan or the treasury). If **NOTHING**, skip this section entirely. Do not invent work.

## Why this matters for DeFi treasuries

Regulatory risk to a user of concentrated-liquidity pools travels through **where we route**, not through what we hold. A rule that sets a $700M liquidity floor and a surveillance-sharing requirement is a test a venue passes. Our exposure is the venue's qualification, not the asset's registration status. That reframes the watch from "is crypto allowed?" to "does our rail still qualify under the membership shape?"
