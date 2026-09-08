# GenTech API Safety Suite — Reference Implementation

**Script location:** `/root/.hermes/profiles/gentech/scripts/api-safety-suite/run_safety_suite.py`
**Golden files:** `/root/.hermes/profiles/gentech/scripts/api-safety-suite/golden/`

## What It Tests

| Test | Count | Verifies |
|------|-------|----------|
| Health endpoint | 1 | 200 + `status: ok` |
| CORS preflight | 1 | OPTIONS → proper headers |
| Games API | 2 | 402 shape + accepts[] |
| Movies API | 2 | 402 shape + accepts[] |
| Intel API | 2 | 402 shape + accepts[] |
| NFT API | 1 | 402 shape + accepts[] |
| Wallet API | 1 | 402 shape + accepts[] |
| Agent scan | 1 | 402 shape + accepts[] |
| Airdrops check | 1 | 402 shape + accepts[] |
| **Total** | **12** | |

## Gateway Details

- **Base URL:** `https://api.gentechlabs.net/v1`
- **Version:** 7.0.0
- **Endpoints:** 15 paid, 5 free
- **Networks:** Base, Solana, Avalanche, BNB, OKX
- **Token:** USDC

## Cron Schedule

```
0 2,8,14,20 * * *  → api-safety-suite/run_safety_suite.py (no_agent)
```

## History

- **Jul 18, 2026** — Built and tested. 12/12 passing. Wired as context feed for x402 Compliance Scout.
