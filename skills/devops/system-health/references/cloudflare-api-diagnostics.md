# Cloudflare API Diagnostics — Triage Chain

Diagnostic pattern for API subdomains behind Cloudflare that return 403/502/1003.

## Triage Chain (always run in order)

### Step 1: Test local backend (bypass nginx + Cloudflare)
```bash
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:<PORT>/<PATH>
```
If 200 → backend is healthy. If 404 → wrong path (try /v1/health, /docs, /openapi.json).

### Step 2: Test through nginx directly (bypass Cloudflare)
```bash
curl -s -o /dev/null -w "%{http_code}" -H "Host: <subdomain>.gentechlabs.net" http://<SERVER_IP>/<PATH>
```
If 200 → nginx proxying works. If 403 → check nginx location blocks.

### Step 3: Test through Cloudflare
```bash
curl -s -o /dev/null -w "%{http_code}" https://<subdomain>.gentechlabs.net/<PATH>
```

## Error Interpretation

| Error | Meaning | Fix |
|-------|---------|-----|
| `error code: 1003` | Cloudflare WAF blocking | Switch DNS to grey cloud (DNS-only) OR add WAF exception |
| `000` (connection refused) | DNS changed to our IP but SSL cert is self-signed | Install Let's Encrypt cert |
| `error code: 521/525` | Cloudflare can't reach origin | Check if backend process is running on server |
| `403` through proxy but `200` locally | WAF or auth middleware | Check x402 payment headers, Cloudflare WAF, or nginx auth |

## When Switching to DNS-Only (Grey Cloud)

When a subdomain is switched from Proxied (orange cloud) to DNS-only (grey cloud):
1. **DNS points directly to server IP** — `dig +short <subdomain>.gentechlabs.net @8.8.8.8` should show server IP, not Cloudflare IPs
2. **SSL cert must be valid** — Cloudflare's edge certificate no longer terminates SSL. Need Let's Encrypt or other public cert.
3. **Propagation** — TTL "Auto" means 5-30 min. Check with `dig +short <subdomain>.gentechlabs.net @8.8.8.8`

## Getting Let's Encrypt Cert for DNS-Only Subdomains

### 1. Add .well-known location to nginx HTTP block
```nginx
location /.well-known/ { root /var/www/gentechlabs; }
```
Before the proxy_pass location block.

### 2. Run certbot
```bash
certbot certonly --webroot -w /var/www/gentechlabs -d <subdomain>.gentechlabs.net
```

### 3. Update nginx SSL block
Replace self-signed cert paths:
```nginx
ssl_certificate /etc/letsencrypt/live/<subdomain>.gentechlabs.net/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/<subdomain>.gentechlabs.net/privkey.pem;
```

### 4. Reload nginx
```bash
nginx -t && systemctl reload nginx
```

### 5. Verify
```bash
curl -s -o /dev/null -w "%{http_code}" https://<subdomain>.gentechlabs.net/<PATH>
```

Certbot auto-renews via systemd timer.

## Common Pitfalls

- **Cloudflare error 1003** is NOT a server issue — it's Cloudflare's WAF. Fix it in Cloudflare dashboard, not on the server.
- **Self-signed certs work locally** but fail through any browser/curl validation. Always confirm cert issuer: `openssl x509 -in /etc/nginx/ssl/gentechlabs.crt -text -noout | grep Issuer`
- **ACME challenge needs .well-known** to be served from a static directory, NOT proxied to a backend that doesn't handle it.
