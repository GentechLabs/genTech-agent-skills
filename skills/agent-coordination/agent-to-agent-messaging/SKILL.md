---
name: agent-to-agent-messaging
description: "Use when one agent must reach another agent — pick the path, prove it landed, and never report a wake that never happened. Covers peer DM, peer run, the vault handoff, and the local twin."
category: agent-coordination
version: 1.1.0
author: Gentech
tags: [communication, agents, peer, handoff, mesh, fleet]
related_skills:
  - group-handoff-mesh
  - handoff-mesh
  - fleet-consult
---

# Reaching another agent

**One rule above all: the vault is the RECORD, a message channel is only a WAKE — and a wake that
never landed must never be reported as a wake.** A DM that failed silently is worse than no DM,
because the sender believes the work moved.

## The four paths

| path | what it is | use it for |
|---|---|---|
| `hermes peer dm <peer>[/<seat>] "<msg>"` | cross-machine delivery into the target's canonical chat; **blocks** for the reply | a quick answer, a checkpoint before a restart |
| `hermes peer run <peer> --idempotency-key <key>` | fire-and-forget; returns `run_<id>` immediately, stable key makes a retry a no-op | long work you must not block on |
| `01-HANDOFFS/<from>-to-<to>/<YYYY-MM-DD>.md` | durable, survives a machine being off, read by the digest/scanner | **everything that matters** |
| `hermes -p <profile> chat --query-file <f> --oneshot` | the **local twin** — runs a real turn as that seat on this box | the peer path is dark |

## Step 0 — MEASURE the path before you rely on it

A peer DM fails in two very different ways and they look nothing alike: the peer *refusing* (you get
a reply) and **nothing listening at all** (an instant `[Errno 111] Connection refused`). Only the
first is information.

```bash
ss -ltnp | grep -E ':(864[0-9])'          # any listener at all?
hermes peer list                            # what URL + port are registered?
```

**Nothing listening is NOT the peer refusing, and it is NOT "the agent is busy".** Do not retry, do
not read silence as consent, and do not let a restart depend on an ACK that could never have arrived.

Measured state, re-measure it rather than trusting this line: after the multiplex convergence (one
gateway process serves every profile) the four per-profile api_servers are **gone** — `:8642`–`:8645`
refuse instantly — because a secondary profile never gets its own `api_server`; the default's adapter
is what serves `/p/<profile>/` **mirrors**. Repair = one bind on the default profile + per-seat peer
URLs + **per-seat keys**, and it is **gateway-affecting: checkpoint ACKs from every VPS seat first**.
Never take it alone.

## Step 1 — write the durable copy FIRST, then wake

Vault note first (the source of truth), wake second. If the wake dies, the record survives; if the
machine was off, the note is still there in the morning.

## Step 2 — wake, and read the RESULT, not the return code

- `peer dm` prints the peer's reply. An instant connection error = **failed wake**.
- `peer run` returns an id that must be polled to completion; "started" is not "delivered".
- The local twin prints the seat's turn. **It can be interrupted mid-turn** — if it stops partway,
  whatever it had already written to disk is real and anything it had not finished is not. Say so.

## Step 3 — PROVE the message landed in the target's own artefacts

Not by assuming the channel worked. Look for: a reply note in your lane, a file the target touched,
a session/transcript entry. **If nothing shows, the honest statement is "the wake failed"** — never
"they have been notified".

## Step 4 — record it, including the failure

In the return note: what was sent, by which path, whether it landed, and the error **verbatim** when
it did not. The next reader must be able to tell a delivered message from an attempted one.

## When a path is DOWN — the fleet fallback (adopted 2026-09-30)

A single channel must never be the failure point. **The vault handoff is the delivery; the DM is only
the accelerator.** When Step 0 shows the wake path is dark, the sender still:

1. **files the vault handoff** — the record is written regardless of whether a channel exists;
2. **states in the record that the wake FAILED** — the error verbatim, never "they were notified";
3. **does NOT wait** — no blocking on a channel that cannot answer.

**A restart never *gates* on a channel that cannot answer — but a dark channel is NOT consent.** The
gate is failed *to the seat that owns it* (Jordan), never read as an ACK. **Gating ≠ proceeding.** An
ACK that could not have arrived must not be waited for **and must not be assumed** — those are two
different mistakes and both are forbidden.

> Boundary this rule must NOT be allowed to mean: *"dark channel ⇒ proceed."* It never does. A
> measured-dark path escalates; it does not authorise.

## Related rules that bite here

- **A peer's claim is a claim.** Verify what they report before relaying it (`verify-after-every-action`).
  Asking for something and receiving an answer is not the same as the answer being true.
- **A peer's report on work you originated is a continuation, not a new ask** (`group-handoff-mesh`).
- **`peer dm` blocks until the reply** — never put it on a path that can hang a session you need.
- **Never leave another seat's in-flight edits to rot**: if their turn was interrupted, their
  uncommitted files are theirs. Do not commit them for them; name the state instead.
