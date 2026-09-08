# Cloudflare + Nginx Setup — GenTech Labs

## Domain
- **Domain:** gentechnlabs.net (registered on Cloudflare)
- **Registrar:** Cloudflare ($11.86/yr, auto-renew ON)
- **Expires:** June 22, 2027

## VPS
- **IP:** 2.24.195.196
- **IPv6:** 2a02:4780:75:e297::1
- **Host:** Hostinger VPS (srv1582785)

## DNS Records (Cloudflare)

| Type | Name | Content | Proxy |
|------|------|---------|-------|
| A | @ | 2.24.195.196 | ✅ Orange cloud |
| A | api | 2.24.195.196 | ✅ Orange cloud |
| CNAME | www | gentechnlabs.net | ✅ Orange cloud |
| A | rugcheck | 2.24.195.196 | ✅ Orange cloud |

## SSL/TLS
- Set to **Full (Strict)** in Cloudflare dashboard
- Cloudflare auto-manages certificates

## Nginx Config
Located at `/etc/nginx/sites-available/gentech`

### Main site (gentechnlabs.net)
- Serves Jordan's Hub from `/root/vaults/gentech/Profiles/hub.html`
- Health check at `/health`

### API server (api.gentechnlabs.net)
- Proxies to `http://127.0.0.1:8090` (x402 API server)
- 6 endpoints: Token Risk, DeFi Intel, Travel, Content, Agent Search, Agent Details

### Rugcheck (rugcheck.gentechnlabs.net)
- Proxies to `http://127.0.0.1:8088` (Rugcheck API)

## Commands
```bash
# Test nginx config
nginx -t

# Restart nginx
systemctl restart nginx

# Check status
systemctl status nginx

# Test locally with host header
curl -H "Host: gentechnlabs.net" http://localhost/health
curl -H "Host: api.gentechnlabs.net" http://localhost/v1/health

# Check DNS propagation
nslookup gentechnlabs.net 8.8.8.8
```

## Pitfalls

### DNS propagation delay
New domains can take 15-30 minutes to propagate. Direct IP works immediately:
```bash
curl -H "Host: gentechnlabs.net" http://2.24.195.196/health
```

### Nginx needs host headers for local testing
When testing locally, you MUST pass the Host header:
```bash
curl -H "Host: api.gentechnlabs.net" http://localhost/v1/health
```
Without the header, nginx returns the default server block.

### Port conflicts
- Port 8088: Rugcheck API (python)
- Port 8090: x402 API server (python3)
- Port 80/443: nginx reverse proxy
- If a port is in use, check with `ss -tlnp | grep :PORT`
