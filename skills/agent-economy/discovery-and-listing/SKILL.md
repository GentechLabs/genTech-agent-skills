---
name: discovery-and-listing
description: "Use when a live agent service gets no traffic."
tags: [discovery, listing, x402, erc-8004, mcp, a2a, directories, reputation, distribution]
trigger: "When a live, working agent service still gets no traffic. When listing/submitting to a directory, marketplace, facilitator or registry. When a listing was accepted but nothing shows up. When asked 'why aren't we getting found?'"
version: 1.0.0
author: Gentech
---

# Discovery & Listing — getting noticed in the agent economy

Full playbook (layers, gates, validators, the surface registry and the funnel):
**`references/surface-registry.md`** — read it before submitting anywhere.

**The hard lesson, measured on ourselves:** a service can be completely built, correct, payable and
live — and still be invisible. Every surface has its own gate, the gates are unrelated to each other,
and each one fails silently. "We're not getting found" is almost never one bug; it is a stack of
unchecked ones.

## The layers, each with its own gate (all observed first-hand)

| Layer | What it gates | Real rules we hit |
|---|---|---|
| **Payment / facilitator** | whether a settle is accepted | Facilitators are per-protocol and differ. CDP: no gating on payer/payee being registered (they told us directly) — the trap is a **307 instead of 402**, i.e. the advertised resource URL must equal the route that challenges. OKX: rejects **multi-network `accepts[]`** and unknown extension blocks. Dexter: expects a different SDK envelope. |
| **Directory / registry** | whether you appear at all | 8004scan: card needs a top-level `type` and `services[].endpoint` (we shipped `url`, so their parser extracted **nothing** — 11 warnings, `services: null`). Re-parse is **owner-signed and cooldown-limited**, and derived fields come from a **separate scoring pass**. x402-list: graded compliance + an ownership proof file at a well-known path. GitHub-catalog PRs: a PR from an account invisible to logged-out readers **does not exist** to crawlers. |
| **Protocol** | whether an agent can call you | MCP (`tools/list` shape, POST JSON-RPC), A2A (`/.well-known/agent-card.json`), x402 (402 + `accepts[]`). Declaring a protocol you don't serve is a falsifiable claim in public metadata. |
| **Identity / reputation** | whether you get chosen | ERC-8004 registries. Score tracks **feedback count**, and feedback is written by real callers with a real client address. It cannot be self-manufactured. |

## The procedure — for ANY new surface

1. **Ask who the buyer is and how they search**, not how to list. Listing is not distribution.
2. **Probe the surface's own validator with the real artifact.** Never trust its docs; docs and
   validators disagree constantly. Submit the real thing and read the exact error.
3. **Capture the failure text verbatim** — it usually names the missing field (`Missing required
   field: type`, `Agent has no endpoints configured`).
4. **Fix the canonical artifact once**, regenerate every copy from it, and verify the **served bytes**
   (repo/vault/webroot drifting apart is normal).
5. **Write the gate into the surface registry as a test** so the next regression is caught by us, not
   by a reviewer.
6. **Probe before you declare.** Every capability in public metadata must answer 200 right now.

## The mistake to never repeat

Solving each surface ad hoc and then forgetting the rule. The expensive part is not the fix — it is
rediscovering the rule every time. **A surface without a recorded gate is a surface we will fail
again.**

## Funnel — measure discovery, not effort

`presence (listed?) → reachability (endpoint answers?) → discovery (do agents find us?) →
conversion (paid calls from non-us) → reputation (feedback)`

Be strict about "non-us": self-traffic inflates every stage above it. A successful submit is not a
successful listing — refresh accepted ≠ re-parsed ≠ fields populated ≠ ranked. Verify each hop
separately.
