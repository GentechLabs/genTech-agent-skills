# Agent Kit x402 Commerce Layer

## Pattern: Three-Module Architecture

When building agent-to-agent payment systems, use this three-module pattern:

### 1. Payment Module (SPENDING side)
**File:** `payment_module.py`
**Purpose:** Policy enforcement BEFORE calling Q402 MCP tools
**Key classes:**
- `PaymentPolicy` — daily limits, per-tx caps, chain/token approval lists, blocked recipients
- `AgentPayment` — validate, format commands, record attempts, daily summary

**Flow:** Agent wants to pay → validate against policy → format Q402 command → agent executes → record to audit log

**Key methods:**
- `validate(chain, token, to, amount, memo)` → `{approved, reason}`
- `format_pay_command(...)` → string the agent calls via MCP
- `record_attempt(...)` → PaymentRecord with audit trail
- `get_daily_summary()` → spending totals

### 2. Revenue Module (RECEIVING side)
**File:** `revenue_module.py`
**Purpose:** Verify incoming payments before serving API responses
**Key classes:**
- `Endpoint` — registered API with price, rate limit, active status
- `AgentRevenue` — receipt verification, double-spend prevention, revenue tracking

**Flow:** Agent sends receipt → check double-spend → verify amount → mark consumed → serve response

**Key methods:**
- `register_endpoint(path, price_usd, description)` → Endpoint
- `verify_payment(receipt_id, amount, endpoint, payer)` → `{verified, reason}`
- `check_rate_limit(payer, endpoint, max_per_min)` → bool
- `daily_report()` → revenue totals

### 3. Gateway (UNIFIED layer)
**File:** `gateway.py`
**Purpose:** Ties spending + revenue into one agent-callable API
**Key classes:**
- `APIRoute` — registered API with pricing + provider address
- `AgentPaymentGateway` — unified spending + revenue + budget management

**Key methods:**
- `register_api(path, price_usd, description)` → dict
- `handle_request(receipt_id, endpoint, payer)` → `{allowed, reason}`
- `check_budget(endpoint, amount)` → `{affordable, daily_remaining}`
- `daily_summary()` → combined spending + revenue

## Revenue Model

| Action | Price | Margin |
|--------|-------|--------|
| API query | $0.01 | ~90% |
| Place detail | $0.05 | ~85% |
| Review extract | $0.02 | ~90% |
| Content brief | $0.05 | ~80% |

## Config Pattern

```yaml
policy:
  daily_limit_usd: 100.0
  per_tx_limit_usd: 50.0
  approved_chains: [base, bnb, ethereum, arbitrum, avalanche]
  approved_tokens: [USDC, USDT]
  require_memo: true

q402:
  mode: sandbox
  default_chain: base
  default_token: USDC

audit:
  log_dir: ~/.hermes/profiles/gentech/audit/payments
  retention_days: 90
```

## Integration with Q402 MCP

The payment module does NOT call Q402 directly. It formats commands the agent executes via MCP tools: `q402_pay`, `q402_batch_pay`, `q402_balance`, `q402_verify_receipt`. Policy validates BEFORE calling Q402.

## Audit Trail

Every payment attempt (approved or blocked) gets logged to JSONL with id, timestamp, chain, token, to, amount, memo, status, and policy_check.

## Testing Pattern

Each module gets its own test file. Key categories: policy validation, daily limits, double-spend, rate limiting, command formatting, audit trail.
