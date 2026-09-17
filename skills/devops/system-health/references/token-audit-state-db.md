# Token Usage Audit — state.db Reference

## Database Location
`~/.hermes/state.db` (SQLite, ~316MB as of May 2026)

## Full Schema

### sessions table
```
id                  TEXT PRIMARY KEY
source              TEXT NOT NULL       -- 'cron' or 'cli'
user_id             TEXT
model               TEXT                -- model name string
model_config        TEXT                -- JSON config blob
system_prompt       TEXT
parent_session_id   TEXT                -- for subagent sessions
started_at          REAL NOT NULL       -- unix timestamp
ended_at            REAL
end_reason          TEXT                -- 'completed', 'cli_close', 'cron_complete', 'compression'
message_count       INTEGER DEFAULT 0
tool_call_count     INTEGER DEFAULT 0
input_tokens        INTEGER DEFAULT 0
output_tokens       INTEGER DEFAULT 0
cache_read_tokens   INTEGER DEFAULT 0
cache_write_tokens  INTEGER DEFAULT 0
reasoning_tokens    INTEGER DEFAULT 0
billing_provider    TEXT                -- 'nous', 'custom', 'opencode-go', 'gemini'
billing_base_url    TEXT
billing_mode        TEXT
estimated_cost_usd  REAL
actual_cost_usd     REAL
cost_status         TEXT
cost_source         TEXT
pricing_version     TEXT
title               TEXT
api_call_count      INTEGER DEFAULT 0
```

### messages table
```
id              INTEGER PRIMARY KEY
session_id      TEXT NOT NULL       -- FK to sessions.id
role            TEXT NOT NULL       -- 'user', 'assistant', 'tool', 'system'
content         TEXT
tool_call_id    TEXT
tool_calls      TEXT                -- JSON array of tool call objects
tool_name       TEXT
timestamp       REAL NOT NULL
token_count     INTEGER
finish_reason   TEXT
reasoning       TEXT
reasoning_content   TEXT
reasoning_details   TEXT
codex_reasoning_items TEXT
codex_message_items  TEXT
```

## Key Queries

### Session totals by date
```sql
SELECT date(started_at, 'unixepoch') as day,
       COUNT(*) as sessions,
       SUM(input_tokens) as input_tok,
       SUM(output_tokens) as output_tok,
       SUM(estimated_cost_usd) as cost
FROM sessions
WHERE started_at >= ? AND started_at < ?
GROUP BY day ORDER BY day
```

### Provider cost breakdown
```sql
SELECT billing_provider, model,
       COUNT(*) as sessions,
       SUM(input_tokens) as input_tok,
       SUM(estimated_cost_usd) as cost
FROM sessions
WHERE started_at >= ? AND started_at < ?
GROUP BY billing_provider, model
ORDER BY cost DESC
```

### Runaway sessions (high tool calls)
```sql
SELECT model, source, tool_call_count, message_count,
       input_tokens, estimated_cost_usd,
       datetime(started_at, 'unixepoch') as started
FROM sessions
WHERE started_at >= ? AND started_at < ?
  AND tool_call_count > 50
ORDER BY tool_call_count DESC
```

### Cron vs CLI split
```sql
SELECT source,
       COUNT(*) as sessions,
       SUM(input_tokens) as input_tok,
       SUM(estimated_cost_usd) as cost
FROM sessions
WHERE started_at >= ? AND started_at < ?
GROUP BY source
```

## Known Pricing (as of May 2026)

| Model | Provider | Input Cost | Output Cost | Notes |
|-------|----------|-----------|-------------|-------|
| xiaomi/mimo-v2-flash | Nous | ~$0.297/1M | varies | Paid |
| stepfun/step-3.5-flash | Nous | ~$0.08/1M | varies | Paid |
| openai/gpt-5.4-nano | Nous | ~$1.12/1M | varies | Paid |
| mimo-v2.5 | custom/opencode-go | $0 | $0 | Free tier |
| arcee-ai/trinity-large-thinking | Nous | $0 | $0 | Free tier |
| gemini-3-flash-preview | gemini | $0 | $0 | Free tier |

## Anomaly Patterns

1. **Runaway CLI loops**: Sessions with 100+ tool calls, typically on paid models. Root cause: agent hitting iteration limit without completing task. Mitigation: set `max_iterations` cap.

2. **Zero-input sessions**: Sessions with 0 input tokens but non-zero output. Usually error/empty sessions or sessions that hit provider error before first token.

3. **Cost spikes from model switches**: When default model changes to a paid tier, cost jumps from $0 to real dollars. Check `billing_provider` column to identify.

4. **Post-consolidation validation**: After fleet architecture changes (e.g., Option 1), compare cron session counts and costs pre/post to verify rerouting worked.
