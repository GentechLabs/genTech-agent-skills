# Q402 Escrow — Technical Integration

**Provider**: QuackAI (@QuackAI_AI)
**Launch**: July 1, 2026
**Package**: @quackai/q402-mcp

---

## What It Does

Gasless escrow for AI agents:
- Buyer signs once → Q402 relays → funds lock on-chain
- Release on approval, refund after timeout, dispute arbiter
- Supports USDC/USDT payments

---

## Technical Under the Hood

- **EIP-7702 delegated execution**: Gasless relayed transactions
- **EIP-712 signatures**: Type-safe, off-chain signing
- **buyer-bound escrowId**: Each escrow is tied to the buyer
- **canonical vault**: Standardized vault contract
- **on-chain token allowlist**: Only whitelisted tokens accepted
- **replay protection**: Prevents transaction replay attacks

---

## Installation

```bash
npm i @quackai/q402-mcp
```

**Supported agents**: Claude, Codex, Cursor, Cline, Copilot, Hermes

---

## Integration Use Cases

### Use Case 1: Complex Agent-to-Agent Jobs
When agents negotiate price, scope, and delivery terms (e.g., "research market and build strategy"), use Q402 escrow:
1. Buyer signs escrow lock (USDC/USDT amount)
2. Provider agent works on task
3. Buyer approves delivery → funds released
4. Or timeout → refund to buyer
5. Or dispute → arbiter resolves

### Use Case 2: OKX.AI Agent-to-Agent Mode
OKX.AI supports Agent-to-Agent commerce with built-in escrow. Q402 can complement or replace their escrow if gasless is critical.

### Use Case 3: Cross-Protocol Payments
Build a payment router:
- Simple tasks → x402 instant payments
- Complex tasks → Q402 escrow
- Agents support both → choose based on task complexity

---

## Workflow Example

### Step 1: Buyer Initiates Escrow
```javascript
// Agent calls Q402 MCP to lock funds
{
  "token": "USDC",
  "amount": "10",
  "timeout": "86400", // 24 hours
  "buyer": "0x123..."
}
```

### Step 2: Q402 Relays Transaction
- Buyer signs off-chain (EIP-712)
- Q402 relays to chain (EIP-7702)
- Funds locked in canonical vault

### Step 3: Provider Agent Completes Task
- Agent works on deliverable
- Submits results to buyer

### Step 4: Buyer Approves (or Timeout)
- **Approve**: Buyer signs release → funds transferred to provider
- **Timeout**: Auto-refund to buyer after timeout
- **Dispute**: Arbiter reviews evidence → decides who gets funds

---

## Integration Pattern: x402 + Q402 Dual Protocol

**Architecture**:
```
Payment Router
├── Task Type: Simple API call → x402 (instant)
├── Task Type: Complex job → Q402 escrow
└── Fallback: Platform SDK (OKX.AI, others)
```

**Implementation steps**:
1. Detect task complexity (duration, deliverable type, value)
2. Route to appropriate payment protocol
3. Track reputation across all payment modes
4. Unified interface for buyer (doesn't care about backend)

---

## Comparison: Q402 vs OKX APP vs x402

| Feature | Q402 | OKX APP | x402 |
|---|---|---|---|
| Gasless | ✅ Yes | ✅ Yes (X Layer) | ❌ User pays gas |
| Escrow | ✅ Native | ✅ Native | ⚠️ Can build on top |
| Instant payments | ❌ No | ❌ No | ✅ Yes (100M+ proven) |
| Cross-chain | Likely EVM | EVM + Solana | EVM + Solana (OOBE) |
| Protocol standard | Proprietary? | Open standard | AP2 standard |
| Dispute resolution | ✅ Arbiter | ✅ Arbiter | ⚠️ Needs integration |
| Installation | npm package | OKX SDK | Custom integration |

**Strategic fit**: Q402 solves escrow immediately while we build full x402 escrow layer. Use theirs for now, migrate to ours later if needed.

---

## Next Steps for Gentech

### Immediate (Week 1)
1. Install Q402 MCP in Hermes environment
2. Test escrow flow with USDC on testnet
3. Document usage pattern for Gentech agents

### Integration (Week 2)
1. Add Q402 as escrow option for DCA Rebalancing Agent on OKX.AI
2. Build payment router (auto-choose protocol based on task)
3. Test end-to-end: buyer → escrow → delivery → release

### Long-term (Q3)
1. Build x402 ↔ Q402 bridge for cross-protocol payments
2. Position Gentech as dual-protocol agent fleet
3. Publish integration guide for other providers

---

## Links

- Twitter announcement: https://x.com/QuackAI_AI/status/2072271478788403304
- Package: @quackai/q402-mcp (npm)
- Docs: (likely in package, check after install)

---

## Notes

**Gasless advantage**: Critical for marketplace UX. If OKX.AI uses X Layer (zero gas), Q402 matches that experience.

**Dispute resolution**: Q402's arbiter system is battle-tested from marketplace operations. Leverage this instead of building from scratch.

**Protocol independence**: Even as we use Q402, maintain x402 independence. If Q402 becomes restricted, we can migrate to x402 escrow layer.