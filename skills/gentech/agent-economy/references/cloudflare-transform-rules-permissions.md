# Cloudflare Transform Rules — API Token Permissions

## Issue
When creating API tokens for Cloudflare, **Zone → Zone WAF → Edit** does NOT grant access to Transform Rules (for security headers). You need **Zone → Zone → Edit**.

## Correct Token Configuration

### Permissions Section
| Row | Resource | Permission |
|-----|----------|------------|
| 1 | Account Customizations | Read |
| 2 | Workers Scripts | Edit |
| 3 | Zone → Zone | Edit |
| 4 | Zone WAF | Edit (optional, for WAF rules) |

**Critical:** Row 3 MUST be "Zone" (middle dropdown), NOT "Zone WAF", "Zone DNS", or "Zone Workers".

### Account Resources
- Include → Your Account (e.g., Jordanjones0902@gmail.com's Account)

### Zone Resources
- Include → Specific zone → gentechlabs.net

## API Verification Pattern

```bash
# Verify token works
curl -s "https://api.cloudflare.com/client/v4/user/tokens/verify" \
  -H "Authorization: Bearer YOUR_TOKEN" | jq '.success'

# Test Transform Rules access
curl -s "https://api.cloudflare.com/client/v4/zones/ZONE_ID/rulesets" \
  -H "Authorization: Bearer YOUR_TOKEN" | jq '.result[] | {name,kind,phase}'
```

## Mobile UI Navigation

Transform Rules location on mobile:
1. Dashboard → gentechlabs.net
2. **Rules** (NOT Security → WAF)
3. **Transform Rules** sub-section

## Propagation Delay
After adding Zone → Edit permissions and rolling the token:
- **Wait 5-10 minutes** for permissions to propagate
- Old token strings won't work — must roll/regenerate to apply new permissions
- If still getting "Authentication error" after rolling, check:
  1. Account Resources → Your account included
  2. Zone Resources → gentechlabs.net included
  3. Zone → Zone (not Zone WAF) in permissions

## Example Transform Rule API Call

```bash
# Create custom ruleset for response headers
curl -s -X POST "https://api.cloudflare.com/client/v4/zones/ZONE_ID/rulesets" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "custom-response-headers",
    "kind": "custom",
    "phase": "http_response_headers_transform",
    "description": "Custom security headers"
  }' | jq '.'
```

## Manual Dashboard Fallback (When API Fails)

If API token permissions aren't working, add security headers manually:

1. Dashboard → gentechlabs.net → Rules → Transform Rules
2. Create rule: **Modify Response Header**
3. For each header:
   - **X-Frame-Options**: Set static → `DENY`
   - **Referrer-Policy**: Set static → `strict-origin-when-cross-origin`
   - **Permissions-Policy**: Set static → `camera=(), microphone=(), geolocation=()`
4. When: Hostname equals `gentechlabs.net`
5. Deploy

## Verification

```bash
curl -I https://gentechlabs.net | grep -iE "x-frame|referrer-policy|permissions-policy"
```

Expected output:
```
x-frame-options: DENY
referrer-policy: strict-origin-when-cross-origin
permissions-policy: camera=(), microphone=(), geolocation=()
```

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `Authentication error` (10000) | Token lacks Zone → Edit | Update permissions + roll token |
| `Unauthorized to access requested resource` (9109) | Zone not in Zone Resources | Add gentechlabs.net to Zone Resources |
| `not_found` (1000) on rulesets/phases | Wrong phase/endpoint | Use `/rulesets?kind=custom` instead |
| Permissions work but Transform Rules fail | Missing Zone → Edit | Ensure middle dropdown says "Zone" not "Zone WAF" |