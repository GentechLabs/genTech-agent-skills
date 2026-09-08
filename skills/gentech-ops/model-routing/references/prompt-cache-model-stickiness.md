# Prompt-cache preservation: fallback chain must reuse the primary model

Source: Teknium (Nous Research) on X, Aug 25, 2026
(https://x.com/Teknium/status/2092141955082019311).

## The rule (fundamentals of inference, not Hermes-specific)

Every mid-session model switch invalidates the entire prompt cache on the new model.
You repay full input-token price (1x) and forfeit the ~0.1x cached-read discount.
Worse: the cache is byte-exact per model, so switching back does NOT restore it once
the entry ages past TTL.

## The risk for our setup

If the gateway silently falls to a DIFFERENT model when the primary stutters
(rate-limit, 5xx, connection error), the whole live session re-pays input tokens.
This is the invisible version of the OpenRouter "auto-routed provider flip" failure
Brett calls out in the same thread.

## Canonical chain (Jordan directive, Aug 25, 2026)

```
Primary:    deepseek-v4-flash:0731  (ollama-cloud)   # weekly reset, fast
Fallback 1: deepseek-v4-flash  (opencode-go)         # SAME model → cache survives
Fallback 2: blockrun/auto      (clawrouter)          # tertiary safety net only
```

- Fallback 1 pins the SAME model as primary so a failover keeps the cache valid.
- `blockrun/auto` = router picks the model → can silently flip and invalidate cache.
  It belongs as the LAST-resort fallback, never first.

## The bug we fixed (Aug 25)

The live config had `clawrouter / blockrun/auto` as the ONLY fallback. That was
(a) wrong per Jordan's intended chain (opencode-go is the backup) and
(b) a cache-invalidation risk because `blockrun/auto` lets the router choose a
different model on failover. Fixed by writing the real YAML list via the config module.

## How to write the fallback chain (correct schema)

`hermes config set fallback_providers '[...]'` stores the list as a QUOTED STRING that
`get_fallback_chain` does NOT parse → `hermes fallback list` reports "No fallback
providers configured". Write a real YAML list via the config module:

```bash
/usr/local/lib/hermes-agent/venv/bin/python -c "
from hermes_cli.config import load_config, save_config
cfg = load_config()
cfg['fallback_providers'] = [
    {'provider': 'opencode-go', 'model': 'deepseek-v4-flash', 'base_url': 'https://opencode.ai/zen/go/v1'},
    {'provider': 'clawrouter', 'model': 'blockrun/auto', 'base_url': 'http://127.0.0.1:8402/v1'},
]
save_config(cfg)
"
```

Verify with `hermes fallback list` (source of truth, not grep). Config change takes
effect on the next gateway restart — there is no mid-session reload.

## What does NOT invalidate the cache

Tiering work across SEPARATE sessions:
- Cheap model (deepseek-v4-flash) for the grind / develop-and-verify front half.
- Delegate big-model audits (GLM 5.2, Kimi) to an isolated subagent via delegate_task.

Each of these is a fresh session with its own context — no shared cache to invalidate.
This is the correct cost pattern and should be preserved. Model "switching" is only a
problem when it happens MID-session (same conversation, back-and-forth), or when the
gateway auto-fails-over to a different model silently.
