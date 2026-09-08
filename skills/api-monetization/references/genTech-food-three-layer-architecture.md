# GenTech Food — Three-Layer x402 Product Architecture

Concrete example of building a paid x402 product with free + paid + microtask-offset layers.

## The Three Layers

| Layer | What | Monetization | Tech |
|-------|------|-------------|------|
| **🧠 Food Memory** | Free personal food journal — save dishes from travel, describe or photo, agent stores it | **Free** (loss leader, builds habit) | Vault JSON + agent conversation |
| **🚚 Ordering** | Check dd-cli for deals, order from favorite restaurants via agent | **$0.01/query** via AgentCash Router | `dd-cli` + AgentCash Router |
| **💰 Work Offset** | Do WURK microtasks to cover delivery fees | **Free** (retention mechanic, keeps users in ecosystem) | WURK.fun EarnFi |

## Why Three Layers

Single-purpose paid APIs have low retention. Users pay once, get the data, leave.

The three-layer model solves this:
1. **Free layer** builds habit — user saves dishes, returns to check them
2. **Paid layer** captures value — user pays $0.01 when they want to order
3. **Work offset layer** keeps them engaged — user does microtasks instead of paying, which generates data/reputation for us

## The Flywheel

```
User saves a dish (free) → wants to order it (paid $0.01) → 
can't afford delivery fee → does WURK tasks (free for user, we earn micro-revenue) → 
Agent learns preferences → better recommendations → more orders
```

## Mapping to x402

- **Food Memory**: No payment required — served from vault/agent context
- **Ordering**: x402 $0.01/call — `POST /api/order` with `X-PAYMENT` header
- **Work Offset**: No x402 — uses WURK.fun token system (EarnFi credits)
- **Kroger Ingredient Search**: x402 $0.01/call — `POST /api/stores` with `X-PAYMENT`

## Stack

- **API**: AgentCash Router (`@agentcash/router`) — auto-handles 402 challenges, settlement, discovery
- **Memory**: Vault JSON files (`Food/dishes/`, `Food/stores.json`)
- **Delivery**: `dd-cli` (DoorDash CLI for agents)
- **Work Offset**: WURK.fun microtask marketplace
- **Grocery**: Kroger Product API (developer.kroger.com)

## When to Use This Pattern

Use the three-layer model when:
- Your product has a natural "memory" component (what user did before)
- You can offer a free tier that's genuinely useful on its own
- There's a high-frequency action (ordering) worth charging for
- You can offer an alternative payment method (work) that benefits your ecosystem

Don't use it when:
- Users have no recurring need (one-and-done data fetch)
- The free tier would cannibalize all paid use
- Microtask economics don't pencil out (delivery fee too high vs task payout)
