# Infra-to-Infra Partnership: "Same Rails, Different Layer" (Brickken, Aug 4 2026)

## Context
Jordan shared an RWA market recap post that named Brickken (tokenization infrastructure).
Past research (June 9) had already established Brickken is NOT a competitor — they issue/
tokenize assets; Gentech moves the money (x402 rail + ERC-8004 identity). Same primitives,
different layer.

## The discovery that unlocked the pitch
Brickken's own agentic stack runs on the EXACT primitives we build on. From their Q2 2026
recap and Base MCP post:

> **CLI → x402 → ERC-8004 → Token Deploy**
> A developer, or an AI agent itself, can install the CLI, pay for Brickken API calls
> through x402, register an on-chain identity through ERC-8004, and deploy a compliant
> token directly from the terminal.

Their Base MCP (mcp.brickken.com) explicitly invites agent developers to "point an agent
at it and share what you build." This is the wedge: they are courting exactly the profile
Gentech is.

## "Same rails, different layer" positioning
This is the strongest infra-to-infra framing — not "we're complementary in theory," but
"we are already two nodes on the same stack":

- **Gentech → Brickken:** a live x402 payment-gateway partner (13 revenue-capable x402
  services) that proves their x402 payment layer end-to-end with real traffic; an
  ERC-8004-native agent that can run a compliant token through their Base MCP as a
  reference deployment.
- **Brickken → Gentech:** institutional-grade tokenization access (ERC-7943 Final,
  RAMS/ERC-8226, ISO 27001/27701/27018), a regulated-asset pipeline (DTCC pilot,
  BlackRock BUIDL, 150+ clients, $660M+).
- **Standards handshake:** Brickken's RAMS (ERC-8226) was explicitly built to work with
  ERC-8004 (our agent identity). A joint demo of agent identity (us) + compliance
  mandate (Brickken) + payment (us) is a first-mover story.

**One-line pitch:** "Brickken tokenizes the asset. Gentech moves the money on it — we're
already on the same identity + payment rails."

## Three-in-one outreach strategy (Jordan's directive)
Run three angles CONCURRENTLY, each de-risking the others. This is better than a single
channel because it covers decision-makers at every level of the org:

1. **X DM** (@Brickken) — short, direct, points to live stack + shared rails. Sent by
   Jordan from his own handle.
2. **Partner application** — Certified Partner Program
   (landing.brickken.com/webinar-brickken-certified-partner-program) — the formal door:
   badge, warm intros, dedicated account manager. Driven by Jordan.
3. **Cold email** — full pitch to `sales@brickken.com` (primary) cc `tech@brickken.com`
   (integration/tech angle). Covers reference deployment + payment-gateway integration +
   standards handshake.

**Why DM goes through the human:** xurl OAuth is not authenticated on the VPS and must
never be set up with secrets in an agent session. The DM is Jordan's channel; the agent
preps the email + prospect file.

## Contact map (Brickken-specific)
- sales@brickken.com — partnership/sales (primary)
- tech@brickken.com — technical/security/integration reports (cc on infra partnerships)
- support@brickken.com — general support (not for partnerships)
- X @Brickken — responsive, replies to thread tags (they replied to the RWA recap thread)
- Certified Partner Program — formal partner funnel

## Vault tracking
Full prospect (status, drafts, open actions) saved at
`vault/11-Mess Hall/partnerships/2026-08-04-brickken-prospect.md`.

## Reusable pattern checklist (any infra-to-infra outreach)
- [ ] Research whether the partner's OWN stack uses the same primitives (x402, ERC-8004,
      CCIP, etc.) — quote their own docs as the hook
- [ ] Name the layer separation explicitly: "you do X, we do Y, same rails"
- [ ] Offer a concrete first integration (reference deployment / POC), not vague synergy
- [ ] Find the standards overlap (their standard ↔ ours) as the technical anchor
- [ ] Run 3 channels concurrently: DM (human) + formal partner app (Jordan) + email (agent)
- [ ] Log in vault partnerships/ folder; add to marketplace-listings-registry.md once an
      integration or listing lands
- [ ] Keep identity consistent (same agent name/handle/chain) across all 3 channels so
      they cross-reference one clean entity
