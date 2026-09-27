# The Layer System: Detecting vs SELECTING a Posture

The treasury's strategy directive, the layers that feed it, and the architectural gap that stops the
system acting on all of them at once.

Full ratified spec: `<vault>/03-Strategies/agentic-yield-and-trade.md` ("AYT").

---

## The standing directive (user's words, the prime constraints)

> **Fee efficiency is number one. Market sentiment is very important. There is no wrong answer.**

Read precisely — these are the two governing constraints, not a preference ranking:

1. **Fee efficiency is the PRIME directive.** Every posture is ultimately judged on whether it earns.
   A posture that scores well on sentiment but earns nothing has failed.
2. **Sentiment/market read is the FIRST INPUT** — it is what selects *which* posture, not a tiebreak.
3. **"No wrong answer" means: no single layer is authoritative on its own.** Every layer is allowed to
   dissent, and the answer is the combination. It does NOT mean any answer is acceptable.
4. **Flexibility and creativity are the point** — combining strategies, leaving the pool when a
   pullback is spiking, re-entering after. The directive is explicitly for a system that *chooses*.

**Protection outranks opportunity.** A risk/protection layer's veto beats a yield layer's
recommendation. Without this ordering, "combine all the layers" degenerates into taking the most
aggressive read available.

---

## The layers

Each layer answers a different question and is read INDEPENDENTLY:

| Layer | Question it answers |
|---|---|
| **Protection** | is there a move that no legal band survives? |
| **Yield / efficiency** | is the current book earning, and is it placed where it was built to earn? |
| **Market read (regime)** | chop, trend, or contracting — what weather is this? |
| **Sentiment / macro** | is a scheduled or structural event about to move the tape? |
| **Venue compatibility** | can this shape/rail even be expressed where the capital sits? |
| **Hold vs farm** | does the position beat simply holding the asset? |

---

## The posture vocabulary must be FINITE and enumerated

A decision layer that can emit free text cannot be tested, logged, or reasoned about. Enumerate the
outputs, and keep the set small enough that every one has a defined entry and exit:

```
FLAT · HOLD · FARM_CURVE · FARM_BIDASK · SKEW_CURVE · SPOT · LADDER_IN · EXIT_TO_STABLE
```

Two rules that make an enumerated posture usable:

- **Every posture names the layer that set it.** "FARM_BIDASK (set by: market read)" is auditable;
  a bare posture is not. The first question asked of any posture is *which layer decided this*.
- **Every posture has an exit condition** expressed in the same currency the layer reads. A posture
  with no exit is a trap, not a decision.

---

## The gap: the layers DETECT but do not SELECT

This is the defect the directive is really pointing at, and it is structural:

- The efficiency trigger can compute an alternative shape's score — and then **re-deploys the same
  shape**. It *reports* a finding it cannot act on.
- The macro layer holds a calendar of scheduled events but has **no automatic switch** on it.
- There is **no posture vocabulary in the code at all** — several independent triggers, each with its
  own authority, and no component that decides between them.

**Consequence:** a risk/exit rule can be fully written in the doctrine and entirely absent from the
running system — the written-down-dead class. Verify each doctrine rule has a live caller before
claiming the system implements it.

**The fix, in one line:** one component reads every layer and emits **ONE** posture, naming which
layer set it. Each existing trigger stops being an independent actor and becomes an **INPUT** to that
single decision. Nothing else about them needs to change.

That is what "respond using all the layers" requires. Adding a seventh detector does not move it.

---

## Implementation shape: ONE gather, ONE pure resolver

Split the component in two, and the split is what makes the precedence rules testable:

- **`gather()` does every live read**, and seals each layer as `{readable: bool, error: <cause>}`. A
  layer that cannot be read comes back with its REASON attached, never as a bare null and never as a
  default.
- **`resolve(layers)` is PURE** — readings in as DATA, one posture out. No clock, no network, no I/O.
  This is the whole point: precedence is where the bugs live, and a pure resolver can be exercised in a
  loop (a `--selftest` over synthetic layer sets) instead of only against whatever the market happens
  to be doing. A decision layer you can only observe live is a decision layer whose precedence rules
  are untested.

**An unreadable layer must ABSTAIN — it must not vote.** The failure this prevents is subtle: a
function taking optional readings will substitute the read it *can* make for the one it cannot, so a
missing input **changes which branch of the decision runs**. Order the branches so a missing input can
never select the permissive one, give the decision an explicit abstain posture (`HOLD_SHAPE` / *keep
what we hold*), and make 
"I could not read layer X" a first-class output. An abstained layer is not a neutral layer — treating
"could not read" as "no objection" is exactly how an unmeasured input gets outvoted by a default.

**Report abstentions even when the outcome is confident.** A posture that does not name its
abstentions reads as unanimous, and a layer that is quietly missing is indistinguishable from a layer
that agreed.

**Judge each layer's score against the shape the CHAIN holds, not the shape the layer wants.** A score
is only meaningful against the geometry that produced it, so a layer evaluating "would a curve read
better" is computing a number about a book that does not exist. Same for the resolver: it decides, and
the geometry that follows from the decision is reported BESIDE the posture — the bin count is a
CONSEQUENCE of the posture, not an independent input to it.

**A pivot is not a re-centre.** The efficiency rule has two distinct actions and conflating them is a
defect: re-centre keeps the shape and moves it; **pivot changes the shape.** Emit them as different
outcomes (`pivot` vs `re_centre_first`) so the resolver can order them differently — protection and
pivot outrank a re-centre, and a re-centre of the wrong shape is wasted work.

## Pitfalls

- **Do not implement the directive as another trigger.** More detectors widen the gap; the missing
  piece is the arbitration between them. The deliverable is the decision component, not a new rule.
- **A decision layer that is BUILT but not wired changes nothing.** Reading and deciding are not
  acting: the resolver can be complete, self-tested, and reporting correctly while the older triggers
  still perform every state change. Say plainly which half is live, and treat wiring the decision into
  the actuator as its own step — it can reshape a live book, which is a capital action.
- **Do not let "no wrong answer" become "no decision."** The user means every layer may dissent and
  the combination decides — not that the system may stall or default. Ambiguity resolves to a posture.
- **A geometry score is not a yield reading and cannot select a posture by itself.** See the
  efficiency-score section of the parent skill: the score reports placement, not earnings, and it
  cannot be improved by acting on it.
- **An exit rule the doctrine already contains is still not implemented.** Search the code for a live
  caller before reporting the capability as present.
