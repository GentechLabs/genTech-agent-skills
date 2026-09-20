---
name: dev-vs-invest
version: 1.0
author: Gentech AI
class: defi
description: Separate whether a chain or token is good to BUILD on from whether it is good to HOLD. Developers fuse these two questions by default, which is how you buy a chain because its docs are nice. ALGO is the canonical case: cheap and pleasant to build on, paying nothing to hold.
---

# DEV vs INVEST — Two Axes, Never One

## The trap this skill exists to break

**You are a developer. So the question "is this chain good?" feels like one question.**

It is two, and they have different inputs and different answers:

- **DEV** — can I *build* here? Cost to transact, tooling, ecosystem depth, composability, docs.
- **INVEST** — does *holding* this pay? Price trend, measured yield, liquidity to exit.

**Judging one by the other is how you buy a chain because its docs are nice, or dismiss one because its chart is ugly.** Both are the same error: answering a question nobody asked.

## The canonical case

**Algorand.** Clean tech, fast finality, quantum-resistant narrative, pleasant SDKs. **Good to build on.**

**As a holding: 7 pools existed in a 16,763-pool universe. Largest was $16.4M paying 0.00%. Native staking ~4.87% gated behind a 30,000 ALGO minimum (~$2,937 at the time) — a floor our treasury could not clear.**

**Verdict: BUILD YES / HOLD NO.** That is not a contradiction. It is the correct answer to two different questions.

## How to measure each

**DEV — measurable, not vibes:**
| Input | How |
|---|---|
| Cost to transact | Send a real tx; read the receipt. Never quote a headline. |
| Ecosystem depth | TVL, protocol count, *distinct* pools (not pool names) |
| Composability | Can you call the contracts you need from one tx path? |
| Tooling | SDKs, explorers, RPC reliability |

**INVEST — also measurable:**
| Input | How |
|---|---|
| Trend | Multi-window returns (30d/90d), from a *paged* candle source |
| Yield | Measured over a window, FEE SEPARATED FROM EMISSIONS |
| Exit | **24h volume and pool depth at YOUR size** — see below |

## The liquidity rule that makes "hot" meaningless without it

**Beta needs liquidity to transmit.** When capital rotates, it can only enter markets deep enough to receive it. **In a thin market the rotation gaps the price — that is noise, not signal-following.**

Measured example: as AVAX ran +18%, a memecoin paired to it rose **+11.82%** — a beta of **0.95**, *lagging* its own quote currency on every horizon. **The majors (ETH 1.30, SOL 1.31 vs BTC) amplify because rotation reaches them; a $50K/day market cannot receive a rotation at all.**

**So: "hot" is not a property of a token. It is a property of the token AND its market depth together.**

## The rules

1. **Never answer "should I hold this" with evidence about building on it.** Different question.
2. **Quote the fee core, not the emissions headline.** A pool paying in its own token pays you in the thing you are trying to leave.
3. **Check exit liquidity at your size before entry.** A position you cannot leave is not a position.
4. **A disagreement between the axes is a RESULT, not an error.** Report it; do not average it away.
5. **A missing measurement is UNKNOWN — never render it as zero or as a decline.** `(value or 0) > 0` turns "no data" into "down". Label it UNKNOWN.

## Checklist before capital moves

- [ ] DEV verdict stated separately from INVEST verdict
- [ ] Yield measured over a window, fees and emissions separated
- [ ] Exit liquidity checked against position size
- [ ] Any missing input explicitly labelled UNKNOWN
- [ ] If the axes disagree, that is written down — not smoothed over
