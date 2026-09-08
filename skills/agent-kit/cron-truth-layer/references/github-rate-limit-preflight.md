# GitHub API Rate Limit Preflight

## Problem
Cron jobs that make GitHub API calls can exhaust the 5,000 requests/hour limit, causing false "token invalid" errors. The token is valid — the rate limit is just depleted.

## Detection
```bash
curl -s -H "Authorization: token $(grep GITHUB_TOKEN /root/.env | cut -d= -f2)" \
  https://api.github.com/rate_limit | \
  python3 -c "import sys,json; d=json.load(sys.stdin); c=d['resources']['core']; print(f'Core: {c[\"remaining\"]}/{c[\"limit\"]}')"
```

## Preflight Check
Add this at the top of any cron job that makes GitHub API calls:

```python
import subprocess, json

def check_github_rate_limit(min_remaining=100):
    """Check GitHub API rate limit. Returns (ok, remaining, limit)."""
    try:
        token = open('/root/.env').read().split('GITHUB_TOKEN=')[1].split('\n')[0].strip()
        result = subprocess.run(
            ['curl', '-s', '-H', f'Authorization: token {token}',
             'https://api.github.com/rate_limit'],
            capture_output=True, text=True, timeout=10
        )
        data = json.loads(result.stdout)
        core = data.get('resources', {}).get('core', {})
        remaining = core.get('remaining', 0)
        limit = core.get('limit', 5000)
        
        if remaining < min_remaining:
            print(f"⛔ Rate limited — {remaining}/{limit} remaining. Skipping this run.")
            return False, remaining, limit
        return True, remaining, limit
    except Exception as e:
        print(f"⚠️ Could not check rate limit: {e}")
        return True, 999, 5000  # Proceed on failure
```

## Usage
```python
ok, remaining, limit = check_github_rate_limit()
if not ok:
    sys.exit(0)  # Skip silently
```

## Key Facts
- **5,000 requests/hour** for authenticated users (Core API)
- **30 requests/minute** for Search API (separate pool)
- Resets on the hour (not rolling window)
- Rate limit is per-user, not per-token
- `gh auth status` reports "token invalid" when rate limited — this is misleading
- The token is fine; just wait for the reset (~21 min max)
