# Prompt-to-Yield Service Design

**Concept:** Agents that receive strategy prompts (e.g., "use bid-ask for this range") and automatically execute rebalances with gas payment, transforming user intent into yield farming operations.

**User's vision (verbatim):**

> "There are other protocols that are also doing like a prompt to defy or a prompt to do this or that. One of the advantages we could have for our prompt to yield farm is like, we'll use bid ask for an example, right? In our previous example, we talked about how, you know, you could sell into strength or you could go down, right? Well, let's say like right now in our scenario, if we're on the outer edge going up, what if we were to prompt what the next shape should look like? And we say between what range we want it at, right?"

> "If the way that Trader Joe works is you can only yield farm at the current price, right? I'm guessing that's how most platforms are, unless maybe we could be different. I like the idea of prompting the next shape based on where it's going."

> "Because we talked about the agents having a built-in like gas feature, they'll automatically pay the gas and take care of that for you."

---

## Three-Layer Architecture

```
┌─────────────────────────────────────────────────┐
│           PRESENTATION LAYER                    │
│   User prompts: "Bid-ask between $6.70-$7.05"   │
├─────────────────────────────────────────────────┤
│              AGENT LAYER                        │
│   Strategy execution, rebalancing, gas payment  │
├─────────────────────────────────────────────────┤
│               DATA LAYER (Oracles)              │
│   On-chain RPC, DexScreener, LFJ CLI           │
└─────────────────────────────────────────────────┘
```

---

## Signal Layer (Implemented Jul 3, 2026)

The DeFi monitor now includes intelligent range migration suggestions as part of the alert system:

**Alert + Suggestion Example:**

```
🔴 OUT OF RANGE
🔧 MIGRATE: Shift range to $6.9318-$7.1524 (CURVE) — price $7.0200 above $7.0067
```

**Decision Flow:**
```
1. Agent monitors → efficiency drops to 49%
2. Agent alerts with suggestion
3. User approves: "Yes, execute with gas budget $2"
4. Agent executes: Withdraw → Calculate new bins → Add liquidity
5. Agent reports: "Done. New efficiency: 72%"
```

---

## Execution Layer (Future API Service)

**Service Skeleton:**

```python
# Flask API for yield farming operations
app = Flask(__name__)

@app.route('/api/strategy/suggest', methods=['POST'])
def suggest_strategy():
    """
    Analyze current position and suggest optimal strategy.
    Returns: shape, range_low, range_high, confidence
    """
    price = request.json.get('price')
    current_shape = request.json.get('shape')
    current_range = request.json.get('range')
    
    # Call lp-monitor-v2.py suggest_new_range()
    suggestion = suggest_new_range(price, current_shape, *current_range, 'LOW_EFFICIENCY')
    
    return jsonify({
        'suggestion': suggestion,
        'shape': 'curve',
        'range_low': 6.7640,
        'range_high': 7.0288,
        'confidence': 0.82
    })

@app.route('/api/position/migrate', methods=['POST'])
def migrate_position():
    """
    Execute range migration with gas auto-payment.
    Returns: tx_hash, new_range, gas_used, status
    """
    wallet = request.json.get('wallet')
    new_shape = request.json.get('shape')
    new_range = request.json.get('range')
    gas_budget = request.json.get('gas_budget', 2.0)
    
    # 1. Withdraw current bins
    # 2. Calculate new bin IDs
    # 3. Add liquidity to new bins
    # 4. Pay gas from agent wallet
    
    tx_hash = execute_lfj_cli_migration(wallet, new_shape, new_range)
    
    return jsonify({
        'tx_hash': tx_hash,
        'new_range': new_range,
        'gas_used': 0.015,
        'status': 'completed'
    })
```

---

## Competitive Advantage

**Most platforms:** Force yield farming at current price (LFJ UI limitation)

**AAE differentiation:**
- Anticipatory positioning: "Prompt what the next shape should look like"
- Range migration: Place bins anywhere within tick spacing
- Gas abstraction: Agents handle gas, users see results
- Prompt-to-yield: Natural language → executed strategy

---

## User Experience Pattern

**Phase 1: Signal (Active)**
```
User: "How's my pool doing?"
Agent: Shows current state + efficiency trend
```

**Phase 2: Suggestion (Active)**
```
Agent: "Efficiency dropping to 49%. Suggest switching to CURVE at $6.76-$7.03."
User: "Do it."
```

**Phase 3: Execution (Future)**
```
Agent: "Withdrawing bins... calculating... adding liquidity... done. New efficiency 72%. Gas: $0.015."
```

---

## Integration with AAE Milestone

This service is the **action layer** of the AAE DeFi milestone:

1. **Presentation**: Dashboards show milestones and progress
2. **Signal**: Smart alerts with suggestions (implemented)
3. **Action**: Prompt-to-yield execution (future API service)

Agents sell "range migration as a service" — not just monitoring, but autonomous strategy execution.

---

## Reference Implementation

**Signal layer code:** `/root/.hermes/profiles/gentech/scripts/lp-monitor-v2.py`
- `check_debounce()` function: Alert escalation + silence rules
- `suggest_new_range()` function: Shape/range optimization recommendations

**Test command:**
```bash
python3 /tmp/test_lp_alert.py
```

**Future API location:** `/root/.hermes/profiles/gentech/scripts/defi-yield-api.py`