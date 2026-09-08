# Port Health Monitor Pattern — TCP-Level Service Checking

Use when you need to verify backend processes are alive but they don't expose a `/health` endpoint.

## Problem

Backend services (x402 gateway, APIs, agents) run on ports but may not have a dedicated HTTP health endpoint. Checking for a specific HTTP response (200 OK) returns false negatives — the service is running but returns 403/404/405 because the URL path doesn't exist.

## Solution: Two-Level Check

### Level 1 — TCP Port Listening (definitive)
Check if the OS kernel reports the port is open with a process attached. This works even if the service has no `/health` endpoint.

```bash
ssh root@VPS_HOST "ss -tlnp | grep -E ':PORT '"
```

If this returns output, the port is **actually listening**. The process is alive at the OS level.

### Level 2 — HTTP Response (optional, for public URLs)
Check if any HTTP response is returned (not just 200). 4xx/5xx means the server is alive — the endpoint just doesn't exist.

```python
import urllib.request, urllib.error

def check_public_url(url):
    try:
        resp = urllib.request.urlopen(url, timeout=10)
        return True, f"HTTP {resp.getcode()}"
    except urllib.error.HTTPError as e:
        # 4xx means the server is alive
        return True, f"HTTP {e.code}"
    except urllib.error.URLError as e:
        return False, str(e.reason)
```

### Combining Both Levels

```python
SERVICES = [
    ("x402 Gateway", 8090, "port"),
    ("Token Security", 8086, "port"),
    ("Main Site", "https://gentechlabs.net", "web"),
]

def check(name, target, stype):
    if stype == "port":
        result = subprocess.run(
            ["ssh", "root@VPS_HOST", f"ss -tlnp | grep -E ':{target} '"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            return True, "listening"
        return False, "port not listening"
    
    elif stype == "web":
        code, err = check_public_url(target)
        if code and code < 500:
            return True, f"HTTP {code}"
        return False, err
```

## Implementation

Full production script at `/root/.hermes/profiles/gentech/scripts/port-health-monitor.py`:
- 7 backend ports (8090, 8088, 8080, 8082, 8084, 8086, 3099)
- 5 public URLs (main site, demo, yield, arb, portfolio)
- DNS-only subdomains handled as optional (no false alarm if DNS not configured yet)
- Silent when healthy — no news is good news
- Reports via stdout when something is down

## Cron Configuration

```json
{
  "name": "Port Health Monitor — Daily Check",
  "schedule": "0 6,18 * * *",
  "script": "port-health-monitor.py",
  "no_agent": true,
  "deliver": "origin"
}
```

## Key Insight

The Python `urllib` SSL context fights with Cloudflare proxied domains — always use `curl -sk` from the VPS directly to bypass Cloudflare's SSL interception for definitive health checks. The VPS-local curl command reveals the actual nginx response without Cloudflare's layer in the middle.

## SSL Certificates for DNS-Only Subdomains

When you add subdomains as **DNS-only** (grey cloud) in Cloudflare and want HTTPS, you need to issue Let's Encrypt certs for them separately. The main domain cert does NOT cover subdomains via wildcard unless explicitly requested.

```bash
# Issue cert for multiple subdomains in one command
certbot --nginx \
  -d demo.yourdomain.net \
  -d yield.yourdomain.net \
  -d arb.yourdomain.net \
  --non-interactive --agree-tos --email you@yourdomain.net
```

Certbot auto-creates nginx server block entries for HTTPS redirect. Verify:

```bash
# Direct HTTPS check
curl -skI https://demo.yourdomain.net | head -2    # Expect: HTTP/1.1 200

# Certificate expiry
certbot certificates 2>/dev/null | grep -A3 "Certificate Name: demo"
```

Confirmed Jul 28, 2026: certbot `--nginx` mode auto-deploys certs to existing nginx configs for `demo.gentechlabs.net`, `yield.gentechlabs.net`, `arb.gentechlabs.net`. No manual nginx edit needed.

## nginx Virtual Host Testing (server_name Gotcha)

When testing nginx from the VPS directly, `curl http://localhost/path` does NOT test the correct server block. It hits the **default server block** — which may serve a completely different site.

Always use the `Host` header to match the intended virtual host:

```bash
# WRONG — hits default server block, likely returns 404
curl http://localhost/frameforge.html

# CORRECT — tests the gentechlabs.net server block
curl -H "Host: gentechlabs.net" http://localhost/frameforge.html
```

This is critical for multi-site nginx configurations where multiple server blocks exist. Confirmed Jul 28, 2026: `curl http://localhost/frameforge.html` returned 404, but the correct `curl -H "Host: gentechlabs.net" http://localhost/frameforge.html` returned 200.
