# Revenue Dashboard Blueprint

## Core Metrics to Track

### Real-Time Dashboard
```typescript
// Dashboard components:
- Total revenue (today, 7 days, 30 days)
- Revenue by API endpoint (top performers)
- Revenue by customer (whales vs. long-tail)
- Top 10 revenue-generating APIs
- Conversion funnel (visits → calls → payments)
- Failed payments tracking (rate, reasons)
```

### Per-Endpoint Tracking
```yaml
metrics:
  - endpoint: /api/agent/register
    total_calls: 1,234
    paid_calls: 456
    revenue_usd: 4.56
    conversion_rate: 36.9%
    failed_payments: 12
    avg_call_latency_ms: 245
    
  - endpoint: /api/defi/position
    total_calls: 8,901
    paid_calls: 2,345
    revenue_usd: 23.45
    conversion_rate: 26.3%
    failed_payments: 89
    avg_call_latency_ms: 512
```

### Per-Customer Tracking
```yaml
customer_0xabc123:
  wallet_address: 0xabc123...
  total_calls: 567
  total_revenue: 5.67
  first_call: 2026-07-01T10:23:45Z
  last_call: 2026-07-05T14:56:78Z
  top_endpoints:
    - /api/agent/search (234 calls, $2.34)
    - /api/defi/position (123 calls, $1.23)
  
customer_0xdef456:
  wallet_address: 0xdef456...
  total_calls: 12,345
  total_revenue: 123.45
  first_call: 2026-06-15T09:12:34Z
  last_call: 2026-07-05T15:23:45Z
  status: premium (1000+ calls)
```

## Payment Webhook Events

```javascript
// Events to track:
- payment_successful → increment revenue, log settlement
- payment_failed → alert for investigation, log error
- payment_refunded → adjust revenue, flag for review
- chargeback → revoke access, investigate fraud
- payment_expired → log, no action (client will retry)
```

## Weekly Automated Report

```markdown
# GenTech API Revenue Report — Week of 2026-07-01

## Summary
- Revenue this week: $45.67 (+23% vs last week)
- Total calls: 4,567 (+18% vs last week)
- New customers: 12
- Conversion rate: 5.2% (↑ from 4.1%)

## Top APIs
| API | Calls | Revenue | % of Total |
|-----|-------|---------|------------|
| Agent Registration | 1,234 | $12.34 | 27% |
| DeFi Intelligence | 987 | $9.87 | 22% |
| Agent Search | 765 | $7.65 | 17% |

## Issues
- Failed payments: 45 (rate: 1.0%)
- Top failure reason: "insufficient funds" (23)
- Action needed: None (within acceptable threshold)

## Next Week Target
- Revenue: $50
- New customers: 15
```

## Database Schema

```sql
-- Payment transactions
CREATE TABLE payments (
    id TEXT PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    endpoint TEXT NOT NULL,
    wallet_address TEXT NOT NULL,
    amount_usd DECIMAL(10, 4) NOT NULL,
    verified BOOLEAN NOT NULL,
    tx_hash TEXT,
    error TEXT,
    INDEX idx_timestamp (timestamp),
    INDEX idx_endpoint (endpoint),
    INDEX idx_wallet (wallet_address)
);

-- Daily aggregates
CREATE TABLE daily_revenue (
    date DATE PRIMARY KEY,
    total_calls INT,
    paid_calls INT,
    revenue_usd DECIMAL(10, 2),
    failed_payments INT
);

-- Endpoint performance
CREATE TABLE endpoint_stats (
    endpoint TEXT PRIMARY KEY,
    total_calls INT,
    paid_calls INT,
    revenue_usd DECIMAL(10, 2),
    failed_payments INT,
    avg_latency_ms INT,
    updated_at TIMESTAMP
);
```

## Build Priority

### Day 1: Core Dashboard
- [ ] Revenue totals (today, 7d, 30d)
- [ ] Revenue by endpoint chart
- [ ] Failed payments counter

### Day 2: Payment Webhooks
- [ ] webhook endpoint for payment events
- [ ] Event logging to database
- [ ] Revenue increment on success

### Day 3: Customer Tracking
- [ ] Per-customer metrics
- [ ] Top customers view
- [ ] Customer lifetime value

### Day 4: Automated Reports
- [ ] Weekly email/Slack report
- [ ] Daily revenue summary
- [ ] Alert on high failure rate

### Day 5: Optimization
- [ ] Performance tuning
- [ ] Historical data migration
- [ ] A/B testing integration

## Implementation Notes

- Use SQLite for simplicity (migrate to PostgreSQL at scale)
- Tag all API calls with `X-Customer-Wallet` header
- Store settlement data from facilitator for reconciliation
- Implement rate limiting per wallet before payment verification
- Log all payment events for debugging