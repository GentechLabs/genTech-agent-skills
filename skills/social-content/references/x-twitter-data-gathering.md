# X/Twitter Data Gathering for Content Research

## Tools Evaluated

### twscrape (⭐ 2380 — vladkens/twscrape)
- **What:** Python library using X's GraphQL API. Search, tweets, users, followers, trends.
- **Install:** `pip install twscrape`
- **Auth:** Requires X/Twitter accounts (cookies or login/password). No guest token support — X blocks guest tokens (403).
- **CLI:** `twscrape search "query"`, `twscrape user_by_login handle`, `twscrape trends`
- **Python:** Async API with `gather()` helper. Supports parallel scrapers.
- **Features:** Rate limit handling with auto account switching, session persistence, email verification for login.
- **Status:** ✅ Installed on server. ⚠️ Needs account cookies to function.
- **Verdict:** Best self-contained scraper for bulk data gathering. Requires at least one X account.

### xurl (official X developer CLI)
- **What:** Official X API CLI. Post, search, DM, media, v2 raw access.
- **Status:** ✅ Installed (v1.1.0). ❌ No apps registered — needs manual OAuth setup.
- **Auth:** User must register app at developer.x.com, then run `xurl auth oauth2 --app <name>` outside agent session.
- **Best for:** Posting, engagement, authenticated API access. Not bulk scraping.
- **See:** `xurl` skill for full docs.

### Social Media Scraping APIs (cporter202/social-media-scraping-apis)
- **What:** Curated list of 3,268 Apify actors for social media scraping.
- **Status:** ❌ NOT useful — it's a directory of links to third-party paid Apify services, not self-contained code.
- **Lesson:** Always check repo structure before cloning. Star count ≠ useful code.

## Decision Matrix

| Need | Tool | Why |
|------|------|-----|
| Bulk tweet scraping for content research | twscrape | Async, rate-limited, search/users/trends |
| Posting, engagement, real-time interaction | xurl | Official API, OAuth 2.0, full write access |
| Quick tweet read (no auth) | browser_navigate + browser_vision | Fallback for reading public tweets |
| Social media analytics | External services (Apify, etc.) | Paid, not self-hosted |

## Setup Requirements for twscrape

### Option 1: Browser Cookie Extraction (Fastest)
1. Log into X/Twitter on your PC browser
2. Extract cookies (abc, ct0 values from DevTools → Application → Cookies)
3. Add account: `twscrape add_accounts accounts.txt username:password:email:email_password:_:cookies`
4. Cookies are more stable than login flow

### Option 2: Username/Password Login
1. Create accounts file: `username:password:email:email_password`
2. Add: `twscrape add_accounts accounts.txt username:password:email:email_password`
3. Login: `twscrape login_accounts`
4. Requires IMAP access to email for verification codes
5. Some email providers (ProtonMail) don't support IMAP — use `--manual` flag

### Minimum for Testing
- One X account with valid cookies
- Run: `twscrape add_accounts test.txt username:password:email:email_password:_:cookies`
- Test: `twscrape search "AI agents" -n 5`

## Usage Examples

### Search for Content Research
```python
import asyncio
from twscrape import API, gather

async def research():
    api = API()
    # Search latest tweets about a topic
    tweets = await gather(api.search("AI agents crypto", limit=50))
    for t in tweets:
        print(f"@{t.user.username}: {t.rawContent[:100]}")

asyncio.run(research())
```

### CLI Search
```bash
twscrape search "AI agents" -n 20
twscrape user_by_login elonmusk
twscrape trends news
```

### Content Pipeline Integration
1. Search for topic keywords → collect 50-100 tweets
2. Extract patterns: hooks, formats, engagement signals
3. Feed insights into content calendar (see social-content skill)
4. Track what's working in the niche

## Pitfalls
- Guest tokens don't work — X blocks them with 403
- Free X accounts get rate-limited fast; multiple accounts help
- Cookie-based auth is more stable than login flow
- Always test with a small search first before bulk operations
- Don't scrape too aggressively — respect rate limits
